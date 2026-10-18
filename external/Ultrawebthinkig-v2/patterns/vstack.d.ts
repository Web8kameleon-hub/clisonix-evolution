/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface VstackProperties {
   justify?: SystemProperties["justifyContent"]
	gap?: string | number
}

interface VstackStyles extends VstackProperties, Omit<Record<string, any>, keyof VstackProperties > {}

interface VstackPatternFn {
  (styles?: VstackStyles): string
  raw: (styles?: VstackStyles) => Record<string, any>
}


export declare const vstack: VstackPatternFn;
