/**
 * Guardian Express Middleware
 * Integrates Guardian Engine with Express.js requests
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0 Industrial
 * @license MIT
 */

import { Request, Response, NextFunction } from 'express'
import { monitorRequest, getGuardianStatus, getLogs, getBlockedIPs } from './guardian'

/**
 * Express middleware for Guardian protection
 */
export function guardianMiddleware(req: Request, res: Response, next: NextFunction): void {
  const clientIP = req.ip || req.connection.remoteAddress || 'unknown'
  const payloadSize = req.get('content-length') ? parseInt(req.get('content-length')!) : 0
  const userAgent = req.get('user-agent') || 'unknown'
  const requestPath = req.path

  // Simple rate limiting based on request timestamp
  const now = Date.now()
  const requestRate = 60 // This would be calculated based on recent requests

  // Monitor the request
  const isAllowed = monitorRequest(clientIP, payloadSize, requestRate, userAgent, requestPath)

  if (!isAllowed) {
    res.status(429).json({
      error: 'Request blocked by Guardian',
      message: 'Your request has been blocked due to suspicious activity',
      code: 'GUARDIAN_BLOCK',
      timestamp: new Date().toISOString()
    })
    return
  }

  // Add Guardian headers to response
  res.setHeader('X-Guardian-Status', 'Protected')
  res.setHeader('X-Guardian-Version', '8.0.0')

  next()
}

/**
 * Guardian dashboard route handler
 */
export function guardianDashboard(req: Request, res: Response): void {
  const status = getGuardianStatus()
  const recentLogs = getLogs(undefined, 100) // Last 100 logs
  const blockedIPs = getBlockedIPs()

  res.json({
    guardian: status,
    logs: recentLogs,
    blockedIPs,
    timestamp: new Date().toISOString()
  })
}

/**
 * Guardian logs route handler
 */
export function guardianLogsHandler(req: Request, res: Response): void {
  const { level, limit, since } = req.query
  
  const parsedLimit = limit ? parseInt(limit as string) : undefined
  const parsedSince = since ? parseInt(since as string) : undefined
  
  const logs = getLogs(level as any, parsedLimit, parsedSince)
  
  res.json({
    logs,
    total: logs.length,
    timestamp: new Date().toISOString()
  })
}

/**
 * Guardian stats route handler
 */
export function guardianStatsHandler(req: Request, res: Response): void {
  const status = getGuardianStatus()
  
  res.json({
    stats: status.stats,
    health: status.health,
    hostname: status.hostname,
    timestamp: new Date().toISOString()
  })
}
