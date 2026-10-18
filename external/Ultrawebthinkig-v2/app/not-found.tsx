/**
 * UltraWeb - 404 Not Found Page
 * Ultra-themed with navigation integration
 */

'use client';

import Link from 'next/link';

export default function NotFound() {
  return (
    <div style={{ 
      minHeight: '100vh',
      background: `
        radial-gradient(circle at 20% 50%, #00ff0011 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, #ff008011 0%, transparent 50%),
        linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)
      `,
      color: 'white',
      padding: '2rem',
      fontFamily: 'SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div style={{ textAlign: 'center', maxWidth: '600px' }}>
        <h1 style={{ 
          fontSize: '8rem', 
          fontWeight: 900, 
          marginBottom: '1rem',
          background: 'linear-gradient(45deg, #00ff00, #ff0080)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          textShadow: '0 0 30px #00ff00',
          letterSpacing: '-4px'
        }}>
          404
        </h1>
        
        <h2 style={{ 
          fontSize: '2.5rem', 
          fontWeight: 700, 
          marginBottom: '1rem',
          color: '#00ff00'
        }}>
          Page Not Found
        </h2>
        
        <p style={{ 
          fontSize: '1.25rem', 
          marginBottom: '3rem',
          color: '#aaaaaa',
          lineHeight: 1.6
        }}>
          The page you are looking for does not exist or has been moved.<br/>
          Navigate back to UltraWeb's neural network.
        </p>
        
        {/* Quick Navigation */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '1rem',
          marginBottom: '2rem'
        }}>
          {[
            { href: '/', label: 'Home', emoji: '🏠', color: '#3b82f6' },
            { href: '/neural-dev', label: 'Neural Dev', emoji: '🧠', color: '#ff0080' },
            { href: '/neural-search-demo', label: 'Neural Search', emoji: '🔍', color: '#00ff00' },
            { href: '/agimed-professional', label: 'AGI×Med Pro', emoji: '🛡️', color: '#0066cc' },
            { href: '/real-search-demo', label: 'Real Search', emoji: '🔍', color: '#10b981' },
            { href: '/ultra-speed', label: 'Ultra Speed', emoji: '⚡', color: '#00ff00' }
          ].map((item, index) => (
            <Link key={index} href={item.href} style={{ textDecoration: 'none' }}>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '1.5rem 1rem',
                background: `${item.color}22`,
                border: `2px solid ${item.color}`,
                borderRadius: '12px',
                color: 'white',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = `${item.color}44`;
                e.currentTarget.style.transform = 'translateY(-5px)';
                e.currentTarget.style.boxShadow = `0 10px 25px ${item.color}44`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = `${item.color}22`;
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}>
                <span style={{ fontSize: '2rem' }}>{item.emoji}</span>
                <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>
                  {item.label}
                </span>
              </div>
            </Link>
          ))}
        </div>
        
        <div style={{
          fontSize: '0.875rem',
          color: '#666',
          marginTop: '2rem'
        }}>
          UltraWeb v8.0.0 - Më i Shpejti në Rruzullin Tokësor
        </div>
      </div>
    </div>
  )
}