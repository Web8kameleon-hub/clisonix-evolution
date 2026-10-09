import { NextResponse } from "next/server";

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

export async function GET() {
  let lastError = "LinkedIn service unavailable";

  for (const base of LINKEDIN_CANDIDATES) {
    try {
      const response = await fetch(`${base}/api/v1/published`, {
        headers: { Accept: "application/json" },
        cache: "no-store",
      });

      const contentType = response.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        lastError = `Unexpected response type from ${base}`;
        continue;
      }

      const data = await response.json();
      if (response.ok) {
        const articles = Array.isArray(data?.articles) ? data.articles : [];
        const posted = articles
          .map((entry: unknown) => {
            if (typeof entry === "string") return entry;
            if (entry && typeof entry === "object") {
              const record = entry as Record<string, unknown>;
              const key =
                record.article_id ||
                record.id ||
                record.title ||
                record.post_filename;
              return typeof key === "string" ? key : "";
            }
            return "";
          })
          .filter((id: string) => Boolean(id));

        return NextResponse.json({ posted, count: posted.length });
      }

      lastError = data?.error || data?.detail || `HTTP ${response.status}`;
    } catch (error) {
      lastError =
        error instanceof Error ? error.message : "Unknown request error";
    }
  }

  console.error("Error fetching posted articles:", lastError);
  return NextResponse.json(
    { posted: [], count: 0, error: lastError },
    { status: 502 },
  );
}
