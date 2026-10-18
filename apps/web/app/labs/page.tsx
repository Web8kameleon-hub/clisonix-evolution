'use client'

import Link from 'next/link'
import { useEffect, useMemo, useState } from 'react'

type Lab = {
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
}

type LabsSnapshot = {
  total: number
  healthy: number
  degraded: number
  unavailable: number
  analysis_ready?: number
  fully_operational?: boolean
  laboratories: Lab[]
  timestamp: string
}

const CITY_LABS_API = '/api/city-labs/api/v1'

export default function CityLabsPage() {
  const [snapshot, setSnapshot] = useState<LabsSnapshot | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')

  useEffect(() => {
    let active = true
    const load = async () => {
      try {
        const response = await fetch(`${CITY_LABS_API}/labs?live=true`, { cache: 'no-store' })
        if (!response.ok) throw new Error(`City Labs registry HTTP ${response.status}`)
        const payload = await response.json()
        if (active) {
          setSnapshot(payload)
          setError(null)
        }
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : 'Could not load City Labs')
      } finally {
        if (active) setLoading(false)
      }
    }

    load()
    const timer = window.setInterval(load, 10000)
    return () => {
      active = false
      window.clearInterval(timer)
    }
  }, [])

  const labs = snapshot?.laboratories || []
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return labs
    return labs.filter((lab) =>
      [lab.name, lab.city, lab.country, lab.function, lab.lab_type, lab.service]
        .some((value) => String(value).toLowerCase().includes(q)),
    )
  }, [labs, query])

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="border-b border-slate-800 bg-slate-950/95">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-400">Clisonix · AI as Operating Environment</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight">Kameleon City Labs</h1>
              <p className="mt-3 max-w-3xl text-slate-400">
                One adaptive operating surface for 23 city laboratories. Runtime health and analysis readiness are measured separately from live services.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-5">
              {[
                ['Registry', snapshot?.total],
                ['Healthy', snapshot?.healthy],
                ['Analysis', snapshot?.analysis_ready],
                ['Degraded', snapshot?.degraded],
                ['Unavailable', snapshot?.unavailable],
              ].map(([label, value]) => (
                <div key={String(label)} className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-3">
                  <div className="text-slate-500">{label}</div>
                  <div className="mt-1 text-2xl font-semibold">{loading ? '—' : value ?? '—'}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3 text-xs">
            <span className={`rounded-full px-3 py-1.5 ${snapshot?.fully_operational ? 'bg-emerald-950 text-emerald-300' : 'bg-amber-950 text-amber-300'}`}>
              {snapshot?.fully_operational ? '23/23 fully operational' : 'runtime and analysis gates measured independently'}
            </span>
            {snapshot?.timestamp && <span className="text-slate-600">Live snapshot: {new Date(snapshot.timestamp).toLocaleString()}</span>}
          </div>

          <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search city, country, domain or function…"
              className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm outline-none ring-cyan-500/30 transition focus:border-cyan-500 focus:ring-4"
            />
            <Link href="/ocean" className="whitespace-nowrap rounded-xl border border-slate-700 px-4 py-3 text-sm text-slate-300 hover:bg-slate-900">
              Ocean Core →
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-8">
        {loading && <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-400">Probing 23 City Labs…</div>}
        {error && <div className="mb-6 rounded-2xl border border-red-900/70 bg-red-950/30 p-6 text-red-300">{error}</div>}

        {!loading && (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {filtered.map((lab) => {
              const live = lab.status === 'healthy'
              return (
                <Link
                  key={lab.lab_id}
                  href={`/labs/${encodeURIComponent(lab.lab_id)}`}
                  className="group rounded-2xl border border-slate-800 bg-slate-900/70 p-5 transition hover:-translate-y-0.5 hover:border-cyan-700 hover:bg-slate-900"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="text-xs uppercase tracking-[0.18em] text-cyan-400">{lab.lab_type}</div>
                      <h2 className="mt-2 text-xl font-semibold group-hover:text-cyan-100">{lab.name}</h2>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <span className={`rounded-full px-2.5 py-1 text-xs ${live ? 'bg-emerald-950 text-emerald-300' : lab.status === 'degraded' ? 'bg-amber-950 text-amber-300' : 'bg-red-950/60 text-red-300'}`}>
                        {lab.status}
                      </span>
                      <span className={`rounded-full px-2.5 py-1 text-xs ${lab.analysis_ready ? 'bg-cyan-950 text-cyan-300' : 'bg-slate-800 text-slate-400'}`}>
                        {lab.analysis_ready ? 'analysis ready' : 'runtime only'}
                      </span>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-slate-400">{lab.city}, {lab.country}</p>
                  <p className="mt-4 min-h-10 text-sm leading-6 text-slate-300">{lab.function}</p>
                  <div className="mt-5 grid grid-cols-2 gap-3 border-t border-slate-800 pt-4 text-xs">
                    <div>
                      <div className="text-slate-600">Service</div>
                      <div className="mt-1 text-slate-400">{lab.service}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-slate-600">Probe latency</div>
                      <div className="mt-1 text-slate-400">{lab.latency_ms == null ? '—' : `${lab.latency_ms} ms`}</div>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </section>
    </main>
  )
}
