/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface SpacerProperties {
   size?: ConditionalValue<Tokens["spacing"]>
}

interface SpacerStyles extends SpacerProperties, Omit<Record<string, any>, keyof SpacerProperties > {}

interface SpacerPatternFn {
  (styles?: SpacerStyles): string
  raw: (styles?: SpacerStyles) => Record<string, any>
}


export declare const spacer: SpacerPatternFn;
