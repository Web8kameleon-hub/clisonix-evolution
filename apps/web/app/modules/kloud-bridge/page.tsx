"use client"

import { useState, useEffect, useCallback, useRef } from 'react'
import Link from 'next/link'

interface KloudBridgeData {
  status: {
bridge: string
    sovereign: string
    ocean: string
    ready: string
  }
  metrics: {
    activity_updates: number | null
    containers_running: number
    containers_total: number
    data_sources_active: number | null
    worker_containers: number | null
    non_running_containers: number | null
    system_cpu: number | null
    system_memory: number | null
  }
  human_readable: {
    status: string
    sync: string
    updates: string
    uptime: string
  }
  timestamp: string
}

function formatCount(value: number | null | undefined) {
  return typeof value === 'number' && Number.isFinite(value)
    ? new Intl.NumberFormat('en').format(value)
    : 'Unavailable'
}

function StatusBadge({ status }: { status: string }) {
  const colors = {
    'connected-monitored': { bg: 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400', pulse: true },
    ready: { bg: 'bg-emerald-500', text: 'text-emerald-50', pulse: false },
    synchronized: { bg: 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400', pulse: true },
    initializing: { bg: 'bg-amber-500/20 border-amber-500/50 text-amber-400', pulse: true },
    'almost': { bg: 'bg-amber-500', text: 'text-amber-50', pulse: false },
    checking: { bg: 'bg-slate-500/20 border-slate-500/50 text-slate-400', pulse: true },
    error: { bg: 'bg-red-500/20 border-red-500/50 text-red-400', pulse: true }
  }

const config = colors[status as keyof typeof colors] || colors.checking!
  const dotClass = config.bg?.includes('emerald') ? 'bg-emerald-500 animate-pulse' :
                   config.bg?.includes('cyan') ? 'bg-cyan-500 animate-pulse' :
                   'bg-amber-500 animate-pulse'
  return (
    <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border font-medium text-sm transition-all ${config.bg}`}>
      <div className={`w-3 h-3 rounded-full ${dotClass}`} />
      {status.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
    </div>
  )
}

function ProgressBar({ percent, label }: { percent: number | null, label: string }) {
  const safePercent = typeof percent === 'number' && Number.isFinite(percent)
    ? Math.max(0, Math.min(percent, 100))
    : null
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-slate-400">
        <span>{label}</span>
        <span>{safePercent === null ? 'Unavailable' : `${safePercent}%`}</span>
      </div>
      <div className="w-full bg-slate-800 rounded-full h-2">
        <div
          className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-2 rounded-full transition-all duration-1000"
          style={{ width: `${safePercent ?? 0}%` }}
        />
      </div>
    </div>
  )
}

export default function KloudBridge() {
  const [data, setData] = useState<KloudBridgeData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const pollingHandleRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const isFetchInFlightRef = useRef(false)
  const hasLoadedOnceRef = useRef(false)

  const fetchData = useCallback(async (showLoader = false) => {
    if (isFetchInFlightRef.current) {
      return false
    }

    isFetchInFlightRef.current = true
    if (showLoader) {
      setLoading(true)
    }
    try {
      const response = await fetch('/api/proxy/kloud-bridge', { cache: 'no-store' })
      if (!response.ok) throw new Error('Kloud Bridge unavailable')
      const result = await response.json()
      setData(result)
      setError(null)
      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed')
      return false
    } finally {
      if (showLoader || !hasLoadedOnceRef.current) {
        setLoading(false)
      }
      hasLoadedOnceRef.current = true
      isFetchInFlightRef.current = false
    }
  }, [])

  useEffect(() => {
    let disposed = false

    const clearPollingHandle = () => {
      if (pollingHandleRef.current) {
        clearTimeout(pollingHandleRef.current)
        pollingHandleRef.current = null
      }
    }

    const schedulePoll = (delayMs: number) => {
      clearPollingHandle()
      if (disposed) {
        return
      }
      pollingHandleRef.current = setTimeout(runPoll, delayMs)
    }

    const runPoll = async () => {
      if (disposed) {
        return
      }
      if (typeof document !== 'undefined' && document.hidden) {
        schedulePoll(30000)
        return
      }

      const ok = await fetchData(!hasLoadedOnceRef.current)
      schedulePoll(ok ? 15000 : 60000)
    }

    const onVisibilityChange = () => {
      if (typeof document !== 'undefined' && !document.hidden) {
        void runPoll()
      }
    }

    void runPoll()
    document.addEventListener('visibilitychange', onVisibilityChange)

    return () => {
      disposed = true
      clearPollingHandle()
      document.removeEventListener('visibilitychange', onVisibilityChange)
    }
  }, [fetchData])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-cyan-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-400/30 border-t-cyan-500 rounded-full animate-spin mx-auto mb-6" />
          <p className="text-slate-400 text-lg">Establishing Kloud Bridge...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-cyan-950">
      {/* Header */}
      <header className="border-b border-slate-800/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-6 py-8">
          <Link href="/modules" className="inline-flex items-center gap-2 text-slate-500 hover:text-white text-sm mb-6 transition-colors">
            ← Back to Modules
          </Link>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-cyan-300 bg-clip-text text-transparent mb-2">
            Kloud Bridge
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl leading-relaxed">
            Real user services • Live connectivity • Status based on fresh telemetry
          </p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 pb-12">
        {error ? (
          <div className="mb-12 p-8 rounded-2xl border border-red-500/30 bg-red-500/5 text-red-300 text-center">
            {error}. <button onClick={() => void fetchData(true)} className="underline hover:no-underline">Retry</button>
          </div>
        ) : null}

        {/* Main Status Cards */}
        <div className="grid lg:grid-cols-2 gap-8 mb-12">
          {/* Service Health */}
          <div className="bg-slate-900/30 backdrop-blur-sm border border-slate-800/50 rounded-3xl p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-emerald-500/20 rounded-2xl flex items-center justify-center">
                <span className="text-emerald-400 text-2xl">✓</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Service Health</h2>
                <p className="text-slate-500">{data?.human_readable.status || 'Live runtime snapshot'}</p>
              </div>
            </div>
            <StatusBadge status={data?.status.bridge || 'checking'} />
            <div className="grid md:grid-cols-2 gap-6 mt-8">
              <div>
                <ProgressBar percent={data?.metrics.system_cpu ?? null} label="CPU" />
                <ProgressBar percent={data?.metrics.system_memory ?? null} label="Memory" />
              </div>
              <div>
                <div className="text-sm text-slate-400 mb-4">Active Containers</div>
                <div className="text-3xl font-bold text-emerald-400">
                  {data?.metrics.containers_running}/{data?.metrics.containers_total}
                </div>
                <div className="mt-3 space-y-1 text-sm text-slate-400">
                  <div>Workers/Labor: {formatCount(data?.metrics.worker_containers)}</div>
                  <div>Non-running: {formatCount(data?.metrics.non_running_containers)}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Connectivity Flow */}
          <div className="bg-slate-900/30 backdrop-blur-sm border border-slate-800/50 rounded-3xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl flex items-center justify-center">
                <span className="text-white font-bold">🌉</span>
              </div>
              Connectivity Flow
            </h2>
            <div className="space-y-4">
              <div className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-2xl">
                <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse" />
                <StatusBadge status={data?.status.bridge || 'checking'} />
              </div>
              <div className="flex items-center justify-center">
                <div className="w-20 h-1 bg-gradient-to-r from-emerald-500 via-cyan-500 to-emerald-500 rounded-full animate-pulse" />
              </div>
              <div className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-2xl">
                <div className="w-3 h-3 bg-cyan-500 rounded-full animate-pulse" />
                <StatusBadge status={data?.status.sovereign || 'initializing'} />
              </div>
              <div className="flex items-center justify-center">
                <div className="w-20 h-1 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full animate-pulse" />
              </div>
              <div className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-2xl">
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" />
                <StatusBadge status={data?.status.ocean || 'building'} />
              </div>
              <div className="flex items-center justify-center">
                <div className="w-20 h-1 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full animate-pulse" />
              </div>
              <div className="flex items-center gap-4 p-4 bg-emerald-500/20 border border-emerald-500/50 rounded-2xl">
                <div className="w-3 h-3 bg-emerald-500 rounded-full" />
                <StatusBadge status={data?.status.ready || 'almost'} />
              </div>
            </div>
          </div>
        </div>

        {/* Activity Timeline */}
        <div className="bg-slate-900/30 backdrop-blur-sm border border-slate-800/50 rounded-3xl p-8">
          <h2 className="text-2xl font-bold text-white mb-8">Live Activity</h2>
          <div className="space-y-6">
            <div className="flex items-start gap-4 p-6 bg-slate-800/50 rounded-2xl group hover:bg-slate-700/50 transition-all">
              <div className="w-2 h-2 bg-cyan-500 rounded-full mt-2 flex-shrink-0 animate-pulse" />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-3 py-1 bg-cyan-500/20 text-cyan-400 text-xs font-medium rounded-full">Live</span>
                  <span className="text-slate-500 text-sm">{data?.human_readable.sync}</span>
                </div>
                <div className="text-3xl font-bold text-white mb-1">{data?.human_readable.updates || 'No live activity yet'}</div>
                <p className="text-slate-400">Activity updates streamed</p>
              </div>
            </div>
            <div className="grid md:grid-cols-2 gap-6 pt-6 border-t border-slate-700">
              <div>
                <h3 className="font-semibold text-white mb-3">Data Sources</h3>
                <div className="text-2xl font-bold text-cyan-400">{formatCount(data?.metrics.data_sources_active)}</div>
                <p className="text-slate-500 text-sm mt-1">Active streams</p>
              </div>
              <div>
                <h3 className="font-semibold text-white mb-3">Last Update</h3>
                <div className="text-cyan-400 font-mono text-sm">
                  {new Date(data?.timestamp || '').toLocaleTimeString()}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Ready Status */}
        {data?.status.ready === 'ready' && (
          <div className="mt-12 text-center p-12 bg-emerald-500/10 border-2 border-emerald-500/30 rounded-3xl">
            <div className="w-20 h-20 bg-emerald-500 rounded-3xl flex items-center justify-center mx-auto mb-6 text-4xl shadow-2xl">
              ✅
            </div>
            <h2 className="text-3xl font-bold text-emerald-400 mb-4">Kloud Bridge Ready</h2>
            <p className="text-xl text-slate-300 max-w-md mx-auto">
              Everything synchronized and live. Your services are fully connected.
            </p>
          </div>
        )}
      </main>
    </div>
  )
}

