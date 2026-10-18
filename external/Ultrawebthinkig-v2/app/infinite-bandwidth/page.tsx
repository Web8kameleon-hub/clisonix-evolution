/**
 * Infinite Bandwidth Page - Unlimited Data Throughput
 * Coming Soon - Requires Monthly Subscription
 */

'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function InfiniteBandwidthPage() {
  return (
    <div style={{
      minHeight: '100vh',
      background: `
        radial-gradient(circle at 20% 50%, #0080ff22 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, #ff6b0022 0%, transparent 50%),
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
        color: '#0080ff',
        textDecoration: 'none'
      }}>
        <ArrowLeft size={20} />
        Back to Ultra Speed
      </Link>

      <div style={{ marginBottom: '3rem' }}>
        <div style={{ fontSize: '8rem', marginBottom: '1rem' }}>∞</div>
        <h1 style={{
          fontSize: '4rem',
          fontWeight: 900,
          margin: '0 0 1rem 0',
          background: 'linear-gradient(45deg, #0080ff, #ffffff)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          Infinite Bandwidth
        </h1>
        <p style={{ fontSize: '1.5rem', color: '#aaaaaa', margin: '0 0 3rem 0' }}>
          Unlimited Data Throughput • Coming Soon
        </p>
        <div style={{
          background: 'rgba(0, 128, 255, 0.1)',
          border: '2px solid #0080ff',
          borderRadius: '20px',
          padding: '2rem',
          maxWidth: '500px'
        }}>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0080ff', margin: '0 0 1rem 0' }}>
            Premium Service
          </h3>
          <p style={{ color: '#cccccc', lineHeight: 1.6 }}>
            Unlimited bandwidth technology requires monthly subscription.
          </p>
        </div>
      </div>
    </div>
  );
}
