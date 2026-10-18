/**
 * 🚀 UltraCom Integration Demo Page
 * Complete example of Client ↔ Technician communication system
 * 
 * Architecture:
 * - FastAPI WebSocket backend (Python) 
 * - JWT authentication with role-based access
 * - Real-time messaging with animated UI
 * - Production-grade error handling & reconnection
 * 
 * @version 1.0.0 ULTRACOM DEMO
 * @author UltraWebThinking Team
 */

import { UltraComChat } from '../components/UltraComChat';
import { UltraComAuth } from '../lib/ultracom-client';
import { useState, useEffect } from 'react';

export default function UltraComDemo() {
  const [tokens, setTokens] = useState({
    client: '',
    technician: '',
    admin: ''
  });
  const [currentUser, setCurrentUser] = useState({
    role: 'client' as 'client' | 'technician' | 'admin',
    name: 'client-007',
    token: ''
  });
  const [room] = useState('support-ACME-42');
  const [backendUrl] = useState(
    typeof window !== 'undefined'
      ? '/backend'
      : 'http://127.0.0.1:8080'
  );

  // Generate demo tokens
  useEffect(() => {
    const generateTokens = async () => {
      const clientToken = await UltraComAuth.createToken('secret', 'client-007', 'client');
      const techToken = await UltraComAuth.createToken('secret', 'tech-ops-1', 'technician'); 
      const adminToken = await UltraComAuth.createToken('secret', 'admin-ultra', 'admin');
      
      setTokens({
        client: clientToken,
        technician: techToken,
        admin: adminToken
      });
      
      setCurrentUser({
        role: 'client',
        name: 'client-007',
        token: clientToken
      });
    };

    generateTokens();
  }, []);

  const switchUser = (role: 'client' | 'technician' | 'admin') => {
    const names = {
      client: 'client-007',
      technician: 'tech-ops-1', 
      admin: 'admin-ultra'
    };
    
    setCurrentUser({
      role,
      name: names[role],
      token: tokens[role]
    });
  };

  if (!currentUser.token) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '1.2rem'
      }}>
        🔄 Po inicializohet UltraCom...
      </div>
    );
  }

  return (
    <div style={{
      padding: '20px',
      maxWidth: '1200px',
      margin: '0 auto',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea, #764ba2)',
        color: 'white',
        padding: '24px',
        borderRadius: '16px',
        marginBottom: '24px',
        textAlign: 'center'
      }}>
        <h1 style={{ margin: 0, fontSize: '2rem', fontWeight: 700 }}>
          🚀 UltraCom System Demo
        </h1>
        <p style={{ margin: '8px 0 0', fontSize: '1.1rem', opacity: 0.9 }}>
          Client ↔ Technician Real-time Communication
        </p>
      </div>

      {/* Controls */}
      <div style={{
        background: '#f8fafc',
        padding: '20px',
        borderRadius: '12px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        flexWrap: 'wrap'
      }}>
        <span style={{ fontWeight: 600, color: '#374151' }}>Zgjidh rolin:</span>
        
        {(['client', 'technician', 'admin'] as const).map(role => (
          <button
            key={role}
            onClick={() => switchUser(role)}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: '2px solid transparent',
              background: currentUser.role === role 
                ? (role === 'client' ? '#3b82f6' : role === 'technician' ? '#10b981' : '#ef4444')
                : '#ffffff',
              color: currentUser.role === role ? '#ffffff' : '#6b7280',
              cursor: 'pointer',
              fontWeight: 600,
              transition: 'all 0.2s',
              textTransform: 'capitalize'
            }}
          >
            {role === 'client' ? '👤' : role === 'technician' ? '🔧' : '👑'} {role}
          </button>
        ))}

        <div style={{
          marginLeft: 'auto',
          padding: '8px 12px',
          background: '#ffffff',
          borderRadius: '8px',
          border: '1px solid #d1d5db',
          fontSize: '0.9rem',
          color: '#6b7280'
        }}>
          Room: <strong>{room}</strong>
        </div>
      </div>

      {/* Chat Interface */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr',
        gap: '24px'
      }}>
        <div style={{
          background: '#ffffff',
          borderRadius: '16px',
          border: '1px solid #e5e7eb',
          overflow: 'hidden',
          boxShadow: '0 4px 24px rgba(0,0,0,0.1)'
        }}>
          <UltraComChat
            key={`${currentUser.role}-${currentUser.name}`} // Re-mount on user change
            baseUrl={backendUrl}
            token={currentUser.token}
            room={room}
            userRole={currentUser.role}
            userName={currentUser.name}
          />
        </div>
      </div>

      {/* Information */}
      <div style={{
        marginTop: '32px',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '20px'
      }}>
        {/* Architecture Info */}
        <div style={{
          background: '#f0f9ff',
          border: '2px solid #0ea5e9',
          borderRadius: '12px',
          padding: '20px'
        }}>
          <h3 style={{ 
            margin: '0 0 12px', 
            color: '#0369a1',
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px' 
          }}>
            🏗️ Architecture
          </h3>
          <ul style={{ margin: 0, padding: '0 0 0 20px', color: '#0c4a6e' }}>
            <li><strong>Backend:</strong> FastAPI + WebSocket</li>
            <li><strong>Auth:</strong> JWT with role-based access</li>
            <li><strong>Database:</strong> SQLAlchemy + SQLite/PostgreSQL</li>
            <li><strong>Frontend:</strong> React + Web8 Motion</li>
            <li><strong>Real-time:</strong> WebSocket with REST fallback</li>
          </ul>
        </div>

        {/* Features Info */}
        <div style={{
          background: '#f0fdf4',
          border: '2px solid #22c55e',
          borderRadius: '12px',
          padding: '20px'
        }}>
          <h3 style={{ 
            margin: '0 0 12px', 
            color: '#15803d',
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px' 
          }}>
            ✨ Features
          </h3>
          <ul style={{ margin: 0, padding: '0 0 0 20px', color: '#14532d' }}>
            <li>Role-based messaging (Client/Tech/Admin)</li>
            <li>Real-time typing indicators</li>
            <li>Auto-reconnection with exponential backoff</li>
            <li>Message history with pagination</li>
            <li>Animated UI with Web8 Motion</li>
          </ul>
        </div>

        {/* Backend Setup */}
        <div style={{
          background: '#fef3c7',
          border: '2px solid #f59e0b',
          borderRadius: '12px',
          padding: '20px'
        }}>
          <h3 style={{ 
            margin: '0 0 12px', 
            color: '#92400e',
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px' 
          }}>
            🚀 Backend Setup
          </h3>
          <div style={{ fontSize: '0.9rem', color: '#78350f' }}>
            <p style={{ margin: '0 0 8px' }}><strong>1. Clone UltraCom backend:</strong></p>
            <code style={{ 
              background: '#fbbf24', 
              padding: '4px 8px', 
              borderRadius: '4px',
              display: 'block',
              marginBottom: '8px'
            }}>
              git clone ultracom && cd ultracom
            </code>
            <p style={{ margin: '0 0 8px' }}><strong>2. Install & run:</strong></p>
            <code style={{ 
              background: '#fbbf24', 
              padding: '4px 8px', 
              borderRadius: '4px',
              display: 'block'
            }}>
              pip install -r requirements.txt<br />
              uvicorn app.main:app --port 8080
            </code>
          </div>
        </div>

        {/* Production Deployment */}
        <div style={{
          background: '#fef2f2',
          border: '2px solid #ef4444',
          borderRadius: '12px',
          padding: '20px'
        }}>
          <h3 style={{ 
            margin: '0 0 12px', 
            color: '#dc2626',
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px' 
          }}>
            🔥 Production
          </h3>
          <div style={{ fontSize: '0.9rem', color: '#7f1d1d' }}>
            <p style={{ margin: '0 0 8px' }}><strong>Docker Compose:</strong></p>
            <code style={{ 
              background: '#f87171', 
              padding: '4px 8px', 
              borderRadius: '4px',
              display: 'block',
              marginBottom: '8px'
            }}>
              docker compose up --build -d
            </code>
            <p style={{ margin: '0 0 4px' }}>Includes: PostgreSQL, Redis, MinIO, Nginx, OTEL</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div style={{
        marginTop: '40px',
        textAlign: 'center',
        padding: '20px',
        color: '#6b7280',
        fontSize: '0.9rem'
      }}>
        <p style={{ margin: 0 }}>
          🚀 <strong>UltraCom System</strong> - Industrial-grade communication platform<br />
          Built with FastAPI + React + Web8 Motion • Production Ready
        </p>
      </div>
    </div>
  );
}

console.log('🎯 UltraComDemo Page - LOADED');
console.log('👥 Multi-role Chat: CLIENT/TECHNICIAN/ADMIN');
console.log('⚡ Real-time WebSocket: ACTIVE');
console.log('🎨 Animated UI: WEB8 MOTION POWERED');
