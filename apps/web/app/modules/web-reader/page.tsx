'use client'

import Link from 'next/link'
import { useState, FormEvent, useRef } from 'react'

const API_PROXY = '/api/ocean/web-reader'

interface SearchResult {
  title: string
  url: string
}

interface BrowseResult {
  url: string
  content: string
  chars?: number
  char_count?: number
  title?: string
}

interface ChatMessage {
  id: number
  sender: 'user' | 'bot'
  text: string
  status?: 'streaming' | 'complete' | 'error'
}

export default function WebReaderPage() {
  const [activeTab, setActiveTab] = useState<'browse' | 'search' | 'chat'>('browse')

  // Browse state
  const [browseUrl, setBrowseUrl] = useState('')
  const [browseContent, setBrowseContent] = useState<BrowseResult | null>(null)
  const [browseLoading, setBrowseLoading] = useState(false)

  // Search state
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [searchLoading, setSearchLoading] = useState(false)

  // Chat state
  const [chatUrl, setChatUrl] = useState('')
  const [chatMessage, setChatMessage] = useState('')
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatLoading, setChatLoading] = useState(false)
  const [chatStatus, setChatStatus] = useState('')
  const abortControllerRef = useRef<AbortController | null>(null)

  const [error, setError] = useState('')

  function normalizeUrl(input: string): string {
    const value = input.trim()
    if (!value) return value

    let candidate = value
    if (!/^https?:\/\//i.test(candidate)) {
      candidate = `https://${candidate}`
    }

    try {
      const parsed = new URL(candidate)
      const hostname = parsed.hostname
      if (hostname && !hostname.includes('.') && hostname !== 'localhost') {
        parsed.hostname = `${hostname}.com`
      }
      return parsed.toString()
    } catch {
      return candidate
    }
  }

  // ─── Browse a URL ───
  async function handleBrowse(e: FormEvent) {
    e.preventDefault()
    if (!browseUrl.trim()) return
    setError('')
    setBrowseLoading(true)
    setBrowseContent(null)

    const normalizedUrl = normalizeUrl(browseUrl)
    setBrowseUrl(normalizedUrl)

    try {
      const res = await fetch(`${API_PROXY}?action=browse&url=${encodeURIComponent(normalizedUrl)}&max_chars=10000`)
      const json = await res.json()
      if (json.success && json.data) {
        const chars = Number(json.data.chars ?? json.data.char_count ?? 0)
        if (!json.data.content || json.data.content.trim().length === 0 || chars === 0) {
          setError('No readable content found for this URL. Try a full page URL (example: https://google.com).')
        } else {
          setBrowseContent(json.data)
        }
      } else {
        setError(json.error || 'Failed to read page')
      }
    } catch {
      setError('Connection error — Ocean Core may be offline')
    } finally {
      setBrowseLoading(false)
    }
  }

  // ─── Web Search ───
  async function handleSearch(e: FormEvent) {
    e.preventDefault()
    if (!searchQuery.trim()) return
    setError('')
    setSearchLoading(true)
    setSearchResults([])

    try {
      const res = await fetch(`${API_PROXY}?action=search&q=${encodeURIComponent(searchQuery)}&num=10`)
      const json = await res.json()
      if (json.success && json.data?.results) {
        setSearchResults(json.data.results)
      } else {
        setError(json.error || 'Search failed')
      }
    } catch {
      setError('Connection error — Ocean Core may be offline')
    } finally {
      setSearchLoading(false)
    }
  }

  // ─── Chat with webpage (ELASTIC STREAMING) ───
  async function handleChat(e: FormEvent) {
    e.preventDefault()
    if (!chatUrl.trim() || !chatMessage.trim()) return
    setError('')
    setChatLoading(true)
    setChatStatus('Connecting...')

    const normalizedChatUrl = normalizeUrl(chatUrl)
    setChatUrl(normalizedChatUrl)

    const userMsg: ChatMessage = { id: Date.now(), sender: 'user', text: chatMessage }
    setChatMessages(prev => [...prev, userMsg])
    const msg = chatMessage
    setChatMessage('')

    // Add bot message placeholder for streaming
    const botMsgId = Date.now() + 1
    setChatMessages(prev => [...prev, { id: botMsgId, sender: 'bot', text: '', status: 'streaming' }])

    try {
      // Try streaming first
      abortControllerRef.current = new AbortController()

      const res = await fetch('/api/ocean/web-reader/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'chat', url: normalizedChatUrl, message: msg }),
        signal: abortControllerRef.current.signal
      })

      if (!res.ok || !res.body) {
        // Fallback to non-streaming
        const fallbackRes = await fetch(API_PROXY, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'chat', url: normalizedChatUrl, message: msg }),
        })
        const json = await fallbackRes.json()
        const reply = json.data?.response || json.data?.answer || json.data?.message || json.error || 'No response'
        setChatMessages(prev => prev.map(m =>
          m.id === botMsgId ? { ...m, text: reply, status: 'complete' } : m
        ))
        setChatLoading(false)
        setChatStatus('')
        return
      }

      // SSE Streaming
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let fullText = ''
      let pending = ''

      const appendStreamText = (data: Record<string, unknown>) => {
        const candidates = [data.token, data.chunk, data.response, data.text, data.answer]
        for (const candidate of candidates) {
          if (typeof candidate === 'string' && candidate.length > 0) {
            fullText += candidate
            return true
          }
        }
        return false
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        pending += decoder.decode(value, { stream: true })
        const lines = pending.split('\n')
        pending = lines.pop() || ''

        for (const line of lines) {
          const trimmedLine = line.trim()
          if (trimmedLine.startsWith('data: ')) {
            try {
              const data = JSON.parse(trimmedLine.slice(6))

              if (data.status === 'browsing') {
                setChatStatus(`📖 Reading page: ${typeof data.title === 'string' ? data.title : 'Loading...'}`)
              } else if (data.status === 'thinking') {
                setChatStatus('🧠 Analyzing content...')
              } else if (appendStreamText(data as Record<string, unknown>)) {
                setChatMessages(prev => prev.map(m =>
                  m.id === botMsgId ? { ...m, text: fullText, status: 'streaming' } : m
                ))
                setChatStatus('💬 Responding...')
              } else if (data.status === 'complete') {
                setChatMessages(prev => prev.map(m =>
                  m.id === botMsgId ? { ...m, status: 'complete' } : m
                ))
              } else if (data.error) {
                setChatMessages(prev => prev.map(m =>
                  m.id === botMsgId ? { ...m, text: data.error, status: 'error' } : m
                ))
              }
            } catch {
              // Skip malformed JSON
            }
          }
        }
      }

      const trailing = pending.trim()
      if (trailing.startsWith('data: ')) {
        try {
          const data = JSON.parse(trailing.slice(6))
          if (appendStreamText(data as Record<string, unknown>)) {
            setChatMessages(prev => prev.map(m =>
              m.id === botMsgId ? { ...m, text: fullText, status: 'streaming' } : m
            ))
          }
        } catch {
          // ignore trailing partial payload
        }
      }

      // If no text received, show error
      if (!fullText) {
        try {
          const fallbackRes = await fetch(API_PROXY, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'chat', url: normalizedChatUrl, message: msg }),
          })
          const json = await fallbackRes.json()
          const reply = json.data?.response || json.data?.answer || json.data?.message || json.error || 'No response received'
          setChatMessages(prev => prev.map(m =>
            m.id === botMsgId ? { ...m, text: reply, status: 'complete' } : m
          ))
        } catch {
          setChatMessages(prev => prev.map(m =>
            m.id === botMsgId ? { ...m, text: 'No response received', status: 'error' } : m
          ))
        }
      }

    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        setChatMessages(prev => prev.map(m =>
          m.id === botMsgId ? { ...m, text: '⏹️ Cancelled', status: 'error' } : m
        ))
      } else {
        // Fallback to non-streaming on error
        try {
          const fallbackRes = await fetch(API_PROXY, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'chat', url: normalizedChatUrl, message: msg }),
          })
          const json = await fallbackRes.json()
          const reply = json.data?.response || json.data?.answer || json.data?.message || json.error || 'Connection error'
          setChatMessages(prev => prev.map(m =>
            m.id === botMsgId ? { ...m, text: reply, status: 'complete' } : m
          ))
        } catch {
          setChatMessages(prev => prev.map(m =>
            m.id === botMsgId ? { ...m, text: 'Connection error - Ocean Core may be offline', status: 'error' } : m
          ))
        }
      }
    } finally {
      setChatLoading(false)
      setChatStatus('')
      abortControllerRef.current = null
    }
  }

  function cancelChat() {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
  }

  // Open a search result in browse tab
  function openInBrowse(url: string) {
    setBrowseUrl(url)
    setActiveTab('browse')
    setBrowseContent(null)
    // Auto-trigger browse
    setTimeout(() => {
      const form = document.getElementById('browse-form') as HTMLFormElement
      form?.requestSubmit()
    }, 100)
  }

  const tabs = [
    { id: 'browse' as const, label: '🌐 Browse', desc: 'Read any webpage' },
    { id: 'search' as const, label: '🔍 Search', desc: 'Search the web' },
    { id: 'chat' as const, label: '💬 Chat', desc: 'Chat with a page' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/modules" className="text-violet-400 hover:text-violet-300 transition-colors">
              ← Modules
            </Link>
            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
              <span className="text-3xl">🌐</span> Web Reader
            </h1>
          </div>
          <span className="px-3 py-1 text-xs rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            ● Connected to Ocean Core
          </span>
        </div>
      </header>

      {/* Tabs */}
      <div className="max-w-6xl mx-auto px-6 pt-6">
        <div className="flex bg-white/5 rounded-xl p-1 max-w-lg">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-violet-600 text-white shadow-lg'
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
        {/* ═══ BROWSE TAB ═══ */}
        {activeTab === 'browse' && (
          <div>
            <form id="browse-form" onSubmit={handleBrowse} className="flex gap-3 mb-6">
              <input
                type="text"
                value={browseUrl}
                onChange={e => setBrowseUrl(e.target.value)}
                placeholder="https://example.com — Enter any URL to read..."
                className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500"
              />
              <button
                type="submit"
                disabled={browseLoading}
                className="px-6 py-3 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 rounded-xl text-white font-medium transition-all"
              >
                {browseLoading ? '⏳ Reading...' : '📖 Read'}
              </button>
            </form>

            {browseContent && (
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-white truncate max-w-xl">
                    {browseContent.title || browseContent.url}
                  </h2>
                  <span className="text-xs text-white/40">{(browseContent.chars || browseContent.char_count || 0).toLocaleString()} chars</span>
                </div>
                <div className="prose prose-invert max-w-none">
                  <pre className="whitespace-pre-wrap text-sm text-gray-300 leading-relaxed font-sans max-h-[70vh] overflow-y-auto">
                    {browseContent.content}
                  </pre>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ═══ SEARCH TAB ═══ */}
        {activeTab === 'search' && (
          <div>
            <form onSubmit={handleSearch} className="flex gap-3 mb-6">
              <input
                type="text"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="Search the web..."
                className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500"
              />
              <button
                type="submit"
                disabled={searchLoading}
                className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 rounded-xl text-white font-medium transition-all"
              >
                {searchLoading ? '⏳ Searching...' : '🔍 Search'}
              </button>
            </form>

            {searchResults.length > 0 && (
              <div className="space-y-3">
                {searchResults.map((result, i) => (
                  <div
                    key={i}
                    className="p-4 bg-white/5 border border-white/10 rounded-xl hover:border-violet-500/50 transition-all"
                  >
                    <h3 className="text-white font-medium mb-1">{result.title || result.url}</h3>
                    <a
                      href={result.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-violet-400 text-sm hover:underline truncate block"
                    >
                      {result.url}
                    </a>
                    <button
                      onClick={() => openInBrowse(result.url)}
                      className="mt-2 text-xs px-3 py-1 bg-violet-600/20 text-violet-400 rounded-lg hover:bg-violet-600/40 transition-all"
                    >
                      📖 Read this page
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ═══ CHAT TAB ═══ */}
        {activeTab === 'chat' && (
          <div>
            <div className="mb-4">
              <input
                type="text"
                value={chatUrl}
                onChange={e => setChatUrl(e.target.value)}
                placeholder="https://example.com — URL to chat about"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-violet-500"
              />
            </div>

            {/* Status indicator */}
            {chatStatus && (
              <div className="mb-3 px-4 py-2 bg-violet-500/10 border border-violet-500/30 rounded-lg flex items-center justify-between">
                <span className="text-violet-400 text-sm animate-pulse">{chatStatus}</span>
                <button
                  onClick={cancelChat}
                  className="text-xs px-2 py-1 bg-red-500/20 text-red-400 rounded hover:bg-red-500/40"
                >
                  ⏹️ Cancel
                </button>
              </div>
            )}

            {/* Chat messages */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-4 h-[50vh] overflow-y-auto mb-4 space-y-3">
              {chatMessages.length === 0 && (
                <div className="text-center text-white/30 py-20">
                  <div className="text-4xl mb-3">💬</div>
                  <p>Enter a URL above and ask questions about the page content</p>
                  <p className="text-xs mt-2 text-white/20">🚀 Now with elastic streaming - no timeouts!</p>
                </div>
              )}
              {chatMessages.map(msg => (
                <div
                  key={msg.id}
                  className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm whitespace-pre-wrap ${
                      msg.sender === 'user'
                        ? 'bg-violet-600 text-white'
                        : msg.status === 'error'
                        ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                        : msg.status === 'streaming'
                        ? 'bg-white/10 text-gray-200 border border-violet-500/30'
                        : 'bg-white/10 text-gray-200'
                    }`}
                  >
                    {msg.text || (msg.status === 'streaming' && '...')}
                    {msg.status === 'streaming' && (
                      <span className="inline-block w-2 h-4 bg-violet-400 ml-1 animate-pulse" />
                    )}
                  </div>
                </div>
              ))}
            </div>

            <form onSubmit={handleChat} className="flex gap-3">
              <input
                type="text"
                value={chatMessage}
                onChange={e => setChatMessage(e.target.value)}
                placeholder="Ask about the webpage..."
                className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-violet-500"
              />
              <button
                type="submit"
                disabled={chatLoading || !chatUrl}
                className="px-6 py-3 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 rounded-xl text-white font-medium transition-all"
              >
                {chatLoading ? '⏳' : 'Send'}
              </button>
            </form>
          </div>
        )}
      </main>
    </div>
  )
}
