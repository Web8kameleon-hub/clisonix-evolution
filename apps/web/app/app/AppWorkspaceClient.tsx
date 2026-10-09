'use client';

import Link from 'next/link';
import { useCallback, useEffect, useRef, useState } from 'react';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8001';

const OUTPUT_TYPES = [
  { key: 'excel', label: 'Excel', ext: 'xlsx' },
  { key: 'pdf',   label: 'PDF',   ext: 'pdf' },
  { key: 'word',  label: 'Word',  ext: 'docx' },
  { key: 'pptx',  label: 'PPT',   ext: 'pptx' },
] as const;

type OutputKey = (typeof OUTPUT_TYPES)[number]['key'];

const TEMPLATES = [
  { key: 'sales_report_pack',      label: 'Sales Report Pack',       desc: 'Weekly/monthly KPI, pipeline, close rate' },
  { key: 'ops_weekly_brief',       label: 'Operations Weekly Brief', desc: 'Ops metrics, incidents, SLA status' },
  { key: 'research_summary_pack',  label: 'Research Summary Pack',   desc: 'Sources, key findings, citations' },
] as const;

type TemplateKey = (typeof TEMPLATES)[number]['key'];

const QUICK_REPORT_PRESETS = [
  {
    key: 'eu-demography',
    label: 'Europe Demography',
    sourceHint: 'europa demografia',
    command: 'Europe demography report by year with references and source links.',
    template: 'research_summary_pack' as const,
    output: 'pdf' as const,
  },
  {
    key: 'usa-debt-economy',
    label: 'USA Economy & Debt',
    sourceHint: 'usa ekonomia borxhi statistikat',
    command: 'USA economy and public debt report with key statistics, trends, and references.',
    template: 'research_summary_pack' as const,
    output: 'excel' as const,
  },
  {
    key: 'eu-energy',
    label: 'Europe Energy Pulse',
    sourceHint: 'europa energjia statistikat',
    command: 'Europe energy market snapshot with production, demand, price trend, and references.',
    template: 'ops_weekly_brief' as const,
    output: 'pptx' as const,
  },
  {
    key: 'crypto-weather-ops',
    label: 'Crypto + Weather Ops',
    sourceHint: 'crypto weather operations',
    command: 'Operational dashboard report combining crypto market movement and weather risk signals with references.',
    template: 'ops_weekly_brief' as const,
    output: 'word' as const,
  },
];

type JobStatus = 'queued' | 'processing' | 'complete' | 'failed';

interface Job {
  job_id: string;
  status: JobStatus;
  command: string;
  output_format: OutputKey;
  created_at: string;
  updated_at: string;
  download_url: string | null;
  error: string | null;
}

