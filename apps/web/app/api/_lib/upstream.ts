export type UpstreamGroup = "api" | "reporting";

function normalizeBaseUrl(value?: string | null) {
  return value?.trim().replace(/\/+$/, "") || null;
}

function unique(values: Array<string | null | undefined>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}

export function getUpstreamCandidates(group: UpstreamGroup) {
  const apiInternal = normalizeBaseUrl(process.env.API_INTERNAL_URL);
  const reportingInternal = normalizeBaseUrl(process.env.REPORTING_INTERNAL_URL);
  const publicApi = normalizeBaseUrl(process.env.NEXT_PUBLIC_API_URL);
  const publicReporting = normalizeBaseUrl(
    process.env.NEXT_PUBLIC_REPORTING_URL,
  );

  if (group === "reporting") {
    return unique([
      reportingInternal,
      publicReporting,
      apiInternal,
      publicApi,
    ]);
  }

  return unique([apiInternal, publicApi]);
}

interface FetchFromCandidatesOptions {
  group: UpstreamGroup;
  path: string;
  headers?: HeadersInit;
  init?: RequestInit;
  timeoutMs?: number;
}

interface FetchFromCandidatesResult {
  response: Response;
  source: string;
}

export async function fetchFromCandidates({
  group,
  path,
  headers,
  init,
  timeoutMs = 5000,
}: FetchFromCandidatesOptions): Promise<FetchFromCandidatesResult> {
  const candidates = getUpstreamCandidates(group);
  if (candidates.length === 0) {
    throw new Error(
      group === "reporting"
        ? "Missing upstream config: set REPORTING_INTERNAL_URL or API_INTERNAL_URL"
        : "Missing upstream config: set API_INTERNAL_URL",
    );
  }

  let lastError = `No source responded for ${path}`;

  for (const base of candidates) {
    const source = `${base}${path}`;

    try {
      const internalKey = process.env.KITCHEN_RUN_API_KEY ?? "";
      const response = await fetch(source, {
        cache: "no-store",
        ...init,
        headers: {
          Accept: "application/json",
          ...(internalKey ? { "X-Internal-Service": internalKey } : {}),
          ...(headers || {}),
          ...(init?.headers || {}),
        },
        signal: AbortSignal.timeout(timeoutMs),
      });

      if (!response.ok) {
        lastError = `${source} -> ${response.status}`;
        continue;
      }

      return { response, source };
    } catch (error) {
      lastError = `${source} -> ${error instanceof Error ? error.message : "unknown error"}`;
    }
  }

  throw new Error(lastError);
}

export async function fetchJsonFromCandidates<T = unknown>(
  options: FetchFromCandidatesOptions,
): Promise<{ data: T; source: string }> {
  const { response, source } = await fetchFromCandidates(options);

  try {
    const data = (await response.json()) as T;
    return { data, source };
  } catch {
    throw new Error(`${source} -> invalid JSON payload`);
  }
}

export async function fetchArrayBufferFromCandidates(
  options: FetchFromCandidatesOptions,
): Promise<{ data: ArrayBuffer; source: string; contentType: string | null }> {
  const { response, source } = await fetchFromCandidates(options);
  const data = await response.arrayBuffer();

  return {
    data,
    source,
    contentType: response.headers.get("content-type"),
  };
}
