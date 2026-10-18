/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface SquareProperties {
   size?: SystemProperties["width"]
}

interface SquareStyles extends SquareProperties, Omit<Record<string, any>, keyof SquareProperties > {}

interface SquarePatternFn {
  (styles?: SquareStyles): string
  raw: (styles?: SquareStyles) => Record<string, any>
}


export declare const square: SquarePatternFn;
