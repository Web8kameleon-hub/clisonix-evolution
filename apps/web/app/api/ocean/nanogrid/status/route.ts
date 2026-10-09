import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const NANOGRID_INTERNAL_URL =
  process.env.NANOGRID_INTERNAL_URL || "http://clisonix-nanogrid-zeiss:8043";
const OCEAN_MULTIMODAL_INTERNAL_URL =
  process.env.OCEAN_MULTIMODAL_INTERNAL_URL ||
  "http://clisonix-ocean-core-multimodal:8033";
const OCEAN_INTERNAL_URL =
  process.env.OCEAN_INTERNAL_URL || "http://clisonix-ocean-core:8030";

function normalizeBase(url: string): string {
  return (url || "").trim().replace(/\/+$/, "");
}

async function fetchJson(
  url: string,
): Promise<{
  ok: boolean;
  status: number;
  data: Record<string, unknown> | null;
  text: string;
}> {
  try {
    const response = await fetch(url, {
      method: "GET",
      cache: "no-store",
      headers: { Accept: "application/json" },
    });

    const text = await response.text();
    let data: Record<string, unknown> | null = null;
    try {
      const parsed = JSON.parse(text) as unknown;
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
        data = parsed as Record<string, unknown>;
      }
    } catch {}

    return { ok: response.ok, status: response.status, data, text };
  } catch (error) {
    return {
      ok: false,
      status: 503,
      data: null,
      text: error instanceof Error ? error.message : String(error),
    };
  }
}

export async function GET() {
  try {
    const nanogridBases = [
      normalizeBase(NANOGRID_INTERNAL_URL),
      normalizeBase(OCEAN_MULTIMODAL_INTERNAL_URL),
    ].filter(
      (value, index, list) => Boolean(value) && list.indexOf(value) === index,
    );
    const oceanBase = normalizeBase(OCEAN_INTERNAL_URL);

    let lastDirect: {
      status: number;
      text: string;
      detail?: string;
    } = { status: 503, text: "NanoGrid ZEISS status unavailable" };

    for (const base of nanogridBases) {
      const direct = await fetchJson(`${base}/api/v1/nanogrid/status`);
      if (direct.ok) {
        return NextResponse.json(
          {
            available: true,
            route: "nanogrid-direct",
            source: base,
            ...(direct.data || {}),
          },
          { status: 200 },
        );
      }

      const health = await fetchJson(`${base}/health`);
      if (health.ok) {
        return NextResponse.json(
          {
            available: true,
            route: "nanogrid-health",
            source: base,
            detail: "NanoGrid upstream healthy; status endpoint unavailable",
          },
          { status: 200 },
        );
      }

      lastDirect = {
        status: direct.status || health.status,
        text: direct.text || health.text,
        detail:
          (direct.data?.detail as string) ||
          (health.data?.detail as string) ||
          undefined,
      };
    }

    const oceanFallback = await fetchJson(
      `${oceanBase}/api/v1/nanogrid/status`,
    );
    if (oceanFallback.ok) {
      return NextResponse.json(
        {
          available: true,
          route: "ocean-fallback",
          ...(oceanFallback.data || {}),
        },
        { status: 200 },
      );
    }

    return NextResponse.json(
      {
        available: false,
        status: "unavailable",
        direct_status: lastDirect.status,
        fallback_status: oceanFallback.status,
        detail:
          lastDirect.detail ||
          (oceanFallback.data?.detail as string) ||
          lastDirect.text ||
          oceanFallback.text ||
          "NanoGrid ZEISS status unavailable",
      },
      { status: 503 },
    );
  } catch (error) {
    return NextResponse.json(
      {
        available: false,
        status: "error",
        detail: error instanceof Error ? error.message : String(error),
      },
      { status: 503 },
    );
  }
}
