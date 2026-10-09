'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  Play,
  Square,
  Upload,
  Settings,
  Wifi,
  WifiOff,
  Volume2,
  Music,
  Brain,
  Waves,
  Zap,
  Clock,
  FileAudio,
  Trash2,
  Download,
  RefreshCw,
  Activity,
  Sliders
} from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================
interface FrequencyBand {
  name: string;
  range: string;
  power: number;
  color: string;
  description: string;
}

interface AudioFile {
  file_id: string;
  filename: string;
  format: string;
  duration_ms: number;
  sample_rate: number;
  channels: number;
  size_bytes: number;
  created_at: string;
  neural_frequency: number;
  waveform_type: string;
}

function normalizeAudioFiles(input: unknown): AudioFile[] {
  if (!Array.isArray(input)) return [];

  const byFileId = new Map<string, AudioFile & { _quality: number }>();
  const byFilename = new Map<string, AudioFile & { _quality: number }>();

  const toPositiveInt = (value: unknown): number => {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) return 0;
    return Math.max(0, Math.trunc(parsed));
  };

  const toPositiveFloat = (value: unknown): number => {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) return 0;
    return Math.max(0, parsed);
  };

  for (const row of input) {
    if (!row || typeof row !== 'object') continue;
    const source = row as Record<string, unknown>;

    const fileId = String(source.file_id ?? '').trim();
    const filename = String(source.filename ?? '').trim();
    if (!fileId || !filename) continue;

    const waveformType = String(source.waveform_type ?? '').trim().toLowerCase() || 'unknown';

    const item: AudioFile & { _quality: number } = {
      file_id: fileId,
      filename,
      format: String(source.format ?? 'wav').trim() || 'wav',
      duration_ms: toPositiveInt(source.duration_ms),
      sample_rate: toPositiveInt(source.sample_rate),
      channels: Math.max(1, toPositiveInt(source.channels || 1)),
      size_bytes: toPositiveInt(source.size_bytes),
      created_at: String(source.created_at ?? ''),
      neural_frequency: toPositiveFloat(source.neural_frequency),
      waveform_type: waveformType,
      _quality: 0,
    };

    const hasValidDuration = item.duration_ms > 0;
    const hasValidFrequency = item.neural_frequency > 0;
    const hasKnownWaveform = !['', 'unknown', 'none', 'null'].includes(item.waveform_type);
    item._quality = Number(hasValidDuration) + Number(hasValidFrequency) + Number(hasKnownWaveform);

    const existingById = byFileId.get(item.file_id);
    if (!existingById || item._quality > existingById._quality) {
      byFileId.set(item.file_id, item);
    }
  }

  for (const item of byFileId.values()) {
    const key = item.filename.toLowerCase();
    const existing = byFilename.get(key);
    if (!existing || item._quality > existing._quality) {
      byFilename.set(key, item);
    }
  }

  return Array.from(byFilename.values())
    .map(({ _quality, ...cleaned }) => cleaned)
    .sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
}

// ============================================================================
// CONSTANTS
// ============================================================================
const WAVEFORM_TYPES = [
  { id: 'sine', name: 'Sine Wave', icon: '∿', description: 'Smooth, pure tone' },
  { id: 'binaural', name: 'Binaural Beats', icon: '◐◑', description: 'Stereo frequency difference' },
  { id: 'isochronic', name: 'Isochronic Tones', icon: '▮▯▮', description: 'Pulsing single tone' },
  { id: 'pink_noise', name: 'Pink Noise', icon: '▒▓▒', description: 'Natural ambient sound' }
];

const PRESET_FREQUENCIES = [
  { hz: 2.5, name: 'Deep Sleep', band: 'Delta', color: '#8B5CF6' },
  { hz: 6.0, name: 'Meditation', band: 'Theta', color: '#F59E0B' },
  { hz: 10.0, name: 'Relaxation', band: 'Alpha', color: '#3B82F6' },
  { hz: 14.0, name: 'Focus', band: 'Low Beta', color: '#10B981' },
  { hz: 20.0, name: 'Alertness', band: 'Beta', color: '#06B6D4' },
  { hz: 40.0, name: 'Cognition', band: 'Gamma', color: '#EC4899' }
];

