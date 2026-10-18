import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

function getBackendOrigin() {
  const origin =
    process.env.ULTRA_BACKEND_ORIGIN || process.env.BACKEND_PROXY_URL;
  return origin ? origin.replace(/\/$/, "") : null;
}

async function proxy(request: NextRequest, pathSegments: string[]) {
  const backendOrigin = getBackendOrigin();

  if (!backendOrigin) {
    return Response.json(
      {
        error: "Ultra backend origin is not configured",
        code: "ULTRA_BACKEND_ORIGIN_MISSING",
      },
      { status: 503 },
    );
  }

  const upstreamUrl = new URL(`${backendOrigin}/${pathSegments.join("/")}`);
  request.nextUrl.searchParams.forEach((value, key) => {
    upstreamUrl.searchParams.append(key, value);
  });

  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.set("x-forwarded-host", request.headers.get("host") || "");
  headers.set("x-forwarded-proto", request.nextUrl.protocol.replace(":", ""));

  const init: RequestInit = {
    method: request.method,
    headers,
    redirect: "manual",
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = await request.arrayBuffer();
  }

  const upstreamResponse = await fetch(upstreamUrl, init);
  const responseHeaders = new Headers(upstreamResponse.headers);
  responseHeaders.set("x-ultra-backend-proxy", "vercel-edge");

  return new Response(upstreamResponse.body, {
    status: upstreamResponse.status,
    statusText: upstreamResponse.statusText,
    headers: responseHeaders,
  });
}

type RouteContext = {
  params: Promise<{
    path: string[];
  }>;
};

async function handler(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return proxy(request, path || []);
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
export const OPTIONS = handler;
export const HEAD = handler;
