/**
 * AGICoreComponent - React Component Wrapper for AGI Core
 * Provides UI interface for the AGI Core system
 * 
 * @author UltraWeb Thinking
 * @version 8.0.0-AGI-COMPONENT
 * @license MIT
 */

'use client';

import * as React from "react";
import { useState, useEffect } from "react";
import { AGICore } from './AGICore';

interface AGICoreComponentProps {
  className?: string;
  onProcessing?: (isProcessing: boolean) => void;
  onResponse?: (response: string) => void;
}

export const AGICoreComponent: React.FC<AGICoreComponentProps> = ({
  className = '',
  onProcessing,
  onResponse
}) => {
  const [agiCore, setAgiCore] = useState<AGICore | null>(null);
  const [status, setStatus] = useState<string>('Initializing...');
  const [memory, setMemory] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [isClient, setIsClient] = useState<boolean>(false);
  const [query, setQuery] = useState<string>('');
  const [response, setResponse] = useState<string>('');

  useEffect(() => {
    // Mark as client-side only
    setIsClient(true);
    
    // Initialize AGICore
    const core = new AGICore();
    setAgiCore(core);
    setStatus('AGI Core Active');
    
    // Get initial memory state
    setMemory(core.getMemory());

    // Subscribe to memory changes
    const unsubscribe = core.subscribe(() => {
      setMemory(core.getMemory());
    });

    return () => {
      unsubscribe();
    };
  }, []);

  // Don't render dynamic content until client-side
  if (!isClient) {
    return (
      <div className={`agi-container ${className || ''}`}>
        <div className="loading-state">
          <span className="status-indicator">
            🧠 AGI Core Loading...
          </span>
        </div>
      </div>
    );
  }

  const handleQuery = async (inputQuery: string) => {
    if (!agiCore || !inputQuery.trim()) return;

    setIsProcessing(true);
    onProcessing?.(true);
    setQuery(inputQuery);

    try {
      agiCore.setAGIStatus('PROCESSING');
      const model = process.env.NEXT_PUBLIC_OLLAMA_MODEL;
      const apiResponse = await fetch('/api/ai-manager', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputQuery, model, clientId: 'agi-core-ui' })
      });

      if (!apiResponse.ok) {
        let errorMessage = `AGI upstream error (${apiResponse.status})`;
        try {
          const errorData = await apiResponse.json();
          errorMessage = errorData?.detail?.message || errorData?.detail?.error || errorMessage;
        } catch {
          errorMessage = `AGI upstream error (${apiResponse.status})`;
        }
        throw new Error(errorMessage);
      }

      const responseData = await apiResponse.json();
      const result = String(
        responseData?.result?.response || responseData?.response || responseData?.content || ''
      ).trim();
      if (!result) {
        throw new Error('AGI returned empty response');
      }

      // Update AGI memory with the response
      agiCore.addAGIResponse(inputQuery, result);
      agiCore.setAGIStatus('ACTIVE');

      setResponse(result);
      onResponse?.(result);
    } catch (error) {
      const errorMessage = `AGI Error: ${error instanceof Error ? error.message : 'Unknown processing error'}`;
      setResponse(errorMessage);
      onResponse?.(errorMessage);
      agiCore.setAGIStatus('IDLE');
    } finally {
      setIsProcessing(false);
      onProcessing?.(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const userQuery = formData.get('query') as string;
    if (userQuery) {
      handleQuery(userQuery);
      (e.target as HTMLFormElement).reset();
    }
  };

  return (
    <div className={`agi-container ${className || ''}`} suppressHydrationWarning>
      {/* AGI Status Header */}
      <div className="agi-header">
        <div className="status-section">
          <span className={`status-indicator ${isProcessing ? 'processing' : 'active'}`}>
            {isProcessing ? '🔄' : '🧠'}
          </span>
          <span className="status-text">{status}</span>
        </div>

        {memory && (
          <div className="memory-info">
            <span>Queries: {memory.agi?.queries?.length || 0}</span>
            <span>Responses: {memory.agi?.responses?.length || 0}</span>
          </div>
        )}
      </div>

      {/* Query Input */}
      <form onSubmit={handleFormSubmit} className="query-form">
        <div className="input-group">
          <input
            type="text"
            name="query"
            placeholder="Ask AGI anything..."
            className="query-input"
            disabled={isProcessing}
          />
          <button 
            type="submit"
            className="submit-button"
            disabled={isProcessing}
          >
            {isProcessing ? '🔄' : '🚀'} {isProcessing ? 'Processing...' : 'Ask AGI'}
          </button>
        </div>
      </form>

      {/* Response Display */}
      {response && (
        <div className="response-section">
          <div className="response-header">
            <span>🤖 AGI Response:</span>
            {query && <span className="query-echo">Re: "{query}"</span>}
          </div>
          <div className="response-content">
            {response}
          </div>
        </div>
      )}

      {/* Memory Debug (optional) */}
      {process.env.NODE_ENV === 'development' && memory && (
        <details className="memory-debug">
          <summary>🧠 Memory State (Debug)</summary>
          <pre>{JSON.stringify(memory, null, 2)}</pre>
        </details>
      )}

      <style jsx>{`
        .agi-container {
          max-width: 800px;
          margin: 0 auto;
          padding: 2rem;
          background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
          border-radius: 15px;
          border: 1px solid #00ffff33;
          box-shadow: 0 0 30px rgba(0, 255, 255, 0.1);
          color: #e2e8f0;
          font-family: 'JetBrains Mono', monospace;
        }

        .loading-state {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 200px;
        }

        .agi-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
          padding: 1rem;
          background: rgba(0, 255, 255, 0.05);
          border-radius: 10px;
          border: 1px solid #00ffff22;
        }

        .status-section {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .status-indicator {
          font-size: 1.5rem;
          display: inline-block;
        }

        .status-indicator.processing {
          animation: spin 1s linear infinite;
        }

        .status-text {
          color: #00ffff;
          font-weight: 600;
        }

        .memory-info {
          display: flex;
          gap: 1rem;
          font-size: 0.9rem;
          color: #a0aec0;
        }

        .query-form {
          margin-bottom: 2rem;
        }

        .input-group {
          display: flex;
          gap: 1rem;
        }

        .query-input {
          flex: 1;
          padding: 1rem 1.5rem;
          background: rgba(0, 0, 0, 0.5);
          border: 1px solid #00ffff44;
          border-radius: 25px;
          color: #ffffff;
          font-size: 1rem;
          font-family: inherit;
        }

        .query-input:focus {
          outline: none;
          border-color: #00ffff;
          box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
        }

        .query-input::placeholder {
          color: #888;
        }

        .submit-button {
          padding: 1rem 2rem;
          background: linear-gradient(135deg, #00ffff, #0099cc);
          border: none;
          border-radius: 25px;
          color: #000;
          font-weight: bold;
          cursor: pointer;
          transition: all 0.3s ease;
          font-family: inherit;
        }

        .submit-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 5px 15px rgba(0, 255, 255, 0.4);
        }

        .submit-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          transform: none;
        }

        .response-section {
          background: rgba(0, 255, 255, 0.05);
          border: 1px solid #00ffff22;
          border-radius: 15px;
          padding: 1.5rem;
          margin-bottom: 2rem;
        }

        .response-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          font-weight: 600;
          color: #00ffff;
        }

        .query-echo {
          font-size: 0.9rem;
          color: #a0aec0;
          font-style: italic;
        }

        .response-content {
          line-height: 1.6;
          white-space: pre-wrap;
          word-wrap: break-word;
        }

        .memory-debug {
          margin-top: 2rem;
          padding: 1rem;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 10px;
          border: 1px solid #333;
        }

        .memory-debug summary {
          cursor: pointer;
          color: #00ffff;
          font-weight: 600;
        }

        .memory-debug pre {
          margin-top: 1rem;
          font-size: 0.8rem;
          overflow-x: auto;
          color: #a0aec0;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .agi-container {
            margin: 1rem;
            padding: 1rem;
          }

          .agi-header {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
          }

          .input-group {
            flex-direction: column;
          }

          .response-header {
            flex-direction: column;
            gap: 0.5rem;
            align-items: flex-start;
          }
        }
      `}</style>
    </div>
  );
};

export default AGICoreComponent;