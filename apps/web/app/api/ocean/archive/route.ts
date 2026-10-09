import { NextRequest, NextResponse } from "next/server";

const OCEAN_CORE = process.env.OCEAN_API_URL || "http://ocean-core:8030";

/**
 * Archive / Research Proxy — Scientific papers, Wikipedia, data sources
 *
 * GET /api/ocean/archive?action=arxiv&q=...
 * GET /api/ocean/archive?action=wiki&q=...
 * GET /api/ocean/archive?action=pubmed&q=...
 * GET /api/ocean/archive?action=sources
 * POST /api/ocean/archive { action: 'multi-search', query: '...' }
 */

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get("action") || "arxiv";
    const q = searchParams.get("q") || "";
    const limit = searchParams.get("limit") || "10";

    let endpoint = "";

    switch (action) {
      case "arxiv":
        if (!q) {
          return NextResponse.json(
            { error: 'Query parameter "q" is required' },
            { status: 400 },
          );
        }
        endpoint = `${OCEAN_CORE}/api/v1/arxiv/${encodeURIComponent(q)}?max_results=${limit}`;
        break;

      case "wiki":
        if (!q) {
          return NextResponse.json(
            { error: 'Query parameter "q" is required' },
            { status: 400 },
          );
        }
        endpoint = `${OCEAN_CORE}/api/v1/wiki/${encodeURIComponent(q)}?limit=${limit}`;
        break;

      case "pubmed":
        if (!q) {
          return NextResponse.json(
            { error: 'Query parameter "q" is required' },
            { status: 400 },
          );
        }
        endpoint = `${OCEAN_CORE}/api/v1/pubmed/${encodeURIComponent(q)}?max_results=${limit}`;
        break;

      case "sources":
        endpoint = `${OCEAN_CORE}/api/v1/sources`;
        break;

      case "github": {
        const owner = searchParams.get("owner") || "";
        const repo = searchParams.get("repo") || "";
        if (!owner || !repo) {
          return NextResponse.json(
            { error: '"owner" and "repo" are required' },
            { status: 400 },
          );
        }
        endpoint = `${OCEAN_CORE}/api/v1/github/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}`;
        break;
      }

      default:
        return NextResponse.json(
          { error: `Unknown action: ${action}` },
          { status: 400 },
        );
    }

    const upstream = await fetch(endpoint, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!upstream.ok) {
      const errorText = await upstream.text();
      console.error(
        `[archive] Ocean Core error: ${upstream.status}`,
        errorText,
      );
      throw new Error(`Ocean Core responded with ${upstream.status}`);
    }

    const data = await upstream.json();
    return NextResponse.json({ success: true, action, data });
  } catch (error) {
    console.error("[archive] proxy error:", error);
    return NextResponse.json(
      { success: false, error: "Failed to connect to Ocean Core" },
      { status: 502 },
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, query } = body;

    if (action === "multi-search" && query) {
      // Search across multiple sources simultaneously
      const [arxiv, wiki, pubmed] = await Promise.allSettled([
        fetch(
          `${OCEAN_CORE}/api/v1/arxiv/${encodeURIComponent(query)}?max_results=5`,
          { cache: "no-store" },
        ).then((r) => r.json()),
        fetch(
          `${OCEAN_CORE}/api/v1/wiki/${encodeURIComponent(query)}?limit=5`,
          { cache: "no-store" },
        ).then((r) => r.json()),
        fetch(
          `${OCEAN_CORE}/api/v1/pubmed/${encodeURIComponent(query)}?max_results=5`,
          { cache: "no-store" },
        ).then((r) => r.json()),
      ]);

      return NextResponse.json({
        success: true,
        action: "multi-search",
        query,
        results: {
          arxiv: arxiv.status === "fulfilled" ? arxiv.value : null,
          wikipedia: wiki.status === "fulfilled" ? wiki.value : null,
          pubmed: pubmed.status === "fulfilled" ? pubmed.value : null,
        },
      });
    }

    return NextResponse.json(
      { error: "Unknown action or missing query" },
      { status: 400 },
    );
  } catch (error) {
    console.error("[archive] POST proxy error:", error);
    return NextResponse.json(
      { success: false, error: "Failed to connect to Ocean Core" },
      { status: 502 },
    );
  }
}
