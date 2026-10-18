/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface ContainerProperties {
   
}

interface ContainerStyles extends ContainerProperties, Omit<Record<string, any>, keyof ContainerProperties > {}

interface ContainerPatternFn {
  (styles?: ContainerStyles): string
  raw: (styles?: ContainerStyles) => Record<string, any>
}


export declare const container: ContainerPatternFn;
