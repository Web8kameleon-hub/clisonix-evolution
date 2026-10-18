/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface FloatProperties {
   offsetX?: ConditionalValue<Tokens["spacing"] | Properties["left"]>
	offsetY?: ConditionalValue<Tokens["spacing"] | Properties["top"]>
	offset?: ConditionalValue<Tokens["spacing"] | Properties["top"]>
	placement?: ConditionalValue<"bottom-end" | "bottom-start" | "top-end" | "top-start" | "bottom-center" | "top-center" | "middle-center" | "middle-end" | "middle-start">
}

interface FloatStyles extends FloatProperties, Omit<Record<string, any>, keyof FloatProperties > {}

interface FloatPatternFn {
  (styles?: FloatStyles): string
  raw: (styles?: FloatStyles) => Record<string, any>
}


export declare const float: FloatPatternFn;
