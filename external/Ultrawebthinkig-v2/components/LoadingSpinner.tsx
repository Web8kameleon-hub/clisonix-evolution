/**
 * EuroWeb - Loading Spinner Component
 * Pure CSS Modules + CVA
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @version 8.0.0 Ultra
 */

'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { cva, type VariantProps } from 'class-variance-authority'
import styles from './LoadingSpinner.module.css'

const spinnerVariants = cva(styles.spinner, {
  variants: {
    size: {
      small: styles.small,
      medium: styles.medium,
      large: styles.large,
    },
    color: {
      primary: styles.primary,
      secondary: styles.secondary,
      accent: styles.accent,
    },
  },
  defaultVariants: {
    size: 'medium',
    color: 'primary',
  },
})

interface LoadingSpinnerProps extends VariantProps<typeof spinnerVariants> {
  className?: string
}

export function LoadingSpinner({ size, color, className }: LoadingSpinnerProps) {
  return (
    <motion.div
      className={spinnerVariants({ size, color, className })}
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: 'linear',
      }}
      aria-label="Loading..."
      role="status"
    >
      <div className={styles.inner} />
    </motion.div>
  )
}
