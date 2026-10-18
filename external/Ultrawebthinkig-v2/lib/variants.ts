/**
 * EuroWeb Web8 - CVA Component Variants
 * Clean Class Variance Authority Configurations
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @version 8.0.1 Industrial
 */

import { cva } from 'class-variance-authority';
import buttonStyles from '../styles/Button.module.css';
import cardStyles from '../styles/Card.module.css';

// Button variants
export const buttonVariants = cva(buttonStyles.button, {
  variants: {
    variant: {
      primary: buttonStyles.primary,
      secondary: buttonStyles.secondary,
      outline: buttonStyles.outline,
      ghost: buttonStyles.ghost,
      danger: buttonStyles.danger,
    },
    size: {
      small: buttonStyles.small,
      medium: buttonStyles.medium,
      large: buttonStyles.large,
    },
    fullWidth: {
      true: buttonStyles.fullWidth,
    },
    loading: {
      true: buttonStyles.loading,
    },
  },
  defaultVariants: {
    variant: 'primary',
    size: 'medium',
  },
});

// Card variants
export const cardVariants = cva(cardStyles.card, {
  variants: {
    variant: {
      default: '',
      elevated: cardStyles.elevated,
      flat: cardStyles.flat,
      outlined: cardStyles.outlined,
      primary: cardStyles.primary,
      secondary: cardStyles.secondary,
    },
    size: {
      small: cardStyles.small,
      medium: cardStyles.medium,
      large: cardStyles.large,
      fullWidth: cardStyles.fullWidth,
    },
    interactive: {
      true: cardStyles.interactive,
    },
  },
  defaultVariants: {
    variant: 'default',
    size: 'medium',
  },
});

// Typography variants using pure CSS classes
export const textVariants = cva('', {
  variants: {
    size: {
      xs: 'text-xs',
      sm: 'text-sm', 
      base: 'text-base',
      lg: 'text-lg',
      xl: 'text-xl',
      '2xl': 'text-2xl',
      '3xl': 'text-3xl',
      '4xl': 'text-4xl',
      '5xl': 'text-5xl',
    },
    weight: {
      normal: 'font-normal',
      medium: 'font-medium',
      semibold: 'font-semibold',
      bold: 'font-bold',
    },
    color: {
      primary: 'text-primary',
      secondary: 'text-secondary',
      muted: 'text-muted',
      error: 'text-error',
      success: 'text-success',
      warning: 'text-warning',
      info: 'text-info',
    },
    align: {
      left: 'text-left',
      center: 'text-center',
      right: 'text-right',
      justify: 'text-justify',
    },
  },
  defaultVariants: {
    size: 'base',
    weight: 'normal',
    color: 'primary',
    align: 'left',
  },
});

// Layout container variants
export const containerVariants = cva('', {
  variants: {
    size: {
      sm: 'max-w-sm',
      md: 'max-w-md',
      lg: 'max-w-lg',
      xl: 'max-w-xl',
      '2xl': 'max-w-2xl',
      '3xl': 'max-w-3xl',
      '4xl': 'max-w-4xl',
      '5xl': 'max-w-5xl',
      '6xl': 'max-w-6xl',
      '7xl': 'max-w-7xl',
      full: 'max-w-full',
    },
    padding: {
      none: 'p-0',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
      xl: 'p-12',
    },
    centered: {
      true: 'mx-auto',
    },
  },
  defaultVariants: {
    size: 'lg',
    padding: 'md',
    centered: true,
  },
});

// Flex layout variants
export const flexVariants = cva('flex', {
  variants: {
    direction: {
      row: 'flex-row',
      column: 'flex-col',
      rowReverse: 'flex-row-reverse',
      columnReverse: 'flex-col-reverse',
    },
    justify: {
      start: 'justify-start',
      end: 'justify-end',
      center: 'justify-center',
      between: 'justify-between',
      around: 'justify-around',
      evenly: 'justify-evenly',
    },
    align: {
      start: 'items-start',
      end: 'items-end',
      center: 'items-center',
      baseline: 'items-baseline',
      stretch: 'items-stretch',
    },
    wrap: {
      nowrap: 'flex-nowrap',
      wrap: 'flex-wrap',
      wrapReverse: 'flex-wrap-reverse',
    },
    gap: {
      none: 'gap-0',
      xs: 'gap-1',
      sm: 'gap-2',
      md: 'gap-4',
      lg: 'gap-6',
      xl: 'gap-8',
      '2xl': 'gap-12',
    },
  },
  defaultVariants: {
    direction: 'row',
    justify: 'start',
    align: 'center',
    wrap: 'nowrap',
    gap: 'md',
  },
});

// Grid layout variants
export const gridVariants = cva('grid', {
  variants: {
    cols: {
      1: 'grid-cols-1',
      2: 'grid-cols-2',
      3: 'grid-cols-3',
      4: 'grid-cols-4',
      5: 'grid-cols-5',
      6: 'grid-cols-6',
      12: 'grid-cols-12',
    },
    gap: {
      none: 'gap-0',
      xs: 'gap-1',
      sm: 'gap-2',
      md: 'gap-4',
      lg: 'gap-6',
      xl: 'gap-8',
      '2xl': 'gap-12',
    },
  },
  defaultVariants: {
    cols: 1,
    gap: 'md',
  },
});
