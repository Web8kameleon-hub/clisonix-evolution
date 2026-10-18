/**
 * EuroWeb Industrial Token System Demo
 * Demonstrates comprehensive CVA token usage with vanilla motion
 */

import { cva } from 'class-variance-authority';
import { clsx } from 'clsx';
import { motion } from 'framer-motion';
import React from 'react';

// CVA variants for TokenDemo components
const containerVariants = cva(
  'max-w-6xl mx-auto px-6 py-12 space-y-16',
  {
    variants: {
      variant: {
        default: 'bg-background',
        industrial: 'bg-slate-50',
        dark: 'bg-slate-900'
      }
    },
    defaultVariants: {
      variant: 'default'
    }
  }
);

const stackVariants = cva(
  'flex flex-col',
  {
    variants: {
      gap: {
        '4': 'space-y-4',
        '6': 'space-y-6', 
        '8': 'space-y-8'
      }
    },
    defaultVariants: {
      gap: '6'
    }
  }
);

const hstackVariants = cva(
  'flex flex-row items-center',
  {
    variants: {
      gap: {
        '4': 'space-x-4',
        '6': 'space-x-6'
      },
      justify: {
        center: 'justify-center',
        start: 'justify-start',
        end: 'justify-end'
      }
    },
    defaultVariants: {
      gap: '4',
      justify: 'center'
    }
  }
);

const cardVariants = cva(
  'rounded-lg border transition-all duration-300 cursor-pointer',
  {
    variants: {
      variant: {
        default: 'bg-white border-slate-200 hover:shadow-xl hover:-translate-y-0.5 hover:border-slate-300',
        industrial: 'bg-slate-100 border-slate-300 hover:shadow-lg hover:border-slate-400',
        agi: 'bg-purple-950 border-purple-500 shadow-purple-500/20 hover:shadow-purple-500/40',
        gradient: 'bg-gradient-to-br from-orange-100 to-orange-200 border-white/10 backdrop-blur-md'
      },
      size: {
        default: 'p-6',
        lg: 'p-8'
      }
    },
    defaultVariants: {
      variant: 'default',
      size: 'default'
    }
  }
);

const textVariants = cva(
  'font-medium',
  {
    variants: {
      size: {
        sm: 'text-sm',
        base: 'text-base', 
        lg: 'text-lg',
        xl: 'text-xl',
        '2xl': 'text-2xl',
        '4xl': 'text-4xl'
      },
      weight: {
        medium: 'font-medium',
        semibold: 'font-semibold',
        bold: 'font-bold'
      },
      color: {
        default: 'text-slate-900',
        muted: 'text-slate-600',
        agi: 'text-purple-100',
        'agi-muted': 'text-purple-200'
      },
      align: {
        center: 'text-center',
        left: 'text-left'
      },
      gradient: {
        industrial: 'bg-gradient-to-r from-slate-600 to-slate-800 bg-clip-text text-transparent',
        agi: 'bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent',
        quantum: 'bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent'
      }
    },
    defaultVariants: {
      size: 'base',
      weight: 'medium',
      color: 'default'
    }
  }
);

const themeBoxVariants = cva(
  'w-20 h-20 rounded-lg flex items-center justify-center text-white text-sm font-medium capitalize shadow-lg transition-all duration-300 cursor-pointer hover:scale-105 hover:shadow-xl',
  {
    variants: {
      theme: {
        industrial: 'bg-slate-500',
        agi: 'bg-purple-500',
        quantum: 'bg-blue-500',
        ultra: 'bg-orange-500', 
        neural: 'bg-emerald-500'
      }
    }
  }
);

