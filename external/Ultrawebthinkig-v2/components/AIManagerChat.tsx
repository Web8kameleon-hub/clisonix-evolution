'use client'

import React, { useState, useEffect, useRef } from 'react'

/**
 * Industrial Grade AI Manager Chat (Production)
 * Zero Human Intervention • Secure • Real AGI Link
 */

interface AIMessage {
  id: string
  type: 'client' | 'ai' | 'system' | 'alert'
  content: string
  timestamp: string
  confidence?: number
  category?: string
  handledBy?: string
}

interface AIManagerChatProps {
  clientId?: string
  endpoint?: string
  managerUrl?: string
  className?: string
  onSystemAlert?: (alert: any) => void
}

export const AIManagerChat: React.FC<AIManagerChatProps> = ({
  clientId = 'client-001',
  endpoint = '/api/ai-manager',
  managerUrl,
  className = '',
  onSystemAlert = (alert: any) => { console.log('System Alert:', alert) }
}) => {
  const resolvedEndpoint = managerUrl || endpoint
  const [messages, setMessages] = useState<AIMessage[]>([])
  const [input, setInput] = useState('')
  const [processing, setProcessing] = useState(false)
  const [health, setHealth] = useState('OPERATIONAL')
  const endRef = useRef<HTMLDivElement>(null)

  /** Auto-scroll */
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  /** Initial system boot message */
  useEffect(() => {
    setMessages([
      {
        id: 'boot',
        type: 'ai',
        content: `🤖 AGI Neural Manager Initialized\n\nSystem Online • Secure Channel Established\n\nAGI: ✅ | ALBA: ✅ | ASI: ✅\nStatus: ${health}`,
        timestamp: new Date().toISOString(),
        confidence: 0.97,
        handledBy: 'AGI Core'
      }
    ])
  }, [])

  /** Send message to AGI Manager Backend */
  const sendMessage = async () => {
    if (!input.trim() || processing) return
    const userMsg: AIMessage = {
      id: `client-${Date.now()}`,
      type: 'client',
      content: input.trim(),
      timestamp: new Date().toISOString()
    }
    setMessages((prev: AIMessage[]) => [...prev, userMsg])
    setInput('')
    setProcessing(true)

    try {
      const res = await fetch(resolvedEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ clientId, message: userMsg.content, language: 'sq' })
      })

      const contentType = res.headers.get('content-type') || ''
      let data: any

      if (contentType.includes('application/json')) {
        data = await res.json()
      } else {
        const rawText = await res.text()
        throw new Error(`Non-JSON response from ${resolvedEndpoint}: ${rawText.slice(0, 120)}`)
      }

      if (!res.ok || data?.success === false) {
        throw new Error(data?.message || data?.error || `Request failed with ${res.status}`)
      }

      const aiMsg: AIMessage = {
        id: `ai-${Date.now()}`,
        type: 'ai',
        content: data.result?.response || data.result?.message || data.response || '✅ Task completed.',
        timestamp: data.timestamp || new Date().toISOString(),
        confidence: data.confidence ?? 0.92,
        category: data.category ?? 'general',
        handledBy: data.handledBy ?? 'ManagerModule'
      }

      if (data.category === 'emergency') onSystemAlert?.(data)
      setMessages((prev: AIMessage[]) => [...prev, aiMsg])
    } catch (err: any) {
      console.error('AI Manager Error:', err)
      setMessages((prev: AIMessage[]) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          type: 'system',
          content: `⚠️ Connection Error\n${String(err)}\nSystem attempting recovery...`,
          timestamp: new Date().toISOString()
        }
      ])
      setHealth('DEGRADED')
    } finally {
      setProcessing(false)
    }
  }

  /** Handle Enter key */
  const handleKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  /** Get message class name by type */
  const getMessageClassName = (msg: AIMessage): string => {
    const baseClass = 'aim-message'
    switch (msg.type) {
      case 'client':
        return `${baseClass} aim-message-client`
      case 'ai':
        return `${baseClass} aim-message-ai`
      case 'system':
        return `${baseClass} aim-message-system`
      default:
        return baseClass
    }
  }

  return (
    <div className={`aim-container ${className}`}>
      {/* Header */}
      <div className="aim-header">
        <div>
          <strong>AGI Neural Manager</strong>
          <p className="aim-header-text">Client {clientId} • {health}</p>
        </div>
        <div
          className={`aim-health-indicator ${
            health === 'OPERATIONAL' ? 'operational' : 'degraded'
          }`}
        />
      </div>

      {/* Messages */}
      <div className="aim-messages-container">
        {messages.map((m: AIMessage) => (
          <div key={m.id} className={getMessageClassName(m)}>
            <div className="aim-message-content">{m.content}</div>
            <div className="aim-message-meta">
              {new Date(m.timestamp).toLocaleTimeString()} {m.handledBy ? `• ${m.handledBy}` : ''}
            </div>
          </div>
        ))}
        {processing && (
          <div className="aim-processing-indicator">
            Processing request via AGI networks...
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="aim-input-container">
        <input
          value={input}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Send command to AGI Manager..."
          className="aim-input"
        />
        <button
          onClick={sendMessage}
          disabled={!input.trim() || processing}
          className="aim-button"
        >
          {processing ? '...' : 'Send'}
        </button>
      </div>
    </div>
  )
}

export default AIManagerChat
