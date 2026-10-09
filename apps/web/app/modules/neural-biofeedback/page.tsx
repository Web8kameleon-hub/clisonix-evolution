'use client';

import { useState, useEffect, useCallback } from 'react';
import { Heart, Brain, Waves, Radio, RefreshCw, Clock, CheckCircle, AlertCircle, Zap, Activity, Target } from 'lucide-react';

// API Response Types
interface TrainingSession {
  session_id: string;
  wave_type: string;
  frequency_range: string;
  duration_seconds: number;
  coherence: number;
  progress: number;
  started_at: string;
  completed: boolean;
}

interface TrainingProgress {
  wave_type: string;
  frequency_range: string;
  total_sessions: number;
  avg_coherence: number;
  best_coherence: number;
  total_time_minutes: number;
  last_session: string;
}

interface BiofeedbackMetrics {
  service: string;
  status: string;
  alpha_training: TrainingProgress;
  theta_training: TrainingProgress;
  beta_training: TrainingProgress;
  active_session: TrainingSession | null;
  total_sessions_completed: number;
}

interface APIResponse {
  success: boolean;
  data: BiofeedbackMetrics | TrainingSession | TrainingProgress[] | null;
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
  { name: 'ASI Status', method: 'GET', path: '/api/asi/status', description: 'ASI Trinity system status' },
  { name: 'ASI Health', method: 'GET', path: '/api/asi/health', description: 'System health check' },
  { name: 'ALBI Metrics', method: 'GET', path: '/api/asi/albi/metrics', description: 'ALBI neural processor metrics' },
  { name: 'ALBA Metrics', method: 'GET', path: '/api/asi/alba/metrics', description: 'ALBA network metrics' },
  { name: 'JONA Metrics', method: 'GET', path: '/api/asi/jona/metrics', description: 'JONA coordination metrics' },
];

// Use relative paths for security - proxied through Next.js API routes
const API_BASE = '';

