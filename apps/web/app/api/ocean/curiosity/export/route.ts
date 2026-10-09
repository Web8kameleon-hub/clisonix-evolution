import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const OCEAN_INTERNAL_URL =
  process.env.OCEAN_INTERNAL_URL || "http://clisonix-ocean-core:8030";
const OCEAN_CORE_URL = process.env.OCEAN_CORE_URL;

type ExportFormat = "pdf" | "docx" | "xlsx";

function resolveUpstreams(): string[] {
  const unique = [OCEAN_INTERNAL_URL, OCEAN_CORE_URL]
    .filter((url): url is string => Boolean(url && url.trim()))
    .map((url) => url.replace(/\/+$/, ""));
  return [...new Set(unique)];
}

function sanitizeFileName(name: string): string {
  return name
    .replace(/[^a-zA-Z0-9._-]/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

function buildConversationQuery(
  messages: Array<{ role: string; content: string }>,
  language?: string,
): string {
  const turns = messages
    .filter((m) => m && typeof m.content === "string" && m.content.trim())
    .slice(-40)
    .map(
      (m, idx) =>
        `${idx + 1}. ${String(m.role || "user").toUpperCase()}: ${m.content.trim()}`,
    )
    .join("\n\n");

  return [
    "Generate a structured conversation export from the following Curiosity Ocean chat.",
    "Preserve key technical points, tables and decision bullets whenever present.",
    language ? `Language: ${language}` : undefined,
    "",
    "Conversation:",
    turns || "No conversation content provided.",
  ]
    .filter(Boolean)
    .join("\n");
}

function buildLocalTranscriptArtifact(
  messages: Array<{ role: string; content: string }>,
  language?: string,
): {
  fileName: string;
  mimeType: string;
  bytes: Uint8Array;
} {
  const ts = new Date().toISOString();
  const lines: string[] = [
    "Curiosity Ocean Conversation Export",
    `Timestamp: ${ts}`,
    `Language: ${language || "en"}`,
    "",
    "Transcript:",
  ];

  for (const [idx, msg] of messages.entries()) {
    const role = String(msg?.role || "user").toUpperCase();
    const content = typeof msg?.content === "string" ? msg.content.trim() : "";
    if (!content) continue;
    lines.push("");
    lines.push(`${idx + 1}. ${role}`);
    lines.push(content);
  }

  const bytes = new TextEncoder().encode(lines.join("\n"));
  return {
    fileName: `curiosity-export-${Date.now()}.txt`,
    mimeType: "text/plain; charset=utf-8",
    bytes,
  };
}

function parseExportArtifact(payload: Record<string, unknown>): {
  fileName: string;
  mimeType: string;
  bytes: Uint8Array;
} | null {
  const documentObj =
    payload.document && typeof payload.document === "object"
      ? (payload.document as Record<string, unknown>)
      : null;

  if (!documentObj) return null;

  const contentBase64 =
    typeof documentObj.content_base64 === "string"
      ? documentObj.content_base64
      : typeof documentObj.file_base64 === "string"
        ? documentObj.file_base64
        : null;

  if (!contentBase64) return null;

  const fileNameRaw =
    typeof documentObj.filename === "string"
      ? documentObj.filename
      : typeof documentObj.file_name === "string"
        ? documentObj.file_name
        : "curiosity-export.bin";

  const mimeType =
    typeof documentObj.content_type === "string"
      ? documentObj.content_type
      : typeof documentObj.mime_type === "string"
        ? documentObj.mime_type
        : "application/octet-stream";

  try {
    const bytes = Buffer.from(contentBase64, "base64");
    return {
      fileName: sanitizeFileName(fileNameRaw) || "curiosity-export.bin",
      mimeType,
      bytes: new Uint8Array(bytes),
    };
  } catch {
    return null;
  }
}

function parseStructuredDocumentFallback(payload: Record<string, unknown>): {
  fileName: string;
  mimeType: string;
  bytes: Uint8Array;
} | null {
  const documentObj =
    payload.document && typeof payload.document === "object"
      ? (payload.document as Record<string, unknown>)
      : null;
  if (!documentObj) return null;

  const rows = Array.isArray(documentObj.rows)
    ? (documentObj.rows as Array<Record<string, unknown>>)
    : [];
  const metadata =
    documentObj.metadata && typeof documentObj.metadata === "object"
      ? (documentObj.metadata as Record<string, unknown>)
      : {};

  const lines: string[] = [];
  if (typeof metadata.query === "string" && metadata.query.trim()) {
    lines.push(`Query: ${metadata.query.trim()}`);
  }

  if (rows.length > 0) {
    lines.push("");
    lines.push("Generated document rows:");
    rows.forEach((row, idx) => {
      lines.push("");
      lines.push(`# Row ${idx + 1}`);
      for (const [key, value] of Object.entries(row || {})) {
        lines.push(`- ${key}: ${String(value ?? "")}`);
      }
    });
  }

  if (lines.length === 0) return null;

  const text = lines.join("\n").trim();
  if (!text) return null;

  const fileName = `curiosity-export-${Date.now()}.txt`;
  const bytes = new TextEncoder().encode(text);
  return {
    fileName,
    mimeType: "text/plain; charset=utf-8",
    bytes,
  };
}

function extensionFor(format: ExportFormat): string {
  if (format === "pdf") return "pdf";
  if (format === "docx") return "docx";
  return "xlsx";
}

function upstreamFormatFor(format: ExportFormat): string {
  if (format === "docx") return "report";
  return format;
}

function upstreamContractTypeFor(_format: ExportFormat): string {
  // ocean-core currently supports contract_type in: cpi, research, video, voice
  // For chat transcript exports, research is the safest generic contract.
  return "research";
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json().catch(() => ({}))) as Record<
      string,
      unknown
    >;
    const format = String(body.format || "pdf").toLowerCase() as ExportFormat;
    const messages = Array.isArray(body.messages)
      ? (body.messages as Array<{ role: string; content: string }>)
      : [];
    const language =
      typeof body.language === "string" ? body.language : undefined;

    if (!["pdf", "docx", "xlsx"].includes(format)) {
      return NextResponse.json(
        { error: "Unsupported export format. Use pdf, docx, or xlsx." },
        { status: 400 },
      );
    }

    if (!messages.length) {
      return NextResponse.json(
        { error: "No conversation messages provided for export." },
        { status: 422 },
      );
    }

    const query = buildConversationQuery(messages, language);
    const desiredFormat = upstreamFormatFor(format);
    const contractType = upstreamContractTypeFor(format);
    const localTranscriptArtifact = buildLocalTranscriptArtifact(
      messages,
      language,
    );
    let lastError = "No export upstream available";

    for (const upstream of resolveUpstreams()) {
      const response = await fetch(`${upstream}/api/v1/documents/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          query,
          format: desiredFormat,
          contract_type: contractType,
          language: language || "en",
          auto_translate: false,
        }),
      }).catch((err) => {
        lastError = err instanceof Error ? err.message : String(err);
        return null;
      });

      if (!response) continue;
      const rawText = await response.text();

      if (!response.ok) {
        lastError = rawText || `Upstream export failed (${response.status})`;
        continue;
      }

      let payload: Record<string, unknown> = {};
      try {
        payload = JSON.parse(rawText) as Record<string, unknown>;
      } catch {
        payload = {};
      }

      const artifact = parseExportArtifact(payload);
      const fallbackArtifact = artifact || parseStructuredDocumentFallback(payload);
      if (!fallbackArtifact) {
        lastError =
          "Upstream did not return a binary export artifact. Document generation is available but file packaging is missing.";
        continue;
      }

      const fallbackName = `curiosity-ocean-${Date.now()}.${extensionFor(format)}`;
      const finalName = fallbackArtifact.fileName || fallbackName;
      const normalizedBytes = Uint8Array.from(fallbackArtifact.bytes);
      const body = new Blob([normalizedBytes], { type: fallbackArtifact.mimeType });

      return new NextResponse(body, {
        status: 200,
        headers: {
          "Content-Type": fallbackArtifact.mimeType,
          "Content-Disposition": `attachment; filename=\"${finalName}\"`,
          "Cache-Control": "no-store",
        },
      });
    }

    const localBody = new Blob([Buffer.from(localTranscriptArtifact.bytes)], {
      type: localTranscriptArtifact.mimeType,
    });

    return new NextResponse(localBody, {
      status: 200,
      headers: {
        "Content-Type": localTranscriptArtifact.mimeType,
        "Content-Disposition": `attachment; filename=\"${localTranscriptArtifact.fileName}\"`,
        "Cache-Control": "no-store",
        "X-Export-Fallback": "local-transcript",
        "X-Export-Error": lastError,
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        error: "Export request failed",
        detail: error instanceof Error ? error.message : String(error),
      },
      { status: 500 },
    );
  }
}
