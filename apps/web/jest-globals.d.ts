import "@jest/globals";

declare global {
  namespace jest {
    interface Matchers<R, T = unknown> {
      toBeOneOf(expected: readonly T[]): R;
    }
  }
}

declare module "expect" {
  interface Matchers<R, T = unknown> {
    toBeOneOf(expected: readonly T[]): R;
  }

  interface AsymmetricMatchers {
    toBeOneOf(expected: readonly unknown[]): void;
  }
}

export {};
