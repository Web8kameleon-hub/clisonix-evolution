import type { Metadata } from 'next';
import Link from 'next/link';
import { moduleGuides } from '../../../src/lib/module-docs';

export const metadata: Metadata = {
  title: 'How to Use Modules | Clisonix',
  description:
    'Practical how-to documentation for Clisonix modules with usage flow, purpose, and quick steps for each module.',
  alternates: {
    canonical: '/modules/how-to-use',
  },
  openGraph: {
    title: 'How to Use Clisonix Modules',
    description:
      'Step-by-step usage overview for Clisonix modules, including AI, research, neuroscience, data, and developer tools.',
    url: 'https://www.clisonix.com/modules/how-to-use',
  },
};

export default function ModulesHowToUsePage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-300">Module Documentation</p>
          <h1 className="mt-4 text-4xl font-bold md:text-5xl">How to use each Clisonix module</h1>
          <p className="mt-5 text-lg text-slate-300 leading-8">
            Central reference page with practical steps for each major module. Use this as the operational guide before starting workflows.
          </p>
          <div className="mt-5">
            <Link
              href="/developers/docs-index"
              className="inline-flex items-center rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-4 py-2 text-sm font-semibold text-emerald-200 hover:bg-emerald-500/20"
            >
              Open Enterprise Docs Index
            </Link>
          </div>
        </div>

        <div className="mt-10 grid gap-5 md:grid-cols-2">
          {moduleGuides.map((module) => (
            <section key={module.name} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-xl font-semibold">{module.name}</h2>
                  <p className="mt-2 text-sm text-slate-300 leading-7">{module.summary}</p>
                </div>
                <Link
                  href={module.href}
                  className="whitespace-nowrap rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-emerald-200 hover:bg-emerald-500/20"
                >
                  Open Module
                </Link>
              </div>

              <ol className="mt-5 space-y-2 text-sm text-slate-200">
                <li>1. {module.howTo[0]}</li>
                <li>2. {module.howTo[1]}</li>
                <li>3. {module.howTo[2]}</li>
              </ol>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}
