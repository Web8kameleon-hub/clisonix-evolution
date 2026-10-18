import cors from 'cors'
import express from 'express'

const app = express()

const port = Number(process.env.BACKEND_PORT || process.env.PORT_BACKEND || 8080)
const host = process.env.BACKEND_HOST || '127.0.0.1'

app.use(cors())
app.use(express.json({ limit: '2mb' }))

app.get('/health', (_req, res) => {
	res.status(200).json({
		ok: true,
		service: 'euroweb-backend',
		uptime: process.uptime(),
		timestamp: new Date().toISOString(),
	})
})

app.get('/api/status', (_req, res) => {
	res.status(200).json({
		status: 'running',
		environment: process.env.NODE_ENV || 'development',
		host,
		port,
	})
})

const server = app.listen(port, host, () => {
	console.log(`Backend listening at http://${host}:${port}`)
})

const keepAliveTimer = setInterval(() => {
	if (process.env.NODE_ENV !== 'production') {
		console.log('Backend heartbeat: alive')
	}
}, 60000)

const shutdown = (signal: string) => {
	console.log(`Received ${signal}, shutting down backend...`)
	clearInterval(keepAliveTimer)
	server.close(() => {
		process.exit(0)
	})
}

process.on('SIGINT', () => shutdown('SIGINT'))
process.on('SIGTERM', () => shutdown('SIGTERM'))
