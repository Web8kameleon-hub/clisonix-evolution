import { NextRequest, NextResponse } from "next/server";

/**
 * Document Analysis API Proxy
 * Proxies document/analyze requests to Ocean-Core backend
 * This runs server-side so it can reach the internal Docker network
 */

const isDev = process.env.NODE_ENV !== "production";
const OCEAN_INTERNAL_URL =
  process.env.OCEAN_INTERNAL_URL || "http://clisonix-ocean-core:8030";
const OCEAN_CORE_URL = process.env.OCEAN_CORE_URL;
const OCEAN_LOCAL_URL = "http://localhost:8030";
const OCEAN_PUBLIC_URL = process.env.NEXT_PUBLIC_OCEAN_API_URL;

function resolveOceanUpstreams(): string[] {
  const candidates = [
    OCEAN_INTERNAL_URL,
    OCEAN_CORE_URL,
    isDev ? OCEAN_LOCAL_URL : undefined,
    OCEAN_PUBLIC_URL,
  ]
    .filter((url): url is string => Boolean(url && url.trim()))
    .map((url) => url.replace(/\/+$/, ""));

  const unique = [...new Set(candidates)];
  if (!unique.length) {
    throw new Error("Ocean document upstream is not configured");
  }
  return unique;
}

async function fetchOceanStrict(
  path: string,
  init: RequestInit,
): Promise<globalThis.Response> {
  const [upstream] = resolveOceanUpstreams();
  return await fetch(`${upstream}${path}`, init);
}

async function fetchOceanWithFallbacks(
  paths: string[],
  init: RequestInit,
): Promise<globalThis.Response> {
  let lastResponse: globalThis.Response | null = null;

  for (const upstream of resolveOceanUpstreams()) {
    for (const path of paths) {
      const response = await fetch(`${upstream}${path}`, init);
      lastResponse = response;
      if (response.status !== 404) {
        return response;
      }
    }
  }

  return (
    lastResponse ||
    new Response(JSON.stringify({ message: "Document upstream unavailable" }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    })
  );
}

async function decodeUpstreamPayload(
  response: globalThis.Response,
): Promise<Record<string, unknown>> {
  const contentType = (
    response.headers.get("content-type") || ""
  ).toLowerCase();

  if (contentType.includes("application/cbor")) {
    try {
      const { default: cbor } = await import("cbor");
      const raw = Buffer.from(await response.arrayBuffer());
      const decoded = cbor.decodeFirstSync(raw);
      if (decoded && typeof decoded === "object") {
        return decoded as Record<string, unknown>;
      }
    } catch {
      return {};
    }
    return {};
  }

  try {
    return (await response.json()) as Record<string, unknown>;
  } catch {
    return {};
  }
}