export default function NeuralBiofeedbackPage() {
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
    }, 2000);
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

  const getCoherenceColor = (coherence: number) => {
    if (coherence >= 80) return 'text-blue-700';
    if (coherence >= 60) return 'text-violet-400';
    if (coherence >= 40) return 'text-amber-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-rose-950 to-slate-950 text-white p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-gradient-to-br from-rose-500/20 to-pink-500/20 border border-rose-500/30">
              <Heart className="w-8 h-8 text-rose-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-rose-400 to-pink-400 bg-clip-text text-transparent">
                Neural Biofeedback
              </h1>
              <p className="text-slate-400 text-sm">Brain Wave Training System • Postman-Style API Interface</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all ${autoRefresh
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
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
              <Radio className="w-4 h-4 text-rose-400" />
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
                      ? 'bg-rose-500/20 border border-rose-500/30'
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
              <Clock className="w-4 h-4 text-rose-400" />
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
                className="px-6 py-2 bg-gradient-to-r from-rose-500 to-pink-500 text-white font-semibold rounded-lg hover:from-rose-600 hover:to-pink-600 transition-all disabled:opacity-50 flex items-center gap-2"
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
                      {/* Biofeedback Metrics Cards */}
                      {(response.data as BiofeedbackMetrics).service && (
                        <>
                          <div className="grid grid-cols-4 gap-4">
                            <div className="p-4 rounded-xl bg-gradient-to-br from-rose-500/10 to-pink-500/10 border border-rose-500/20">
                              <div className="flex items-center gap-2 mb-2">
                                <Heart className="w-5 h-5 text-rose-400" />
                                <span className="text-sm text-slate-400">Status</span>
                              </div>
                              <p className={`text-xl font-bold capitalize ${(response.data as BiofeedbackMetrics).status === 'online' ? 'text-blue-700' : 'text-slate-400'
                                }`}>
                                {(response.data as BiofeedbackMetrics).status || 'Unknown'}
                              </p>
                            </div>
                            <div className="p-4 rounded-xl bg-gradient-to-br from-violet-500/10 to-violet-500/10 border border-violet-500/20">
                              <div className="flex items-center gap-2 mb-2">
                                <Target className="w-5 h-5 text-violet-400" />
                                <span className="text-sm text-slate-400">Total Sessions</span>
                              </div>
                              <p className="text-xl font-bold text-violet-400">
                                {(response.data as BiofeedbackMetrics).total_sessions_completed || 0}
                              </p>
                            </div>
                            <div className="p-4 rounded-xl bg-gradient-to-br from-blue-800/10 to-green-500/10 border border-blue-800/20">
                              <div className="flex items-center gap-2 mb-2">
                                <Waves className="w-5 h-5 text-blue-700" />
                                <span className="text-sm text-slate-400">Alpha Sessions</span>
                              </div>
                              <p className="text-xl font-bold text-blue-700">
                                {(response.data as BiofeedbackMetrics).alpha_training?.total_sessions || 0}
                              </p>
                            </div>
                            <div className="p-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-violet-500/10 border border-purple-500/20">
                              <div className="flex items-center gap-2 mb-2">
                                <Brain className="w-5 h-5 text-purple-400" />
                                <span className="text-sm text-slate-400">Theta Sessions</span>
                              </div>
                              <p className="text-xl font-bold text-purple-400">
                                {(response.data as BiofeedbackMetrics).theta_training?.total_sessions || 0}
                              </p>
                            </div>
                          </div>

                          {/* Training Progress */}
                          <div className="grid grid-cols-3 gap-4">
                            {/* Alpha */}
                            <div className="p-4 rounded-xl bg-gradient-to-br from-violet-500/10 to-violet-500/10 border border-violet-500/20">
                              <h4 className="text-sm font-semibold text-violet-400 mb-3 flex items-center gap-2">
                                🌊 Alpha Training
                              </h4>
                              <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                  <span className="text-slate-400">Avg Coherence</span>
                                  <span className={getCoherenceColor((response.data as BiofeedbackMetrics).alpha_training?.avg_coherence || 0)}>
                                    {(response.data as BiofeedbackMetrics).alpha_training?.avg_coherence?.toFixed(1) || 0}%
                                  </span>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span className="text-slate-400">Best</span>
                                  <span className="text-blue-700">
                                    {(response.data as BiofeedbackMetrics).alpha_training?.best_coherence?.toFixed(1) || 0}%
                                  </span>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span className="text-slate-400">Total Time</span>
                                  <span className="text-white">
                                    {(response.data as BiofeedbackMetrics).alpha_training?.total_time_minutes || 0} min
                                  </span>
                                </div>
                              </div>
                            </div>

                            {/* Theta */}
                            <div className="p-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-violet-500/10 border border-purple-500/20">
                              <h4 className="text-sm font-semibold text-purple-400 mb-3 flex items-center gap-2">
                                🧘 Theta Training
                              </h4>
                              <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                  <span className="text-slate-400">Avg Coherence</span>
                                  <span className={getCoherenceColor((response.data as BiofeedbackMetrics).theta_training?.avg_coherence || 0)}>
                                    {(response.data as BiofeedbackMetrics).theta_training?.avg_coherence?.toFixed(1) || 0}%
                                  </span>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span className="text-slate-400">Best</span>
                                  <span className="text-blue-700">
                                    {(response.data as BiofeedbackMetrics).theta_training?.best_coherence?.toFixed(1) || 0}%
                                  </span>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span className="text-slate-400">Total Time</span>
                                  <span className="text-white">
                                    {(response.data as BiofeedbackMetrics).theta_training?.total_time_minutes || 0} min
                                  </span>
                                </div>
                              </div>
                            </div>

                            {/* Beta */}
                            <div className="p-4 rounded-xl bg-gradient-to-br from-blue-800/10 to-green-500/10 border border-blue-800/20">
                              <h4 className="text-sm font-semibold text-blue-700 mb-3 flex items-center gap-2">
                                ⚡ Beta Training
                              </h4>
                              <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                  <span className="text-slate-400">Avg Coherence</span>
                                  <span className={getCoherenceColor((response.data as BiofeedbackMetrics).beta_training?.avg_coherence || 0)}>
                                    {(response.data as BiofeedbackMetrics).beta_training?.avg_coherence?.toFixed(1) || 0}%
                                  </span>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span className="text-slate-400">Best</span>
                                  <span className="text-blue-700">
                                    {(response.data as BiofeedbackMetrics).beta_training?.best_coherence?.toFixed(1) || 0}%
                                  </span>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span className="text-slate-400">Total Time</span>
                                  <span className="text-white">
                                    {(response.data as BiofeedbackMetrics).beta_training?.total_time_minutes || 0} min
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </>
                      )}

                      {/* Raw JSON Response */}
                      <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
                        <h4 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                          <Zap className="w-4 h-4 text-rose-400" />
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
          Neural Biofeedback Training • Real API Data • No Mock Values
        </p>
      </div>
    </div>
  );
}







