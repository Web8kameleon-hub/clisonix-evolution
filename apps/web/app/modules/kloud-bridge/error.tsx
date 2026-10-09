'use client';

import Link from 'next/link';
import { useEffect } from 'react';

export default function KloudBridgeError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Kloud Bridge route error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center px-6">
      <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900/70 p-8">
        <p className="text-sm uppercase tracking-wider text-cyan-400">Kloud Bridge</p>
        <h1 className="mt-2 text-3xl font-semibold">We hit a temporary issue</h1>
        <p className="mt-4 text-slate-300">
          The module is reachable, but this request failed at runtime. You can retry now or go back to the modules list.
        </p>
        <p className="mt-3 text-xs text-slate-500 break-all">{error?.message || 'Unknown runtime error'}</p>
        <div className="mt-8 flex flex-wrap gap-3">
          <button
            onClick={reset}
            className="rounded-lg bg-cyan-500 px-4 py-2 text-slate-950 font-medium hover:bg-cyan-400"
          >
            Retry
          </button>
          <Link
            href="/modules"
            className="rounded-lg border border-slate-700 px-4 py-2 text-slate-200 hover:bg-slate-800"
          >
            Back to modules
          </Link>
        </div>
      </div>
    </div>
  );
}
