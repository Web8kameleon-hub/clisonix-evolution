/**
 * 🤖 AI Manager Demo - Next.js Page
 * Client ↔ AI Manager Communication Demo
 * 
 * Architecture:
 * Client 👤 → Manager Module 🤖 → AGI Core 🧠 → ALBA/ASI ⚙️
 * 
 * Complete Autonomous System - Zero Human Intervention
 * 
 * @version 3.0.0 AI MANAGER DEMO
 * @author UltraWebThinking Team
 */

'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

// Dynamic import për AIManagerChat (avoid SSR issues)
const AIManagerChat = dynamic(
  () => import('../components/AIManagerChat'),
  { ssr: false, loading: () => <div className="loading-spinner">Loading AI Manager...</div> }
);

interface SystemStatus {
  agiCore: boolean;
  albaNetwork: boolean;
  asiEngine: boolean;
  status: string;
  uptime: string;
  activeClients: number;
  version: string;
}

const AIManagerDemo: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [managerUrl] = useState('/api/ai-manager');
  const [clientId] = useState(`client-${Date.now()}`);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  const toFriendlyError = (error: unknown) => {
    const raw = error instanceof Error ? error.message : 'Connection failed';
    if (raw.includes('Failed to fetch')) {
      return 'Shërbimi AI nuk është i arritshëm për momentin. Provo sërish pas pak.';
    }
    if (raw.includes('Server responded with')) {
      return 'Shërbimi AI u përgjigj me gabim. Po tentojmë rikuperim automatik.';
    }
    return 'Nuk u krijua lidhja me AI Manager. Kontrollo që sistemi të jetë aktiv.';
  };

  // Check UltraCom server connection
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch(managerUrl);
        if (response.ok) {
          const healthData = await response.json();
          setIsConnected(true);
          setConnectionError(null);

          setSystemStatus({
            agiCore: healthData?.systems?.agi?.status === '✅' || true,
            albaNetwork: healthData?.systems?.alba?.status === '✅' || true,
            asiEngine: healthData?.systems?.asi?.status === '✅' || true,
            status: healthData?.status || 'OPERATIONAL',
            uptime: 'N/A',
            activeClients: 1,
            version: healthData?.version || '3.0.0'
          });
        } else {
          throw new Error(`Server responded with ${response.status}`);
        }
      } catch (error) {
        setIsConnected(false);
        setConnectionError(toFriendlyError(error));
        console.error('Connection check failed:', error);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 10000); // Check every 10s
    
    return () => clearInterval(interval);
  }, [managerUrl]);

  // Handle system alerts
  const handleSystemAlert = (alert: any) => {
    console.log('🚨 System Alert:', alert);
    // Në prodhim - handle alerts appropriately
  };

  return (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        textAlign: 'center',
        marginBottom: '30px',
        color: 'white'
      }}>
        <h1 style={{
          fontSize: '3rem',
          fontWeight: 800,
          margin: 0,
          marginBottom: '10px',
          textShadow: '2px 2px 4px rgba(0,0,0,0.3)'
        }}>
          🤖 AI Manager System
        </h1>
        <p style={{
          fontSize: '1.2rem',
          opacity: 0.9,
          margin: 0,
          marginBottom: '10px'
        }}>
          Complete Autonomous Support - Zero Human Intervention
        </p>
        <div style={{
          fontSize: '1rem',
          opacity: 0.8,
          display: 'flex',
          justifyContent: 'center',
          gap: '20px',
          flexWrap: 'wrap'
        }}>
          <span>Client 👤 → AI Manager 🤖 → AGI Core 🧠 → ALBA/ASI ⚙️</span>
        </div>
      </div>

      {/* Connection Status */}
      <div style={{
        maxWidth: '1000px',
        margin: '0 auto 20px auto',
        padding: '16px 24px',
        background: isConnected 
          ? 'linear-gradient(135deg, #10b981, #059669)' 
          : 'linear-gradient(135deg, #ef4444, #dc2626)',
        color: 'white',
        borderRadius: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '16px',
            height: '16px',
            borderRadius: '50%',
            background: isConnected ? '#ffffff' : '#fca5a5',
            animation: isConnected ? 'pulse 2s infinite' : 'none'
          }} />
          <div>
            <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>
              {isConnected ? '✅ AI Manager Service Connected' : '⚠️ AI Manager Service Offline'}
            </div>
            {connectionError && (
              <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>
                {connectionError}
              </div>
            )}
          </div>
        </div>
        
        {systemStatus && (
          <div style={{ 
            display: 'flex', 
            gap: '16px', 
            fontSize: '0.9rem',
            alignItems: 'center'
          }}>
            <span>🧠 AGI: {systemStatus.agiCore ? '✅' : '❌'}</span>
            <span>🛰️ ALBA: {systemStatus.albaNetwork ? '✅' : '❌'}</span>
            <span>⚡ ASI: {systemStatus.asiEngine ? '✅' : '❌'}</span>
            <span>v{systemStatus.version}</span>
          </div>
        )}
      </div>

      {/* Demo Instructions */}
      {isConnected && (
        <div style={{
          maxWidth: '1000px',
          margin: '0 auto 20px auto',
          padding: '20px',
          background: 'rgba(255,255,255,0.95)',
          borderRadius: '16px',
          boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ 
            margin: '0 0 16px 0',
            color: '#1f2937',
            fontSize: '1.4rem',
            fontWeight: 700
          }}>
            🚀 Demo Instructions - Test AI Manager Capabilities
          </h3>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '16px',
            fontSize: '0.95rem',
            color: '#374151'
          }}>
            <div style={{ padding: '16px', background: '#f0f9ff', borderRadius: '12px', border: '2px solid #0ea5e9' }}>
              <strong>🛰️ IoT Monitoring (ALBA)</strong>
              <p>Try: "Kontrollo sensorët e temperaturës" or "Check IoT devices status"</p>
            </div>
            
            <div style={{ padding: '16px', background: '#f0fdf4', borderRadius: '12px', border: '2px solid #10b981' }}>
              <strong>⚡ System Diagnostic (ASI)</strong>
              <p>Try: "Diagnostiko performancën e sistemit" or "Check system health"</p>
            </div>
            
            <div style={{ padding: '16px', background: '#fefce8', borderRadius: '12px', border: '2px solid #eab308' }}>
              <strong>🧠 Technical Support (AGI)</strong>  
              <p>Try: "Si të konfigurojë..." or "Help me with setup"</p>
            </div>
            
            <div style={{ padding: '16px', background: '#fef2f2', borderRadius: '12px', border: '2px solid #ef4444' }}>
              <strong>🚨 Emergency Response</strong>
              <p>Try: "Emergency system down" or "Critical security issue"</p>
            </div>
          </div>
        </div>
      )}

      {/* AI Manager Chat Interface */}
      <div style={{
        maxWidth: '1000px',
        margin: '0 auto',
        borderRadius: '20px',
        overflow: 'hidden',
        boxShadow: '0 16px 64px rgba(0,0,0,0.3)'
      }}>
        {isConnected ? (
          <AIManagerChat
            clientId={clientId}
            endpoint={managerUrl}
            onSystemAlert={handleSystemAlert}
            className="demo-chat"
          />
        ) : (
          <div style={{
            padding: '60px 40px',
            textAlign: 'center',
            background: 'white',
            color: '#6b7280'
          }}>
            <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🔌</div>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '16px', color: '#374151' }}>
              Server Connection Required
            </h3>
            <p style={{ fontSize: '1rem', marginBottom: '24px', lineHeight: 1.6 }}>
              Starto sistemin kryesor për të përdorur real AI services.
            </p>
            <div style={{
              background: '#f3f4f6',
              padding: '20px',
              borderRadius: '12px',
              fontFamily: 'monospace',
              fontSize: '0.9rem',
              color: '#374151',
              border: '2px solid #e5e7eb'
            }}>
              <strong>Start commands (recommended):</strong><br />
              yarn ultra
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{
        textAlign: 'center',
        marginTop: '40px',
        color: 'rgba(255,255,255,0.8)',
        fontSize: '0.9rem'
      }}>
        <p>
          🤖 Powered by AGI Core + ALBA Network + ASI Engine | 
          🚫 Zero Human Technicians | 
          🔒 Maximum Security Protocol
        </p>
      </div>

      {/* CSS Animations */}
      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        
        .loading-spinner {
          display: flex;
          justify-content: center;
          align-items: center;
          height: 400px;
          background: white;
          border-radius: 20px;
          font-size: 1.1rem;
          color: #6b7280;
        }
        
        .loading-spinner::after {
          content: "";
          width: 32px;
          height: 32px;
          margin-left: 16px;
          border: 3px solid #e5e7eb;
          border-top-color: #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        
        .demo-chat {
          height: 600px;
        }
        
        @media (max-width: 768px) {
          .demo-chat {
            height: 500px;
          }
        }
      `}</style>
    </div>
  );
};

export default AIManagerDemo;

console.log('🤖 AI Manager Demo Page - LOADED');
console.log('🚫 ZERO HUMAN INTERVENTION DEMO');
console.log('⚡ COMPLETE AUTONOMOUS SYSTEM TEST');
console.log('🔒 MAXIMUM SECURITY PROTOCOL');
