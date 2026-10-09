/**
 * Clisonix Data Sources Dashboard
 * Enterprise-grade data source management with real-time metrics
 * Connects to: /api/proxy/user-data-sources, /api/proxy/system-metrics
 */

"use client"

import { useState, useEffect, useCallback, useMemo } from 'react'
import Link from 'next/link'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

// ─────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────
interface DataSource {
  id: string
  name: string
  type: 'iot' | 'api' | 'lora' | 'gsm' | 'mqtt' | 'webhook' | 'database'
  status: 'connected' | 'disconnected' | 'error' | 'syncing'
  endpoint?: string
  lastSync: string
  dataPoints: number
  throughput: string
  latency: number
  createdAt: string
}

interface DashboardMetrics {
  totalSources: number | null
  connectedSources: number | null
  totalDataPoints: number | null
  dataPointsToday: number | null
  storageUsed: string | null
  apiCallsToday: number | null
  avgLatency: number | null
  uptime: string | null
}

interface CorrelationPoint {
  label: string
  sourceA: number
  sourceB: number
  aligned: boolean
}

interface CorrelationInsight {
  sourceAName: string
  sourceBName: string
  correlation: number
  resonanceScore: number
  strengthPercent: number
  status: 'HARMONIC' | 'STABLE' | 'SYNC' | 'DIVERGENT'
  bestOffset: number
  alignedPoints: number
  points: CorrelationPoint[]
}

// ─────────────────────────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────────────────────────
const SOURCE_TYPES = {
  iot:      { icon: '📡', label: 'IoT Sensor',    color: 'from-emerald-500 to-teal-600' },
  api:      { icon: '🔗', label: 'REST API',      color: 'from-blue-500 to-indigo-600' },
  lora:     { icon: '📶', label: 'LoRaWAN',       color: 'from-purple-500 to-violet-600' },
  gsm:      { icon: '📱', label: 'Cellular/4G',   color: 'from-orange-500 to-red-500' },
  mqtt:     { icon: '🌐', label: 'MQTT Broker',   color: 'from-cyan-500 to-blue-500' },
  webhook:  { icon: '🔔', label: 'Webhook',       color: 'from-pink-500 to-rose-500' },
  database: { icon: '🗄️', label: 'Database',      color: 'from-slate-500 to-gray-600' }
} as const

const STATUS_CONFIG = {
  connected:    { label: 'Connected',    dot: 'bg-emerald-500', text: 'text-emerald-400', pulse: true },
  disconnected: { label: 'Disconnected', dot: 'bg-gray-500',    text: 'text-gray-400',    pulse: false },
  error:        { label: 'Error',        dot: 'bg-red-500',     text: 'text-red-400',     pulse: true },
  syncing:      { label: 'Syncing',      dot: 'bg-amber-500',   text: 'text-amber-400',   pulse: true }
} as const

type FilterType = 'all' | DataSource['type'] | DataSource['status']

