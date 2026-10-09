/**
 * MyMirror Now - Client Admin Portal
 * Dashboard personal për klientët - të dhënat e VETA
 * Real-time metrics, data sources, excel export
 */

"use client"

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'

// Types
interface DataSource {
  id: string
  name: string
  type: 'iot' | 'api' | 'mqtt' | 'database' | 'file' | 'webhook'
  endpoint: string
  status: 'active' | 'inactive' | 'error'
  last_data: string | null
  data_points: number
  created_at: string
  module_url?: string
  docs_url?: string
  region?: string
  tags?: string[]
}

interface LiveMetrics {
  cpu: number | null
  memory: number | null
  disk: number | null
  containers: number | null
  active_containers: number | null
}

interface DockerContainer {
  id: string
  name: string
  image: string
  status: string
  cpu: number
  memory: number
  ports: string
}

interface TenantStats {
  data_sources_count: number
  active_sources: number
  total_data_points: number
  tracked_metrics: number
  storage_used_gb: number | null
  api_calls_today: number | null
  internal_apis?: number | null
  external_apis?: number | null
  laboratories?: number | null
  cores?: number | null
  engines?: number | null
  reliability_score?: number | null
  source_health_ratio?: number | null
  source_quality_score?: number | null
}

interface RuntimeMeta {
  fetched_at: string | null
  upstream: string | null
  upstream_latency_ms: number | null
}

interface TrendPoint {
  timestamp: string
  value: number
}

interface LiveTrend {
  window_points: number
  reliability_score: TrendPoint[]
  source_health_ratio: TrendPoint[]
  cpu: TrendPoint[]
  directions: {
    reliability_score: 'up' | 'down' | 'stable'
    source_health_ratio: 'up' | 'down' | 'stable'
    cpu: 'up' | 'down' | 'stable'
  }
}

interface LiveAlert {
  metric: string
  severity: 'low' | 'medium' | 'high'
  message: string
  sustained?: boolean
}

interface AlertPolicy {
  cpu_high: number
  memory_high: number
  disk_high: number
  reliability_low: number
  source_health_low: number
  sustained_samples: number
}

interface JonaHealthSnapshot {
  service: 'JONA'
  status: 'healthy' | 'degraded' | 'error'
  degraded_reason: string | null
  checks: {
    upstream?: { status: string; detail?: string | null }
    operational?: { status: string; value?: boolean }
    health_score?: { status: string; value?: number | null; detail?: string | null }
    coordination?: { status: string; value?: number | null; detail?: string | null }
  }
  data: {
    operational: boolean
    health_score: number | null
    coordination_score: number
    requests_5m: number
    audio_synthesis: boolean
    timestamp?: string
  }
}

// Source type config
const SOURCE_TYPES = {
  iot: { icon: '📡', label: 'IoT Device', color: 'bg-gray-500' },
  api: { icon: '🔗', label: 'REST API', color: 'bg-purple-500' },
  mqtt: { icon: '📶', label: 'MQTT Broker', color: 'bg-green-500' },
  database: { icon: '🗄️', label: 'Database', color: 'bg-orange-500' },
  file: { icon: '📁', label: 'File Upload', color: 'bg-yellow-500' },
  webhook: { icon: '🔔', label: 'Webhook', color: 'bg-pink-500' }
}

