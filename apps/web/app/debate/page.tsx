'use client'

import { Suspense, useState, useRef, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'

interface DebateResponse {
  persona: string
  name: string
  emoji: string
  role: string
  response: string
  status: 'success' | 'error' | 'partial'
  tokens?: number
}

const LANGUAGE_NAMES: Record<string, string> = {
  en: 'English',
  sq: 'Albanian',
  de: 'German',
  fr: 'French',
  it: 'Italian',
  es: 'Spanish',
  pt: 'Portuguese',
  tr: 'Turkish',
}

const DEBATE_UI = {
  en: {
    title: 'Trinity Debate',
    subtitle: '5 AI perspectives • Elastic streaming • Conversation memory + i18n',
    back: '← Back',
    backToOcean: '← Back to Ocean',
    processing: 'Processing...',
    thinking: (name?: string) => `${name || 'A persona'} is thinking...`,
    placeholder: 'Enter a topic for debate...',
    suggestions: ['Future of AI', 'Remote vs office', 'Privacy vs security', 'Climate action'],
    stop: 'Stop',
    streaming: 'Streaming...',
    start: 'Start debate',
    cancelled: 'Debate cancelled',
    connectError: 'Debate engine is temporarily unavailable. Please try again.',
    liveStreaming: 'Streaming live...',
    topic: 'Topic',
    responses: (count: number, total: number) => `${count}/${total} responses`,
    words: 'words',
    noResponse: 'No response',
    partial: 'Partial',
    error: 'Error',
    emptyTitle: 'Enter a topic to start a multi-perspective debate',
    emptySubtitle: '5 AI personas • Elastic streaming • Keeps conversation flow',
  },
  sq: {
    title: 'Debati i Trinitetit',
    subtitle: '5 perspektiva AI • Streaming elastik • Memorie bisede + i18n',
    back: '← Mbrapa',
    backToOcean: '← Back to Ocean',
    processing: 'Duke përpunuar...',
    thinking: (name?: string) => `${name || 'Një personazh'} po mendon...`,
    placeholder: 'Futni një temë për debat...',
    suggestions: ['E ardhmja e AI', 'Në distancë vs zyrë', 'Privatësia vs Siguria', 'Veprimi për klimën'],
    stop: 'Ndalo',
    streaming: 'Duke transmetuar...',
    start: 'Filloni debatin',
    cancelled: 'Debati u anulua',
    connectError: 'Motori i debatit është përkohësisht i padisponueshëm. Ju lutem provoni përsëri.',
    liveStreaming: 'Po transmetohet live...',
    topic: 'Tema',
    responses: (count: number, total: number) => `${count}/${total} përgjigje`,
    words: 'fjalë',
    noResponse: 'Pa përgjigje',
    partial: 'Pjesërisht',
    error: 'Gabim',
    emptyTitle: 'Futni një temë për të filluar një debat me shumë perspektiva',
    emptySubtitle: '5 persona AI • Streaming elastik • Ruan rrjedhën e bisedës',
  },
} as const

function normalizeLangCode(input: string | null): string {
  if (!input) return ''
  return input.trim().toLowerCase().replace('_', '-').split('-')[0]
}

function sanitizePreferredLangCode(input: string | null): string {
  const normalized = normalizeLangCode(input)
  if (!normalized || normalized === 'auto') return ''
  return normalized
}

function detectBrowserLangCode(): string {
  if (typeof window === 'undefined') return ''
  return sanitizePreferredLangCode(window.navigator.language)
}

function decodeBase64Utf8(input: string): string {
  try {
    if (typeof window === 'undefined') return input
    const binary = window.atob(input)
    const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0))
    return new TextDecoder().decode(bytes)
  } catch {
    return input
  }
}

