'use client'
/**
 * Self-Learning Dashboard — Ocean Engine
 * Real-time view of automatic knowledge acquisition status
 */

import { useState, useEffect, useCallback } from 'react'

interface LearningStats {
  totalLearned?: number
  sessionEntries?: number
  knowledgeSize?: string
  lastUpdated?: string
}

interface SelfLearningStatus {
  isActive: boolean
  engine: string
  mode: string
  statistics: LearningStats
  features: string[]
  endpoints: Record<string, string>
}

interface StatusResponse {
  success: boolean
  selfLearning: SelfLearningStatus
  timestamp: string
}

export default function SelfLearningPage() {
  const [data, setData] = useState<StatusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [toggling, setToggling] = useState(false)

  const fetch_status = useCallback(async () => {
    try {
      const res = await fetch('/api/ocean/self-learning-status')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = await res.json()
      setData(json)
      setError(null)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Fetch failed')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetch_status()
    const interval = setInterval(fetch_status, 10000)
    return () => clearInterval(interval)
  }, [fetch_status])

  const toggle = async () => {
    if (!data) return
    setToggling(true)
    try {
      const action = data.selfLearning.isActive ? 'stop' : 'start'
      const res = await fetch('/api/ocean/self-learning-status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      await fetch_status()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Toggle failed')
    } finally {
      setToggling(false)
    }
  }

  const sl = data?.selfLearning

  return (
    <div className="min-h-screen bg-black text-white p-6 font-mono">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-cyan-400">🧠 Self-Learning Engine</h1>
          <p className="text-gray-400 text-sm mt-1">Ocean Core — autonomous knowledge acquisition</p>
          <a href="/ocean" className="text-xs text-gray-600 hover:text-gray-400 underline">← Ocean Dashboard</a>
        </div>

        {loading && (
          <div className="text-gray-500 text-sm animate-pulse">Loading self-learning status...</div>
        )}

        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded p-3 text-red-400 text-sm mb-4">
            ⚠ {error}
          </div>
        )}

        {sl && (
          <div className="space-y-4">
            {/* Status Card */}
            <div className={`rounded-lg border p-5 ${sl.isActive ? 'border-cyan-700 bg-cyan-950/30' : 'border-gray-700 bg-gray-900/30'}`}>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${sl.isActive ? 'bg-cyan-400 animate-pulse' : 'bg-gray-600'}`} />
                    <span className="font-bold text-lg">{sl.isActive ? 'ACTIVE' : 'INACTIVE'}</span>
                  </div>
                  <div className="text-xs text-gray-400 mt-1">Engine: {sl.engine} · Mode: {sl.mode}</div>
                </div>
                <button
                  onClick={toggle}
                  disabled={toggling}
                  className={`px-4 py-2 rounded text-sm font-bold transition-colors ${
                    sl.isActive
                      ? 'bg-red-900 hover:bg-red-800 text-red-200 border border-red-700'
                      : 'bg-cyan-900 hover:bg-cyan-800 text-cyan-200 border border-cyan-700'
                  } disabled:opacity-50`}
                >
                  {toggling ? '...' : sl.isActive ? 'Stop Learning' : 'Start Learning'}
                </button>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { label: 'Total Learned', val: sl.statistics.totalLearned ?? '—' },
                  { label: 'Session Entries', val: sl.statistics.sessionEntries ?? '—' },
                  { label: 'Knowledge Size', val: sl.statistics.knowledgeSize ?? '—' },
                  { label: 'Last Updated', val: sl.statistics.lastUpdated ? new Date(sl.statistics.lastUpdated).toLocaleTimeString() : '—' },
                ].map(({ label, val }) => (
                  <div key={label} className="bg-black/40 rounded p-3">
                    <div className="text-xs text-gray-500 mb-1">{label}</div>
                    <div className="text-cyan-300 font-mono text-sm">{String(val)}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Features */}
            {sl.features.length > 0 && (
              <div className="rounded-lg border border-gray-800 bg-gray-900/20 p-4">
                <h2 className="text-xs text-gray-500 mb-3 uppercase tracking-widest">Active Features</h2>
                <ul className="space-y-1">
                  {sl.features.map((f, i) => (
                    <li key={i} className="text-sm text-gray-200">{f}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Endpoints */}
            {Object.keys(sl.endpoints).length > 0 && (
              <div className="rounded-lg border border-gray-800 bg-gray-900/20 p-4">
                <h2 className="text-xs text-gray-500 mb-3 uppercase tracking-widest">API Endpoints</h2>
                <ul className="space-y-1">
                  {Object.entries(sl.endpoints).map(([name, path]) => (
                    <li key={name} className="text-xs">
                      <span className="text-gray-500">{name}:</span>{' '}
                      <span className="text-cyan-600">{path}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="text-xs text-gray-700 pt-2">
              Last fetched: {data?.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '—'} · Auto-refresh every 10s
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
