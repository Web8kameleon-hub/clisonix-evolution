'use client';

import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { Music, Radio, Zap, Settings, BookOpen, Play, Pause, Square, Download, Plus, Volume2, Waves, AlertCircle, Check } from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════
// TYPE DEFINITIONS
// ═══════════════════════════════════════════════════════════════════

interface BrainwaveBand {
  name: string;
  frequency_range: [number, number];
  power_percent: number;
  interpretation: string;
}

interface SynthesisMetrics {
  session_id: string;
  state: 'idle' | 'synthesizing' | 'paused' | 'completed';
  duration_seconds: number;
  signals_processed: number;
  audio_files_generated: number;
  current_frequency: number;
  current_waveform: string;
  quality_score: number;
  dominant_band: string;
  thd_percent: number;
  uptime_seconds: number;
  brainwave_bands: BrainwaveBand[];
}

interface AudioFile {
  id: string;
  filename: string;
  preset_used: string;
  duration_seconds: number;
  file_size_kb: number;
  format: string;
  created_at: string;
}

// ═══════════════════════════════════════════════════════════════════
// PROFESSIONAL JONA NEURAL SYNTHESIS COMPONENT
// ═══════════════════════════════════════════════════════════════════

export default function JonaNeuralSynthesis() {
  // State Management
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [metrics, setMetrics] = useState<SynthesisMetrics | null>(null);
  const [audioLibrary, setAudioLibrary] = useState<AudioFile[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSettingsDoc, setShowSettingsDoc] = useState(false);

  // Audio Control State
  const [targetFrequency, setTargetFrequency] = useState(20.0);
  const [waveformType, setWaveformType] = useState<'sine' | 'binaural' | 'isochronic' | 'pink_noise'>('sine');
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null);
  const [volume, setVolume] = useState(75);

  // WebSocket ref
  const wsRef = useRef<WebSocket | null>(null);
  const metricsIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // API Base URL
  const API_BASE = 'http://127.0.0.1:7777';

  // Therapeutic Presets
  const PRESETS = [
    { id: 'deep-sleep', name: 'Deep Sleep', frequency: 2.5, waveform: 'isochronic' },
    { id: 'meditation', name: 'Meditation', frequency: 6.0, waveform: 'binaural' },
    { id: 'relaxation', name: 'Relaxation', frequency: 10.0, waveform: 'sine' },
    { id: 'focus', name: 'Focus', frequency: 14.0, waveform: 'isochronic' },
    { id: 'alertness', name: 'Alertness', frequency: 20.0, waveform: 'binaural' },
    { id: 'cognition', name: 'Cognition', frequency: 40.0, waveform: 'isochronic' },
  ];

  // ═══════════════════════════════════════════════════════════════════
  // SESSION MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════

  const startSynthesis = useCallback(async () => {
    try {
      setError(null);

      // First check if API is running
      try {
        const healthResponse = await fetch(`${API_BASE}/health`, {
          signal: AbortSignal.timeout(2000)
        });
        if (!healthResponse.ok) {
          throw new Error('API not ready');
        }
      } catch (healthErr) {
        throw new Error(`JONA API is not running on port 7777. Please start the backend service first.`);
      }

      const response = await fetch(`${API_BASE}/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'user_' + Math.random().toString(36).substr(2, 9),
          target_frequency: targetFrequency,
          waveform_type: waveformType,
          preset_id: selectedPreset,
          volume: volume
        }),
        signal: AbortSignal.timeout(5000)
      });

      // Check content type before parsing
      const contentType = response.headers.get('content-type');
      if (!contentType?.includes('application/json')) {
        const text = await response.text();
        throw new Error(`API returned non-JSON response: ${text.substring(0, 100)}`);
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Failed to start synthesis');
      }

      setSessionId(data.session_id);
      setIsSynthesizing(true);
      setMetrics(null);

      // Connect WebSocket
      connectWebSocket(data.session_id);

      // Start polling metrics
      startMetricsPolling(data.session_id);

    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to start synthesis';
      setError(message);
      console.error('Start synthesis error:', err);
    }
  }, [targetFrequency, waveformType, selectedPreset, volume]);

  const stopSynthesis = useCallback(async () => {
    if (!sessionId) return;

    try {
      await fetch(`${API_BASE}/session/${sessionId}/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      setSessionId(null);
      setIsSynthesizing(false);
      setIsPaused(false);

      // Disconnect WebSocket
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      if (metricsIntervalRef.current) {
        clearInterval(metricsIntervalRef.current);
      }

    } catch (err) {
      console.error('Stop synthesis error:', err);
    }
  }, [sessionId]);

  const connectWebSocket = (sid: string) => {
    try {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const wsUrl = `${wsProtocol}://127.0.0.1:7777/stream/${sid}`;

      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('✓ WebSocket connected');
        setIsConnected(true);
      };

      wsRef.current.onmessage = (event) => {
        try {
          // Ensure we have valid data
          if (!event.data || event.data.trim() === '') {
            return;
          }
          const data = JSON.parse(event.data);
          // Process real-time synthesis data
          console.log('Synthesis data:', data);
        } catch (e) {
          // Silently ignore JSON parse errors from WebSocket
          console.debug('WebSocket data parse note:', e instanceof Error ? e.message : 'Unknown error');
        }
      };

      wsRef.current.onerror = (event) => {
        console.error('WebSocket error:', event);
        setIsConnected(false);
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket closed');
        setIsConnected(false);
      };
    } catch (err) {
      console.error('WebSocket connection error:', err);
      setIsConnected(false);
    }
  };

  const startMetricsPolling = (sid: string) => {
    metricsIntervalRef.current = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE}/session/${sid}/metrics`, {
          signal: AbortSignal.timeout(3000)
        });

        if (response.ok) {
          const contentType = response.headers.get('content-type');
          if (contentType?.includes('application/json')) {
            const data = await response.json();
            setMetrics(data);
            setError(null);
          } else {
            console.warn('Metrics response is not JSON');
          }
        } else if (response.status === 404) {
          // Session ended
          clearInterval(metricsIntervalRef.current!);
        }
      } catch (err) {
        // Network errors during polling are acceptable, don't display them
        console.debug('Metrics polling interval error:', err instanceof Error ? err.message : 'Unknown error');
      }
    }, 1000);
  };

  // Check API availability on mount
  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        const response = await fetch(`${API_BASE}/health`, {
          signal: AbortSignal.timeout(3000)
        });
        if (response.ok) {
          setError(null);
        } else {
          setError('JONA API health check failed');
        }
      } catch (err) {
        setError('JONA Neural API is not running. Start the backend service: python jona_neural_api.py');
      }
    };

    checkApiHealth();
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
  // HELPER FUNCTIONS
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

  const getWaveformIcon = (type: string) => {
    const icons: Record<string, string> = {
      sine: '∿',
      binaural: '◐◑',
      isochronic: '▮▯▮',
      pink_noise: '▒▓▒'
    };
    return icons[type] || '◐◑';
  };

  // ═══════════════════════════════════════════════════════════════════
  // RENDER UI
  // ═══════════════════════════════════════════════════════════════════

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-950 p-6 font-mono">
      <style>{`
        @keyframes pulse-ring {
          0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7); }
          70% { box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); }
          100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
        }
        .pulse-ring {
          animation: pulse-ring 2s infinite;
        }
        @keyframes frequency-pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
        .frequency-pulse {
          animation: frequency-pulse 1s ease-in-out infinite;
        }
      `}</style>

      {/* HEADER */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center gap-4 mb-2">
          <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg pulse-ring">
            <Music className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-black bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              JONA Neural Synthesis
            </h1>
            <p className="text-slate-400 text-sm mt-1">🎵 Professional Brainwave Entrainment • Therapeutic Audio Synthesis</p>
          </div>
        </div>

        {/* STATUS BAR */}
        <div className="grid grid-cols-5 gap-3 mt-6">
          <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-3">
            <div className="text-xs text-slate-400 mb-1">SYNTHESIS STATUS</div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isSynthesizing ? 'bg-red-500 pulse-ring' : 'bg-slate-600'}`}></div>
              <div className="text-white font-bold">{isSynthesizing ? 'ACTIVE' : 'STANDBY'}</div>
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
            <div className="text-xs text-slate-400 mb-1">FREQUENCY</div>
            <div className="text-white font-bold text-lg frequency-pulse">{targetFrequency.toFixed(1)} Hz</div>
          </div>

          <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-3">
            <div className="text-xs text-slate-400 mb-1">WAVEFORM</div>
            <div className="text-white font-bold text-lg">{getWaveformIcon(waveformType)}</div>
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
                  JONA Neural Synthesis Settings Guide
                </h3>
                <p className="text-purple-200 text-sm mb-3">
                  Professional configuration for advanced audio synthesis and brainwave entrainment.
                </p>
                <div className="text-xs text-purple-300 space-y-1 mb-3">
                  <p>✓ 6-tab interface (Audio, Waveform, Neural, Presets, Metrics, Files)</p>
                  <p>✓ Real-time synthesis parameter tuning</p>
                  <p>✓ Custom preset creation and management</p>
                  <p>✓ Professional audio quality monitoring</p>
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
              href="/jona-settings-documentation"
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
            <Radio className="w-5 h-5 text-indigo-400" />
            SYNTHESIS CONTROL
          </h2>
        </div>

        <div className="flex gap-3 flex-wrap mb-6">
          {!sessionId ? (
            <button
              onClick={startSynthesis}
              className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-lg font-bold transition-all flex items-center gap-2"
            >
              <Play className="w-5 h-5" />
              START SYNTHESIS
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
                onClick={stopSynthesis}
                className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-bold transition-all flex items-center gap-2"
              >
                <Square className="w-5 h-5" />
                STOP
              </button>

              <button
                onClick={() => window.location.href = `${API_BASE}/session/${sessionId}/export?format=wav`}
                className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-bold transition-all flex items-center gap-2"
              >
                <Download className="w-5 h-5" />
                EXPORT WAV
              </button>
            </>
          )}
        </div>

        {/* FREQUENCY CONTROL */}
        <div className="space-y-3">
          <div>
            <label className="text-sm text-slate-300 font-bold mb-2 block">Target Frequency: {targetFrequency.toFixed(1)} Hz</label>
            <input
              type="range"
              min="0.5"
              max="50"
              step="0.5"
              value={targetFrequency}
              onChange={(e) => setTargetFrequency(parseFloat(e.target.value))}
              disabled={isSynthesizing}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-slate-400 mt-1">
              <span>0.5 Hz (Delta)</span>
              <span>50 Hz (Gamma)</span>
            </div>
          </div>

          {/* VOLUME CONTROL */}
          <div className="flex items-center gap-4">
            <label className="text-sm text-slate-300 font-bold">Volume:</label>
            <div className="flex items-center gap-2 flex-1">
              <Volume2 className="w-4 h-4 text-slate-400" />
              <input
                type="range"
                min="0"
                max="100"
                value={volume}
                onChange={(e) => setVolume(parseInt(e.target.value))}
                className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-sm text-white font-bold w-12 text-right">{volume}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      {sessionId && metrics ? (
        <div className="max-w-7xl mx-auto grid grid-cols-12 gap-6">

          {/* LEFT COLUMN - SYNTHESIS DATA */}
          <div className="col-span-8 space-y-6">

            {/* PRESETS */}
            <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-amber-400" />
                THERAPEUTIC PRESETS
              </h3>

              <div className="grid grid-cols-3 gap-3">
                {PRESETS.map((preset) => (
                  <button
                    key={preset.id}
                    onClick={() => {
                      setSelectedPreset(preset.id);
                      setTargetFrequency(preset.frequency);
                      setWaveformType(preset.waveform as any);
                    }}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      selectedPreset === preset.id
                        ? 'border-indigo-500 bg-indigo-900/30'
                        : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                    }`}
                  >
                    <div className="font-bold text-white mb-1">{preset.name}</div>
                    <div className="text-sm text-slate-300">{preset.frequency} Hz</div>
                  </button>
                ))}
              </div>
            </div>

            {/* WAVEFORM SELECTION */}
            <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Waves className="w-5 h-5 text-cyan-400" />
                WAVEFORM TYPE
              </h3>

              <div className="grid grid-cols-2 gap-4">
                {[
                  { type: 'sine', icon: '∿', name: 'Sine Wave', desc: 'Smooth, pure tone' },
                  { type: 'binaural', icon: '◐◑', name: 'Binaural Beats', desc: 'Stereo frequency difference' },
                  { type: 'isochronic', icon: '▮▯▮', name: 'Isochronic Tones', desc: 'Pulsing single tone' },
                  { type: 'pink_noise', icon: '▒▓▒', name: 'Pink Noise', desc: 'Natural ambient sound' }
                ].map((wave) => (
                  <button
                    key={wave.type}
                    onClick={() => setWaveformType(wave.type as any)}
                    disabled={isSynthesizing}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      waveformType === wave.type
                        ? 'border-indigo-500 bg-indigo-900/30'
                        : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                    } disabled:opacity-50`}
                  >
                    <div className="text-2xl mb-2">{wave.icon}</div>
                    <div className="font-bold text-white text-sm">{wave.name}</div>
                    <div className="text-xs text-slate-400">{wave.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* BRAINWAVE ANALYSIS */}
            <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Radio className="w-5 h-5 text-pink-400" />
                BRAINWAVE BANDS
              </h3>

              <div className="space-y-3">
                {metrics.brainwave_bands.map((band) => (
                  <div key={band.name} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <div>
                        <span className="font-bold text-white">{band.name}</span>
                        <span className="text-slate-400 ml-2">({band.frequency_range[0]}-{band.frequency_range[1]} Hz)</span>
                      </div>
                      <span className="font-bold text-white">{band.power_percent}%</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-600 to-purple-400 transition-all"
                        style={{ width: `${band.power_percent}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-4 p-3 bg-indigo-500/10 border border-indigo-500/30 rounded text-indigo-300 text-sm">
                ✓ Dominant Band: <strong>{metrics.dominant_band.toUpperCase()}</strong> at {metrics.quality_score}% purity
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN - DIAGNOSTICS */}
          <div className="col-span-4 space-y-6">

            {/* SYNTHESIS QUALITY */}
            <div className={`border rounded-lg p-6 ${getQualityBg(metrics.quality_score)}`}>
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Check className="w-5 h-5" />
                SYNTHESIS QUALITY
              </h3>
              <div className="text-center">
                <div className={`text-5xl font-black ${getQualityColor(metrics.quality_score)}`}>
                  {Math.round(metrics.quality_score)}%
                </div>
                <div className="text-sm text-slate-300 mt-2">
                  {metrics.quality_score >= 90 ? 'Professional Grade' :
                   metrics.quality_score >= 75 ? 'High Quality' : 'Check Parameters'}
                </div>
              </div>
            </div>

            {/* PROCESSING METRICS */}
            <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-3">PROCESSING METRICS</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-300">Signals Processed:</span>
                  <span className="text-white font-bold">{metrics.signals_processed.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-300">Audio Files:</span>
                  <span className="text-white font-bold">{metrics.audio_files_generated}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-300">Duration:</span>
                  <span className="text-white font-bold">{Math.floor(metrics.duration_seconds / 60)}m {metrics.duration_seconds % 60}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-300">THD:</span>
                  <span className={`font-bold ${metrics.thd_percent < 5 ? 'text-green-400' : metrics.thd_percent < 10 ? 'text-yellow-400' : 'text-red-400'}`}>
                    {metrics.thd_percent.toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>

            {/* SESSION INFO */}
            <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-6 text-sm">
              <h3 className="font-bold text-white mb-3">SESSION INFO</h3>
              <div className="space-y-2 text-slate-300">
                <div className="flex justify-between">
                  <span>Session ID:</span>
                  <span className="text-white font-bold text-xs">{sessionId.substring(0, 12)}...</span>
                </div>
                <div className="flex justify-between">
                  <span>State:</span>
                  <span className="text-indigo-400 font-bold">{metrics.state.toUpperCase()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Uptime:</span>
                  <span className="text-white font-bold">{Math.floor(metrics.uptime_seconds / 60)}m {metrics.uptime_seconds % 60}s</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="max-w-7xl mx-auto text-center py-20">
          <Music className="w-20 h-20 text-slate-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-400 mb-2">Ready to Synthesize</h2>
          <p className="text-slate-500 mb-6">Click START SYNTHESIS to begin professional audio neural entrainment</p>
          <button
            onClick={startSynthesis}
            className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-lg font-bold text-lg transition-all"
          >
            START SYNTHESIS
          </button>
        </div>
      )}
    </div>
  );
}
