/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface BleedProperties {
   inline?: SystemProperties["marginInline"]
	block?: SystemProperties["marginBlock"]
}

interface BleedStyles extends BleedProperties, Omit<Record<string, any>, keyof BleedProperties > {}

interface BleedPatternFn {
  (styles?: BleedStyles): string
  raw: (styles?: BleedStyles) => Record<string, any>
}


export declare const bleed: BleedPatternFn;
