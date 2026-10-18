import { createServer } from 'node:net'
import { spawn } from 'node:child_process'
import { rmSync } from 'node:fs'

const HOST = process.env.ULTRA_HOST || '127.0.0.1'

function parsePortList(value, defaults) {
  const raw = value || defaults
  return raw
    .split(',')
    .map((part) => Number(part.trim()))
    .filter((port) => Number.isInteger(port) && port > 0 && port < 65536)
}

function isPortFree(host, port) {
  return new Promise((resolve) => {
    const server = createServer()

    server.once('error', () => {
      resolve(false)
    })

    server.once('listening', () => {
      server.close(() => resolve(true))
    })

    server.listen(port, host)
  })
}

async function pickFreePort(host, candidates, serviceName) {
  for (const port of candidates) {
    const free = await isPortFree(host, port)
    if (free) {
      return port
    }
  }

  throw new Error(
    `No free port found for ${serviceName}. Checked: ${candidates.join(', ')}`
  )
}

function startService(command, args, env) {
  return spawn(command, args, {
    env,
    stdio: 'inherit',
    shell: process.platform === 'win32',
  })
}

async function main() {
  rmSync('.next', { recursive: true, force: true })

  const webPorts = parsePortList(process.env.ULTRA_WEB_PORTS, '3000,3001,3002,3010')
  const apiPorts = parsePortList(process.env.ULTRA_API_PORTS, '8080,8081,8082,8090')

  const webPort = await pickFreePort(HOST, webPorts, 'web')
  const apiPort = await pickFreePort(HOST, apiPorts, 'api')

  if (webPort === apiPort) {
    throw new Error(`Web and API cannot share same port: ${webPort}`)
  }

  const sharedEnv = {
    ...process.env,
    ULTRA_HOST: HOST,
    NEXT_PUBLIC_BASE_URL: `http://${HOST}:${webPort}`,
    NEXT_PUBLIC_API_URL: `http://${HOST}:${webPort}`,
  }

  const webEnv = {
    ...sharedEnv,
    HOST,
    PORT: String(webPort),
  }

  const apiEnv = {
    ...sharedEnv,
    BACKEND_HOST: HOST,
    BACKEND_PORT: String(apiPort),
    PORT_BACKEND: String(apiPort),
  }

  console.log('────────────────────────────────────────────')
  console.log('Ultra Microservices Dev Topology')
  console.log(`WEB: http://${HOST}:${webPort}`)
  console.log(`API: http://${HOST}:${apiPort}`)
  console.log('────────────────────────────────────────────')

  const yarnCmd = process.platform === 'win32' ? 'yarn.cmd' : 'yarn'
  const webProc = startService(yarnCmd, ['dev'], webEnv)
  const apiProc = startService(yarnCmd, ['dev:backend'], apiEnv)

  let isShuttingDown = false

  const shutdown = (signal) => {
    if (isShuttingDown) {
      return
    }

    isShuttingDown = true
    console.log(`\nReceived ${signal}, stopping microservices...`)

    if (!webProc.killed) {
      webProc.kill('SIGINT')
    }

    if (!apiProc.killed) {
      apiProc.kill('SIGINT')
    }

    setTimeout(() => process.exit(0), 500)
  }

  process.on('SIGINT', () => shutdown('SIGINT'))
  process.on('SIGTERM', () => shutdown('SIGTERM'))

  webProc.on('exit', (code) => {
    if (isShuttingDown) {
      return
    }

    console.error(`Web service exited with code ${code}`)
    shutdown('WEB_EXIT')
    process.exit(code ?? 1)
  })

  apiProc.on('exit', (code) => {
    if (isShuttingDown) {
      return
    }

    console.error(`API service exited with code ${code}`)
    shutdown('API_EXIT')
    process.exit(code ?? 1)
  })
}

main().catch((error) => {
  console.error(error.message)
  process.exit(1)
})
