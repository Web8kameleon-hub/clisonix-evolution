"use client";


// ⚡ CONVERTED TO STATIC CLIENT COMPONENT
// - Removed useState for Web8 compliance
// - Added "use client" directive
// - Use props or static values instead of state

/**
 * EuroWeb Web8 - Dynamic Component System with CVA
 * Ultra-High Performance Dynamic Components with Class Variance Authority
 * 
 * @module DynamicComponents
 * @author Ledjan Ahmati (100% Owner)
 * @license MIT
 * @version 8.0.1 Industrial
 */

import { cva, type VariantProps } from 'class-variance-authority';
import React from 'react';
import { motion } from 'framer-motion';

/**
 * Industrial Button Component Variants
 */
const buttonVariants = cva(
  // Base classes
  "inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
        secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500",
        destructive: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
        ghost: "text-gray-700 hover:bg-gray-100 focus:ring-gray-500",
        agi: "bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 focus:ring-purple-500",
        industrial: "bg-gray-900 text-white border border-gray-700 hover:bg-gray-800 focus:ring-gray-600"
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-base",
        lg: "h-12 px-6 text-lg",
        xl: "h-14 px-8 text-xl"
      },
      width: {
        auto: "w-auto",
        full: "w-full",
        fit: "w-fit"
      }
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
      width: "auto"
    }
  }
);

/**
 * Industrial Card Component Variants
 */
const cardVariants = cva(
  "rounded-lg border shadow-sm transition-all duration-200",
  {
    variants: {
      variant: {
        default: "bg-white border-gray-200",
        dark: "bg-gray-900 border-gray-800 text-white",
        agi: "bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 border-purple-500/20 text-white",
        industrial: "bg-gray-950 border-gray-700 text-gray-100",
        glass: "bg-white/10 backdrop-blur-lg border-white/20 text-white"
      },
      padding: {
        none: "p-0",
        sm: "p-4",
        md: "p-6",
        lg: "p-8",
        xl: "p-10"
      },
      shadow: {
        none: "shadow-none",
        sm: "shadow-sm",
        md: "shadow-md",
        lg: "shadow-lg",
        xl: "shadow-xl"
      }
    },
    defaultVariants: {
      variant: "default",
      padding: "md",
      shadow: "sm"
    }
  }
);

/**
 * Industrial Text Component Variants
 */
const textVariants = cva(
  "transition-colors duration-200",
  {
    variants: {
      variant: {
        default: "text-gray-900",
        muted: "text-gray-500",
        accent: "text-blue-600",
        destructive: "text-red-600",
        success: "text-green-600",
        warning: "text-yellow-600",
        agi: "bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent",
        industrial: "text-gray-100"
      },
      size: {
        xs: "text-xs",
        sm: "text-sm",
        base: "text-base",
        lg: "text-lg",
        xl: "text-xl",
        "2xl": "text-2xl",
        "3xl": "text-3xl",
        "4xl": "text-4xl"
      },
      weight: {
        normal: "font-normal",
        medium: "font-medium",
        semibold: "font-semibold",
        bold: "font-bold"
      },
      align: {
        left: "text-left",
        center: "text-center",
        right: "text-right"
      }
    },
    defaultVariants: {
      variant: "default",
      size: "base",
      weight: "normal",
      align: "left"
    }
  }
);

/**
 * Industrial Layout Component Variants
 */
const layoutVariants = cva(
  "w-full",
  {
    variants: {
      display: {
        block: "block",
        flex: "flex",
        grid: "grid",
        inline: "inline",
        "inline-flex": "inline-flex",
        "inline-grid": "inline-grid"
      },
      direction: {
        row: "flex-row",
        col: "flex-col",
        "row-reverse": "flex-row-reverse",
        "col-reverse": "flex-col-reverse"
      },
      justify: {
        start: "justify-start",
        center: "justify-center",
        end: "justify-end",
        between: "justify-between",
        around: "justify-around",
        evenly: "justify-evenly"
      },
      align: {
        start: "items-start",
        center: "items-center",
        end: "items-end",
        stretch: "items-stretch",
        baseline: "items-baseline"
      },
      gap: {
        none: "gap-0",
        xs: "gap-1",
        sm: "gap-2",
        md: "gap-4",
        lg: "gap-6",
        xl: "gap-8",
        "2xl": "gap-10"
      },
      padding: {
        none: "p-0",
        xs: "p-1",
        sm: "p-2",
        md: "p-4",
        lg: "p-6",
        xl: "p-8",
        "2xl": "p-10"
      },
      margin: {
        none: "m-0",
        xs: "m-1",
        sm: "m-2",
        md: "m-4",
        lg: "m-6",
        xl: "m-8",
        "2xl": "m-10"
      }
    },
    defaultVariants: {
      display: "block",
      gap: "none",
      padding: "none",
      margin: "none"
    }
  }
);

/**
 * Type Definitions for CVA Props
 */
export type ButtonVariants = VariantProps<typeof buttonVariants>;
export type CardVariants = VariantProps<typeof cardVariants>;
export type TextVariants = VariantProps<typeof textVariants>;
export type LayoutVariants = VariantProps<typeof layoutVariants>;

/**
 * Dynamic Component Interfaces
 */
