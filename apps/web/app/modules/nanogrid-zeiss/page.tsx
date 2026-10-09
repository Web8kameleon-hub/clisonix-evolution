"use client";

import Link from 'next/link';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Brain, Camera, Zap, Gauge, ArrowRight, Activity, ChevronDown, ChevronUp, UploadCloud } from 'lucide-react';

const presets = [
  {
    title: 'Neural Synthesis',
    description: 'Ultra-precision visual readout for waveform & session quality.',
    topic: 'Run NanoGrid Plus ZEISS analysis for Neural Synthesis with maximum precision',
    icon: <Brain className="w-5 h-5 text-cyan-400" />
  },
  {
    title: 'ALBI EEG Analysis',
    description: 'High-resolution inspection for EEG signal quality and artifacts.',
    topic: 'Run NanoGrid Plus ZEISS analysis for ALBI EEG signal quality and artifact detection',
    icon: <Activity className="w-5 h-5 text-violet-400" />
  },
  {
    title: 'Fitness Dashboard',
    description: 'Motion and posture-centric ZEISS review for training sessions.',
    topic: 'Run NanoGrid Plus ZEISS analysis for Fitness Dashboard training session quality',
    icon: <Gauge className="w-5 h-5 text-emerald-400" />
  },
];

type HealthPayload = {
  status?: string;
  active_sessions?: number;
  timestamp?: string;
};

type SessionMetricsPayload = {
  quality_score?: number;
  dominant_band?: string;
  dominant_band_power?: number;
  duration_seconds?: number;
  samples_received?: number;
  channels_count?: number;
  state_interpretation?: string;
};

