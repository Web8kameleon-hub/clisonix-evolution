/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface AspectRatioProperties {
   ratio?: ConditionalValue<number>
}

interface AspectRatioStyles extends AspectRatioProperties, Omit<Record<string, any>, keyof AspectRatioProperties | 'aspectRatio'> {}

interface AspectRatioPatternFn {
  (styles?: AspectRatioStyles): string
  raw: (styles?: AspectRatioStyles) => Record<string, any>
}


export declare const aspectRatio: AspectRatioPatternFn;
