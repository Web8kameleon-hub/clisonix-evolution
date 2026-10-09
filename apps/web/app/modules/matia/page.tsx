'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  Brain, Activity, Zap, AlertTriangle, CheckCircle, ChevronRight,
  Loader2, ArrowLeft, RefreshCw, MonitorSmartphone, BarChart3,
  Lightbulb, ListChecks, X, Play
} from 'lucide-react';

// ─── Types ───────────────────────────────────────────────────────────────────

interface Theory {
  name: string;
  confidence: number;
  description: string;
  evidence: string[];
}

interface MatiaState {
  streaming: boolean;
  done: boolean;
  answer: string;
  theories: Theory[];
  anomalies: string[];
  steps: string[];
  ttft_ms: number;
  error: string | null;
}

// ─── Confidence bar ───────────────────────────────────────────────────────────

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = pct >= 80 ? 'bg-red-500' : pct >= 50 ? 'bg-amber-500' : 'bg-emerald-500';
  return (
    <div className="flex items-center gap-2 mt-1">
      <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs text-slate-400 w-8 text-right">{pct}%</span>
    </div>
  );
}

// ─── Theory card ─────────────────────────────────────────────────────────────

function TheoryCard({ t }: { t: Theory }) {
  const severity =
    t.confidence >= 0.8 ? { border: 'border-red-500/40', bg: 'bg-red-500/10', icon: <AlertTriangle className="w-4 h-4 text-red-400" /> } :
    t.confidence >= 0.5 ? { border: 'border-amber-500/40', bg: 'bg-amber-500/10', icon: <Zap className="w-4 h-4 text-amber-400" /> } :
    { border: 'border-emerald-500/40', bg: 'bg-emerald-500/10', icon: <CheckCircle className="w-4 h-4 text-emerald-400" /> };

  return (
    <div className={`rounded-xl border p-4 ${severity.border} ${severity.bg} space-y-2`}>
      <div className="flex items-center gap-2">
        {severity.icon}
        <span className="font-semibold text-white text-sm">{t.name}</span>
      </div>
      <ConfidenceBar value={t.confidence} />
      <p className="text-xs text-slate-300 leading-relaxed">{t.description}</p>
      {t.evidence && t.evidence.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-1">
          {t.evidence.map((e, i) => (
            <span key={i} className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full font-mono">
              {e}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Answer renderer ──────────────────────────────────────────────────────────

function AnswerBlock({ text }: { text: string }) {
  const lines = text.split('\n');
  return (
    <div className="space-y-1 text-sm text-slate-200 leading-relaxed font-mono whitespace-pre-wrap">
      {lines.map((line, i) => {
        if (line.startsWith('### ')) {
          return <h3 key={i} className="text-cyan-400 font-bold mt-3 not-italic">{line.replace('### ', '')}</h3>;
        }
        if (line.startsWith('**') && line.endsWith('**')) {
          return <p key={i} className="text-white font-semibold">{line.replace(/\*\*/g, '')}</p>;
        }
        if (line.startsWith('- ') || line.startsWith('* ')) {
          return <p key={i} className="pl-3 before:content-['·'] before:mr-2 before:text-cyan-500">{line.slice(2)}</p>;
        }
        if (/^\d+\./.test(line)) {
          return <p key={i} className="pl-3 text-emerald-300">{line}</p>;
        }
        if (line.startsWith('> ')) {
          return <p key={i} className="pl-3 border-l-2 border-slate-600 text-slate-400">{line.slice(2)}</p>;
        }
        return <p key={i} className={line === '' ? 'h-2' : ''}>{line}</p>;
      })}
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function MatiaPage() {
  const [screenText, setScreenText] = useState('');
  const [question, setQuestion] = useState('');
  const [pullMetrics, setPullMetrics] = useState(true);
  const [state, setState] = useState<MatiaState>({
    streaming: false,
    done: false,
    answer: '',
    theories: [],
    anomalies: [],
    steps: [],
    ttft_ms: 0,
    error: null,
  });

  const abortRef = useRef<AbortController | null>(null);
  const answerRef = useRef<HTMLDivElement>(null);
  const autoRunTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastAutoRunSignatureRef = useRef<string>('');

  // Auto-scroll to bottom of answer
  useEffect(() => {
    if (answerRef.current) {
      answerRef.current.scrollTop = answerRef.current.scrollHeight;
    }
  }, [state.answer]);

  const runAnalysis = useCallback(async () => {
    if (state.streaming) return;

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    setState({
      streaming: true,
      done: false,
      answer: '',
      theories: [],
      anomalies: [],
      steps: [],
      ttft_ms: 0,
      error: null,
    });

    try {
      const resp = await fetch('/api/matia?path=stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          screen_text: screenText,
          question,
          pull_metrics: pullMetrics,
          language: 'sq',
        }),
        signal: abortRef.current.signal,
      });

      if (!resp.ok) {
        const errData = await resp.json().catch(() => ({ error: `HTTP ${resp.status}` }));
        setState(s => ({ ...s, streaming: false, done: true, error: errData.error || `HTTP ${resp.status}` }));
        return;
      }

      const reader = resp.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const raw = line.slice(6).trim();
          if (raw === '[DONE]') {
            setState(s => ({ ...s, streaming: false, done: true }));
            break;
          }
          try {
            const payload = JSON.parse(raw);
            if (typeof payload.chunk === 'string') {
              setState(s => ({ ...s, answer: s.answer + payload.chunk }));
            } else if (payload.done) {
              setState(s => ({
                ...s,
                anomalies: payload.anomalies ?? s.anomalies,
                steps: payload.steps ?? s.steps,
                theories: payload.theories ?? s.theories,
              }));
            } else if (payload.metric === 'ttft') {
              setState(s => ({ ...s, ttft_ms: payload.ms }));
            } else if (payload.error) {
              setState(s => ({ ...s, error: payload.error }));
            }
          } catch { /* ignore parse errors */ }
        }
      }
    } catch (err: unknown) {
      if ((err as Error).name === 'AbortError') return;
      setState(s => ({ ...s, streaming: false, done: true, error: (err as Error).message }));
    }
  }, [screenText, question, pullMetrics, state.streaming]);

  const stop = useCallback(() => {
    abortRef.current?.abort();
    setState(s => ({ ...s, streaming: false }));
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setScreenText('');
    setQuestion('');
    setState({ streaming: false, done: false, answer: '', theories: [], anomalies: [], steps: [], ttft_ms: 0, error: null });
  }, []);

  // ─── Keyboard shortcut: Ctrl+Enter → run ──────────────────────────────────
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      runAnalysis();
    }
  }, [runAnalysis]);

  useEffect(() => {
    if (state.streaming) return;

    const normalizedScreen = screenText.trim();
    const normalizedQuestion = question.trim();
    const signature = `${normalizedScreen}||${normalizedQuestion}`;

    if (normalizedScreen.length < 12) return;
    if (signature === lastAutoRunSignatureRef.current) return;

    if (autoRunTimerRef.current) {
      clearTimeout(autoRunTimerRef.current);
    }

    autoRunTimerRef.current = setTimeout(() => {
      if (state.streaming) return;
      if (!screenText.trim()) return;

      lastAutoRunSignatureRef.current = `${screenText.trim()}||${question.trim()}`;
      void runAnalysis();
    }, 700);

    return () => {
      if (autoRunTimerRef.current) {
        clearTimeout(autoRunTimerRef.current);
        autoRunTimerRef.current = null;
      }
    };
  }, [screenText, question, state.streaming, runAnalysis]);

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* ── Header ────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-40 bg-[#0a0a0f]/90 backdrop-blur border-b border-slate-800/60">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-4">
          <Link href="/modules" className="text-slate-400 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-cyan-500 flex items-center justify-center">
              <Brain className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-wide">Matia</h1>
              <p className="text-[10px] text-slate-500 leading-none">
                Metric · Analyse · Teorie · Implementation · Answer
              </p>
            </div>
          </div>
          {state.ttft_ms > 0 && (
            <div className="ml-auto flex items-center gap-1.5 text-xs text-slate-400">
              <Activity className="w-3 h-3 text-cyan-500" />
              <span>{state.ttft_ms}ms</span>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-5 gap-6">

        {/* ── Left panel: input ──────────────────────────────────────── */}
        <div className="lg:col-span-2 space-y-4">

          {/* Screen Text Input */}
          <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-4 space-y-3">
            <div className="flex items-center gap-2 text-slate-300 text-sm font-medium">
              <MonitorSmartphone className="w-4 h-4 text-violet-400" />
              <span>Lexo Ekranin</span>
            </div>
            <textarea
              value={screenText}
              onChange={e => setScreenText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ngjit tekstin që sheh në ekran (error messages, logs, output)… Matia analizon automatikisht pas një pauze të shkurtër."
              rows={6}
              className="w-full bg-slate-800/60 border border-slate-700/40 rounded-xl px-3 py-2.5 text-sm text-slate-200
                         placeholder-slate-500 resize-none focus:outline-none focus:border-violet-500/60
                         font-mono leading-relaxed"
            />
          </div>

          {/* Question Input */}
          <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-4 space-y-3">
            <div className="flex items-center gap-2 text-slate-300 text-sm font-medium">
              <Lightbulb className="w-4 h-4 text-amber-400" />
              <span>Pyetja / Konteksti</span>
            </div>
            <textarea
              value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Çfarë dëshiron të analizojë Matia? (opsionale)"
              rows={3}
              className="w-full bg-slate-800/60 border border-slate-700/40 rounded-xl px-3 py-2.5 text-sm text-slate-200
                         placeholder-slate-500 resize-none focus:outline-none focus:border-amber-500/60
                         leading-relaxed"
            />
          </div>

          {/* Options */}
          <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-4">
            <label className="flex items-center gap-3 cursor-pointer group">
              <div
                onClick={() => setPullMetrics(v => !v)}
                className={`w-10 h-5 rounded-full transition-colors relative ${
                  pullMetrics ? 'bg-violet-600' : 'bg-slate-700'
                }`}
              >
                <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all ${
                  pullMetrics ? 'left-5' : 'left-0.5'
                }`} />
              </div>
              <div>
                <span className="text-sm text-slate-300">Mbledh metrika live</span>
                <p className="text-[11px] text-slate-500">ALBI · JONA · Ocean · API · Kloud</p>
              </div>
            </label>
          </div>

          {/* Action buttons */}
          <div className="flex gap-3">
            <button
              onClick={state.streaming ? stop : runAnalysis}
              disabled={!screenText.trim() && !question.trim() && !state.streaming}
              className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-sm
                          transition-all disabled:opacity-40 disabled:cursor-not-allowed
                          ${state.streaming
                            ? 'bg-red-600 hover:bg-red-500 text-white'
                            : 'bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white shadow-lg shadow-violet-900/40'
                          }`}
            >
              {state.streaming
                ? <><X className="w-4 h-4" /> Stop</>
                : <><Play className="w-4 h-4" /> Analizo &nbsp;<kbd className="opacity-50 text-[10px] border border-current rounded px-1">⌘↵</kbd></>
              }
            </button>
            <button
              onClick={reset}
              className="px-4 py-3 rounded-xl border border-slate-700 text-slate-400 hover:text-white hover:border-slate-500 transition-all"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* ── Right panel: results ───────────────────────────────────── */}
        <div className="lg:col-span-3 space-y-4">

          {/* Answer stream */}
          <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-4">
            <div className="flex items-center gap-2 text-slate-300 text-sm font-medium mb-3">
              <Brain className="w-4 h-4 text-violet-400" />
              <span>Përgjigja e Matia</span>
              {state.streaming && (
                <span className="ml-auto flex items-center gap-1.5 text-xs text-violet-400">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  Duke analizuar…
                </span>
              )}
              {state.done && !state.streaming && state.answer && (
                <span className="ml-auto text-[11px] text-emerald-400">✓ Kompletuar</span>
              )}
            </div>

            {state.error && (
              <div className="flex items-start gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/40 text-red-400 text-sm">
                <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
                {state.error}
              </div>
            )}

            {!state.streaming && !state.answer && !state.error && (
              <div className="flex flex-col items-center justify-center py-12 text-slate-600 space-y-2">
                <Brain className="w-10 h-10 opacity-30" />
                <p className="text-sm">Ngjit tekstin nga ekrani dhe kliko <strong>Analizo</strong></p>
              </div>
            )}

            {state.answer && (
              <div
                ref={answerRef}
                className="max-h-72 overflow-y-auto pr-1 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-700"
              >
                <AnswerBlock text={state.answer} />
              </div>
            )}

            {state.streaming && !state.answer && (
              <div className="flex items-center gap-2 text-slate-500 text-sm py-4">
                <Loader2 className="w-4 h-4 animate-spin text-violet-400" />
                Duke mbledhur metrika dhe aplikuar teori…
              </div>
            )}
          </div>

          {/* Theories */}
          {state.theories.length > 0 && (
            <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-slate-300 text-sm font-medium">
                <BarChart3 className="w-4 h-4 text-cyan-400" />
                <span>Teoritë ({state.theories.length})</span>
              </div>
              <div className="space-y-3">
                {state.theories.map((t, i) => <TheoryCard key={i} t={t} />)}
              </div>
            </div>
          )}

          {/* Anomalies */}
          {state.anomalies.length > 0 && (
            <div className="bg-slate-900/60 border border-red-500/20 rounded-2xl p-4 space-y-2">
              <div className="flex items-center gap-2 text-slate-300 text-sm font-medium">
                <AlertTriangle className="w-4 h-4 text-red-400" />
                <span>Anomali ({state.anomalies.length})</span>
              </div>
              <ul className="space-y-1.5">
                {state.anomalies.map((a, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-red-300 font-mono">
                    <ChevronRight className="w-3 h-3 mt-0.5 text-red-500 shrink-0" />
                    {a}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Implementation steps */}
          {state.steps.length > 0 && (
            <div className="bg-slate-900/60 border border-emerald-500/20 rounded-2xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-slate-300 text-sm font-medium">
                <ListChecks className="w-4 h-4 text-emerald-400" />
                <span>Hapat e Implementimit</span>
              </div>
              <ol className="space-y-2">
                {state.steps.map((s, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-slate-300">
                    <span className="shrink-0 w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 text-[11px] flex items-center justify-center font-bold mt-0.5">
                      {i + 1}
                    </span>
                    {s}
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
