'use client'
/**
 * SPECIALIZED EXPERT CHAT
 * =======================
 * 
 * Expert-level conversations in specialized domains:
 * - Neuroscience & Brain Research
 * - AI/ML & Deep Learning
 * - Quantum Physics & Energy
 * - IoT/LoRa & Sensor Networks
 * - Cybersecurity & Encryption
 * - Bioinformatics & Genetics
 * - Data Science & Analytics
 * - Marine Biology & Environmental Science
 */

import { useState, useEffect, useRef } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  domain?: string
  confidence?: number
  sources?: string[]
}

interface Domain {
  id: string
  name: string
  icon: string
  description: string
  keywords: string[]
}

const EXPERT_DOMAINS: Domain[] = [
  { id: 'neuro', name: 'Neuroscience', icon: '🧠', description: 'Brain research, cognition, neural pathways', keywords: ['brain', 'neuron', 'cognition', 'memory'] },
  { id: 'ai', name: 'AI & Deep Learning', icon: '🤖', description: 'Machine learning, neural networks, AGI', keywords: ['ai', 'ml', 'neural network', 'deep learning'] },
  { id: 'quantum', name: 'Quantum Physics', icon: '⚛️', description: 'Quantum mechanics, entanglement, computing', keywords: ['quantum', 'physics', 'entanglement', 'qubit'] },
  { id: 'iot', name: 'IoT & LoRa Networks', icon: '📡', description: 'Sensors, gateways, embedded systems', keywords: ['iot', 'lora', 'sensor', 'embedded'] },
  { id: 'security', name: 'Cybersecurity', icon: '🔐', description: 'Encryption, vulnerabilities, protocols', keywords: ['security', 'encryption', 'vulnerability', 'firewall'] },
  { id: 'bio', name: 'Bioinformatics', icon: '🧬', description: 'Genetics, DNA analysis, proteins', keywords: ['genetics', 'dna', 'protein', 'genome'] },
  { id: 'data', name: 'Data Science', icon: '📊', description: 'Statistics, analytics, visualization', keywords: ['data', 'statistics', 'analytics', 'visualization'] },
  { id: 'marine', name: 'Marine Biology', icon: '🌊', description: 'Ocean ecosystems, marine life', keywords: ['ocean', 'marine', 'ecosystem', 'coral'] },
]

const API_PROXY = '/api/ocean/specialized'

export default function SpecializedChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null)
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Check API status
  useEffect(() => {
    const checkApi = async () => {
      try {
        const res = await fetch(API_PROXY)
        setApiStatus(res.ok ? 'online' : 'offline')
      } catch {
        setApiStatus('offline')
      }
    }
    checkApi()
  }, [])

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Welcome message
  useEffect(() => {
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: `🎓 **Welcome to Specialized Expert Chat**

I'm an expert-level AI assistant trained in advanced domains. Select a specialty below or ask me anything about:

${EXPERT_DOMAINS.map(d => `- ${d.icon} **${d.name}**: ${d.description}`).join('\n')}

_My responses are powered by domain-specific knowledge bases and research databases._`,
      timestamp: new Date()
    }])
  }, [])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch(API_PROXY, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          domain: selectedDomain
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        const assistantMessage: Message = {
          id: `ai-${Date.now()}`,
          role: 'assistant',
          content: data.response || data.fused_answer || 'Processing your specialized query...',
          timestamp: new Date(),
          domain: data.domain || data.query_category,
          confidence: data.confidence,
          sources: data.sources || data.sources_cited
        }
        
        setMessages(prev => [...prev, assistantMessage])
      } else {
        throw new Error(`API error: ${response.status}`)
      }
    } catch {
      setMessages(prev => [...prev, {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: '⚠️ **Connection Error**\n\nUnable to reach Ocean Core API. Please verify the service is running on port 8030.',
        timestamp: new Date()
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-800 text-white">
      {/* Header */}
      <div className="border-b border-purple-500/30 bg-black/30 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
                🎓 Specialized Expert Chat
              </h1>
              <p className="text-sm text-gray-400 mt-1">
                Expert-level AI conversations in advanced domains
              </p>
            </div>
            <div className={`px-3 py-1 rounded-full text-xs ${
              apiStatus === 'online' ? 'bg-green-500/20 text-green-400' :
              apiStatus === 'offline' ? 'bg-red-500/20 text-red-400' :
              'bg-yellow-500/20 text-yellow-400'
            }`}>
              {apiStatus === 'online' ? '● Online' : apiStatus === 'offline' ? '● Offline' : '● Checking...'}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Domain Selector */}
          <div className="lg:col-span-1">
            <div className="bg-black/40 rounded-xl p-4 border border-purple-500/20">
              <h3 className="text-sm font-semibold text-purple-400 mb-3">Select Expertise</h3>
              <div className="space-y-2">
                {EXPERT_DOMAINS.map(domain => (
                  <button
                    key={domain.id}
                    onClick={() => setSelectedDomain(selectedDomain === domain.id ? null : domain.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg transition-all text-sm ${
                      selectedDomain === domain.id
                        ? 'bg-purple-600/40 border border-purple-400'
                        : 'bg-gray-800/50 hover:bg-gray-700/50 border border-transparent'
                    }`}
                  >
                    <span className="mr-2">{domain.icon}</span>
                    {domain.name}
                  </button>
                ))}
              </div>
              {selectedDomain && (
                <div className="mt-4 p-3 bg-purple-900/20 rounded-lg border border-purple-500/20">
                  <p className="text-xs text-purple-300">
                    {EXPERT_DOMAINS.find(d => d.id === selectedDomain)?.description}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3">
            <div className="bg-black/40 rounded-xl border border-purple-500/20 flex flex-col h-[600px]">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map(msg => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[80%] rounded-xl px-4 py-3 ${
                      msg.role === 'user'
                        ? 'bg-purple-600/40 border border-purple-500/30'
                        : 'bg-gray-800/60 border border-gray-700/30'
                    }`}>
                      <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
                      {msg.domain && (
                        <div className="mt-2 text-xs text-purple-400">
                          Domain: {msg.domain}
                          {msg.confidence && ` • Confidence: ${Math.round(msg.confidence * 100)}%`}
                        </div>
                      )}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-1 text-xs text-gray-500">
                          Sources: {msg.sources.join(', ')}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-800/60 rounded-xl px-4 py-3 border border-gray-700/30">
                      <div className="flex items-center space-x-2">
                        <div className="animate-pulse w-2 h-2 bg-purple-500 rounded-full"></div>
                        <div className="animate-pulse w-2 h-2 bg-purple-500 rounded-full delay-100"></div>
                        <div className="animate-pulse w-2 h-2 bg-purple-500 rounded-full delay-200"></div>
                        <span className="text-sm text-gray-400 ml-2">Expert analyzing...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="border-t border-purple-500/20 p-4">
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                    placeholder={selectedDomain 
                      ? `Ask about ${EXPERT_DOMAINS.find(d => d.id === selectedDomain)?.name}...`
                      : 'Ask an expert question...'
                    }
                    className="flex-1 bg-gray-800/50 border border-gray-700 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-purple-500 transition-colors"
                    disabled={loading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={loading || !input.trim()}
                    className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg font-medium text-sm hover:opacity-90 transition-opacity disabled:opacity-50"
                  >
                    {loading ? '...' : 'Send'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}







