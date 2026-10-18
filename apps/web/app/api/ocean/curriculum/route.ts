import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const ALBA_INTERNAL_URL = process.env.ALBA_INTERNAL_URL;
const ALBA_URL = process.env.ALBA_URL;
const ALBA_LOCAL_URL = "http://localhost:5555";
const ALBA_CONTAINER_URL = "http://clisonix-alba:5555";

function buildAlbaCandidates(): string[] {
  const ordered = [
    ALBA_INTERNAL_URL,
    ALBA_URL,
    ALBA_CONTAINER_URL,
    ALBA_LOCAL_URL,
  ]
    .filter((url): url is string => Boolean(url && url.trim()))
    .map((url) => url.replace(/\/+$/, ""));

  return [...new Set(ordered)];
}

async function fetchFirstHealthy(
  path: string,
  init: RequestInit,
): Promise<Response> {
  const candidates = buildAlbaCandidates();
  let lastError: string | null = null;

  for (const base of candidates) {
    try {
      const response = await fetch(`${base}${path}`, {
        ...init,
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

  throw new Error(lastError || "ALBA curriculum upstream unavailable");
}

function getHeaders(request: NextRequest): Headers {
  const headers = new Headers({
    "Content-Type": "application/json",
    Accept: "application/json",
  });

  const auth = request.headers.get("authorization");
  if (auth) {
    headers.set("authorization", auth);
  }

  return headers;
}

export async function GET(request: NextRequest) {
  try {
    const action = request.nextUrl.searchParams.get("action") || "status";
    const limit = request.nextUrl.searchParams.get("limit") || "100";
    const challengeId = request.nextUrl.searchParams.get("challenge_id") || "";
    const tier = request.nextUrl.searchParams.get("tier") || "validated";

    let path = "/gs26/curriculum/status";
    if (action === "challenge") {
      if (!challengeId.trim()) {
        return NextResponse.json(
          { error: "challenge_id is required for action=challenge" },
          { status: 400 },
        );
      }
      path = `/gs26/curriculum/challenges/${encodeURIComponent(challengeId)}`;
    } else if (action === "memory") {
      path = `/gs26/curriculum/memory/${encodeURIComponent(tier)}?limit=${encodeURIComponent(limit)}`;
    }

    const response = await fetchFirstHealthy(path, {
      method: "GET",
      headers: getHeaders(request),
    });

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
        error: "curriculum_upstream_unavailable",
        message: error instanceof Error ? error.message : String(error),
      },
      { status: 502 },
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json().catch(() => ({}))) as Record<string, unknown>;
    const action = String(body.action || "submit").toLowerCase().trim();

    if (action !== "submit") {
      return NextResponse.json(
        { error: "unsupported_action", supported: ["submit"] },
        { status: 400 },
      );
    }

    const payload = {
      challenge_id: body.challenge_id,
      topic: body.topic,
      difficulty: body.difficulty,
      claims: body.claims,
    };

    const response = await fetchFirstHealthy("/gs26/curriculum/challenges", {
      method: "POST",
      headers: getHeaders(request),
      body: JSON.stringify(payload),
    });

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
        error: "curriculum_submit_failed",
        message: error instanceof Error ? error.message : String(error),
      },
      { status: 502 },
    );
  }
}
