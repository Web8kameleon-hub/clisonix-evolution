/* eslint-disable */
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface FlexProperties {
   align?: SystemProperties["alignItems"]
	justify?: SystemProperties["justifyContent"]
	direction?: SystemProperties["flexDirection"]
	wrap?: SystemProperties["flexWrap"]
	basis?: SystemProperties["flexBasis"]
	grow?: SystemProperties["flexGrow"]
	shrink?: SystemProperties["flexShrink"]
}

interface FlexStyles extends FlexProperties, Omit<Record<string, any>, keyof FlexProperties > {}

interface FlexPatternFn {
  (styles?: FlexStyles): string
  raw: (styles?: FlexStyles) => Record<string, any>
}


export declare const flex: FlexPatternFn;
