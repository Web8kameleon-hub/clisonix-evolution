/**
 * EuroWeb - Simple Static Component
 * Pure CSS (no CVA, no Tailwind)
 */

export function SimpleDemo() {
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
          EuroWeb Platform
        </h1>
        
        <p style={{ 
          fontSize: '1.2rem', 
          marginBottom: '3rem',
          color: '#cbd5e1'
        }}>
          Pure TypeScript + Vanilla CSS + Next.js 14
        </p>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1.5rem',
          marginTop: '2rem'
        }}>
          <div style={{
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.2)',
            borderRadius: '0.5rem',
            padding: '1.5rem'
          }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
              TypeScript
            </h3>
            <p style={{ color: '#94a3b8' }}>
              100% TypeScript implementation with strict mode
            </p>
          </div>
          
          <div style={{
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            border: '1px solid rgba(34, 197, 94, 0.2)',
            borderRadius: '0.5rem',
            padding: '1.5rem'
          }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
              Vanilla CSS
            </h3>
            <p style={{ color: '#94a3b8' }}>
              Pure CSS modules without any runtime overhead
            </p>
          </div>
          
          <div style={{
            backgroundColor: 'rgba(168, 85, 247, 0.1)',
            border: '1px solid rgba(168, 85, 247, 0.2)',
            borderRadius: '0.5rem',
            padding: '1.5rem'
          }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
              Industrial Grade
            </h3>
            <p style={{ color: '#94a3b8' }}>
              Enterprise-ready platform for modern web applications
            </p>
          </div>
        </div>
        
        <div style={{ 
          marginTop: '3rem',
          padding: '1.5rem',
          backgroundColor: 'rgba(15, 23, 42, 0.5)',
          borderRadius: '0.75rem',
          border: '1px solid rgba(71, 85, 105, 0.3)'
        }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
            Status
          </h2>
          <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <span style={{ color: '#10b981' }}>✅</span> TypeScript Compilation
            </div>
            <div>
              <span style={{ color: '#10b981' }}>✅</span> ESLint Setup
            </div>
            <div>
              <span style={{ color: '#10b981' }}>✅</span> Next.js Build
            </div>
            <div>
              <span style={{ color: '#10b981' }}>✅</span> Pure Architecture
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