const APP_LAUNCHER_ITEMS = [
  { label: 'API Marketplace', href: '/marketplace', desc: 'Pay-per-use API keys for power users' },
  { label: 'API Keys',        href: '/modules/account', desc: 'Manage credentials and usage' },
  { label: 'IoT / Pay-per-use', href: '/modules/my-data-dashboard', desc: 'Device streams and metered ops' },
  { label: 'Developer Docs',  href: '/developers', desc: 'OpenAPI reference and SDKs' },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function track(event: string, payload?: Record<string, unknown>) {
  try {
    window.dispatchEvent(new CustomEvent('clx:analytics', { detail: { event, ...payload } }));
    if (typeof (window as any).gtag === 'function') (window as any).gtag('event', event, payload ?? {});
  } catch { /* silent */ }
}

function fmtTime(iso: string) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function normalizeInputToUrl(input: string): string {
  const value = input.trim();
  if (!value) return '';
  if (/^https?:\/\//i.test(value)) return value;
  // Treat plain text (e.g. "bota") as search query.
  return `https://duckduckgo.com/?q=${encodeURIComponent(value)}`;
}

const STATUS_COLOR: Record<JobStatus, string> = {
  queued:     'text-amber-600 bg-amber-50 border-amber-200',
  processing: 'text-blue-600 bg-blue-50 border-blue-200',
  complete:   'text-emerald-700 bg-emerald-50 border-emerald-200',
  failed:     'text-red-700 bg-red-50 border-red-200',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function AppWorkspaceClient() {
  const [activeTab, setActiveTab]           = useState<'reader' | 'dashboard' | 'public'>('reader');
  const [urlInput, setUrlInput]             = useState('');
  const [fileLabel, setFileLabel]           = useState<string | null>(null);
  const [sourceSummary, setSourceSummary]   = useState<string | null>(null);
  const [sourceLoading, setSourceLoading]   = useState(false);
  const [sourceError, setSourceError]       = useState<string | null>(null);
  const [pendingSource, setPendingSource]   = useState<string | null>(null); // source_id for "send to report"
  const [sourceIds, setSourceIds]           = useState<string[]>([]);

  const [command, setCommand]               = useState('');
  const [selectedOutput, setSelectedOutput] = useState<OutputKey>('pdf');
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateKey>('ops_weekly_brief');

  const [jobs, setJobs]                     = useState<Job[]>([]);
  const [submitting, setSubmitting]         = useState(false);
  const [submitError, setSubmitError]       = useState<string | null>(null);

  const [showLauncher, setShowLauncher]     = useState(false);

  const fileRef   = useRef<HTMLInputElement>(null);
  const pollRef   = useRef<ReturnType<typeof setInterval> | null>(null);

  const applyQuickPreset = (presetKey: string) => {
    const preset = QUICK_REPORT_PRESETS.find((p) => p.key === presetKey);
    if (!preset) return;
    setCommand(preset.command);
    setSelectedTemplate(preset.template);
    setSelectedOutput(preset.output);
    setUrlInput(preset.sourceHint);
    track('quick_preset_apply', { preset: preset.key, template: preset.template, output: preset.output });
  };

  // ---------------------------------------------------------------------------
  // Polling
  // ---------------------------------------------------------------------------
  const pollJob = useCallback(async (job_id: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/reports/jobs/${job_id}`, {
        headers: { 'X-API-Key': localStorage.getItem('clx_api_key') ?? '' },
      });
      if (!res.ok) return;
      const data: { job: Job } = await res.json();
      setJobs((prev) => prev.map((j) => (j.job_id === data.job.job_id ? data.job : j)));
      if (data.job.status === 'complete' || data.job.status === 'failed') {
        track('job_' + data.job.status, { job_id });
      }
    } catch { /* network — will retry */ }
  }, []);

  useEffect(() => {
    const activeJobs = jobs.filter((j) => j.status === 'queued' || j.status === 'processing');
    if (activeJobs.length === 0) {
      if (pollRef.current) clearInterval(pollRef.current);
      pollRef.current = null;
      return;
    }
    if (!pollRef.current) {
      pollRef.current = setInterval(() => {
        activeJobs.forEach((j) => pollJob(j.job_id));
      }, 2000);
    }
    return () => {
      if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
    };
  }, [jobs, pollJob]);

  // ---------------------------------------------------------------------------
  // Web Reader — Ingest URL
  // ---------------------------------------------------------------------------
  const ingestUrlValue = async (url: string) => {
    if (!url.trim()) return;
    const targetUrl = normalizeInputToUrl(url);
    if (!targetUrl) return;
    setSourceLoading(true);
    setSourceError(null);
    setSourceSummary(null);
    track('reader_ingest_url');
    try {
      const res = await fetch(`${API_BASE}/api/v1/reader/ingest-url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': localStorage.getItem('clx_api_key') ?? '' },
        body: JSON.stringify({ url: targetUrl }),
      });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const data = await res.json();
      setSourceSummary(data.source.preview ?? '(no preview)');
      setPendingSource(data.source.source_id);
      if (data.source.source_id) {
        setSourceIds((prev) => [data.source.source_id, ...prev.filter((id) => id !== data.source.source_id)]);
      }
    } catch (e: any) {
      setSourceError(e.message ?? 'Failed to fetch URL');
    } finally {
      setSourceLoading(false);
    }
  };

  const ingestUrl = async () => {
    await ingestUrlValue(urlInput.trim());
  };

  const browseSearch = async () => {
    const query = urlInput.trim();
    if (!query) return;
    const targetUrl = normalizeInputToUrl(query);
    if (!/^https?:\/\//i.test(query)) setUrlInput(targetUrl);
    track('reader_browse_search', { query });
    await ingestUrlValue(targetUrl);
  };

  // ---------------------------------------------------------------------------
  // Web Reader — Ingest File
  // ---------------------------------------------------------------------------
  const ingestFile = async (file: File) => {
    setSourceLoading(true);
    setSourceError(null);
    setSourceSummary(null);
    setFileLabel(file.name);
    const form = new FormData();
    form.append('file', file);
    try {
      const res = await fetch(`${API_BASE}/api/v1/reader/ingest-file`, {
        method: 'POST',
        headers: { 'X-API-Key': localStorage.getItem('clx_api_key') ?? '' },
        body: form,
      });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const data = await res.json();
      setSourceSummary(data.source.preview ?? '(no preview)');
      setPendingSource(data.source.source_id);
      if (data.source.source_id) {
        setSourceIds((prev) => [data.source.source_id, ...prev.filter((id) => id !== data.source.source_id)]);
      }
    } catch (e: any) {
      setSourceError(e.message ?? 'Failed to upload file');
    } finally {
      setSourceLoading(false);
    }
  };

  const sendToReport = () => {
    if (sourceSummary) setCommand((prev) => prev || `Summarize and format as report: ${sourceSummary.slice(0, 120)}`);
    if (pendingSource) {
      setSourceIds((prev) => [pendingSource, ...prev.filter((id) => id !== pendingSource)]);
    }
    setActiveTab('reader');
    track('reader_send_to_report');
  };

  // ---------------------------------------------------------------------------
  // Submit command → create job
  // ---------------------------------------------------------------------------
  const submitCommand = async () => {
    if (!command.trim()) return;
    setSubmitting(true);
    setSubmitError(null);
    track('command_submit', { format: selectedOutput, template: selectedTemplate });
    try {
      const res = await fetch(`${API_BASE}/api/v1/commands/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': localStorage.getItem('clx_api_key') ?? '' },
        body: JSON.stringify({
          command,
          output_format: selectedOutput,
          template: selectedTemplate,
          sources: sourceIds,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `${res.status}`);
      }
      const data: { job: Job } = await res.json();
      setJobs((prev) => [data.job, ...prev]);
      setActiveTab('dashboard');
      setCommand('');
    } catch (e: any) {
      setSubmitError(e.message ?? 'Failed to submit command');
    } finally {
      setSubmitting(false);
    }
  };

  // ---------------------------------------------------------------------------
  // Download file
  // ---------------------------------------------------------------------------
  const downloadJob = (job: Job) => {
    if (!job.download_url) return;
    const ext = OUTPUT_TYPES.find((o) => o.key === job.output_format)?.ext ?? job.output_format;
    const a = document.createElement('a');
    a.href = `${API_BASE}${job.download_url}`;
    a.download = `clisonix_report_${job.job_id.slice(0, 8)}.${ext}`;
    a.click();
    track('download', { format: job.output_format });
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <div className="flex min-h-screen flex-col bg-[radial-gradient(circle_at_top_right,_#fff8ed_0%,_#fffdf8_40%,_#f7fbff_100%)] text-slate-900">

      {/* ── HEADER ────────────────────────────────────────── */}
      <header className="sticky top-0 z-30 border-b border-amber-200/60 bg-white/90 backdrop-blur-xl">
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-4 py-2 sm:px-6">
          <Link href="/" className="flex items-center gap-2">
            <div className="grid h-7 w-7 place-items-center rounded-lg bg-slate-900 text-xs font-black text-amber-400">C</div>
            <span className="text-sm font-bold tracking-tight text-slate-800">Clisonix</span>
          </Link>

          {/* Tabs */}
          <nav className="flex gap-1">
            {([['reader','Web Reader'],['dashboard','Dashboard'],['public','Public Page']] as const).map(([tab, label]) => (
              <button
                key={tab}
                type="button"
                onClick={() => { setActiveTab(tab); if (tab === 'public') window.open('/', '_blank'); }}
                className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                  activeTab === tab ? 'bg-slate-900 text-amber-400' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-800'
                }`}
              >
                {label}
              </button>
            ))}
            <Link
              href="/modules/curiosity-ocean"
              className="rounded-lg px-3 py-1.5 text-xs font-semibold text-slate-500 transition hover:bg-slate-100 hover:text-slate-800"
            >
              Ocean Curiosity
            </Link>
          </nav>

          {/* App Launcher */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowLauncher((v) => !v)}
              className="grid h-8 w-8 grid-cols-3 grid-rows-3 place-items-center gap-px rounded-lg border border-slate-200 bg-white shadow-sm transition hover:bg-slate-50"
              aria-label="Open advanced tools"
            >
              {Array.from({ length: 9 }).map((_, i) => (
                <span key={i} className="h-[4px] w-[4px] rounded-full bg-slate-500" />
              ))}
            </button>
            {showLauncher && (
              <div className="absolute right-0 top-10 z-50 w-64 rounded-2xl border border-slate-200 bg-white p-2 shadow-2xl">
                <p className="mb-1 px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest text-slate-400">Power User Tools</p>
                {APP_LAUNCHER_ITEMS.map((item) => (
                  <Link key={item.label} href={item.href} onClick={() => setShowLauncher(false)}
                    className="block rounded-xl px-3 py-2 transition hover:bg-slate-100">
                    <p className="text-sm font-semibold text-slate-800">{item.label}</p>
                    <p className="text-xs text-slate-500">{item.desc}</p>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Archive & Search button */}
        <div className="mx-auto flex w-full max-w-5xl items-center gap-2 px-4 pb-1.5 sm:px-6">
          <Link href="/modules/archive" className="rounded-full border border-slate-200 bg-white px-3 py-0.5 text-xs font-medium text-slate-500 shadow-sm transition hover:bg-slate-50 hover:text-slate-800">
            📜 Archive & Search
          </Link>
        </div>
      </header>

      {/* ── MAIN LAYOUT ────────────────────────────────────── */}
      <div className="mx-auto flex w-full max-w-5xl flex-1 gap-4 px-4 py-5 sm:px-6">

        {/* ── LEFT: main content area ───────────────────────── */}
        <main className="flex-1 min-w-0">

          {/* ── TAB: WEB READER ───────────────────────────────── */}
          {activeTab === 'reader' && (
            <div className="space-y-4">
              <h2 className="text-base font-bold text-slate-800">Web Reader <span className="ml-2 text-xs font-normal text-slate-400">Load → Read → Use</span></h2>

              {/* URL input */}
              <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <label className="mb-2 block text-xs font-bold uppercase tracking-widest text-slate-500">URL</label>
                <div className="flex gap-2">
                  <input
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && browseSearch()}
                    placeholder="https://example.com/report-source or search term"
                    className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none ring-amber-400 focus:border-amber-400 focus:ring-2"
                  />
                  <button
                    type="button"
                    onClick={browseSearch}
                    disabled={sourceLoading || !urlInput.trim()}
                    className="rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-xs font-bold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
                  >
                    Browse Search
                  </button>
                  <button
                    type="button"
                    onClick={ingestUrl}
                    disabled={sourceLoading || !urlInput.trim()}
                    className="rounded-xl bg-slate-900 px-4 py-2.5 text-xs font-bold text-amber-400 transition hover:bg-slate-800 disabled:opacity-50"
                  >
                    {sourceLoading ? '…' : 'Load'}
                  </button>
                </div>
              </div>

              {/* File upload */}
              <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-5 shadow-sm">
                <p className="mb-2 text-xs font-bold uppercase tracking-widest text-slate-500">Or Upload File</p>
                <button
                  type="button"
                  onClick={() => fileRef.current?.click()}
                  className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-100"
                >
                  {fileLabel ?? 'Choose file…'}
                </button>
                <input ref={fileRef} type="file" className="hidden"
                  onChange={(e) => { const f = e.target.files?.[0]; if (f) ingestFile(f); }} />
              </div>

              {/* Error */}
              {sourceError && (
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{sourceError}</div>
              )}

              {/* Summary preview */}
              {sourceSummary && (
                <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5 shadow-sm">
                  <p className="mb-2 text-xs font-bold uppercase tracking-widest text-emerald-600">Preview</p>
                  <p className="text-sm leading-relaxed text-slate-700">{sourceSummary}</p>
                  <button
                    type="button"
                    onClick={sendToReport}
                    className="mt-3 rounded-xl bg-slate-900 px-4 py-2 text-xs font-bold text-amber-400 transition hover:bg-slate-800"
                  >
                    Send to Report →
                  </button>
                </div>
              )}

              {/* Command + template + format */}
              <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm space-y-4">
                <div>
                  <p className="mb-2 text-xs font-bold uppercase tracking-widest text-slate-500">Quick Menu (Real Report Presets)</p>
                  <div className="flex flex-wrap gap-2">
                    {QUICK_REPORT_PRESETS.map((preset) => (
                      <button
                        key={preset.key}
                        type="button"
                        onClick={() => applyQuickPreset(preset.key)}
                        className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:bg-slate-100"
                      >
                        {preset.label}
                      </button>
                    ))}
                  </div>
                  <p className="mt-2 text-xs text-slate-500">Click one preset, load a source, then generate report.</p>
                </div>

                <div>
                  <label className="mb-2 block text-xs font-bold uppercase tracking-widest text-slate-500">Command</label>
                  <textarea
                    value={command}
                    onChange={(e) => setCommand(e.target.value)}
                    rows={2}
                    placeholder="Generate weekly ops report for sales + ops team"
                    className="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none ring-amber-400 focus:border-amber-400 focus:ring-2"
                  />
                </div>

                <div>
                  <p className="mb-2 text-xs font-bold uppercase tracking-widest text-slate-500">Template</p>
                  <div className="flex flex-col gap-1.5">
                    {TEMPLATES.map((t) => (
                      <button
                        key={t.key}
                        type="button"
                        onClick={() => setSelectedTemplate(t.key)}
                        className={`flex items-start gap-3 rounded-xl border px-4 py-2.5 text-left text-sm transition ${
                          selectedTemplate === t.key
                            ? 'border-amber-400 bg-amber-50 text-slate-900'
                            : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                        }`}
                      >
                        <span className={`mt-0.5 h-3 w-3 shrink-0 rounded-full border-2 ${selectedTemplate === t.key ? 'border-amber-500 bg-amber-500' : 'border-slate-300'}`} />
                        <span>
                          <span className="font-semibold">{t.label}</span>
                          <span className="ml-2 text-xs text-slate-400">{t.desc}</span>
                        </span>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="mb-2 text-xs font-bold uppercase tracking-widest text-slate-500">Output Format</p>
                  <div className="flex gap-2 flex-wrap">
                    {OUTPUT_TYPES.map((o) => (
                      <button
                        key={o.key}
                        type="button"
                        onClick={() => setSelectedOutput(o.key)}
                        className={`rounded-lg border px-4 py-2 text-sm font-bold transition ${
                          selectedOutput === o.key
                            ? 'border-amber-500 bg-amber-500 text-slate-900 shadow-sm'
                            : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                        }`}
                      >
                        {o.label}
                      </button>
                    ))}
                  </div>
                </div>

                {submitError && (
                  <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{submitError}</p>
                )}

                {!submitError && sourceIds.length === 0 && (
                  <p className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-800">
                    Ingest a URL or file first. Real data source is required before report generation.
                  </p>
                )}

                <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-600">
                  <p className="font-semibold text-slate-700">What Clisonix can generate in record time:</p>
                  <p className="mt-1">Demography reports, economy/debt snapshots, KPI packs, operations briefs, and source-linked research summaries.</p>
                </div>

                <button
                  type="button"
                  onClick={submitCommand}
                  disabled={submitting || !command.trim() || sourceIds.length === 0}
                  className="mt-1 flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 py-3.5 text-sm font-bold text-amber-400 shadow-lg shadow-slate-900/20 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {submitting ? (
                    <><span className="h-4 w-4 animate-spin rounded-full border-2 border-amber-400 border-t-transparent" /> Submitting…</>
                  ) : 'Generate Report'}
                </button>
              </div>
            </div>
          )}

          {/* ── TAB: DASHBOARD / JOBS ──────────────────────────── */}
          {activeTab === 'dashboard' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-bold text-slate-800">Report Jobs</h2>
                <button
                  type="button"
                  onClick={() => setActiveTab('reader')}
                  className="rounded-xl bg-slate-900 px-4 py-2 text-xs font-bold text-amber-400 transition hover:bg-slate-800"
                >
                  + New Report
                </button>
              </div>

              {jobs.length === 0 && (
                <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center">
                  <p className="text-sm text-slate-400">No jobs yet. Go to Web Reader and generate a report.</p>
                </div>
              )}

              {jobs.map((job) => (
                <div key={job.job_id} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="truncate text-sm font-semibold text-slate-800">{job.command}</p>
                      <p className="text-xs text-slate-400">{job.job_id.slice(0, 8)}… · {job.output_format.toUpperCase()} · {fmtTime(job.created_at)}</p>
                    </div>
                    <span className={`shrink-0 rounded-full border px-2.5 py-0.5 text-xs font-bold ${STATUS_COLOR[job.status]}`}>
                      {job.status}
                    </span>
                  </div>

                  {/* Status timeline */}
                  <div className="mt-3 flex gap-0 overflow-hidden rounded-xl">
                    {(['queued','processing','complete'] as const).map((s, i) => {
                      const done = job.status === 'complete' ? i <= 2 : job.status === 'processing' ? i <= 1 : job.status === 'queued' ? i <= 0 : false;
                      const active = job.status === s;
                      return (
                        <div key={s} className={`flex-1 py-1 text-center text-[10px] font-bold uppercase tracking-wider transition ${
                          job.status === 'failed' ? 'bg-red-100 text-red-400' :
                          done ? 'bg-emerald-500 text-white' :
                          active ? 'bg-amber-400 text-slate-900' :
                          'bg-slate-100 text-slate-400'
                        }`}>
                          {s}
                        </div>
                      );
                    })}
                  </div>

                  {job.status === 'failed' && job.error && (
                    <p className="mt-2 text-xs text-red-600">{job.error}</p>
                  )}

                  {job.status === 'complete' && (
                    <button
                      type="button"
                      onClick={() => downloadJob(job)}
                      className="mt-3 rounded-xl bg-slate-900 px-4 py-2 text-xs font-bold text-amber-400 transition hover:bg-slate-800"
                    >
                      Download {job.output_format.toUpperCase()} ↓
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </main>

        {/* ── RIGHT UTILITY RAIL: Ocean Curiosity Chat ──────────── */}
        <aside className="hidden w-36 flex-col items-end pt-1 md:flex">
          <Link
            href="/modules/curiosity-ocean"
            className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-bold uppercase tracking-[0.08em] text-slate-600 shadow-sm transition hover:bg-slate-50 hover:text-slate-800"
          >
            🌊 Ocean Chat
          </Link>
        </aside>

        {/* Mobile chat toggle */}
        <Link
          href="/modules/curiosity-ocean"
          className="fixed bottom-4 right-4 z-40 flex h-12 w-12 items-center justify-center rounded-full bg-slate-900 text-xl shadow-xl transition hover:bg-slate-800 md:hidden"
        >
          🌊
        </Link>
      </div>
    </div>
  );
}
