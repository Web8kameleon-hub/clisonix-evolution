'use client';

import { useState, useEffect, useCallback } from 'react';
import { Music2, Waves, Radio, RefreshCw, Clock, CheckCircle, AlertCircle, Zap, Volume2, Settings, Download } from 'lucide-react';

// API Response Types
interface ConversionSettings {
  input_channel: string;
  output_format: string;
  frequency_mapping: string;
  spatial_audio: boolean;
  realtime_processing: boolean;
}

interface AudioOutput {
  is_converting: boolean;
  current_frequency: number;
  output_level: number;
  mapped_note: string;
  spatial_position: { x: number; y: number; z: number };
}

interface ConversionStats {
  total_conversions: number;
  average_latency_ms: number;
  conversion_quality: number;
  exported_files: number;
}

interface ConverterStatus {
  service: string;
  status: string;
  settings: ConversionSettings;
  current_output: AudioOutput;
  stats: ConversionStats;
  supported_formats: string[];
  supported_mappings: string[];
}

interface APIResponse {
  success: boolean;
  data: ConverterStatus | ConversionStats | AudioOutput | null;
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
  { name: 'JONA Metrics', method: 'GET', path: '/api/asi/jona/metrics', description: 'JONA audio synthesis metrics' },
  { name: 'ASI Status', method: 'GET', path: '/api/asi/status', description: 'ASI Trinity system status' },
  { name: 'ASI Health', method: 'GET', path: '/api/asi/health', description: 'System health check' },
  { name: 'ALBI Metrics', method: 'GET', path: '/api/asi/albi/metrics', description: 'ALBI neural metrics' },
  { name: 'ALBA Metrics', method: 'GET', path: '/api/asi/alba/metrics', description: 'ALBA network metrics' },
];

// Use relative paths for security - proxied through Next.js API routes
const API_BASE = '';

