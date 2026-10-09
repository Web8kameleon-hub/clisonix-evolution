'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';

type TabKey = 'overview' | 'documents' | 'market-updates' | 'recent-notes' | 'investor-files' | 'contact';

type InvestorDoc = {
  title: string;
  description: string;
  category: string;
};

type MarketUpdate = {
  title: string;
  date: string;
  tags: string;
  summary: string;
};

const INVEST_REPO_URL = 'https://github.com/BledjonaAhmati/clisonix-invest';

const TABS: Array<{ key: TabKey; label: string }> = [
  { key: 'overview', label: 'Overview' },
  { key: 'documents', label: 'Documents' },
  { key: 'market-updates', label: 'Market Updates' },
  { key: 'recent-notes', label: 'Recent Notes' },
  { key: 'investor-files', label: 'Investor Files' },
  { key: 'contact', label: 'Contact' },
];

const INVESTOR_DOCS: InvestorDoc[] = [
  {
    title: 'Pitch Deck',
    description: 'Main investor presentation, prepared for direct review, PDF export, or presentation transfer.',
    category: 'Investor deck',
  },
  {
    title: 'What Clisonix Is',
    description: 'Authoritative one-page overview based on the official public platform repository.',
    category: 'Core Investor Documents',
  },
  {
    title: '1-Pager',
    description: 'Concise company overview for first meetings and introductions.',
    category: 'Core Investor Documents',
  },
  {
    title: 'Executive Summary',
    description: 'Structured executive summary for public funding and institutional review.',
    category: 'Core Investor Documents',
  },
  {
    title: 'Due Diligence Checklist',
    description: 'Prepared diligence checklist for investor and advisor review.',
    category: 'Core Investor Documents',
  },
  {
    title: 'Term Sheet',
    description: 'Reference framework for seed round negotiations.',
    category: 'Core Investor Documents',
  },
  {
    title: 'VC Target List',
    description: 'Curated DACH investor target list for fundraising outreach.',
    category: 'Funding and Outreach Materials',
  },
  {
    title: 'Funding Application Notes',
    description: 'BMWK and EIC-oriented preparation material.',
    category: 'Funding and Outreach Materials',
  },
  {
    title: 'Teaser Video Script',
    description: 'Script and storyboard for polished outbound presentation material.',
    category: 'Funding and Outreach Materials',
  },
  {
    title: 'Logo Kit',
    description: 'Official logo package for press, investor decks, and partner materials.',
    category: 'Brand and Media Assets',
  },
  {
    title: 'Android Brief',
    description: 'Android product and distribution brief prepared for investor and partner review.',
    category: 'Product Expansion Materials',
  },
];

const FINANCIAL_MODEL_SECTIONS = [
  { title: 'Assumptions', desc: 'Core commercial and operating assumptions for the model.' },
  { title: 'Revenue Model', desc: 'Revenue forecast and customer growth trajectory.' },
  { title: 'P&L', desc: 'Projected profit and loss statement through 2028.' },
  { title: 'DCF Valuation', desc: 'Discounted cash flow valuation and IRR analysis.' },
];

const MARKET_UPDATES: MarketUpdate[] = [
  {
    title: '1-Pager: Die Essenz von Clisonix',
    date: '08 April 2026',
    tags: 'Overview, Quick-Reference',
    summary:
      'Kurz, praegnant und investorenfreundlich: die Kernaussagen von Clisonix auf einer Seite mit klaren Kennzahlen und Positionierung.',
  },
  {
    title: 'Financial Model: EUR 5.23M Revenue Projection (2028)',
    date: '10 April 2026',
    tags: 'Financials, Fundraising, Business Model',
    summary:
      'Excel-ready Modell mit ARR, CAC, LTV, DCF und der gesamten Skalierungslogik von 2026 bis 2028.',
  },
  {
    title: 'Clisonix Pitchdeck - Investor Ready',
    date: '12 April 2026',
    tags: 'Pitchdeck, Fundraising',
    summary:
      'Komplett vorbereitetes 10-Slide Investor Deck mit klarer Storyline, Design-Guide und direkter Export-Bereitschaft.',
  },
];