// ============================================================================
// API Functions
// ============================================================================
const API_BASE = '/api/jona';

async function fetchAPI(endpoint: string, options?: RequestInit) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers
      }
    });

    const contentType = res.headers.get('content-type') || '';
    if (!res.ok) {
      const errorPayload = contentType.includes('application/json') ? await res.json().catch(() => null) : null;
      return {
        success: false,
        status: 'error',
        http_status: res.status,
        redirected: res.redirected,
        final_url: res.url,
        error: errorPayload?.error || `HTTP ${res.status}`,
      };
    }

    if (!contentType.includes('application/json')) {
      return {
        success: false,
        status: 'error',
        redirected: res.redirected,
        final_url: res.url,
        error: 'Unexpected non-JSON response from JONA API',
      };
    }

    return await res.json();
  } catch (error) {
    console.error('API Error:', error);
    return { success: false, error: 'Connection failed' };
  }
}

// ============================================================================
// COMPONENTS
// ============================================================================

// Header Component
const Header = ({
  isConnected,
  isSynthesizing,
  onStartStop,
  onExport,
  sessionName,
  elapsedTime
}: {
  isConnected: boolean;
  isSynthesizing: boolean;
  onStartStop: () => void;
  onExport: () => void;
  sessionName: string;
  elapsedTime: number;
}) => (
  <div className="bg-white border-b border-slate-200 px-6 py-4">
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center shadow-lg">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-slate-800">JONA</h1>
            <p className="text-xs text-slate-500">Neural Synthesis</p>
          </div>
        </div>

        {isSynthesizing && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-orange-100 rounded-lg">
            <div className="w-2 h-2 rounded-full bg-orange-500 animate-pulse" />
            <span className="text-sm font-medium text-orange-700">{sessionName}</span>
            <span className="text-sm text-orange-600">{formatTime(elapsedTime)}</span>
          </div>
        )}

        {/* Connection Status */}
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${isConnected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {isConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
          <span className="text-sm font-medium">{isConnected ? 'Connected' : 'Offline'}</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-3">
        <button
          onClick={onStartStop}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium transition-all ${
            isSynthesizing
              ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/30'
              : 'bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-400 hover:to-orange-400 text-white shadow-lg shadow-orange-500/30'
          }`}
        >
          {isSynthesizing ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          {isSynthesizing ? 'Stop Synthesis' : 'Start Synthesis'}
        </button>

        <button
          onClick={onExport}
          className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 font-medium transition-colors"
        >
          <Upload className="w-4 h-4" />
          Export
        </button>

        <button className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors">
          <Settings className="w-5 h-5" />
        </button>
      </div>
    </div>
  </div>
);

// Format time helper
const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

// Format bytes helper
const formatBytes = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

// Waveform Visualizer Component
const WaveformVisualizer = ({ isActive, frequency }: { isActive: boolean; frequency: number }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>(0);
  const phaseRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const draw = () => {
      const width = canvas.width;
      const height = canvas.height;
      const centerY = height / 2;

      ctx.fillStyle = '#f8fafc';
      ctx.fillRect(0, 0, width, height);

      // Draw grid lines
      ctx.strokeStyle = '#e2e8f0';
      ctx.lineWidth = 1;
      for (let i = 0; i <= 4; i++) {
        const y = (height / 4) * i;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      if (isActive) {
        // Draw main waveform
        const gradient = ctx.createLinearGradient(0, 0, width, 0);
        gradient.addColorStop(0, '#f59e0b');
        gradient.addColorStop(0.5, '#f97316');
        gradient.addColorStop(1, '#ea580c');

        ctx.strokeStyle = gradient;
        ctx.lineWidth = 2;
        ctx.beginPath();

        for (let x = 0; x < width; x++) {
          const normalizedX = x / width;
          const baseWave = Math.sin((normalizedX * frequency * 2 + phaseRef.current) * Math.PI);
          const modulation = Math.sin((normalizedX * 3 + phaseRef.current * 0.5) * Math.PI) * 0.3;
          const noise = (Math.random() - 0.5) * 0.1;
          const y = centerY + (baseWave + modulation + noise) * (height * 0.35);

          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();

        // Draw secondary harmonics
        ctx.strokeStyle = 'rgba(249, 115, 22, 0.3)';
        ctx.lineWidth = 1;
        ctx.beginPath();

        for (let x = 0; x < width; x++) {
          const normalizedX = x / width;
          const wave = Math.sin((normalizedX * frequency * 4 + phaseRef.current * 1.5) * Math.PI);
          const y = centerY + wave * (height * 0.2);

          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();

        phaseRef.current += 0.05;
      } else {
        // Draw flat line when inactive
        ctx.strokeStyle = '#cbd5e1';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, centerY);
        ctx.lineTo(width, centerY);
        ctx.stroke();
      }

      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => cancelAnimationFrame(animationRef.current);
  }, [isActive, frequency]);

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
          <Waves className="w-5 h-5 text-orange-500" />
          Neural Waveform
        </h2>
        {isActive && (
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-slate-500">Synthesizing at {frequency} Hz</span>
          </div>
        )}
      </div>
      <canvas
        ref={canvasRef}
        width={600}
        height={150}
        className="w-full rounded-lg"
      />
    </div>
  );
};

// Frequency Control Panel
const FrequencyControl = ({
  frequency,
  setFrequency,
  waveform,
  setWaveform,
  isActive
}: {
  frequency: number;
  setFrequency: (f: number) => void;
  waveform: string;
  setWaveform: (w: string) => void;
  isActive: boolean;
}) => (
  <div className="bg-white rounded-xl border border-slate-200 p-5">
    <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2 mb-4">
      <Sliders className="w-5 h-5 text-purple-500" />
      Frequency Control
    </h2>

    {/* Main Frequency Slider */}
    <div className="mb-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-slate-600">Target Frequency</span>
        <span className="text-2xl font-bold text-orange-600">{(Number(frequency ?? 0)).toFixed(1)} Hz</span>
      </div>
      <input
        type="range"
        min="0.5"
        max="50"
        step="0.5"
        value={frequency}
        onChange={(e) => setFrequency(parseFloat(e.target.value))}
        disabled={isActive}
        className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-orange-500 disabled:opacity-50"
      />
      <div className="flex justify-between text-xs text-slate-400 mt-1">
        <span>0.5 Hz (Delta)</span>
        <span>50 Hz (Gamma)</span>
      </div>
    </div>

    {/* Preset Frequencies */}
    <div className="mb-6">
      <span className="text-sm font-medium text-slate-600 block mb-2">Presets</span>
      <div className="grid grid-cols-3 gap-2">
        {PRESET_FREQUENCIES.map(preset => (
          <button
            key={preset.hz}
            onClick={() => !isActive && setFrequency(preset.hz)}
            disabled={isActive}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-all border ${
              Math.abs(frequency - preset.hz) < 0.5
                ? 'border-orange-400 bg-orange-50 text-orange-700'
                : 'border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100'
            } disabled:opacity-50`}
          >
            <div className="font-semibold">{preset.name}</div>
            <div className="text-xs opacity-70">{preset.hz} Hz</div>
          </button>
        ))}
      </div>
    </div>

    {/* Waveform Type */}
    <div>
      <span className="text-sm font-medium text-slate-600 block mb-2">Waveform Type</span>
      <div className="grid grid-cols-2 gap-2">
        {WAVEFORM_TYPES.map(type => (
          <button
            key={type.id}
            onClick={() => !isActive && setWaveform(type.id)}
            disabled={isActive}
            className={`p-3 rounded-lg text-left transition-all border ${
              waveform === type.id
                ? 'border-orange-400 bg-orange-50'
                : 'border-slate-200 bg-slate-50 hover:bg-slate-100'
            } disabled:opacity-50`}
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg">{type.icon}</span>
              <span className="font-medium text-slate-700">{type.name}</span>
            </div>
            <p className="text-xs text-slate-500">{type.description}</p>
          </button>
        ))}
      </div>
    </div>
  </div>
);