export default function NanoGridZeissPage() {
  const [profile, setProfile] = useState<'balanced' | 'clinical' | 'athlete'>('balanced');
  const [intensity, setIntensity] = useState(92);
  const [precision, setPrecision] = useState(97);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isStartingSession, setIsStartingSession] = useState(false);
  const [isStoppingSession, setIsStoppingSession] = useState(false);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [sessionError, setSessionError] = useState<string | null>(null);
  const [serviceHealth, setServiceHealth] = useState<HealthPayload | null>(null);
  const [sessionMetrics, setSessionMetrics] = useState<SessionMetricsPayload | null>(null);
  
  // Shtuar për UI: Kontrolli i hapjes së panelit të Ingestion
  const [showIngestion, setShowIngestion] = useState(false);

  const ALBI_API_BASE = '/api/albi-user';

  const resolvedProfileLabel = useMemo(() => {
    if (profile === 'clinical') return 'Clinical';
    if (profile === 'athlete') return 'Athlete';
    return 'Balanced';
  }, [profile]);

  const buildPresetHref = (topic: string) => {
    const params = new URLSearchParams({
      topic, lang: 'auto', intensity: String(intensity),
      precision: String(precision), profile, mode: 'limit',
      vision: 'zeiss_ultra', grid: 'nanogrid_plus',
    });
    return `/modules/curiosity-ocean?${params.toString()}`;
  };

  const fetchServiceHealth = useCallback(async () => {
    try {
      const response = await fetch(`${ALBI_API_BASE}/health`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`ALBI health failed (${response.status})`);
      const payload: HealthPayload = await response.json();
      setServiceHealth(payload);
      setStatusError(null);
    } catch (err) {
      setStatusError(err instanceof Error ? err.message : 'Failed to fetch ALBI health');
    }
  }, []);

  const fetchSessionMetrics = useCallback(async (activeSessionId: string) => {
    try {
      const response = await fetch(`${ALBI_API_BASE}/session/${activeSessionId}/metrics`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Session metrics failed (${response.status})`);
      const payload: SessionMetricsPayload = await response.json();
      setSessionMetrics(payload);
      setSessionError(null);
    } catch (err) {
      setSessionError(err instanceof Error ? err.message : 'Failed to fetch session metrics');
    }
  }, []);

  const startAlbiSession = useCallback(async () => {
    setIsStartingSession(true);
    setSessionError(null);
    try {
      const params = new URLSearchParams({ user_id: 'nanogrid_zeiss_operator', session_name: `NanoGrid-${resolvedProfileLabel}` });
      const response = await fetch(`${ALBI_API_BASE}/session/start?${params.toString()}`, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
      if (!response.ok) throw new Error(`Failed to start ALBI session (${response.status})`);
      const payload = await response.json();
      const nextSessionId = payload?.session_id as string | undefined;
      if (!nextSessionId) throw new Error('ALBI start response missing session_id');
      setSessionId(nextSessionId);
      await fetchSessionMetrics(nextSessionId);
      await fetchServiceHealth();
    } catch (err) {
      setSessionError(err instanceof Error ? err.message : 'Failed to start ALBI session');
    } finally {
      setIsStartingSession(false);
    }
  }, [ALBI_API_BASE, fetchServiceHealth, fetchSessionMetrics, resolvedProfileLabel]);

  const stopAlbiSession = useCallback(async () => {
    if (!sessionId) return;
    setIsStoppingSession(true);
    setSessionError(null);
    try {
      const response = await fetch(`${ALBI_API_BASE}/session/${sessionId}/stop`, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
      if (!response.ok) throw new Error(`Failed to stop ALBI session (${response.status})`);
      setSessionId(null);
      setSessionMetrics(null);
      await fetchServiceHealth();
    } catch (err) {
      setSessionError(err instanceof Error ? err.message : 'Failed to stop ALBI session');
    } finally {
      setIsStoppingSession(false);
    }
  }, [ALBI_API_BASE, fetchServiceHealth, sessionId]);

  useEffect(() => {
    fetchServiceHealth();
    const interval = setInterval(fetchServiceHealth, 10000);
    return () => clearInterval(interval);
  }, [fetchServiceHealth]);

  useEffect(() => {
    if (!sessionId) return;
    fetchSessionMetrics(sessionId);
    const interval = setInterval(() => fetchSessionMetrics(sessionId), 2000);
    return () => clearInterval(interval);
  }, [fetchSessionMetrics, sessionId]);

  const serviceOnline = serviceHealth?.status === 'operational';
  const canStart = serviceOnline && !sessionId && !isStartingSession;
  const canStop = !!sessionId && !isStoppingSession;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-cyan-500/30">
      <div className="mx-auto max-w-6xl px-6 py-12 space-y-10">
        
        {/* HEADER SECTION */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-800/80">
          <div>
            <div className="flex items-center gap-3 text-cyan-400 mb-2">
              <Brain className="h-6 w-6" />
              <span className="text-xs font-bold tracking-widest uppercase">NanoGrid + ZEISS</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-light tracking-tight text-white">
              Base Control <span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-400">Dashboard</span>
            </h1>
            <p className="mt-2 text-sm text-slate-400 max-w-2xl">
              Unified launch surface for ZEISS Vision Ultra workflows across neural, EEG, and training modules.
            </p>
          </div>
          
          <div className="flex items-center gap-4 bg-slate-900/50 p-2 rounded-2xl border border-slate-800">
             <div className="flex items-center gap-2 px-3">
                <span className={`relative flex h-3 w-3 ${serviceOnline ? 'text-emerald-400' : 'text-red-400'}`}>
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${serviceOnline ? 'bg-emerald-400' : 'bg-red-400'}`}></span>
                  <span className={`relative inline-flex rounded-full h-3 w-3 ${serviceOnline ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
                </span>
                <span className="text-sm font-medium">{serviceOnline ? 'ALBI Online' : 'ALBI Offline'}</span>
             </div>
             <div className="w-px h-8 bg-slate-700"></div>
             <button
                onClick={sessionId ? stopAlbiSession : startAlbiSession}
                disabled={sessionId ? !canStop : !canStart}
                className={`px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  sessionId 
                  ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30' 
                  : 'bg-cyan-500 text-slate-950 hover:bg-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.3)] disabled:opacity-50 disabled:shadow-none'
                }`}
             >
                {isStartingSession ? 'Starting...' : isStoppingSession ? 'Stopping...' : sessionId ? 'Stop Session' : 'Start Session'}
             </button>
          </div>
        </header>

        {/* LIVE METRICS SECTION */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-violet-400" /> Live Metrics
            </h2>
            {sessionId && <span className="text-xs font-mono text-slate-500 bg-slate-900 px-3 py-1 rounded-full border border-slate-800">ID: {sessionId}</span>}
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {[
              { label: 'Quality Score', value: sessionMetrics?.quality_score, highlight: true },
              { label: 'Dominant Band', value: sessionMetrics?.dominant_band, highlight: true },
              { label: 'Band Power', value: sessionMetrics?.dominant_band_power },
              { label: 'Duration (sec)', value: sessionMetrics?.duration_seconds },
              { label: 'Samples', value: sessionMetrics?.samples_received },
              { label: 'Channels', value: sessionMetrics?.channels_count },
            ].map((metric, i) => (
              <div key={i} className="bg-slate-900/40 backdrop-blur-md rounded-2xl p-5 border border-slate-800/60 shadow-sm relative overflow-hidden group">
                {metric.highlight && <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-violet-500 opacity-50 group-hover:opacity-100 transition-opacity"></div>}
                <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{metric.label}</p>
                <p className={`mt-2 font-light ${metric.highlight ? 'text-4xl text-white' : 'text-2xl text-slate-300'}`}>
                  {metric.value ?? '—'}
                </p>
              </div>
            ))}
          </div>
          {sessionError && <p className="text-sm text-red-400 mt-2">{sessionError}</p>}
          <p className="text-xs text-slate-500 mt-2">
            {sessionMetrics?.state_interpretation || 'Start a real ALBI session to stream live metrics.'}
          </p>
        </section>

        {/* CONTROLS & PRESETS GRID */}
        <div className="grid lg:grid-cols-3 gap-8">
          
          {/* Left Column: Limit Controls */}
          <section className="lg:col-span-1 space-y-4">
            <h2 className="text-lg font-medium text-white flex items-center gap-2">
              <Gauge className="w-5 h-5 text-cyan-400" /> Limit Controls
            </h2>
            <div className="bg-slate-900/40 backdrop-blur-md rounded-2xl p-6 border border-slate-800/60 space-y-6">
              
              <div className="space-y-3">
                <label className="text-sm font-medium text-slate-300">Profile</label>
                <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800">
                  {['balanced', 'clinical', 'athlete'].map((p) => (
                    <button
                      key={p}
                      onClick={() => setProfile(p as any)}
                      className={`flex-1 py-1.5 text-xs font-medium rounded-lg transition-colors capitalize ${
                        profile === p ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-500 hover:text-slate-300'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <label className="font-medium text-slate-300">Intensity</label>
                    <span className="text-cyan-400 font-mono">{intensity}</span>
                  </div>
                  <input
                    type="range" min={60} max={100} step={1} value={intensity}
                    onChange={(e) => setIntensity(Number(e.target.value))}
                    className="w-full accent-cyan-500 h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer"
                  />
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <label className="font-medium text-slate-300">Precision</label>
                    <span className="text-violet-400 font-mono">{precision}</span>
                  </div>
                  <input
                    type="range" min={70} max={100} step={1} value={precision}
                    onChange={(e) => setPrecision(Number(e.target.value))}
                    className="w-full accent-violet-500 h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer"
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-slate-800">
                <p className="text-xs text-slate-500">
                  Active Mode: <span className="text-slate-300 font-medium">{resolvedProfileLabel}</span>
                </p>
              </div>
            </div>
          </section>

          {/* Right Column: Presets */}
          <section className="lg:col-span-2 space-y-4">
            <h2 className="text-lg font-medium text-white flex items-center gap-2">
              <Zap className="w-5 h-5 text-emerald-400" /> Ocean Guidance Presets
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              {presets.map((preset, i) => (
                <Link key={i} href={buildPresetHref(preset.topic)}
                  className="group relative flex flex-col justify-between bg-slate-900/40 backdrop-blur-md rounded-2xl p-6 border border-slate-800/60 hover:border-cyan-500/50 hover:bg-slate-800/60 transition-all duration-300"
                >
                  <div>
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2 bg-slate-950 rounded-lg border border-slate-800 group-hover:scale-110 transition-transform">
                        {preset.icon}
                      </div>
                      <h3 className="font-medium text-white">{preset.title}</h3>
                    </div>
                    <p className="text-sm text-slate-400 leading-relaxed">{preset.description}</p>
                  </div>
                  <div className="mt-6 flex items-center text-xs font-medium text-cyan-400 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
                    Launch Workflow <ArrowRight className="w-3 h-3 ml-1" />
                  </div>
                </Link>
              ))}
              
              {/* Card për Bulk Ingestion (Opsionale, e fshehur brenda nje butoni) */}
              <div className="md:col-span-2 mt-2">
                 <button 
                   onClick={() => setShowIngestion(!showIngestion)}
                   className="w-full flex items-center justify-between p-4 bg-slate-900/20 border border-slate-800/50 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-900/40 transition-colors"
                 >
                    <div className="flex items-center gap-2 text-sm font-medium">
                       <UploadCloud className="w-4 h-4" /> Bulk EEG / Device Dump Ingestion
                    </div>
                    {showIngestion ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                 </button>
                 
                 {showIngestion && (
                    <div className="mt-4 p-6 bg-slate-900/40 border border-slate-800/60 rounded-2xl animate-in fade-in slide-in-from-top-2 duration-200">
                       <div className="grid md:grid-cols-2 gap-6">
                          <div className="space-y-4">
                             <div>
                                <label className="text-xs text-slate-400 mb-1 block">EEG Dump File</label>
                                <input type="file" className="w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700 transition-colors" />
                             </div>
                             <div>
                                <label className="text-xs text-slate-400 mb-1 block">Payload Format</label>
                                <select className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-cyan-500">
                                   <option>JSON array / {'{'} frames: [] {'}'}</option>
                                </select>
                             </div>
                          </div>
                          <div className="space-y-4">
                             <div>
                                <label className="text-xs text-slate-400 mb-1 block">Channel names (comma-separated)</label>
                                <input type="text" defaultValue="Fp1,Fp2,F3,F4" className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-cyan-500 font-mono" />
                             </div>
                             <div className="flex items-end h-full pb-1">
                                <button className="w-full bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium py-2 rounded-lg transition-colors border border-slate-700">
                                   Upload & Analyze
                                </button>
                             </div>
                          </div>
                       </div>
                    </div>
                 )}
              </div>
            </div>
          </section>
        </div>

      </div>
    </main>
  );
}