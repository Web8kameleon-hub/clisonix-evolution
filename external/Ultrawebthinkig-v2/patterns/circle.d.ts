/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface CircleProperties {
   size?: SystemProperties["width"]
}

interface CircleStyles extends CircleProperties, Omit<Record<string, any>, keyof CircleProperties > {}

interface CirclePatternFn {
  (styles?: CircleStyles): string
  raw: (styles?: CircleStyles) => Record<string, any>
}


export declare const circle: CirclePatternFn;
