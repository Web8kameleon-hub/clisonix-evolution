/**
 * 📗 Excel Dashboard Module - LIVE DATA
 * Dashboard me te dhena reale nga serveri
 */

"use client"

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface ContainerInfo {
  name: string
  status: string
  image: string
  created: string
  ports: string
}

interface SystemMetrics {
  cpu_percent: number
  memory_percent: number
  disk_percent: number
}

interface ContainerStats {
  name: string
  cpu_percent: string
  memory_percent: string
  memory_usage: string
}

// Use local proxy routes to bypass Cloudflare
const API_BASE = ''

export default function ExcelDashboardPage() {
  const [containers, setContainers] = useState<ContainerInfo[]>([])
  const [stats, setStats] = useState<ContainerStats[]>([])
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Fetch real data from server via proxy
  useEffect(() => {
    const fetchData = async () => {
      try {
        setError(null)
        const [containersRes, statsRes, metricsRes] = await Promise.all([
          fetch(`/api/proxy/docker-containers`),
          fetch(`/api/proxy/docker-stats`),
          fetch(`/api/proxy/system-metrics`)
        ])

        if (containersRes.ok) {
          const data = await containersRes.json()
          setContainers(data.containers || [])
        }

        if (statsRes.ok) {
          const data = await statsRes.json()
          setStats(data.stats || [])
        }

        if (metricsRes.ok) {
          const data = await metricsRes.json()
          setSystemMetrics(data)
        }

        setLastUpdate(new Date())
        setLoading(false)
      } catch (err) {
        console.error('Failed to fetch data:', err)
        setError('Failed to connect to server')
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const runningContainers = containers.filter(c => c.status?.includes('running') || c.status?.includes('Up')).length
  const totalContainers = containers.length
  
  const openExcel = (filename: string) => {
    // Thirr API për të hapur Excel
    fetch(`/api/open-excel?file=${filename}`)
      .then(() => console.log(`Opening ${filename}`))
      .catch(err => console.error(err))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-900 via-slate-900 to-green-900 p-8">
      {/* Header */}
      <div className="text-center mb-8">
        <Link href="/modules" className="text-green-400 hover:text-green-300 mb-4 inline-block">
          ← Back to Modules
        </Link>
        <h1 className="text-5xl font-bold text-white mb-4 flex items-center justify-center gap-4">
          <span className="text-6xl">📗</span>
          EXCEL ∞ LIVE
        </h1>
        <p className="text-xl text-green-300">
          Production-Ready Dashboard with REAL Data
        </p>
        {lastUpdate && (
          <p className="text-sm text-gray-400 mt-2">
            Last updated: {lastUpdate.toLocaleTimeString()}
            <span className="ml-2 inline-block w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          </p>
        )}
      </div>

      {/* LIVE System Metrics */}
      <div className="max-w-6xl mx-auto mb-8">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          🖥️ LIVE System Metrics
          {loading && <span className="text-yellow-400 animate-pulse text-sm">(Loading...)</span>}
        </h2>
        
        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-300 rounded-lg p-4 mb-4">
            ❌ {error}
          </div>
        )}

        {systemMetrics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gradient-to-br from-violet-600/30 to-slate-800/30 border-2 border-violet-500 rounded-xl p-6 text-center">
              <div className="text-4xl font-bold text-violet-400">{systemMetrics.cpu_percent.toFixed(1)}%</div>
              <div className="text-gray-300 font-semibold">CPU Usage</div>
              <div className="mt-2 h-2 bg-slate-700 rounded-full overflow-hidden">
                <div className="h-full bg-violet-500 transition-all" style={{ width: `${systemMetrics.cpu_percent}%` }}></div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-green-600/30 to-green-800/30 border-2 border-green-500 rounded-xl p-6 text-center">
              <div className="text-4xl font-bold text-green-400">{systemMetrics.memory_percent.toFixed(1)}%</div>
              <div className="text-gray-300 font-semibold">RAM Usage</div>
              <div className="mt-2 h-2 bg-slate-700 rounded-full overflow-hidden">
                <div className="h-full bg-green-500 transition-all" style={{ width: `${systemMetrics.memory_percent}%` }}></div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-purple-600/30 to-purple-800/30 border-2 border-purple-500 rounded-xl p-6 text-center">
              <div className="text-4xl font-bold text-purple-400">{systemMetrics.disk_percent.toFixed(1)}%</div>
              <div className="text-gray-300 font-semibold">Disk Usage</div>
              <div className="mt-2 h-2 bg-slate-700 rounded-full overflow-hidden">
                <div className="h-full bg-purple-500 transition-all" style={{ width: `${systemMetrics.disk_percent}%` }}></div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-orange-600/30 to-orange-800/30 border-2 border-orange-500 rounded-xl p-6 text-center">
              <div className="text-4xl font-bold text-orange-400">{runningContainers}/{totalContainers}</div>
              <div className="text-gray-300 font-semibold">Containers</div>
              <div className="mt-2 text-sm text-green-400">
                {runningContainers === totalContainers ? '✅ All Running' : '⚠️ Some Stopped'}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* LIVE Docker Containers Table */}
      <div className="max-w-6xl mx-auto mb-8">
        <h2 className="text-xl font-bold text-white mb-4">🐳 LIVE Docker Containers</h2>

        <div className="bg-slate-800/80 rounded-xl border border-slate-600 overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-700">
              <tr>
                <th className="text-left px-4 py-3 text-gray-300 font-semibold">Status</th>
                <th className="text-left px-4 py-3 text-gray-300 font-semibold">Container</th>
                <th className="text-left px-4 py-3 text-gray-300 font-semibold">Image</th>
                <th className="text-left px-4 py-3 text-gray-300 font-semibold">CPU</th>
                <th className="text-left px-4 py-3 text-gray-300 font-semibold">Memory</th>
                <th className="text-left px-4 py-3 text-gray-300 font-semibold">Ports</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {containers.map((container, idx) => {
                const isRunning = container.status?.includes('running') || container.status?.includes('Up')
                const containerStat = stats.find(s => s.name === container.name)
                return (
                  <tr key={idx} className="hover:bg-slate-700/50 transition-colors">
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm ${isRunning ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'
                        }`}>
                        <span className={`w-2 h-2 rounded-full ${isRunning ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
                        {isRunning ? 'Running' : 'Stopped'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-white font-mono">{container.name}</td>
                    <td className="px-4 py-3 text-gray-400 text-sm">{container.image?.split(':')[0]}</td>
                    <td className="px-4 py-3 text-violet-400 font-mono">{containerStat?.cpu_percent || '0%'}</td>
                    <td className="px-4 py-3 text-green-400 font-mono">{containerStat?.memory_percent || '0%'}</td>
                    <td className="px-4 py-3 text-purple-400 text-sm">{container.ports || '-'}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>

          {containers.length === 0 && !loading && (
            <div className="text-center py-8 text-gray-400">
              No containers found
            </div>
          )}
        </div>
      </div>

      {/* Excel Files Section */}
      <div className="max-w-6xl mx-auto">
        <h2 className="text-xl font-bold text-white mb-4">📊 Excel Export</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <a
            href={`${API_BASE}/api/reporting/export-excel`}
            target="_blank"
            className="bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white rounded-xl p-6 text-center transition-all transform hover:scale-105 shadow-lg shadow-green-500/30"
          >
            <div className="text-3xl mb-2">📗</div>
            <div className="font-bold">Download LIVE Excel</div>
            <div className="text-green-200 text-sm mt-1">Real API Data Export</div>
          </a>

          <a
            href={`${API_BASE}/api/reporting/export-pptx`}
            target="_blank"
            className="bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 text-white rounded-xl p-6 text-center transition-all transform hover:scale-105 shadow-lg shadow-orange-500/30"
          >
            <div className="text-3xl mb-2">📙</div>
            <div className="font-bold">Download PPTX</div>
            <div className="text-orange-200 text-sm mt-1">Presentation Export</div>
          </a>

          <Link 
            href="/modules/protocol-kitchen"
            className="bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-500 hover:to-purple-400 text-white rounded-xl p-6 text-center transition-all transform hover:scale-105 shadow-lg shadow-purple-500/30"
          >
            <div className="text-3xl mb-2">🔬</div>
            <div className="font-bold">Protocol Kitchen</div>
            <div className="text-purple-200 text-sm mt-1">Pipeline Dashboard</div>
          </Link>
        </div>

        {/* Quick Links */}
        <div className="flex flex-wrap gap-4 justify-center">
          <a 
            href={`${API_BASE}/api/reporting/dashboard`}
            target="_blank"
            className="px-6 py-3 bg-violet-600 hover:bg-violet-500 text-white rounded-lg font-semibold transition-all"
          >
            📊 API Dashboard
          </a>
          
          <Link
            href="/modules/reporting-dashboard"
            className="px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-semibold transition-all"
          >
            📈 Analytics Center
          </Link>
          
          <Link 
            href="/modules"
            className="px-6 py-3 bg-slate-600 hover:bg-slate-500 text-white rounded-lg font-semibold transition-all"
          >
            🏠 All Modules
          </Link>
        </div>
      </div>
    </div>
  )
}