export default function InvestWorkspace() {
  const [activeTab, setActiveTab] = useState<TabKey>('overview');

  const docCategories = useMemo(() => {
    const groups = new Map<string, InvestorDoc[]>();
    for (const doc of INVESTOR_DOCS) {
      if (!groups.has(doc.category)) groups.set(doc.category, []);
      groups.get(doc.category)?.push(doc);
    }
    return [...groups.entries()];
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-[#0b1f1c] to-slate-950 text-white">
      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-6 flex items-center justify-between gap-3">
          <Link href="/modules" className="text-sm text-slate-400 hover:text-white">
            Back to Modules
          </Link>
          <a
            href="https://www.clisonix.com"
            target="_blank"
            rel="noreferrer"
            className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-200 hover:bg-emerald-500/20"
          >
            Official Website
          </a>
        </div>

        <section className="mb-6 rounded-2xl border border-emerald-500/30 bg-gradient-to-r from-emerald-500/20 to-cyan-500/10 p-6">
          <p className="text-xs uppercase tracking-[0.16em] text-emerald-300">Investor Materials Portal</p>
          <h1 className="mt-2 text-3xl font-semibold">Clisonix Investor Materials</h1>
          <p className="mt-3 text-slate-200">
            Deep-Tech OS fuer neuronale Intelligenz | EUR 1.2M Seed Ready
          </p>
          <p className="mt-3 text-slate-300">
            Share one professional link for all investor documents. Investors and funding partners can access PDF-ready materials,
            Excel-ready financial models, and core diligence files in one place.
          </p>
          <div className="mt-4">
            <a
              href={INVEST_REPO_URL}
              target="_blank"
              rel="noreferrer"
              className="inline-block rounded-md border border-emerald-500/50 bg-emerald-500/10 px-3 py-2 text-xs text-emerald-200 hover:bg-emerald-500/20"
            >
              Open investor materials repository
            </a>
          </div>
        </section>

        <section className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <article className="rounded-xl border border-slate-700 bg-slate-900/70 p-5">
            <p className="text-xs uppercase tracking-wide text-slate-400">Uptime SLA</p>
            <p className="mt-2 text-2xl font-semibold">99.9%</p>
          </article>
          <article className="rounded-xl border border-slate-700 bg-slate-900/70 p-5">
            <p className="text-xs uppercase tracking-wide text-slate-400">Revenue Target 2028</p>
            <p className="mt-2 text-2xl font-semibold">EUR 5.23M</p>
          </article>
          <article className="rounded-xl border border-slate-700 bg-slate-900/70 p-5">
            <p className="text-xs uppercase tracking-wide text-slate-400">Projected IRR</p>
            <p className="mt-2 text-2xl font-semibold">65%</p>
          </article>
          <article className="rounded-xl border border-slate-700 bg-slate-900/70 p-5">
            <p className="text-xs uppercase tracking-wide text-slate-400">Round Status</p>
            <p className="mt-2 text-2xl font-semibold">Seed Ready</p>
          </article>
          <article className="rounded-xl border border-slate-700 bg-slate-900/70 p-5">
            <p className="text-xs uppercase tracking-wide text-slate-400">Service Footprint</p>
            <p className="mt-2 text-2xl font-semibold">106 Services</p>
          </article>
        </section>

        <section className="mb-6 flex flex-wrap gap-2">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-white text-slate-900'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </section>

        {activeTab === 'overview' ? (
          <section className="grid gap-4 md:grid-cols-2">
            <article className="rounded-xl border border-slate-700 bg-slate-900/70 p-6">
              <h2 className="text-xl font-semibold">What Clisonix Is</h2>
              <p className="mt-3 text-sm text-slate-200">
                Based on the official public repository, Clisonix is an AI and neural intelligence platform built for
                industrial and scientific use, combining production infrastructure with EEG, analytics, APIs, and developer tooling.
              </p>
              <ul className="mt-4 space-y-2 text-sm text-slate-300">
                <li>Official platform at www.clisonix.com, positioned as AI and neuroscience software infrastructure.</li>
                <li>Core capabilities: AI workflows, EEG analysis, research tooling, real-time analytics, multimodal processing.</li>
                <li>Production stack includes multi-service architecture (106 services), observability, health endpoints, billing controls, and SDKs.</li>
                <li>Platform architecture references modular engines: ALBA, ALBI, JONA, ASI and support services.</li>
              </ul>
            </article>

            <article className="rounded-xl border border-slate-700 bg-slate-900/70 p-6">
              <h2 className="text-xl font-semibold">Financial Model Snapshot</h2>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <div className="rounded-lg border border-slate-700 bg-slate-800/60 p-3">
                  <p className="text-xs text-slate-400">Revenue 2028</p>
                  <p className="text-lg font-semibold">EUR 5.23M</p>
                </div>
                <div className="rounded-lg border border-slate-700 bg-slate-800/60 p-3">
                  <p className="text-xs text-slate-400">Projected IRR</p>
                  <p className="text-lg font-semibold">65%</p>
                </div>
              </div>
              <div className="mt-4 space-y-2 text-sm text-slate-300">
                {FINANCIAL_MODEL_SECTIONS.map((section) => (
                  <div key={section.title} className="rounded-lg border border-slate-700 bg-slate-800/40 p-3">
                    <p className="font-medium text-slate-200">{section.title}</p>
                    <p className="mt-1 text-xs text-slate-400">{section.desc}</p>
                  </div>
                ))}
              </div>
            </article>
          </section>
        ) : null}

        {activeTab === 'documents' ? (
          <section className="space-y-6">
            {docCategories.map(([category, docs]) => (
              <article key={category} className="rounded-xl border border-slate-700 bg-slate-900/70 p-6">
                <h2 className="text-lg font-semibold text-emerald-200">{category}</h2>
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  {docs.map((doc) => (
                    <div key={doc.title} className="rounded-lg border border-slate-700 bg-slate-800/40 p-4">
                      <p className="text-sm font-semibold text-white">{doc.title}</p>
                      <p className="mt-2 text-xs text-slate-300">{doc.description}</p>
                      <div className="mt-3 flex gap-2">
                        <a
                          href={INVEST_REPO_URL}
                          target="_blank"
                          rel="noreferrer"
                          className="rounded-md border border-emerald-500/50 bg-emerald-500/10 px-3 py-1.5 text-xs text-emerald-200 hover:bg-emerald-500/20"
                        >
                          Open in Repository
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </article>
            ))}
          </section>
        ) : null}

        {activeTab === 'market-updates' ? (
          <section className="rounded-xl border border-slate-700 bg-slate-900/70 p-6">
            <h2 className="text-xl font-semibold">Recent Market and Company Notes</h2>
            <div className="mt-4 space-y-3">
              {MARKET_UPDATES.map((note) => (
                <article key={note.title} className="rounded-lg border border-slate-700 bg-slate-800/40 p-4">
                  <p className="text-sm font-semibold text-white">{note.title}</p>
                  <p className="mt-1 text-xs text-slate-400">
                    {note.date} | {note.tags}
                  </p>
                  <p className="mt-2 text-sm text-slate-300">{note.summary}</p>
                  <a
                    href={INVEST_REPO_URL}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-3 inline-block rounded-md border border-emerald-500/50 bg-emerald-500/10 px-3 py-1.5 text-xs text-emerald-200 hover:bg-emerald-500/20"
                  >
                    View in repository
                  </a>
                </article>
              ))}
            </div>
          </section>
        ) : null}

        {activeTab === 'recent-notes' ? (
          <section className="rounded-xl border border-slate-700 bg-slate-900/70 p-6">
            <h2 className="text-xl font-semibold">Investor Narrative</h2>
            <p className="mt-2 text-sm text-slate-300">
              Clisonix positions itself as a production-grade deep-tech AI operating system for industrial and
              scientific workflows with a clear funding path and investor-ready documentation.
            </p>
            <ul className="mt-4 space-y-2 text-sm text-slate-300">
              <li>Single-link investor distribution model to reduce attachment overhead and speed diligence workflows.</li>
              <li>Seed-ready package with pitch deck, one-pager, executive summary, and term sheet references.</li>
              <li>Financial model includes assumptions, revenue build-up, P&L, and DCF-based valuation logic.</li>
              <li>Target profile covers strategic VCs, grant programs, and institutional deep-tech funding tracks.</li>
            </ul>
          </section>
        ) : null}

        {activeTab === 'investor-files' ? (
          <section className="rounded-xl border border-slate-700 bg-slate-900/70 p-6">
            <h2 className="text-xl font-semibold">Investor File Access</h2>
            <p className="mt-2 text-sm text-slate-300">
              Access investor documents from this page link for review, sharing, and export workflows.
            </p>
            <div className="mt-4 grid gap-4 md:grid-cols-3">
              <article className="rounded-lg border border-slate-700 bg-slate-800/50 p-4">
                <p className="text-xs uppercase tracking-wide text-slate-400">Deck</p>
                <p className="mt-2 text-2xl font-semibold">10 slides</p>
              </article>
              <article className="rounded-lg border border-slate-700 bg-slate-800/50 p-4">
                <p className="text-xs uppercase tracking-wide text-slate-400">Model</p>
                <p className="mt-2 text-2xl font-semibold">Excel-ready</p>
              </article>
              <article className="rounded-lg border border-slate-700 bg-slate-800/50 p-4">
                <p className="text-xs uppercase tracking-wide text-slate-400">Data Room</p>
                <p className="mt-2 text-2xl font-semibold">Link-based</p>
              </article>
            </div>
            <div className="mt-6 grid gap-3 md:grid-cols-2">
              <a
                href="https://github.com/BledjonaAhmati/clisonix-invest/tree/main/brand"
                target="_blank"
                rel="noreferrer"
                className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 p-4 hover:bg-emerald-500/20"
              >
                <p className="text-sm font-semibold text-emerald-200">Logo Kit</p>
                <p className="mt-1 text-xs text-slate-300">Create and publish official SVG/PNG logo assets in the brand folder.</p>
              </a>
              <a
                href="https://github.com/BledjonaAhmati/clisonix-invest/tree/main/android"
                target="_blank"
                rel="noreferrer"
                className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 p-4 hover:bg-emerald-500/20"
              >
                <p className="text-sm font-semibold text-emerald-200">Android Brief</p>
                <p className="mt-1 text-xs text-slate-300">Create and publish Android roadmap, architecture, and launch notes for investors.</p>
              </a>
            </div>
          </section>
        ) : null}

        {activeTab === 'contact' ? (
          <section className="rounded-xl border border-slate-700 bg-slate-900/70 p-6">
            <h2 className="text-xl font-semibold">Contact</h2>
            <p className="mt-3 text-sm text-slate-300">Ledjan Ahmati - Founder & CEO</p>
            <p className="mt-1 text-sm text-slate-300">Email: clisonix@pm.me</p>
            <p className="mt-1 text-sm text-slate-300">Phone: +355 69 254 0305</p>
            <p className="mt-1 text-sm text-slate-300">Location: Bochum NRW</p>
            <a
              href="https://www.clisonix.com"
              target="_blank"
              rel="noreferrer"
              className="mt-4 inline-block rounded-md border border-emerald-500/50 bg-emerald-500/10 px-3 py-1.5 text-xs text-emerald-200 hover:bg-emerald-500/20"
            >
              www.clisonix.com
            </a>
          </section>
        ) : null}
      </main>
    </div>
  );
}

