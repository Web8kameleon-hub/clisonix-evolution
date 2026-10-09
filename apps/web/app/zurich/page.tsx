'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'

interface ZurichResponse {
  ok: boolean
  output: string
  confidence: number
  strategy: string
  domains: string[]
  processing_time_ms: number
  engine: string
}

const STAGES = [
  { num: 1, name: 'Parse' },
  { num: 2, name: 'Classify' },
  { num: 3, name: 'Decompose' },
  { num: 4, name: 'Retrieve' },
  { num: 5, name: 'Apply' },
  { num: 6, name: 'Synthesize' },
  { num: 7, name: 'Validate' },
  { num: 8, name: 'Format' },
  { num: 9, name: 'Output' },
]

const QUICK_PROMPTS = [
  'S0=3, S1=7, S2=11, compute S10',
  'x0=5, f(x)=(2*x)^3, find x6',
  'x0=7, f(x)=3*x ^ 5, compute x4',
]

export default function ZurichPage() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<ZurichResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeStage, setActiveStage] = useState(-1)
  const [error, setError] = useState<string | null>(null)
  const [healthState, setHealthState] = useState<'checking' | 'online' | 'offline'>('checking')

  const checkZurichHealth = async () => {
    setHealthState('checking')
    try {
      const res = await fetch('/api/zurich', { method: 'GET' })
      setHealthState(res.ok ? 'online' : 'offline')
    } catch {
      setHealthState('offline')
    }
  }

  useEffect(() => {
    checkZurichHealth()
  }, [])

  const getErrorDetail = (payload: unknown): string | null => {
    if (!payload || typeof payload !== 'object') return null
    const data = payload as Record<string, unknown>
    if (typeof data.error === 'string' && data.error.trim()) return data.error
    if (typeof data.details === 'string' && data.details.trim()) return data.details
    if (typeof data.message === 'string' && data.message.trim()) return data.message
    return null
  }

  const processQuery = async () => {
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResponse(null)

    for (let i = 0; i < 9; i++) {
      setActiveStage(i)
      await new Promise(r => setTimeout(r, 80))
    }

    try {
      const signal = AbortSignal.timeout(45000)
      const res = await fetch('/api/zurich', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: query }),
        signal,
      })

      if (!res.ok) {
        const payload = await res.json().catch(() => ({}))
        const detail = getErrorDetail(payload)
        throw new Error(detail || `Zurich request failed (${res.status})`)
      }

      const data = await res.json()
      setResponse(data)
      setHealthState('online')
    } catch (err) {
      const message = err instanceof Error && err.message
        ? err.message
        : 'Connection failed. Please verify Zurich API is online and try again.'
      setError(message)
      setHealthState('offline')
    } finally {
      setActiveStage(-1)
      setLoading(false)
    }
  }

  const applyQuickPrompt = (prompt: string) => {
    setQuery(prompt)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-sky-50/40 to-slate-100 text-slate-800 relative overflow-hidden">
      <div className="pointer-events-none absolute -top-28 left-1/4 h-80 w-80 rounded-full bg-emerald-100/80 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-40 right-1/4 h-96 w-96 rounded-full bg-cyan-100/70 blur-3xl" />

      <header className="border-b border-slate-200/80 backdrop-blur-sm sticky top-0 z-10 bg-white/90">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-5 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4 min-w-0">
            <div className="w-11 h-11 rounded-xl border border-emerald-200 bg-white flex items-center justify-center text-xl shadow">
              ⚙️
            </div>
            <div className="min-w-0">
              <h1 className="text-lg font-semibold text-slate-900 tracking-tight">Zürich Engine</h1>
              <p className="text-xs text-slate-500">Deterministic 9-Stage Reasoning • Clisonix Ultra Stack</p>
            </div>
          </div>
          <div className="flex items-center flex-wrap gap-2 sm:gap-3">
            <span className="px-2.5 py-1 rounded-md text-[11px] border border-emerald-300 text-emerald-700 bg-emerald-50">
              Deterministic
            </span>
            <span className="px-2.5 py-1 rounded-md text-[11px] border border-cyan-300 text-cyan-700 bg-cyan-50">
              No Randomness
            </span>
            <Link href="/modules" className="text-sm text-slate-600 hover:text-slate-900">
              ← Back
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <div className="grid lg:grid-cols-5 gap-8">

          {/* Pipeline */}
          <div className="lg:col-span-2 space-y-5">
            <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">
              Pipeline
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-1.5 shadow-sm">
              {STAGES.map((stage, i) => (
                <div
                  key={i}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors border ${
                    activeStage === i
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      : activeStage > i
                        ? 'text-slate-700 border-slate-200 bg-slate-50'
                        : 'text-slate-500 border-transparent'
                  }`}
                >
                  <span className={`w-5 h-5 rounded text-xs flex items-center justify-center ${
                    activeStage === i
                      ? 'bg-emerald-600 text-white font-semibold'
                      : activeStage > i
                        ? 'bg-slate-300 text-slate-900'
                        : 'bg-slate-100 text-slate-500'
                  }`}>
                    {activeStage > i ? '✓' : stage.num}
                  </span>
                  <span>{stage.name}</span>
                  {activeStage === i && (
                    <span className="ml-auto w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                  )}
                </div>
              ))}
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-3 shadow-sm">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500 uppercase tracking-wider">Execution state</span>
                <span className={loading ? 'text-emerald-700' : 'text-slate-500'}>{loading ? 'Running' : 'Idle'}</span>
              </div>
              <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 transition-all duration-200"
                  style={{ width: `${loading ? Math.max(0, ((activeStage + 1) / 9) * 100) : 0}%` }}
                />
              </div>
              <div className="text-xs text-slate-500 leading-relaxed">
                Stable reasoning chain with explicit stage gating and deterministic output assembly.
              </div>
            </div>
          </div>

          {/* Main */}
          <div className="lg:col-span-3 space-y-6">

            <div className="grid sm:grid-cols-3 gap-3">
              <div className="rounded-xl border border-slate-200/90 bg-white px-4 py-3 shadow-sm">
                <div className="text-[11px] uppercase tracking-wider text-slate-500">Engine Mode</div>
                <div className="text-sm text-slate-800 mt-1">9-Stage Deterministic</div>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
                <div className="text-[11px] uppercase tracking-wider text-slate-500">Context</div>
                <div className="text-sm text-slate-800 mt-1">Clisonix Zürich Core</div>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
                <div className="text-[11px] uppercase tracking-wider text-slate-500">Connection</div>
                <div className={`text-sm mt-1 ${
                  healthState === 'online'
                    ? 'text-emerald-700'
                    : healthState === 'offline'
                      ? 'text-red-700'
                      : 'text-amber-700'
                }`}>
                  {healthState === 'online' ? 'Online' : healthState === 'offline' ? 'Offline' : 'Checking...'}
                </div>
              </div>
            </div>

            {/* Input */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-md space-y-4">
              <div className="space-y-2">
                <p className="text-sm font-medium text-slate-700">Try a quick example</p>
                <div className="flex flex-wrap gap-2">
                  {QUICK_PROMPTS.map((prompt) => (
                    <button
                      key={prompt}
                      type="button"
                      onClick={() => applyQuickPrompt(prompt)}
                      className="px-3 py-1.5 text-xs rounded-full bg-slate-100 text-slate-700 border border-slate-200 hover:bg-slate-200 transition-colors"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>

              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), processQuery())}
                placeholder="Enter your query for high-fidelity deterministic analysis..."
                className="w-full h-32 bg-white text-slate-900 placeholder-slate-400 border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-300 resize-none text-sm shadow-inner"
              />
              <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                <span className="text-xs text-slate-500">{query.length} chars</span>
                <button
                  onClick={processQuery}
                  disabled={loading || !query.trim()}
                  className="px-5 py-2 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white text-sm font-semibold rounded-lg hover:opacity-95 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow"
                >
                  {loading ? 'Processing...' : 'Analyze'}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm">
                <div className="text-red-700 font-medium">{error}</div>
                <div className="mt-1 text-red-600">If this persists, check service health on /api/zurich.</div>
                <div className="mt-3 flex items-center gap-2">
                  <button
                    type="button"
                    onClick={processQuery}
                    disabled={loading || !query.trim()}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Retry Analyze
                  </button>
                  <button
                    type="button"
                    onClick={checkZurichHealth}
                    disabled={healthState === 'checking'}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-white border border-red-200 text-red-700 hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Re-check Connection
                  </button>
                </div>
              </div>
            )}

            {/* Output */}
            {response && (
              <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-md">
                <div className="px-5 py-4 border-b border-slate-200 bg-slate-50/70 flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-800">Result</span>
                  <div className="flex items-center gap-4 text-xs text-slate-500">
                    <span>{response.processing_time_ms.toFixed(2)}ms</span>
                    <span>{(response.confidence * 100).toFixed(0)}% confidence</span>
                  </div>
                </div>
                <div className="p-5">
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className="px-2 py-1 bg-slate-100 text-slate-700 text-xs rounded border border-slate-200">
                      {response.strategy}
                    </span>
                    {response.domains.map(d => (
                      <span key={d} className="px-2 py-1 bg-slate-100 text-slate-700 text-xs rounded border border-slate-200">
                        {d}
                      </span>
                    ))}
                  </div>
                  <pre className="whitespace-pre-wrap text-slate-800 text-sm font-mono leading-relaxed bg-white border border-slate-200 rounded-xl p-4">
                    {response.output}
                  </pre>
                </div>
              </div>
            )}

            {/* Empty */}
            {!response && !loading && !error && (
              <div className="text-center py-16 text-slate-500">
                <div className="text-4xl mb-3">🎯</div>
                <p className="text-sm">Enter a query for deterministic analysis</p>
                <p className="text-xs text-slate-400 mt-1">No AI randomness • Reproducible results</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