function parseCompactDebateEvent(eventType: string, payload: string): Record<string, unknown> | null {
  const normalized = (payload || '').trim()
  if (!normalized) return null

  try {
    const parsed = JSON.parse(normalized)
    if (parsed && typeof parsed === 'object') {
      return parsed as Record<string, unknown>
    }
  } catch {
    // compact non-JSON protocol fallback
  }

  const parts = normalized.split('|').map((part) => decodeBase64Utf8(part))

  if (eventType === 'thinking' && parts.length >= 4) {
    return {
      persona: parts[0],
      name: parts[1],
      emoji: parts[2],
      role: parts[3],
    }
  }

  if (eventType === 'response' && parts.length >= 6) {
    const parsedTokens = Number(parts[5])
    return {
      persona: parts[0],
      name: parts[1],
      emoji: parts[2],
      role: parts[3],
      status: parts[4],
      tokens: Number.isFinite(parsedTokens) ? parsedTokens : undefined,
    }
  }

  if (eventType === 'start' && parts.length >= 6) {
    const parsedPersonas = Number(parts[1])
    const parsedBudget = Number(parts[2])
    return {
      topic: parts[0],
      personas: Number.isFinite(parsedPersonas) ? parsedPersonas : undefined,
      max_tokens: Number.isFinite(parsedBudget) ? parsedBudget : undefined,
      language: {
        code: parts[3],
        name: parts[4],
        source: parts[5],
      },
    }
  }

  if (eventType === 'done') {
    return { status: parts[0] || 'ok' }
  }

  return null
}

async function readDebateErrorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const payload = await response.json()
    const detail = Array.isArray(payload?.detail)
      ? payload.detail.map((item: { msg?: string }) => item?.msg).filter(Boolean).join(' • ')
      : payload?.detail || payload?.error

    if (response.status === 429) {
      return 'Debate is temporarily busy. Please retry in a moment.'
    }

    if (typeof detail === 'string' && detail.trim()) {
      return detail.trim()
    }
  } catch {
    // ignore parse errors and use fallback
  }

  return fallback
}

function inferTopicLangCode(topic: string): string {
  const text = (topic || '').trim().toLowerCase()
  if (!text) return ''

  if (/(^|\s)(pershendetje|përshëndetje|jeni|gati|filluar|deb(at|ati)|nje|një|cfare|çfarë|ju|vlla)(\s|$|[!?.,;:])/i.test(text)) {
    return 'sq'
  }

  return ''
}

function isAlgebraBinaryTopic(input: string): boolean {
  const text = (input || '').toLowerCase()
  if (!text) return false
  if (/0b[01]+|\b[01]{5,}\b/.test(text)) return true
  if (/\d+\s*(xor|and|or|\+|\-|\*|\/|\^|>>|<<|&|\|)\s*\d+/i.test(text)) return true
  return /(algebra|equation|math|matrix|binary|bitwise|boolean|logic gate|xor|nand|nor)/i.test(text)
}

const PERSONAS = [
  { id: 'alba', name: 'Alba', emoji: '🌅', role: 'Optimist' },
  { id: 'albi', name: 'Albi', emoji: '🔧', role: 'Pragmatist' },
  { id: 'jona', name: 'Jona', emoji: '🔍', role: 'Skeptic' },
  { id: 'blerina', name: 'Blerina', emoji: '💡', role: 'Analyst' },
  { id: 'asi', name: 'ASI', emoji: '🧠', role: 'Meta-Thinker' },
]

function buildDebatePrefill(personaId: string, uiLanguage: 'en' | 'sq'): string {
  const copy = uiLanguage === 'sq'
    ? {
        alba: 'Po formuloj këndvështrimin optimist… ',
        albi: 'Po e kthej temën në hapa praktikë… ',
        jona: 'Po testoj rreziqet dhe kundërshtitë… ',
        blerina: 'Po mbledh evidencën dhe analizën… ',
        asi: 'Po lidh modelin më të gjerë… ',
      }
    : {
        alba: 'Framing the optimistic angle… ',
        albi: 'Turning the topic into practical steps… ',
        jona: 'Stress-testing the risks and objections… ',
        blerina: 'Gathering the evidence and analysis… ',
        asi: 'Connecting the higher-level pattern… ',
      }

  return copy[personaId as keyof typeof copy] || (uiLanguage === 'sq' ? 'Po analizoj… ' : 'Analyzing… ')
}

