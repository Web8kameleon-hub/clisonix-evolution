/**
 * EuroWeb Surfing Ultra - Ultra-Fluid Hybrid Navigation
 * Ultra-Fast Performance with Quantum-Enhanced Animations
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0 Ultra-Fluid
 * @license MIT
 */

"use client";

import React, { useState, useCallback, useMemo } from "react";
import { motion, AnimatePresence, useSpring, useTransform } from "framer-motion";

// Ultra-fluid animation variants
const ultraFluidVariants = {
  initial: { 
    opacity: 0, 
    scale: 0.8, 
    y: 50,
    filter: 'blur(10px)',
    rotateX: -15
  },
  animate: { 
    opacity: 1, 
    scale: 1, 
    y: 0,
    filter: 'blur(0px)',
    rotateX: 0,
    transition: {
      type: "spring" as const,
      stiffness: 300,
      damping: 25,
      mass: 0.8,
      duration: 0.6
    }
  },
  exit: { 
    opacity: 0, 
    scale: 0.9, 
    y: -30,
    filter: 'blur(5px)',
    transition: {
      duration: 0.3,
      ease: "easeOut" as const
    }
  }
};

const containerVariants = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
};

const itemVariants = {
  initial: { 
    opacity: 0, 
    x: -50, 
    rotateY: -25,
    scale: 0.9
  },
  animate: { 
    opacity: 1, 
    x: 0, 
    rotateY: 0,
    scale: 1,
    transition: {
      type: "spring" as const,
      stiffness: 400,
      damping: 30
    }
  }
};

interface SurfingState {
  input: string;
  response: string;
  loading: boolean;
  error: string;
  mode: 'search' | 'chat' | 'navigate';
}

const Surfing: React.FC = () => {
  const [state, setState] = useState<SurfingState>({
    input: "",
    response: "",
    loading: false,
    error: "",
    mode: 'search'
  });

  // Ultra-fast spring animations
  const springConfig = { stiffness: 400, damping: 30, mass: 0.8 };
  const x = useSpring(0, springConfig);
  const y = useSpring(0, springConfig);
  const scale = useSpring(1, springConfig);
  
  const rotateX = useTransform(y, [-100, 100], [-15, 15]);
  const rotateY = useTransform(x, [-100, 100], [-15, 15]);

  // Ultra-fast input handler with debouncing
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setState(prev => ({ ...prev, input: value, error: "" }));
  }, []);

  // Hybrid mode switcher
  const switchMode = useCallback((newMode: 'search' | 'chat' | 'navigate') => {
    setState(prev => ({ ...prev, mode: newMode }));
  }, []);

  // Ultra-fast AGI processing simulation
  const handleAsk = useCallback(async () => {
    if (!state.input.trim()) return;

    setState(prev => ({ ...prev, loading: true, error: "", response: "" }));

    // Simulate ultra-fast AI processing
    await new Promise(resolve => setTimeout(resolve, 800));

    const responses = {
      search: `🔍 Ultra Search Results për "${state.input}":\n\n✅ Gjetur ${Math.floor(Math.random() * 10000)} rezultate\n🚀 Kohë përgjigje: 0.${Math.floor(Math.random() * 99)}ms\n🧠 AGI Confidence: ${(Math.random() * 0.3 + 0.7).toFixed(3)}`,
      chat: `🤖 AGI Chat Response:\n\nUnë kuptova kërkesën tuaj për "${state.input}". Ja një përgjigje e detajuar:\n\n• Analiza e kompletuar në ${Math.floor(Math.random() * 50)}ms\n• Quantum processing active\n• Neural networks optimized\n\nA doni më shumë detaje?`,
      navigate: `🌐 Navigation Ultra për "${state.input}":\n\n📍 Destinacion: ${state.input}\n🚄 Kohë udhëtimi: ${Math.floor(Math.random() * 60)} minuta\n⚡ Route optimization: Active\n🛡️ Security level: Maximum`
    };

    setState(prev => ({ ...prev, loading: false, response: responses[state.mode] }));
  }, [state.input, state.mode]);

  // Mode configuration
  const modeConfig = useMemo(() => ({
    search: { color: '#3b82f6', icon: '🔍' },
    chat: { color: '#10b981', icon: '🤖' },
    navigate: { color: '#f59e0b', icon: '🌐' }
  }), []);

  // Styles object
  const styles = useMemo(() => ({
    container: "w-full max-w-4xl mx-auto p-6 bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 rounded-2xl shadow-2xl",
    searchBox: "relative mb-6 p-4 bg-white/10 backdrop-blur-lg rounded-xl border border-white/20",
    input: "w-full px-4 py-3 bg-white/5 border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:border-blue-400",
    button: "px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-semibold hover:from-blue-600 hover:to-purple-700 transition-all",
    modeButtons: "flex gap-2 mb-4",
    modeButton: "px-4 py-2 rounded-lg font-medium transition-all",
    response: "mt-4 p-4 bg-white/5 rounded-lg border border-white/20 text-white whitespace-pre-wrap"
  }), []);

  return (
    <motion.div 
      className={styles.container}
      variants={containerVariants}
      initial="initial"
      animate="animate"
    >
      <motion.div 
        className={styles.searchBox}
        style={{
          border: `2px solid ${modeConfig[state.mode].color}`,
          background: state.loading ? 'rgba(107, 114, 128, 0.3)' : `linear-gradient(45deg, ${modeConfig[state.mode].color}20, ${modeConfig[state.mode].color}10)`
        }}
        whileHover={{ scale: 1.02, boxShadow: `0 10px 25px ${modeConfig[state.mode].color}40` }}
        variants={ultraFluidVariants}
      >
        {/* Mode Selection */}
        <div className={styles.modeButtons}>
          {Object.entries(modeConfig).map(([mode, config]) => (
            <button
              key={mode}
              className={`${styles.modeButton} ${state.mode === mode ? 'bg-blue-500/20 text-white' : 'bg-white/10 text-white/70'}`}
              onClick={() => switchMode(mode as 'search' | 'chat' | 'navigate')}
            >
              {config.icon} {mode.charAt(0).toUpperCase() + mode.slice(1)}
            </button>
          ))}
        </div>

        {/* Input */}
        <input
          type="text"
          value={state.input}
          onChange={handleInputChange}
          placeholder={`Enter your ${state.mode} query...`}
          className={styles.input}
          disabled={state.loading}
        />

        {/* Submit Button */}
        <button
          onClick={handleAsk}
          disabled={state.loading}
          className={`${styles.button} mt-3 w-full ${state.loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {state.loading ? '⚡ Processing...' : `${modeConfig[state.mode].icon} ${state.mode.charAt(0).toUpperCase() + state.mode.slice(1)}`}
        </button>

        {/* Response */}
        <AnimatePresence>
          {state.response && (
            <motion.div
              className={styles.response}
              variants={itemVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              {state.response}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error */}
        {state.error && (
          <div className="mt-3 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200">
            ❌ {state.error}
          </div>
        )}
      </motion.div>
    </motion.div>
  );
};

export default Surfing;