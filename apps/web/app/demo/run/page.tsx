'use client';

import Link from 'next/link';
import { useMemo } from 'react';

const FILE_OPTIONS = ['Excel', 'PDF', 'Word', 'PPT'] as const;

export default function DemoRunPage() {
  const timestamp = useMemo(() => new Date().toLocaleString(), []);

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#fff5e4_0%,_#f9fffb_40%,_#f4f8ff_100%)] px-4 py-10 sm:px-6">
      <div className="mx-auto w-full max-w-3xl rounded-3xl border border-slate-200 bg-white p-8 text-slate-900 shadow-xl shadow-slate-900/10">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">Demo Run</p>
        <h1 className="mt-2 text-3xl font-black">Weekly Operations Report - Simulated</h1>
        <p className="mt-3 text-sm text-slate-600">
          This output is generated from demo data for meetings and first-time UX tests.
        </p>

        <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900">
          <p className="font-semibold">Report generated successfully</p>
          <p className="mt-1">Retail operations summary prepared at {timestamp}.</p>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          {FILE_OPTIONS.map((fileType) => (
            <button
              key={fileType}
              type="button"
              className="rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              Download {fileType}
            </button>
          ))}
        </div>

        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/app" className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800">
            Back to App
          </Link>
          <Link href="/" className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">
            Public Home
          </Link>
        </div>
      </div>
    </div>
  );
}
