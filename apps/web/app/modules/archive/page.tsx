'use client'

import Link from 'next/link'
import { useState, FormEvent } from 'react'

const API_PROXY = '/api/ocean/archive'

// Proper interfaces matching Ocean Core API response
interface ArxivPaper {
  title: string
  summary: string
  authors: string[]
  published: string
  url: string
  categories: string[]
}

interface ArxivResult {
  query: string
  total_results: number
  papers: ArxivPaper[]
  source: string
}

interface WikiArticle {
  title: string
  snippet: string
  pageid: number
  wordcount: number
  url: string
}

interface WikiResult {
  query: string
  total_results: number
  results: WikiArticle[]
  source: string
}

interface PubMedArticle {
  pmid: string
  title: string
  authors: string[]
  source: string
  pubdate: string
  url: string
}

interface MultiSearchResults {
  arxiv: ArxivResult | null
  wikipedia: WikiResult | null
  pubmed: { articles: PubMedArticle[] } | null
}

export default function ArchivePage() {
  const [activeTab, setActiveTab] = useState<'unified' | 'arxiv' | 'wiki' | 'sources'>('unified')
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Unified search results
  const [multiResults, setMultiResults] = useState<MultiSearchResults | null>(null)

  // Individual results
  const [arxivResult, setArxivResult] = useState<ArxivResult | null>(null)
  const [wikiResult, setWikiResult] = useState<WikiResult | null>(null)
  const [dataSources, setDataSources] = useState<Record<string, unknown> | null>(null)

  // ─── Unified multi-source search ───
  async function handleUnifiedSearch(e: FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    setError('')
    setLoading(true)
    setMultiResults(null)

    try {
      const res = await fetch(API_PROXY, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'multi-search', query }),
      })
      const json = await res.json()
      if (json.success && json.results) {
        setMultiResults(json.results)
      } else {
        setError(json.error || 'Search failed')
      }
    } catch {
      setError('Connection error — Ocean Core may be offline')
    } finally {
      setLoading(false)
    }
  }

  // ─── ArXiv search ───
  async function handleArxivSearch(e: FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    setError('')
    setLoading(true)
    setArxivResult(null)

    try {
      const res = await fetch(`${API_PROXY}?action=arxiv&q=${encodeURIComponent(query)}`)
      const json = await res.json()
      if (json.success && json.data) {
        setArxivResult(json.data)
      } else {
        setError(json.error || 'ArXiv search failed')
      }
    } catch {
      setError('Connection error')
    } finally {
      setLoading(false)
    }
  }

  // ─── Wikipedia search ───
  async function handleWikiSearch(e: FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    setError('')
    setLoading(true)
    setWikiResult(null)

    try {
      const res = await fetch(`${API_PROXY}?action=wiki&q=${encodeURIComponent(query)}`)
      const json = await res.json()
      if (json.success && json.data) {
        setWikiResult(json.data)
      } else {
        setError(json.error || 'Wikipedia search failed')
      }
    } catch {
      setError('Connection error')
    } finally {
      setLoading(false)
    }
  }

  // ─── Load data sources ───
  async function loadSources() {
    setError('')
    setLoading(true)
    try {
      const res = await fetch(`${API_PROXY}?action=sources`)
      const json = await res.json()
      if (json.success) {
        setDataSources(json.data)
      } else {
        setError('Failed to load data sources')
      }
    } catch {
      setError('Connection error')
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'unified' as const, label: '🔬 Research', desc: 'Multi-source search' },
    { id: 'arxiv' as const, label: '📚 ArXiv', desc: 'Scientific papers' },
    { id: 'wiki' as const, label: '📖 Wikipedia', desc: 'Encyclopedia' },
    { id: 'sources' as const, label: '🌍 Data Sources', desc: '5000+ sources' },
  ]

  function getSearchHandler(): (e: FormEvent) => void {
    switch (activeTab) {
      case 'unified': return handleUnifiedSearch
      case 'arxiv': return handleArxivSearch
      case 'wiki': return handleWikiSearch
      default: return (e: FormEvent) => e.preventDefault()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/modules" className="text-violet-400 hover:text-violet-300 transition-colors">
              ← Modules
            </Link>
            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
              <span className="text-3xl">📜</span> Archive & Research
            </h1>
          </div>
          <span className="px-3 py-1 text-xs rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            ArXiv • Wikipedia • PubMed • 5000+ Sources
          </span>
        </div>
      </header>

      {/* Tabs */}
      <div className="max-w-6xl mx-auto px-6 pt-6">
        <div className="flex bg-white/5 rounded-xl p-1">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id)
                if (tab.id === 'sources' && !dataSources) loadSources()
              }}
              className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'text-white/60 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="max-w-6xl mx-auto px-6 mt-4">
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        </div>
      )}

      <main className="max-w-6xl mx-auto px-6 py-6">

        {/* Search bar (for all tabs except sources) */}
        {activeTab !== 'sources' && (
          <form onSubmit={getSearchHandler()} className="flex gap-3 mb-6">
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder={
                activeTab === 'unified'
                  ? 'Search across ArXiv, Wikipedia, and more...'
                  : activeTab === 'arxiv'
                  ? 'Search scientific papers on ArXiv...'
                  : 'Search Wikipedia...'
              }
              className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-xl text-white font-medium transition-all"
            >
              {loading ? '⏳ Searching...' : '🔍 Search'}
            </button>
          </form>
        )}

        {/* ═══ UNIFIED RESULTS ═══ */}
        {activeTab === 'unified' && multiResults && (
          <div className="space-y-6">
            {/* ArXiv section */}
            {multiResults.arxiv && multiResults.arxiv.papers && multiResults.arxiv.papers.length > 0 && (
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <span>📚</span> ArXiv Papers ({multiResults.arxiv.papers.length})
                </h2>
                <div className="space-y-3">
                  {multiResults.arxiv.papers.map((paper, i) => (
                    <div key={i} className="p-4 bg-white/5 rounded-lg border border-white/5 hover:border-indigo-500/30 transition-all">
                      <a href={paper.url} target="_blank" rel="noopener noreferrer" className="block">
                        <h3 className="text-white font-medium hover:text-indigo-400 transition-colors">{paper.title}</h3>
                      </a>
                      <p className="text-gray-400 text-sm mt-2 line-clamp-2">{paper.summary}</p>
                      <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                        <span>👥 {paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 ? ` +${paper.authors.length - 3}` : ''}</span>
                        <span>📅 {paper.published?.split('T')[0]}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Wikipedia section */}
            {multiResults.wikipedia && multiResults.wikipedia.results && multiResults.wikipedia.results.length > 0 && (
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <span>📖</span> Wikipedia ({multiResults.wikipedia.results.length})
                </h2>
                <div className="space-y-3">
                  {multiResults.wikipedia.results.map((item, i) => (
                    <div key={i} className="p-4 bg-white/5 rounded-lg border border-white/5 hover:border-indigo-500/30 transition-all">
                      <a href={item.url} target="_blank" rel="noopener noreferrer" className="block">
                        <h3 className="text-white font-medium hover:text-indigo-400 transition-colors">{item.title}</h3>
                      </a>
                      <p
                        className="text-gray-400 text-sm mt-1"
                        dangerouslySetInnerHTML={{ __html: item.snippet || '' }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* PubMed section */}
            {multiResults.pubmed && multiResults.pubmed.articles && multiResults.pubmed.articles.length > 0 && (
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <span>🏥</span> PubMed ({multiResults.pubmed.articles.length})
                </h2>
                <div className="space-y-3">
                  {multiResults.pubmed.articles.map((article, i) => (
                    <div key={i} className="p-4 bg-white/5 rounded-lg border border-white/5 hover:border-indigo-500/30 transition-all">
                      <a href={article.url} target="_blank" rel="noopener noreferrer" className="block">
                        <h3 className="text-white font-medium hover:text-indigo-400 transition-colors">{article.title}</h3>
                      </a>
                      <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                        <span>👥 {article.authors.slice(0, 3).join(', ')}</span>
                        <span>📅 {article.pubdate}</span>
                        <span>📰 {article.source}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!multiResults.arxiv?.papers?.length && !multiResults.wikipedia?.results?.length && !multiResults.pubmed?.articles?.length && (
              <div className="text-center text-white/30 py-12">No results found</div>
            )}
          </div>
        )}

        {/* ═══ ARXIV TAB ═══ */}
        {activeTab === 'arxiv' && arxivResult && arxivResult.papers && arxivResult.papers.length > 0 && (
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">
              📚 {arxivResult.total_results} papers found
            </h2>
            <div className="space-y-3">
              {arxivResult.papers.map((paper, i) => (
                <div key={i} className="p-4 bg-white/5 rounded-lg border border-white/5 hover:border-indigo-500/30 transition-all">
                  <div className="flex items-start gap-3">
                    <span className="text-indigo-400 font-mono text-sm mt-0.5">#{i + 1}</span>
                    <div className="flex-1">
                      <a href={paper.url} target="_blank" rel="noopener noreferrer">
                        <h3 className="text-white font-medium hover:text-indigo-400 transition-colors">{paper.title}</h3>
                      </a>
                      <p className="text-gray-400 text-sm mt-2 line-clamp-3">{paper.summary}</p>
                      <div className="flex flex-wrap items-center gap-3 mt-3 text-xs text-gray-500">
                        <span>👥 {paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 ? ` +${paper.authors.length - 3} more` : ''}</span>
                        <span>📅 {paper.published?.split('T')[0]}</span>
                        {paper.categories.length > 0 && (
                          <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-400 rounded">{paper.categories[0]}</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ═══ WIKI TAB ═══ */}
        {activeTab === 'wiki' && wikiResult && wikiResult.results && (
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">📖 Wikipedia Results ({wikiResult.total_results})</h2>
            <div className="space-y-3">
              {wikiResult.results.map((item, i) => (
                <div key={i} className="p-4 bg-white/5 rounded-lg border border-white/5 hover:border-indigo-500/30 transition-all">
                  <a href={item.url} target="_blank" rel="noopener noreferrer">
                    <h3 className="text-white font-medium mb-1 hover:text-indigo-400 transition-colors">{item.title}</h3>
                  </a>
                  <p
                    className="text-gray-400 text-sm"
                    dangerouslySetInnerHTML={{ __html: item.snippet || '' }}
                  />
                  <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                    <span>📝 {item.wordcount.toLocaleString()} words</span>
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-indigo-400 hover:underline"
                    >
                      Read on Wikipedia →
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ═══ DATA SOURCES TAB ═══ */}
        {activeTab === 'sources' && (
          <div>
            {loading && (
              <div className="text-center text-white/50 py-12 animate-pulse">
                Loading 5000+ data sources...
              </div>
            )}
            {dataSources && (
              <div className="space-y-6">
                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <h2 className="text-lg font-semibold text-white mb-4">🌍 Global Data Sources</h2>
                  <p className="text-gray-400 text-sm mb-6">
                    Ocean Core connects to 5000+ data sources from 200+ countries for comprehensive research coverage.
                  </p>
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap max-h-[60vh] overflow-y-auto bg-white/5 rounded-lg p-4">
                    {JSON.stringify(dataSources, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Empty state */}
        {!loading && activeTab !== 'sources' && !multiResults && !arxivResult && !wikiResult && (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">📜</div>
            <h3 className="text-xl font-medium text-white mb-2">Search the Knowledge Archive</h3>
            <p className="text-gray-400 max-w-md mx-auto">
              Search across ArXiv scientific papers, Wikipedia, PubMed research, 
              and 5000+ global data sources — all powered by Ocean Core.
            </p>
          </div>
        )}
      </main>
    </div>
  )
}
