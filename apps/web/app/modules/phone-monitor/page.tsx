'use client';

import { useState, useEffect, useCallback } from 'react';
import { Smartphone, Radio, Shield, Activity, RefreshCw, Clock, CheckCircle, AlertCircle, Brain, Wifi, Lock, Database } from 'lucide-react';

// Endpoint Configuration - REAL APIs ONLY
interface EndpointConfig {
  url: string;
  method: 'GET' | 'POST';
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  category: 'monitoring' | 'neural' | 'security' | 'system';
}

interface ResponseState {
  data: unknown;
  loading: boolean;
  error: string | null;
  responseTime: number;
  status: number | null;
  timestamp: string | null;
}

// REAL API ENDPOINTS - No fake data, no Math.random()
const ENDPOINTS: EndpointConfig[] = [
  {
    url: '/api/asi-status',
    method: 'GET',
    name: 'ASI Phone Status',
    description: 'Neural phone monitoring status from ASI Trinity',
    icon: Smartphone,
    category: 'monitoring'
  },
  {
    url: '/api/asi/status',
    method: 'GET',
    name: 'ASI Trinity Status',
    description: 'Complete ASI system status with ALBA, ALBI, JONA',
    icon: Brain,
    category: 'neural'
  },
  {
    url: '/api/asi/health',
    method: 'GET',
    name: 'ASI Health Check',
    description: 'Health status of all ASI components',
    icon: Activity,
    category: 'system'
  },
  {
    url: '/api/asi/alba/metrics',
    method: 'GET',
    name: 'ALBA Neural Metrics',
    description: 'Advanced neural processing metrics from ALBA',
    icon: Radio,
    category: 'neural'
  },
  {
    url: '/api/asi/albi/metrics',
    method: 'GET',
    name: 'ALBI Signal Metrics',
    description: 'Signal processing and biofeedback data from ALBI',
    icon: Wifi,
    category: 'neural'
  },
  {
    url: '/api/system/health',
    method: 'GET',
    name: 'System Health',
    description: 'Unified system health status',
    icon: Shield,
    category: 'system'
  },
  {
    url: '/api/asi/jona/metrics',
    method: 'GET',
    name: 'JONA Analytics',
    description: 'AI-powered analytics and insights from JONA',
    icon: Database,
    category: 'neural'
  },
  {
    url: '/api/security/status',
    method: 'GET',
    name: 'Security Status',
    description: 'Security monitoring and threat detection status',
    icon: Lock,
    category: 'security'
  }
];

