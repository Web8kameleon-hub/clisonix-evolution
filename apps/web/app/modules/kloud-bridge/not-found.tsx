import Link from 'next/link';

export default function KloudBridgeNotFound() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center px-6">
      <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900/70 p-8 text-center">
        <p className="text-sm uppercase tracking-wider text-cyan-400">Kloud Bridge</p>
        <h1 className="mt-2 text-3xl font-semibold">Module page not found</h1>
        <p className="mt-4 text-slate-300">
          This module route is currently unavailable. Try again in a minute or return to the modules overview.
        </p>
        <div className="mt-8">
          <Link
            href="/modules"
            className="inline-flex rounded-lg border border-slate-700 px-4 py-2 text-slate-200 hover:bg-slate-800"
          >
            Back to modules
          </Link>
        </div>
      </div>
    </div>
  );
}
