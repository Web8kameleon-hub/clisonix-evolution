/**
 * EuroWeb Web8 - Demo Component
 * Pure Vanilla CSS + Framer Motion Implementation
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @version 8.0.1 Industrial
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { fadeInUp, staggerContainer, cardHover } from '../../lib/motion';

export function Demo(): React.ReactElement {
  return (
    <motion.div
      variants={staggerContainer}
      initial="initial"
      animate="animate"
      style={{
        padding: '2rem',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <motion.h1
        variants={fadeInUp}
        style={{
          fontSize: '3rem',
          fontWeight: '700',
          color: 'white',
          textAlign: 'center',
          marginBottom: '2rem',
          textShadow: '0 4px 8px rgba(0, 0, 0, 0.3)',
        }}
      >
        Demo Component
      </motion.h1>

      <motion.div
        variants={fadeInUp}
        whileHover={cardHover}
        style={{
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          padding: '2rem',
          borderRadius: '1rem',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          maxWidth: '600px',
          textAlign: 'center',
        }}
      >
        <p style={{ 
          color: 'rgba(255, 255, 255, 0.9)', 
          fontSize: '1.125rem',
          lineHeight: '1.6'
        }}>
          This is a demo component built with pure Vanilla CSS and Framer Motion.
          Clean industrial-grade code with CSS Modules + CVA architecture.
        </p>
      </motion.div>
    </motion.div>
  );
}
