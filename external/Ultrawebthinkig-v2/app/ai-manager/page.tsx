'use client'

import React from 'react'
import AIManagerChat from '../../components/AIManagerChat'

/**
 * 🤖 AI Manager Dashboard Page
 * Advanced Neural Network Communication Interface
 */

export default function AIManagerPage() {
  const handleSystemAlert = (alert: any) => {
    console.log('System Alert:', alert)
    // Handle emergency alerts here
    if (alert.category === 'emergency') {
      // Could trigger notifications, logging, etc.
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
      padding: '20px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {/* Page Header */}
        <div style={{
          marginBottom: '30px',
          textAlign: 'center',
          color: 'white'
        }}>
          <h1 style={{
            fontSize: '2.5rem',
            fontWeight: 700,
            margin: 0,
            marginBottom: '10px',
            background: 'linear-gradient(45deg, #3b82f6, #8b5cf6, #06b6d4)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            🤖 AI Manager Dashboard
          </h1>
          <p style={{
            fontSize: '1.1rem',
            opacity: 0.8,
            margin: 0
          }}>
            Advanced Neural Network Communication • AGI + ALBA + ASI Integration
          </p>
        </div>

        {/* System Status Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px',
          marginBottom: '30px'
        }}>
          <div style={{
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1))',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: '16px',
            padding: '20px',
            color: 'white'
          }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>🧠</div>
            <h3 style={{ margin: 0, marginBottom: '4px', color: '#10b981' }}>AGI Neural Core</h3>
            <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>
              Consciousness Level: 85.7%<br/>
              Neural Networks: Active
            </p>
          </div>

          <div style={{
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(29, 78, 216, 0.1))',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            borderRadius: '16px',
            padding: '20px',
            color: 'white'
          }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>🛰️</div>
            <h3 style={{ margin: 0, marginBottom: '4px', color: '#3b82f6' }}>ALBA IoT Network</h3>
            <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>
              Active Nodes: 8,293<br/>
              Signal Strength: 95.9%
            </p>
          </div>

          <div style={{
            background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(124, 58, 237, 0.1))',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            borderRadius: '16px',
            padding: '20px',
            color: 'white'
          }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>⚡</div>
            <h3 style={{ margin: 0, marginBottom: '4px', color: '#8b5cf6' }}>ASI Quantum Engine</h3>
            <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>
              Processing Units: 19,427<br/>
              Efficiency: 95.1%
            </p>
          </div>

          <div style={{
            background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.1))',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '16px',
            padding: '20px',
            color: 'white'
          }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>🔬</div>
            <h3 style={{ margin: 0, marginBottom: '4px', color: '#f59e0b' }}>System Analytics</h3>
            <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>
              Neural Pathways: 2.48M<br/>
              Quantum Coherence: Active
            </p>
          </div>
        </div>

        {/* AI Manager Chat Interface */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '20px',
          padding: '20px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)'
        }}>
          <AIManagerChat
            clientId="dashboard-user-001"
            endpoint="/api/ai-manager"
            onSystemAlert={handleSystemAlert}
          />
        </div>

        {/* Quick Actions */}
        <div style={{
          marginTop: '30px',
          display: 'flex',
          gap: '15px',
          flexWrap: 'wrap',
          justifyContent: 'center'
        }}>
          <button
            onClick={() => window.open('/api/agi-advanced', '_blank')}
            style={{
              background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              padding: '12px 24px',
              fontSize: '0.9rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 8px 25px rgba(59, 130, 246, 0.4)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            🧠 AGI Advanced API
          </button>

          <button
            onClick={() => window.open('/advanced-chat-standalone.html', '_blank')}
            style={{
              background: 'linear-gradient(135deg, #10b981, #059669)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              padding: '12px 24px',
              fontSize: '0.9rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 8px 25px rgba(16, 185, 129, 0.4)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            💬 Standalone Chat
          </button>

          <button
            onClick={() => window.open('/api/ai-manager', '_blank')}
            style={{
              background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              padding: '12px 24px',
              fontSize: '0.9rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 8px 25px rgba(139, 92, 246, 0.4)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            🤖 Manager API
          </button>
        </div>
      </div>
    </div>
  )
}
