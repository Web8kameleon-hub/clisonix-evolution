/**
 * EuroWeb Web8 - Button Component
 * CSS Modules + CVA Implementation
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @version 8.0.1 Industrial
 */

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import styles from '../styles/Button.module.css';

// CVA button variants using CSS module classes
const buttonVariants = cva(styles.button, {
  variants: {
    variant: {
      primary: styles.primary,
      secondary: styles.secondary,
      outline: styles.outline,
      ghost: styles.ghost,
      danger: styles.danger,
    },
    size: {
      small: styles.small,
      medium: styles.medium,
      large: styles.large,
    },
    fullWidth: {
      true: styles.fullWidth,
    },
    loading: {
      true: styles.loading,
    },
  },
  defaultVariants: {
    variant: 'primary',
    size: 'medium',
  },
});

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
  children: React.ReactNode;
}

export function Button({ 
  className, 
  variant, 
  size, 
  fullWidth, 
  loading, 
  children, 
  disabled, 
  ...props 
}: ButtonProps) {
  return (
    <button
      className={buttonVariants({ variant, size, fullWidth, loading, className })}
      disabled={disabled || loading}
      {...props}
    >
      {children}
    </button>
  );
}

// Named export only - no default exports in Web8

