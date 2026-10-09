'use client'

import Link from 'next/link'
import { FormEvent, useMemo, useState } from 'react'

type MediaType = 'all' | 'video' | 'image' | 'photo' | 'status'

interface SearchResult {
  platform: string
  mediaType: MediaType
  url: string
}

export default function SocialIntelligencePage() {
  const [query, setQuery] = useState('')
  const [mediaType, setMediaType] = useState<MediaType>('all')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])

  const mediaTypes: MediaType[] = useMemo(() => ['all', 'video', 'image', 'photo', 'status'], [])

  async function handleSearch(e: FormEvent) {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setResults([])

    try {
      const res = await fetch('/api/ocean/social', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'search', query, mediaType }),
      })

      const json = await res.json()
      if (!res.ok || json.status !== 'ok') {
        setError(json.message || 'Search failed')
        return
      }

      setResults(Array.isArray(json.results) ? json.results : [])
    } catch {
      setError('Connection error while querying social media routes')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900">
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/modules" className="text-violet-400 hover:text-violet-300 transition-colors">
              ← Modules
            </Link>
            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
              <span className="text-3xl">📡</span> Social Intelligence
            </h1>
          </div>
          <span className="px-3 py-1 text-xs rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            Video • Image • Photo • Status
          </span>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        <div className="mb-5 text-white/80">
          Search directly across YouTube, TikTok, Instagram, X, LinkedIn and Facebook with one query.
        </div>

        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex gap-3">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search videos, photos, figures, posts, trends..."
              className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-xl text-white font-medium transition-all"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {mediaTypes.map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => setMediaType(type)}
                className={`px-3 py-1.5 rounded-lg border text-sm transition ${
                  mediaType === type
                    ? 'bg-indigo-600 border-indigo-500 text-white'
                    : 'bg-white/5 border-white/20 text-white/80 hover:bg-white/10'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </form>

        {error && (
          <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-300 text-sm">
            {error}
          </div>
        )}

        {results.length > 0 && (
          <div className="mt-6 grid gap-3">
            {results.map((item) => (
              <a
                key={`${item.platform}-${item.url}`}
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-4 rounded-xl bg-white/5 border border-white/10 hover:border-indigo-400 transition"
              >
                <div className="text-white font-medium">{item.platform.toUpperCase()}</div>
                <div className="text-xs text-indigo-300 uppercase tracking-wide mt-1">{item.mediaType}</div>
                <div className="text-sm text-white/70 mt-2 break-all">{item.url}</div>
              </a>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
