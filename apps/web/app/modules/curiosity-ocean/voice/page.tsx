'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import {
  chooseVoiceLanguage,
  languageDisplayName,
  takeLines,
  takeSpeech,
  type VoiceCapabilities,
  type VoiceMessage,
} from './voice-protocol';

type Phase = 'off' | 'listening' | 'hearing' | 'thinking' | 'speaking';
const labels: Record<Phase, string> = {
  off: 'Mikrofoni i fikur', listening: 'Po dëgjoj…', hearing: 'Po flisni…',
  thinking: 'Po përgatis përgjigjen…', speaking: 'Ocean po flet…',
};

async function base64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = reject;
    reader.onload = () => resolve(String(reader.result).split(',')[1]);
    reader.readAsDataURL(blob);
  });
}

async function checked(response: Response): Promise<Response> {
  if (response.ok) return response;
  const data = await response.json().catch(() => ({}));
  throw new Error(data.error || data.message || data.detail || `Shërbimi i zërit: ${response.status}`);
}

export default function VoiceConversation() {
  const [capabilities, setCapabilities] = useState<VoiceCapabilities | null>(null);
  const [language, setLanguage] = useState('');
  const [voice, setVoice] = useState('');
  const [uiLocale, setUiLocale] = useState('en');
  const [phase, setPhase] = useState<Phase>('off');
  const [enabled, setEnabled] = useState(false);
  const [error, setError] = useState('');
  const [messages, setMessages] = useState<VoiceMessage[]>([]);
  const [level, setLevel] = useState(0);
  const active = useRef(false);
  const starting = useRef(false);
  const history = useRef<VoiceMessage[]>([]);
  const mic = useRef<MediaStream | null>(null);
  const context = useRef<AudioContext | null>(null);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);
  const recorder = useRef<MediaRecorder | null>(null);
  const turn = useRef<AbortController | null>(null);
  const audio = useRef<AudioBufferSourceNode | null>(null);
  const busy = useRef(false);

  const interrupt = useCallback(() => {
    turn.current?.abort();
    turn.current = null;
    try { audio.current?.stop(); } catch { /* Playback already ended. */ }
    audio.current = null;
    busy.current = false;
  }, []);

  const stop = useCallback(() => {
    active.current = false;
    starting.current = false;
    interrupt();
    if (timer.current) clearInterval(timer.current);
    timer.current = null;
    if (recorder.current) {
      recorder.current.onstop = null;
      if (recorder.current.state !== 'inactive') recorder.current.stop();
    }
    recorder.current = null;
    mic.current?.getTracks().forEach((track) => track.stop());
    mic.current = null;
    void context.current?.close();
    context.current = null;
    setEnabled(false); setPhase('off'); setLevel(0);
  }, [interrupt]);

  // Release permission-sensitive resources on navigation as well as Stop.
  useEffect(() => () => { stop(); }, [stop]);

  useEffect(() => {
    const controller = new AbortController();
    const locale = navigator.language || document.documentElement.lang || 'en';
    setUiLocale(locale);
    fetch('/api/ocean/voice/capabilities', { cache: 'no-store', signal: controller.signal })
      .then(checked)
      .then((response) => response.json() as Promise<VoiceCapabilities>)
      .then((data) => {
        if (!Array.isArray(data.languages) || data.languages.length === 0) {
          throw new Error('Nuk u gjetën gjuhë dhe zëra aktivë.');
        }
        const selected = chooseVoiceLanguage(data, locale);
        const profile = data.languages.find((item) => item.code === selected) || data.languages[0];
        setCapabilities(data);
        setLanguage(profile.code);
        setVoice(profile.default_voice);
      })
      .catch((reason) => {
        if (!controller.signal.aborted) {
          setError(reason instanceof Error ? reason.message : 'Aftësitë zanore nuk u ngarkuan.');
        }
      });
    return () => controller.abort();
  }, []);

  const languageProfile = capabilities?.languages.find((item) => item.code === language);
  const changeLanguage = (nextLanguage: string) => {
    const profile = capabilities?.languages.find((item) => item.code === nextLanguage);
    if (!profile) return;
    setLanguage(profile.code);
    setVoice(profile.default_voice);
  };

  async function conversation(blob: Blob) {
    if (!active.current) return;
    interrupt();
    const controller = new AbortController();
    turn.current = controller;
    const signal = controller.signal;
    busy.current = true;
    setPhase('thinking'); setError('');
    let spoken = Promise.resolve();
    let speechError: Error | null = null;
    try {
      const transcription = await checked(await fetch('/api/ocean/voice/transcribe', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, signal,
        body: JSON.stringify({ audio_base64: await base64(blob), language }),
      }));
      const data = await transcription.json();
      const text = String(data.transcript || data.text || data.transcription || '').trim();
      if (!text) throw new Error('Nuk u dallua të folur. Provoni përsëri.');
      const previous = history.current.slice(-10);
      history.current = [...history.current, { role: 'user', content: text }, { role: 'assistant', content: '' }];
      const answerIndex = history.current.length - 1;
      setMessages([...history.current]);

      function queueSpeech(phrase: string) {
        // Start preparing each sentence while the earlier sentence is playing.
        const prepared = fetch('/api/ocean/voice/tts', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, signal,
          body: JSON.stringify({ text: phrase, language, voice, rate: '+0%' }),
        }).then(checked).then((response) => response.blob()).then(
          (blob) => ({ blob, error: null }),
          (error: Error) => ({ blob: null, error }),
        );
        spoken = spoken.then(async () => {
          if (signal.aborted || speechError) return;
          const result = await prepared;
          if (signal.aborted) return;
          if (result.error || !result.blob?.size) throw result.error || new Error('Zëri nuk u gjenerua.');
          const ctx = context.current;
          if (!ctx || ctx.state === 'closed') return;
          const buffer = await ctx.decodeAudioData(await result.blob.arrayBuffer());
          if (signal.aborted) return;
          const player = ctx.createBufferSource();
          player.buffer = buffer;
          player.connect(ctx.destination);
          audio.current = player;
          setPhase('speaking');
          await new Promise<void>((resolve, reject) => {
            const cleanup = () => {
              signal.removeEventListener('abort', cancelled);
              player.onended = null;
              try { player.stop(); } catch { /* Playback already ended. */ }
              player.disconnect();
              if (audio.current === player) audio.current = null;
            };
            const cancelled = () => { cleanup(); resolve(); };
            player.onended = () => { cleanup(); resolve(); };
            signal.addEventListener('abort', cancelled, { once: true });
            if (signal.aborted) { cancelled(); return; }
            try { player.start(); } catch (reason) { cleanup(); reject(reason); }
          });
        }).catch((reason) => { if (!signal.aborted) speechError = reason; });
      }

      const response = await checked(await fetch('/api/ocean/voice/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, signal,
        body: JSON.stringify({ text, language, messages: previous }),
      }));
      if (!response.body) throw new Error('Përgjigjja e modelit mungon.');
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let pending = '', unsaid = '', answer = '';
      let doneEvent = false;
      const consume = (line: string) => {
        if (!line.trim()) return;
        const event = JSON.parse(line);
        if (event.error) throw new Error(event.error);
        if (event.done) doneEvent = true;
        if (typeof event.text !== 'string') return;
        answer += event.text; unsaid += event.text;
        history.current[answerIndex] = { role: 'assistant', content: answer };
        setMessages([...history.current]);
        const batch = takeSpeech(unsaid);
        unsaid = batch.rest;
        batch.phrases.forEach(queueSpeech);
      };
      try {
        while (!signal.aborted) {
          const { value, done } = await reader.read();
          if (done) break;
          pending += decoder.decode(value, { stream: true });
          const batch = takeLines(pending);
          pending = batch.rest;
          batch.lines.forEach(consume);
        }
        pending += decoder.decode();
        if (pending.trim()) consume(pending);
        if (!signal.aborted && !doneEvent) throw new Error('Përgjigjja u ndërpre. Provoni përsëri.');
        if (!signal.aborted) takeSpeech(unsaid, true).phrases.forEach(queueSpeech);
      } finally { await reader.cancel().catch(() => {}); }
      await spoken;
      if (speechError) throw speechError;
    } catch (reason) {
      if (!signal.aborted && active.current) {
        setError(reason instanceof Error ? reason.message : 'Biseda zanore dështoi.');
        controller.abort();
      }
    } finally {
      if (turn.current === controller) {
        busy.current = false;
        if (active.current && recorder.current?.state !== 'recording') setPhase('listening');
      }
    }
  }

  async function start() {
    if (active.current || starting.current) return;
    if (!language || !voice) {
      setError('Prisni derisa Ocean të zbulojë gjuhët dhe zërat aktivë.');
      return;
    }
    starting.current = true; setError('');
    try {
      if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
        throw new Error('Mikrofoni kërkon HTTPS dhe një shfletues që mbështet regjistrimin audio.');
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: {
        echoCancellation: true, noiseSuppression: true, autoGainControl: true,
      } });
      if (!starting.current) { stream.getTracks().forEach((track) => track.stop()); return; }
      mic.current = stream;
      const ctx = new AudioContext(); context.current = ctx;
      await ctx.resume();
      if (!starting.current) return;
      const analyser = ctx.createAnalyser(); analyser.fftSize = 2048;
      ctx.createMediaStreamSource(stream).connect(analyser);
      const samples = new Float32Array(analyser.fftSize);
      const mimeType = ['audio/webm;codecs=opus', 'audio/mp4', 'audio/webm'].find((type) => MediaRecorder.isTypeSupported(type));
      active.current = true; starting.current = false;
      setEnabled(true); setPhase('listening');
      let lastVoice = 0, recordingStart = 0, voiceFrames = 0;
      timer.current = setInterval(() => {
        if (!active.current) return;
        analyser.getFloatTimeDomainData(samples);
        const rms = Math.sqrt(samples.reduce((sum, sample) => sum + sample * sample, 0) / samples.length);
        setLevel(Math.min(1, rms * 12));
        const now = performance.now();
        const voiced = rms > (audio.current ? 0.035 : 0.018);
        if (voiced) {
          lastVoice = now; voiceFrames++;
          if (voiceFrames >= 3 && busy.current) { interrupt(); setPhase('hearing'); }
          if (!recorder.current || recorder.current.state === 'inactive') {
            recordingStart = now; voiceFrames = 1;
            const recording = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
            const chunks: BlobPart[] = [];
            recorder.current = recording;
            recording.ondataavailable = (event) => { if (event.data.size) chunks.push(event.data); };
            recording.onstop = () => {
              if (recorder.current === recording) recorder.current = null;
              if (active.current && voiceFrames >= 3) {
                void conversation(new Blob(chunks, { type: recording.mimeType }));
              } else if (active.current && !busy.current) setPhase('listening');
            };
            recording.start(200);
            if (!busy.current) setPhase('hearing');
          }
        }
        if (recorder.current?.state === 'recording' && (now - lastVoice > 650 || now - recordingStart > 30000)) {
          recorder.current.stop();
        }
      }, 50);
    } catch (reason) {
      stop(); setError(reason instanceof Error ? reason.message : 'Mikrofoni nuk u hap.');
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 px-5 py-10">
      <div className="mx-auto max-w-2xl">
        <Link className="text-sm text-emerald-300" href="/modules/curiosity-ocean">← Curiosity Ocean</Link>
        <div className="mt-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-semibold">Bisedë me zë</h1>
            <p className="mt-3 text-slate-400">Flisni natyrshëm. Ocean përgjigjet me zë dhe ndalet kur flisni përsëri.</p>
          </div>
        </div>
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <label className="grid gap-2" htmlFor="voice-language">
            <span>Gjuha</span>
            <select id="voice-language" value={language} disabled={enabled || !capabilities} onChange={(event) => changeLanguage(event.target.value)} className="rounded-lg bg-slate-800 px-3 py-2">
              {!capabilities ? <option value="">Po zbulohen gjuhët…</option> : capabilities.languages.map((item) => (
                <option key={item.code} value={item.code}>{languageDisplayName(item, uiLocale)}</option>
              ))}
            </select>
          </label>
          <label className="grid gap-2" htmlFor="voice-speaker">
            <span>Zëri</span>
            <select id="voice-speaker" value={voice} disabled={enabled || !languageProfile} onChange={(event) => setVoice(event.target.value)} className="rounded-lg bg-slate-800 px-3 py-2">
              {!languageProfile ? <option value="">Po zbulohen zërat…</option> : languageProfile.voices.map((item) => (
                <option key={item.id} value={item.id}>{item.name} · {item.locale}</option>
              ))}
            </select>
          </label>
        </div>
        <div className="my-10 flex flex-col items-center gap-5 rounded-3xl border border-slate-800 bg-slate-900 p-8">
          <div aria-hidden="true" className="h-24 w-24 rounded-full bg-emerald-400 transition-transform duration-100" style={{ transform: `scale(${1 + level * 0.4})`, opacity: enabled ? 0.9 : 0.25 }} />
          <p aria-live="polite">{labels[phase]}</p>
          <button onClick={enabled ? stop : () => void start()} disabled={!capabilities || !language || !voice} className="rounded-full bg-emerald-400 px-7 py-3 font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-50">{enabled ? 'Ndalo bisedën' : 'Fillo bisedën'}</button>
          {enabled && <button className="text-sm text-emerald-300" onClick={() => { interrupt(); setPhase('listening'); }}>Ndërprit përgjigjen</button>}
          <p className="text-xs text-slate-400">Mikrofoni qëndron aktiv vetëm gjatë bisedës. Përdorni kufje për më pak jehonë.</p>
        </div>
        {error && <p role="alert" className="mb-6 rounded-xl bg-red-950 p-4 text-red-200">{error}</p>}
        <section aria-label="Transkripti i bisedës" className="space-y-4">
          {messages.map((message, index) => message.content && <div key={index} className={`rounded-2xl p-4 ${message.role === 'user' ? 'ml-8 bg-slate-800' : 'mr-8 bg-emerald-950'}`}>
            <p className="mb-1 text-xs text-slate-400">{message.role === 'user' ? 'Ju' : 'Ocean'}</p><p className="whitespace-pre-wrap">{message.content}</p>
          </div>)}
        </section>
      </div>
    </main>
  );
}
