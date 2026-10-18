 
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface GridProperties {
   gap?: string | number
	columnGap?: string | number
	rowGap?: string | number
	columns?: ConditionalValue<number>
	minChildWidth?: ConditionalValue<Tokens["sizes"] | Properties["width"]>
}

interface GridStyles extends GridProperties, Omit<Record<string, any>, keyof GridProperties > {}

interface GridPatternFn {
  (styles?: GridStyles): string
  raw: (styles?: GridStyles) => Record<string, any>
}


export declare const grid: GridPatternFn;