async function postOceanCborFirst(
  paths: string[],
  payload: Record<string, unknown>,
  userId?: string,
): Promise<globalThis.Response> {
  const { default: cbor } = await import("cbor");

  const cborHeaders: Record<string, string> = {
    "Content-Type": "application/cbor",
    Accept: "application/cbor, application/json",
  };

  if (userId) {
    cborHeaders["X-User-ID"] = userId;
    cborHeaders["X-User-Id"] = userId;
  }

  const cborResponse = await fetchOceanWithFallbacks(paths, {
    method: "POST",
    headers: cborHeaders,
    body: new Uint8Array(cbor.encode(payload)),
  });

  if (![400, 415, 422].includes(cborResponse.status)) {
    return cborResponse;
  }

  const jsonHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };

  if (userId) {
    jsonHeaders["X-User-ID"] = userId;
    jsonHeaders["X-User-Id"] = userId;
  }

  return fetchOceanWithFallbacks(paths, {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify(payload),
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const action =
      typeof body?.action === "string" ? body.action.toLowerCase() : "analyze";
    const docType = typeof body?.doc_type === "string" ? body.doc_type : "text";
    const encoding =
      typeof body?.encoding === "string" ? body.encoding : "text";
    const rawContent = typeof body?.content === "string" ? body.content : "";
    const contentBase64 =
      typeof body?.content_base64 === "string" ? body.content_base64 : "";
    const filename =
      typeof body?.filename === "string" ? body.filename : "upload.txt";
    const contentType =
      typeof body?.content_type === "string"
        ? body.content_type
        : "application/octet-stream";

    // Forward auth headers
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };
    const userId =
      request.headers.get("X-User-ID") || request.headers.get("X-User-Id");
    if (userId) {
      headers["X-User-ID"] = userId;
      headers["X-User-Id"] = userId;
    }

    let response: globalThis.Response;

    if (action === "capabilities") {
      response = await fetchOceanWithFallbacks(
        [`/api/v1/documents/capabilities`],
        {
          method: "GET",
          headers,
          cache: "no-store",
        },
      );
    } else if (action === "generate" || !!body?.query) {
      response = await postOceanCborFirst(
        [`/api/v1/documents/generate`],
        {
          query: body?.query || rawContent,
          format: body?.format || "xlsx",
          contract_type: body?.contract_type || "cpi",
          language: body?.language || "en",
        },
        userId || undefined,
      );
    } else if (action === "scan" || !!contentBase64) {
      if (!contentBase64) {
        return NextResponse.json(
          {
            status: "error",
            message: "Missing content_base64 for scan action.",
          },
          { status: 400 },
        );
      }

      let binary: Buffer;
      try {
        binary = Buffer.from(contentBase64, "base64");
      } catch {
        return NextResponse.json(
          {
            status: "error",
            message: "Invalid base64 content.",
          },
          { status: 400 },
        );
      }

      const form = new FormData();
      const blob = new Blob([new Uint8Array(binary)], { type: contentType });
      form.append("file", blob, filename);

      const qs = new URLSearchParams();
      if (body?.max_chars) {
        qs.set("max_chars", String(body.max_chars));
      }

      const scanPath = qs.toString()
        ? `/api/v1/documents/scan?${qs.toString()}`
        : `/api/v1/documents/scan`;
      const legacyScanPath = qs.toString()
        ? `/api/v1/document/scan?${qs.toString()}`
        : `/api/v1/document/scan`;

      const scanHeaders: Record<string, string> = {};
      if (userId) {
        scanHeaders["X-User-ID"] = userId;
        scanHeaders["X-User-Id"] = userId;
      }

      response = await fetchOceanWithFallbacks([scanPath, legacyScanPath], {
        method: "POST",
        headers: scanHeaders,
        body: form,
      });
    } else {
      if (!rawContent.trim()) {
        response = await fetchOceanWithFallbacks(
          [`/api/v1/documents/capabilities`],
          {
            method: "GET",
            headers,
            cache: "no-store",
          },
        );
      } else {
        let content = rawContent;
        if (encoding === "base64") {
          try {
            content = Buffer.from(rawContent, "base64").toString("utf-8");
          } catch {
            content = "";
          }
        }

        const analysisPrompt = `Analyze this document content and provide key insights:\n\n${content}`;
        response = await postOceanCborFirst(
          [`/api/v1/query`],
          { query: analysisPrompt, message: analysisPrompt },
          userId || undefined,
        );
      }
    }

    let data: Record<string, unknown> = await decodeUpstreamPayload(response);

    if (response.status === 404) {
      return NextResponse.json(
        {
          status: "error",
          message: "Ocean document module not found.",
        },
        { status: 404 },
      );
    }

    if (response.ok && typeof data?.response === "string") {
      data = {
        status: "ok",
        analysis: data.response,
        confidence: data.confidence,
        sources: data.sources,
        timestamp: data.timestamp,
      };
    } else if (
      response.ok &&
      data &&
      typeof data === "object" &&
      data.extraction &&
      typeof data.extraction === "object"
    ) {
      const extraction = data.extraction as Record<string, unknown>;
      const extractedText =
        typeof extraction.text === "string"
          ? extraction.text
          : typeof extraction.text_preview === "string"
            ? extraction.text_preview
            : "";
      const parser =
        typeof extraction.parser === "string" ? extraction.parser : "unknown";

      data = {
        status: "ok",
        extracted_text: extractedText,
        analysis: extractedText,
        parser,
        validation_status: extractedText.trim() ? "read_ok" : "empty_text",
        checksum_sha256:
          typeof data.sha256 === "string" ? data.sha256 : undefined,
        ingestion_id:
          typeof data.ingestion_id === "string" ? data.ingestion_id : undefined,
        filename: typeof data.filename === "string" ? data.filename : undefined,
        content_type:
          typeof data.content_type === "string" ? data.content_type : undefined,
        size_bytes:
          typeof data.size_bytes === "number" ? data.size_bytes : undefined,
        processing_time_ms:
          typeof data.processing_time_ms === "number"
            ? data.processing_time_ms
            : undefined,
      };
    }

    const accept = request.headers.get("accept") || "";
    if (accept.includes("application/cbor")) {
      const { default: cbor } = await import("cbor");
      const encoded = cbor.encode(data);
      return new NextResponse(encoded as unknown as BodyInit, {
        status: response.status,
        headers: { "Content-Type": "application/cbor" },
      });
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("[Document Proxy] Error:", error);
    const detail = error instanceof Error ? error.message : "unknown error";
    return NextResponse.json(
      {
        status: "error",
        message: "Document analysis service unavailable. Please try again.",
        detail,
      },
      { status: 502 },
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const action = (
      url.searchParams.get("action") || "capabilities"
    ).toLowerCase();
    if (action !== "capabilities") {
      return NextResponse.json(
        {
          status: "error",
          message: "Only action=capabilities is supported for GET.",
        },
        { status: 400 },
      );
    }

    const response = await fetchOceanWithFallbacks(
      [`/api/v1/documents/capabilities`],
      {
        method: "GET",
        cache: "no-store",
      },
    );

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("[Document Proxy][GET] Error:", error);
    return NextResponse.json(
      { status: "error", message: "Failed to fetch document capabilities." },
      { status: 502 },
    );
  }
}
