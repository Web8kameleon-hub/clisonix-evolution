/**
 * EuroWeb - AGI Demo Page
 * Vanilla CSS + Next.js
 */

export default function AGIDemoPage() {
  return (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(to bottom right, #1e293b, #334155)',
      color: 'white',
      padding: '2rem',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
        <h1 style={{ 
          fontSize: '3rem', 
          fontWeight: 'bold', 
          marginBottom: '2rem',
          color: '#60a5fa'
        }}>
          AGI Demo
        </h1>
        
        <p style={{ 
          fontSize: '1.2rem', 
          marginBottom: '3rem',
          color: '#cbd5e1'
        }}>
          Advanced General Intelligence Platform - Coming Soon
        </p>
      </div>
    </div>
  )
}