export interface DynamicButtonProps extends ButtonVariants {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

export interface DynamicCardProps extends CardVariants {
  children: React.ReactNode;
  className?: string;
}

export interface DynamicTextProps extends TextVariants {
  children: React.ReactNode;
  as?: 'p' | 'span' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'div';
  className?: string;
}

export interface DynamicLayoutProps extends LayoutVariants {
  children: React.ReactNode;
  as?: 'div' | 'section' | 'article' | 'header' | 'footer' | 'main' | 'aside';
  className?: string;
}

/**
 * Motion Configuration for Dynamic Components
 */
export const motionPresets = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.3 }
  },
  slideUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: { duration: 0.4, ease: "easeOut" }
  },
  slideDown: {
    initial: { opacity: 0, y: -20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 20 },
    transition: { duration: 0.4, ease: "easeOut" }
  },
  scale: {
    initial: { opacity: 0, scale: 0.9 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.9 },
    transition: { duration: 0.3, ease: "easeOut" }
  },
  industrial: {
    initial: { opacity: 0, y: 30, scale: 0.95 },
    animate: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, y: -30, scale: 0.95 },
    transition: { duration: 0.5, ease: [0.23, 1, 0.32, 1] }
  }
} as const;

/**
 * Dynamic Component Factory
 */
export class DynamicComponentFactory {
  /**
   * Create a dynamic button with CVA variants and motion
   */
  static createButton(props: DynamicButtonProps & { motion?: keyof typeof motionPresets }): React.ReactElement {
    const { children, variant, size, width, className, motion: motionType, ...rest } = props;
    
    if (motionType) {
      const motionProps = motionPresets[motionType];
      return React.createElement(
        motion.button,
        {
          className: buttonVariants({ variant, size, width, className }),
          ...motionProps,
          ...rest
        },
        children
      );
    }
    
    return React.createElement(
      'button',
      {
        className: buttonVariants({ variant, size, width, className }),
        ...rest
      },
      children
    );
  }

  /**
   * Create a dynamic card with CVA variants and motion
   */
  static createCard(props: DynamicCardProps & { motion?: keyof typeof motionPresets }): React.ReactElement {
    const { children, variant, padding, shadow, className, motion: motionType, ...rest } = props;
    
    if (motionType) {
      const motionProps = motionPresets[motionType];
      return React.createElement(
        motion.div,
        {
          className: cardVariants({ variant, padding, shadow, className }),
          ...motionProps,
          ...rest
        },
        children
      );
    }
    
    return React.createElement(
      'div',
      {
        className: cardVariants({ variant, padding, shadow, className }),
        ...rest
      },
      children
    );
  }

  /**
   * Create dynamic text with CVA variants and motion
   */
  static createText(props: DynamicTextProps & { motion?: keyof typeof motionPresets }): React.ReactElement {
    const { children, variant, size, weight, align, as = 'p', className, motion: motionType, ...rest } = props;
    
    if (motionType) {
      const motionProps = motionPresets[motionType];
      const MotionComponent = motion[as as keyof typeof motion] as any;
      return React.createElement(
        MotionComponent,
        {
          className: textVariants({ variant, size, weight, align, className }),
          ...motionProps,
          ...rest
        },
        children
      );
    }
    
    return React.createElement(
      as,
      {
        className: textVariants({ variant, size, weight, align, className }),
        ...rest
      },
      children
    );
  }

  /**
   * Create dynamic layout with CVA variants and motion
   */
  static createLayout(props: DynamicLayoutProps & { motion?: keyof typeof motionPresets }): React.ReactElement {
    const { 
      children, 
      display, 
      direction, 
      justify, 
      align, 
      gap, 
      padding, 
      margin, 
      as = 'div', 
      className, 
      motion: motionType,
      ...rest 
    } = props;
    
    if (motionType) {
      const motionProps = motionPresets[motionType];
      const MotionComponent = motion[as as keyof typeof motion] as any;
      return React.createElement(
        MotionComponent,
        {
          className: layoutVariants({ 
            display, 
            direction, 
            justify, 
            align, 
            gap, 
            padding, 
            margin, 
            className 
          }),
          ...motionProps,
          ...rest
        },
        children
      );
    }
    
    return React.createElement(
      as,
      {
        className: layoutVariants({ 
          display, 
          direction, 
          justify, 
          align, 
          gap, 
          padding, 
          margin, 
          className 
        }),
        ...rest
      },
      children
    );
  }
}

/**
 * Export CVA variants for direct use
 */
export { buttonVariants, cardVariants, textVariants, layoutVariants };

/**
 * Industrial Component Presets
 */
export const IndustrialPresets = {
  AGIButton: {
    variant: 'agi' as const,
    size: 'lg' as const,
    motion: 'industrial' as const
  },
  IndustrialCard: {
    variant: 'industrial' as const,
    padding: 'lg' as const,
    shadow: 'xl' as const,
    motion: 'slideUp' as const
  },
  AGITitle: {
    variant: 'agi' as const,
    size: '3xl' as const,
    weight: 'bold' as const,
    align: 'center' as const,
    motion: 'fadeIn' as const
  },
  IndustrialLayout: {
    display: 'flex' as const,
    direction: 'col' as const,
    gap: 'lg' as const,
    padding: 'xl' as const,
    motion: 'industrial' as const
  }
};
