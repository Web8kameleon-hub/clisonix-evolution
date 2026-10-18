import { resolveVoiceIdentity } from '../_lib/identity';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 120;

// Voice law: this exact Gemma model, full GPU residency, no fallback.
const model = 'huihui_ai/gemma-4-abliterated:12b';
const policyHeaders = { 'X-Ocean-Voice-Policy': 'gemma-only-v1', 'Cache-Control': 'no-store' };
const ollama = (process.env.OLLAMA_INTERNAL_URL || 'http://clisonix-ollama:11434').replace(/\/+$/, '');
const active = new Set<string>();
const windows = new Map<string, { start: number; count: number }>();

export async function POST(request: Request) {
  const identity = (await resolveVoiceIdentity(request)).key;
  if (process.env.OCEAN_VOICE_MODEL && process.env.OCEAN_VOICE_MODEL !== model) {
    return Response.json({ error: 'Voice policy requires the approved Gemma model.', code: 'VOICE_MODEL_POLICY' }, { status: 503, headers: policyHeaders });
  }
  if (Number(request.headers.get('content-length')) > 80000) {
    return Response.json({ error: 'Request too large.' }, { status: 413 });
  }
  const raw = await request.text();
  if (raw.length > 80000) return Response.json({ error: 'Request too large.' }, { status: 413 });
  let body: Record<string, unknown>;
  try { body = JSON.parse(raw); } catch {
    return Response.json({ error: 'Invalid JSON.' }, { status: 400 });
  }
  if (!body || typeof body.text !== 'string' || !body.text.trim() || body.text.length > 4000) {
    return Response.json({ error: 'A voice transcript of up to 4000 characters is required.' }, { status: 400 });
  }
  if ('model' in body && body.model !== model) {
    return Response.json({ error: 'Voice accepts only the approved Gemma model.', code: 'VOICE_MODEL_POLICY' }, { status: 400, headers: policyHeaders });
  }
  const now = Date.now();
  for (const [key, value] of windows) if (now - value.start > 60000) windows.delete(key);
  const window = windows.get(identity) || { start: now, count: 0 };
  if (window.count >= 20 || active.has(identity) || active.size >= 2 || windows.size >= 5000) {
    return Response.json({ error: 'Voice service is busy. Try again shortly.' }, { status: 429, headers: { 'Retry-After': '3' } });
  }
  window.count++;
  windows.set(identity, window);
  active.add(identity);
  const abort = new AbortController();
  const cancel = () => abort.abort();
  request.signal.addEventListener('abort', cancel, { once: true });
  const timeout = setTimeout(cancel, 115000);
  let released = false;
  const release = () => {
    if (released) return;
    released = true;
    clearTimeout(timeout);
    request.signal.removeEventListener('abort', cancel);
    active.delete(identity);
  };
  if (request.signal.aborted) cancel();
  try {
    const options = { num_ctx: 4096, num_gpu: 999, num_predict: 192, temperature: 0.65 };
    // Load the conversational model and require actual GPU residency.
    const warm = await fetch(`${ollama}/api/generate`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, prompt: '', stream: false, think: false, keep_alive: '24h', options }),
      signal: abort.signal, cache: 'no-store',
    });
    if (!warm.ok) throw new Error('Voice model unavailable');
    const warmed = await warm.json();
    if (warmed.model !== model) throw new Error('Voice model identity mismatch');
    const residency = await fetch(`${ollama}/api/ps`, { signal: abort.signal, cache: 'no-store' });
    if (!residency.ok) throw new Error('GPU state unavailable');
    const state = await residency.json();
    const loaded = state.models?.find((item: { name: string }) => item.name === model);
    if (!loaded || !Number.isFinite(loaded.size) || !Number.isFinite(loaded.size_vram)
      || !(loaded.size > 0) || loaded.size_vram < loaded.size) {
      release();
      return Response.json({ error: 'Voice requires Gemma fully loaded on GPU. CPU fallback is forbidden.', code: 'VOICE_GPU_REQUIRED' }, { status: 503, headers: policyHeaders });
    }
    const languageCode = String(body.language || '').trim().split('-', 1)[0].toLowerCase();
    let language = 'the user’s language';
    if (/^[a-z]{2,3}$/.test(languageCode)) {
      try { language = new Intl.DisplayNames(['en'], { type: 'language' }).of(languageCode) || language; } catch { /* Use neutral fallback. */ }
    }
    const history = Array.isArray(body.messages) ? body.messages.slice(-10).filter(
      (item) => item && ['user', 'assistant'].includes(item.role) && typeof item.content === 'string',
    ).map((item) => ({ role: item.role, content: item.content.slice(0, 1200) })) : [];
    const response = await fetch(`${ollama}/api/chat`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, stream: true, think: false, keep_alive: '24h', options, messages: [
        { role: 'system', content: `You are Ocean, a friendly conversational assistant. Speak naturally in ${language}. Answer in one to three short sentences unless asked for detail. Remember names and facts from the conversation; use the actual name the user shared, never placeholders or invented personal details. Do not use markdown, lists or stage directions. Ask a brief follow-up only when useful.` },
        ...history, { role: 'user', content: body.text.trim() },
      ] }), signal: abort.signal, cache: 'no-store',
    });
    if (!response.ok || !response.body) throw new Error('Voice generation unavailable');
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    const encoder = new TextEncoder();
    let pending = '';
    let finished = false;
    let sawText = false;
    const stream = new ReadableStream({
      async start(controller) {
        const emit = (value: unknown) => controller.enqueue(encoder.encode(JSON.stringify(value) + '\n'));
        const consume = (line: string) => {
          if (!line.trim()) return;
          const event = JSON.parse(line);
          if (event.model !== model) throw new Error('Voice model identity mismatch');
          if (event.error) throw new Error('Model generation failed');
          if (event.message?.content) { sawText = true; emit({ text: event.message.content }); }
          if (event.done) finished = true;
        };
        try {
          emit({ status: 'ready', model, gpu: true });
          while (!abort.signal.aborted) {
            const { done, value } = await reader.read();
            if (done) break;
            pending += decoder.decode(value, { stream: true });
            const lines = pending.split('\n');
            pending = lines.pop() || '';
            for (const line of lines) consume(line);
          }
          pending += decoder.decode();
          if (pending.trim()) consume(pending);
          if (!abort.signal.aborted) {
            if (!finished || !sawText) throw new Error('Model returned an incomplete response');
            emit({ done: true });
            controller.close();
          }
        } catch {
          if (!abort.signal.aborted) { emit({ error: 'Voice response interrupted. Please try again.' }); controller.close(); }
        } finally { abort.abort(); await reader.cancel().catch(() => {}); release(); }
      },
      cancel() { abort.abort(); release(); return reader.cancel(); },
    });
    return new Response(stream, { headers: {
      ...policyHeaders,
      'Content-Type': 'application/x-ndjson; charset=utf-8',
      'Cache-Control': 'no-store, no-transform', 'X-Accel-Buffering': 'no',
    } });
  } catch {
    abort.abort(); release();
    return Response.json({ error: 'Gemma GPU voice service unavailable. No alternative model will be used.', code: 'VOICE_GEMMA_UNAVAILABLE' }, { status: 503, headers: policyHeaders });
  }
}