export default function PhoneMonitorPage() {
  const [responses, setResponses] = useState<Record<string, ResponseState>>({});
  const [selectedEndpoint, setSelectedEndpoint] = useState<string>(ENDPOINTS[0].url);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(5000);

  // Fetch single endpoint with timing - REAL DATA ONLY
  const fetchEndpoint = useCallback(async (endpoint: EndpointConfig) => {
    const startTime = performance.now();

    setResponses(prev => ({
      ...prev,
      [endpoint.url]: {
        ...prev[endpoint.url],
        loading: true,
        error: null
      }
    }));

    try {
      const response = await fetch(endpoint.url, {
        method: endpoint.method,
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store'
      });

      const endTime = performance.now();
      const responseTime = Math.round(endTime - startTime);

      let data;
      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      setResponses(prev => ({
        ...prev,
        [endpoint.url]: {
          data,
          loading: false,
          error: null,
          responseTime,
          status: response.status,
          timestamp: new Date().toISOString()
        }
      }));
    } catch (error) {
      const endTime = performance.now();
      setResponses(prev => ({
        ...prev,
        [endpoint.url]: {
          data: null,
          loading: false,
          error: error instanceof Error ? error.message : 'Unknown error',
          responseTime: Math.round(endTime - startTime),
          status: null,
          timestamp: new Date().toISOString()
        }
      }));
    }
  }, []);

  // Fetch all endpoints
  const fetchAllEndpoints = useCallback(() => {
    ENDPOINTS.forEach(endpoint => fetchEndpoint(endpoint));
  }, [fetchEndpoint]);

  // Initial load
  useEffect(() => {
    fetchAllEndpoints();
  }, [fetchAllEndpoints]);

  // Auto refresh
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchAllEndpoints, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, fetchAllEndpoints]);

  const getStatusColor = (status: number | null) => {
    if (status === null) return 'bg-gray-500';
    if (status >= 200 && status < 300) return 'bg-green-500';
    if (status >= 400 && status < 500) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getStatusText = (status: number | null) => {
    if (status === null) return 'N/A';
    if (status >= 200 && status < 300) return 'Success';
    if (status >= 400 && status < 500) return 'Client Error';
    return 'Server Error';
  };

  const selectedResponse = responses[selectedEndpoint];
  const selectedConfig = ENDPOINTS.find(e => e.url === selectedEndpoint);

  const categorizedEndpoints = {
    monitoring: ENDPOINTS.filter(e => e.category === 'monitoring'),
    neural: ENDPOINTS.filter(e => e.category === 'neural'),
    security: ENDPOINTS.filter(e => e.category === 'security'),
    system: ENDPOINTS.filter(e => e.category === 'system')
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 text-white p-4 md:p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Smartphone className="w-8 h-8 text-blue-700" />
          <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-blue-700 to-violet-400 bg-clip-text text-transparent">
            Phone Monitor API
          </h1>
          <span className="px-2 py-1 text-xs font-mono bg-blue-800/20 text-blue-700 rounded border border-blue-800/30">
            REAL DATA
          </span>
        </div>
        <p className="text-gray-400">
          Neural phone monitoring system • Real API responses from ASI Trinity
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <button
            onClick={fetchAllEndpoints}
            className="flex items-center gap-2 px-4 py-2 bg-blue-900 hover:bg-emerald-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh All
          </button>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="autoRefresh"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-4 h-4 accent-blue-800"
            />
            <label htmlFor="autoRefresh" className="text-sm text-gray-300">Auto Refresh</label>
          </div>

          {autoRefresh && (
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
            >
              <option value={3000}>3s</option>
              <option value={5000}>5s</option>
              <option value={10000}>10s</option>
              <option value={30000}>30s</option>
            </select>
          )}

          <div className="ml-auto text-xs text-gray-500 font-mono">
            {Object.values(responses).filter(r => !r.loading && r.status !== null).length} / {ENDPOINTS.length} loaded
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Endpoint List */}
        <div className="lg:col-span-1 space-y-4">
          {Object.entries(categorizedEndpoints).map(([category, endpoints]) => (
            <div key={category} className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 overflow-hidden">
              <div className="px-4 py-2 bg-white/5 border-b border-white/10">
                <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">
                  {category}
                </h3>
              </div>
              <div className="divide-y divide-white/5">
                {endpoints.map((endpoint) => {
                  const response = responses[endpoint.url];
                  const Icon = endpoint.icon;
                  const isSelected = selectedEndpoint === endpoint.url;

                  return (
                    <button
                      key={endpoint.url}
                      onClick={() => setSelectedEndpoint(endpoint.url)}
                      className={`w-full p-3 text-left transition-colors ${isSelected ? 'bg-blue-900/20 border-l-2 border-blue-800' : 'hover:bg-white/5'
                        }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <Icon className={`w-4 h-4 ${isSelected ? 'text-blue-700' : 'text-gray-500'}`} />
                          <span className="font-medium text-sm">{endpoint.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {response?.loading ? (
                            <RefreshCw className="w-3 h-3 text-violet-400 animate-spin" />
                          ) : response?.status ? (
                            <span className={`w-2 h-2 rounded-full ${getStatusColor(response.status)}`} />
                          ) : null}
                          <span className="px-1.5 py-0.5 text-xs font-mono bg-blue-800/20 text-blue-700 rounded">
                            {endpoint.method}
                          </span>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500 truncate">{endpoint.url}</div>
                      {response?.responseTime && !response.loading && (
                        <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
                          <Clock className="w-3 h-3" />
                          {response.responseTime}ms
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Response Panel */}
        <div className="lg:col-span-2">
          <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 overflow-hidden">
            {/* Response Header */}
            <div className="p-4 bg-white/5 border-b border-white/10">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {selectedConfig && <selectedConfig.icon className="w-5 h-5 text-blue-700" />}
                  <h2 className="text-lg font-semibold">{selectedConfig?.name}</h2>
                </div>
                <button
                  onClick={() => selectedConfig && fetchEndpoint(selectedConfig)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  disabled={selectedResponse?.loading}
                >
                  <RefreshCw className={`w-4 h-4 ${selectedResponse?.loading ? 'animate-spin text-violet-400' : 'text-gray-400'}`} />
                </button>
              </div>

              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2 font-mono text-blue-700">
                  <span className="px-2 py-0.5 bg-blue-800/20 rounded text-xs">
                    {selectedConfig?.method}
                  </span>
                  {selectedConfig?.url}
                </div>
              </div>

              {selectedResponse && !selectedResponse.loading && (
                <div className="flex items-center gap-4 mt-3 text-xs">
                  <div className="flex items-center gap-1">
                    {selectedResponse.status && selectedResponse.status >= 200 && selectedResponse.status < 300 ? (
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-red-400" />
                    )}
                    <span className={`font-mono ${selectedResponse.status && selectedResponse.status >= 200 && selectedResponse.status < 300 ? 'text-green-400' : 'text-red-400'}`}>
                      {selectedResponse.status} {getStatusText(selectedResponse.status)}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-gray-400">
                    <Clock className="w-3 h-3" />
                    <span className="font-mono">{selectedResponse.responseTime}ms</span>
                  </div>
                  {selectedResponse.timestamp && (
                    <div className="text-gray-500 font-mono">
                      {new Date(selectedResponse.timestamp).toLocaleTimeString()}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Response Body */}
            <div className="p-4">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Response Body</div>

              {selectedResponse?.loading ? (
                <div className="flex items-center justify-center py-12">
                  <RefreshCw className="w-6 h-6 text-blue-700 animate-spin" />
                  <span className="ml-2 text-gray-400">Loading...</span>
                </div>
              ) : selectedResponse?.error ? (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-red-400 mb-2">
                    <AlertCircle className="w-5 h-5" />
                    <span className="font-semibold">Error</span>
                    </div>
                    <pre className="text-sm text-red-300 font-mono whitespace-pre-wrap">
                      {selectedResponse.error}
                    </pre>
                  </div>
                ) : (
                <div className="bg-gray-900/50 rounded-lg p-4 max-h-[600px] overflow-auto">
                  <pre className="text-sm font-mono text-gray-300 whitespace-pre-wrap">
                    {JSON.stringify(selectedResponse?.data, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            {Object.entries(responses).slice(0, 4).map(([url, response]) => {
              const config = ENDPOINTS.find(e => e.url === url);
              if (!config || !response || response.loading) return null;

              return (
                <div key={url} className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <config.icon className="w-4 h-4 text-blue-700" />
                    <span className="text-xs text-gray-400 truncate">{config.name}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className={`text-lg font-bold ${response.status && response.status < 300 ? 'text-green-400' : 'text-red-400'}`}>
                      {response.status || 'N/A'}
                    </span>
                    <span className="text-xs text-gray-500">{response.responseTime}ms</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 text-center">
        <p className="text-xs text-gray-600 font-mono">
          Phone Monitor • Real API Data • No Mock Values • No Math.random()
        </p>
      </div>
    </div>
  );
}








