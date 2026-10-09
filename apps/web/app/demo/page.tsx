import Link from 'next/link';

export default function DemoPage() {
  return (
    <div className="min-h-screen bg-[linear-gradient(160deg,_#f8fbff_0%,_#f7fff8_50%,_#fff9ef_100%)] px-4 py-10 text-slate-900 sm:px-6">
      <div className="mx-auto w-full max-w-3xl rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-900/5">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">Demo Session</p>
        <h1 className="mt-3 text-3xl font-black">Report preview flow</h1>
        <p className="mt-3 text-sm leading-relaxed text-slate-600">
          This path is intentionally decoupled from production APIs. It is built for sales calls and UX testing.
        </p>

        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href="/demo/run"
            className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            Run Demo
          </Link>
          <Link
            href="/app"
            className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
          >
            Back to App
          </Link>
        </div>
      </div>
    </div>
  );
}
