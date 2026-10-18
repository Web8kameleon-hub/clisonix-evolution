'use client'

/**
 * EuroWeb - Error Page
 * Client Component for Error Handling
 */

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div style={{
      display: 'flex',
      height: '100vh',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      backgroundColor: '#0f172a',
      color: '#f1f5f9'
    }}>
      <h2 style={{ color: '#f59e0b', marginBottom: '16px' }}>Something went wrong!</h2>
      <button
        onClick={() => reset()}
        style={{
          backgroundColor: '#f59e0b',
          color: '#0f172a',
          padding: '8px 16px',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Try again
      </button>
    </div>
  )
}
