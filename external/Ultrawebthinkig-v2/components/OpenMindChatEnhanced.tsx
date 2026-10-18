/**
 * OpenMindChat Enhanced - Web8 State Integration
 * Industrial Grade AI Chat with integrated state management
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @version 8.0.0 Ultra + Web8 Integration
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import { useWeb8AI, useWeb8Security } from '@/hooks/useWeb8State';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: number;
  provider?: string;
}

export default function OpenMindChatEnhanced() {
  const [inputMessage, setInputMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Web8 State Hooks
  const {
    messages,
    isLoading,
    error,
    provider,
    addMessage,
    setLoading,
    setError,
    setProvider,
    clearMessages
  } = useWeb8AI();

  const {
    isActive: securityActive,
    threatLevel,
    blockedRequests,
    updateThreatLevel,
    reportBlockedRequest
  } = useWeb8Security();

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Real API call function
  const callRealAPI = async (message: string): Promise<string> => {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          provider: provider || 'openai'
        }),
      });

      if (!response.ok) {
        if (response.status === 403) {
          reportBlockedRequest('AI API request blocked');
          updateThreatLevel('high');
          throw new Error('Request blocked by security system');
        }
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      
      // Update provider based on response
      if (data.provider) {
        setProvider(data.provider);
      }
      
      return data.response || data.message || 'No response received';
    } catch (error) {
      console.error('API call failed:', error);
      setError(error instanceof Error ? error.message : 'Unknown error');
      throw error;
    }
  };

  // Handle message submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setError(null);
    
    // Add user message to state
    addMessage(userMessage, 'user');
    setLoading(true);
    setIsProcessing(true);

    try {
      // Call real API
      const response = await callRealAPI(userMessage);
      
      // Add AI response to state
      addMessage(response, 'assistant');
      
      // Update security level based on interaction
      updateThreatLevel('low');
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get response';
      addMessage(`Error: ${errorMessage}`, 'assistant');
      updateThreatLevel('medium');
    } finally {
      setLoading(false);
      setIsProcessing(false);
    }
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <div className="header-title">
          <h1>🧠 OpenMind Chat Enhanced</h1>
          <span className="subtitle">Web8 State Management + Guardian Security</span>
        </div>
        
        <div className="status-indicators">
          <div className={`indicator ${securityActive ? 'active' : 'inactive'}`}>
            🛡️ Guardian: {securityActive ? 'Active' : 'Inactive'}
          </div>
          <div className={`indicator threat-${threatLevel}`}>
            🚨 Threat: {threatLevel}
          </div>
          <div className={`indicator provider-${provider}`}>
            🤖 Provider: {provider || 'openai'}
          </div>
          {blockedRequests > 0 && (
            <div className="indicator blocked">
              ⛔ Blocked: {blockedRequests}
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h3>Welcome to OpenMind Chat Enhanced!</h3>
            <p>This chat uses Web8 state management with real-time security monitoring.</p>
            <div className="features">
              <span>✅ Real OpenAI API Integration</span>
              <span>✅ Guardian Security System</span>
              <span>✅ Web8 State Management</span>
              <span>✅ Multi-Provider Fallback</span>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.role}`}
            >
              <div className="message-header">
                <span className="role">
                  {message.role === 'user' ? '👤 You' : '🤖 AI'}
                </span>
                <span className="timestamp">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="message-content">
                {message.content}
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="message assistant">
            <div className="message-header">
              <span className="role">🤖 AI</span>
              <span className="timestamp">Processing...</span>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span>●</span>
                <span>●</span>
                <span>●</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="input-form">
        <div className="input-container">
          <input
            type="text"
            value={inputMessage}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInputMessage(e.target.value)}
            placeholder="Type your message here..."
            disabled={isLoading}
            className="message-input"
          />
          <button
            type="submit"
            disabled={isLoading || !inputMessage.trim()}
            className="send-button"
          >
            {isLoading ? '⏳' : '🚀'}
          </button>
        </div>
        
        <div className="actions">
          <button
            type="button"
            onClick={clearMessages}
            className="clear-button"
            disabled={isLoading}
          >
            🗑️ Clear Chat
          </button>
          <div className="message-count">
            Messages: {messages.length}
          </div>
        </div>
      </form>

      <style jsx>{`
        .chat-container {
          display: flex;
          flex-direction: column;
          height: 100vh;
          max-width: 1200px;
          margin: 0 auto;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .chat-header {
          padding: 20px;
          background: rgba(0, 0, 0, 0.2);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .header-title h1 {
          margin: 0;
          font-size: 2rem;
          font-weight: bold;
        }

        .subtitle {
          color: rgba(255, 255, 255, 0.8);
          font-size: 0.9rem;
        }

        .status-indicators {
          display: flex;
          gap: 15px;
          margin-top: 10px;
          flex-wrap: wrap;
        }

        .indicator {
          padding: 5px 10px;
          border-radius: 15px;
          font-size: 0.8rem;
          font-weight: bold;
        }

        .indicator.active {
          background: rgba(0, 255, 0, 0.2);
          border: 1px solid rgba(0, 255, 0, 0.5);
        }

        .indicator.inactive {
          background: rgba(255, 0, 0, 0.2);
          border: 1px solid rgba(255, 0, 0, 0.5);
        }

        .indicator.threat-low {
          background: rgba(0, 255, 0, 0.2);
        }

        .indicator.threat-medium {
          background: rgba(255, 255, 0, 0.2);
        }

        .indicator.threat-high {
          background: rgba(255, 0, 0, 0.2);
        }

        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .welcome-message {
          text-align: center;
          padding: 40px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 15px;
          backdrop-filter: blur(5px);
        }

        .features {
          display: flex;
          flex-direction: column;
          gap: 10px;
          margin-top: 20px;
        }

        .features span {
          background: rgba(255, 255, 255, 0.1);
          padding: 8px 15px;
          border-radius: 20px;
          font-size: 0.9rem;
        }

        .message {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 15px;
          padding: 15px;
          backdrop-filter: blur(5px);
          border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .message.user {
          align-self: flex-end;
          background: rgba(100, 200, 255, 0.2);
          border-color: rgba(100, 200, 255, 0.3);
          max-width: 80%;
        }

        .message.assistant {
          align-self: flex-start;
          background: rgba(255, 255, 255, 0.1);
          max-width: 90%;
        }

        .message-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          font-size: 0.8rem;
        }

        .role {
          font-weight: bold;
        }

        .timestamp {
          opacity: 0.7;
        }

        .message-content {
          line-height: 1.6;
          white-space: pre-wrap;
        }

        .typing-indicator {
          display: flex;
          gap: 4px;
        }

        .typing-indicator span {
          animation: typing 1.4s infinite;
          font-size: 1.2em;
        }

        .typing-indicator span:nth-child(2) {
          animation-delay: 0.2s;
        }

        .typing-indicator span:nth-child(3) {
          animation-delay: 0.4s;
        }

        @keyframes typing {
          0%, 60%, 100% { opacity: 0.3; }
          30% { opacity: 1; }
        }

        .error-banner {
          background: rgba(255, 0, 0, 0.2);
          border: 1px solid rgba(255, 0, 0, 0.5);
          padding: 10px 20px;
          margin: 0 20px;
          border-radius: 8px;
          font-weight: bold;
        }

        .input-form {
          padding: 20px;
          background: rgba(0, 0, 0, 0.2);
          backdrop-filter: blur(10px);
          border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .input-container {
          display: flex;
          gap: 10px;
          margin-bottom: 10px;
        }

        .message-input {
          flex: 1;
          padding: 15px;
          border: none;
          border-radius: 25px;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          font-size: 1rem;
          backdrop-filter: blur(5px);
        }

        .message-input::placeholder {
          color: rgba(255, 255, 255, 0.6);
        }

        .message-input:focus {
          outline: none;
          background: rgba(255, 255, 255, 0.2);
        }

        .send-button {
          padding: 15px 20px;
          border: none;
          border-radius: 25px;
          background: rgba(100, 200, 255, 0.3);
          color: white;
          font-size: 1.2rem;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .send-button:hover:not(:disabled) {
          background: rgba(100, 200, 255, 0.5);
          transform: translateY(-2px);
        }

        .send-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 0.9rem;
        }

        .clear-button {
          padding: 8px 15px;
          border: none;
          border-radius: 15px;
          background: rgba(255, 100, 100, 0.2);
          color: white;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .clear-button:hover:not(:disabled) {
          background: rgba(255, 100, 100, 0.4);
        }

        .message-count {
          opacity: 0.7;
        }
      `}</style>
    </div>
  );
}
