/**
 * Light Speed I/O Page - Faster than Light Data Transfer
 * Coming Soon - Requires Monthly Subscription
 */

'use client';

import Link from 'next/link';
import { ArrowLeft, Zap, Sparkles } from 'lucide-react';

export default function LightSpeedIOPage() {
  return (
    <div style={{
      minHeight: '100vh',
      background: `
        radial-gradient(circle at 20% 50%, #ffffff22 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, #0080ff22 0%, transparent 50%),
        radial-gradient(circle at 40% 80%, #ff008022 0%, transparent 50%),
        linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)
      `,
      color: 'white',
      padding: '2rem',
      fontFamily: '"SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      textAlign: 'center'
    }}>
      
      <Link href="/ultra-speed" style={{ 
        position: 'absolute',
        top: '2rem',
        left: '2rem',
        display: 'flex', 
        alignItems: 'center', 
        gap: '0.5rem',
        color: '#ffffff',
        textDecoration: 'none',
        fontSize: '1rem'
      }}>
        <ArrowLeft size={20} />
        Back to Ultra Speed
      </Link>

      <div style={{ marginBottom: '3rem' }}>
        <div style={{ fontSize: '8rem', marginBottom: '1rem' }}>💫</div>
        
        <h1 style={{
          fontSize: '4rem',
          fontWeight: 900,
          margin: '0 0 1rem 0',
          background: 'linear-gradient(45deg, #ffffff, #0080ff)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          Light Speed I/O
        </h1>
        
        <p style={{ 
          fontSize: '1.5rem', 
          color: '#aaaaaa', 
          margin: '0 0 3rem 0',
          maxWidth: '600px'
        }}>
          Faster than Light Data Transfer • Coming Soon
        </p>

        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          border: '2px solid #ffffff',
          borderRadius: '20px',
          padding: '2rem',
          maxWidth: '500px',
          margin: '0 auto'
        }}>
          <Sparkles size={48} style={{ color: '#ffffff', marginBottom: '1rem' }} />
          <h3 style={{ 
            fontSize: '1.5rem', 
            fontWeight: 700, 
            color: '#ffffff',
            margin: '0 0 1rem 0'
          }}>
            Premium Service
          </h3>
          <p style={{ 
            fontSize: '1rem', 
            color: '#cccccc',
            margin: 0,
            lineHeight: 1.6
          }}>
            This revolutionary data transfer system requires a monthly subscription. 
            Quantum entanglement-based I/O exceeding light speed will be available soon.
          </p>
        </div>
      </div>
    </div>
  );
}
