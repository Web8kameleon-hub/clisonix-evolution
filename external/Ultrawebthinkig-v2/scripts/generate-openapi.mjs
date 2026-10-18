import { promises as fs } from 'node:fs'
import path from 'node:path'

const rootDir = process.cwd()
const outputPath = path.join(rootDir, 'openapi', 'internal-openapi.json')

const walk = async (directory) => {
  const entries = await fs.readdir(directory, { withFileTypes: true })
  const files = []

  for (const entry of entries) {
    const resolved = path.join(directory, entry.name)
    if (entry.isDirectory()) {
      files.push(...(await walk(resolved)))
    } else {
      files.push(resolved)
    }
  }

  return files
}

const toProjectRelative = (absolutePath) => path.relative(rootDir, absolutePath).replace(/\\/g, '/')

const toApiPathFromAppRoute = (filePath) => {
  const normalized = filePath.replace(/\\/g, '/')
  const apiSuffix = normalized
    .replace(/^app\/api/, '/api')
    .replace(/\/route\.(ts|tsx|js|jsx)$/, '')
  return apiSuffix === '/api' ? '/api' : apiSuffix
}

const toApiPathFromPagesRoute = (filePath) => {
  const normalized = filePath.replace(/\\/g, '/')
  const apiSuffix = normalized
    .replace(/^pages\/api/, '/api')
    .replace(/\.(ts|tsx|js|jsx)$/, '')
  return apiSuffix
}

const detectAppRouteMethods = (content) => {
  const matches = content.matchAll(/export\s+async\s+function\s+(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)\b/g)
  const methods = [...new Set([...matches].map((m) => m[1].toLowerCase()))]
  return methods.sort()
}

const detectPagesRouteMethods = (content) => {
  const methods = new Set()
  for (const method of ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD']) {
    const methodRegex = new RegExp(`req\\.method\\s*={2,3}\\s*['\"]${method}['\"]`, 'g')
    if (methodRegex.test(content)) {
      methods.add(method.toLowerCase())
    }
  }

  if (methods.size === 0) {
    methods.add('post')
  }

  return [...methods].sort()
}

const buildOperation = ({ method, sourceFile }) => ({
  tags: ['internal'],
  summary: `Internal ${method.toUpperCase()} endpoint`,
  operationId: `${method}_${sourceFile.replace(/[^a-zA-Z0-9]/g, '_')}`,
  responses: {
    '200': {
      description: 'Successful response',
      content: {
        'application/json': {
          schema: {
            type: 'object',
            additionalProperties: true,
          },
        },
      },
    },
  },
  'x-internal-source': sourceFile,
})

const buildSpec = async () => {
  const appApiDir = path.join(rootDir, 'app', 'api')
  const pagesApiDir = path.join(rootDir, 'pages', 'api')

  const appRouteFiles = (await walk(appApiDir))
    .map(toProjectRelative)
    .filter((file) => /app\/api\/.+\/route\.(ts|tsx|js|jsx)$/.test(file))

  const pagesApiFiles = (await walk(pagesApiDir))
    .map(toProjectRelative)
    .filter((file) => /pages\/api\/.+\.(ts|tsx|js|jsx)$/.test(file))

  const paths = {}

  for (const file of appRouteFiles.sort()) {
    const absoluteFile = path.join(rootDir, file)
    const content = await fs.readFile(absoluteFile, 'utf8')
    const methods = detectAppRouteMethods(content)
    if (methods.length === 0) continue

    const apiPath = toApiPathFromAppRoute(file)
    const operations = {}
    for (const method of methods) {
      operations[method] = buildOperation({ method, sourceFile: file })
    }

    paths[apiPath] = operations
  }

  for (const file of pagesApiFiles.sort()) {
    const absoluteFile = path.join(rootDir, file)
    const content = await fs.readFile(absoluteFile, 'utf8')
    const methods = detectPagesRouteMethods(content)
    if (methods.length === 0) continue

    const apiPath = toApiPathFromPagesRoute(file)
    const existing = paths[apiPath] || {}

    for (const method of methods) {
      existing[method] = buildOperation({ method, sourceFile: file })
    }

    paths[apiPath] = existing
  }

  const orderedPaths = Object.fromEntries(
    Object.entries(paths).sort(([a], [b]) => a.localeCompare(b))
  )

  const spec = {
    openapi: '3.1.0',
    info: {
      title: 'Ultrawebthinking Internal APIs',
      version: '1.0.0',
      description: 'Auto-generated internal API catalog for App Router and Pages Router endpoints.',
    },
    servers: [
      { url: 'https://ultraweb.ai', description: 'Frontend on Vercel (production)' },
      { url: 'https://api.ultraweb.ai', description: 'Backend microservices (Docker production)' },
      { url: 'http://127.0.0.1:3000', description: 'Frontend local development' },
      { url: 'http://127.0.0.1:8080', description: 'Backend local microservice' },
    ],
    tags: [
      { name: 'internal', description: 'Internal platform endpoints' },
    ],
    paths: orderedPaths,
  }

  return spec
}

const main = async () => {
  const spec = await buildSpec()
  await fs.mkdir(path.dirname(outputPath), { recursive: true })
  await fs.writeFile(outputPath, JSON.stringify(spec, null, 2) + '\n', 'utf8')
  const pathCount = Object.keys(spec.paths).length
  console.log(`OpenAPI generated: ${outputPath} (${pathCount} paths)`)
}

main().catch((error) => {
  console.error('Failed to generate OpenAPI spec:', error)
  process.exit(1)
})
