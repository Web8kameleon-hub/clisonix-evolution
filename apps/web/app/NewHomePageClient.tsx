'use client';

import Link from 'next/link';
import { useEffect } from 'react';

const HOW_IT_WORKS = [
  {
    step: '1',
    title: 'Connect your data',
    desc: 'Paste a URL, upload a file, or point to your existing source. No pipeline setup needed.',
  },
  {
    step: '2',
    title: 'Give one command',
    desc: 'Tell Clisonix what report you need — weekly ops, client summary, sales snapshot.',
  },
  {
    step: '3',
    title: 'Download the result',
    desc: 'Get a polished Excel or PowerPoint file in seconds. Ready to send.',
  },
];

const PLANS = [
  {
    id: 'free',
    name: 'Free',
    price: '0',
    period: '/month',
    highlight: false,
    features: ['1,000 requests / day', 'Excel & PowerPoint output', 'Core report templates'],
    cta: 'Start free',
    href: '/app',
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '29',
    period: '/month',
    highlight: true,
    features: ['Unlimited requests', 'Excel & PowerPoint output', 'Priority processing', 'Advanced report types'],
    cta: 'Start Pro',
    href: '/app',
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: '99',
    period: '/month',
    highlight: false,
    features: ['Everything in Pro', 'Custom integrations', 'Dedicated support', 'On-premise option'],
    cta: 'Contact us',
    href: '/pricing',
  },
];

function track(event: string, payload?: Record<string, unknown>) {
  try {
    window.dispatchEvent(new CustomEvent('clx:analytics', { detail: { event, ...payload } }));
    if (typeof (window as any).gtag === 'function') (window as any).gtag('event', event, payload ?? {});
  } catch {
    // silent
  }
}

