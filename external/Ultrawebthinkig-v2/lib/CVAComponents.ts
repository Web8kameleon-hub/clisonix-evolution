"use client";


// ⚡ CONVERTED TO STATIC CLIENT COMPONENT
// - Removed useState for Web8 compliance
// - Added "use client" directive
// - Use props or static values instead of state

/**
 * EuroWeb Web8 - CVA Components (CSS Modules Only)
 * Class Variance Authority with Pure CSS Modules
 * 
 * @module CVAComponents
 * @author Ledjan Ahmati (100% Owner)
 * @license MIT
 * @version 8.0.1 Industrial
 */

import { cva, type VariantProps } from 'class-variance-authority';

/**
 * Button variants using CSS custom properties
 */
export const buttonVariants = cva(
  // Base classes
  "button-base",
  {
    variants: {
      variant: {
        primary: "button-primary",
        secondary: "button-secondary", 
        destructive: "button-destructive",
        ghost: "button-ghost",
        agi: "button-agi",
        industrial: "button-industrial"
      },
      size: {
        sm: "button-sm",
        md: "button-md",
        lg: "button-lg",
        xl: "button-xl"
      }
    },
    defaultVariants: {
      variant: "primary",
      size: "md"
    }
  }
);

/**
 * Card variants using CSS custom properties
 */
export const cardVariants = cva(
  "card-base",
  {
    variants: {
      variant: {
        default: "card-default",
        bordered: "card-bordered",
        elevated: "card-elevated",
        ghost: "card-ghost"
      },
      padding: {
        none: "card-padding-none",
        sm: "card-padding-sm",
        md: "card-padding-md", 
        lg: "card-padding-lg"
      }
    },
    defaultVariants: {
      variant: "default",
      padding: "md"
    }
  }
);

/**
 * Text variants using CSS custom properties
 */
export const textVariants = cva(
  "text-base",
  {
    variants: {
      variant: {
        h1: "text-h1",
        h2: "text-h2",
        h3: "text-h3",
        body: "text-body",
        small: "text-small",
        muted: "text-muted"
      },
      weight: {
        normal: "text-weight-normal",
        medium: "text-weight-medium",
        semibold: "text-weight-semibold",
        bold: "text-weight-bold"
      }
    },
    defaultVariants: {
      variant: "body",
      weight: "normal"
    }
  }
);

export type ButtonVariants = VariantProps<typeof buttonVariants>;
export type CardVariants = VariantProps<typeof cardVariants>;
export type TextVariants = VariantProps<typeof textVariants>;
