'use client';

/**
 * Ocean Helpers UI Component
 * Integrates helper engine with chat/query interface
 * Shows real-time routing and response handling
 */

import { useState, useRef, useEffect } from 'react';

interface HelperResponse {
  ok: boolean;
  domain: 'math' | 'science' | 'reasoning' | 'language';
  answer: string;
  notes?: string;
  confidence?: 'high' | 'medium' | 'low';
}

interface Message {
  type: 'user' | 'helper' | 'error';
  domain?: string;
  content: string;
  timestamp: Date;
}

export function OceanHelpersUI() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Submit question to helper API
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    // Add user message
    setMessages((prev) => [
      ...prev,
      {
        type: 'user',
        content: question,
        timestamp: new Date(),
      },
    ]);

    setLoading(true);

    try {
      // Call helper endpoint
      const response = await fetch('/api/ocean/helpers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question.trim(),
          debug: false,
          stream: false,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      const result: HelperResponse = data.result;

      // Add helper response
      setMessages((prev) => [
        ...prev,
        {
          type: 'helper',
          domain: result.domain,
          content: result.answer,
          timestamp: new Date(),
        },
      ]);

      // Show notes if available
      if (result.notes) {
        setMessages((prev) => [
          ...prev,
          {
            type: 'helper',
            domain: result.domain,
            content: `📝 ${result.notes}`,
            timestamp: new Date(),
          },
        ]);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: 'error',
          content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
      setQuestion('');
    }
  };

  // Handle streaming response
  const handleStream = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setMessages((prev) => [
      ...prev,
      {
        type: 'user',
        content: question,
        timestamp: new Date(),
      },
    ]);

    setStreaming(true);
    let streamBuffer = '';

    try {
      const response = await fetch('/api/ocean/helpers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question.trim(),
          debug: false,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No stream reader');

      const decoder = new TextDecoder();
      let messageId: string | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        streamBuffer += decoder.decode(value, { stream: true });
        const lines = streamBuffer.split('\n');

        // Process complete lines
        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i];

          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.event === 'result' || data.event === 'stream_notice') {
                if (!messageId) {
                  messageId = Math.random().toString(36);
                  setMessages((prev) => [
                    ...prev,
                    {
                      type: 'helper',
                      domain: data.data?.domain,
                      content: data.data?.answer || data.message,
                      timestamp: new Date(),
                    },
                  ]);
                }
              }
            } catch {
              // Ignore parse errors
            }
          }
        }

        // Keep incomplete line in buffer
        streamBuffer = lines[lines.length - 1];
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: 'error',
          content: `Stream error: ${error instanceof Error ? error.message : 'Unknown error'}`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setStreaming(false);
      setQuestion('');
    }
  };

  // Get domain color/icon
  const getDomainStyle = (domain?: string) => {
    const styles: Record<string, { bg: string; icon: string; color: string }> =
      {
        math: { bg: 'bg-blue-100', icon: '🔢', color: 'text-blue-700' },
        science: { bg: 'bg-green-100', icon: '🧪', color: 'text-green-700' },
        reasoning: { bg: 'bg-purple-100', icon: '🧠', color: 'text-purple-700' },
        language: { bg: 'bg-orange-100', icon: '📚', color: 'text-orange-700' },
      };

    return styles[domain || 'reasoning'] || styles.reasoning;
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <div className="bg-slate-800 border-b border-slate-700 p-4">
        <h1 className="text-2xl font-bold text-cyan-400 flex items-center gap-2">
          <span>🌊</span> Ocean Helpers
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Deterministic routing for math, science, and complex reasoning
        </p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-slate-400 text-lg mb-4">
                Ask a question to get started...
              </p>
              <div className="text-5xl opacity-20">🌊</div>
            </div>
          </div>
        )}

        {messages.map((msg, i) => {
          const domainStyle = getDomainStyle(msg.domain);
          return (
            <div
              key={i}
              className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-2xl p-4 rounded-lg ${
                  msg.type === 'user'
                    ? 'bg-cyan-600 text-white'
                    : msg.type === 'error'
                      ? 'bg-red-900 text-red-100'
                      : `${domainStyle.bg} ${domainStyle.color}`
                }`}
              >
                {msg.type === 'helper' && (
                  <div className="flex gap-2 items-start mb-2">
                    <span className="text-xl">{domainStyle.icon}</span>
                    <span className="font-semibold text-sm capitalize">
                      {msg.domain}
                    </span>
                  </div>
                )}
                <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                <p className="text-xs opacity-60 mt-2">
                  {msg.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-700 text-slate-300 p-4 rounded-lg">
              <p className="flex items-center gap-2">
                <span className="animate-spin">⏳</span> Processing...
              </p>
            </div>
          </div>
        )}

        {streaming && (
          <div className="flex justify-start">
            <div className="bg-slate-700 text-slate-300 p-4 rounded-lg">
              <p className="flex items-center gap-2">
                <span className="animate-pulse">📡</span> Streaming...
              </p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-slate-800 border-t border-slate-700 p-4">
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question... (math, science, reasoning)"
              disabled={loading || streaming}
              className="flex-1 bg-slate-700 text-white placeholder-slate-400 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
            <button
              type="submit"
              disabled={loading || streaming || !question.trim()}
              className="bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-700 text-white px-6 py-2 rounded font-medium transition"
            >
              {loading ? '...' : 'Ask'}
            </button>
            <button
              type="button"
              onClick={handleStream}
              disabled={loading || streaming || !question.trim()}
              className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-700 text-white px-6 py-2 rounded font-medium transition"
            >
              {streaming ? '...' : 'Stream'}
            </button>
          </div>
          <p className="text-xs text-slate-400">
            💡 Examples: &quot;27 + 56?&quot;, &quot;What is DNA?&quot;, &quot;Why is the sky blue?&quot;
          </p>
        </form>
      </div>
    </div>
  );
}
