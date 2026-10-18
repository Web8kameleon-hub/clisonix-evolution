/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface LinkOverlayProperties {
   
}

interface LinkOverlayStyles extends LinkOverlayProperties, Omit<Record<string, any>, keyof LinkOverlayProperties > {}

interface LinkOverlayPatternFn {
  (styles?: LinkOverlayStyles): string
  raw: (styles?: LinkOverlayStyles) => Record<string, any>
}


export declare const linkOverlay: LinkOverlayPatternFn;