function DebatePageContent() {
  const searchParams = useSearchParams()
  const [topic, setTopic] = useState('')
  const [responses, setResponses] = useState<DebateResponse[]>([])
  const [streamingText, setStreamingText] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [activeSpeaker, setActiveSpeaker] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [linkedFromOcean, setLinkedFromOcean] = useState(false)
  const [returnToOceanUrl, setReturnToOceanUrl] = useState('/modules/curiosity-ocean')
  const [uiLanguage, setUiLanguage] = useState<'en' | 'sq'>('en')
  const [preferredLangCode, setPreferredLangCode] = useState('en')
  const abortRef = useRef<AbortController | null>(null)
  const pendingTokensRef = useRef<Record<string, string>>({})
  const streamingTextRef = useRef<Record<string, string>>({})
  const prefillActiveRef = useRef<Record<string, boolean>>({})
  const flushTimerRef = useRef<number | null>(null)
  const autoStartedRef = useRef(false)
  const sessionIdRef = useRef(`debate_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`)
  const conversationRef = useRef<string[]>([])

  useEffect(() => {
    return () => {
      if (flushTimerRef.current) {
        window.clearInterval(flushTimerRef.current)
        flushTimerRef.current = null
      }
    }
  }, [])

  useEffect(() => {
    const topicFromUrl = searchParams.get('topic')
    if (topicFromUrl && topicFromUrl.trim()) {
      setTopic(topicFromUrl.trim())
    }
  }, [searchParams])

  useEffect(() => {
    const from = (searchParams.get('from') || '').trim().toLowerCase()
    const explicitReturn = (searchParams.get('return_to') || '').trim()
    const fromOcean = from === 'ocean'
    setLinkedFromOcean(fromOcean)

    const returnTopic = (searchParams.get('topic') || '').trim()
    const returnLang = normalizeLangCode(searchParams.get('lang'))
    const params = new URLSearchParams()
    if (returnTopic) params.set('topic', returnTopic)
    if (returnLang) params.set('lang', returnLang)

    if (explicitReturn.startsWith('/')) {
      setReturnToOceanUrl(returnTopic || returnLang ? `${explicitReturn}${explicitReturn.includes('?') ? '&' : '?'}${params.toString()}` : explicitReturn)
      return
    }

    const defaultBase = '/modules/curiosity-ocean'
    setReturnToOceanUrl(returnTopic || returnLang ? `${defaultBase}?${params.toString()}` : defaultBase)
  }, [searchParams])

  useEffect(() => {
    const explicitLang = sanitizePreferredLangCode(searchParams.get('lang'))

    let storedLang = ''
    if (typeof window !== 'undefined') {
      try {
        storedLang = sanitizePreferredLangCode(window.localStorage.getItem('clisonix_language'))
      } catch {
        storedLang = ''
      }
    }

    const browserLang = detectBrowserLangCode()
    const resolved = explicitLang || storedLang || browserLang || 'en'
    setPreferredLangCode(resolved)
    setUiLanguage(resolved === 'sq' ? 'sq' : 'en')
  }, [searchParams])

  const ui = DEBATE_UI[uiLanguage]

  const startTokenFlushLoop = () => {
    if (flushTimerRef.current) return
    flushTimerRef.current = window.setInterval(() => {
      const pending = pendingTokensRef.current
      const personaIds = Object.keys(pending)
      if (personaIds.length === 0) return

      setStreamingText(prev => {
        const next = { ...prev }
        for (const personaId of personaIds) {
          const chunk = pending[personaId]
          if (!chunk) continue
          next[personaId] = (next[personaId] || '') + chunk
          streamingTextRef.current[personaId] = next[personaId]
        }
        pendingTokensRef.current = {}
        return next
      })
    }, 24)
  }

  const stopTokenFlushLoop = () => {
    if (flushTimerRef.current) {
      window.clearInterval(flushTimerRef.current)
      flushTimerRef.current = null
    }
  }

  const startDebate = async () => {
    if (!topic.trim()) return

    // Cancel previous request if any
    if (abortRef.current) {
      abortRef.current.abort()
    }
    abortRef.current = new AbortController()

    setLoading(true)
    setError(null)
    setResponses([])
    setStreamingText({})
    setProgress(0)
    streamingTextRef.current = {}
    pendingTokensRef.current = {}
    prefillActiveRef.current = {}
    startTokenFlushLoop()

    const explicitLang = sanitizePreferredLangCode(searchParams.get('lang'))
    const inferredTopicLang = sanitizePreferredLangCode(inferTopicLangCode(topic))
    const browserLang = detectBrowserLangCode()
    const preferredLanguage = explicitLang || preferredLangCode || inferredTopicLang || browserLang || 'en'
    const languageName = preferredLanguage
      ? (LANGUAGE_NAMES[preferredLanguage] || preferredLanguage.toUpperCase())
      : undefined
    const useBinaryProfile = isAlgebraBinaryTopic(topic)
    const conversationContext = conversationRef.current.slice(-8)

    try {
      // Use streaming endpoint for elastic responses
      const res = await fetch('/api/debate/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          stream_mode: 'compact',
          max_tokens: -1,
          preferred_language: preferredLanguage,
          language_name: languageName,
          quality_profile: 'high',
          language_layers: useBinaryProfile ? 4 : 6,
          binary: useBinaryProfile,
          response_format: useBinaryProfile ? 'cbor2' : 'json',
          session_id: sessionIdRef.current,
          conversation_context: conversationContext,
        }),
        signal: abortRef.current.signal
      })

      if (!res.ok) {
        throw new Error(await readDebateErrorMessage(res, ui.connectError))
      }

      const reader = res.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) throw new Error('No stream available')

      let completedCount = 0
      let sseBuffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        sseBuffer += decoder.decode(value, { stream: true })
        const events = sseBuffer.split('\n\n')
        sseBuffer = events.pop() || ''

        for (const event of events) {
          const eventType = (event.split('\n').find(line => line.startsWith('event:')) || '').replace('event:', '').trim()
          const dataLines = event
            .split('\n')
            .filter(line => line.startsWith('data:'))
            .map(line => line.replace(/^data:\s?/, ''))

          if (dataLines.length === 0) continue

          const payload = dataLines.join('\n')

          if (eventType === 't') {
            try {
              const sep = payload.indexOf(':')
              if (sep > 0) {
                const personaId = payload.slice(0, sep)
                const encoded = payload.slice(sep + 1)
                const token = decodeBase64Utf8(encoded)

                if (prefillActiveRef.current[personaId]) {
                  prefillActiveRef.current[personaId] = false
                  streamingTextRef.current[personaId] = ''
                  setStreamingText(prev => ({ ...prev, [personaId]: '' }))
                  pendingTokensRef.current[personaId] = token
                } else {
                  pendingTokensRef.current[personaId] = (pendingTokensRef.current[personaId] || '') + token
                }
              }
            } catch {
            }
            continue
          }

          if (eventType === 'thinking') {
            const info = parseCompactDebateEvent('thinking', payload)
            const personaId = typeof info?.persona === 'string' ? info.persona : null
            if (personaId) {
              setActiveSpeaker(personaId)
              prefillActiveRef.current[personaId] = true
              const prefill = buildDebatePrefill(personaId, uiLanguage)
              setStreamingText(prev => {
                const next = { ...prev, [personaId]: prefill }
                streamingTextRef.current[personaId] = prefill
                return next
              })
            }
            continue
          }

          if (eventType === 'prefill') {
            try {
              const sep = payload.indexOf(':')
              if (sep > 0) {
                const personaId = payload.slice(0, sep)
                const encoded = payload.slice(sep + 1)
                const text = decodeBase64Utf8(encoded)
                prefillActiveRef.current[personaId] = true
                setStreamingText(prev => {
                  const next = { ...prev, [personaId]: text }
                  streamingTextRef.current[personaId] = text
                  return next
                })
              }
            } catch {
            }
            continue
          }

          if (eventType === 'response') {
            const meta = parseCompactDebateEvent('response', payload)
            const personaId = typeof meta?.persona === 'string' ? meta.persona : null
            if (personaId) {
              prefillActiveRef.current[personaId] = false
              const fromStream = `${streamingTextRef.current[personaId] || ''}${pendingTokensRef.current[personaId] || ''}`
              const finalResponse = (meta.response && String(meta.response).trim().length > 0)
                ? String(meta.response)
                : fromStream

              setResponses(prev => [...prev, {
                persona: personaId,
                name: typeof meta?.name === 'string' ? meta.name : PERSONAS.find(p => p.id === personaId)?.name || personaId,
                emoji: typeof meta?.emoji === 'string' ? meta.emoji : PERSONAS.find(p => p.id === personaId)?.emoji || '🤖',
                role: typeof meta?.role === 'string' ? meta.role : PERSONAS.find(p => p.id === personaId)?.role || 'Perspective',
                response: finalResponse,
                status: (typeof meta?.status === 'string' ? (meta.status as 'success' | 'error' | 'partial') : 'success'),
                tokens: typeof meta?.tokens === 'number' ? meta.tokens : undefined,
              }])

              setStreamingText(prev => {
                const newState = { ...prev }
                delete newState[personaId]
                delete streamingTextRef.current[personaId]
                delete pendingTokensRef.current[personaId]
                return newState
              })

              completedCount++
              setProgress((completedCount / PERSONAS.length) * 100)
              setActiveSpeaker(null)
            }
            continue
          }

          if (eventType === 'done') {
            setActiveSpeaker(null)
            continue
          }

          try {
            const data = JSON.parse(payload)

            if (data.type === 'thinking') {
              setActiveSpeaker(data.persona)
              prefillActiveRef.current[data.persona] = true
              const prefill = buildDebatePrefill(data.persona, uiLanguage)
              setStreamingText(prev => {
                const next = { ...prev, [data.persona]: prefill }
                streamingTextRef.current[data.persona] = prefill
                return next
              })
            } else if (data.type === 'token') {
              if (prefillActiveRef.current[data.persona]) {
                prefillActiveRef.current[data.persona] = false
                streamingTextRef.current[data.persona] = ''
                setStreamingText(prev => ({ ...prev, [data.persona]: '' }))
                pendingTokensRef.current[data.persona] = data.token
              } else {
                pendingTokensRef.current[data.persona] = (pendingTokensRef.current[data.persona] || '') + data.token
              }
            } else if (data.type === 'response') {
              const personaId = data.data.persona
              prefillActiveRef.current[personaId] = false
              const fromStream = `${streamingTextRef.current[personaId] || ''}${pendingTokensRef.current[personaId] || ''}`
              const finalResponse = (data.data.response && String(data.data.response).trim().length > 0)
                ? data.data.response
                : fromStream

              setResponses(prev => [...prev, { ...data.data, response: finalResponse }])
              setStreamingText(prev => {
                const newState = { ...prev }
                delete newState[personaId]
                delete streamingTextRef.current[personaId]
                delete pendingTokensRef.current[personaId]
                return newState
              })
              completedCount++
              setProgress((completedCount / PERSONAS.length) * 100)
              setActiveSpeaker(null)
            } else if (data.type === 'done') {
              setActiveSpeaker(null)
            }
          } catch {
            // Skip parse errors
          }
        }
      }
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        setError(ui.cancelled)
      } else {
        // Fallback to non-streaming
        try {
          const res = await fetch('/api/debate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              topic,
              max_tokens: -1,
              preferred_language: preferredLanguage,
              language_name: languageName,
              quality_profile: 'high',
              language_layers: useBinaryProfile ? 4 : 6,
              binary: useBinaryProfile,
              response_format: useBinaryProfile ? 'cbor2' : 'json',
              session_id: sessionIdRef.current,
              conversation_context: conversationContext,
            })
          })
          if (res.ok) {
            const data = await res.json()
            setResponses(data.responses || [])
          } else {
            setError(await readDebateErrorMessage(res, ui.connectError))
          }
        } catch (fallbackErr) {
          const message = fallbackErr instanceof Error && fallbackErr.message
            ? fallbackErr.message
            : ui.connectError
          setError(message)
        }
      }
    } finally {
      if (topic.trim()) {
        conversationRef.current = [...conversationRef.current, topic.trim()].slice(-12)
      }
      stopTokenFlushLoop()
      setActiveSpeaker(null)
      setLoading(false)
      abortRef.current = null
    }
  }

  useEffect(() => {
    const topicFromUrl = searchParams.get('topic')
    const shouldAutostart = searchParams.get('autostart') === '1'
    if (!shouldAutostart || autoStartedRef.current) return
    if (!topicFromUrl || !topicFromUrl.trim()) return
    if (loading) return

    autoStartedRef.current = true
    setTopic(topicFromUrl.trim())
    window.setTimeout(() => {
      void startDebate()
    }, 0)
  }, [searchParams, loading])

  const cancelDebate = () => {
    if (abortRef.current) {
      abortRef.current.abort()
    }
  }

  const getResponseForPersona = (personaId: string) => {
    return responses.find(r => r.persona === personaId)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-700/70 bg-slate-900/40 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center text-lg">
              🎭
            </div>
            <div>
              <h1 className="text-lg font-semibold text-slate-100">{ui.title}</h1>
              <p className="text-xs text-slate-300">{ui.subtitle}</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {linkedFromOcean && (
              <a href={returnToOceanUrl} className="text-sm text-slate-300 hover:text-white">
                {ui.backToOcean}
              </a>
            )}
            <a href="/modules" className="text-sm text-slate-300 hover:text-white">
              {ui.back}
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">

        {/* Progress Bar */}
        {loading && (
          <div className="mb-6">
            <div className="h-1 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-xs text-slate-300 mt-2 text-center">
              {activeSpeaker ? ui.thinking(PERSONAS.find(p => p.id === activeSpeaker)?.name) : ui.processing}
            </p>
          </div>
        )}

        {/* Personas */}
        <div className="grid grid-cols-5 gap-3 mb-8">
          {PERSONAS.map((p) => {
            const resp = getResponseForPersona(p.id)
            const isActive = activeSpeaker === p.id
            const hasResponse = !!resp

            return (
              <div
                key={p.id}
                className={`text-center p-4 rounded-xl border transition-all ${
                  isActive
                    ? 'bg-blue-900/20 border-blue-600 animate-pulse'
                    : hasResponse
                      ? resp.status === 'success'
                        ? 'bg-green-900/10 border-green-800'
                        : 'bg-yellow-900/10 border-yellow-800'
                          : 'bg-slate-800/70 border-slate-600'
                }`}
              >
                <div className="text-2xl mb-2">{p.emoji}</div>
                <div className="text-sm font-medium text-slate-100">{p.name}</div>
                <div className="text-xs text-slate-300">{p.role}</div>
                {isActive && (
                  <div className="mt-2 flex justify-center gap-1">
                    <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}} />
                    <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}} />
                    <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}} />
                  </div>
                )}
                {hasResponse && !isActive && (
                  <div className="mt-2 text-xs text-slate-300">
                    {resp.tokens ? `${resp.tokens} words` : '✓'}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Input */}
        <div className="bg-slate-800/80 rounded-xl p-5 border border-slate-600 mb-6">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !loading && startDebate()}
            placeholder={ui.placeholder}
            className="w-full bg-transparent text-slate-100 placeholder-slate-300 focus:outline-none text-sm"
            disabled={loading}
          />
          <div className="flex items-center justify-between pt-4 mt-4 border-t border-slate-600">
            <div className="flex flex-wrap gap-2">
              {ui.suggestions.map((t) => (
                <button
                  key={t}
                  onClick={() => setTopic(t)}
                  disabled={loading}
                  className="px-3 py-1.5 bg-slate-700 text-slate-200 text-xs rounded-lg hover:bg-slate-600 hover:text-white transition-colors disabled:opacity-50"
                >
                  {t}
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              {loading && (
                <button
                  onClick={cancelDebate}
                  className="px-4 py-2 bg-red-900/25 text-red-300 text-sm font-medium rounded-lg hover:bg-red-900/40 transition-colors"
                >
                  {ui.stop}
                </button>
              )}
              <button
                onClick={startDebate}
                disabled={loading || !topic.trim()}
                className="px-5 py-2 bg-white text-slate-900 text-sm font-medium rounded-lg hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? ui.streaming : ui.start}
              </button>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-4 text-red-400 text-sm mb-6">
            {error}
          </div>
        )}

        {/* LIVE Streaming Response */}
        {activeSpeaker && streamingText[activeSpeaker] && (
          <div className="bg-slate-800/80 rounded-xl p-5 border border-blue-500/60 mb-6">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 bg-blue-900/30 rounded-lg flex items-center justify-center text-xl flex-shrink-0">
                {PERSONAS.find(p => p.id === activeSpeaker)?.emoji || '🤖'}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-medium text-blue-400">
                    {PERSONAS.find(p => p.id === activeSpeaker)?.name}
                  </span>
                  <span className="text-xs text-blue-500/70">{ui.liveStreaming}</span>
                  <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                </div>
                <p className="text-slate-100 text-sm leading-relaxed whitespace-pre-wrap">
                  {streamingText[activeSpeaker]}
                  <span className="inline-block w-1.5 h-4 bg-blue-400 ml-0.5 animate-blink" />
                </p>
              </div>
            </div>
          </div>
        )}
        {/* Debate Results - Real-time streaming */}
        {responses.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-200">{ui.topic}: <span className="text-white">{topic}</span></span>
              <span className="text-slate-300">{ui.responses(responses.filter(r => r.status === 'success').length, PERSONAS.length)}</span>
            </div>

            {responses.map((r, idx) => (
              <div
                key={r.persona}
                className="bg-slate-800/80 rounded-xl p-5 border border-slate-600 animate-fadeIn"
                style={{animationDelay: `${idx * 100}ms`}}
              >
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center text-xl flex-shrink-0">
                    {r.emoji}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-medium text-slate-100">{r.name}</span>
                      <span className="text-xs text-slate-300">{r.role}</span>
                      {r.status === 'partial' && (
                        <span className="px-2 py-0.5 bg-yellow-500/10 text-yellow-400 text-xs rounded">
                          {ui.partial}
                        </span>
                      )}
                      {r.status === 'error' && (
                        <span className="px-2 py-0.5 bg-red-500/10 text-red-400 text-xs rounded">
                          {ui.error}
                        </span>
                      )}
                      {r.tokens && (
                        <span className="px-2 py-0.5 bg-slate-700 text-slate-200 text-xs rounded">
                          {r.tokens} {ui.words}
                        </span>
                      )}
                    </div>
                    <p className="text-slate-100 text-sm leading-relaxed whitespace-pre-wrap">
                      {r.response || ui.noResponse}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty */}
        {responses.length === 0 && !loading && !error && (
          <div className="text-center py-20 text-slate-300">
            <div className="text-5xl mb-4">🎭</div>
            <p className="text-sm">{ui.emptyTitle}</p>
            <p className="text-xs text-slate-300 mt-1">{ui.emptySubtitle}</p>
          </div>
        )}
      </main>

      {/* CSS for animations */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  )
}

export default function DebatePage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-slate-100" />}>
      <DebatePageContent />
    </Suspense>
  )
}
