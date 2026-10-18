import { NextRequest } from 'next/server';
import { resolveVoiceIdentity } from '../_lib/identity';

export const runtime = 'nodejs';
export const maxDuration = 90;
const active = new Set<string>();

export async function POST(request: NextRequest) {
  const identity = (await resolveVoiceIdentity(request)).key;
  if (active.has(identity) || active.size >= 2) return Response.json({ error: 'Transcription is busy.' }, { status: 429 });
  if (Number(request.headers.get('content-length')) > 6000000) return Response.json({ error: 'Recording too large.' }, { status: 413 });
  const raw = await request.clone().text();
  if (raw.length > 6000000) return Response.json({ error: 'Recording too large.' }, { status: 413 });
  try {
    const body = JSON.parse(raw);
    if (typeof body?.audio_base64 !== 'string' || !body.audio_base64) return Response.json({ error: 'Audio is required.' }, { status: 400 });
  } catch { return Response.json({ error: 'Invalid JSON.' }, { status: 400 }); }
  active.add(identity);
  try {
    const upstream = process.env.OCEAN_VOICE_STT_URL || 'http://clisonix-voice-stt:8045';
    const response = await fetch(`${upstream.replace(/\/+$/, '')}/transcribe`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: raw,
      signal: AbortSignal.any([request.signal, AbortSignal.timeout(85000)]), cache: 'no-store',
    });
    const data = await response.json();
    return Response.json(data, { status: response.status, headers: { 'Cache-Control': 'no-store' } });
  } catch {
    return Response.json({ error: 'GPU transcription unavailable. Please try again.' }, { status: 503 });
  } finally { active.delete(identity); }
}
