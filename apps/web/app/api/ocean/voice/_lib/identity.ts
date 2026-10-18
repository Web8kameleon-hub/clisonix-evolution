import { createHash } from 'node:crypto';
import { auth } from '@/lib/auth/core';

export type VoiceIdentity = {
  key: string;
  authenticated: boolean;
};

export async function resolveVoiceIdentity(request: Request): Promise<VoiceIdentity> {
  try {
    const session = await auth();
    const account = session?.user?.id || session?.user?.email;
    if (account) return { key: `account:${account}`, authenticated: true };
  } catch {
    // Voice remains available with the bounded guest policy if auth is degraded.
  }

  const forwarded = request.headers.get('cf-connecting-ip')
    || request.headers.get('x-real-ip')
    || request.headers.get('x-forwarded-for')?.split(',')[0]
    || 'unknown';
  const fingerprint = createHash('sha256').update(forwarded.trim()).digest('hex').slice(0, 24);
  return { key: `guest:${fingerprint}`, authenticated: false };
}
