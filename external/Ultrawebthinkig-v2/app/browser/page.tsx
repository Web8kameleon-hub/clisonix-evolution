/**
 * EuroWeb - Browser Page
 * Web8 Tab Browser Interface
 */

export default function BrowserPage() {
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
          Web8 Browser
        </h1>
        
        <p style={{ 
          fontSize: '1.2rem', 
          marginBottom: '3rem',
          color: '#cbd5e1'
        }}>
          Next-Generation Web Browser Interface
        </p>
        
        <div style={{
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          borderRadius: '0.5rem',
          padding: '2rem',
          marginTop: '2rem'
        }}>
          <h3 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem' }}>
            Tab System
          </h3>
          <p style={{ color: '#94a3b8' }}>
            Advanced tab management with live metrics and AI integration
          </p>
        </div>
      </div>
    </div>
  )
}