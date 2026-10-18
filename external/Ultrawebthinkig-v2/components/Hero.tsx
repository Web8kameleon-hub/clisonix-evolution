'use client';
import { motion } from 'framer-motion';

const Hero = () => {
  return (
    <section style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #000000 0%, #111827 50%, #1f2937 100%)',
      color: 'white',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '0 24px'
    }}>
      <motion.h1 
        style={{
          fontSize: 'clamp(2rem, 8vw, 4rem)',
          fontWeight: 800,
          textAlign: 'center',
          marginBottom: '16px',
          background: 'linear-gradient(45deg, #d4af37, #f7e08b)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        EuroWeb Platform
      </motion.h1>
      <motion.p 
        style={{
          fontSize: 'clamp(1.25rem, 4vw, 1.5rem)',
          color: '#cbd5e1',
          textAlign: 'center',
          marginBottom: '32px',
          maxWidth: '600px'
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 1 }}
      >
        Pure TypeScript Industrial Web8 Architecture with AGI-Core Intelligence
      </motion.p>
      <motion.div 
        style={{
          display: 'flex',
          gap: '24px',
          flexWrap: 'wrap',
          justifyContent: 'center'
        }}
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1, duration: 1 }}
      >
        <button style={{
          background: '#d4af37',
          color: '#000',
          padding: '12px 24px',
          borderRadius: '8px',
          fontWeight: 600,
          border: 'none',
          cursor: 'pointer',
          transition: 'all 0.2s ease'
        }}>
          Start AGI Core
        </button>
        <button style={{
          border: '2px solid #d4af37',
          background: 'transparent',
          color: '#d4af37',
          padding: '12px 24px',
          borderRadius: '8px',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'all 0.2s ease'
        }}>
          Explore Platform
        </button>
      </motion.div>
    </section>
  );
}



export { Hero }
// Removed default export: Hero

