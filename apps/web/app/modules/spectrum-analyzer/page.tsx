'use client';

import { useState, useEffect, useCallback } from 'react';
import { BarChart3, Waves, Radio, RefreshCw, Clock, CheckCircle, AlertCircle, Zap, Activity } from 'lucide-react';

// API Response Types
interface FrequencyBand {
  name: string;
  range: string;
  power: number;
  dominant: boolean;
  color: string;
}

interface SpectrumData {
  session_id: string;
  timestamp: string;
  sampling_rate: number;
  frequency_bands: FrequencyBand[];
  total_power: number;
  dominant_band: string;
  signal_quality: number;
  analysis_duration_ms: number;
}

interface HistoricalSession {
  id: string;
  name: string;
  timestamp: string;
  duration_seconds: number;
  average_power: number;
  dominant_frequency: string;
}

interface APIResponse {
  success: boolean;
  data: SpectrumData | HistoricalSession[] | null;
  error: string | null;
  status: number;
  responseTime: number;
  timestamp: string;
}

interface EndpointConfig {
  name: string;
  method: string;
  path: string;
  description: string;
}

const ENDPOINTS: EndpointConfig[] = [
  { name: 'Live Spectrum', method: 'GET', path: '/api/spectrum/live', description: 'Real-time FFT analysis' },
  { name: 'Frequency Bands', method: 'GET', path: '/api/spectrum/bands', description: 'Frequency band breakdown' },
  { name: 'Historical Sessions', method: 'GET', path: '/api/spectrum/history', description: 'Past analysis sessions' },
  { name: 'ALBI Health', method: 'GET', path: '/api/albi/health', description: 'ALBI service status' },
];

// Use relative paths for security - proxied through Next.js API routes
const API_BASE = '';

const BAND_COLORS: Record<string, string> = {
  'delta': 'bg-red-500',
  'theta': 'bg-orange-500',
  'alpha': 'bg-yellow-500',
  'beta': 'bg-blue-800',
  'gamma': 'bg-purple-500',
};

