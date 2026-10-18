/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface StackProperties {
   align?: SystemProperties["alignItems"]
	justify?: SystemProperties["justifyContent"]
	direction?: SystemProperties["flexDirection"]
	gap?: string | number
}

interface StackStyles extends StackProperties, Omit<Record<string, any>, keyof StackProperties > {}

interface StackPatternFn {
  (styles?: StackStyles): string
  raw: (styles?: StackStyles) => Record<string, any>
}


export declare const stack: StackPatternFn;
