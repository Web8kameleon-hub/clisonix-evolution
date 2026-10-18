/**
 * 🍳 RECIPE TYPES - CVA RECIPE PATTERN TYPES
 * Type definitions for CVA recipe patterns and variants
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0-RECIPE
 * @license MIT
 */

// Simple utility types for recipes
export type DistributiveOmit<T, K extends keyof any> = T extends any
  ? Omit<T, K>
  : never;

export type VariantProps<T> = T extends (...args: unknown[]) => any
  ? Parameters<T>[0]
  : never;

// Base Recipe Configuration
export interface RecipeConfig<T extends Record<string, any> = Record<string, any>> {
  base?: string | string[];
  variants?: T;
  compoundVariants?: Array<{
    [K in keyof T]?: T[K] extends Record<string, any> 
      ? keyof T[K] 
      : T[K];
  } & {
    class?: string | string[];
    className?: string | string[];
  }>;
  defaultVariants?: {
    [K in keyof T]?: T[K] extends Record<string, any> 
      ? keyof T[K] 
      : T[K];
  };
}

// Recipe Function Type
export interface Recipe<T extends Record<string, any> = Record<string, any>> {
  (props?: RecipeProps<T>): string;
  variants: T;
  config: RecipeConfig<T>;
}

// Recipe Props Type
export type RecipeProps<T extends Record<string, any>> = {
  [K in keyof T]?: T[K] extends Record<string, any> 
    ? keyof T[K] 
    : T[K];
};

// Slot Recipe for Multi-part Components
export interface SlotRecipeConfig<S extends Record<string, any> = Record<string, any>, T extends Record<string, any> = Record<string, any>> {
  slots: S;
  base?: {
    [K in keyof S]?: string | string[];
  };
  variants?: T;
  compoundVariants?: Array<{
    [K in keyof T]?: T[K] extends Record<string, any> 
      ? keyof T[K] 
      : T[K];
  } & {
    class?: {
      [K in keyof S]?: string | string[];
    };
    className?: {
      [K in keyof S]?: string | string[];
    };
  }>;
  defaultVariants?: {
    [K in keyof T]?: T[K] extends Record<string, any> 
      ? keyof T[K] 
      : T[K];
  };
}

export interface SlotRecipe<S extends Record<string, any> = Record<string, any>, T extends Record<string, any> = Record<string, any>> {
  (props?: SlotRecipeProps<T>): {
    [K in keyof S]: string;
  };
  slots: S;
  variants: T;
  config: SlotRecipeConfig<S, T>;
}

// Slot Recipe Props Type
export type SlotRecipeProps<T extends Record<string, any>> = {
  [K in keyof T]?: T[K] extends Record<string, any> 
    ? keyof T[K] 
    : T[K];
};

// Common Recipe Variants
export interface CommonVariants {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
  intent?: 'primary' | 'secondary' | 'accent' | 'neutral' | 'destructive';
  state?: 'idle' | 'loading' | 'success' | 'error' | 'disabled';
  visual?: 'solid' | 'outline' | 'ghost' | 'link';
  placement?: 'top' | 'right' | 'bottom' | 'left';
  orientation?: 'horizontal' | 'vertical';
}

// Utility Types for Recipes
export type RecipeVariants<T> = T extends Recipe<infer V> ? V : never;
export type RecipeVariantProps<T> = T extends Recipe<any> ? VariantProps<T> : never;

// Neural Component Variants
export interface NeuralVariants {
  activity?: 'low' | 'medium' | 'high' | 'critical';
  pulse?: 'slow' | 'normal' | 'fast' | 'flickering';
  status?: 'active' | 'throttled' | 'safethink' | 'offline';
  node?: 'input' | 'processing' | 'output' | 'ethical' | 'decision';
}

// Motion Component Variants
export interface MotionVariants {
  animation?: 'fade' | 'slide' | 'scale' | 'rotate' | 'bounce';
  duration?: 'fast' | 'normal' | 'slow' | 'slower';
  easing?: 'linear' | 'easeIn' | 'easeOut' | 'easeInOut';
  direction?: 'up' | 'down' | 'left' | 'right';
}
