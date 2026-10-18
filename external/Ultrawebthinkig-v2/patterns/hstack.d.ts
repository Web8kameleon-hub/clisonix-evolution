/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface HstackProperties {
   justify?: SystemProperties["justifyContent"]
	gap?: string | number
}

interface HstackStyles extends HstackProperties, Omit<Record<string, any>, keyof HstackProperties > {}

interface HstackPatternFn {
  (styles?: HstackStyles): string
  raw: (styles?: HstackStyles) => Record<string, any>
}


export declare const hstack: HstackPatternFn;
