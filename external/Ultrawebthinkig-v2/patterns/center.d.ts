/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface CenterProperties {
   inline?: ConditionalValue<boolean>
}

interface CenterStyles extends CenterProperties, Omit<Record<string, any>, keyof CenterProperties > {}

interface CenterPatternFn {
  (styles?: CenterStyles): string
  raw: (styles?: CenterStyles) => Record<string, any>
}


export declare const center: CenterPatternFn;
