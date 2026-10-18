/**
 * Guardian Status Component
 * Real-time monitoring of Guardian Engine DDoS protection
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0 Industrial
 * @license MIT
 */

'use client'

import { motion } from 'framer-motion'
import React from 'react'

interface GuardianStats {
  totalRequests: number
  blockedIPs: number
  alertsGenerated: number
  criticalThreats: number
  uptime: number
  startTime: number
}

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

interface GuardianStatus {
  status: string
  hostname: string
  stats: GuardianStats
  health: 'healthy' | 'warning' | 'critical'
}

const GuardianMonitor: React.FC = () => {
  // Mock data for demonstration
  const guardianStatus: GuardianStatus = {
    status: 'Guardian Engine Active',
    hostname: 'euroweb-server-01',
    stats: {
      totalRequests: 15847,
      blockedIPs: 23,
      alertsGenerated: 156,
      criticalThreats: 8,
      uptime: 3600000, // 1 hour
      startTime: Date.now() - 3600000
    },
    health: 'healthy'
  }

  const recentLogs: GuardianLog[] = [
    {
      timestamp: Date.now() - 300000,
      ip: '192.168.1.100',
      reason: 'High request rate detected: 105 req/min',
      level: 'critical',
      userAgent: 'Mozilla/5.0',
      requestPath: '/api/test',
      requestRate: 105
    },
    {
      timestamp: Date.now() - 600000,
      ip: '10.0.0.15',
      reason: 'Large payload size detected: 600000 bytes',
      level: 'warn',
      payloadSize: 600000
    },
    {
      timestamp: Date.now() - 900000,
      ip: '203.0.113.45',
      reason: 'Suspicious user agent: python-requests/2.28.1',
      level: 'warn',
      userAgent: 'python-requests/2.28.1'
    }
  ]

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return '#22c55e'
      case 'warning': return '#f59e0b'
      case 'critical': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'info': return '#3b82f6'
      case 'warn': return '#f59e0b'
      case 'critical': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const formatUptime = (uptime: number) => {
    const hours = Math.floor(uptime / 3600000)
    const minutes = Math.floor((uptime % 3600000) / 60000)
    const seconds = Math.floor((uptime % 60000) / 1000)
    return `${hours}h ${minutes}m ${seconds}s`
  }

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <div style={{
      background: 'rgba(15, 20, 25, 0.95)',
      padding: '32px',
      minHeight: '100vh',
      color: '#f8fafc'
    }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          textAlign: 'center',
          marginBottom: '40px'
        }}
      >
        <h1 style={{
          fontSize: '48px',
          fontWeight: 800,
          marginBottom: '16px',
          background: 'linear-gradient(45deg, #d4af37, #f7e08b)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          🛡️ Guardian Engine
        </h1>
        <p style={{
          fontSize: '20px',
          color: '#cbd5e1',
          marginBottom: '24px'
        }}>
          Industrial-Grade DDoS Protection & Network Security Monitor
        </p>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '12px',
          background: `rgba(${guardianStatus.health === 'healthy' ? '34, 197, 94' : guardianStatus.health === 'warning' ? '245, 158, 11' : '239, 68, 68'}, 0.2)`,
          border: `1px solid ${getHealthColor(guardianStatus.health)}`,
          borderRadius: '12px',
          padding: '12px 24px',
          fontSize: '16px',
          fontWeight: 600
        }}>
          <div style={{
            width: '12px',
            height: '12px',
            background: getHealthColor(guardianStatus.health),
            borderRadius: '50%'
          }} />
          System {guardianStatus.health.toUpperCase()}
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '24px',
          marginBottom: '40px'
        }}
      >
        <div style={{
          background: 'rgba(45, 52, 70, 0.8)',
          border: '1px solid rgba(212, 175, 55, 0.3)',
          borderRadius: '16px',
          padding: '24px',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '36px',
            fontWeight: 700,
            color: '#3b82f6',
            marginBottom: '8px'
          }}>
            {guardianStatus.stats.totalRequests.toLocaleString()}
          </div>
          <div style={{
            fontSize: '14px',
            color: '#cbd5e1',
            textTransform: 'uppercase',
            letterSpacing: '1px'
          }}>
            Total Requests
          </div>
        </div>

        <div style={{
          background: 'rgba(45, 52, 70, 0.8)',
          border: '1px solid rgba(212, 175, 55, 0.3)',
          borderRadius: '16px',
          padding: '24px',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '36px',
            fontWeight: 700,
            color: '#ef4444',
            marginBottom: '8px'
          }}>
            {guardianStatus.stats.blockedIPs}
          </div>
          <div style={{
            fontSize: '14px',
            color: '#cbd5e1',
            textTransform: 'uppercase',
            letterSpacing: '1px'
          }}>
            Blocked IPs
          </div>
        </div>

        <div style={{
          background: 'rgba(45, 52, 70, 0.8)',
          border: '1px solid rgba(212, 175, 55, 0.3)',
          borderRadius: '16px',
          padding: '24px',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '36px',
            fontWeight: 700,
            color: '#f59e0b',
            marginBottom: '8px'
          }}>
            {guardianStatus.stats.alertsGenerated}
          </div>
          <div style={{
            fontSize: '14px',
            color: '#cbd5e1',
            textTransform: 'uppercase',
            letterSpacing: '1px'
          }}>
            Alerts Generated
          </div>
        </div>

        <div style={{
          background: 'rgba(45, 52, 70, 0.8)',
          border: '1px solid rgba(212, 175, 55, 0.3)',
          borderRadius: '16px',
          padding: '24px',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '36px',
            fontWeight: 700,
            color: '#22c55e',
            marginBottom: '8px'
          }}>
            {formatUptime(guardianStatus.stats.uptime)}
          </div>
          <div style={{
            fontSize: '14px',
            color: '#cbd5e1',
            textTransform: 'uppercase',
            letterSpacing: '1px'
          }}>
            System Uptime
          </div>
        </div>
      </motion.div>

      {/* Recent Logs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.5 }}
        style={{
          background: 'rgba(45, 52, 70, 0.8)',
          border: '1px solid rgba(212, 175, 55, 0.3)',
          borderRadius: '16px',
          padding: '24px'
        }}
      >
        <h2 style={{
          fontSize: '24px',
          fontWeight: 700,
          color: '#d4af37',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          📊 Recent Security Events
        </h2>

        <div style={{
          display: 'grid',
          gap: '16px'
        }}>
          {recentLogs.map((log, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index, duration: 0.3 }}
              style={{
                background: 'rgba(15, 20, 25, 0.6)',
                border: `1px solid ${getLevelColor(log.level)}`,
                borderRadius: '12px',
                padding: '16px',
                display: 'grid',
                gridTemplateColumns: 'auto 1fr auto',
                alignItems: 'center',
                gap: '16px'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <div style={{
                  width: '8px',
                  height: '8px',
                  background: getLevelColor(log.level),
                  borderRadius: '50%'
                }} />
                <span style={{
                  color: getLevelColor(log.level),
                  fontSize: '12px',
                  fontWeight: 600,
                  textTransform: 'uppercase'
                }}>
                  {log.level}
                </span>
              </div>

              <div>
                <div style={{
                  color: '#f8fafc',
                  fontSize: '14px',
                  fontWeight: 600,
                  marginBottom: '4px'
                }}>
                  {log.reason}
                </div>
                <div style={{
                  color: '#94a3b8',
                  fontSize: '12px'
                }}>
                  IP: {log.ip} {log.userAgent && `• UA: ${log.userAgent}`} {log.requestPath && `• Path: ${log.requestPath}`}
                </div>
              </div>

              <div style={{
                color: '#64748b',
                fontSize: '12px',
                textAlign: 'right'
              }}>
                {formatTimestamp(log.timestamp)}
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Control Panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
        style={{
          marginTop: '40px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px'
        }}
      >
        <button style={{
          background: 'rgba(34, 197, 94, 0.2)',
          border: '1px solid #22c55e',
          borderRadius: '12px',
          color: '#22c55e',
          padding: '16px 24px',
          fontSize: '14px',
          fontWeight: 600,
          cursor: 'pointer'
        }}>
          🔄 Refresh Logs
        </button>

        <button style={{
          background: 'rgba(59, 130, 246, 0.2)',
          border: '1px solid #3b82f6',
          borderRadius: '12px',
          color: '#3b82f6',
          padding: '16px 24px',
          fontSize: '14px',
          fontWeight: 600,
          cursor: 'pointer'
        }}>
          📋 Export Report
        </button>

        <button style={{
          background: 'rgba(212, 175, 55, 0.2)',
          border: '1px solid #d4af37',
          borderRadius: '12px',
          color: '#d4af37',
          padding: '16px 24px',
          fontSize: '14px',
          fontWeight: 600,
          cursor: 'pointer'
        }}>
          ⚙️ Configuration
        </button>

        <button style={{
          background: 'rgba(239, 68, 68, 0.2)',
          border: '1px solid #ef4444',
          borderRadius: '12px',
          color: '#ef4444',
          padding: '16px 24px',
          fontSize: '14px',
          fontWeight: 600,
          cursor: 'pointer'
        }}>
          🛑 Emergency Block
        </button>
      </motion.div>
    </div>
  )
}

export default GuardianMonitor
