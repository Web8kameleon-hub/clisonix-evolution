 
// Simplified: removed system-styles dependency
import type { Properties } from '../types/csstype';
// Simplified: removed system-styles dependency
// Simplified: removed system-styles dependency
import type { Tokens } from '../tokens/index';

export interface CqProperties {
   name?: ConditionalValue<Tokens["containerNames"] | Properties["containerName"]>
	type?: SystemProperties["containerType"]
}

interface CqStyles extends CqProperties, Omit<Record<string, any>, keyof CqProperties > {}

interface CqPatternFn {
  (styles?: CqStyles): string
  raw: (styles?: CqStyles) => Record<string, any>
}


export declare const cq: CqPatternFn;