export default function SpectrumAnalyzerPage() {
  const [selectedEndpoint, setSelectedEndpoint] = useState<EndpointConfig>(ENDPOINTS[0]);
  const [response, setResponse] = useState<APIResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [requestHistory, setRequestHistory] = useState<APIResponse[]>([]);

  const executeRequest = useCallback(async (endpoint: EndpointConfig) => {
    setIsLoading(true);
    const startTime = performance.now();

    try {
      const res = await fetch(`${API_BASE}${endpoint.path}`, {
        method: endpoint.method,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        cache: 'no-store',
      });

      const endTime = performance.now();
      const responseTime = Math.round(endTime - startTime);

      let data = null;
      let error = null;

      try {
        const jsonData = await res.json();
        if (res.ok) {
          data = jsonData;
        } else {
          error = jsonData.detail || jsonData.message || `HTTP ${res.status}`;
        }
      } catch {
        error = 'Invalid JSON response';
      }

      const apiResponse: APIResponse = {
        success: res.ok,
        data,
        error,
        status: res.status,
        responseTime,
        timestamp: new Date().toISOString(),
      };

      setResponse(apiResponse);
      setRequestHistory(prev => [apiResponse, ...prev].slice(0, 10));

    } catch (err) {
      const endTime = performance.now();
      const apiResponse: APIResponse = {
        success: false,
        data: null,
        error: err instanceof Error ? err.message : 'Network error',
        status: 0,
        responseTime: Math.round(endTime - startTime),
        timestamp: new Date().toISOString(),
      };
      setResponse(apiResponse);
      setRequestHistory(prev => [apiResponse, ...prev].slice(0, 10));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    executeRequest(selectedEndpoint);
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      executeRequest(selectedEndpoint);
    }, 1000);
    return () => clearInterval(interval);
  }, [autoRefresh, selectedEndpoint, executeRequest]);

  const getStatusColor = (status: number) => {
    if (status >= 200 && status < 300) return 'text-blue-700';
    if (status >= 400 && status < 500) return 'text-amber-400';
    return 'text-red-400';
  };

  const getStatusBadge = (status: number) => {
    if (status >= 200 && status < 300) return 'bg-blue-800/20 text-blue-700 border-blue-800/30';
    if (status >= 400 && status < 500) return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    return 'bg-red-500/20 text-red-400 border-red-500/30';
  };

  const getBandColor = (name: string) => {
    return BAND_COLORS[name.toLowerCase()] || 'bg-slate-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-emerald-950 to-slate-950 text-white p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-gradient-to-br from-blue-800/20 to-violet-500/20 border border-blue-800/30">
              <BarChart3 className="w-8 h-8 text-blue-700" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-700 to-violet-400 bg-clip-text text-transparent">
                Spectrum Analyzer
              </h1>
              <p className="text-slate-400 text-sm">Multi-band EEG FFT Analysis • Postman-Style API Interface</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all ${autoRefresh
                  ? 'bg-blue-800/20 text-blue-700 border border-blue-800/30'
                  : 'bg-slate-800/50 text-slate-400 border border-slate-700/50 hover:bg-slate-700/50'
                }`}
            >
              <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
              {autoRefresh ? 'Live' : 'Auto'}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-12 gap-6">
        {/* Sidebar - Endpoints */}
        <div className="col-span-3 space-y-3">
          <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-800/50 p-4">
            <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
              <Radio className="w-4 h-4 text-blue-700" />
              API Endpoints
            </h3>
            <div className="space-y-2">
              {ENDPOINTS.map((endpoint) => (
                <button
                  key={endpoint.path}
                  onClick={() => {
                    setSelectedEndpoint(endpoint);
                    executeRequest(endpoint);
                  }}
                  className={`w-full text-left p-3 rounded-lg transition-all ${selectedEndpoint.path === endpoint.path
                      ? 'bg-blue-800/20 border border-blue-800/30'
                      : 'bg-slate-800/30 border border-slate-700/30 hover:bg-slate-800/50'
                    }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 text-xs font-mono rounded bg-blue-800/20 text-blue-700 border border-blue-800/30">
                      {endpoint.method}
                    </span>
                    <span className="text-sm font-medium text-white">{endpoint.name}</span>
                  </div>
                  <p className="text-xs text-slate-500 font-mono truncate">{endpoint.path}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Request History */}
          <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-800/50 p-4">
            <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
              <Clock className="w-4 h-4 text-blue-700" />
              Request History
            </h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {requestHistory.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-4">No requests yet</p>
              ) : (
                requestHistory.map((req, idx) => (
                  <div key={idx} className="p-2 rounded-lg bg-slate-800/30 border border-slate-700/30">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-xs font-mono ${getStatusColor(req.status)}`}>
                        {req.status || 'ERR'}
                      </span>
                      <span className="text-xs text-slate-500">{req.responseTime}ms</span>
                    </div>
                    <p className="text-xs text-slate-400">
                      {new Date(req.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="col-span-9 space-y-6">
          {/* Request Bar */}
          <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-800/50 p-4">
            <div className="flex items-center gap-3">
              <span className="px-3 py-1.5 text-sm font-mono rounded-lg bg-blue-800/20 text-blue-700 border border-blue-800/30">
                {selectedEndpoint.method}
              </span>
              <div className="flex-1 px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700/50 font-mono text-sm text-slate-300">
                {selectedEndpoint.path}
              </div>
              <button
                onClick={() => executeRequest(selectedEndpoint)}
                disabled={isLoading}
                className="px-6 py-2 bg-gradient-to-r from-blue-800 to-violet-500 text-white font-semibold rounded-lg hover:from-blue-900 hover:to-violet-600 transition-all disabled:opacity-50 flex items-center gap-2"
              >
                {isLoading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Zap className="w-4 h-4" />
                )}
                Send
              </button>
            </div>
          </div>

          {/* Response Section */}
          {response && (
            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-800/50 overflow-hidden">
              {/* Response Header */}
              <div className="px-4 py-3 border-b border-slate-800/50 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className={`px-3 py-1 text-sm font-mono rounded-lg border ${getStatusBadge(response.status)}`}>
                    {response.status || 'Error'}
                  </span>
                  <span className="text-sm text-slate-400">
                    <Clock className="w-4 h-4 inline mr-1" />
                    {response.responseTime}ms
                  </span>
                  {response.success ? (
                    <span className="text-blue-700 flex items-center gap-1 text-sm">
                      <CheckCircle className="w-4 h-4" /> Success
                    </span>
                  ) : (
                    <span className="text-red-400 flex items-center gap-1 text-sm">
                      <AlertCircle className="w-4 h-4" /> Failed
                    </span>
                  )}
                </div>
                <span className="text-xs text-slate-500">
                  {new Date(response.timestamp).toLocaleString()}
                </span>
              </div>

              {/* Response Body */}
              <div className="p-4">
                {response.error ? (
                  <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400">
                    <p className="font-mono text-sm">{response.error}</p>
                  </div>
                ) : response.data ? (
                  <div className="space-y-6">
                    {/* Spectrum Metrics */}
                    {(response.data as SpectrumData).frequency_bands && (
                      <>
                        <div className="grid grid-cols-4 gap-4">
                          <div className="p-4 rounded-xl bg-gradient-to-br from-blue-800/10 to-violet-500/10 border border-blue-800/20">
                            <div className="flex items-center gap-2 mb-2">
                              <BarChart3 className="w-5 h-5 text-blue-700" />
                              <span className="text-sm text-slate-400">Total Power</span>
                            </div>
                            <p className="text-2xl font-bold text-blue-700">
                              {(response.data as SpectrumData).total_power?.toFixed(1) || 0} dB
                            </p>
                          </div>
                          <div className="p-4 rounded-xl bg-gradient-to-br from-violet-500/10 to-violet-500/10 border border-violet-500/20">
                            <div className="flex items-center gap-2 mb-2">
                              <Waves className="w-5 h-5 text-violet-400" />
                              <span className="text-sm text-slate-400">Dominant</span>
                            </div>
                            <p className="text-2xl font-bold text-violet-400 capitalize">
                              {(response.data as SpectrumData).dominant_band || 'N/A'}
                            </p>
                          </div>
                          <div className="p-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20">
                            <div className="flex items-center gap-2 mb-2">
                              <Activity className="w-5 h-5 text-purple-400" />
                              <span className="text-sm text-slate-400">Signal Quality</span>
                            </div>
                            <p className="text-2xl font-bold text-purple-400">
                              {(response.data as SpectrumData).signal_quality || 0}%
                            </p>
                          </div>
                          <div className="p-4 rounded-xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/20">
                            <div className="flex items-center gap-2 mb-2">
                              <Clock className="w-5 h-5 text-amber-400" />
                              <span className="text-sm text-slate-400">Analysis Time</span>
                            </div>
                            <p className="text-2xl font-bold text-amber-400">
                              {(response.data as SpectrumData).analysis_duration_ms || 0} ms
                            </p>
                          </div>
                        </div>

                          {/* Frequency Bands Visualization */}
                          <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
                            <h4 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                              <BarChart3 className="w-4 h-4 text-blue-700" />
                              Frequency Bands Analysis
                            </h4>
                            <div className="space-y-4">
                              {(response.data as SpectrumData).frequency_bands.map((band, idx) => (
                                <div key={idx} className="flex items-center gap-4">
                                  <div className="w-20 flex items-center gap-2">
                                    {band.dominant && <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>}
                                    <span className="text-sm font-medium text-slate-300 capitalize">{band.name}</span>
                                </div>
                                <div className="text-xs text-slate-500 w-24">{band.range}</div>
                                <div className="flex-1 h-6 bg-slate-700/50 rounded-lg overflow-hidden">
                                  <div
                                    className={`h-full ${getBandColor(band.name)} transition-all duration-500 flex items-center justify-end pr-2`}
                                    style={{ width: `${Math.min(band.power, 100)}%` }}
                                  >
                                    {band.power > 20 && (
                                      <span className="text-xs font-mono text-white">{band.power.toFixed(1)}%</span>
                                    )}
                                  </div>
                                </div>
                                <div className="w-16 text-right text-sm font-mono text-slate-400">
                                  {band.power.toFixed(1)}%
                                </div>
                              </div>
                            ))}
                            </div>
                          </div>
                        </>
                      )}

                      {/* Historical Sessions */}
                      {Array.isArray(response.data) && response.data.length > 0 && (
                        <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
                          <h4 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                            <Clock className="w-4 h-4 text-blue-700" />
                            Historical Sessions ({response.data.length})
                          </h4>
                          <div className="space-y-2">
                            {(response.data as HistoricalSession[]).map((session, idx) => (
                              <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-slate-900/50 border border-slate-700/30">
                              <div>
                                <p className="text-sm font-medium text-white">{session.name}</p>
                                <p className="text-xs text-slate-500">
                                  {new Date(session.timestamp).toLocaleString()} • {session.duration_seconds}s
                                </p>
                              </div>
                              <div className="flex items-center gap-4">
                                <span className="text-sm text-blue-700 font-mono">{session.average_power.toFixed(1)} dB</span>
                                <span className="text-xs px-2 py-1 rounded bg-violet-500/20 text-violet-400 capitalize">
                                  {session.dominant_frequency}
                                </span>
                              </div>
                            </div>
                          ))}
                          </div>
                        </div>
                      )}

                      {/* Raw JSON Response */}
                      <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
                        <h4 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                          <Zap className="w-4 h-4 text-blue-700" />
                          Raw JSON Response
                        </h4>
                        <pre className="p-4 bg-slate-950/50 rounded-lg overflow-x-auto text-xs font-mono text-slate-300 max-h-96 overflow-y-auto">
                          {JSON.stringify(response.data, null, 2)}
                        </pre>
                    </div>
                  </div>
                ) : (
                      <p className="text-slate-500 text-center py-8">No data received</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-7xl mx-auto mt-8 text-center">
        <p className="text-xs text-slate-600">
          Spectrum Analyzer Module • Real API Data • No Mock Values
        </p>
      </div>
    </div>
  );
}