export default function NeuroacousticConverterPage() {
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
    }, 500);
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

  const getMethodBadge = (method: string) => {
    if (method === 'GET') return 'bg-blue-800/20 text-blue-700 border-blue-800/30';
    if (method === 'POST') return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    return 'bg-violet-500/20 text-violet-400 border-violet-500/30';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-violet-950 to-slate-950 text-white p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-gradient-to-br from-violet-500/20 to-purple-500/20 border border-violet-500/30">
              <Music2 className="w-8 h-8 text-violet-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
                Neuroacoustic Converter
              </h1>
              <p className="text-slate-400 text-sm">EEG to Audio Conversion • Postman-Style API Interface</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all ${autoRefresh
                  ? 'bg-violet-500/20 text-violet-400 border border-violet-500/30'
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
              <Radio className="w-4 h-4 text-violet-400" />
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
                      ? 'bg-violet-500/20 border border-violet-500/30'
                      : 'bg-slate-800/30 border border-slate-700/30 hover:bg-slate-800/50'
                    }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-2 py-0.5 text-xs font-mono rounded border ${getMethodBadge(endpoint.method)}`}>
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
              <Clock className="w-4 h-4 text-violet-400" />
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
              <span className={`px-3 py-1.5 text-sm font-mono rounded-lg border ${getMethodBadge(selectedEndpoint.method)}`}>
                {selectedEndpoint.method}
              </span>
              <div className="flex-1 px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700/50 font-mono text-sm text-slate-300">
                {selectedEndpoint.path}
              </div>
              <button
                onClick={() => executeRequest(selectedEndpoint)}
                disabled={isLoading}
                className="px-6 py-2 bg-gradient-to-r from-violet-500 to-purple-500 text-white font-semibold rounded-lg hover:from-violet-600 hover:to-purple-600 transition-all disabled:opacity-50 flex items-center gap-2"
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
                    {/* Converter Status Cards */}
                    {(response.data as ConverterStatus).service && (
                      <>
                        <div className="grid grid-cols-4 gap-4">
                          <div className="p-4 rounded-xl bg-gradient-to-br from-violet-500/10 to-purple-500/10 border border-violet-500/20">
                            <div className="flex items-center gap-2 mb-2">
                              <Music2 className="w-5 h-5 text-violet-400" />
                              <span className="text-sm text-slate-400">Status</span>
                              </div>
                              <p className={`text-xl font-bold capitalize ${(response.data as ConverterStatus).status === 'online' ? 'text-blue-700' :
                                  (response.data as ConverterStatus).status === 'converting' ? 'text-violet-400' :
                                    'text-slate-400'
                                }`}>
                                {(response.data as ConverterStatus).status || 'Unknown'}
                              </p>
                            </div>
                            <div className="p-4 rounded-xl bg-gradient-to-br from-violet-500/10 to-violet-500/10 border border-violet-500/20">
                              <div className="flex items-center gap-2 mb-2">
                                <Waves className="w-5 h-5 text-violet-400" />
                                <span className="text-sm text-slate-400">Frequency</span>
                              </div>
                              <p className="text-xl font-bold text-violet-400">
                                {(response.data as ConverterStatus).current_output?.current_frequency?.toFixed(1) || 0} Hz
                              </p>
                            </div>
                            <div className="p-4 rounded-xl bg-gradient-to-br from-blue-800/10 to-green-500/10 border border-blue-800/20">
                              <div className="flex items-center gap-2 mb-2">
                                <Volume2 className="w-5 h-5 text-blue-700" />
                                <span className="text-sm text-slate-400">Output Level</span>
                              </div>
                              <p className="text-xl font-bold text-blue-700">
                                {(response.data as ConverterStatus).current_output?.output_level?.toFixed(0) || 0}%
                              </p>
                            </div>
                            <div className="p-4 rounded-xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/20">
                              <div className="flex items-center gap-2 mb-2">
                                <Download className="w-5 h-5 text-amber-400" />
                                <span className="text-sm text-slate-400">Exported</span>
                              </div>
                              <p className="text-xl font-bold text-amber-400">
                                {(response.data as ConverterStatus).stats?.exported_files || 0}
                              </p>
                            </div>
                          </div>

                          {/* Current Output */}
                          {(response.data as ConverterStatus).current_output && (
                            <div className="p-4 rounded-xl bg-gradient-to-r from-violet-500/10 to-purple-500/10 border border-violet-500/20">
                              <h4 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                                <Music2 className="w-4 h-4 text-violet-400" />
                                Current Audio Output
                              </h4>
                              <div className="grid grid-cols-4 gap-4 text-center">
                                <div>
                                  <p className="text-2xl font-bold text-violet-400">
                                    {(response.data as ConverterStatus).current_output?.mapped_note || 'N/A'}
                                  </p>
                                  <p className="text-xs text-slate-500">Mapped Note</p>
                                </div>
                                <div>
                                  <p className="text-2xl font-bold text-violet-400">
                                    {(response.data as ConverterStatus).current_output?.current_frequency?.toFixed(1) || 0} Hz
                                  </p>
                                  <p className="text-xs text-slate-500">Frequency</p>
                                </div>
                                <div>
                                  <p className="text-2xl font-bold text-blue-700">
                                    {(response.data as ConverterStatus).current_output?.output_level?.toFixed(0) || 0}%
                                  </p>
                                  <p className="text-xs text-slate-500">Level</p>
                                </div>
                                <div>
                                  <p className={`text-2xl font-bold ${(response.data as ConverterStatus).current_output?.is_converting ? 'text-blue-700' : 'text-slate-400'}`}>
                                    {(response.data as ConverterStatus).current_output?.is_converting ? 'Active' : 'Idle'}
                                  </p>
                                  <p className="text-xs text-slate-500">Converting</p>
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Settings */}
                          {(response.data as ConverterStatus).settings && (
                            <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
                              <h4 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                                <Settings className="w-4 h-4 text-violet-400" />
                                Conversion Settings
                              </h4>
                              <div className="grid grid-cols-3 gap-4">
                                <div className="p-3 rounded-lg bg-slate-900/50">
                                  <p className="text-xs text-slate-500 mb-1">Input Channel</p>
                                  <p className="text-sm font-mono text-white">
                                    {(response.data as ConverterStatus).settings?.input_channel || 'N/A'}
                                  </p>
                                </div>
                                <div className="p-3 rounded-lg bg-slate-900/50">
                                  <p className="text-xs text-slate-500 mb-1">Output Format</p>
                                  <p className="text-sm font-mono text-white">
                                    {(response.data as ConverterStatus).settings?.output_format || 'N/A'}
                                  </p>
                                </div>
                                <div className="p-3 rounded-lg bg-slate-900/50">
                                  <p className="text-xs text-slate-500 mb-1">Frequency Mapping</p>
                                  <p className="text-sm font-mono text-white capitalize">
                                    {(response.data as ConverterStatus).settings?.frequency_mapping || 'N/A'}
                                  </p>
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Stats */}
                          {(response.data as ConverterStatus).stats && (
                            <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
                              <h4 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                                <Zap className="w-4 h-4 text-violet-400" />
                                Conversion Statistics
                              </h4>
                              <div className="grid grid-cols-4 gap-4">
                                <div className="text-center">
                                  <p className="text-xl font-bold text-violet-400">
                                    {(response.data as ConverterStatus).stats?.total_conversions?.toLocaleString() || 0}
                                  </p>
                                  <p className="text-xs text-slate-500">Total Conversions</p>
                                </div>
                                <div className="text-center">
                                  <p className="text-xl font-bold text-violet-400">
                                    {(response.data as ConverterStatus).stats?.average_latency_ms?.toFixed(1) || 0} ms
                                  </p>
                                  <p className="text-xs text-slate-500">Avg Latency</p>
                                </div>
                                <div className="text-center">
                                  <p className="text-xl font-bold text-blue-700">
                                    {(response.data as ConverterStatus).stats?.conversion_quality?.toFixed(1) || 0}%
                                  </p>
                                  <p className="text-xs text-slate-500">Quality</p>
                                </div>
                                <div className="text-center">
                                  <p className="text-xl font-bold text-amber-400">
                                    {(response.data as ConverterStatus).stats?.exported_files || 0}
                                  </p>
                                  <p className="text-xs text-slate-500">Exported Files</p>
                                </div>
                              </div>
                            </div>
                          )}
                        </>
                      )}

                      {/* Raw JSON Response */}
                      <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
                        <h4 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                          <Zap className="w-4 h-4 text-violet-400" />
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
          Neuroacoustic Converter • Real API Data • No Mock Values
        </p>
      </div>
    </div>
  );
}








