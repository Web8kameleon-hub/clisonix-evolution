/**
 * 🔧 SYSTEM TYPES - UTILITY TYPES FOR STYLING SYSTEMS
 * Advanced TypeScript utility types for CVA and styling
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0-SYSTEM-TYPES
 * @license MIT
 */

// Utility Types for CVA and Styling
export type DistributiveOmit<T, K extends keyof any> = T extends any
  ? Omit<T, K>
  : never;

export type StringLiteral<T> = T extends string
  ? string extends T
    ? never
    : T
  : never;

export type Pretty<T> = {
  [K in keyof T]: T[K];
} & {};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? never : K;
}[keyof T];

export type OptionalKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? K : never;
}[keyof T];

export type PickRequired<T> = Pick<T, RequiredKeys<T>>;
export type PickOptional<T> = Pick<T, OptionalKeys<T>>;

export type Expand<T> = T extends (...args: infer A) => infer R
  ? (...args: Expand<A>) => Expand<R>
  : T extends infer O
  ? { [K in keyof O]: O[K] }
  : never;

export type ExpandDeep<T> = T extends (...args: infer A) => infer R
  ? (...args: ExpandDeep<A>) => ExpandDeep<R>
  : T extends object
  ? T extends infer O
    ? { [K in keyof O]: ExpandDeep<O[K]> }
    : never
  : T;

// Style Value Types
export type StyleValue = string | number | boolean | undefined | null;

export type ResponsiveValue<T> = T | {
  base?: T;
  sm?: T;
  md?: T;
  lg?: T;
  xl?: T;
  '2xl'?: T;
};

export type ConditionalValue<T> = T | ResponsiveValue<T>;

export type SystemStyleObject = {
  [property: string]: StyleValue | ResponsiveValue<StyleValue>;
};

// CVA Variant Types
export type VariantProps<T> = T extends (...args: unknown[]) => any
  ? Parameters<T>[0]
  : never;

export type ClassValue = string | number | boolean | undefined | null;

export type ClassArray = ClassValue[];

export type ClassDictionary = Record<string, any>;

export type ClassNameValue = ClassValue | ClassArray | ClassDictionary;
