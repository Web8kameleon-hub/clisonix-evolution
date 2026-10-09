'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { getMicroserviceIcon } from '@/lib/microservice-icons';

interface SystemMetrics {
  cpu_percent: number | null;
  memory_percent: number | null;
  disk_percent: number | null;
  uptime_seconds: number | null;
}

interface DiscoveryService {
  id?: string;
  name?: string;
  url?: string;
  category?: string;
  capabilities?: string[];
  health?: string;
  stack?: string;
  source?: string;
}

interface DockerContainerInfo {
  name?: string;
  container_name?: string;
  state?: string;
  status?: string;
  State?: string;
  Status?: string;
  Names?: string[] | string;
  healthy?: boolean;
}

interface ServiceStatus {
  id: string;
  name: string;
  icon: string;
  status: 'online' | 'offline' | 'degraded';
  responseTime?: number;
  url?: string;
  category?: string;
  stack?: string;
  source?: string;
  capabilities?: string[];
}

interface DashboardData {
  system: SystemMetrics;
  services: ServiceStatus[];
  api_requests_24h: number | null;
  api_errors_24h: number | null;
  documents_generated: number | null;
  cache_hit_rate: number | null;
  avg_response_time_ms: number | null;
  p95_latency_ms: number | null;
  p99_latency_ms: number | null;
  cache_status: string | null;
  cache_memory_used_mb: number | null;
  db_status: string | null;
  db_connections: number | null;
  db_query_avg_ms: number | null;
  service_fleet_total: number;
  running_containers: number;
  total_containers: number;
  capability_count: number;
  category_count: number;
  kloud_nodes: number;
}

interface ErrorItem {
  error_id: string;
  timestamp: string;
  line_number: number;
  function_name: string;
  error_type: string;
  error_message: string;
}

interface ErrorSummary {
  total_errors: number;
  error_types: Record<string, number>;
  most_common_function: string;
}

function normalizeErrorItems(payload: unknown): ErrorItem[] {
  if (!payload || typeof payload !== 'object') {
    return [];
  }

  const source = payload as Record<string, unknown>;
  const rawItems =
    (Array.isArray(source.errors) && source.errors) ||
    (Array.isArray(source.alerts) && source.alerts) ||
    (Array.isArray(source.recent_errors) && source.recent_errors) ||
    [];

  return rawItems.map((item, idx) => {
    const entry = (item ?? {}) as Record<string, unknown>;
    return {
      error_id: String(entry.error_id ?? entry.id ?? `ERR-${idx + 1}`),
      timestamp: String(entry.timestamp ?? entry.time ?? new Date().toISOString()),
      line_number: Number(entry.line_number ?? entry.line ?? 0),
      function_name: String(entry.function_name ?? entry.function ?? 'unknown'),
      error_type: String(entry.error_type ?? entry.type ?? 'unknown'),
      error_message: String(entry.error_message ?? entry.message ?? entry.error ?? 'Unknown error'),
    };
  });
}

// Use relative paths for security - proxied through Next.js API routes
const API_BASE = '';

function normalizeServiceName(value?: string | null) {
  return (value ?? '').toLowerCase().trim();
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}

function toNullableNumber(value: unknown): number | null {
  return isFiniteNumber(value) ? value : null;
}

function clampPercent(value: number | null | undefined) {
  if (!isFiniteNumber(value)) return 0;
  return Math.max(0, Math.min(100, value));
}

function formatCount(value: number | null | undefined) {
  return isFiniteNumber(value) ? value.toLocaleString() : 'Unavailable';
}

function formatPercent(value: number | null | undefined, digits = 1) {
  return isFiniteNumber(value) ? `${value.toFixed(digits)}%` : 'Unavailable';
}

function formatLatency(value: number | null | undefined) {
  return isFiniteNumber(value) ? `${Math.round(value)}ms` : 'Unavailable';
}

function formatMegabytes(value: number | null | undefined) {
  return isFiniteNumber(value) ? `${Math.round(value)}MB` : 'Unavailable';
}

async function probeServiceHealth(service: DiscoveryService) {
  const healthTarget = service.health || service.url;
  if (!healthTarget) {
    return { status: 'degraded' as const, latency: undefined };
  }

  const target = healthTarget.startsWith('http') ? healthTarget : `${API_BASE}${healthTarget}`;
  const started = performance.now();

  try {
    const response = await fetch(target, { cache: 'no-store' });
    const latency = Math.round(performance.now() - started);

    if (response.ok) {
      return { status: 'online' as const, latency };
    }

    return {
      status: response.status >= 500 ? 'offline' as const : 'degraded' as const,
      latency,
    };
  } catch {
    return { status: 'offline' as const, latency: undefined };
  }
}

function isRunningContainer(container: DockerContainerInfo) {
  const statusText = `${container.state ?? container.State ?? container.status ?? container.Status ?? ''}`.toLowerCase();

  if (typeof container.healthy === 'boolean') {
    return container.healthy || statusText.includes('running') || statusText.includes('up');
  }

  if (statusText.includes('exited') || statusText.includes('stopped') || statusText.includes('dead') || statusText.includes('unhealthy')) {
    return false;
  }

  return statusText.includes('running') || statusText.includes('up') || statusText.includes('healthy');
}