// Frequency Bands Display
const FrequencyBands = ({ bands }: { bands: FrequencyBand[] }) => (
  <div className="bg-white rounded-xl border border-slate-200 p-5">
    <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2 mb-4">
      <Brain className="w-5 h-5 text-blue-500" />
      Brainwave Bands
    </h2>

    <div className="space-y-3">
      {bands.map(band => (
        <div key={band.name} className="space-y-1">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: band.color }} />
              <span className="text-sm font-medium text-slate-700">{band.name}</span>
              <span className="text-xs text-slate-400">({band.range})</span>
            </div>
            <span className="text-sm font-semibold text-slate-800">{(Number(band.power ?? 0)).toFixed(0)}%</span>
          </div>
          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${band.power}%`, backgroundColor: band.color }}
            />
          </div>
        </div>
      ))}
    </div>

    {(() => {
      const strongest = bands.length
        ? [...bands].sort((a, b) => Number(b.power ?? 0) - Number(a.power ?? 0))[0]
        : null
      const dominantDescription = strongest?.description || 'Waiting for live neural metrics'

      return (
        <div className="mt-4 p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-100">
          <div className="text-sm text-slate-600">Dominant Band</div>
          <div className="text-lg font-bold text-blue-700">{strongest?.name || 'N/A'}</div>
          <div className="text-sm text-slate-500">{dominantDescription}</div>
        </div>
      )
    })()}
  </div>
);

// Audio Library Panel
const AudioLibrary = ({
  files,
  onRefresh,
  onDelete,
  onPlay,
  onDownload,
  playingId
}: {
  files: AudioFile[];
  onRefresh: () => void;
  onDelete: (id: string) => void;
  onPlay: (id: string) => void;
  onDownload: (id: string) => void;
  playingId: string | null;
}) => (
  <div className="bg-white rounded-xl border border-slate-200 p-5">
    <div className="flex items-center justify-between mb-4">
      <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
        <Music className="w-5 h-5 text-green-500" />
        Audio Library
      </h2>
      <button
        onClick={onRefresh}
        className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors"
      >
        <RefreshCw className="w-4 h-4" />
      </button>
    </div>

    {files.length === 0 ? (
      <div className="text-center py-8 text-slate-400">
        <FileAudio className="w-12 h-12 mx-auto mb-2 opacity-50" />
        <p>No audio files yet</p>
        <p className="text-sm">Start synthesizing to create audio</p>
      </div>
    ) : (
      <div className="space-y-2 max-h-[300px] overflow-y-auto">
        {files.map(file => (
          <div
            key={file.file_id}
            className={`p-3 rounded-lg border transition-all ${
              playingId === file.file_id
                ? 'border-green-400 bg-green-50'
                : 'border-slate-100 bg-slate-50 hover:bg-slate-100'
            }`}
          >
            <div className="flex items-center gap-3">
              <button
                onClick={() => onPlay(file.file_id)}
                className={`p-2 rounded-full transition-colors ${
                  playingId === file.file_id
                    ? 'bg-green-500 text-white'
                    : 'bg-slate-200 text-slate-600 hover:bg-slate-300'
                }`}
              >
                {playingId === file.file_id ? <Volume2 className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </button>

              <div className="flex-1 min-w-0">
                <div className="font-medium text-slate-700 truncate">{file.filename}</div>
                <div className="flex items-center gap-3 text-xs text-slate-500">
                  <span>{formatTime(file.duration_ms / 1000)}</span>
                  <span>{(Number(file.neural_frequency ?? 0)).toFixed(1)} Hz</span>
                  <span>{file.waveform_type}</span>
                  <span>{formatBytes(file.size_bytes)}</span>
                </div>
              </div>

              <div className="flex items-center gap-1">
                <button
                  onClick={() => onDownload(file.file_id)}
                  className="p-1.5 hover:bg-slate-200 rounded text-slate-400 hover:text-slate-600"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button
                  onClick={() => onDelete(file.file_id)}
                  className="p-1.5 hover:bg-red-100 rounded text-slate-400 hover:text-red-500"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    )}

    {files.length > 0 && (
      <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-sm text-slate-500">
        <span>{files.length} files</span>
        <span>Total: {formatBytes(files.reduce((sum, f) => sum + f.size_bytes, 0))}</span>
      </div>
    )}
  </div>
);

// Synthesis Stats
const SynthesisStats = ({ stats }: { stats: { signals: number; files: number; uptime: number } }) => (
  <div className="grid grid-cols-3 gap-4">
    <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
      <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-blue-100 flex items-center justify-center">
        <Activity className="w-5 h-5 text-blue-600" />
      </div>
      <div className="text-2xl font-bold text-slate-800">{stats.signals.toLocaleString()}</div>
      <div className="text-sm text-slate-500">Signals Processed</div>
    </div>
    <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
      <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-green-100 flex items-center justify-center">
        <Music className="w-5 h-5 text-green-600" />
      </div>
      <div className="text-2xl font-bold text-slate-800">{stats.files}</div>
      <div className="text-sm text-slate-500">Audio Files</div>
    </div>
    <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
      <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-purple-100 flex items-center justify-center">
        <Clock className="w-5 h-5 text-purple-600" />
      </div>
      <div className="text-2xl font-bold text-slate-800">{formatTime(stats.uptime)}</div>
      <div className="text-sm text-slate-500">Uptime</div>
    </div>
  </div>
);

// ============================================================================
// MAIN COMPONENT
// ============================================================================
export default function NeuralSynthesisPage() {
  const [isConnected, setIsConnected] = useState(true);
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  const [frequency, setFrequency] = useState(14.0);
  const [waveform, setWaveform] = useState('sine');
  const [elapsedTime, setElapsedTime] = useState(0);
  const [sessionName, setSessionName] = useState('');
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([]);
  const [playingId, setPlayingId] = useState<string | null>(null);
  const [stats, setStats] = useState({ signals: 0, files: 0, uptime: 0 });

  const [bands, setBands] = useState<FrequencyBand[]>([]);
  const [isClient, setIsClient] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const previewAudioRef = useRef<HTMLAudioElement | null>(null);
  const stopPreviewLoopRef = useRef<(() => void) | null>(null);

  // Initialize on client
  useEffect(() => {
    setIsClient(true);
    setBands([]);
  }, []);

  // Ensure canonical domain to avoid /api redirect + CORS failures from apex host
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (window.location.hostname !== 'clisonix.com') return;

    const nextUrl = `https://www.clisonix.com${window.location.pathname}${window.location.search}${window.location.hash}`;
    window.location.replace(nextUrl);
  }, []);

  // Fetch initial data
  useEffect(() => {
    if (!isClient) return;
    if (typeof window !== 'undefined' && window.location.hostname === 'clisonix.com') return;

    const isOk = (payload: any) => payload?.success === true || payload?.status === 'success' || payload?.status === 'online' || payload?.status === 'operational';

    const fetchData = async () => {
      // Fetch status
      const statusRes = await fetchAPI('/status');
      const statusMetrics = statusRes?.metrics ?? statusRes;
      if (isOk(statusRes) && statusMetrics) {
        setStats({
          signals: statusMetrics.eeg_signals_processed || 0,
          files: statusMetrics.audio_files_created || 0,
          uptime: statusMetrics.uptime_seconds || 0
        });
        setIsConnected(true);
      } else {
        setIsConnected(false);
      }

      // Fetch audio files
      const audioRes = await fetchAPI('/audio/list');
      if (isOk(audioRes) && audioRes.files) {
        setAudioFiles(normalizeAudioFiles(audioRes.files));
      }

      // Fetch frequency bands
      const bandsRes = await fetchAPI('/frequencies');
      if (isOk(bandsRes) && bandsRes.bands) {
        const bandData = bandsRes.bands;
        setBands([
          { name: 'Delta', range: bandData.delta.range, power: bandData.delta.power, color: '#8B5CF6', description: bandData.delta.description },
          { name: 'Theta', range: bandData.theta.range, power: bandData.theta.power, color: '#F59E0B', description: bandData.theta.description },
          { name: 'Alpha', range: bandData.alpha.range, power: bandData.alpha.power, color: '#3B82F6', description: bandData.alpha.description },
          { name: 'Beta', range: bandData.beta.range, power: bandData.beta.power, color: '#10B981', description: bandData.beta.description },
          { name: 'Gamma', range: bandData.gamma.range, power: bandData.gamma.power, color: '#EC4899', description: bandData.gamma.description }
        ]);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [isClient]);

  // Timer for synthesis
  useEffect(() => {
    if (!isSynthesizing) return;

    const timer = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [isSynthesizing]);

  // Start/Stop synthesis
  const handleStartStop = useCallback(async () => {
    const isOk = (payload: any) => payload?.success === true || payload?.status === 'success';

    if (isSynthesizing) {
      // Stop
      const res = await fetchAPI('/synthesis/stop', { method: 'POST' });
      if (isOk(res)) {
        setIsSynthesizing(false);
        setElapsedTime(0);
        setActiveSessionId(null);
        // Refresh audio files
        const audioRes = await fetchAPI('/audio/list');
        if (isOk(audioRes) && audioRes.files) {
          setAudioFiles(normalizeAudioFiles(audioRes.files));
        }
      }
    } else {
      // Start
      const res = await fetchAPI('/synthesis/start', {
        method: 'POST',
        body: JSON.stringify({
          frequency,
          waveform,
          duration: 300, // 5 minutes max
          modulation: true,
          binaural: waveform === 'binaural'
        })
      });
      if (isOk(res)) {
        const sessionId = res?.session?.session_id || res?.session_id || null;
        const symphonyName =
          res?.session?.symphony_name ||
          (sessionId ? `Neural Symphony #${String(sessionId).slice(-6)}` : 'Neural Synthesis Session');

        setIsSynthesizing(true);
        setSessionName(symphonyName);
        setElapsedTime(0);
        setActiveSessionId(sessionId ? String(sessionId) : null);
      }
    }
  }, [isSynthesizing, frequency, waveform]);

  const stopLivePreview = useCallback(() => {
    if (stopPreviewLoopRef.current) {
      stopPreviewLoopRef.current();
      stopPreviewLoopRef.current = null;
    }

    if (previewAudioRef.current) {
      previewAudioRef.current.pause();
      previewAudioRef.current.currentTime = 0;
    }
  }, []);

  const playLivePreviewChunk = useCallback(async (sessionId?: string | null) => {
    const query = new URLSearchParams({ seconds: '2.2' });
    if (sessionId) {
      query.set('session_id', sessionId);
    }

    const res = await fetch(`${API_BASE}/synthesis/preview?${query.toString()}`);
    if (!res.ok) {
      throw new Error(`Preview failed: ${res.status}`);
    }

    const audioBlob = await res.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = previewAudioRef.current || new Audio();
    previewAudioRef.current = audio;
    audio.src = audioUrl;

    try {
      await audio.play();
      await new Promise<void>((resolve) => {
        audio.onended = () => resolve();
        audio.onerror = () => resolve();
      });
    } finally {
      URL.revokeObjectURL(audioUrl);
    }
  }, []);

  useEffect(() => {
    if (!isSynthesizing) {
      stopLivePreview();
      return;
    }

    let cancelled = false;
    stopPreviewLoopRef.current = () => {
      cancelled = true;
    };

    const runLoop = async () => {
      while (!cancelled) {
        try {
          await playLivePreviewChunk(activeSessionId);
        } catch (error) {
          console.error('Live preview failed:', error);
          await new Promise((resolve) => setTimeout(resolve, 500));
        }
      }
    };

    void runLoop();

    return () => {
      cancelled = true;
    };
  }, [isSynthesizing, activeSessionId, playLivePreviewChunk, stopLivePreview]);

  const handleExport = useCallback(() => {
    if (!audioFiles.length) {
      alert('No audio files yet. Start and stop synthesis first.');
      return;
    }
    window.open(`${API_BASE}/audio/${audioFiles[0].file_id}/download`, '_blank');
  }, [audioFiles]);

  const handleRefreshAudio = useCallback(async () => {
    const res = await fetchAPI('/audio/list');
    if ((res?.success === true || res?.status === 'success') && res.files) {
      setAudioFiles(normalizeAudioFiles(res.files));
    }
  }, []);

  const handleDeleteAudio = useCallback(async (fileId: string) => {
    const res = await fetchAPI(`/audio/${fileId}`, { method: 'DELETE' });
    if (res.success) {
      setAudioFiles(prev => prev.filter(f => f.file_id !== fileId));
    }
  }, []);

  const handlePlayAudio = useCallback((fileId: string) => {
    if (!audioRef.current) {
      audioRef.current = new Audio();
    }

    if (playingId === fileId) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setPlayingId(null);
      return;
    }

    audioRef.current.pause();
    audioRef.current.currentTime = 0;
    audioRef.current.src = `${API_BASE}/audio/${fileId}/download`;
    audioRef.current.play().then(() => {
      setPlayingId(fileId);
    }).catch((error) => {
      console.error('Audio playback failed:', error);
      setPlayingId(null);
    });

    audioRef.current.onended = () => {
      setPlayingId(null);
    };
  }, [playingId]);

  const handleDownloadAudio = useCallback((fileId: string) => {
    window.open(`${API_BASE}/audio/${fileId}/download`, '_blank');
  }, []);

  if (!isClient) {
    return <div className="min-h-screen bg-slate-100 flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-orange-500 border-t-transparent"></div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <Header
        isConnected={isConnected}
        isSynthesizing={isSynthesizing}
        onStartStop={handleStartStop}
        onExport={handleExport}
        sessionName={sessionName}
        elapsedTime={elapsedTime}
      />

      <div className="px-6 pt-4">
        <div className="rounded-xl border border-violet-200 bg-gradient-to-r from-violet-50 to-blue-50 px-4 py-3 flex flex-wrap items-center justify-between gap-3">
          <div className="text-sm font-semibold text-slate-700">CLISONIX ZEISS VISION ULTRA • 2450px+ • Neural Synthesis Ready</div>
          <a
            href="/modules/curiosity-ocean?topic=Analyze%20neural%20synthesis%20session%20with%20ZEISS%20Vision%20Ultra&lang=auto"
            className="inline-flex items-center rounded-lg bg-violet-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-violet-700"
          >
            Open ZEISS Vision
          </a>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Stats Row */}
        <SynthesisStats stats={stats} />

        {/* Main Waveform */}
        <WaveformVisualizer isActive={isSynthesizing} frequency={frequency} />

        {/* Control Panels */}
        <div className="grid grid-cols-2 gap-6">
          <FrequencyControl
            frequency={frequency}
            setFrequency={setFrequency}
            waveform={waveform}
            setWaveform={setWaveform}
            isActive={isSynthesizing}
          />
          <FrequencyBands bands={bands} />
        </div>

        {/* Audio Library */}
        <AudioLibrary
          files={audioFiles}
          onRefresh={handleRefreshAudio}
          onDelete={handleDeleteAudio}
          onPlay={handlePlayAudio}
          onDownload={handleDownloadAudio}
          playingId={playingId}
        />
      </div>
    </div>
  );
}








