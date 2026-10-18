import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const CURIOSITY_OCEAN_URL = process.env.CURIOSITY_OCEAN_URL;
const CURIOSITY_INTERNAL_URL = process.env.CURIOSITY_INTERNAL_URL;
const CURIOSITY_CONTAINER_URL = "http://clisonix-curiosity-ocean:8031";
const CURIOSITY_LOCAL_URL = "http://localhost:8031";

function buildCuriosityCandidates(): string[] {
  const ordered = [
    CURIOSITY_OCEAN_URL,
    CURIOSITY_INTERNAL_URL,
    CURIOSITY_CONTAINER_URL,
    CURIOSITY_LOCAL_URL,
  ]
    .filter((url): url is string => Boolean(url && url.trim()))
    .map((url) => url.replace(/\/+$/, ""));

  return [...new Set(ordered)];
}

async function callManifestValidator(
  body: Record<string, unknown>,
  authHeader: string | null,
): Promise<Response> {
  const candidates = buildCuriosityCandidates();
  let lastError: string | null = null;

  for (const base of candidates) {
    try {
      const headers = new Headers({
        "Content-Type": "application/json",
        Accept: "application/json",
      });
      if (authHeader) {
        headers.set("authorization", authHeader);
      }

      const response = await fetch(`${base}/ocean/manifest/validate`, {
        method: "POST",
        headers,
        body: JSON.stringify(body),
        cache: "no-store",
      });

      if (response.ok || response.status < 500) {
        return response;
      }

      lastError = `upstream ${base} failed with ${response.status}`;
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
    }
  }

  throw new Error(lastError || "manifest validator upstream unavailable");
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json().catch(() => ({}))) as Record<string, unknown>;
    const auth = request.headers.get("authorization");

    const response = await callManifestValidator(body, auth);
    const text = await response.text();

    let data: unknown = text;
    try {
      data = text ? (JSON.parse(text) as unknown) : null;
    } catch {
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        error: "manifest_validator_unavailable",
        message: error instanceof Error ? error.message : String(error),
      },
      { status: 502 },
    );
  }
}
