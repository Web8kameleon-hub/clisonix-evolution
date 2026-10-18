'use client'

import Link from 'next/link'
import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'next/navigation'

type Manifest = {
  lab_id: string
  name: string
  city: string
  country: string
  lab_type: string
  function: string
  status: string
  capabilities: string[]
  runtime?: {
    port?: number
    analysis_upstream_configured?: boolean
    analysis_contract?: string
    trace_provider?: string
    identity_source?: string
  }
}

type LabObservation = {
  lab_id: string
  service: string
  name: string
  function: string
  city: string
  country: string
  lab_type: string
  status: string
  analysis_ready?: boolean
  latency_ms?: number | null
  health?: Record<string, unknown> | null
  manifest?: Manifest
  checked_at?: string
}

type AnalysisResponse = {
  schema?: string
  status?: string
  trace_id?: string
  result?: unknown
  evidence?: Record<string, unknown>
  timestamp?: string
}

type TraceEvent = {
  source?: string
  kind?: string
  level?: string
  message?: string
  timestamp?: string
  trace_id?: string
  payload?: Record<string, unknown>
}

type Section = { key: string; title: string; description: string }

const CITY_LABS_API = '/api/city-labs/api/v1'

const TYPE_SECTIONS: Record<string, Section[]> = {
  AI: [
    { key: 'models', title: 'Models & agents', description: 'Available intelligence capabilities, agent routes and execution surfaces.' },
    { key: 'experiments', title: 'AI experiments', description: 'Traceable model, routing and evaluation workflows.' },
  ],
  Medical: [
    { key: 'clinical', title: 'Clinical signals', description: 'Clinical and biomedical inputs exposed by the laboratory runtime.' },
    { key: 'research', title: 'Research workflows', description: 'Experiments, analysis tasks and validated outputs.' },
  ],
  IoT: [
    { key: 'devices', title: 'Devices & sensors', description: 'Connected devices, edge nodes and sensor telemetry.' },
    { key: 'events', title: 'Live events', description: 'Streaming observations and device-originated events.' },
  ],
  Marine: [
    { key: 'ocean', title: 'Ocean telemetry', description: 'Marine, environmental and observational data streams.' },
    { key: 'missions', title: 'Marine missions', description: 'Active collection and analysis workflows.' },
  ],
  Environmental: [
    { key: 'environment', title: 'Environment', description: 'Climate, pollution and ecological telemetry.' },
    { key: 'anomalies', title: 'Anomalies', description: 'Events requiring analysis or intervention.' },
  ],
  Security: [
    { key: 'threats', title: 'Threat surface', description: 'Security events, isolation state and runtime trust signals.' },
    { key: 'response', title: 'Response workflows', description: 'Detection, routing, containment and recovery.' },
  ],
  Energy: [
    { key: 'grid', title: 'Energy telemetry', description: 'Power-system signals, production and consumption context.' },
    { key: 'forecast', title: 'Forecast & optimization', description: 'Analysis and adaptive operational workflows.' },
  ],
  Finance: [
    { key: 'market', title: 'Market context', description: 'Financial data and risk-analysis inputs.' },
    { key: 'risk', title: 'Risk workflows', description: 'Traceable analysis, decisions and evidence.' },
  ],
  Robotics: [
    { key: 'robots', title: 'Robotic fleet', description: 'Robots, controllers, sensors and edge state.' },
    { key: 'missions', title: 'Missions', description: 'Autonomous tasks, execution and recovery state.' },
  ],
  Data: [
    { key: 'streams', title: 'Data streams', description: 'Live datasets, pipelines and processing state.' },
    { key: 'observability', title: 'Observability', description: 'Metrics, traces and data quality signals.' },
  ],
}

const COMMON_SECTIONS: Section[] = [
  { key: 'live', title: 'Live', description: 'Runtime health, probe latency, streams and connected resources.' },
  { key: 'capabilities', title: 'Capabilities', description: 'Functions declared by the active laboratory manifest.' },
  { key: 'intelligence', title: 'Intelligence', description: 'Run a context-aware Ocean analysis from this laboratory.' },
  { key: 'memory', title: 'Memory', description: 'Trace evidence, contextual continuity and laboratory knowledge.' },
  { key: 'system', title: 'System', description: 'OS-CLX, Kloud routing, traces, isolation and recovery.' },
]

