import { NextRequest, NextResponse } from "next/server";

const LINKEDIN_CANDIDATES = [
  process.env.BLOG_PUBLISHER_URL,
  process.env.LINKEDIN_API_URL,
  "http://clisonix-blog-publisher:8041",
  "http://blog_publisher:8041",
  "http://localhost:8041",
  "http://clisonix-linkedin-poster:8007",
  "http://linkedin-poster:8007",
  "http://localhost:8007",
].filter((url): url is string => Boolean(url && url.trim()));

async function postToLinkedin(path: string, body?: string) {
  let lastError = "LinkedIn service unavailable";

  for (const base of LINKEDIN_CANDIDATES) {
    try {
      const response = await fetch(`${base}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
      });

      const contentType = response.headers.get("content-type") || "";
      const isJson = contentType.includes("application/json");
      const payload = isJson
        ? await response.json()
        : { success: false, error: await response.text() };

      if (response.ok) {
        return NextResponse.json(payload);
      }

      lastError =
        payload?.error || payload?.detail || `HTTP ${response.status}`;
    } catch (error) {
      lastError =
        error instanceof Error ? error.message : "Unknown request error";
    }
  }

  return NextResponse.json(
    { success: false, error: lastError },
    { status: 502 },
  );
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as { text?: string; title?: string };
    const text = String(body?.text || "").trim();
    if (!text) {
      return NextResponse.json(
        { success: false, error: "text is required" },
        { status: 400 },
      );
    }

    const rawTitle = String(body?.title || text.slice(0, 80)).trim();
    const title =
      rawTitle.length > 3
        ? rawTitle
        : `Clisonix Update ${new Date().toISOString().slice(0, 10)}`;

    const response = await postToLinkedin(
      "/api/v1/publish/direct",
      JSON.stringify({ title, content: text, source: "newsroom" }),
    );

    if (!response.ok) return response;

    const payload = await response.json();
    return NextResponse.json({
      success: true,
      post_id: payload.post_filename || payload.github_url || title,
      message: payload.message || "Custom post published",
      github_url: payload.github_url,
      status: payload.status,
    });
  } catch (error) {
    console.error("Error posting custom content:", error);
    return NextResponse.json(
      { success: false, error: "Failed to post custom content" },
      { status: 500 },
    );
  }
}
