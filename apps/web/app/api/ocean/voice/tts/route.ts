import { NextRequest } from 'next/server';
import { resolveVoiceIdentity } from '../_lib/identity';

export const runtime = 'nodejs';
export const maxDuration = 60;
const active = new Set<string>();
const windows = new Map<string, { start: number; count: number }>();

export async function POST(request: NextRequest) {
  const identity = (await resolveVoiceIdentity(request)).key;
  const now = Date.now();
  for (const [key, value] of windows) if (now - value.start > 60000) windows.delete(key);
  const window = windows.get(identity) || { start: now, count: 0 };
  if (window.count >= 60 || active.has(identity) || active.size >= 4 || windows.size >= 5000) {
    return Response.json({ error: 'Speech service is busy. Try again shortly.' }, { status: 429, headers: { 'Retry-After': '3' } });
  }
  if (Number(request.headers.get('content-length')) > 12000) return Response.json({ error: 'Request too large.' }, { status: 413 });
  const raw = await request.clone().text();
  if (raw.length > 12000) return Response.json({ error: 'Request too large.' }, { status: 413 });
  try {
    const body = JSON.parse(raw);
    if (typeof body?.text !== 'string' || !body.text.trim() || body.text.length > 2400) {
      return Response.json({ error: 'A short speech phrase is required.' }, { status: 400 });
    }
  } catch { return Response.json({ error: 'Invalid JSON.' }, { status: 400 }); }
  window.count++;
  windows.set(identity, window);
  active.add(identity);
  try {
    const upstream = process.env.OCEAN_VOICE_STT_URL || 'http://clisonix-voice-stt:8045';
    const response = await fetch(`${upstream.replace(/\/+$/, '')}/synthesize`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: raw,
      signal: AbortSignal.any([request.signal, AbortSignal.timeout(55000)]), cache: 'no-store',
    });
    if (!response.ok) return Response.json({ error: 'Neural voice temporarily unavailable.' }, { status: response.status });
    return new Response(response.body, { headers: {
      'Content-Type': 'audio/mpeg', 'Cache-Control': 'no-store',
      'X-Voice-Used': response.headers.get('X-Voice-Used') || '',
    } });
  } catch {
    return Response.json({ error: 'Neural voice unavailable. Please try again.' }, { status: 503 });
  } finally {
    active.delete(identity);
  }
}
