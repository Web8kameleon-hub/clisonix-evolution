import { NextRequest, NextResponse } from "next/server";

const OCEAN_BASE_URL =
  process.env.OCEAN_INTERNAL_URL ||
  process.env.OCEAN_CORE_URL ||
  "http://clisonix-ocean-core:8030";

function buildTargetUrl(path: string[], search: string): string {
  const cleanPath = path.join("/").replace(/^\/+/, "");
  const first = path[0]?.toLowerCase();
  const isAbsolutePath =
    first === "api" ||
    first === "health" ||
    first === "status" ||
    first === "docs" ||
    first === "openapi.json";

  const upstreamPath = isAbsolutePath
    ? `/${cleanPath}`
    : `/api/v1/${cleanPath}`;

  return `${OCEAN_BASE_URL.replace(/\/+$/, "")}${upstreamPath}${search}`;
}

async function forward(request: NextRequest, path: string[]) {
  try {
    const targetUrl = buildTargetUrl(path, request.nextUrl.search);
    const method = request.method;

    const headers = new Headers();
    const incomingContentType = request.headers.get("content-type");
    const incomingAccept = request.headers.get("accept");
    const authorization = request.headers.get("authorization");

    if (incomingContentType) headers.set("content-type", incomingContentType);
    if (incomingAccept) headers.set("accept", incomingAccept);
    if (authorization) headers.set("authorization", authorization);

    const init: RequestInit = { method, headers, cache: "no-store" };

    if (!["GET", "HEAD"].includes(method)) {
      const body = await request.text();
      if (body) init.body = body;
    }

    const upstream = await fetch(targetUrl, init);

    const outHeaders = new Headers();
    const upstreamContentType = upstream.headers.get("content-type");
    if (upstreamContentType) outHeaders.set("content-type", upstreamContentType);

    const cacheControl = upstream.headers.get("cache-control");
    if (cacheControl) outHeaders.set("cache-control", cacheControl);

    if (upstream.body) {
      outHeaders.set("cache-control", "no-cache, no-transform");
      outHeaders.set("x-accel-buffering", "no");
      return new NextResponse(upstream.body, {
        status: upstream.status,
        headers: outHeaders,
      });
    }

    return new NextResponse(null, {
      status: upstream.status,
      headers: outHeaders,
    });
  } catch (error) {
    return NextResponse.json(
      {
        error: "Ocean upstream unavailable",
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 502 },
    );
  }
}

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

export async function GET(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return forward(request, path);
}

export async function POST(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return forward(request, path);
}

export async function PUT(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return forward(request, path);
}

export async function PATCH(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return forward(request, path);
}

export async function DELETE(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return forward(request, path);
}

export async function OPTIONS(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return forward(request, path);
}
