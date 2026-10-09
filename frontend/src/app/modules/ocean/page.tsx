'use client'

import { useEffect, useState, useCallback } from 'react'
import Link from 'next/link'

interface AlphabetLayer {
  name: string
  type: 'greek' | 'albanian' | 'meta'
  number: number
}

interface OceanStatus {
  status: string
  personas: number
  laboratories: number
  alphabetLayers: number
  binaryProtocol: boolean
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  persona?: string
}

export default function OceanPage() {
  const [status, setStatus] = useState<OceanStatus>({
    status: 'loading',
    personas: 14,
    laboratories: 23,
    alphabetLayers: 61,
    binaryProtocol: true
  })
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'layers' | 'binary'>('chat')

  // Greek alphabet for display
  const greekLetters = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']
  const albanianLetters = ['a', 'b', 'c', 'ç', 'd', 'dh', 'e', 'ë', 'f', 'g', 'gj', 'h', 'i', 'j', 'k', 'l', 'll', 'm', 'n', 'nj', 'o', 'p', 'q', 'r', 'rr', 's', 'sh', 't', 'th', 'u', 'v', 'x', 'xh', 'y', 'z', 'zh']

  useEffect(() => {
    // Check Ocean Core status
    const checkStatus = async () => {
      try {
        const res = await fetch('http://localhost:8030/api/status')
        if (res.ok) {
          const data = await res.json()
          setStatus({
            status: 'operational',
            personas: data.personas || 14,
            laboratories: data.data_sources?.laboratories || 23,
            alphabetLayers: 61,
            binaryProtocol: true
          })
        }
      } catch (error) {
        setStatus(prev => ({ ...prev, status: 'offline' }))
      }
    }

    checkStatus()
    const interval = setInterval(checkStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const res = await fetch('http://localhost:8030/api/chat/orchestrated', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      })

      if (res.ok) {
        const data = await res.json()
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: data.fused_answer || data.response || 'No response',
          timestamp: new Date().toISOString(),
          persona: data.primary_persona
        }
        setMessages(prev => [...prev, assistantMessage])
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠️ Could not connect to Ocean Core. Make sure it\'s running on port 8030.',
        timestamp: new Date().toISOString()
      }])
    }

    setIsLoading(false)
  }, [input, isLoading])

  return (
    <div className="min-h-screen text-white p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-black bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400 bg-clip-text text-transparent">
            🌊 Ocean Core
          </h1>
          <p className="text-gray-400 mt-1">
            61 Alphabet Layers • Binary Algebra • 14 Personas
          </p>
        </div>
        <div className={`px-4 py-2 rounded-full text-sm font-medium ${
          status.status === 'operational' ? 'bg-green-900 text-green-300 border border-green-700' :
          status.status === 'offline' ? 'bg-red-900 text-red-300 border border-red-700' :
          'bg-yellow-900 text-yellow-300 border border-yellow-700'
        }`}>
          ● {status.status.toUpperCase()}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gradient-to-br from-blue-900/50 to-blue-800/30 p-4 rounded-xl border border-blue-700/50">
          <div className="text-3xl font-bold text-blue-300">61</div>
          <div className="text-sm text-blue-400">Alphabet Layers</div>
          <div className="text-xs text-blue-500 mt-1">Greek 24 + Albanian 36 + Meta 1</div>
        </div>
        <div className="bg-gradient-to-br from-purple-900/50 to-purple-800/30 p-4 rounded-xl border border-purple-700/50">
          <div className="text-3xl font-bold text-purple-300">{status.personas}</div>
          <div className="text-sm text-purple-400">Personas</div>
          <div className="text-xs text-purple-500 mt-1">Specialist Modules</div>
        </div>
        <div className="bg-gradient-to-br from-green-900/50 to-green-800/30 p-4 rounded-xl border border-green-700/50">
          <div className="text-3xl font-bold text-green-300">{status.laboratories}</div>
          <div className="text-sm text-green-400">Laboratories</div>
          <div className="text-xs text-green-500 mt-1">City-Named Labs</div>
        </div>
        <div className="bg-gradient-to-br from-orange-900/50 to-orange-800/30 p-4 rounded-xl border border-orange-700/50">
          <div className="text-3xl font-bold text-orange-300">BIN</div>
          <div className="text-sm text-orange-400">Protocol</div>
          <div className="text-xs text-orange-500 mt-1">CBOR2 / MessagePack</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {['chat', 'layers', 'binary'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              activeTab === tab
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {tab === 'chat' && '💬 Chat'}
            {tab === 'layers' && '🔤 Layers'}
            {tab === 'binary' && '🔢 Binary'}
          </button>
        ))}
      </div>

      {/* Chat Tab */}
      {activeTab === 'chat' && (
        <div className="bg-gray-900 rounded-xl border border-gray-700 overflow-hidden">
          {/* Chat Messages */}
          <div className="h-96 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 py-12">
                <div className="text-4xl mb-4">🌊</div>
                <p>Start a conversation with Ocean Core</p>
                <p className="text-sm mt-2">Ask anything - 14 personas will analyze your query</p>
              </div>
            )}
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] p-3 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-200'
                }`}>
                  {msg.persona && (
                    <div className="text-xs text-blue-400 mb-1">
                      🎭 {msg.persona}
                    </div>
                  )}
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-800 p-3 rounded-lg">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-100" />
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-200" />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t border-gray-700 p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Ask Ocean Core anything..."
                className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Layers Tab */}
      {activeTab === 'layers' && (
        <div className="space-y-6">
          {/* Greek Layers (1-24) */}
          <div className="bg-gray-900 rounded-xl border border-gray-700 p-6">
            <h3 className="text-lg font-bold mb-4 text-blue-400">
              🇬🇷 Greek Layers (1-24) - Pure Mathematics
            </h3>
            <div className="grid grid-cols-8 md:grid-cols-12 gap-2">
              {greekLetters.map((letter, idx) => (
                <div
                  key={letter}
                  className="bg-blue-900/30 border border-blue-700/50 rounded-lg p-3 text-center hover:bg-blue-800/50 transition-colors cursor-pointer"
                  title={`Layer ${idx + 1}`}
                >
                  <div className="text-2xl">{letter}</div>
                  <div className="text-xs text-blue-400">{idx + 1}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Albanian Layers (25-60) */}
          <div className="bg-gray-900 rounded-xl border border-gray-700 p-6">
            <h3 className="text-lg font-bold mb-4 text-red-400">
              🇦🇱 Albanian Layers (25-60) - Phonetic Mathematics
            </h3>
            <div className="grid grid-cols-6 md:grid-cols-12 gap-2">
              {albanianLetters.map((letter, idx) => (
                <div
                  key={letter}
                  className="bg-red-900/30 border border-red-700/50 rounded-lg p-3 text-center hover:bg-red-800/50 transition-colors cursor-pointer"
                  title={`Layer ${idx + 25}`}
                >
                  <div className="text-lg font-bold">{letter}</div>
                  <div className="text-xs text-red-400">{idx + 25}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Meta Layer (61) */}
          <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-xl border border-purple-500 p-6 text-center">
            <div className="text-5xl mb-2">Ω+</div>
            <h3 className="text-xl font-bold text-purple-300">Meta Layer 61</h3>
            <p className="text-purple-400 text-sm">Unified Consciousness - Combines all 60 layers</p>
          </div>
        </div>
      )}

      {/* Binary Tab */}
      {activeTab === 'binary' && (
        <div className="bg-gray-900 rounded-xl border border-gray-700 p-6">
          <h3 className="text-lg font-bold mb-6 text-green-400">
            🔢 Binary Algebra Engine
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Operations */}
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-3">Operations</h4>
              <div className="grid grid-cols-4 gap-2">
                {['AND', 'OR', 'XOR', 'NOT', 'NAND', 'NOR', 'SHL', 'SHR', 'ADD', 'SUB', 'MUL', 'DIV'].map(op => (
                  <div
                    key={op}
                    className="bg-gray-800 border border-gray-600 rounded p-2 text-center text-sm font-mono hover:bg-gray-700 cursor-pointer"
                  >
                    {op}
                  </div>
                ))}
              </div>
            </div>

            {/* Protocols */}
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-3">Binary Protocols</h4>
              <div className="space-y-2">
                <div className="bg-green-900/30 border border-green-700 rounded p-3 flex items-center justify-between">
                  <span>CBOR2</span>
                  <span className="text-green-400 text-sm">● Active (Default)</span>
                </div>
                <div className="bg-gray-800 border border-gray-600 rounded p-3 flex items-center justify-between">
                  <span>MessagePack</span>
                  <span className="text-gray-400 text-sm">Available</span>
                </div>
                <div className="bg-gray-800 border border-gray-600 rounded p-3 flex items-center justify-between">
                  <span>Custom Binary</span>
                  <span className="text-gray-400 text-sm">Available</span>
                </div>
              </div>
            </div>
          </div>

          {/* API Info */}
          <div className="mt-6 bg-gray-800 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-400 mb-2">Binary API Endpoints</h4>
            <div className="font-mono text-sm space-y-1 text-gray-300">
              <div>POST /api/v1/bin/compute - Process through layers</div>
              <div>POST /api/v1/bin/layer - Single layer execution</div>
              <div>POST /api/v1/bin/compose - Word composition</div>
              <div>POST /api/v1/bin/algebra - Binary algebra ops</div>
              <div>POST /api/v1/bin/stream - Signal stream processing</div>
              <div>POST /api/v1/bin/matrix - Matrix operations</div>
            </div>
          </div>
        </div>
      )}

      {/* Footer Links */}
      <div className="mt-8 flex justify-center gap-6 text-sm">
        <a
          href="http://localhost:8030/api/v1/docs"
          target="_blank"
          className="text-blue-400 hover:text-blue-300"
        >
          📚 Ocean API Docs
        </a>
        <a
          href="http://localhost:8061/api/v1/docs"
          target="_blank"
          className="text-green-400 hover:text-green-300"
        >
          🔤 Alphabet API Docs
        </a>
        <Link href="/" className="text-gray-400 hover:text-gray-300">
          ← Back to Home
        </Link>
      </div>
    </div>
  )
}
