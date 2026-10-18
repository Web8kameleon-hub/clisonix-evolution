'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'

interface PingResult {
  timestamp: number
  latency: number | null
  status: 'success' | 'error'
  endpoint: string
}

interface PingPongProps {
  endpoints?: string[]
  interval?: number
}

export function PingPong({ 
  endpoints = ['/api/health', '/api/system/real'], 
  interval = 5000 
}: PingPongProps) {
  const [results, setResults] = useState<PingResult[]>([])
  const [isRunning, setIsRunning] = useState(false)

  const pingEndpoint = async (endpoint: string): Promise<PingResult> => {
    const startTime = performance.now()
    
    try {
      await axios.get(endpoint, { timeout: 3000 })
      const latency = performance.now() - startTime
      
      return {
        timestamp: Date.now(),
        latency: Math.round(latency),
        status: 'success',
        endpoint
      }
    } catch (error) {
      return {
        timestamp: Date.now(),
        latency: null,
        status: 'error',
        endpoint
      }
    }
  }

  const runPingPong = async () => {
    const newResults: PingResult[] = []
    
    for (const endpoint of endpoints) {
      const result = await pingEndpoint(endpoint)
      newResults.push(result)
    }
    
    setResults((prev: PingResult[]) => [...newResults, ...prev].slice(0, 20)) // Keep last 20 results
  }

  useEffect(() => {
    if (!isRunning) return

    const intervalId = setInterval(runPingPong, interval)
    
    // Run immediately
    runPingPong()

    return () => clearInterval(intervalId)
  }, [isRunning, interval])

  const avgLatency = results
    .filter((r: PingResult) => r.latency !== null)
    .reduce((sum: number, r: PingResult) => sum + (r.latency || 0), 0) / 
    results.filter((r: PingResult) => r.latency !== null).length

  const successRate = results.length > 0 ? 
    (results.filter((r: PingResult) => r.status === 'success').length / results.length) * 100 : 0

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      background: 'rgba(0,0,0,0.9)',
      color: 'white',
      padding: '16px',
      borderRadius: '8px',
      minWidth: '300px',
      fontSize: '12px',
      fontFamily: 'monospace',
      zIndex: 9999,
      border: '1px solid #333'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <strong>🏓 Ping Pong Monitor</strong>
        <button
          onClick={() => setIsRunning(!isRunning)}
          style={{
            background: isRunning ? '#ff4444' : '#44ff44',
            color: 'white',
            border: 'none',
            padding: '4px 8px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {isRunning ? 'Stop' : 'Start'}
        </button>
      </div>

      {results.length > 0 && (
        <div style={{ marginBottom: '8px' }}>
          <div>🎯 Success Rate: {successRate.toFixed(1)}%</div>
          <div>⚡ Avg Latency: {avgLatency ? `${avgLatency.toFixed(1)}ms` : 'N/A'}</div>
        </div>
      )}

      <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
        {results.slice(0, 10).map((result: PingResult, index: number) => (
          <div key={index} style={{
            display: 'flex',
            justifyContent: 'space-between',
            padding: '2px 0',
            borderBottom: '1px solid #333'
          }}>
            <span>{result.endpoint}</span>
            <span style={{ color: result.status === 'success' ? '#44ff44' : '#ff4444' }}>
              {result.status === 'success' ? `${result.latency}ms` : 'ERROR'}
            </span>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '8px', fontSize: '10px', opacity: 0.7 }}>
        Last update: {results[0] ? new Date(results[0].timestamp).toLocaleTimeString() : 'Never'}
      </div>
    </div>
  )
}

export default PingPong
