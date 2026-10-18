/**
 * FLUID FLOW DEMO PAGE
 * Natural water-like flow demonstration
 * 
 * @version 8.0.0-FLUID
 */

'use client';

import React from 'react';
import { FluidMonitor } from '@/components/FluidMonitor';

export default function FluidFlowDemo() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 50%, #90caf9 100%)',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '20px'
      }}>
        <header style={{
          textAlign: 'center',
          marginBottom: '40px',
          background: 'rgba(255, 255, 255, 0.9)',
          padding: '30px',
          borderRadius: '20px',
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)'
        }}>
          <h1 style={{
            fontSize: '3.5rem',
            margin: '0 0 20px 0',
            background: 'linear-gradient(45deg, #1565c0, #42a5f5)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: '700'
          }}>
            🌊 FLUID ARCHITECTURE SYSTEM
          </h1>
          <p style={{
            fontSize: '1.4rem',
            color: '#424242',
            margin: '0',
            fontWeight: '500'
          }}>
            Rrjedhje e natyrshme si ujë i kulluar në çdo aspekt të projektit
          </p>
          <div style={{
            marginTop: '20px',
            display: 'flex',
            justifyContent: 'center',
            gap: '20px',
            flexWrap: 'wrap'
          }}>
            <span style={{
              background: 'linear-gradient(45deg, #e3f2fd, #bbdefb)',
              padding: '8px 16px',
              borderRadius: '20px',
              color: '#1565c0',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              💧 Crystal Clear Flow
            </span>
            <span style={{
              background: 'linear-gradient(45deg, #e8f5e8, #c8e6c8)',
              padding: '8px 16px',
              borderRadius: '20px',
              color: '#2e7d32',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              ⚡ Natural Velocity
            </span>
            <span style={{
              background: 'linear-gradient(45deg, #fff3e0, #ffe0b2)',
              padding: '8px 16px',
              borderRadius: '20px',
              color: '#f57c00',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              🛡️ Zero Turbulence
            </span>
          </div>
        </header>

        <FluidMonitor />

        <footer style={{
          textAlign: 'center',
          marginTop: '40px',
          background: 'rgba(255, 255, 255, 0.8)',
          padding: '25px',
          borderRadius: '15px',
          color: '#666'
        }}>
          <p style={{ margin: '0', fontSize: '1.1rem' }}>
            🌊 <strong>Fluid Architecture</strong> - Ku çdo komponent rrjedh natyrshëm si ujë i pastër
          </p>
          <p style={{ margin: '10px 0 0 0', fontSize: '0.9rem', color: '#888' }}>
            Real-time monitoring • Automatic optimization • Crystal clear performance
          </p>
        </footer>
      </div>
    </div>
  );
}