function findMatchingContainer(service: DiscoveryService, containers: DockerContainerInfo[]) {
  const candidates = [service.id, service.name, service.url]
    .map((value) => normalizeServiceName(value))
    .filter(Boolean);

  return containers.find((container) => {
    const label = [
      container.name,
      container.container_name,
      Array.isArray(container.Names) ? container.Names.join(' ') : container.Names,
      container.state,
      container.status,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();

    return candidates.some((candidate) => {
      if (!candidate) return false;
      if (label.includes(candidate)) return true;
      if (label.includes(`clisonix-${candidate}`)) return true;
      if (candidate === 'main-api' && label.includes('clisonix-api')) return true;
      return false;
    });
  });
}

async function buildVisibleServices(
  services: DiscoveryService[],
  containers: DockerContainerInfo[],
  kloudReachable: boolean,
) {
  const priority = ['kloud-bridge', 'main-api', 'ocean-core', 'reporting', 'marketplace', 'api', 'asi', 'alba', 'albi', 'jona'];

  const mapped = await Promise.all(services.map(async (service, index): Promise<ServiceStatus> => {
    const id = String(service.id || service.name || `service-${index + 1}`);
    const matchedContainer = findMatchingContainer(service, containers);
    const running = matchedContainer ? isRunningContainer(matchedContainer) : false;
    const normalizedId = normalizeServiceName(id);
    const isKloudService = normalizedId.includes('kloud') || normalizedId.startsWith('node') || normalizeServiceName(service.category).includes('kloud');

    const healthProbe = await probeServiceHealth(service);

    let status: ServiceStatus['status'] = healthProbe.status;
    if (isKloudService && kloudReachable) {
      status = 'online';
    } else if (healthProbe.status === 'offline' && running) {
      status = 'degraded';
    } else if (healthProbe.status === 'offline' && matchedContainer && !running) {
      status = 'offline';
    }

    return {
      id,
      name: String(service.name || id),
      icon: getMicroserviceIcon(service.name || id),
      status,
      responseTime: healthProbe.latency,
      url: service.health || service.url || '/developers',
      category: service.category || 'service',
      stack: service.stack || 'clisonix',
      source: service.source || 'catalog',
      capabilities: Array.isArray(service.capabilities) ? service.capabilities.slice(0, 4) : [],
    };
  }));

  return mapped
    .sort((left, right) => {
      const statusRank = { online: 0, degraded: 1, offline: 2 };
      const leftPriority = priority.indexOf(normalizeServiceName(left.id));
      const rightPriority = priority.indexOf(normalizeServiceName(right.id));

      if (statusRank[left.status] !== statusRank[right.status]) {
        return statusRank[left.status] - statusRank[right.status];
      }

      if (leftPriority !== -1 || rightPriority !== -1) {
        return (leftPriority === -1 ? 99 : leftPriority) - (rightPriority === -1 ? 99 : rightPriority);
      }

      return left.name.localeCompare(right.name);
    })
    .slice(0, 18);
}

export default function UltraReportingDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [activeTab, setActiveTab] = useState<'overview' | 'services' | 'metrics' | 'exports'>('overview');
  const [exporting, setExporting] = useState(false);
  const [showErrorTracker, setShowErrorTracker] = useState(false);
  const [errors, setErrors] = useState<ErrorItem[]>([]);
  const [errorSummary, setErrorSummary] = useState<ErrorSummary | null>(null);
  const [loadingErrors, setLoadingErrors] = useState(false);
  const pollingHandleRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isFetchInFlightRef = useRef(false);

  const fetchData = useCallback(async () => {
    if (isFetchInFlightRef.current) {
      return false;
    }

    isFetchInFlightRef.current = true;
    try {
      const [healthRes, metricsRes, discoveryRes, containersRes, kloudRes] = await Promise.all([
        fetch(`${API_BASE}/api/proxy/health`).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE}/api/proxy/reporting-dashboard`).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE}/api/service-discovery`).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE}/api/proxy/docker-containers`).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE}/api/kloud-bridge/status`).then(r => r.json()).catch(() => null),
      ]);

      const mainHealth = healthRes?.data || healthRes || {};
      const reportingData = metricsRes?.data || metricsRes || {};
      const reportingSystem = reportingData?.system || {};
      const discoveryData = discoveryRes?.data || discoveryRes || {};
      const discoveryIsDegraded = Boolean(discoveryRes?.meta?.degraded);
      // Always use catalog services even when live registry is degraded
      const discoveredServices = Array.isArray(discoveryData?.services)
        ? (discoveryData.services as DiscoveryService[])
        : [];
      const discoverySummary = discoveryData?.summary || {};
      const containers = Array.isArray(containersRes?.containers)
        ? (containersRes.containers as DockerContainerInfo[])
        : [];
      const kloudReachable = Boolean(kloudRes?.upstream?.reachable);
      const services = await buildVisibleServices(discoveredServices, containers, kloudReachable);

      const capabilityCount = typeof discoverySummary?.capabilities === 'number'
        ? discoverySummary.capabilities
        : new Set(discoveredServices.flatMap((service) => Array.isArray(service.capabilities) ? service.capabilities : [])).size;

      const categoryCount = typeof discoverySummary?.categories === 'number'
        ? discoverySummary.categories
        : new Set(discoveredServices.map((service) => service.category || 'unknown')).size;

      const serviceFleetTotal = typeof discoverySummary?.totalServices === 'number'
        ? discoverySummary.totalServices
        : Number(discoveryData?.count || discoveredServices.length || services.length);

      const runningContainers = typeof containersRes?.running === 'number'
        ? containersRes.running
        : containers.filter(isRunningContainer).length;

      const totalContainers = typeof containersRes?.total === 'number'
        ? containersRes.total
        : containers.length;

      const kloudNodes = typeof discoverySummary?.kloudNodes === 'number'
        ? discoverySummary.kloudNodes
        : discoveredServices.filter((service) => {
            const normalized = normalizeServiceName(service.id || service.name);
            return normalized.startsWith('node') || normalizeServiceName(service.category).includes('kloud');
          }).length;

      setData({
        system: {
          cpu_percent: toNullableNumber(
            mainHealth?.system?.cpu_percent
            ?? reportingData?.system_cpu_percent
            ?? reportingSystem?.cpu_percent,
          ),
          memory_percent: toNullableNumber(
            mainHealth?.system?.memory_percent
            ?? reportingData?.system_memory_percent
            ?? reportingSystem?.memory_percent,
          ),
          disk_percent: toNullableNumber(
            mainHealth?.system?.disk_percent
            ?? reportingData?.system_disk_percent
            ?? reportingSystem?.disk_percent,
          ),
          uptime_seconds: toNullableNumber(
            mainHealth?.system?.uptime_seconds
            ?? reportingData?.system_uptime_seconds
            ?? reportingSystem?.uptime_seconds,
          ),
        },
        services,
        api_requests_24h: toNullableNumber(reportingData?.api_requests_24h),
        api_errors_24h: toNullableNumber(reportingData?.api_errors_24h),
        documents_generated: toNullableNumber(reportingData?.documents_generated_24h ?? reportingData?.documents_generated),
        cache_hit_rate: toNullableNumber(reportingData?.cache_hit_rate_percent ?? reportingData?.cache_hit_rate),
        avg_response_time_ms: toNullableNumber(reportingData?.avg_response_time_ms ?? reportingData?.avg_response_ms),
        p95_latency_ms: toNullableNumber(reportingData?.api_latency_p95_ms ?? reportingData?.p95_latency_ms),
        p99_latency_ms: toNullableNumber(reportingData?.api_latency_p99_ms ?? reportingData?.p99_latency_ms),
        cache_status: typeof reportingData?.cache_status === 'string' ? reportingData.cache_status : null,
        cache_memory_used_mb: toNullableNumber(reportingData?.cache_memory_used_mb),
        db_status: typeof reportingData?.db_status === 'string'
          ? reportingData.db_status
          : typeof mainHealth?.database?.status === 'string'
            ? mainHealth.database.status
            : null,
        db_connections: toNullableNumber(reportingData?.db_connections),
        db_query_avg_ms: toNullableNumber(reportingData?.db_query_avg_ms ?? mainHealth?.database?.response_time_ms),
        service_fleet_total: serviceFleetTotal || services.length,
        running_containers: toNullableNumber(reportingData?.running_containers) ?? runningContainers,
        total_containers:
          toNullableNumber(reportingData?.total_containers) ??
          totalContainers ??
          serviceFleetTotal ??
          services.length,
        capability_count: capabilityCount,
        category_count: categoryCount,
        kloud_nodes: kloudNodes,
      });

      setLastUpdate(new Date());
      setLoading(false);
      setError(
        discoveryIsDegraded && discoveredServices.length === 0
          ? 'Live service discovery is unavailable. No catalog fallback is being shown.'
          : null
      );
      return true;
    } catch (err) {
      setError('Failed to fetch metrics');
      setLoading(false);
      return false;
    } finally {
      isFetchInFlightRef.current = false;
    }
  }, []);

  const fetchErrors = useCallback(async () => {
    setLoadingErrors(true);
    try {
      const [errorsRes, summaryRes] = await Promise.all([
        fetch('/api/proxy/reporting-errors').then(r => r.json()).catch(() => ({ errors: [] })),
        fetch('/api/proxy/reporting-error-summary').then(r => r.json()).catch(() => ({}))
      ]);
      const normalizedErrors = normalizeErrorItems(errorsRes);
      const safeSummary = (summaryRes && typeof summaryRes === 'object' ? summaryRes : {}) as Record<string, unknown>;
      const summaryTotal = Number(safeSummary.total_errors ?? 0);
      const summaryTypes = (safeSummary.error_types && typeof safeSummary.error_types === 'object')
        ? (safeSummary.error_types as Record<string, number>)
        : {};

      setErrors(normalizedErrors);
      setErrorSummary({
        total_errors: Number.isFinite(summaryTotal) ? summaryTotal : normalizedErrors.length,
        error_types: summaryTypes,
        most_common_function: String(safeSummary.most_common_function ?? 'unknown'),
      });
    } catch (err) {
      console.error('Failed to fetch errors:', err);
    }
    setLoadingErrors(false);
  }, []);

  const summaryTotalErrors = isFiniteNumber(errorSummary?.total_errors) ? errorSummary.total_errors : 0;
  const effectiveErrorCount = Math.max(errors.length, summaryTotalErrors);

  useEffect(() => {
    let disposed = false;

    const clearPollingHandle = () => {
      if (pollingHandleRef.current) {
        clearTimeout(pollingHandleRef.current);
        pollingHandleRef.current = null;
      }
    };

    const schedulePoll = (delayMs: number) => {
      clearPollingHandle();
      if (disposed) {
        return;
      }
      pollingHandleRef.current = setTimeout(runPoll, delayMs);
    };

    const runPoll = async () => {
      if (disposed) {
        return;
      }
      if (typeof document !== 'undefined' && document.hidden) {
        schedulePoll(30000);
        return;
      }

      const ok = await fetchData();
      schedulePoll(ok ? 15000 : 60000);
    };

    const onVisibilityChange = () => {
      if (typeof document !== 'undefined' && !document.hidden) {
        void runPoll();
      }
    };

    void runPoll();
    document.addEventListener('visibilitychange', onVisibilityChange);

    return () => {
      disposed = true;
      clearPollingHandle();
      document.removeEventListener('visibilitychange', onVisibilityChange);
    };
  }, [fetchData]);

  const handleExport = async (format: 'xlsx' | 'pptx' | 'pdf') => {
    setExporting(true);
    try {
      let endpoint = '';
      let filename = `clisonix-report-${new Date().toISOString().split('T')[0]}`;

      if (format === 'xlsx') {
        endpoint = '/api/proxy/reporting-export-excel';
        filename += '.xlsx';
      } else if (format === 'pptx') {
        endpoint = '/api/proxy/reporting-export-pptx';
        filename += '.pptx';
      } else {
        console.error('PDF export not yet implemented');
        return;
      }

      const response = await fetch(endpoint, {
        method: 'GET',
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        console.error('Export failed:', response.status);
      }
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setExporting(false);
    }
  };

  const formatUptime = (seconds: number | null) => {
    if (!isFiniteNumber(seconds)) return 'Unavailable';
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${mins}m`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'offline': return 'bg-red-500';
      case 'degraded': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getMetricColor = (value: number | null, thresholds: { warning: number; critical: number }) => {
    if (!isFiniteNumber(value)) return 'text-gray-400';
    if (value >= thresholds.critical) return 'text-red-400';
    if (value >= thresholds.warning) return 'text-yellow-400';
    return 'text-green-400';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading ULTRA Reporting Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <header className="border-b border-gray-700/50 bg-gray-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg shadow-violet-500/25">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">ULTRA Reporting</h1>
                <p className="text-sm text-gray-400">Command Center - Real-time Analytics</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right text-sm">
                <p className="text-gray-400">Last Update</p>
                <p className="text-white font-mono">{lastUpdate.toLocaleTimeString()}</p>
              </div>
              <button
                onClick={fetchData}
                className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-600 transition-colors"
                title="Refresh"
              >
                <svg className="w-5 h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
              <Link
                href="/modules"
                className="px-4 py-2 text-sm text-gray-300 hover:text-white border border-gray-600 hover:border-gray-500 rounded-lg transition-colors"
              >
                &#8592; Back
              </Link>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 mt-4">
            {(['overview', 'services', 'metrics', 'exports'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                  activeTab === tab
                    ? 'bg-gray-800 text-white border-t border-l border-r border-gray-600'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400">
            {error}
          </div>
        )}

        {/* Overview Tab */}
        {activeTab === 'overview' && data && (
          <div className="space-y-6">
            {/* System Health Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-gray-400 text-sm">CPU Usage</span>
                  <div className="w-8 h-8 rounded-lg bg-violet-500/20 flex items-center justify-center">
                    <svg className="w-4 h-4 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                    </svg>
                  </div>
                </div>
                <p className={`text-3xl font-bold ${getMetricColor(data.system.cpu_percent, { warning: 70, critical: 90 })}`}>
                  {formatPercent(data.system.cpu_percent)}
                </p>
                <div className="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-violet-500 transition-all duration-500"
                    style={{ width: `${clampPercent(data.system.cpu_percent)}%` }}
                  ></div>
                </div>
              </div>

              <div className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-gray-400 text-sm">Memory Usage</span>
                  <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center">
                    <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                </div>
                <p className={`text-3xl font-bold ${getMetricColor(data.system.memory_percent, { warning: 70, critical: 85 })}`}>
                  {formatPercent(data.system.memory_percent)}
                </p>
                <div className="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-purple-500 transition-all duration-500"
                    style={{ width: `${clampPercent(data.system.memory_percent)}%` }}
                  ></div>
                </div>
              </div>

              <div className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-gray-400 text-sm">Disk Usage</span>
                  <div className="w-8 h-8 rounded-lg bg-orange-500/20 flex items-center justify-center">
                    <svg className="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                    </svg>
                  </div>
                </div>
                <p className={`text-3xl font-bold ${getMetricColor(data.system.disk_percent, { warning: 80, critical: 90 })}`}>
                  {formatPercent(data.system.disk_percent)}
                </p>
                <div className="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-orange-500 transition-all duration-500"
                    style={{ width: `${clampPercent(data.system.disk_percent)}%` }}
                  ></div>
                </div>
              </div>

              <div className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-gray-400 text-sm">System Uptime</span>
                  <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center">
                    <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <p className="text-3xl font-bold text-green-400">
                  {formatUptime(data.system.uptime_seconds)}
                </p>
                <p className="mt-2 text-xs text-gray-500">Since last restart</p>
              </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-6 rounded-xl bg-gradient-to-br from-violet-600/20 to-slate-800/20 border border-violet-500/30">
                <p className="text-violet-300 text-sm mb-2">API Requests (24h)</p>
                <p className="text-4xl font-bold text-white">{formatCount(data.api_requests_24h)}</p>
              </div>
              <div className="p-6 rounded-xl bg-gradient-to-br from-red-600/20 to-red-800/20 border border-red-500/30 cursor-pointer hover:border-red-400/60 transition-all" onClick={() => { setShowErrorTracker(true); fetchErrors(); }}>
                <p className="text-red-300 text-sm mb-2">Errors (24h)</p>
                <p className="text-4xl font-bold text-white hover:text-red-300 transition-colors">{formatCount(data.api_errors_24h)}</p>
                <p className="text-xs text-red-400 mt-1">
                  {isFiniteNumber(data.api_errors_24h) && isFiniteNumber(data.api_requests_24h) && data.api_requests_24h > 0
                    ? `${((data.api_errors_24h / data.api_requests_24h) * 100).toFixed(2)}% error rate`
                    : 'Error rate unavailable'}
                </p>
                <p className="text-xs text-red-500 mt-2 opacity-75">Click to view error tracker →</p>
              </div>
              <div className="p-6 rounded-xl bg-gradient-to-br from-green-600/20 to-green-800/20 border border-green-500/30">
                <p className="text-green-300 text-sm mb-2">Documents Generated</p>
                <p className="text-4xl font-bold text-white">{formatCount(data.documents_generated)}</p>
              </div>
              <div className="p-6 rounded-xl bg-gradient-to-br from-purple-600/20 to-purple-800/20 border border-purple-500/30">
                <p className="text-purple-300 text-sm mb-2">Cache Hit Rate</p>
                <p className="text-4xl font-bold text-white">{formatPercent(data.cache_hit_rate)}</p>
              </div>
            </div>

            {/* Platform Fleet Snapshot */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-6 rounded-xl bg-gradient-to-br from-cyan-600/20 to-slate-800/20 border border-cyan-500/30">
                <p className="text-cyan-300 text-sm mb-2">Service Fleet</p>
                <p className="text-4xl font-bold text-white">{data.service_fleet_total}</p>
                <p className="text-xs text-cyan-100/80 mt-1">Compose + discovery-backed service surface</p>
              </div>
              <div className="p-6 rounded-xl bg-gradient-to-br from-emerald-600/20 to-slate-800/20 border border-emerald-500/30">
                <p className="text-emerald-300 text-sm mb-2">Running Containers</p>
                <p className="text-4xl font-bold text-white">{data.running_containers}<span className="text-lg text-gray-400">/{data.total_containers}</span></p>
                <p className="text-xs text-emerald-100/80 mt-1">Verified runtime footprint</p>
              </div>
              <div className="p-6 rounded-xl bg-gradient-to-br from-fuchsia-600/20 to-slate-800/20 border border-fuchsia-500/30">
                <p className="text-fuchsia-300 text-sm mb-2">Capability Surface</p>
                <p className="text-4xl font-bold text-white">{data.capability_count}</p>
                <p className="text-xs text-fuchsia-100/80 mt-1">Unique capabilities flowing to the frontend</p>
              </div>
              <div className="p-6 rounded-xl bg-gradient-to-br from-amber-600/20 to-slate-800/20 border border-amber-500/30">
                <p className="text-amber-300 text-sm mb-2">Kloud Layer</p>
                <p className="text-4xl font-bold text-white">{data.kloud_nodes}</p>
                <p className="text-xs text-amber-100/80 mt-1">Visible Kloud nodes across {data.category_count} service categories</p>
              </div>
            </div>

            {/* Services Overview */}
            <div className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50">
              <div className="flex flex-wrap items-end justify-between gap-3 mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-white">Service Fleet — Clisonix + Kloud</h3>
                  <p className="text-sm text-gray-400">A broader live-facing view of the backend stack, with service categories, icons, and verified runtime posture.</p>
                </div>
                <div className="text-right text-xs text-gray-400">
                  <p>{data.service_fleet_total} discovered services</p>
                  <p>{data.running_containers} running containers</p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                {data.services.slice(0, 12).map(service => (
                  <div key={service.id} className="p-4 rounded-lg bg-gray-900/50 border border-gray-700/30">
                    <div className="flex items-center justify-between gap-2 mb-3">
                      <div className="flex items-center gap-2 min-w-0">
                        <Image src={service.icon} alt={service.name} width={16} height={16} />
                        <div className={`w-2 h-2 rounded-full ${getStatusColor(service.status)} animate-pulse`}></div>
                        <span className="text-xs text-gray-400 uppercase tracking-wide truncate">{service.category || 'service'}</span>
                      </div>
                      <span className="text-[10px] uppercase tracking-wide text-gray-500">{service.stack || 'clisonix'}</span>
                    </div>
                    <p className="text-sm font-medium text-white truncate">{service.name}</p>
                    <p className="text-xs text-gray-500 mt-1 capitalize">{service.status}</p>
                    {service.capabilities && service.capabilities.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-1">
                        {service.capabilities.slice(0, 2).map((capability) => (
                          <span key={`${service.id}-${capability}`} className="rounded-full border border-gray-700 bg-gray-800 px-2 py-0.5 text-[10px] text-gray-300">
                            {capability}
                          </span>
                        ))}
                      </div>
                    )}
                    <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                      <span>{service.responseTime ? `${service.responseTime}ms` : (service.source || 'catalog')}</span>
                      <span className={service.status === 'online' ? 'text-green-400' : service.status === 'offline' ? 'text-red-400' : 'text-yellow-400'}>
                        {service.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* ASI Trinity Architecture */}
            <div className="p-6 rounded-xl bg-gradient-to-br from-gray-800/70 to-gray-900/70 border border-violet-500/30">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="w-3 h-3 bg-violet-500 rounded-full animate-pulse"></span>
                ASI Trinity Architecture - Real Metrics
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Analytical Intelligence */}
                <div className="p-4 rounded-lg bg-blue-800/10 border border-blue-800/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-blue-700 font-medium">📊 Analytical Intelligence</span>
                    <span className="w-2 h-2 bg-blue-800 rounded-full animate-pulse"></span>
                  </div>
                  <p className="text-xs text-gray-400 mb-3">CPU usage, memory, network latency from actual system monitoring</p>
                  <a
                    href="/api/asi/alba/metrics"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-700 hover:text-blue-600 flex items-center gap-1"
                  >
                    → Real metrics endpoint
                  </a>
                </div>

                {/* Creative Intelligence */}
                <div className="p-4 rounded-lg bg-violet-500/10 border border-violet-500/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-violet-400 font-medium">🧠 Creative Intelligence</span>
                    <span className="w-2 h-2 bg-violet-500 rounded-full animate-pulse"></span>
                  </div>
                  <p className="text-xs text-gray-400 mb-3">Neural patterns, processing efficiency, real-time metrics</p>
                  <a
                    href="/api/asi/albi/metrics"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-violet-400 hover:text-violet-300 flex items-center gap-1"
                  >
                    → Real metrics endpoint
                  </a>
                </div>

                {/* Coordinator Intelligence */}
                <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-purple-400 font-medium">🛡️ Coordinator Intelligence</span>
                    <span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></span>
                  </div>
                  <p className="text-xs text-gray-400 mb-3">Request throughput, uptime, coordination efficiency from live system</p>
                  <a
                    href="/api/asi/jona/metrics"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1"
                  >
                    → Real metrics endpoint
                  </a>
                </div>
              </div>

              {/* ASI Status Links */}
              <div className="mt-4 pt-4 border-t border-gray-700/50 flex gap-4">
                <a
                  href="/api/asi/status"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-gray-700/50 hover:bg-gray-600/50 text-violet-400 text-sm rounded-lg transition-colors"
                >
                  View ASI Status
                </a>
                <a
                  href="/api/asi/health"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-gray-700/50 hover:bg-gray-600/50 text-green-400 text-sm rounded-lg transition-colors"
                >
                  View ASI Health
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Services Tab */}
        {activeTab === 'services' && data && (
          <div className="space-y-4">
            <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
              <div>
                <h2 className="text-xl font-bold text-white">Service Health Monitor</h2>
                <p className="text-sm text-gray-400">Live-facing fleet view for the broader Clisonix backend, including the Kloud bridge layer.</p>
              </div>
              <div className="text-right text-sm text-gray-400">
                <p>{data.service_fleet_total} services discovered</p>
                <p>{data.running_containers}/{data.total_containers} containers running • {data.kloud_nodes} Kloud nodes</p>
              </div>
            </div>

            <div className="grid gap-4 xl:grid-cols-2">
              {data.services.map(service => (
                <div key={service.id} className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                  <div className="flex items-center gap-4 min-w-0">
                    <Image src={service.icon} alt={service.name} width={24} height={24} />
                    <div className={`w-4 h-4 rounded-full ${getStatusColor(service.status)}`}></div>
                    <div className="min-w-0">
                      <h3 className="text-lg font-medium text-white truncate">{service.name}</h3>
                      <p className="text-sm text-gray-400 capitalize">{service.category || 'service'} • {service.stack || 'clisonix'} • {service.source || 'catalog'}</p>
                      {service.capabilities && service.capabilities.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {service.capabilities.slice(0, 3).map((capability) => (
                            <span key={`${service.id}-${capability}`} className="rounded-full border border-gray-700 bg-gray-900/60 px-2 py-0.5 text-[10px] text-gray-300">
                              {capability}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-sm text-gray-400">Response Time</p>
                      <p className="text-lg font-mono text-white">{formatLatency(service.responseTime)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-400">Status</p>
                      <p className={`text-lg font-medium ${
                        service.status === 'online' ? 'text-green-400' :
                        service.status === 'offline' ? 'text-red-400' : 'text-yellow-400'
                      }`}>
                        {service.status.toUpperCase()}
                      </p>
                    </div>
                    <a
                      href={service.url || '/developers'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded-lg transition-colors"
                    >
                      Open
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Metrics Tab */}
        {activeTab === 'metrics' && data && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-white mb-6">Detailed Metrics</h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* API Metrics */}
              <div className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50">
                <h3 className="text-lg font-semibold text-white mb-4">API Performance</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Total Requests (24h)</span>
                    <span className="text-white font-mono">{formatCount(data.api_requests_24h)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Error Rate</span>
                    <span className="text-green-400 font-mono">
                      {isFiniteNumber(data.api_errors_24h) && isFiniteNumber(data.api_requests_24h) && data.api_requests_24h > 0
                        ? `${((data.api_errors_24h / data.api_requests_24h) * 100).toFixed(3)}%`
                        : 'Unavailable'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Avg Response Time</span>
                    <span className="text-white font-mono">{formatLatency(data.avg_response_time_ms)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">P95 Latency</span>
                    <span className="text-white font-mono">{formatLatency(data.p95_latency_ms)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">P99 Latency</span>
                    <span className="text-white font-mono">{formatLatency(data.p99_latency_ms)}</span>
                  </div>
                </div>
              </div>

              {/* System Metrics */}
              <div className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50">
                <h3 className="text-lg font-semibold text-white mb-4">System Resources</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-gray-400">CPU</span>
                      <span className="text-white font-mono">{formatPercent(data.system.cpu_percent)}</span>
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-violet-500" style={{ width: `${clampPercent(data.system.cpu_percent)}%` }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-gray-400">Memory</span>
                      <span className="text-white font-mono">{formatPercent(data.system.memory_percent)}</span>
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-purple-500" style={{ width: `${clampPercent(data.system.memory_percent)}%` }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-gray-400">Disk</span>
                      <span className="text-white font-mono">{formatPercent(data.system.disk_percent)}</span>
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-orange-500" style={{ width: `${clampPercent(data.system.disk_percent)}%` }}></div>
                    </div>
                  </div>
                  <div className="flex justify-between items-center pt-2">
                    <span className="text-gray-400">Uptime</span>
                    <span className="text-green-400 font-mono">{formatUptime(data.system.uptime_seconds)}</span>
                  </div>
                </div>
              </div>

              {/* Cache Metrics */}
              <div className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50">
                <h3 className="text-lg font-semibold text-white mb-4">Cache Performance</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Hit Rate</span>
                    <span className="text-green-400 font-mono">{formatPercent(data.cache_hit_rate)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Cache Status</span>
                    <span className={data.cache_status === 'connected' ? 'text-green-400' : 'text-gray-300'}>{data.cache_status || 'Unavailable'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Memory Used</span>
                    <span className="text-white font-mono">{formatMegabytes(data.cache_memory_used_mb)}</span>
                  </div>
                </div>
              </div>

              {/* Database Metrics */}
              <div className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50">
                <h3 className="text-lg font-semibold text-white mb-4">Database Health</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Database Status</span>
                    <span
                      className={
                        data.db_status === 'healthy'
                          ? 'text-green-400'
                          : data.db_status === 'not_configured'
                            ? 'text-amber-400'
                            : 'text-gray-300'
                      }
                    >
                      {data.db_status || 'Unavailable'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Active Connections</span>
                    <span className="text-white font-mono">
                      {data.db_status === 'not_configured' ? 'N/A' : formatCount(data.db_connections)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Query Avg Time</span>
                    <span className="text-white font-mono">
                      {data.db_status === 'not_configured' ? 'N/A' : formatLatency(data.db_query_avg_ms)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Exports Tab */}
        {activeTab === 'exports' && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-white mb-6">Export Reports</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Excel Export */}
              <div className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50 hover:border-green-500/50 transition-colors">
                <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-green-500/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-white text-center mb-2">Excel Report</h3>
                <p className="text-sm text-gray-400 text-center mb-4">
                  Complete metrics with charts, tables, and formulas
                </p>
                <button
                  onClick={() => handleExport('xlsx')}
                  disabled={exporting}
                  className="w-full py-3 bg-green-600 hover:bg-green-500 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors"
                >
                  {exporting ? 'Generating...' : 'Download .xlsx'}
                </button>
              </div>

              {/* PowerPoint Export */}
              <div className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50 hover:border-orange-500/50 transition-colors">
                <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-orange-500/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-white text-center mb-2">PowerPoint</h3>
                <p className="text-sm text-gray-400 text-center mb-4">
                  Executive presentation with visualizations
                </p>
                <button
                  onClick={() => handleExport('pptx')}
                  disabled={exporting}
                  className="w-full py-3 bg-orange-600 hover:bg-orange-500 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors"
                >
                  {exporting ? 'Generating...' : 'Download .pptx'}
                </button>
              </div>

              {/* PDF Export */}
              <div className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50 hover:border-red-500/50 transition-colors">
                <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-red-500/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-white text-center mb-2">PDF Report</h3>
                <p className="text-sm text-gray-400 text-center mb-4">
                  Print-ready comprehensive report
                </p>
                <button
                  onClick={() => handleExport('pdf')}
                  disabled={exporting}
                  className="w-full py-3 bg-red-600 hover:bg-red-500 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors"
                >
                  {exporting ? 'Generating...' : 'Download .pdf'}
                </button>
              </div>
            </div>

            {/* Quick Links */}
            <div className="p-6 rounded-xl bg-gray-800/50 border border-gray-700/50">
              <h3 className="text-lg font-semibold text-white mb-4">API Endpoints</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <a
                  href={`${API_BASE}/api/reporting/dashboard`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-4 bg-gray-900/50 rounded-lg hover:bg-gray-700/50 transition-colors"
                >
                  <code className="text-violet-400 text-sm">GET /api/reporting/dashboard</code>
                  <p className="text-xs text-gray-500 mt-1">Live dashboard metrics</p>
                </a>
                <a
                  href={`${API_BASE}/api/reporting/export?format=xlsx`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-4 bg-gray-900/50 rounded-lg hover:bg-gray-700/50 transition-colors"
                >
                  <code className="text-green-400 text-sm">POST /api/reporting/export</code>
                  <p className="text-xs text-gray-500 mt-1">Generate reports</p>
                </a>
                <a
                  href={`${API_BASE}/api/reporting/metrics`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-4 bg-gray-900/50 rounded-lg hover:bg-gray-700/50 transition-colors"
                >
                  <code className="text-purple-400 text-sm">GET /api/reporting/metrics</code>
                  <p className="text-xs text-gray-500 mt-1">Raw metrics data</p>
                </a>
                <a
                  href={`${API_BASE}/api/reporting/alerts`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-4 bg-gray-900/50 rounded-lg hover:bg-gray-700/50 transition-colors"
                >
                  <code className="text-red-400 text-sm">GET /api/reporting/alerts</code>
                  <p className="text-xs text-gray-500 mt-1">Active alerts</p>
                </a>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-700/50 py-4 mt-8">
        <p className="text-center text-xs text-gray-500">
          ULTRA Reporting Command Center - Clisonix Cloud Platform - Real-time Analytics
        </p>
      </footer>

      {/* Error Tracker Modal */}
      {showErrorTracker && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-xl border border-red-500/30 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
            <div className="sticky top-0 bg-gray-900 border-b border-red-500/30 p-6 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-red-300">ERROR REFERENCE TRACKER</h2>
              <button
                onClick={() => setShowErrorTracker(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Error Summary */}
              {errorSummary && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-red-900/30 rounded-lg border border-red-500/30">
                    <p className="text-red-300 text-sm">Total Errors</p>
                    <p className="text-3xl font-bold text-white">{effectiveErrorCount}</p>
                  </div>
                  <div className="p-4 bg-red-900/30 rounded-lg border border-red-500/30">
                    <p className="text-red-300 text-sm">Error Types</p>
                    <p className="text-2xl font-bold text-white">{Object.keys(errorSummary.error_types || {}).length}</p>
                  </div>
                  <div className="p-4 bg-red-900/30 rounded-lg border border-red-500/30">
                    <p className="text-red-300 text-sm">Most Common Function</p>
                    <p className="text-sm font-bold text-white truncate">{errorSummary.most_common_function || 'N/A'}</p>
                  </div>
                </div>
              )}

              {/* Error List */}
              {loadingErrors ? (
                <div className="text-center py-8">
                  <p className="text-gray-400">Loading errors...</p>
                </div>
              ) : effectiveErrorCount === 0 ? (
                <div className="text-center py-8">
                  <p className="text-green-400 text-lg">✓ No errors recorded</p>
                </div>
              ) : errors.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-yellow-300 text-lg">Error summary detected incidents, but detailed rows are unavailable.</p>
                </div>
              ) : (
                <div className="space-y-2 overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-red-500/30 text-left">
                        <th className="pb-3 px-3 text-red-300">Error ID</th>
                        <th className="pb-3 px-3 text-red-300">Timestamp</th>
                        <th className="pb-3 px-3 text-red-300">Line</th>
                        <th className="pb-3 px-3 text-red-300">Function</th>
                        <th className="pb-3 px-3 text-red-300">Type</th>
                        <th className="pb-3 px-3 text-red-300">Message</th>
                      </tr>
                    </thead>
                    <tbody>
                      {errors.map((err, idx) => (
                        <tr key={idx} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
                          <td className="py-3 px-3 font-bold text-violet-400">{err.error_id}</td>
                          <td className="py-3 px-3 text-gray-400 text-xs">{new Date(err.timestamp).toLocaleTimeString()}</td>
                          <td className="py-3 px-3 text-yellow-400 font-mono">{err.line_number}</td>
                          <td className="py-3 px-3 text-violet-400">{err.function_name}</td>
                          <td className="py-3 px-3 text-orange-400">{err.error_type}</td>
                          <td className="py-3 px-3 text-red-400 truncate max-w-xs">{err.error_message}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Error Type Breakdown */}
              {errorSummary?.error_types && Object.keys(errorSummary.error_types).length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-bold text-red-300 mb-3">Error Type Breakdown</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {Object.entries(errorSummary.error_types).map(([type, count]) => (
                      <div key={type} className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                        <p className="text-gray-400 text-sm">{type}</p>
                        <p className="text-2xl font-bold text-red-400">{count as number}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}







