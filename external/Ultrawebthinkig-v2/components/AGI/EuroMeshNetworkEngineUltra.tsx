/**
 * EuroMesh Network Engine Ultra - Distributed Mesh Network Intelligence
 * EuroWeb Platform - Advanced Mesh Networking & Distributed Systems AI
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.1.0 Ultra
 * @license MIT
 */

'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface MeshNode {
  id: string
  name: string
  type: 'gateway' | 'relay' | 'endpoint' | 'bridge'
  status: 'online' | 'offline' | 'degraded' | 'maintenance'
  location: string
  connections: string[]
  signalStrength: number
  bandwidth: number
  latency: number
  uptime: number
  load: number
}

interface NetworkMetrics {
  totalNodes: number
  activeNodes: number
  networkHealth: number
  throughput: number
  avgLatency: number
  packetLoss: number
  coverage: number
  redundancy: number
}

interface MeshAlert {
  id: string
  type: 'connection' | 'performance' | 'security' | 'maintenance'
  severity: 'low' | 'medium' | 'high' | 'critical'
  nodeId?: string
  message: string
  timestamp: Date
}

const EuroMeshNetworkEngineUltra: React.FC = () => {
  const [metrics, setMetrics] = useState<NetworkMetrics>({
    totalNodes: 24,
    activeNodes: 22,
    networkHealth: 96.8,
    throughput: 847.5,
    avgLatency: 12.3,
    packetLoss: 0.02,
    coverage: 98.5,
    redundancy: 94.2
  })

  const [nodes, setNodes] = useState<MeshNode[]>([
    {
      id: 'GW-001',
      name: 'Main Gateway',
      type: 'gateway',
      status: 'online',
      location: 'Central Hub',
      connections: ['RL-001', 'RL-002', 'BG-001'],
      signalStrength: 98,
      bandwidth: 1000,
      latency: 5.2,
      uptime: 99.9,
      load: 45
    },
    {
      id: 'RL-001',
      name: 'Relay North',
      type: 'relay',
      status: 'online',
      location: 'North Sector',
      connections: ['GW-001', 'EP-001', 'EP-002'],
      signalStrength: 87,
      bandwidth: 500,
      latency: 8.1,
      uptime: 99.2,
      load: 62
    },
    {
      id: 'RL-002',
      name: 'Relay South',
      type: 'relay',
      status: 'online',
      location: 'South Sector',
      connections: ['GW-001', 'EP-003', 'EP-004'],
      signalStrength: 92,
      bandwidth: 500,
      latency: 7.5,
      uptime: 99.7,
      load: 38
    },
    {
      id: 'BG-001',
      name: 'Bridge East',
      type: 'bridge',
      status: 'online',
      location: 'East Connection',
      connections: ['GW-001', 'RL-003'],
      signalStrength: 83,
      bandwidth: 750,
      latency: 15.2,
      uptime: 98.5,
      load: 71
    },
    {
      id: 'EP-001',
      name: 'Endpoint Alpha',
      type: 'endpoint',
      status: 'online',
      location: 'Building A',
      connections: ['RL-001'],
      signalStrength: 76,
      bandwidth: 100,
      latency: 18.3,
      uptime: 97.8,
      load: 25
    },
    {
      id: 'EP-002',
      name: 'Endpoint Beta',
      type: 'endpoint',
      status: 'degraded',
      location: 'Building B',
      connections: ['RL-001'],
      signalStrength: 54,
      bandwidth: 100,
      latency: 34.7,
      uptime: 95.2,
      load: 88
    },
    {
      id: 'EP-003',
      name: 'Endpoint Gamma',
      type: 'endpoint',
      status: 'offline',
      location: 'Building C',
      connections: [],
      signalStrength: 0,
      bandwidth: 0,
      latency: 0,
      uptime: 0,
      load: 0
    },
    {
      id: 'EP-004',
      name: 'Endpoint Delta',
      type: 'endpoint',
      status: 'maintenance',
      location: 'Building D',
      connections: [],
      signalStrength: 0,
      bandwidth: 0,
      latency: 0,
      uptime: 0,
      load: 0
    }
  ])

  const [alerts, setAlerts] = useState<MeshAlert[]>([
    {
      id: '1',
      type: 'performance',
      severity: 'medium',
      nodeId: 'EP-002',
      message: 'High latency detected on Endpoint Beta',
      timestamp: new Date()
    },
    {
      id: '2',
      type: 'connection',
      severity: 'high',
      nodeId: 'EP-003',
      message: 'Node EP-003 offline - connection lost',
      timestamp: new Date()
    },
    {
      id: '3',
      type: 'maintenance',
      severity: 'low',
      nodeId: 'EP-004',
      message: 'Scheduled maintenance on Endpoint Delta',
      timestamp: new Date()
    }
  ])

  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'topology' | 'metrics' | 'analytics'>('topology')

  // Real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        networkHealth: Math.max(95, Math.min(100, prev.networkHealth + (Math.random() - 0.5) * 1)),
        throughput: Math.max(800, prev.throughput + (Math.random() - 0.5) * 50),
        avgLatency: Math.max(10, prev.avgLatency + (Math.random() - 0.5) * 2),
        packetLoss: Math.max(0, Math.min(0.1, prev.packetLoss + (Math.random() - 0.5) * 0.01)),
        coverage: Math.max(95, Math.min(100, prev.coverage + (Math.random() - 0.5) * 0.5)),
        redundancy: Math.max(90, Math.min(100, prev.redundancy + (Math.random() - 0.5) * 1))
      }))

      // Update node metrics
      setNodes(prev => prev.map(node => {
        if (node.status === 'online' || node.status === 'degraded') {
          return {
            ...node,
            signalStrength: Math.max(30, Math.min(100, node.signalStrength + (Math.random() - 0.5) * 5)),
            latency: Math.max(5, node.latency + (Math.random() - 0.5) * 3),
            load: Math.max(0, Math.min(100, node.load + (Math.random() - 0.5) * 10))
          }
        }
        return node
      }))
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return '#22c55e'
      case 'offline': return '#6b7280'
      case 'degraded': return '#f59e0b'
      case 'maintenance': return '#3b82f6'
      default: return '#6b7280'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#dc2626'
      case 'high': return '#ef4444'
      case 'medium': return '#f59e0b'
      case 'low': return '#22c55e'
      default: return '#6b7280'
    }
  }

  const getNodeTypeIcon = (type: string) => {
    switch (type) {
      case 'gateway': return '🌐'
      case 'relay': return '📡'
      case 'endpoint': return '📱'
      case 'bridge': return '🌉'
      default: return '🔗'
    }
  }

  const getSignalIcon = (strength: number) => {
    if (strength > 80) return '📶'
    if (strength > 60) return '📶'
    if (strength > 40) return '📶'
    if (strength > 20) return '📶'
    return '📶'
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e3a8a 0%, #3730a3 25%, #4338ca 50%, #5b21b6 75%, #7c3aed 100%)',
      color: '#f8fafc',
      padding: '24px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          background: 'rgba(0, 0, 0, 0.4)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          borderRadius: '16px',
          padding: '24px',
          marginBottom: '24px',
          textAlign: 'center'
        }}
      >
        <h1 style={{
          fontSize: '36px',
          fontWeight: 800,
          background: 'linear-gradient(45deg, #6366f1, #8b5cf6, #a855f7)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          color: 'transparent',
          margin: 0,
          marginBottom: '8px'
        }}>
          🕸️ EuroMesh Network Engine Ultra
        </h1>
        <p style={{
          margin: 0,
          fontSize: '18px',
          color: '#e2e8f0',
          fontWeight: 500
        }}>
          Distributed Mesh Network Intelligence & Management
        </p>
      </motion.div>

      {/* Mode Selector */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        style={{
          background: 'rgba(0, 0, 0, 0.4)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          borderRadius: '12px',
          padding: '16px',
          marginBottom: '24px',
          display: 'flex',
          justifyContent: 'center',
          gap: '12px'
        }}
      >
        {(['topology', 'metrics', 'analytics'] as const).map(mode => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            style={{
              background: viewMode === mode ? '#6366f1' : 'rgba(0, 0, 0, 0.3)',
              color: viewMode === mode ? '#fff' : '#e2e8f0',
              border: 'none',
              padding: '8px 20px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 600,
              textTransform: 'capitalize',
              transition: 'all 0.2s ease'
            }}
          >
            {mode}
          </button>
        ))}
      </motion.div>

      {/* Network Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        style={{
          background: 'rgba(0, 0, 0, 0.4)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          borderRadius: '16px',
          padding: '24px',
          marginBottom: '24px'
        }}
      >
        <h2 style={{
          fontSize: '24px',
          fontWeight: 700,
          color: '#f8fafc',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          📊 Network Status
          <span style={{
            fontSize: '14px',
            background: 'rgba(34, 197, 94, 0.2)',
            color: '#22c55e',
            padding: '4px 8px',
            borderRadius: '6px',
            fontWeight: 600
          }}>
            {metrics.activeNodes}/{metrics.totalNodes} Active
          </span>
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px'
        }}>
          {Object.entries(metrics).map(([key, value], index) => (
            <motion.div
              key={key}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
              whileHover={{ scale: 1.02 }}
              style={{
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid rgba(99, 102, 241, 0.5)',
                borderRadius: '12px',
                padding: '20px'
              }}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '12px'
              }}>
                <span style={{
                  fontSize: '14px',
                  fontWeight: 600,
                  color: '#f8fafc',
                  textTransform: 'capitalize'
                }}>
                  {key.replace(/([A-Z])/g, ' $1').toLowerCase()}
                </span>
                <span style={{
                  fontSize: '18px',
                  color: '#6366f1',
                  fontWeight: 700
                }}>
                  {key.includes('Nodes') ? value :
                   key.includes('Health') || key.includes('Coverage') || key.includes('Redundancy') ? `${value.toFixed(1)}%` :
                   key.includes('Throughput') ? `${value.toFixed(1)} Mbps` :
                   key.includes('Latency') ? `${value.toFixed(1)} ms` :
                   key.includes('Loss') ? `${(value * 100).toFixed(2)}%` :
                   value}
                </span>
              </div>

              <div style={{
                fontSize: '12px',
                color: '#cbd5e1',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <span>
                  {key === 'totalNodes' || key === 'activeNodes' ? '🔗' :
                   key === 'networkHealth' ? '💚' :
                   key === 'throughput' ? '🚀' :
                   key === 'avgLatency' ? '⏱️' :
                   key === 'packetLoss' ? '📦' :
                   key === 'coverage' ? '📡' : '🔄'}
                </span>
                <span>
                  {key.includes('Health') ? 
                   (value > 95 ? 'Excellent' : value > 90 ? 'Good' : value > 80 ? 'Fair' : 'Poor') :
                   key.includes('Latency') ?
                   (value < 15 ? 'Optimal' : value < 30 ? 'Good' : 'High') :
                   key.includes('Loss') ?
                   (value < 0.01 ? 'Minimal' : value < 0.05 ? 'Low' : 'High') :
                   'Monitored'}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Topology Mode */}
      {viewMode === 'topology' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          style={{
            background: 'rgba(0, 0, 0, 0.4)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px'
          }}
        >
          <h2 style={{
            fontSize: '24px',
            fontWeight: 700,
            color: '#f8fafc',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            🕸️ Network Topology
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '20px'
          }}>
            {nodes.map((node, index) => (
              <motion.div
                key={node.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
                whileHover={{ scale: 1.02 }}
                onClick={() => setSelectedNode(selectedNode === node.id ? null : node.id)}
                style={{
                  background: selectedNode === node.id ? 
                    'rgba(99, 102, 241, 0.2)' : 'rgba(0, 0, 0, 0.3)',
                  border: `1px solid ${getStatusColor(node.status)}`,
                  borderRadius: '12px',
                  padding: '20px',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '12px'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    <span style={{ fontSize: '20px' }}>{getNodeTypeIcon(node.type)}</span>
                    <span style={{
                      fontSize: '16px',
                      fontWeight: 600,
                      color: '#f8fafc'
                    }}>
                      {node.name}
                    </span>
                  </div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <span style={{ fontSize: '14px' }}>{getSignalIcon(node.signalStrength)}</span>
                    <div style={{
                      width: '12px',
                      height: '12px',
                      background: getStatusColor(node.status),
                      borderRadius: '50%',
                      animation: node.status === 'online' ? 'pulse 2s infinite' : 'none'
                    }} />
                  </div>
                </div>

                <div style={{
                  fontSize: '14px',
                  color: '#cbd5e1',
                  marginBottom: '8px'
                }}>
                  📍 {node.location} | {node.type.charAt(0).toUpperCase() + node.type.slice(1)}
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '8px',
                  marginBottom: '12px'
                }}>
                  <div>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>Signal</div>
                    <div style={{ fontSize: '14px', color: '#6366f1', fontWeight: 600 }}>
                      {node.signalStrength}%
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>Latency</div>
                    <div style={{ fontSize: '14px', color: '#6366f1', fontWeight: 600 }}>
                      {node.latency.toFixed(1)}ms
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>Load</div>
                    <div style={{ fontSize: '14px', color: '#6366f1', fontWeight: 600 }}>
                      {node.load}%
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>Uptime</div>
                    <div style={{ fontSize: '14px', color: '#6366f1', fontWeight: 600 }}>
                      {node.uptime.toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div style={{
                  fontSize: '12px',
                  color: '#94a3b8',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span>Connections: {node.connections.length}</span>
                  <span style={{
                    background: `rgba(${getStatusColor(node.status).slice(1)}, 0.2)`,
                    color: getStatusColor(node.status),
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontWeight: 600,
                    textTransform: 'uppercase'
                  }}>
                    {node.status}
                  </span>
                </div>

                {/* Expanded Details */}
                {selectedNode === node.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    style={{
                      marginTop: '12px',
                      paddingTop: '12px',
                      borderTop: '1px solid rgba(99, 102, 241, 0.3)'
                    }}
                  >
                    <div style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.5' }}>
                      <strong>Node Details:</strong><br />
                      ID: {node.id}<br />
                      Type: {node.type.charAt(0).toUpperCase() + node.type.slice(1)}<br />
                      Bandwidth: {node.bandwidth} Mbps<br />
                      Connected to: {node.connections.join(', ') || 'None'}
                    </div>
                  </motion.div>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Metrics Mode */}
      {viewMode === 'metrics' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          style={{
            background: 'rgba(0, 0, 0, 0.4)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px'
          }}
        >
          <h2 style={{
            fontSize: '24px',
            fontWeight: 700,
            color: '#f8fafc',
            marginBottom: '20px'
          }}>
            📈 Performance Metrics
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '20px'
          }}>
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid rgba(99, 102, 241, 0.5)',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center'
            }}>
              <h4 style={{ color: '#f8fafc', marginBottom: '16px' }}>Network Throughput</h4>
              <div style={{
                height: '200px',
                background: 'linear-gradient(45deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1))',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#cbd5e1'
              }}>
                🚀 Real-time Throughput Chart
              </div>
            </div>
            
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid rgba(99, 102, 241, 0.5)',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center'
            }}>
              <h4 style={{ color: '#f8fafc', marginBottom: '16px' }}>Latency Distribution</h4>
              <div style={{
                height: '200px',
                background: 'linear-gradient(45deg, rgba(34, 197, 94, 0.1), rgba(16, 185, 129, 0.1))',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#cbd5e1'
              }}>
                ⏱️ Latency Heatmap
              </div>
            </div>
            
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid rgba(99, 102, 241, 0.5)',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center'
            }}>
              <h4 style={{ color: '#f8fafc', marginBottom: '16px' }}>Signal Strength Map</h4>
              <div style={{
                height: '200px',
                background: 'linear-gradient(45deg, rgba(245, 158, 11, 0.1), rgba(251, 191, 36, 0.1))',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#cbd5e1'
              }}>
                📶 Coverage Map
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Analytics Mode */}
      {viewMode === 'analytics' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          style={{
            background: 'rgba(0, 0, 0, 0.4)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px',
            textAlign: 'center'
          }}
        >
          <h2 style={{
            fontSize: '24px',
            fontWeight: 700,
            color: '#f8fafc',
            marginBottom: '20px'
          }}>
            🔬 Advanced Network Analytics
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
            gap: '20px'
          }}>
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid rgba(99, 102, 241, 0.5)',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center'
            }}>
              <h4 style={{ color: '#f8fafc', marginBottom: '16px' }}>Traffic Flow Analysis</h4>
              <div style={{
                height: '200px',
                background: 'linear-gradient(45deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1))',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#cbd5e1'
              }}>
                🌊 Traffic Visualization
              </div>
            </div>
            
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid rgba(99, 102, 241, 0.5)',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center'
            }}>
              <h4 style={{ color: '#f8fafc', marginBottom: '16px' }}>Mesh Optimization</h4>
              <div style={{
                height: '200px',
                background: 'linear-gradient(45deg, rgba(34, 197, 94, 0.1), rgba(16, 185, 129, 0.1))',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#cbd5e1'
              }}>
                ⚡ Auto-optimization Engine
              </div>
            </div>
            
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid rgba(99, 102, 241, 0.5)',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center'
            }}>
              <h4 style={{ color: '#f8fafc', marginBottom: '16px' }}>Predictive Analytics</h4>
              <div style={{
                height: '200px',
                background: 'linear-gradient(45deg, rgba(245, 158, 11, 0.1), rgba(251, 191, 36, 0.1))',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#cbd5e1'
              }}>
                🔮 AI Predictions
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Alerts Panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        style={{
          background: 'rgba(0, 0, 0, 0.4)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          borderRadius: '16px',
          padding: '24px',
          marginBottom: '24px'
        }}
      >
        <h3 style={{
          fontSize: '20px',
          fontWeight: 600,
          color: '#f8fafc',
          marginBottom: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          🚨 Network Alerts
          {alerts.length > 0 && (
            <span style={{
              fontSize: '12px',
              background: 'rgba(99, 102, 241, 0.2)',
              color: '#6366f1',
              padding: '2px 6px',
              borderRadius: '4px',
              fontWeight: 600
            }}>
              {alerts.length}
            </span>
          )}
        </h3>

        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '12px'
        }}>
          {alerts.length === 0 ? (
            <div style={{
              textAlign: 'center',
              color: '#cbd5e1',
              padding: '20px',
              fontSize: '14px'
            }}>
              ✅ All mesh network nodes operating normally
            </div>
          ) : (
            alerts.map((alert, index) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.05 * index }}
                style={{
                  background: `rgba(${getSeverityColor(alert.severity).slice(1)}, 0.1)`,
                  border: `1px solid ${getSeverityColor(alert.severity)}`,
                  borderRadius: '8px',
                  padding: '16px'
                }}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '8px'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    <span style={{ fontSize: '16px' }}>
                      {alert.type === 'connection' ? '🔗' :
                       alert.type === 'performance' ? '⚡' :
                       alert.type === 'security' ? '🔒' : '🔧'}
                    </span>
                    <span style={{
                      fontSize: '14px',
                      fontWeight: 600,
                      color: getSeverityColor(alert.severity),
                      textTransform: 'uppercase'
                    }}>
                      {alert.severity}
                    </span>
                    <span style={{
                      fontSize: '12px',
                      background: 'rgba(0, 0, 0, 0.3)',
                      color: '#cbd5e1',
                      padding: '2px 6px',
                      borderRadius: '4px'
                    }}>
                      {alert.type}
                    </span>
                  </div>
                  <span style={{
                    fontSize: '12px',
                    color: '#94a3b8'
                  }}>
                    {alert.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                <div style={{
                  fontSize: '14px',
                  color: '#f8fafc',
                  marginBottom: '4px'
                }}>
                  {alert.message}
                </div>
                {alert.nodeId && (
                  <div style={{
                    fontSize: '12px',
                    color: '#cbd5e1'
                  }}>
                    🔗 Node: {alert.nodeId}
                  </div>
                )}
              </motion.div>
            ))
          )}
        </div>
      </motion.div>

      {/* Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        style={{
          padding: '16px',
          background: 'rgba(0, 0, 0, 0.4)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          borderRadius: '12px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '14px'
        }}
      >
        <div style={{ color: '#6366f1' }}>
          🕸️ EuroMesh Network Active - Distributed Intelligence Online
        </div>
        <div style={{ color: '#cbd5e1' }}>
          📡 EuroWeb Platform v8.1.0 | Nodes: {metrics.activeNodes}/{metrics.totalNodes} | Health: {metrics.networkHealth.toFixed(1)}%
        </div>
        <div style={{ color: '#6366f1' }}>
          🌐 {new Date().toLocaleTimeString()} | Mesh AI Mode
        </div>
      </motion.div>
    </div>
  )
}

export default EuroMeshNetworkEngineUltra
