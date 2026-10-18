/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface VisuallyHiddenProperties {
   
}

interface VisuallyHiddenStyles extends VisuallyHiddenProperties, Omit<Record<string, any>, keyof VisuallyHiddenProperties > {}

interface VisuallyHiddenPatternFn {
  (styles?: VisuallyHiddenStyles): string
  raw: (styles?: VisuallyHiddenStyles) => Record<string, any>
}


export declare const visuallyHidden: VisuallyHiddenPatternFn;