export default function MyMirrorNowPage() {
  // State
  const [activeTab, setActiveTab] = useState<'overview' | 'sources' | 'metrics' | 'export'>('overview')
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())
  const [dashboardError, setDashboardError] = useState<string | null>(null)

  // Data state
  const [stats, setStats] = useState<TenantStats>({
    data_sources_count: 0,
    active_sources: 0,
    total_data_points: 0,
    tracked_metrics: 0,
    storage_used_gb: 0,
    api_calls_today: 0,
    internal_apis: null,
    external_apis: null,
    laboratories: null,
    cores: null,
    engines: null,
  })
  const [liveMetrics, setLiveMetrics] = useState<LiveMetrics>({
    cpu: null,
    memory: null,
    disk: null,
    containers: null,
    active_containers: null
  })
  const [jonaHealth, setJonaHealth] = useState<JonaHealthSnapshot | null>(null)
  const [containers, setContainers] = useState<DockerContainer[]>([])
  const [dataSources, setDataSources] = useState<DataSource[]>([])
  const [runtimeMeta, setRuntimeMeta] = useState<RuntimeMeta>({
    fetched_at: null,
    upstream: null,
    upstream_latency_ms: null,
  })
  const [liveTrend, setLiveTrend] = useState<LiveTrend>({
    window_points: 0,
    reliability_score: [],
    source_health_ratio: [],
    cpu: [],
    directions: {
      reliability_score: 'stable',
      source_health_ratio: 'stable',
      cpu: 'stable',
    },
  })
  const [liveAlerts, setLiveAlerts] = useState<LiveAlert[]>([])
  const [alertPolicy, setAlertPolicy] = useState<AlertPolicy>({
    cpu_high: 85,
    memory_high: 90,
    disk_high: 90,
    reliability_low: 70,
    source_health_low: 75,
    sustained_samples: 3,
  })
  const [isSavingPolicy, setIsSavingPolicy] = useState(false)

  // Modal state
  const [showAddSourceModal, setShowAddSourceModal] = useState(false)
  const [newSource, setNewSource] = useState({
    type: 'iot' as keyof typeof SOURCE_TYPES,
    name: '',
    endpoint: '',
    api_key: ''
  })
  const [isAddingSource, setIsAddingSource] = useState(false)

  // Export state
  const [isExporting, setIsExporting] = useState(false)
  const [exportType, setExportType] = useState('full')

  const isFiniteNumber = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value)
  const toNullableNumber = (value: unknown): number | null => {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : null
  }
  const formatInteger = (value: number | null) => (isFiniteNumber(value) ? value.toLocaleString() : 'Unavailable')
  const formatDecimal = (value: number | null, suffix = '') => (isFiniteNumber(value) ? `${value.toFixed(1)}${suffix}` : 'Unavailable')
  const formatPercent = (value: number | null) => (isFiniteNumber(value) ? `${value.toFixed(1)}%` : 'Unavailable')
  const formatFreshness = (iso: string | null) => {
    if (!iso) return 'Unavailable'
    const deltaMs = Date.now() - new Date(iso).getTime()
    if (!Number.isFinite(deltaMs) || deltaMs < 0) return 'Unavailable'
    const sec = Math.floor(deltaMs / 1000)
    if (sec < 60) return `${sec}s ago`
    const min = Math.floor(sec / 60)
    if (min < 60) return `${min}m ago`
    const hr = Math.floor(min / 60)
    return `${hr}h ago`
  }
  const trendDirectionLabel = (direction: 'up' | 'down' | 'stable', inverse = false) => {
    if (direction === 'stable') return 'Stable'
    if (direction === 'up') return inverse ? 'Worsening' : 'Improving'
    return inverse ? 'Improving' : 'Worsening'
  }
  const parseTrendPoints = (value: unknown): TrendPoint[] => {
    if (!Array.isArray(value)) return []
    return value
      .map((item) => {
        if (!item || typeof item !== 'object') return null
        const row = item as { timestamp?: unknown; value?: unknown }
        const timestamp = typeof row.timestamp === 'string' ? row.timestamp : null
        const parsedValue = Number(row.value)
        if (!timestamp || !Number.isFinite(parsedValue)) return null
        return { timestamp, value: parsedValue }
      })
      .filter((item): item is TrendPoint => item !== null)
  }

  // Fetch all data
  const fetchDashboardData = useCallback(async () => {
    const nextErrors: string[] = []

    const readErrorMessage = async (response: Response, message: string) => {
      const payload = await response.json().catch(() => null)
      return payload?.detail || payload?.error || `${message} (${response.status})`
    }

    try {
      const [metricsRes, containersRes, sourcesRes, jonaHealthRes, policyRes] = await Promise.all([
        fetch('/api/mymirror/live-metrics', { cache: 'no-store' }),
        fetch('/api/mymirror/docker-containers', { cache: 'no-store' }),
        fetch('/api/mymirror/data-sources', { cache: 'no-store' }),
        fetch('/api/jona/health', { cache: 'no-store' }),
        fetch('/api/mymirror/alert-policy', { cache: 'no-store' })
      ])

      if (metricsRes.ok) {
        const metricsData = await metricsRes.json()
        const nextSystem = metricsData.system || metricsData
        setRuntimeMeta({
          fetched_at: typeof metricsData?.meta?.fetched_at === 'string' ? metricsData.meta.fetched_at : null,
          upstream: typeof metricsData?.meta?.upstream === 'string' ? metricsData.meta.upstream : null,
          upstream_latency_ms: toNullableNumber(metricsData?.meta?.upstream_latency_ms),
        })
        setLiveMetrics({
          cpu: toNullableNumber(nextSystem.cpu),
          memory: toNullableNumber(nextSystem.memory),
          disk: toNullableNumber(nextSystem.disk),
          containers: toNullableNumber(nextSystem.containers),
          active_containers: toNullableNumber(nextSystem.active_containers)
        })
        if (metricsData.stats) {
          setStats(prev => ({
            ...prev,
            ...metricsData.stats,
            storage_used_gb: toNullableNumber(metricsData.stats.storage_used_gb),
            api_calls_today: toNullableNumber(metricsData.stats.api_calls_today),
            internal_apis: toNullableNumber(metricsData.stats.internal_apis),
            external_apis: toNullableNumber(metricsData.stats.external_apis),
            laboratories: toNullableNumber(metricsData.stats.laboratories),
            cores: toNullableNumber(metricsData.stats.cores),
            engines: toNullableNumber(metricsData.stats.engines),
            reliability_score: toNullableNumber(metricsData.stats.reliability_score),
            source_health_ratio: toNullableNumber(metricsData.stats.source_health_ratio),
            source_quality_score: toNullableNumber(metricsData.stats.source_quality_score),
          }))
        }
        setLiveTrend({
          window_points: Number(metricsData?.trend?.window_points) || 0,
          reliability_score: parseTrendPoints(metricsData?.trend?.reliability_score),
          source_health_ratio: parseTrendPoints(metricsData?.trend?.source_health_ratio),
          cpu: parseTrendPoints(metricsData?.trend?.cpu),
          directions: {
            reliability_score: metricsData?.trend?.directions?.reliability_score === 'up' || metricsData?.trend?.directions?.reliability_score === 'down' ? metricsData.trend.directions.reliability_score : 'stable',
            source_health_ratio: metricsData?.trend?.directions?.source_health_ratio === 'up' || metricsData?.trend?.directions?.source_health_ratio === 'down' ? metricsData.trend.directions.source_health_ratio : 'stable',
            cpu: metricsData?.trend?.directions?.cpu === 'up' || metricsData?.trend?.directions?.cpu === 'down' ? metricsData.trend.directions.cpu : 'stable',
          },
        })
        setLiveAlerts(
          Array.isArray(metricsData?.alerts)
            ? metricsData.alerts.filter((alert: unknown): alert is LiveAlert => {
                if (!alert || typeof alert !== 'object') return false
                const row = alert as { metric?: unknown; severity?: unknown; message?: unknown; sustained?: unknown }
                return (
                  typeof row.metric === 'string' &&
                  (row.severity === 'low' || row.severity === 'medium' || row.severity === 'high') &&
                  typeof row.message === 'string' &&
                  (typeof row.sustained === 'boolean' || typeof row.sustained === 'undefined')
                )
              })
            : [],
        )
        if (metricsData?.alert_policy && typeof metricsData.alert_policy === 'object') {
          const policy = metricsData.alert_policy as Record<string, unknown>
          setAlertPolicy({
            cpu_high: Number(policy.cpu_high) || 85,
            memory_high: Number(policy.memory_high) || 90,
            disk_high: Number(policy.disk_high) || 90,
            reliability_low: Number(policy.reliability_low) || 70,
            source_health_low: Number(policy.source_health_low) || 75,
            sustained_samples: Number(policy.sustained_samples) || 3,
          })
        }
      } else {
        nextErrors.push(await readErrorMessage(metricsRes, 'Live metrics unavailable'))
      }

      if (policyRes.ok) {
        const policyData = await policyRes.json().catch(() => null)
        if (policyData?.policy && typeof policyData.policy === 'object') {
          const policy = policyData.policy as Record<string, unknown>
          setAlertPolicy({
            cpu_high: Number(policy.cpu_high) || 85,
            memory_high: Number(policy.memory_high) || 90,
            disk_high: Number(policy.disk_high) || 90,
            reliability_low: Number(policy.reliability_low) || 70,
            source_health_low: Number(policy.source_health_low) || 75,
            sustained_samples: Number(policy.sustained_samples) || 3,
          })
        }
      }

      if (containersRes.ok) {
        const containersData = await containersRes.json()
        const nextContainers = Array.isArray(containersData?.containers)
          ? containersData.containers
          : Array.isArray(containersData)
            ? containersData
            : []

        setContainers(nextContainers)
        setLiveMetrics(prev => ({
          ...prev,
          containers: toNullableNumber(containersData?.total ?? nextContainers.length ?? prev.containers),
          active_containers: toNullableNumber(
            containersData?.running ??
              nextContainers.filter((container: DockerContainer) => {
                const rawStatus = `${container?.status ?? ''}`.toLowerCase()
                return !/(exited|stopped|dead|unhealthy)/.test(rawStatus) && /(running|up|healthy)/.test(rawStatus)
              }).length ??
              prev.active_containers
          )
        }))
      } else {
        setContainers([])
        setLiveMetrics(prev => ({ ...prev, containers: null, active_containers: null }))
        nextErrors.push(await readErrorMessage(containersRes, 'Docker container metrics unavailable'))
      }

      if (sourcesRes.ok) {
        const sourcesData = await sourcesRes.json()
        const nextSources = sourcesData.sources || []
        setDataSources(nextSources)
        setStats(prev => ({
          ...prev,
          ...(sourcesData.stats || {}),
          data_sources_count: sourcesData.count ?? nextSources.length,
          active_sources: sourcesData.active ?? nextSources.filter((source: DataSource) => source.status === 'active').length,
          storage_used_gb: toNullableNumber(sourcesData?.stats?.storage_used_gb),
          api_calls_today: toNullableNumber(sourcesData?.stats?.api_calls_today)
        }))
      } else {
        setDataSources([])
        setStats(prev => ({
          ...prev,
          data_sources_count: 0,
          active_sources: 0,
          total_data_points: 0,
          tracked_metrics: 0,
        }))
        nextErrors.push(await readErrorMessage(sourcesRes, 'Data sources unavailable'))
      }

      if (jonaHealthRes.ok) {
        const jonaPayload = await jonaHealthRes.json().catch(() => null)
        setJonaHealth(jonaPayload?.data || null)
      } else {
        setJonaHealth(null)
      }

      setDashboardError(nextErrors.length > 0 ? nextErrors.join(' | ') : null)
      setLastUpdated(new Date())
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
      setDashboardError(error instanceof Error ? error.message : 'Failed to fetch dashboard data')
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Initial load and auto-refresh
  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [fetchDashboardData])

  // Handle add data source
  const handleAddSource = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsAddingSource(true)

    try {
      const response = await fetch('/api/mymirror/data-sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSource)
      })

      if (response.ok) {
        setShowAddSourceModal(false)
        setNewSource({ type: 'iot', name: '', endpoint: '', api_key: '' })
        fetchDashboardData()
      } else {
        const error = await response.json()
        alert(error.detail || 'Failed to add data source')
      }
    } catch (error) {
      console.error('Failed to add source:', error)
      alert('Connection error. Please try again.')
    } finally {
      setIsAddingSource(false)
    }
  }

  // Handle delete data source
  const handleDeleteSource = async (sourceId: string) => {
    if (!confirm('Are you sure you want to delete this data source?')) return

    try {
      const response = await fetch(`/api/mymirror/data-sources/${sourceId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        fetchDashboardData()
      }
    } catch (error) {
      console.error('Failed to delete source:', error)
    }
  }

  const handleSaveAlertPolicy = async () => {
    setIsSavingPolicy(true)
    try {
      const response = await fetch('/api/mymirror/alert-policy', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ policy: alertPolicy }),
      })

      if (!response.ok) {
        const payload = await response.json().catch(() => null)
        alert(payload?.error || payload?.detail || 'Failed to save alert policy')
        return
      }

      fetchDashboardData()
    } catch (error) {
      console.error('Failed to save alert policy:', error)
      alert('Failed to save alert policy')
    } finally {
      setIsSavingPolicy(false)
    }
  }

  // Handle Excel export
  const handleExport = async (format: 'excel' | 'pptx') => {
    setIsExporting(true)

    try {
      const response = await fetch('/api/mymirror/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: exportType,
          format: format,
          date_range: {
            start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            end: new Date().toISOString()
          }
        })
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `mymirror_export_${new Date().toISOString().split('T')[0]}.${format === 'excel' ? 'xlsx' : 'pptx'}`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Export failed:', error)
      alert('Export failed. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading MyMirror Now...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-slate-700/50 bg-slate-800/30 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link
                href="/modules"
                className="text-gray-400 hover:text-white transition-colors"
              >
                ← Back to Modules
              </Link>
              <div className="h-6 w-px bg-slate-600"></div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-gray-200 to-white bg-clip-text text-transparent">
                📊 My Data Dashboard
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </span>
              <button
                onClick={fetchDashboardData}
                className="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-600/50 transition-colors"
                title="Refresh"
              >
                🔄
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {dashboardError ? (
          <div className="mb-6 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            Live data error: {dashboardError}
          </div>
        ) : null}

        {/* Page Header */}
        <div className="mb-6 space-y-3">
          <p className="text-gray-400">Manage your data sources, open-data feeds, and module-backed live metrics.</p>
          <div className="flex flex-wrap gap-2 text-sm">
            <Link href="/modules/my-data-dashboard" className="rounded-full border border-slate-600 bg-slate-800/60 px-3 py-1 text-slate-200 hover:border-slate-400 hover:text-white">
              🔌 My Data Dashboard
            </Link>
            <Link href="/modules/aviation-weather" className="rounded-full border border-slate-600 bg-slate-800/60 px-3 py-1 text-slate-200 hover:border-slate-400 hover:text-white">
              AW Aviation Weather
            </Link>
            <Link href="/modules/kloud-bridge" className="rounded-full border border-slate-600 bg-slate-800/60 px-3 py-1 text-slate-200 hover:border-slate-400 hover:text-white">
              ☁️ Kloud Bridge
            </Link>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
            <div className="text-2xl font-bold text-white">{stats.data_sources_count}</div>
            <div className="text-sm text-gray-400">Data Sources</div>
          </div>
          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
            <div className="text-2xl font-bold text-green-400">{stats.active_sources}</div>
            <div className="text-sm text-gray-400">Active</div>
          </div>
          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
            <div className="text-2xl font-bold text-gray-300">{formatInteger(stats.total_data_points)}</div>
            <div className="text-sm text-gray-400">Total Data Points</div>
          </div>
          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
            <div className="text-2xl font-bold text-purple-400">{formatInteger(stats.tracked_metrics)}</div>
            <div className="text-sm text-gray-400">Tracked Metrics</div>
          </div>
          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
            <div className="text-2xl font-bold text-orange-400">{formatDecimal(stats.storage_used_gb, ' GB')}</div>
            <div className="text-sm text-gray-400">Storage Used</div>
          </div>
          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
            <div className="text-2xl font-bold text-pink-400">{formatInteger(stats.api_calls_today)}</div>
            <div className="text-sm text-gray-400">API Calls Today</div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-slate-800/40 rounded-xl p-4 border border-slate-700/50">
            <div className="text-xl font-bold text-cyan-300">{formatInteger(stats.internal_apis ?? null)}</div>
            <div className="text-sm text-gray-400">Internal APIs</div>
          </div>
          <div className="bg-slate-800/40 rounded-xl p-4 border border-slate-700/50">
            <div className="text-xl font-bold text-indigo-300">{formatInteger(stats.external_apis ?? null)}</div>
            <div className="text-sm text-gray-400">External APIs</div>
          </div>
          <div className="bg-slate-800/40 rounded-xl p-4 border border-slate-700/50">
            <div className="text-xl font-bold text-emerald-300">{formatInteger(stats.laboratories ?? null)}</div>
            <div className="text-sm text-gray-400">Laboratories</div>
          </div>
          <div className="bg-slate-800/40 rounded-xl p-4 border border-slate-700/50">
            <div className="text-xl font-bold text-amber-300">{formatInteger(stats.cores ?? null)}</div>
            <div className="text-sm text-gray-400">Cores</div>
          </div>
          <div className="bg-slate-800/40 rounded-xl p-4 border border-slate-700/50">
            <div className="text-xl font-bold text-violet-300">{formatInteger(stats.engines ?? null)}</div>
            <div className="text-sm text-gray-400">Engines</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-slate-800/40 rounded-xl p-4 border border-slate-700/50">
            <div className="text-xl font-bold text-emerald-300">{formatPercent(stats.reliability_score ?? null)}</div>
            <div className="text-sm text-gray-400">Runtime Reliability</div>
          </div>
          <div className="bg-slate-800/40 rounded-xl p-4 border border-slate-700/50">
            <div className="text-xl font-bold text-cyan-300">{formatFreshness(runtimeMeta.fetched_at)}</div>
            <div className="text-sm text-gray-400">Data Freshness</div>
          </div>
          <div className="bg-slate-800/40 rounded-xl p-4 border border-slate-700/50">
            <div className="text-xl font-bold text-amber-300">
              {isFiniteNumber(runtimeMeta.upstream_latency_ms) ? `${runtimeMeta.upstream_latency_ms}ms` : 'Unavailable'}
            </div>
            <div className="text-sm text-gray-400">Upstream Latency</div>
          </div>
        </div>

        {/* Add Data Source Button */}
        <div className="flex justify-end mb-4">
          <button
            onClick={() => setShowAddSourceModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-lg transition-colors font-medium"
          >
            <span>+</span>
            <span>Add Data Source</span>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-slate-700/50 pb-2">
          {(['overview', 'sources', 'metrics', 'export'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-t-lg font-medium transition-colors ${
                activeTab === tab
                  ? 'bg-slate-700/50 text-white border-b-2 border-white'
                  : 'text-gray-400 hover:text-white hover:bg-slate-700/30'
              }`}
            >
              {tab === 'overview' && '📈 Live Metrics'}
              {tab === 'sources' && '🔌 Active Data Sources'}
              {tab === 'metrics' && '📊 Analytics'}
              {tab === 'export' && '📗 Excel Export'}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {/* Overview Tab - Live Metrics */}
          {activeTab === 'overview' && (
            <>
              {/* System Metrics */}
              <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <span>🖥️</span>
                  <span>LIVE System Metrics</span>
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  {/* CPU */}
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-gray-400">CPU Usage</span>
                      <span className="font-bold text-white">{formatPercent(liveMetrics.cpu)}</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-gray-400 to-white transition-all duration-500"
                        style={{ width: `${Math.min(liveMetrics.cpu ?? 0, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                  {/* RAM */}
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-gray-400">RAM Usage</span>
                      <span className="font-bold text-green-400">{formatPercent(liveMetrics.memory)}</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-green-500 to-blue-800 transition-all duration-500"
                        style={{ width: `${Math.min(liveMetrics.memory ?? 0, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                  {/* Disk */}
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-gray-400">Disk Usage</span>
                      <span className="font-bold text-orange-400">{formatPercent(liveMetrics.disk)}</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-orange-500 to-yellow-500 transition-all duration-500"
                        style={{ width: `${Math.min(liveMetrics.disk ?? 0, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                  {/* Containers */}
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-gray-400">Containers</span>
                      <span className="font-bold text-purple-400">
                        {isFiniteNumber(liveMetrics.active_containers) && isFiniteNumber(liveMetrics.containers)
                          ? `${liveMetrics.active_containers}/${liveMetrics.containers}`
                          : 'Unavailable'}
                      </span>
                    </div>
                    <div className="text-sm mt-1">
                      {!isFiniteNumber(liveMetrics.containers) || liveMetrics.containers <= 0 ? (
                        <span className="text-slate-400">⌛ Waiting for live data</span>
                      ) : liveMetrics.active_containers === liveMetrics.containers ? (
                        <span className="text-green-400">✅ All Running</span>
                      ) : (
                        <span className="text-yellow-400">⚠️ Some Issues</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between mb-4">
                  <h2 className="text-lg font-semibold flex items-center gap-2">
                    <span>🛡️</span>
                    <span>JONA Safety Health</span>
                  </h2>
                  <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold border ${
                    !jonaHealth
                      ? 'border-slate-600 text-slate-400 bg-slate-700/30'
                      : jonaHealth.status === 'healthy'
                        ? 'border-green-500/30 text-green-300 bg-green-500/10'
                        : jonaHealth.status === 'degraded'
                          ? 'border-yellow-500/30 text-yellow-300 bg-yellow-500/10'
                          : 'border-red-500/30 text-red-300 bg-red-500/10'
                  }`}>
                    <span>{!jonaHealth ? '○' : jonaHealth.status === 'healthy' ? '●' : jonaHealth.status === 'degraded' ? '◐' : '◉'}</span>
                    <span>{(jonaHealth?.status ?? 'unavailable').toUpperCase()}</span>
                  </span>
                </div>

                {!jonaHealth ? (
                  <p className="text-sm text-slate-400">JONA health snapshot is not available yet.</p>
                ) : (
                  <>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="rounded-lg border border-slate-700/60 bg-slate-900/40 p-4">
                        <div className="text-xs uppercase tracking-wide text-slate-400 mb-1">Operational</div>
                        <div className={`text-lg font-semibold ${jonaHealth.data.operational ? 'text-green-300' : 'text-red-300'}`}>
                          {jonaHealth.data.operational ? 'ONLINE' : 'DEGRADED'}
                        </div>
                      </div>
                      <div className="rounded-lg border border-slate-700/60 bg-slate-900/40 p-4">
                        <div className="text-xs uppercase tracking-wide text-slate-400 mb-1">Health Score</div>
                        <div className="text-lg font-semibold text-white">
                          {jonaHealth.data.health_score ?? 'N/A'}
                        </div>
                      </div>
                      <div className="rounded-lg border border-slate-700/60 bg-slate-900/40 p-4">
                        <div className="text-xs uppercase tracking-wide text-slate-400 mb-1">Coordination</div>
                        <div className="text-lg font-semibold text-purple-300">
                          {jonaHealth.data.coordination_score.toFixed(2)}
                        </div>
                      </div>
                      <div className="rounded-lg border border-slate-700/60 bg-slate-900/40 p-4">
                        <div className="text-xs uppercase tracking-wide text-slate-400 mb-1">Requests / 5m</div>
                        <div className="text-lg font-semibold text-cyan-300">
                          {jonaHealth.data.requests_5m}
                        </div>
                      </div>
                    </div>

                    <div className="rounded-lg border border-slate-700/60 bg-slate-900/40 p-4 mb-4">
                      <div className="text-xs uppercase tracking-wide text-slate-400 mb-2">Health Contract</div>
                      <div className="grid gap-2 text-sm text-slate-300 md:grid-cols-2">
                        <div>
                          Upstream: <span className={jonaHealth.checks.upstream?.status === 'healthy' ? 'text-green-300' : 'text-red-300'}>{jonaHealth.checks.upstream?.status ?? 'unknown'}</span>
                        </div>
                        <div>
                          Coordination check: <span className={jonaHealth.checks.coordination?.status === 'healthy' ? 'text-green-300' : 'text-yellow-300'}>{jonaHealth.checks.coordination?.status ?? 'unknown'}</span>
                        </div>
                        <div>
                          Health score check: <span className={jonaHealth.checks.health_score?.status === 'healthy' ? 'text-green-300' : 'text-yellow-300'}>{jonaHealth.checks.health_score?.status ?? 'unknown'}</span>
                        </div>
                        <div>
                          Audio synthesis: <span className={jonaHealth.data.audio_synthesis ? 'text-green-300' : 'text-slate-400'}>{jonaHealth.data.audio_synthesis ? 'enabled' : 'disabled'}</span>
                        </div>
                      </div>
                    </div>

                    <p className={`text-sm ${jonaHealth.degraded_reason ? 'text-yellow-300' : 'text-slate-400'}`}>
                      {jonaHealth.degraded_reason ?? 'JONA is within expected safety thresholds.'}
                    </p>
                  </>
                )}
              </div>

              {/* Docker Containers Table */}
              <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <span>🐳</span>
                  <span>LIVE Docker Containers</span>
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="text-left text-gray-400 border-b border-slate-700">
                        <th className="pb-3 pr-4">Status</th>
                        <th className="pb-3 pr-4">Container</th>
                        <th className="pb-3 pr-4">Image</th>
                        <th className="pb-3 pr-4">CPU</th>
                        <th className="pb-3 pr-4">Memory</th>
                        <th className="pb-3">Ports</th>
                      </tr>
                    </thead>
                    <tbody>
                      {containers.length === 0 ? (
                        <tr>
                          <td colSpan={6} className="py-8 text-center text-gray-500">
                            No containers found
                          </td>
                        </tr>
                      ) : (
                        containers.map((container) => (
                          <tr key={container.id} className="border-b border-slate-700/50 hover:bg-slate-700/20">
                            <td className="py-3 pr-4">
                              <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
                                container.status === 'running'
                                  ? 'bg-green-500/20 text-green-400'
                                  : 'bg-red-500/20 text-red-400'
                              }`}>
                                {container.status === 'running' ? '●' : '○'}
                                {container.status === 'running' ? 'Running' : container.status}
                              </span>
                            </td>
                            <td className="py-3 pr-4 font-medium">{container.name}</td>
                            <td className="py-3 pr-4 text-gray-400 text-sm truncate max-w-[150px]">
                              {container.image}
                            </td>
                            <td className="py-3 pr-4">{container.cpu}%</td>
                            <td className="py-3 pr-4">{container.memory}%</td>
                            <td className="py-3 text-gray-400">{container.ports || '-'}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}

          {/* Sources Tab */}
          {activeTab === 'sources' && (
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <span>🔌</span>
                <span>Active Data Sources</span>
              </h2>

              {dataSources.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📡</div>
                  <p className="text-gray-400 mb-4">No data sources configured yet.</p>
                  <button
                    onClick={() => setShowAddSourceModal(true)}
                    className="px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-lg transition-colors"
                  >
                    + Add your first data source
                  </button>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="text-left text-gray-400 border-b border-slate-700">
                        <th className="pb-3 pr-4">Status</th>
                        <th className="pb-3 pr-4">Name</th>
                        <th className="pb-3 pr-4">Type</th>
                        <th className="pb-3 pr-4">Endpoint</th>
                        <th className="pb-3 pr-4">Last Data</th>
                        <th className="pb-3 pr-4">Data Points</th>
                        <th className="pb-3">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dataSources.map((source) => (
                        <tr key={source.id} className="border-b border-slate-700/50 hover:bg-slate-700/20">
                          <td className="py-3 pr-4">
                            <span className={`inline-block w-3 h-3 rounded-full ${
                              source.status === 'active' ? 'bg-green-500' :
                              source.status === 'error' ? 'bg-red-500' : 'bg-gray-500'
                            }`}></span>
                          </td>
                          <td className="py-3 pr-4 font-medium">{source.name}</td>
                          <td className="py-3 pr-4">
                            <span className="flex items-center gap-1">
                              {SOURCE_TYPES[source.type]?.icon || '📦'}
                              {SOURCE_TYPES[source.type]?.label || source.type}
                            </span>
                          </td>
                          <td className="py-3 pr-4 text-gray-400 text-sm truncate max-w-[200px]">
                            {source.endpoint}
                          </td>
                          <td className="py-3 pr-4 text-gray-400">
                            {source.last_data ? new Date(source.last_data).toLocaleString() : 'Never'}
                          </td>
                          <td className="py-3 pr-4">{source.data_points.toLocaleString()}</td>
                          <td className="py-3">
                            <div className="flex gap-2">
                              {source.docs_url ? (
                                <a
                                  href={source.docs_url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="p-1 hover:bg-slate-600/50 rounded"
                                  title="Open source endpoint"
                                >
                                  ⚙️
                                </a>
                              ) : (
                                <button className="p-1 hover:bg-slate-600/50 rounded" title="Configure">⚙️</button>
                              )}
                              {source.module_url ? (
                                <Link
                                  href={source.module_url}
                                  className="p-1 hover:bg-slate-600/50 rounded"
                                  title="Open linked module"
                                >
                                  📊
                                </Link>
                              ) : (
                                <button className="p-1 hover:bg-slate-600/50 rounded" title="View Metrics">📊</button>
                              )}
                              <button
                                className="p-1 hover:bg-red-600/50 rounded"
                                title="Delete"
                                onClick={() => handleDeleteSource(source.id)}
                              >🗑️</button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Metrics Tab */}
          {activeTab === 'metrics' && (
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <span>📊</span>
                <span>Analytics Overview</span>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="p-4 bg-slate-700/30 rounded-lg">
                  <h3 className="text-gray-400 mb-2">Data Ingestion Rate</h3>
                  <div className="text-3xl font-bold text-white">
                    {isFiniteNumber(stats.api_calls_today) && isFiniteNumber(stats.total_data_points) && stats.api_calls_today > 0
                      ? `${(stats.total_data_points / Math.max(stats.api_calls_today, 1)).toFixed(1)} pts/call`
                      : 'Unavailable'}
                  </div>
                  <div className="text-sm text-slate-400 mt-1">Derived from live totals only</div>
                </div>
                <div className="p-4 bg-slate-700/30 rounded-lg">
                  <h3 className="text-gray-400 mb-2">API Response Time</h3>
                  <div className="text-3xl font-bold text-green-400">
                    {isFiniteNumber(runtimeMeta.upstream_latency_ms) ? `${runtimeMeta.upstream_latency_ms}ms` : 'Unavailable'}
                  </div>
                  <div className="text-sm text-slate-400 mt-1">Measured from live upstream calls</div>
                </div>
                <div className="p-4 bg-slate-700/30 rounded-lg">
                  <h3 className="text-gray-400 mb-2">Source Quality Score</h3>
                  <div className="text-3xl font-bold text-purple-400">{formatPercent(stats.source_quality_score ?? null)}</div>
                  <div className="text-sm text-slate-400 mt-1">Derived from active, endpoint, docs, and tagged source ratios</div>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 bg-slate-700/30 rounded-lg border border-slate-600/40">
                  <h3 className="text-gray-300 mb-3">Trend Signals ({liveTrend.window_points} samples)</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Reliability</span>
                      <span className="text-emerald-300">{trendDirectionLabel(liveTrend.directions.reliability_score)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Source Health</span>
                      <span className="text-cyan-300">{trendDirectionLabel(liveTrend.directions.source_health_ratio)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">CPU Pressure</span>
                      <span className="text-amber-300">{trendDirectionLabel(liveTrend.directions.cpu, true)}</span>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-slate-700/30 rounded-lg border border-slate-600/40">
                  <h3 className="text-gray-300 mb-3">Active Alerts</h3>
                  {liveAlerts.length === 0 ? (
                    <p className="text-sm text-emerald-300">No active alerts from live thresholds.</p>
                  ) : (
                    <div className="space-y-2">
                      {liveAlerts.map((alert, idx) => (
                        <div key={`${alert.metric}-${idx}`} className="rounded-lg border border-slate-600/50 bg-slate-800/60 px-3 py-2 text-sm">
                          <div className="flex items-center justify-between">
                            <span className={alert.severity === 'high' ? 'text-red-300' : 'text-yellow-300'}>{alert.metric}</span>
                            <span className="text-slate-400">{alert.sustained ? 'sustained' : 'spike'}</span>
                          </div>
                          <p className="text-slate-200 mt-1">{alert.message}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-6 p-4 bg-slate-700/30 rounded-lg border border-slate-600/40">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-gray-300">Alert Policy (Per Tenant)</h3>
                  <button
                    onClick={handleSaveAlertPolicy}
                    disabled={isSavingPolicy}
                    className="px-3 py-1.5 rounded bg-gray-600 hover:bg-gray-500 disabled:bg-gray-700 text-sm"
                  >
                    {isSavingPolicy ? 'Saving...' : 'Save Policy'}
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                  <label className="text-slate-300">CPU High %
                    <input
                      type="number"
                      min={50}
                      max={100}
                      value={alertPolicy.cpu_high}
                      onChange={(e) => setAlertPolicy(prev => ({ ...prev, cpu_high: Number(e.target.value) || prev.cpu_high }))}
                      className="mt-1 w-full rounded bg-slate-800 border border-slate-600 px-2 py-1"
                    />
                  </label>
                  <label className="text-slate-300">Memory High %
                    <input
                      type="number"
                      min={50}
                      max={100}
                      value={alertPolicy.memory_high}
                      onChange={(e) => setAlertPolicy(prev => ({ ...prev, memory_high: Number(e.target.value) || prev.memory_high }))}
                      className="mt-1 w-full rounded bg-slate-800 border border-slate-600 px-2 py-1"
                    />
                  </label>
                  <label className="text-slate-300">Disk High %
                    <input
                      type="number"
                      min={50}
                      max={100}
                      value={alertPolicy.disk_high}
                      onChange={(e) => setAlertPolicy(prev => ({ ...prev, disk_high: Number(e.target.value) || prev.disk_high }))}
                      className="mt-1 w-full rounded bg-slate-800 border border-slate-600 px-2 py-1"
                    />
                  </label>
                  <label className="text-slate-300">Reliability Low %
                    <input
                      type="number"
                      min={0}
                      max={100}
                      value={alertPolicy.reliability_low}
                      onChange={(e) => setAlertPolicy(prev => ({ ...prev, reliability_low: Number(e.target.value) || prev.reliability_low }))}
                      className="mt-1 w-full rounded bg-slate-800 border border-slate-600 px-2 py-1"
                    />
                  </label>
                  <label className="text-slate-300">Source Health Low %
                    <input
                      type="number"
                      min={0}
                      max={100}
                      value={alertPolicy.source_health_low}
                      onChange={(e) => setAlertPolicy(prev => ({ ...prev, source_health_low: Number(e.target.value) || prev.source_health_low }))}
                      className="mt-1 w-full rounded bg-slate-800 border border-slate-600 px-2 py-1"
                    />
                  </label>
                  <label className="text-slate-300">Sustained Samples
                    <input
                      type="number"
                      min={2}
                      max={10}
                      value={alertPolicy.sustained_samples}
                      onChange={(e) => setAlertPolicy(prev => ({ ...prev, sustained_samples: Number(e.target.value) || prev.sustained_samples }))}
                      className="mt-1 w-full rounded bg-slate-800 border border-slate-600 px-2 py-1"
                    />
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Export Tab */}
          {activeTab === 'export' && (
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-lg font-semibold flex items-center gap-2">
                    <span>📗</span>
                    <span>EXCEL ∞ LIVE</span>
                  </h2>
                  <p className="text-gray-400 text-sm">Production-Ready Dashboard with REAL Data</p>
                </div>
                <span className="text-sm text-gray-400">
                  Last updated: {lastUpdated.toLocaleTimeString()}
                </span>
              </div>

              <div className="mb-6">
                <label className="block text-gray-400 mb-2">Export Type</label>
                <select
                  value={exportType}
                  onChange={(e) => setExportType(e.target.value)}
                  className="bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 w-full max-w-xs"
                >
                  <option value="full">Full Dataset</option>
                  <option value="metrics">System Metrics Only</option>
                  <option value="sources">Data Sources Only</option>
                  <option value="containers">Docker Containers</option>
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-6 bg-slate-700/30 rounded-xl border border-slate-600/50 text-center">
                  <div className="text-4xl mb-3">📗</div>
                  <h3 className="font-semibold mb-2">Download LIVE Excel</h3>
                  <p className="text-gray-400 text-sm mb-4">Real API Data Export</p>
                  <button
                    onClick={() => handleExport('excel')}
                    disabled={isExporting}
                    className="w-full px-4 py-2 bg-green-600 hover:bg-green-500 disabled:bg-gray-600 rounded-lg transition-colors"
                  >
                    {isExporting ? 'Exporting...' : 'Download XLSX'}
                  </button>
                </div>

                <div className="p-6 bg-slate-700/30 rounded-xl border border-slate-600/50 text-center">
                  <div className="text-4xl mb-3">📙</div>
                  <h3 className="font-semibold mb-2">Download PPTX</h3>
                  <p className="text-gray-400 text-sm mb-4">Presentation Export</p>
                  <button
                    onClick={() => handleExport('pptx')}
                    disabled={isExporting}
                    className="w-full px-4 py-2 bg-orange-600 hover:bg-orange-500 disabled:bg-gray-600 rounded-lg transition-colors"
                  >
                    {isExporting ? 'Exporting...' : 'Download PPTX'}
                  </button>
                </div>

                <div className="p-6 bg-slate-700/30 rounded-xl border border-slate-600/50 text-center">
                  <div className="text-4xl mb-3">🔬</div>
                  <h3 className="font-semibold mb-2">Protocol Kitchen</h3>
                  <p className="text-gray-400 text-sm mb-4">Pipeline Dashboard</p>
                  <Link
                    href="/modules/protocol-kitchen"
                    className="block w-full px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition-colors"
                  >
                    Open Kitchen
                  </Link>
                </div>
              </div>

              {/* Quick Links */}
              <div className="mt-8">
                <h3 className="text-gray-400 mb-4">🔗 Quick Links</h3>
                <div className="flex flex-wrap gap-3">
                  <Link href="/modules/reporting-dashboard" className="px-4 py-2 bg-slate-700/50 hover:bg-slate-600/50 rounded-lg transition-colors">
                    📊 API Dashboard
                  </Link>
                  <Link href="/modules/data-collection" className="px-4 py-2 bg-slate-700/50 hover:bg-slate-600/50 rounded-lg transition-colors">
                    📈 Analytics Center
                  </Link>
                  <Link href="/modules" className="px-4 py-2 bg-slate-700/50 hover:bg-slate-600/50 rounded-lg transition-colors">
                    🏠 All Modules
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add Data Source Modal */}
      {showAddSourceModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-slate-800 rounded-xl border border-slate-700 w-full max-w-md mx-4 shadow-2xl">
            <div className="flex items-center justify-between p-4 border-b border-slate-700">
              <h3 className="text-lg font-semibold">Add New Data Source</h3>
              <button
                onClick={() => setShowAddSourceModal(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleAddSource} className="p-4 space-y-4">
              <div>
                <label className="block text-gray-400 mb-2">Source Type</label>
                <div className="grid grid-cols-3 gap-2">
                  {(Object.keys(SOURCE_TYPES) as (keyof typeof SOURCE_TYPES)[]).map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => setNewSource({ ...newSource, type })}
                      className={`p-3 rounded-lg border transition-colors ${
                        newSource.type === type
                          ? 'border-white bg-white/20'
                          : 'border-slate-600 bg-slate-700/50 hover:border-slate-500'
                      }`}
                    >
                      <div className="text-2xl mb-1">{SOURCE_TYPES[type].icon}</div>
                      <div className="text-xs">{SOURCE_TYPES[type].label}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-gray-400 mb-2">Source Name</label>
                <input
                  type="text"
                  placeholder="e.g., Temperature Sensor #1"
                  value={newSource.name}
                  onChange={(e) => setNewSource({ ...newSource, name: e.target.value })}
                  required
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:border-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-2">Connection URL / Endpoint</label>
                <input
                  type="text"
                  placeholder="e.g., mqtt://broker.example.com:1883"
                  value={newSource.endpoint}
                  onChange={(e) => setNewSource({ ...newSource, endpoint: e.target.value })}
                  required
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:border-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-2">API Key / Token (optional)</label>
                <input
                  type="password"
                  placeholder="Your API key or authentication token"
                  value={newSource.api_key}
                  onChange={(e) => setNewSource({ ...newSource, api_key: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:border-white focus:outline-none"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddSourceModal(false)}
                  className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isAddingSource}
                  className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-500 disabled:bg-gray-700 rounded-lg transition-colors"
                >
                  {isAddingSource ? 'Adding...' : 'Add Source'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}







