export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    const upstream = process.env.OCEAN_VOICE_STT_URL || 'http://clisonix-voice-stt:8045';
    const response = await fetch(`${upstream.replace(/\/+$/, '')}/capabilities`, {
      signal: AbortSignal.any([request.signal, AbortSignal.timeout(12000)]),
      cache: 'no-store',
    });
    const data = await response.json();
    return Response.json(data, {
      status: response.status,
      headers: { 'Cache-Control': 'no-store' },
    });
  } catch {
    return Response.json({
      error: 'Voice capabilities are temporarily unavailable.',
      languages: [],
    }, { status: 503, headers: { 'Cache-Control': 'no-store' } });
  }
}
