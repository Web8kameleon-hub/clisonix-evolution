import { NextRequest } from "next/server";

const PRIMARY_OCEAN_URL = process.env.OCEAN_API_URL;
const OCEAN_INTERNAL_URL = process.env.OCEAN_INTERNAL_URL;
const INTERNAL_OCEAN_URL = "http://clisonix-ocean-core:8030";
const SERVICE_OCEAN_URL = "http://ocean-core:8030";
const LOCAL_OCEAN_URL = "http://localhost:8030";

function buildUpstreamCandidates(): string[] {
  return [
    OCEAN_INTERNAL_URL,
    INTERNAL_OCEAN_URL,
    SERVICE_OCEAN_URL,
    PRIMARY_OCEAN_URL,
    LOCAL_OCEAN_URL,
  ]
    .filter((url): url is string => Boolean(url && url.trim()))
    .map((url) => url.replace(/\/+$/, ""));
}

/**
 * Web Reader Stream Proxy - SSE streaming for chat with webpage
 * POST /api/ocean/web-reader/stream
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { url, message } = body;

    if (!url || !message) {
      return new Response(
        JSON.stringify({ error: '"url" and "message" are required' }),
        { status: 400, headers: { "Content-Type": "application/json" } },
      );
    }

    // Proxy to Ocean Core streaming endpoint across upstream candidates
    const candidates = buildUpstreamCandidates();
    let upstream: Response | null = null;
    let lastError = "No upstream candidates configured";

    for (const base of candidates) {
      try {
        const res = await fetch(`${base}/api/v1/chat/browse/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url, message }),
        });

        if (res.ok && res.body) {
          upstream = res;
          break;
        }

        lastError = `Ocean Core error ${res.status} via ${base}`;
      } catch (error) {
        lastError =
          error instanceof Error ? error.message : "Unknown upstream error";
      }
    }

    if (!upstream || !upstream.body) {
      return new Response(
        JSON.stringify({ error: `Ocean Core unavailable: ${lastError}` }),
        { status: 502, headers: { "Content-Type": "application/json" } },
      );
    }

    if (upstream && upstream.body) {
      const contentType = (
        upstream.headers.get("content-type") || ""
      ).toLowerCase();
      const isSSE = contentType.includes("text/event-stream");

      if (isSSE) {
        return new Response(upstream.body, {
          headers: {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            Connection: "keep-alive",
          },
        });
      }
    }

    return new Response(
      JSON.stringify({ error: `Ocean Core stream unavailable: ${lastError}` }),
      { status: 502, headers: { "Content-Type": "application/json" } },
    );
  } catch (error) {
    console.error("[web-reader/stream] proxy error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to connect to Ocean Core" }),
      { status: 502, headers: { "Content-Type": "application/json" } },
    );
  }
}