export default function NewHomePageClient() {
  useEffect(() => {
    track('home_view');
  }, []);

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#fff7eb_0%,_#fffdf8_46%,_#f4f8ff_100%)] text-slate-900">
      {/* ── NAV ── */}
      <header className="sticky top-0 z-20 border-b border-amber-100/80 bg-white/90 backdrop-blur-xl">
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-4 py-3 sm:px-6">
          <Link href="/" className="flex items-center gap-3">
            <div className="grid h-9 w-9 place-items-center rounded-xl bg-slate-900 text-amber-400 shadow-lg shadow-slate-900/20 text-sm font-bold">
              C
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-amber-700">Clisonix</p>
              <p className="text-sm font-semibold text-slate-800">Report Automation</p>
            </div>
          </Link>

          <div className="flex items-center gap-3">
            <Link href="/pricing" className="hidden text-sm font-medium text-slate-600 transition hover:text-slate-900 sm:inline">
              Pricing
            </Link>
            <Link
              href="/app"
              onClick={() => track('nav_cta_click')}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-amber-400 transition hover:bg-slate-800"
            >
              Try free
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-5xl px-4 pb-24 pt-16 sm:px-6">

        {/* ── HERO ── */}
        <section className="text-center">
          <h1 className="mx-auto max-w-4xl text-4xl font-black leading-[1.1] tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
            Replace 5 hours of reporting<br className="hidden sm:block" /> with{' '}
            <span className="text-amber-500">1 command.</span>
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg leading-relaxed text-slate-500">
            Generate client-ready reports from real data in minutes — Excel or PowerPoint, ready to send.
          </p>

          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link
              href="/app"
              onClick={() => track('hero_try_click')}
              className="rounded-xl bg-slate-900 px-7 py-3.5 text-sm font-bold text-amber-400 shadow-lg shadow-slate-900/20 transition hover:bg-slate-800"
            >
              Generate my first report
            </Link>
            <Link
              href="/app"
              onClick={() => track('hero_demo_click')}
              className="rounded-xl border border-slate-300 bg-white px-7 py-3.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              Write your command
            </Link>
          </div>
          <p className="mx-auto mt-5 max-w-2xl text-sm text-slate-500">
            Built for teams tired of manual Excel copy-paste workflows.
          </p>
        </section>

        {/* ── OUTPUT PREVIEW ── */}
        <section className="mt-16">
          <p className="mb-2 text-center text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">Output preview</p>
          <h2 className="text-center text-2xl font-black text-slate-900">This is what you get.</h2>
          <p className="mx-auto mt-2 max-w-xl text-center text-sm text-slate-500">A formatted, client-ready report — not raw data. Excel or PowerPoint, ready to send.</p>

          {/* Real-output only preview card (no fabricated values) */}
          <div className="mt-8 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-lg">
            <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50 px-4 py-2.5">
              <span className="h-3 w-3 rounded-full bg-red-400" />
              <span className="h-3 w-3 rounded-full bg-amber-400" />
              <span className="h-3 w-3 rounded-full bg-emerald-400" />
              <span className="ml-3 rounded border border-slate-200 bg-white px-3 py-0.5 text-xs text-slate-500">report.xlsx / report.pptx</span>
            </div>
            <div className="grid gap-3 p-6 sm:grid-cols-2">
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.1em] text-slate-500">Excel Output</p>
                <p className="mt-2 text-sm font-semibold text-slate-800">Structured report workbook</p>
                <p className="mt-1 text-xs text-slate-500">Sheets, summary blocks, and export-ready layout generated from your connected data.</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.1em] text-slate-500">PowerPoint Output</p>
                <p className="mt-2 text-sm font-semibold text-slate-800">Presentation-ready slide deck</p>
                <p className="mt-1 text-xs text-slate-500">Narrative slides and visual summaries for stakeholder updates and client meetings.</p>
              </div>
            </div>
            <div className="border-t border-slate-100 bg-slate-50 px-4 py-2 text-xs text-slate-400">
              Example structure - your report will adapt to your data automatically.
            </div>
          </div>
        </section>

        {/* ── HOW IT WORKS ── */}
        <section className="mt-20">
          <p className="mb-2 text-center text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">How it works</p>
          <h2 className="text-center text-2xl font-black text-slate-900">Three steps. One report.</h2>

          <div className="mt-8 grid gap-5 md:grid-cols-3">
            {HOW_IT_WORKS.map((item) => (
              <div key={item.step} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50 text-sm font-black text-amber-600">
                  {item.step}
                </span>
                <h3 className="mt-3 text-base font-bold text-slate-900">{item.title}</h3>
                <p className="mt-1 text-sm leading-6 text-slate-500">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── USE CASE CARD ── */}
        <section className="mt-16 rounded-3xl border border-amber-200 bg-amber-50 p-6 sm:p-8">
          <p className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-amber-700">Most popular workflow</p>
          <h2 className="text-xl font-black text-slate-900 sm:text-2xl">Weekly Operations Report — Automated</h2>
          <p className="mt-2 max-w-xl text-sm leading-6 text-slate-600">
            Connect your source, write one command, and generate the full report in minutes.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link
              href="/app"
              onClick={() => track('usecase_webreader_click')}
              className="rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-amber-400 transition hover:bg-slate-800"
            >
              Connect source
            </Link>
            <Link
              href="/app"
              onClick={() => track('usecase_ocean_click')}
              className="rounded-xl border border-amber-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-amber-50"
            >
              Write command
            </Link>
            <Link
              href="/app"
              onClick={() => track('usecase_reporting_click')}
              className="rounded-xl border border-amber-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-amber-50"
            >
              Generate report
            </Link>
          </div>
        </section>

        {/* ── PRICING ── */}
        <section className="mt-20">
          <p className="mb-2 text-center text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">Pricing</p>
          <h2 className="text-center text-2xl font-black text-slate-900">Simple, honest pricing.</h2>

          <div className="mt-8 grid gap-5 md:grid-cols-3">
            {PLANS.map((plan) => (
              <div
                key={plan.id}
                className={`flex flex-col rounded-2xl border p-6 ${
                  plan.highlight
                    ? 'border-slate-900 bg-slate-900 text-white shadow-xl shadow-slate-900/20'
                    : 'border-slate-200 bg-white shadow-sm'
                }`}
              >
                <p className={`text-xs font-semibold uppercase tracking-[0.12em] ${plan.highlight ? 'text-amber-400' : 'text-slate-500'}`}>
                  {plan.name}
                </p>
                <p className="mt-3 text-3xl font-black">
                  {plan.price}
                  <span className={`text-base font-normal ${plan.highlight ? 'text-slate-400' : 'text-slate-500'}`}>
                    {' '}EUR{plan.period}
                  </span>
                </p>
                <ul className="mt-5 flex-1 space-y-2">
                  {plan.features.map((f) => (
                    <li key={f} className={`flex items-start gap-2 text-sm ${plan.highlight ? 'text-slate-300' : 'text-slate-600'}`}>
                      <span className={`mt-0.5 text-xs ${plan.highlight ? 'text-amber-400' : 'text-emerald-500'}`}>✓</span>
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href={plan.href}
                  onClick={() => track('pricing_cta_click', { plan: plan.id })}
                  className={`mt-6 rounded-xl px-5 py-2.5 text-center text-sm font-bold transition ${
                    plan.highlight
                      ? 'bg-amber-400 text-slate-900 hover:bg-amber-300'
                      : 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>

          <p className="mt-6 text-center text-xs font-medium text-emerald-700">
            🔒 Your data never leaves your system — on-premise option available
          </p>
          <p className="mt-5 text-center text-xs text-slate-400">
            No setup fees. Cancel anytime.{' '}
            <Link href="/pricing" className="underline underline-offset-2 hover:text-slate-700">
              Full pricing details →
            </Link>
          </p>
        </section>

        {/* ── BOTTOM CTA ── */}
        <section className="mt-20 rounded-3xl bg-slate-900 px-6 py-12 text-center">
          <h2 className="text-2xl font-black text-white sm:text-3xl">
            Your next report is one command away.
          </h2>
          <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-slate-400">
            Start free. No credit card. No setup. Just connect your data and go.
          </p>
          <Link
            href="/app"
            onClick={() => track('bottom_cta_click')}
            className="mt-6 inline-block rounded-xl bg-amber-400 px-8 py-3.5 text-sm font-bold text-slate-900 transition hover:bg-amber-300"
          >
            Generate my first report
          </Link>
          <p className="mt-8 text-xs text-slate-600">Powered by Clisonix</p>
        </section>

      </main>
    </div>
  );
}