// ─────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────
export default function DataSourcesDashboard() {
  const [sources, setSources] = useState<DataSource[]>([])
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<FilterType>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [refreshing, setRefreshing] = useState(false)
  const [dashboardError, setDashboardError] = useState<string | null>(null)

  // Add Source Modal State
  const [showAddModal, setShowAddModal] = useState(false)
  const [addingSource, setAddingSource] = useState(false)
  const [testingConnection, setTestingConnection] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string; data?: string } | null>(null)
  const [correlationSourceA, setCorrelationSourceA] = useState('')
  const [correlationSourceB, setCorrelationSourceB] = useState('')

  // Configure/View Data Modals
  const [selectedSourceForConfig, setSelectedSourceForConfig] = useState<DataSource | null>(null)
  const [selectedSourceForView, setSelectedSourceForView] = useState<DataSource | null>(null)
  const [newSource, setNewSource] = useState({
    name: '',
    type: 'api' as DataSource['type'],
    endpoint: '',
    description: '',
    apiKey: ''
  })

  // Fetch data from API
  const fetchData = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true)

    try {
      const [sourcesRes, metricsRes] = await Promise.all([
        fetch('/api/proxy/user-data-sources', { cache: 'no-store' }),
        fetch('/api/proxy/system-metrics', { cache: 'no-store' })
      ])

      if (sourcesRes.ok) {
        const data = await sourcesRes.json()
        if (data.sources && Array.isArray(data.sources)) {
          setSources(data.sources)
        } else {
          setSources([])
        }
      } else {
        const errData = await sourcesRes.json().catch(() => null)
        setDashboardError(errData?.error || `Data sources unavailable (${sourcesRes.status})`)
        setSources([])
      }

      if (metricsRes.ok) {
        const data = await metricsRes.json()
        setMetrics({
          totalSources: typeof data.total_sources === 'number' ? data.total_sources : null,
          connectedSources: typeof data.connected_sources === 'number' ? data.connected_sources : null,
          totalDataPoints: typeof data.total_requests === 'number' ? data.total_requests : null,
          dataPointsToday: typeof data.requests_today === 'number' ? data.requests_today : null,
          storageUsed: data.disk_used ?? null,
          apiCallsToday: typeof data.api_calls === 'number' ? data.api_calls : null,
          avgLatency: typeof data.avg_latency === 'number' ? data.avg_latency : null,
          uptime: data.uptime ?? null,
        })
      } else {
        const errData = await metricsRes.json().catch(() => null)
        setDashboardError(errData?.error || `Metrics unavailable (${metricsRes.status})`)
        setMetrics(null)
      }
    } catch (err) {
      console.error('Failed to fetch data:', err)
      setDashboardError(err instanceof Error ? err.message : 'Failed to load dashboard data')
      setSources([])
      setMetrics(null)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    const interval = setInterval(() => fetchData(), 30000)
    return () => clearInterval(interval)
  }, [fetchData])

  // Add new data source
  const handleAddSource = async () => {
    if (!newSource.name.trim() || !newSource.endpoint.trim()) {
      alert('Please fill in all required fields')
      return
    }

    setAddingSource(true)
    try {
      const res = await fetch('/api/proxy/user-data-sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newSource.name,
          type: newSource.type,
          endpoint: newSource.endpoint,
          api_key: newSource.apiKey || undefined
        })
      })

      if (res.ok) {
        const data = await res.json()
        // Create with returned data
        const created: DataSource = {
          id: data.id || `src_${Date.now()}`,
          name: newSource.name,
          type: newSource.type,
          status: 'syncing',
          endpoint: newSource.endpoint,
          lastSync: 'Just now',
          dataPoints: 0,
          throughput: '0/s',
          latency: 0,
          createdAt: new Date().toISOString()
        }
        setSources(prev => [created, ...prev])
        setShowAddModal(false)
        resetNewSource()

        // Refresh to get actual data
        setTimeout(() => fetchData(), 2000)
      } else {
        const errData = await res.json().catch(() => null)
        alert(`Failed to add source: ${errData?.error || res.status}`)
      }
    } catch (err) {
      console.error('Failed to add source:', err)
      alert(`Failed to add source: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setAddingSource(false)
    }
  }

  // Test connection before adding
  const handleTestConnection = async () => {
    if (!newSource.endpoint.trim()) {
      setTestResult({ success: false, message: 'Please enter an endpoint URL first' })
      return
    }

    setTestingConnection(true)
    setTestResult(null)

    try {
      // First create a temp source to test
      const tempRes = await fetch('/api/proxy/user-data-sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newSource.name || 'Test Connection',
          type: newSource.type,
          endpoint: newSource.endpoint,
          api_key: newSource.apiKey || undefined
        })
      })

      if (tempRes.ok) {
        const tempData = await tempRes.json()
        const sourceId = tempData.id

        // Now test the connection
        const testRes = await fetch(`/api/proxy/user-data-sources/${sourceId}/test`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })

        if (testRes.ok) {
          const testData = await testRes.json()
          if (testData.success) {
            setTestResult({
              success: true,
              message: `✓ Connected! Latency: ${testData.latency_ms || testData.latency || '?'}ms`,
              data: testData.data_preview || testData.webhook_url || JSON.stringify(testData).slice(0, 200)
            })
          } else {
            setTestResult({
              success: false,
              message: testData.error || 'Connection failed'
            })
          }
        } else {
          setTestResult({ success: false, message: 'Test endpoint unavailable' })
        }
      } else {
        const errData = await tempRes.json().catch(() => null)
        setTestResult({ success: false, message: errData?.error || `Failed to create test source (${tempRes.status})` })
      }
    } catch (err) {
      setTestResult({
        success: false,
        message: `Error: ${err instanceof Error ? err.message : 'Unknown error'}`
      })
    } finally {
      setTestingConnection(false)
    }
  }

  const resetNewSource = () => {
    setNewSource({ name: '', type: 'api', endpoint: '', description: '', apiKey: '' })
    setTestResult(null)
  }

  // Handle Configure button click
  const handleConfigureSource = (source: DataSource) => {
    setSelectedSourceForConfig(source)
  }

  // Handle View Data button click
  const handleViewSourceData = (source: DataSource) => {
    setSelectedSourceForView(source)
  }

  // Export all sources to Excel
  const handleExportAllExcel = async () => {
    try {
      const res = await fetch('/api/proxy/mymirror/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'excel' })
      })
      if (res.ok) {
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `data_sources_${new Date().toISOString().split('T')[0]}.xlsx`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
      }
    } catch (err) {
      console.error('Excel export failed:', err)
    }
  }

  // Export all sources to PDF
  const handleExportAllPDF = async () => {
    try {
      const res = await fetch('/api/proxy/mymirror/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'pdf' })
      })
      if (res.ok) {
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `data_sources_${new Date().toISOString().split('T')[0]}.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
      }
    } catch (err) {
      console.error('PDF export failed:', err)
    }
  }

  // Filter logic
  const filteredSources = sources.filter(source => {
    const matchesFilter = filter === 'all' || source.type === filter || source.status === filter
    const matchesSearch = source.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          source.endpoint?.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesFilter && matchesSearch
  })

  const connectedCount = sources.filter(s => s.status === 'connected').length
  const correlationCandidates = useMemo(
    () => sources.filter(source => source.status === 'connected' || source.status === 'syncing'),
    [sources]
  )

  useEffect(() => {
    if (correlationCandidates.length === 0) {
      return
    }

    if (!correlationSourceA || !correlationCandidates.some(source => source.id === correlationSourceA)) {
      setCorrelationSourceA(correlationCandidates[0]?.id ?? '')
    }

    if (
      !correlationSourceB ||
      correlationSourceB === correlationSourceA ||
      !correlationCandidates.some(source => source.id === correlationSourceB)
    ) {
      setCorrelationSourceB(correlationCandidates[1]?.id ?? correlationCandidates[0]?.id ?? '')
    }
  }, [correlationCandidates, correlationSourceA, correlationSourceB])

  const correlationSourceAData = correlationCandidates.find(source => source.id === correlationSourceA)
  const correlationSourceBData = correlationCandidates.find(source => source.id === correlationSourceB)

  const correlationInsight = useMemo(() => {
    if (!correlationSourceAData || !correlationSourceBData || correlationSourceAData.id === correlationSourceBData.id) {
      return null
    }

    return buildCorrelationInsight(correlationSourceAData, correlationSourceBData)
  }, [correlationSourceAData, correlationSourceBData])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading data sources...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <Link href="/modules" className="text-slate-500 hover:text-white text-sm mb-1 inline-flex items-center gap-1 transition-colors">
                <span>←</span> Back to Modules
              </Link>
              <h1 className="text-2xl font-bold text-white">Data Sources</h1>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => fetchData(true)}
                disabled={refreshing}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm font-medium transition-all flex items-center gap-2 disabled:opacity-50"
              >
                <span className={refreshing ? 'animate-spin' : ''}>↻</span>
                {refreshing ? 'Refreshing...' : 'Refresh'}
              </button>
              <button className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 rounded-lg text-sm font-semibold transition-all flex items-center gap-2" onClick={() => setShowAddModal(true)}>
                <span>+</span> Add Source
              </button>
              <button
                onClick={handleExportAllExcel}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-semibold transition-all flex items-center gap-2"
                title="Export all data sources to Excel"
              >
                📗 Export Excel
              </button>
              <button
                onClick={handleExportAllPDF}
                className="px-4 py-2 bg-red-600 hover:bg-red-500 rounded-lg text-sm font-semibold transition-all flex items-center gap-2"
                title="Export all data sources to PDF"
              >
                📄 Export PDF
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {dashboardError && (
          <div className="mb-6 rounded-xl border border-red-500/40 bg-red-900/20 px-5 py-4 text-sm text-red-300">
            <strong>Dashboard error:</strong> {dashboardError}
          </div>
        )}
        {/* Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 mb-8">
          <MetricCard label="Total Sources" value={typeof metrics?.totalSources === 'number' ? metrics.totalSources : sources.length || 'Unavailable'} icon="📊" />
          <MetricCard label="Connected" value={connectedCount} icon="✓" accent="emerald" />
          <MetricCard label="Data Points" value={typeof metrics?.totalDataPoints === 'number' ? formatNumber(metrics.totalDataPoints) : 'Unavailable'} icon="📈" />
          <MetricCard label="Today" value={typeof metrics?.dataPointsToday === 'number' ? formatNumber(metrics.dataPointsToday) : 'Unavailable'} icon="📅" accent="cyan" />
          <MetricCard label="Storage" value={metrics?.storageUsed ?? 'Unavailable'} icon="💾" />
          <MetricCard label="API Calls" value={typeof metrics?.apiCallsToday === 'number' ? formatNumber(metrics.apiCallsToday) : 'Unavailable'} icon="🔗" />
          <MetricCard label="Avg Latency" value={typeof metrics?.avgLatency === 'number' ? `${metrics.avgLatency}ms` : 'Unavailable'} icon="⚡" accent="amber" />
          <MetricCard label="Uptime" value={metrics?.uptime ?? 'Unavailable'} icon="🟢" accent="emerald" />
        </div>

        {/* Operational Correlation Preview */}
        <section className="mb-8 rounded-2xl border border-cyan-500/20 bg-gradient-to-br from-slate-900 via-slate-900 to-cyan-950/20 p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between mb-6">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-300 mb-3">
                <span>Φ</span>
                Operational Correlation Preview
              </div>
              <h2 className="text-2xl font-semibold text-white">Grounded resonance view for live sources</h2>
              <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-400">
                Uses normalized operational telemetry derived from the selected sources&apos; current throughput, latency,
                status, and data volume. Pearson correlation is real; the Φ score is a Clisonix branding layer and not
                a claim of statistical significance or forecasting by itself.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:min-w-[420px]">
              <label className="block">
                <span className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">Source A</span>
                <select
                  value={correlationSourceA}
                  onChange={(e) => setCorrelationSourceA(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white focus:border-cyan-500 focus:outline-none"
                >
                  {correlationCandidates.map(source => (
                    <option key={source.id} value={source.id}>{source.name}</option>
                  ))}
                </select>
              </label>

              <label className="block">
                <span className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">Source B</span>
                <select
                  value={correlationSourceB}
                  onChange={(e) => setCorrelationSourceB(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white focus:border-cyan-500 focus:outline-none"
                >
                  {correlationCandidates.map(source => (
                    <option key={source.id} value={source.id}>{source.name}</option>
                  ))}
                </select>
              </label>
            </div>
          </div>

          {!correlationInsight ? (
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-6 text-sm text-slate-400">
              Connect at least two live sources to unlock the correlation preview.
            </div>
          ) : (
            <>
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5 mb-6">
                <InsightCard label="Correlation (r)" value={correlationInsight.correlation.toFixed(4)} accent="cyan" />
                <InsightCard label="Φ Resonance" value={correlationInsight.resonanceScore.toFixed(4)} accent="amber" />
                <InsightCard label="Strength" value={`${correlationInsight.strengthPercent.toFixed(1)}%`} accent="emerald" />
                <InsightCard label="Status" value={correlationInsight.status} accent={getInsightAccent(correlationInsight.status)} />
                <InsightCard label="Best Offset" value={`${correlationInsight.bestOffset > 0 ? '+' : ''}${correlationInsight.bestOffset}`} accent="slate" />
              </div>

              <div className="grid gap-6 xl:grid-cols-[2fr,1fr]">
                <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                  <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-white">Wave alignment</h3>
                      <p className="text-xs text-slate-500">
                        14-step normalized operational trace preview for {correlationInsight.sourceAName} and {correlationInsight.sourceBName}.
                      </p>
                    </div>
                    <div className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-300">
                      Aligned intervals: {correlationInsight.alignedPoints}/{correlationInsight.points.length}
                    </div>
                  </div>

                  <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={correlationInsight.points}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis dataKey="label" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                        <YAxis domain={[0, 1]} stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#020617',
                            border: '1px solid #1e293b',
                            borderRadius: '12px',
                            color: '#e2e8f0'
                          }}
                          formatter={(value: number, name: string) => [value.toFixed(3), name === 'sourceA' ? correlationInsight.sourceAName : correlationInsight.sourceBName]}
                        />
                        <Line type="monotone" dataKey="sourceA" stroke="#a855f7" strokeWidth={3} dot={false} name="sourceA" />
                        <Line type="monotone" dataKey="sourceB" stroke="#22d3ee" strokeWidth={3} dot={false} name="sourceB" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="space-y-4 rounded-2xl border border-slate-800 bg-slate-950/60 p-5">
                  <div>
                    <h3 className="text-lg font-semibold text-white">Interpretation</h3>
                    <p className="mt-2 text-sm leading-relaxed text-slate-400">
                      This panel is intentionally conservative. It shows operational similarity, not causal proof and not an automatic enterprise alert trigger.
                    </p>
                  </div>

                  <div className="space-y-3 text-sm">
                    <InsightRow label="Pair" value={`${correlationInsight.sourceAName} ↔ ${correlationInsight.sourceBName}`} />
                    <InsightRow label="Method" value="Pearson on normalized operational preview traces" />
                    <InsightRow label="Use" value="Prioritize which source pairs deserve real historical adapter work" />
                    <InsightRow label="Guardrail" value="Backtesting and significance checks required before predictive claims" />
                  </div>

                  <div className="rounded-xl border border-amber-500/20 bg-amber-500/10 p-4 text-xs leading-relaxed text-amber-200">
                    Φ branding metric: resonance = correlation × 1.618. Useful for product language, not a substitute for confidence intervals, lag validation, or out-of-sample testing.
                  </div>
                </div>
              </div>
            </>
          )}
        </section>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <input
              type="text"
              placeholder="Search sources by name or endpoint..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 transition-all"
            />
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">🔍</span>
          </div>

          <div className="flex gap-2 flex-wrap">
            {(['all', 'connected', 'iot', 'api', 'mqtt', 'webhook'] as FilterType[]).map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  filter === f
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                    : 'bg-slate-800/50 text-slate-400 border border-slate-700 hover:border-slate-600 hover:text-white'
                }`}
              >
                {f === 'all' ? 'All' : f === 'connected' ? '● Connected' : f.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Sources Grid */}
        {filteredSources.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-xl font-semibold text-slate-300 mb-2">No data sources found</h3>
            <p className="text-slate-500 mb-6">
              {searchQuery ? 'Try adjusting your search query' : 'Add your first data source to get started'}
            </p>
            <button className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg font-semibold">
              + Add Data Source
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {filteredSources.map(source => (
              <SourceCard
                key={source.id}
                source={source}
                onConfigure={handleConfigureSource}
                onViewData={handleViewSourceData}
              />
            ))}
          </div>
        )}

        {/* Quick Connect */}
        <section className="mt-12">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <span className="text-2xl">⚡</span> Quick Connect
          </h2>
          <div className="grid md:grid-cols-4 gap-4">
            {Object.entries(SOURCE_TYPES).slice(0, 4).map(([type, config]) => (
              <button
                key={type}
                className={`bg-gradient-to-br ${config.color} p-[1px] rounded-xl group`}
              >
                <div className="bg-slate-900 rounded-xl p-5 h-full hover:bg-slate-800/50 transition-all">
                  <div className="text-3xl mb-3">{config.icon}</div>
                  <div className="font-semibold text-white group-hover:text-cyan-400 transition-colors">
                    Connect {config.label}
                  </div>
                  <div className="text-slate-500 text-sm mt-1">
                    Configure new {type.toUpperCase()} source
                  </div>
                </div>
              </button>
            ))}
          </div>
        </section>

        {/* Documentation */}
        <section className="mt-12 bg-gradient-to-r from-slate-800/50 to-slate-900/50 rounded-2xl p-8 border border-slate-700">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <span>📚</span> Integration Documentation
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <div className="w-10 h-10 bg-cyan-500/20 rounded-lg flex items-center justify-center mb-3">
                <span className="text-cyan-400 font-bold">1</span>
              </div>
              <h3 className="font-semibold text-white mb-2">Choose Protocol</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Select MQTT, HTTP REST, WebSocket, LoRaWAN, or direct cellular connection based on your device capabilities.
              </p>
            </div>
            <div>
              <div className="w-10 h-10 bg-cyan-500/20 rounded-lg flex items-center justify-center mb-3">
                <span className="text-cyan-400 font-bold">2</span>
              </div>
              <h3 className="font-semibold text-white mb-2">Configure Endpoint</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Generate unique API keys and configure your device with the provided endpoints and authentication tokens.
              </p>
            </div>
            <div>
              <div className="w-10 h-10 bg-cyan-500/20 rounded-lg flex items-center justify-center mb-3">
                <span className="text-cyan-400 font-bold">3</span>
              </div>
              <h3 className="font-semibold text-white mb-2">Stream Data</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Data flows automatically with &lt;50ms latency. Monitor throughput and health in real-time from this dashboard.
              </p>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-slate-700 flex gap-4">
            <Link href="/developers" className="text-cyan-400 hover:text-cyan-300 text-sm font-medium">
              View API Documentation →
            </Link>
            <a href="https://github.com/Web8kameleon-hub/clisonix.com" className="text-slate-400 hover:text-white text-sm font-medium">
              GitHub Examples →
            </a>
          </div>
        </section>
      </main>

      {/* ═══ ADD SOURCE MODAL ═══ */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={() => setShowAddModal(false)}
          />

          {/* Modal */}
          <div className="relative bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg p-6 shadow-2xl">
            <button
              onClick={() => setShowAddModal(false)}
              className="absolute top-4 right-4 text-slate-500 hover:text-white text-xl"
            >
              ✕
            </button>

            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
              <span className="w-10 h-10 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center text-lg">+</span>
              Add Data Source
            </h2>

            <div className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Source Name *</label>
                <input
                  type="text"
                  value={newSource.name}
                  onChange={(e) => setNewSource(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Production Temperature Sensors"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50"
                />
              </div>

              {/* Type */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Source Type *</label>
                <div className="grid grid-cols-4 gap-2">
                  {Object.entries(SOURCE_TYPES).map(([key, config]) => (
                    <button
                      key={key}
                      onClick={() => setNewSource(prev => ({ ...prev, type: key as DataSource['type'] }))}
                      className={`p-3 rounded-lg border text-center transition-all ${
                        newSource.type === key
                          ? 'border-cyan-500 bg-cyan-500/10 text-white'
                          : 'border-slate-700 bg-slate-800 text-slate-400 hover:border-slate-600'
                      }`}
                    >
                      <div className="text-xl mb-1">{config.icon}</div>
                      <div className="text-xs">{config.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Endpoint */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Endpoint URL *</label>
                <input
                  type="text"
                  value={newSource.endpoint}
                  onChange={(e) => setNewSource(prev => ({ ...prev, endpoint: e.target.value }))}
                  placeholder={
                    newSource.type === 'mqtt' ? 'mqtt://broker.example.com:1883' :
                    newSource.type === 'iot' ? 'mqtt://sensors.example.com:1883/topic/*' :
                    newSource.type === 'lora' ? 'lorawan://gateway.example.com' :
                    newSource.type === 'webhook' ? '(webhook URL will be generated)' :
                    'https://api.example.com/v1/data'
                  }
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 font-mono text-sm"
                />
              </div>

              {/* API Key (optional) */}
              {(newSource.type === 'api' || newSource.type === 'mqtt') && (
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">API Key / Token (optional)</label>
                  <input
                    type="password"
                    value={newSource.apiKey}
                    onChange={(e) => setNewSource(prev => ({ ...prev, apiKey: e.target.value }))}
                    placeholder="Bearer token or API key for authentication"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 font-mono text-sm"
                  />
                </div>
              )}

              {/* Test Result */}
              {testResult && (
                <div className={`p-4 rounded-lg border ${
                  testResult.success
                    ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-400'
                    : 'bg-red-500/10 border-red-500/50 text-red-400'
                }`}>
                  <div className="font-medium">{testResult.message}</div>
                  {testResult.data && (
                    <div className="mt-2 text-xs font-mono opacity-75 truncate">
                      {testResult.data}
                    </div>
                  )}
                </div>
              )}

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Description (optional)</label>
                <textarea
                  value={newSource.description}
                  onChange={(e) => setNewSource(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Brief description of this data source..."
                  rows={2}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 resize-none"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-between gap-3 mt-6 pt-6 border-t border-slate-700">
              <button
                onClick={handleTestConnection}
                disabled={testingConnection || !newSource.endpoint.trim()}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-all flex items-center gap-2"
              >
                {testingConnection ? (
                  <>
                    <span className="w-4 h-4 border-2 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin" />
                    Testing...
                  </>
                ) : (
                  <>
                    <span>🔌</span> Test Connection
                  </>
                )}
              </button>

              <div className="flex gap-3">
                <button
                  onClick={() => { setShowAddModal(false); resetNewSource(); }}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm font-medium transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddSource}
                  disabled={addingSource || !newSource.name.trim() || !newSource.endpoint.trim()}
                  className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-semibold transition-all flex items-center gap-2"
                >
                  {addingSource ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Adding...
                    </>
                  ) : (
                    <>
                      <span>+</span> Add Source
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────
function MetricCard({
  label,
  value,
  icon,
  accent = 'slate'
}: {
  label: string
  value: string | number
  icon: string
  accent?: 'slate' | 'emerald' | 'cyan' | 'amber'
}) {
  const accentColors = {
    slate: 'text-white',
    emerald: 'text-emerald-400',
    cyan: 'text-cyan-400',
    amber: 'text-amber-400'
  }

  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 hover:border-slate-700 transition-all">
      <div className="text-lg mb-1">{icon}</div>
      <div className={`text-xl font-bold ${accentColors[accent]}`}>{value}</div>
      <div className="text-slate-500 text-xs">{label}</div>
    </div>
  )
}

function InsightCard({
  label,
  value,
  accent = 'slate'
}: {
  label: string
  value: string
  accent?: 'slate' | 'emerald' | 'cyan' | 'amber'
}) {
  const accentColors = {
    slate: 'text-slate-200 border-slate-700',
    emerald: 'text-emerald-400 border-emerald-500/30',
    cyan: 'text-cyan-400 border-cyan-500/30',
    amber: 'text-amber-400 border-amber-500/30'
  }

  return (
    <div className={`rounded-xl border bg-slate-950/60 p-4 ${accentColors[accent]}`}>
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-bold">{value}</div>
    </div>
  )
}

function InsightRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-2">
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-slate-200">{value}</div>
    </div>
  )
}

function SourceCard({
  source,
  onConfigure,
  onViewData
}: {
  source: DataSource
  onConfigure: (source: DataSource) => void
  onViewData: (source: DataSource) => void
}) {
  const typeConfig = SOURCE_TYPES[source.type] || SOURCE_TYPES.api
  const statusConfig = STATUS_CONFIG[source.status] || STATUS_CONFIG.disconnected

  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 hover:border-cyan-500/50 transition-all group">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 bg-gradient-to-br ${typeConfig.color} rounded-xl flex items-center justify-center text-xl shadow-lg`}>
            {typeConfig.icon}
          </div>
          <div>
            <h3 className="font-semibold text-white group-hover:text-cyan-400 transition-colors">
              {source.name}
            </h3>
            <span className="text-slate-500 text-sm">{typeConfig.label}</span>
          </div>
        </div>
        <div className={`flex items-center gap-2 ${statusConfig.text}`}>
          <div className={`w-2 h-2 rounded-full ${statusConfig.dot} ${statusConfig.pulse ? 'animate-pulse' : ''}`} />
          <span className="text-xs font-medium">{statusConfig.label}</span>
        </div>
      </div>

      {source.endpoint && (
        <div className="mb-4 px-3 py-2 bg-slate-800/50 rounded-lg">
          <code className="text-xs text-slate-400 font-mono break-all">{source.endpoint}</code>
        </div>
      )}

      <div className="grid grid-cols-3 gap-3 text-center mb-4">
        <div>
          <div className="text-white font-semibold">{formatNumber(source.dataPoints)}</div>
          <div className="text-slate-500 text-xs">Data Points</div>
        </div>
        <div>
          <div className="text-white font-semibold">{source.throughput}</div>
          <div className="text-slate-500 text-xs">Throughput</div>
        </div>
        <div>
          <div className="text-white font-semibold">{source.latency}ms</div>
          <div className="text-slate-500 text-xs">Latency</div>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-slate-800">
        <span className="text-slate-500 text-xs">Last sync: {source.lastSync}</span>
        <div className="flex gap-2">
          <button
            onClick={() => onConfigure(source)}
            disabled={source.status === 'disconnected' || source.status === 'error'}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded text-xs font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title={source.status !== 'connected' ? 'Source must be connected to configure' : 'Configure this data source'}
          >
            Configure
          </button>
          <button
            onClick={() => onViewData(source)}
            disabled={source.status === 'disconnected'}
            className="px-3 py-1.5 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 rounded text-xs font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title={source.status === 'disconnected' ? 'Source must be available to view data' : 'View data from this source'}
          >
            View Data
          </button>
        </div>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────
// Utilities
// ─────────────────────────────────────────────────────────────
function formatNumber(num: number): string {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`
  return num.toString()
}

function parseThroughput(throughput: string): number {
  const match = throughput.trim().match(/^([\d.]+)\s*([KMB]?)\/s$/i)
  if (!match) return 0

  const value = Number(match[1])
  const suffix = match[2].toUpperCase()
  const multiplier = suffix === 'M' ? 1_000_000 : suffix === 'K' ? 1_000 : suffix === 'B' ? 1_000_000_000 : 1
  return value * multiplier
}

function hashString(value: string): number {
  let hash = 0
  for (let i = 0; i < value.length; i += 1) {
    hash = (hash * 31 + value.charCodeAt(i)) % 100000
  }
  return hash
}

function normalizeSeries(series: number[]): number[] {
  const min = Math.min(...series)
  const max = Math.max(...series)
  if (max === min) {
    return series.map(() => 0.5)
  }

  return series.map(value => (value - min) / (max - min))
}

function pearsonCorrelation(seriesA: number[], seriesB: number[]): number {
  const length = Math.min(seriesA.length, seriesB.length)
  if (length < 2) return 0

  const a = seriesA.slice(0, length)
  const b = seriesB.slice(0, length)
  const meanA = a.reduce((sum, value) => sum + value, 0) / length
  const meanB = b.reduce((sum, value) => sum + value, 0) / length

  let numerator = 0
  let denomA = 0
  let denomB = 0

  for (let index = 0; index < length; index += 1) {
    const deltaA = a[index] - meanA
    const deltaB = b[index] - meanB
    numerator += deltaA * deltaB
    denomA += deltaA * deltaA
    denomB += deltaB * deltaB
  }

  const denominator = Math.sqrt(denomA * denomB)
  if (!denominator) return 0

  return numerator / denominator
}

function shiftedCorrelation(seriesA: number[], seriesB: number[], offset: number): number {
  if (offset === 0) {
    return pearsonCorrelation(seriesA, seriesB)
  }

  if (offset > 0) {
    return pearsonCorrelation(seriesA.slice(offset), seriesB.slice(0, seriesB.length - offset))
  }

  const shift = Math.abs(offset)
  return pearsonCorrelation(seriesA.slice(0, seriesA.length - shift), seriesB.slice(shift))
}

function buildOperationalSeries(source: DataSource, variant: number, length = 14): number[] {
  const seed = hashString(`${source.id}:${source.name}:${variant}`)
  const throughput = parseThroughput(source.throughput)
  const throughputComponent = Math.log10(Math.max(throughput, 1) + 1)
  const dataComponent = Math.log10(source.dataPoints + 10)
  const latencyComponent = Math.max(0.2, 1 - source.latency / 300)
  const statusComponent = source.status === 'connected' ? 1 : source.status === 'syncing' ? 0.85 : 0.45
  const phase = (seed % 360) * (Math.PI / 180)
  const waveDrift = ((seed % 17) - 8) / 90

  return Array.from({ length }, (_, index) => {
    const cyclical = Math.sin((index / 2.3) + phase) * 0.16 + Math.cos((index / 3.1) + phase / 2) * 0.11
    const trend = index * (0.01 + waveDrift / 30)
    return throughputComponent * 0.26 + dataComponent * 0.22 + latencyComponent * 0.28 + statusComponent * 0.24 + cyclical + trend
  })
}

function getCorrelationStatus(correlation: number): CorrelationInsight['status'] {
  const absolute = Math.abs(correlation)
  if (absolute >= 0.9) return 'HARMONIC'
  if (absolute >= 0.75) return 'STABLE'
  if (absolute >= 0.5) return 'SYNC'
  return 'DIVERGENT'
}

function getInsightAccent(status: CorrelationInsight['status']): 'slate' | 'emerald' | 'cyan' | 'amber' {
  if (status === 'HARMONIC') return 'emerald'
  if (status === 'STABLE') return 'cyan'
  if (status === 'SYNC') return 'amber'
  return 'slate'
}

function buildCorrelationInsight(sourceA: DataSource, sourceB: DataSource): CorrelationInsight {
  const rawA = buildOperationalSeries(sourceA, 1)
  const rawB = buildOperationalSeries(sourceB, 2)
  const normalizedA = normalizeSeries(rawA)
  const normalizedB = normalizeSeries(rawB)
  const phi = 1.61803398875

  let bestOffset = 0
  let bestCorrelation = pearsonCorrelation(normalizedA, normalizedB)

  for (let offset = -3; offset <= 3; offset += 1) {
    const candidate = shiftedCorrelation(normalizedA, normalizedB, offset)
    if (Math.abs(candidate) > Math.abs(bestCorrelation)) {
      bestCorrelation = candidate
      bestOffset = offset
    }
  }

  const points = normalizedA.map((value, index) => ({
    label: `T-${normalizedA.length - index - 1}`,
    sourceA: Number(value.toFixed(3)),
    sourceB: Number(normalizedB[index].toFixed(3)),
    aligned: Math.abs(value - normalizedB[index]) <= 0.08
  }))

  return {
    sourceAName: sourceA.name,
    sourceBName: sourceB.name,
    correlation: bestCorrelation,
    resonanceScore: bestCorrelation * phi,
    strengthPercent: Math.abs(bestCorrelation) * 100,
    status: getCorrelationStatus(bestCorrelation),
    bestOffset,
    alignedPoints: points.filter(point => point.aligned).length,
    points
  }
}










