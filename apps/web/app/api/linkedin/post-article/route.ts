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
    const body = (await request.json()) as {
      article_id?: string;
      source?: string;
    };

    const articleId = String(body?.article_id || "").trim();
    if (!articleId) {
      return NextResponse.json(
        { success: false, error: "article_id is required" },
        { status: 400 },
      );
    }

    const response = await postToLinkedin(
      "/api/v1/publish",
      JSON.stringify({
        article_id: articleId,
        source: body?.source || "blerina",
      }),
    );

    if (!response.ok) return response;

    const payload = await response.json();
    return NextResponse.json({
      success: true,
      post_id: payload.post_filename || payload.github_url || articleId,
      message: payload.message || "Article published",
      github_url: payload.github_url,
      status: payload.status,
    });
  } catch (error) {
    console.error("Error posting article:", error);
    return NextResponse.json(
      { success: false, error: "Failed to post article" },
      { status: 500 },
    );
  }
}
