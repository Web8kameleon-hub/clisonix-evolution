/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface WrapProperties {
   gap?: string | number
	rowGap?: string | number
	columnGap?: string | number
	align?: SystemProperties["alignItems"]
	justify?: SystemProperties["justifyContent"]
}

interface WrapStyles extends WrapProperties, Omit<Record<string, any>, keyof WrapProperties > {}

interface WrapPatternFn {
  (styles?: WrapStyles): string
  raw: (styles?: WrapStyles) => Record<string, any>
}


export declare const wrap: WrapPatternFn;
