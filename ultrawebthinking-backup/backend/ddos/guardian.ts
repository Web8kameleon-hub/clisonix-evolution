/**
 * Guardian Engine – Web8 DDoS Defense & Network Integrity Monitor
 * Location: backend/ddos/guardian.ts
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0 Industrial
 * @license MIT
 */

import * as os from 'os'
import { createHash } from 'crypto'
import { writeFileSync, existsSync, mkdirSync } from 'fs'
import * as path from 'path'

interface GuardianLog {
  timestamp: number
  ip: string
  reason: string
  level: 'info' | 'warn' | 'critical'
  userAgent?: string
  requestPath?: string
  payloadSize?: number
  requestRate?: number
}

interface GuardianStats {
  totalRequests: number
  blockedIPs: number
  alertsGenerated: number
  criticalThreats: number
  uptime: number
  startTime: number
}

interface GuardianConfig {
  maxPayloadSize: number
  maxRequestRate: number
  blockDuration: number
  logRetentionDays: number
  enableAutoBlock: boolean
}

const guardianLogs: GuardianLog[] = []
const blockedIPs = new Set<string>()
const requestCounts = new Map<string, number[]>()

const defaultConfig: GuardianConfig = {
  maxPayloadSize: 512000, // 512KB
  maxRequestRate: 100, // requests per minute
  blockDuration: 3600000, // 1 hour in ms
  logRetentionDays: 30,
  enableAutoBlock: true
}

let guardianStats: GuardianStats = {
  totalRequests: 0,
  blockedIPs: 0,
  alertsGenerated: 0,
  criticalThreats: 0,
  uptime: 0,
  startTime: Date.now()
}

// Ensure blocked directory exists
const blockedDir = path.join(process.cwd(), 'blocked')
if (!existsSync(blockedDir)) {
  mkdirSync(blockedDir, { recursive: true })
}

/**
 * Monitor incoming request for suspicious activity
 */
export function monitorRequest(
  ip: string, 
  payloadSize: number, 
  requestRate: number,
  userAgent?: string,
  requestPath?: string
): boolean {
  const now = Date.now()
  guardianStats.totalRequests++
  guardianStats.uptime = now - guardianStats.startTime

  // Check if IP is already blocked
  if (blockedIPs.has(ip)) {
    addLog(ip, 'Request from blocked IP', 'critical', {
      userAgent,
      requestPath,
      payloadSize,
      requestRate
    })
    return false
  }

  let reason = ''
  let level: GuardianLog['level'] = 'info'
  let shouldBlock = false

  // Check payload size
  if (payloadSize > defaultConfig.maxPayloadSize) {
    reason = `Large payload size detected: ${payloadSize} bytes`
    level = 'warn'
    if (payloadSize > defaultConfig.maxPayloadSize * 2) {
      level = 'critical'
      shouldBlock = true
    }
  }

  // Check request rate
  updateRequestCount(ip)
  const currentRate = getRequestRate(ip)
  if (currentRate > defaultConfig.maxRequestRate) {
    reason = `High request rate detected: ${currentRate} req/min`
    level = 'critical'
    shouldBlock = true
  }

  // Check for suspicious patterns
  if (userAgent && isSuspiciousUserAgent(userAgent)) {
    reason = `Suspicious user agent: ${userAgent}`
    level = 'warn'
  }

  if (requestPath && isSuspiciousPath(requestPath)) {
    reason = `Suspicious request path: ${requestPath}`
    level = 'warn'
  }

  // Log if suspicious activity detected
  if (reason) {
    addLog(ip, reason, level, {
      userAgent,
      requestPath,
      payloadSize,
      requestRate: currentRate
    })

    if (level === 'critical') {
      guardianStats.criticalThreats++
    }
    guardianStats.alertsGenerated++

    // Block IP if configured and conditions met
    if (shouldBlock && defaultConfig.enableAutoBlock) {
      blockIP(ip, reason)
      return false
    }
  }

  return true
}

/**
 * Add log entry
 */
function addLog(
  ip: string, 
  reason: string, 
  level: GuardianLog['level'],
  metadata?: {
    userAgent?: string
    requestPath?: string
    payloadSize?: number
    requestRate?: number
  }
): void {
  const log: GuardianLog = {
    timestamp: Date.now(),
    ip,
    reason,
    level,
    ...metadata
  }
  
  guardianLogs.push(log)
  
  // Keep only recent logs (memory management)
  const maxLogs = 10000
  if (guardianLogs.length > maxLogs) {
    guardianLogs.splice(0, guardianLogs.length - maxLogs)
  }
}

/**
 * Update request count for IP tracking
 */
function updateRequestCount(ip: string): void {
  const now = Date.now()
  const minute = Math.floor(now / 60000) * 60000 // Round to minute
  
  if (!requestCounts.has(ip)) {
    requestCounts.set(ip, [])
  }
  
  const counts = requestCounts.get(ip)!
  counts.push(now)
  
  // Remove old entries (older than 1 minute)
  const cutoff = now - 60000
  const filtered = counts.filter(time => time > cutoff)
  requestCounts.set(ip, filtered)
}

/**
 * Get current request rate for IP
 */
function getRequestRate(ip: string): number {
  const counts = requestCounts.get(ip) || []
  return counts.length
}

/**
 * Check if user agent is suspicious
 */
