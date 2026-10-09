'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Brain, Radio, Zap, Eye, Activity, TrendingUp, AlertCircle, Check, Play, Pause, Download, Plus, Settings, BookOpen } from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════
// TYPE DEFINITIONS
// ═══════════════════════════════════════════════════════════════════

interface BrainwaveBand {
  frequency: string;
  power_percent: number;
  interpretation: string;
}

interface SessionMetrics {
  session_id: string;
  state: 'idle' | 'recording' | 'paused' | 'completed';
  sample_rate: number;
  duration_seconds: number;
  samples_received: number;
  channels_count: number;
  quality_score: number;
  dominant_band: string;
  dominant_band_power: number;
  state_interpretation: string;
  hemispheric_balance: {
    left_power_percent: number;
    right_power_percent: number;
    asymmetry: string;
    interpretation: string;
  };
  anomalies_detected: number;
}

interface ChannelData {
  [key: string]: number;
}

// ═══════════════════════════════════════════════════════════════════
// PROFESSIONAL ALBI EEG COMPONENT
// ═══════════════════════════════════════════════════════════════════

export default function ALBIEEGAnalyzer() {
  // State Management
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [metrics, setMetrics] = useState<SessionMetrics | null>(null);
  const [channels, setChannels] = useState<string[]>([]);
  const [channelData, setChannelData] = useState<ChannelData>({});
  const [recentEvents, setRecentEvents] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedChannels, setSelectedChannels] = useState<string[]>(['Fp1', 'Fp2', 'F3', 'F4', 'P3', 'P4', 'O1', 'O2']);
  const [showSettingsDoc, setShowSettingsDoc] = useState(false);

  // WebSocket ref
  const wsRef = useRef<WebSocket | null>(null);
  const metricsIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // API Base URL
  const API_BASE = '/api/albi-user';

  // ═══════════════════════════════════════════════════════════════════
  // SESSION MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════

  const startSession = useCallback(async () => {
    try {
      setError(null);
      const response = await fetch(`${API_BASE}/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'albi_eeg_live_operator',
          session_name: `Session ${new Date().toLocaleTimeString()}`
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to start session');
      }

      setSessionId(data.session_id);
      setIsRecording(true);
      setMetrics(null);
      setChannelData({});
      setRecentEvents([]);

      // Connect WebSocket
      connectWebSocket(data.session_id);

      // Start polling metrics
      startMetricsPolling(data.session_id);

    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to start session';
      setError(message);
      console.error('Start session error:', err);
    }
  }, []);

  const stopSession = useCallback(async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(`${API_BASE}/session/${sessionId}/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        setIsRecording(false);
        setIsPaused(false);

        // Close WebSocket
        if (wsRef.current) {
          wsRef.current.close();
          setIsConnected(false);
        }

        // Stop metrics polling
        if (metricsIntervalRef.current) {
          clearInterval(metricsIntervalRef.current);
        }
      }
    } catch (err) {
      console.error('Stop session error:', err);
    }
  }, [sessionId]);

  // ═══════════════════════════════════════════════════════════════════
  // WEBSOCKET STREAMING
  // ═══════════════════════════════════════════════════════════════════

  const connectWebSocket = useCallback((sid: string) => {
    try {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const wsUrl = `${wsProtocol}://${window.location.hostname}:6681/stream/${sid}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          if (message.type === 'frame') {
            // Update channel data
            const frame = message.data;
            setChannelData(frame.channels || {});
          }
        } catch (err) {
          console.error('WebSocket message parse error:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
        setError('WebSocket connection error');
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('WebSocket connection error:', err);
      setError('Failed to connect WebSocket');
    }
  }, []);

  // ═══════════════════════════════════════════════════════════════════
  // METRICS POLLING
  // ═══════════════════════════════════════════════════════════════════

  const startMetricsPolling = useCallback((sid: string) => {
    // Fetch supported channels first
    fetch(`${API_BASE}/channels`)
      .then(r => r.json())
      .then(data => setChannels(data.channels || []))
      .catch(err => console.error('Failed to fetch channels:', err));

    // Poll metrics every 1 second
    metricsIntervalRef.current = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE}/session/${sid}/metrics`, {
          headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
          const data = await response.json();
          setMetrics(data);
        }
      } catch (err) {
        console.error('Metrics polling error:', err);
      }
    }, 1000);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (metricsIntervalRef.current) {
        clearInterval(metricsIntervalRef.current);
      }
    };
  }, []);

  // ═══════════════════════════════════════════════════════════════════
  // RENDER HELPERS
  // ═══════════════════════════════════════════════════════════════════

  const getQualityColor = (score: number) => {
    if (score >= 90) return 'text-green-500';
    if (score >= 75) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getQualityBg = (score: number) => {
    if (score >= 90) return 'bg-green-500/20 border-green-500/50';
    if (score >= 75) return 'bg-yellow-500/20 border-yellow-500/50';
    return 'bg-red-500/20 border-red-500/50';
  };

  const getDominantBandColor = (band: string) => {
    const colors: Record<string, string> = {
      delta: 'from-purple-600 to-purple-400',
      theta: 'from-blue-600 to-blue-400',
      alpha: 'from-green-600 to-green-400',
      beta: 'from-orange-600 to-orange-400',
      gamma: 'from-red-600 to-red-400'
    };
    return colors[band?.toLowerCase()] || 'from-slate-600 to-slate-400';
  };

  const getBandPercent = (band: string) => {
    if (!metrics) return 0;
    const dominant = (metrics.dominant_band || '').toLowerCase();
    if (dominant === band.toLowerCase()) {
      return Math.max(0, Math.min(100, Math.round(metrics.dominant_band_power)));
    }
    const remainder = Math.max(0, 100 - Math.max(0, Math.min(100, metrics.dominant_band_power)));
    return Math.round(remainder / 4);
  };

  // ═══════════════════════════════════════════════════════════════════
  // RENDER UI
  // ═══════════════════════════════════════════════════════════════════

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 p-6 font-mono">
      <style>{`
        @keyframes pulse-ring {
          0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
          70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); }
          100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
        }
        .pulse-ring {
          animation: pulse-ring 2s infinite;
        }
        @keyframes signal-wave {
          0%, 100% { transform: scaleY(1); }
          50% { transform: scaleY(1.5); }
        }
        .signal-wave {
          animation: signal-wave 0.6s ease-in-out infinite;
        }
      `}</style>

      {/* HEADER */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center gap-4 mb-2">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg pulse-ring">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-black bg-gradient-to-r from-blue-400 via-cyan-400 to-green-400 bg-clip-text text-transparent">
              ALBI Professional EEG Analyzer
            </h1>
            <p className="text-slate-400 text-sm mt-1">🧠 Real-time Brainwave Analysis • Clinical-Grade Signal Processing</p>
          </div>
        </div>

        <div className="rounded-xl border border-cyan-500/40 bg-cyan-500/10 px-4 py-3 flex flex-wrap items-center justify-between gap-3 mb-4">
          <div className="text-sm font-bold text-cyan-200">CLISONIX ZEISS VISION ULTRA • 2450px+ • ALBI EEG Ready</div>
          <a
            href="/modules/curiosity-ocean?topic=Analyze%20ALBI%20EEG%20signal%20quality%20with%20ZEISS%20Vision%20Ultra&lang=auto"
            className="inline-flex items-center rounded-lg bg-cyan-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-cyan-500"
          >
            Open ZEISS Vision
          </a>
        </div>

        {/* STATUS BAR */}
        <div className="grid grid-cols-5 gap-3 mt-6">
          <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-3">
            <div className="text-xs text-slate-400 mb-1">SESSION STATUS</div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isRecording ? 'bg-red-500 pulse-ring' : 'bg-slate-600'}`}></div>
              <div className="text-white font-bold">{isRecording ? 'RECORDING' : 'IDLE'}</div>
            </div>
          </div>

          <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-3">
            <div className="text-xs text-slate-400 mb-1">WEBSOCKET</div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 pulse-ring' : 'bg-slate-600'}`}></div>
              <div className="text-white font-bold">{isConnected ? 'CONNECTED' : 'STANDBY'}</div>
            </div>
          </div>

          <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-3">
            <div className="text-xs text-slate-400 mb-1">CHANNELS ACTIVE</div>
            <div className="text-white font-bold text-lg">{selectedChannels.length}</div>
          </div>

          <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-3">
            <div className="text-xs text-slate-400 mb-1">DURATION</div>
            <div className="text-white font-bold">{metrics?.duration_seconds || 0}s</div>
          </div>

          <button
            onClick={() => setShowSettingsDoc(!showSettingsDoc)}
            className="bg-purple-900/50 border border-purple-600 rounded-lg p-3 hover:bg-purple-800/50 transition-colors cursor-pointer group"
            title="Settings Documentation"
          >
            <div className="text-xs text-purple-300 mb-1 flex items-center gap-1">
              <Settings className="w-3 h-3" />
              SETTINGS
            </div>
            <div className="text-white font-bold text-sm flex items-center gap-1">
              <BookOpen className="w-4 h-4" />
              Docs
            </div>
          </button>
        </div>

        {/* SETTINGS DOCUMENTATION INDICATOR */}
        {showSettingsDoc && (
          <div className="mt-4 p-4 bg-purple-900/20 border border-purple-600/50 rounded-lg">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-bold text-purple-300 mb-2 flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Settings Tab Integration Guide
                </h3>
                <p className="text-purple-200 text-sm mb-3">
                  Complete analysis and implementation roadmap for adding a Settings Tab to the ALBI EEG module.
                </p>
                <div className="text-xs text-purple-300 space-y-1 mb-3">
                  <p>✓ 6-tab interface specification (Device, Display, Data, Alerts, Profiles, Files)</p>
                  <p>✓ 4-week implementation roadmap with phase breakdown</p>
                  <p>✓ Backend API endpoints for settings persistence</p>
                  <p>✓ Hospital-grade profile management</p>
                </div>
              </div>
              <button
                onClick={() => setShowSettingsDoc(false)}
                className="text-purple-400 hover:text-purple-300 text-xl font-bold"
              >
                ✕
              </button>
            </div>
            <a
              href="/albi-settings-documentation"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 mt-3 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-bold transition-colors"
            >
              <BookOpen className="w-4 h-4" />
              View Full Documentation
            </a>
          </div>
        )}
      </div>

      {/* ERROR ALERT */}
      {error && (
        <div className="max-w-7xl mx-auto mb-6 bg-red-500/20 border border-red-500/50 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* CONTROL PANEL */}
      <div className="max-w-7xl mx-auto mb-8 bg-slate-900/50 border border-slate-700 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Radio className="w-5 h-5 text-cyan-400" />
            SESSION CONTROL
          </h2>
        </div>

        <div className="flex gap-3 flex-wrap">
          {!sessionId ? (
            <button
              onClick={startSession}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white rounded-lg font-bold transition-all flex items-center gap-2"
            >
              <Play className="w-5 h-5" />
              START SESSION
            </button>
          ) : (
            <>
              <button
                onClick={() => setIsPaused(!isPaused)}
                className="px-6 py-3 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-bold transition-all flex items-center gap-2"
              >
                {isPaused ? <Play className="w-5 h-5" /> : <Pause className="w-5 h-5" />}
                {isPaused ? 'RESUME' : 'PAUSE'}
              </button>

              <button
                onClick={stopSession}
                className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-bold transition-all flex items-center gap-2"
              >
                STOP SESSION
              </button>

              <button
                onClick={() => window.location.href = `${API_BASE}/session/${sessionId}/export?format=pdf`}
                className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-bold transition-all flex items-center gap-2"
              >
                <Download className="w-5 h-5" />
                EXPORT PDF
              </button>
            </>
          )}
        </div>
      </div>

      {/* MAIN CONTENT */}
      {sessionId && metrics ? (
        <div className="max-w-7xl mx-auto grid grid-cols-12 gap-6">

          {/* LEFT COLUMN - LIVE DATA */}
          <div className="col-span-8 space-y-6">

            {/* LIVE EEG CHANNELS */}
            <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-green-400" />
                LIVE EEG CHANNELS
              </h3>

              <div className="grid grid-cols-4 gap-4">
                {selectedChannels.map((ch) => (
                  <div key={ch} className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-bold text-white text-sm">{ch}</div>
                      <div className="signal-wave text-blue-400 font-bold">◄ ► ◄</div>
                    </div>
                    <div className="text-2xl font-bold text-cyan-400">
                      {typeof channelData[ch] === 'number' ? Math.abs(Math.round(channelData[ch] * 100) / 100) : '—'}
                    </div>
                    <div className="text-xs text-slate-400 mt-1">μV</div>
                  </div>
                ))}
              </div>

              <div className="mt-4 text-xs text-slate-400">
                {selectedChannels.length} channels × {metrics.sample_rate} Hz = {(selectedChannels.length * metrics.sample_rate).toLocaleString()} samples/sec
              </div>
            </div>

            {/* BRAINWAVE ANALYSIS */}
            <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                BRAINWAVE DISTRIBUTION
              </h3>

              <div className="space-y-3">
                {[
                  { band: 'ALPHA', freq: '8-12 Hz', percent: getBandPercent('alpha'), color: 'from-green-600 to-green-400' },
                  { band: 'BETA', freq: '15-30 Hz', percent: getBandPercent('beta'), color: 'from-orange-600 to-orange-400' },
                  { band: 'THETA', freq: '4-8 Hz', percent: getBandPercent('theta'), color: 'from-blue-600 to-blue-400' },
                  { band: 'DELTA', freq: '0.5-4 Hz', percent: getBandPercent('delta'), color: 'from-purple-600 to-purple-400' },
                  { band: 'GAMMA', freq: '30-100 Hz', percent: getBandPercent('gamma'), color: 'from-red-600 to-red-400' },
                ].map((b) => (
                  <div key={b.band} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <div>
                        <span className="font-bold text-white">{b.band}</span>
                        <span className="text-slate-400 ml-2">{b.freq}</span>
                      </div>
                      <span className="font-bold text-white">{b.percent}%</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full bg-gradient-to-r ${b.color} transition-all`}
                        style={{ width: `${b.percent}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded text-blue-300 text-sm">
                ✓ Dominant Band: <strong>{metrics.dominant_band.toUpperCase()}</strong> at {metrics.dominant_band_power}% power
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN - ANALYSIS & DIAGNOSTICS */}
          <div className="col-span-4 space-y-6">

            {/* QUALITY SCORE */}
            <div className={`border rounded-lg p-6 ${getQualityBg(metrics.quality_score)}`}>
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Check className="w-5 h-5" />
                DATA QUALITY
              </h3>
              <div className="text-center">
                <div className={`text-5xl font-black ${getQualityColor(metrics.quality_score)}`}>
                  {Math.round(metrics.quality_score)}%
                </div>
                <div className="text-sm text-slate-300 mt-2">
                  {metrics.quality_score >= 90 ? 'Excellent Signal' :
                   metrics.quality_score >= 75 ? 'Good Signal' : 'Check Electrodes'}
                </div>
              </div>
            </div>

            {/* HEMISPHERIC BALANCE */}
            <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Brain className="w-5 h-5 text-cyan-400" />
                HEMISPHERIC BALANCE
              </h3>

              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-300">Left Hemisphere</span>
                    <span className="font-bold text-white">{metrics.hemispheric_balance.left_power_percent}%</span>
                  </div>
                  <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-600 to-blue-400"
                      style={{ width: `${metrics.hemispheric_balance.left_power_percent}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-300">Right Hemisphere</span>
                    <span className="font-bold text-white">{metrics.hemispheric_balance.right_power_percent}%</span>
                  </div>
                  <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-orange-600 to-orange-400"
                      style={{ width: `${metrics.hemispheric_balance.right_power_percent}%` }}
                    />
                  </div>
                </div>

                <div className="mt-4 p-3 bg-slate-800/50 rounded text-xs text-slate-300 border border-slate-700">
                  <strong className="text-slate-200">Asymmetry:</strong> {metrics.hemispheric_balance.asymmetry.toUpperCase()}
                  <br />
                  <strong className="text-slate-200">Analysis:</strong> {metrics.hemispheric_balance.interpretation}
                </div>
              </div>
            </div>

            {/* SESSION INFO */}
            <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-6 text-sm">
              <h3 className="font-bold text-white mb-3">SESSION INFO</h3>
              <div className="space-y-2 text-slate-300">
                <div className="flex justify-between">
                  <span>Samples:</span>
                  <span className="text-white font-bold">{metrics.samples_received.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Sample Rate:</span>
                  <span className="text-white font-bold">{metrics.sample_rate} Hz</span>
                </div>
                <div className="flex justify-between">
                  <span>Anomalies:</span>
                  <span className={metrics.anomalies_detected === 0 ? 'text-green-400' : 'text-yellow-400'}>
                    {metrics.anomalies_detected}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>State:</span>
                  <span className="text-cyan-400 font-bold">{metrics.state_interpretation}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="max-w-7xl mx-auto text-center py-20">
          <Brain className="w-20 h-20 text-slate-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-400 mb-2">Ready to Begin</h2>
          <p className="text-slate-500 mb-6">Click START SESSION to initialize the EEG analyzer</p>
          <button
            onClick={startSession}
            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white rounded-lg font-bold text-lg transition-all"
          >
            START SESSION
          </button>
        </div>
      )}
    </div>
  );
}
