import { NextResponse } from 'next/server';

const API_CONTRACT_VERSION = '2026-03-v1';

type MetaValue = string | number | boolean | null | Record<string, unknown> | Array<unknown>;

export interface ApiMeta {
  timestamp: string;
  version: string;
  requestId?: string;
  [key: string]: MetaValue | undefined;
}

export interface ApiErrorBody {
  code: string;
  message: string;
  details?: unknown;
}

interface ApiResponseOptions {
  status?: number;
  meta?: Omit<ApiMeta, 'timestamp' | 'version'>;
  headers?: HeadersInit;
}

interface ApiErrorOptions extends ApiResponseOptions {
  details?: unknown;
}

function buildMeta(meta?: Omit<ApiMeta, 'timestamp' | 'version'>): ApiMeta {
  return {
    timestamp: new Date().toISOString(),
    version: API_CONTRACT_VERSION,
    ...(meta ?? {}),
  };
}

export function apiSuccess<T>(
  data: T,
  options: ApiResponseOptions = {},
) {
  const { status = 200, meta, headers } = options;
  return NextResponse.json(
    {
      success: true,
      data,
      meta: buildMeta(meta),
    },
    { status, headers },
  );
}

export function apiError(
  code: string,
  message: string,
  options: ApiErrorOptions = {},
) {
  const { status = 500, meta, details, headers } = options;
  return NextResponse.json(
    {
      success: false,
      error: {
        code,
        message,
        ...(details !== undefined ? { details } : {}),
      },
      meta: buildMeta(meta),
    },
    { status, headers },
  );
}

export function apiDegraded<T>(
  data: T,
  code: string,
  message: string,
  options: ApiErrorOptions = {},
) {
  const { status = 200, meta, details, headers } = options;
  return NextResponse.json(
    {
      success: false,
      data,
      error: {
        code,
        message,
        ...(details !== undefined ? { details } : {}),
      },
      meta: buildMeta({
        degraded: true,
        ...(meta ?? {}),
      }),
    },
    { status, headers },
  );
}