export const TokenDemo: React.FC = () => {
  return (
    <div className={containerVariants()}>
      {/* Token-based Typography */}
      <div className={stackVariants({ gap: '6' })}>
        <motion.h1 
          className={textVariants({ size: '4xl', weight: 'bold', color: 'default', align: 'center' })}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          EuroWeb Industrial Token System
        </motion.h1>
        
        <motion.p 
          className={clsx(
            textVariants({ size: 'lg', color: 'muted', align: 'center' }),
            'max-w-2xl mx-auto leading-relaxed'
          )}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Comprehensive design tokens with semantic meanings and industrial theming
        </motion.p>
      </div>

      {/* Color Palette Demo */}
      <div className={stackVariants({ gap: '8' })}>
        <h2 className={textVariants({ size: '2xl', weight: 'semibold', color: 'default' })}>
          Color System
        </h2>
        
        <div className={hstackVariants({ gap: '4', justify: 'center' })}>
          {(['industrial', 'agi', 'quantum', 'ultra', 'neural'] as const).map((theme, index) => (
            <motion.div 
              key={theme} 
              className={themeBoxVariants({ theme })}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {theme}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Token Cards */}
      <div className={stackVariants({ gap: '8' })}>
        <h2 className={textVariants({ size: '2xl', weight: 'semibold', color: 'default' })}>
          Token-based Cards
        </h2>
        
        {/* Industrial Card using CVA variants */}
        <motion.div 
          className={cardVariants({ variant: 'default' })}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          whileHover={{ y: -2 }}
        >
          <h3 className={textVariants({ size: 'xl', weight: 'semibold', color: 'default' })}>
            Industrial Token Card
          </h3>
          <p className={clsx(textVariants({ color: 'muted' }), 'mt-3 leading-relaxed')}>
            Token-based styling with interactive hover effects and proper semantic color usage.
          </p>
        </motion.div>

        {/* AGI-themed Panel */}
        <motion.div 
          className={cardVariants({ variant: 'agi' })}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          style={{
            boxShadow: '0 0 20px rgba(168, 85, 247, 0.3), inset 0 0 20px rgba(168, 85, 247, 0.1)'
          }}
        >
          <h3 className={textVariants({ size: 'xl', weight: 'semibold', color: 'agi' })}>
            AGI Neural Panel
          </h3>
          <p className={clsx(textVariants({ color: 'agi-muted' }), 'mt-3 leading-relaxed')}>
            Advanced AI interface with glowing effects and neural network aesthetics.
          </p>
        </motion.div>

        {/* Gradient Box using CVA */}
        <motion.div 
          className={cardVariants({ variant: 'gradient' })}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <h3 className={textVariants({ size: 'xl', weight: 'semibold', color: 'default', align: 'center' })}>
            Quantum Gradient Box
          </h3>
          <p className={clsx(textVariants({ color: 'muted', align: 'center' }), 'mt-3 leading-relaxed')}>
            Glassmorphism effect with quantum-themed gradients and backdrop blur.
          </p>
        </motion.div>
      </div>

      {/* Token Usage Examples */}
      <div className={stackVariants({ gap: '6' })}>
        <h2 className={textVariants({ size: '2xl', weight: 'semibold', color: 'default' })}>
          Direct Token Usage
        </h2>
        
        <div className={hstackVariants({ gap: '4', justify: 'center' })}>
          {[
            { label: 'Spacing', value: '1rem' },
            { label: 'Duration', value: '300ms' },
            { label: 'Shadow', value: 'md' }
          ].map((item, index) => (
            <motion.div 
              key={item.label}
              className="p-4 bg-slate-100 border border-slate-200 rounded-md text-sm text-slate-600"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              {item.label}: {item.value}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Text Gradient Utilities */}
      <div className={stackVariants({ gap: '6' })}>
        <h2 className={textVariants({ size: '2xl', weight: 'semibold', color: 'default' })}>
          Text Gradients
        </h2>
        
        <div className={hstackVariants({ gap: '6', justify: 'center' })}>
          {[
            { text: 'Industrial Gradient', gradient: 'industrial' as const },
            { text: 'AGI Gradient', gradient: 'agi' as const },
            { text: 'Quantum Gradient', gradient: 'quantum' as const }
          ].map((item, index) => (
            <motion.div 
              key={item.text}
              className={clsx(
                textVariants({ size: 'xl', weight: 'bold', gradient: item.gradient }),
                'p-6'
              )}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              whileHover={{ scale: 1.05 }}
            >
              {item.text}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TokenDemo;
