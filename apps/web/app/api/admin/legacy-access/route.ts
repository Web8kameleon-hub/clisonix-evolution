import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

interface AccessPayload {
  code?: string;
}

// ---------------------------------------------------------------------------
// In-memory rate limiter — resets on worker restart (acceptable for Edge/Node)
// Max 5 attempts per IP within a 15-minute window, then 30-minute lockout.
// ---------------------------------------------------------------------------
const MAX_ATTEMPTS = 5;
const WINDOW_MS = 15 * 60 * 1000;
const LOCKOUT_MS = 30 * 60 * 1000;

interface BucketEntry {
  count: number;
  windowStart: number;
  lockedUntil: number | null;
}

const buckets = new Map<string, BucketEntry>();

function getClientIp(request: Request): string {
  const xff = (request.headers as Headers).get('x-forwarded-for');
  const ip = xff ? xff.split(',')[0].trim() : 'unknown';
  return ip.slice(0, 64);
}

function checkRateLimit(ip: string): { allowed: boolean; retryAfterSec?: number } {
  const now = Date.now();
  let entry = buckets.get(ip);

  if (!entry) {
    entry = { count: 0, windowStart: now, lockedUntil: null };
    buckets.set(ip, entry);
  }

  if (entry.lockedUntil !== null && now < entry.lockedUntil) {
    return { allowed: false, retryAfterSec: Math.ceil((entry.lockedUntil - now) / 1000) };
  }

  if (now - entry.windowStart > WINDOW_MS) {
    entry.count = 0;
    entry.windowStart = now;
    entry.lockedUntil = null;
  }

  entry.count += 1;

  if (entry.count > MAX_ATTEMPTS) {
    entry.lockedUntil = now + LOCKOUT_MS;
    return { allowed: false, retryAfterSec: Math.ceil(LOCKOUT_MS / 1000) };
  }

  return { allowed: true };
}

export async function POST(request: Request) {
  const ip = getClientIp(request);
  const rateCheck = checkRateLimit(ip);

  if (!rateCheck.allowed) {
    return NextResponse.json(
      { error: 'Too many attempts. Please try again later.' },
      {
        status: 429,
        headers: { 'Retry-After': String(rateCheck.retryAfterSec ?? 1800) },
      },
    );
  }

  const configuredCode = process.env.ADMIN_LEGACY_ACCESS_CODE;

  if (!configuredCode) {
    return NextResponse.json(
      { error: 'Admin access is not configured on this server.' },
      { status: 503 },
    );
  }

  const payload = (await request.json().catch(() => ({}))) as AccessPayload;
  const code = typeof payload.code === 'string' ? payload.code.trim() : '';

  if (!code) {
    return NextResponse.json({ error: 'Code is required.' }, { status: 422 });
  }

  if (code !== configuredCode) {
    return NextResponse.json({ error: 'Invalid code.' }, { status: 401 });
  }

  // Reset bucket on success so an authorised user never gets locked out
  buckets.delete(ip);

  const cookieStore = await cookies();
  cookieStore.set('clx_legacy_gate', 'granted', {
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    maxAge: 60 * 60,
    path: '/',
  });

  return NextResponse.json({ ok: true }, { status: 200 });
}
