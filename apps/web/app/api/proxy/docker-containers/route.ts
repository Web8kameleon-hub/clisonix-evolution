import { NextResponse } from 'next/server'

const REPORTING_PATH = "/api/reporting/docker-containers";
const DEFAULT_API_BASE =
  process.env.NODE_ENV === "production"
    ? "http://clisonix-api:8000"
    : "http://127.0.0.1:8000";
const DEFAULT_REPORTING_BASE =
  process.env.NODE_ENV === "production"
    ? "http://clisonix-reporting:8001"
    : "http://127.0.0.1:8001";

function normalizeBaseUrl(value?: string | null) {
  return value?.trim().replace(/\/+$/, "") || null;
}

const API_CANDIDATES = Array.from(
  new Set(
    [
      normalizeBaseUrl(process.env.API_INTERNAL_URL),
      normalizeBaseUrl(process.env.REPORTING_INTERNAL_URL),
      DEFAULT_API_BASE,
      DEFAULT_REPORTING_BASE,
      process.env.NODE_ENV === "production" ? "http://localhost:8000" : null,
      process.env.NODE_ENV === "production" ? "http://localhost:8001" : null,
    ].filter((value): value is string => Boolean(value)),
  ),
);

async function fetchDockerContainers() {
  let lastError = "No docker container source responded";

  for (const base of API_CANDIDATES) {
    const target = `${base}${REPORTING_PATH}`;

    try {
      const response = await fetch(target, {
        cache: "no-store",
        headers: { Accept: "application/json" },
        next: { revalidate: 0 },
      });

      if (!response.ok) {
        lastError = `${target} -> ${response.status}`;
        continue;
      }

      const data = await response.json();
      if (
        typeof data?.running === "number" ||
        Array.isArray(data?.containers)
      ) {
        return { data, source: target };
      }

      lastError = `${target} -> invalid payload`;
    } catch (error) {
      lastError = `${target} -> ${error instanceof Error ? error.message : "unknown error"}`;
    }
  }

  throw new Error(lastError);
}

export async function GET() {
  try {
    const { data, source } = await fetchDockerContainers();
    return NextResponse.json({ ...data, source }, { status: 200 });
  } catch (error) {
    console.error("Docker containers fetch error:", error);
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "unknown error",
      },
      { status: 503 },
    );
  }
}