function isSuspiciousUserAgent(userAgent: string): boolean {
  const suspiciousPatterns = [
    /bot/i,
    /crawler/i,
    /scanner/i,
    /python/i,
    /curl/i,
    /wget/i,
    /sqlmap/i,
    /nikto/i
  ]
  
  return suspiciousPatterns.some(pattern => pattern.test(userAgent))
}

/**
 * Check if request path is suspicious
 */
function isSuspiciousPath(path: string): boolean {
  const suspiciousPaths = [
    /\/admin/i,
    /\/wp-admin/i,
    /\/phpmyadmin/i,
    /\.php$/i,
    /\.asp$/i,
    /\.jsp$/i,
    /\/etc\/passwd/i,
    /\/proc\//i,
    /\.\./,
    /<script/i,
    /javascript:/i,
    /eval\(/i
  ]
  
  return suspiciousPaths.some(pattern => pattern.test(path))
}

/**
 * Block IP address
 */
function blockIP(ip: string, reason: string): void {
  const now = new Date()
  const hash = createHash('sha256').update(ip).digest('hex')
  const blockFile = path.join(blockedDir, `${hash}.block`)
  
  const blockData = {
    ip,
    reason,
    blockedAt: now.toISOString(),
    expiresAt: new Date(now.getTime() + defaultConfig.blockDuration).toISOString()
  }
  
  try {
    writeFileSync(blockFile, JSON.stringify(blockData, null, 2))
    blockedIPs.add(ip)
    guardianStats.blockedIPs++
    
    console.log(`🚨 Guardian blocked IP: ${ip} (${reason})`)
    
    // Auto-unblock after duration
    setTimeout(() => {
      unblockIP(ip)
    }, defaultConfig.blockDuration)
    
  } catch (error) {
    console.error(`Failed to block IP ${ip}:`, error)
  }
}

/**
 * Unblock IP address
 */
function unblockIP(ip: string): void {
  const hash = createHash('sha256').update(ip).digest('hex')
  const blockFile = path.join(blockedDir, `${hash}.block`)
  
  try {
    if (existsSync(blockFile)) {
      // In a real implementation, you'd delete the file
      // For now, we'll just remove from memory
      blockedIPs.delete(ip)
      console.log(`✅ Guardian unblocked IP: ${ip}`)
    }
  } catch (error) {
    console.error(`Failed to unblock IP ${ip}:`, error)
  }
}

/**
 * Get Guardian system status
 */
export function getGuardianStatus(): {
  status: string
  hostname: string
  stats: GuardianStats
  config: GuardianConfig
  health: 'healthy' | 'warning' | 'critical'
} {
  const criticalThreatsPercentage = guardianStats.totalRequests > 0 
    ? (guardianStats.criticalThreats / guardianStats.totalRequests) * 100 
    : 0

  let health: 'healthy' | 'warning' | 'critical' = 'healthy'
  if (criticalThreatsPercentage > 10) {
    health = 'critical'
  } else if (criticalThreatsPercentage > 5) {
    health = 'warning'
  }

  return {
    status: `Guardian running on ${os.hostname()} with ${guardianLogs.length} alerts`,
    hostname: os.hostname(),
    stats: {
      ...guardianStats,
      uptime: Date.now() - guardianStats.startTime
    },
    config: defaultConfig,
    health
  }
}

/**
 * Get Guardian logs with filtering
 */
export function getLogs(
  level?: GuardianLog['level'], 
  limit?: number,
  since?: number
): GuardianLog[] {
  let filteredLogs = guardianLogs

  // Filter by level
  if (level) {
    filteredLogs = filteredLogs.filter(log => log.level === level)
  }

  // Filter by time
  if (since) {
    filteredLogs = filteredLogs.filter(log => log.timestamp >= since)
  }

  // Sort by timestamp (newest first)
  filteredLogs.sort((a, b) => b.timestamp - a.timestamp)

  // Limit results
  if (limit) {
    filteredLogs = filteredLogs.slice(0, limit)
  }

  return filteredLogs
}

/**
 * Get blocked IPs list
 */
export function getBlockedIPs(): string[] {
  return Array.from(blockedIPs)
}

/**
 * Update Guardian configuration
 */
export function updateConfig(newConfig: Partial<GuardianConfig>): void {
  Object.assign(defaultConfig, newConfig)
  console.log('🔧 Guardian configuration updated:', newConfig)
}

/**
 * Reset Guardian stats
 */
export function resetStats(): void {
  guardianStats = {
    totalRequests: 0,
    blockedIPs: 0,
    alertsGenerated: 0,
    criticalThreats: 0,
    uptime: 0,
    startTime: Date.now()
  }
  guardianLogs.length = 0
  blockedIPs.clear()
  requestCounts.clear()
  console.log('🔄 Guardian stats reset')
}

/**
 * Manual IP block/unblock functions
 */
export function manualBlockIP(ip: string, reason: string = 'Manual block'): void {
  blockIP(ip, reason)
}

export function manualUnblockIP(ip: string): void {
  unblockIP(ip)
}

// Initialize Guardian
console.log('🛡️ Guardian Engine initialized')
console.log(`📊 Monitoring thresholds: Payload=${defaultConfig.maxPayloadSize}B, Rate=${defaultConfig.maxRequestRate}req/min`)