export default function LabWorkspacePage() {
  const params = useParams<{ labId: string }>()
  const requestedId = decodeURIComponent(params.labId)
  const [lab, setLab] = useState<LabObservation | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeSection, setActiveSection] = useState('live')
  const [goal, setGoal] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisError, setAnalysisError] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)
  const [traceEvents, setTraceEvents] = useState<TraceEvent[]>([])

  useEffect(() => {
    let active = true
    const load = async () => {
      try {
        const response = await fetch(`${CITY_LABS_API}/labs/${encodeURIComponent(requestedId)}?live=true`, { cache: 'no-store' })
        if (!response.ok) throw new Error(`City Lab ${requestedId} HTTP ${response.status}`)
        const payload = await response.json()
        if (active) {
          setLab(payload)
          setError(null)
        }
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : 'Could not load laboratory')
      } finally {
        if (active) setLoading(false)
      }
    }
    load()
    const timer = window.setInterval(load, 5000)
    return () => {
      active = false
      window.clearInterval(timer)
    }
  }, [requestedId])

  const manifest = lab?.manifest
  const labType = manifest?.lab_type || lab?.lab_type || 'General'
  const sections = useMemo(() => [
    ...COMMON_SECTIONS,
    ...(TYPE_SECTIONS[labType] || [{ key: 'domain', title: `${labType} workspace`, description: 'Domain-specific tools and laboratory workflows.' }]),
  ], [labType])
  const selected = sections.find((section) => section.key === activeSection) || sections[0]
  const isLive = lab?.status === 'healthy'
  const analysisReady = Boolean(lab?.analysis_ready ?? manifest?.runtime?.analysis_upstream_configured)
  const capabilities = manifest?.capabilities || []

  const loadTrace = async (traceId: string) => {
    const response = await fetch(`${CITY_LABS_API}/labs/${encodeURIComponent(requestedId)}/traces/${encodeURIComponent(traceId)}`, { cache: 'no-store' })
    if (!response.ok) return
    const payload = await response.json()
    setTraceEvents(Array.isArray(payload.events) ? payload.events : [])
  }

  const runAnalysis = async () => {
    const message = goal.trim()
    if (!message || analyzing) return
    setAnalyzing(true)
    setAnalysisError(null)
    setAnalysis(null)
    setTraceEvents([])
    const traceId = crypto.randomUUID()
    try {
      const response = await fetch(`${CITY_LABS_API}/labs/${encodeURIComponent(requestedId)}/analyze`, {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'x-trace-id': traceId },
        body: JSON.stringify({ goal: message, context: { surface: 'kameleon-ui', section: activeSection } }),
      })
      const payload = await response.json().catch(() => ({}))
      if (!response.ok) throw new Error(payload?.detail || `Analysis HTTP ${response.status}`)
      setAnalysis(payload)
      await loadTrace(payload.trace_id || traceId)
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : 'Analysis failed')
      await loadTrace(traceId)
    } finally {
      setAnalyzing(false)
    }
  }

  if (loading) return <main className="min-h-screen bg-slate-950 p-8 text-slate-300">Opening live Kameleon workspace…</main>

  if (error || !lab) {
    return (
      <main className="min-h-screen bg-slate-950 p-8 text-slate-200">
        <div className="mx-auto max-w-4xl rounded-2xl border border-red-900/60 bg-red-950/20 p-6">
          <h1 className="text-xl font-semibold">City Lab unavailable</h1>
          <p className="mt-2 text-red-300">{error}</p>
          <Link href="/labs" className="mt-5 inline-block text-cyan-400">← Back to City Labs</Link>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-950/95">
        <div className="mx-auto max-w-[1500px] px-6 py-6">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-3 text-xs uppercase tracking-[0.18em]">
                <span className="text-cyan-400">Kameleon workspace</span><span className="text-slate-600">/</span><span className="text-slate-400">{labType}</span>
              </div>
              <h1 className="mt-2 text-3xl font-semibold">{manifest?.name || lab.name}</h1>
              <p className="mt-2 text-sm text-slate-400">{manifest?.city || lab.city}, {manifest?.country || lab.country} · {manifest?.function || lab.function}</p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`rounded-full px-3 py-1.5 text-xs ${isLive ? 'bg-emerald-950 text-emerald-300' : lab.status === 'degraded' ? 'bg-amber-950 text-amber-300' : 'bg-red-950/60 text-red-300'}`}>{lab.status}</span>
              <span className={`rounded-full px-3 py-1.5 text-xs ${analysisReady ? 'bg-cyan-950 text-cyan-300' : 'bg-amber-950 text-amber-300'}`}>{analysisReady ? 'analysis ready' : 'runtime only'}</span>
              <Link href="/labs" className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-900">All labs</Link>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1500px] gap-6 px-6 py-6 lg:grid-cols-[240px_minmax(0,1fr)_320px]">
        <aside className="rounded-2xl border border-slate-800 bg-slate-900/60 p-3">
          <div className="px-3 pb-3 pt-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Environment</div>
          <nav className="space-y-1">
            {sections.map((section) => (
              <button key={section.key} onClick={() => setActiveSection(section.key)} className={`w-full rounded-xl px-3 py-3 text-left text-sm transition ${activeSection === section.key ? 'bg-cyan-950/70 text-cyan-100 ring-1 ring-cyan-800' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'}`}>
                {section.title}
              </button>
            ))}
          </nav>
        </aside>

        <section className="min-w-0 space-y-6">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <div className="text-xs uppercase tracking-[0.18em] text-cyan-400">{selected.key}</div>
            <h2 className="mt-2 text-2xl font-semibold">{selected.title}</h2>
            <p className="mt-2 text-slate-400">{selected.description}</p>
            <div className="mt-6 grid gap-4 md:grid-cols-4">
              <Metric label="Lab ID" value={lab.lab_id} />
              <Metric label="Runtime" value={lab.status} />
              <Metric label="Analysis" value={analysisReady ? 'ready' : 'not ready'} />
              <Metric label="Probe" value={lab.latency_ms == null ? '—' : `${lab.latency_ms} ms`} />
            </div>
          </div>

          <div className="rounded-2xl border border-cyan-900/60 bg-slate-900/70 p-6">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400">Lab operator</div>
                <h3 className="mt-2 text-xl font-semibold">Give this laboratory a goal</h3>
                <p className="mt-1 text-sm text-slate-400">The request carries this city, domain, capabilities and one trace ID into Ocean.</p>
              </div>
              <span className={`rounded-full px-3 py-1.5 text-xs ${analysisReady ? 'bg-emerald-950 text-emerald-300' : 'bg-amber-950 text-amber-300'}`}>{analysisReady ? 'Ocean connected' : 'Ocean unavailable'}</span>
            </div>
            <textarea
              value={goal}
              onChange={(event) => setGoal(event.target.value)}
              placeholder={`Example: Analyze the current ${labType.toLowerCase()} context for ${manifest?.city || lab.city} and identify the most important anomaly or next action.`}
              rows={4}
              className="mt-5 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none ring-cyan-500/20 transition focus:border-cyan-500 focus:ring-4"
            />
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <button
                onClick={runAnalysis}
                disabled={!analysisReady || !goal.trim() || analyzing}
                className="rounded-xl bg-cyan-500 px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {analyzing ? 'Executing…' : 'Execute through Ocean'}
              </button>
              <span className="text-xs text-slate-500">No synthetic result is generated if the execution path is unavailable.</span>
            </div>
            {analysisError && <div className="mt-4 rounded-xl border border-red-900/60 bg-red-950/20 p-4 text-sm text-red-300">{analysisError}</div>}
          </div>

          {analysis && (
            <div className="rounded-2xl border border-emerald-900/50 bg-slate-900/70 p-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-400">Execution result</div>
                  <h3 className="mt-2 text-xl font-semibold">Ocean completed the laboratory goal</h3>
                </div>
                <span className="rounded-full bg-emerald-950 px-3 py-1 text-xs text-emerald-300">{analysis.status || 'completed'}</span>
              </div>
              <div className="mt-5 whitespace-pre-wrap rounded-xl border border-slate-800 bg-slate-950 p-4 text-sm leading-6 text-slate-200">
                {renderValue(analysis.result)}
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <Metric label="Trace ID" value={analysis.trace_id || '—'} />
                <Metric label="Contract" value={analysis.schema || '—'} />
                <Metric label="Latency" value={String(analysis.evidence?.latency_ms ?? '—') + (analysis.evidence?.latency_ms != null ? ' ms' : '')} />
              </div>
            </div>
          )}

          {traceEvents.length > 0 && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-violet-400">Signal Fabric trace</div>
              <h3 className="mt-2 text-xl font-semibold">Execution evidence</h3>
              <div className="mt-5 space-y-3">
                {traceEvents.map((event, index) => (
                  <div key={`${event.timestamp || index}-${index}`} className="grid gap-2 rounded-xl border border-slate-800 bg-slate-950 p-4 md:grid-cols-[170px_1fr_auto] md:items-center">
                    <div className="text-xs text-slate-500">{event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : '—'}</div>
                    <div>
                      <div className="text-sm font-medium text-slate-200">{event.kind || 'event'}</div>
                      <div className="mt-1 text-xs text-slate-500">{event.message || ''}</div>
                    </div>
                    <span className="text-xs uppercase tracking-wide text-slate-500">{event.level || 'info'}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === 'capabilities' && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <h3 className="font-medium">Manifest capabilities</h3>
              <div className="mt-4 flex flex-wrap gap-2">
                {capabilities.length ? capabilities.map((cap) => <span key={cap} className="rounded-full border border-cyan-900 bg-cyan-950/40 px-3 py-1.5 text-sm text-cyan-200">{cap}</span>) : <span className="text-sm text-slate-500">No capabilities returned by runtime.</span>}
              </div>
            </div>
          )}
        </section>

        <aside className="space-y-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
            <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Runtime evidence</div>
            <div className="mt-4 space-y-3 text-sm">
              <Evidence label="Service" value={lab.service} />
              <Evidence label="Runtime port" value={manifest?.runtime?.port ? String(manifest.runtime.port) : '—'} />
              <Evidence label="Identity source" value={manifest?.runtime?.identity_source || '—'} />
              <Evidence label="Analysis contract" value={manifest?.runtime?.analysis_contract || '—'} />
              <Evidence label="Trace provider" value={manifest?.runtime?.trace_provider || '—'} />
              <Evidence label="Checked" value={lab.checked_at ? new Date(lab.checked_at).toLocaleTimeString() : '—'} />
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
            <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">System path</div>
            <div className="mt-4 space-y-3 text-sm">
              {['Kameleon context', 'Lab runtime', 'Ocean orchestration', 'Signal Fabric', 'NodeDB / OS-CLX / Kloud'].map((item) => <div key={item} className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2.5 text-slate-300">{item}</div>)}
            </div>
          </div>

          <Link href="/ocean" className="block rounded-2xl border border-cyan-900/60 bg-cyan-950/30 p-5 hover:bg-cyan-950/50">
            <div className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400">Ocean operator</div>
            <p className="mt-2 text-sm leading-6 text-slate-300">Open the broader orchestration surface after inspecting this laboratory execution.</p>
          </Link>
        </aside>
      </div>
    </main>
  )
}

function renderValue(value: unknown): string {
  if (typeof value === 'string') return value
  if (value == null) return 'No result payload returned.'
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-xl border border-slate-800 bg-slate-950 p-4"><div className="text-xs text-slate-500">{label}</div><div className="mt-2 break-all text-sm text-slate-200">{value}</div></div>
}

function Evidence({ label, value }: { label: string; value: string }) {
  return <div className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-3"><div className="text-xs text-slate-600">{label}</div><div className="mt-1 break-all text-slate-300">{value}</div></div>
}
