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

type PendingArticle = {
  id?: string;
  article_id?: string;
  title?: string;
  description?: string;
  excerpt?: string;
  slug?: string;
  category?: string;
  source?: string;
  tags?: string[];
};

function normalizePendingArticles(raw: unknown) {
  const list = Array.isArray(raw) ? (raw as PendingArticle[]) : [];
  return list
    .map((item) => {
      const id = String(item.id || item.article_id || item.slug || "").trim();
      if (!id) return null;
      const title = String(item.title || id).trim();
      const source = String(item.source || item.category || "general").trim();
      return {
        id,
        title,
        description: String(
          item.description || item.excerpt || `Source: ${source}`,
        ).trim(),
        slug: String(item.slug || id).trim(),
        category: String(item.category || source).trim(),
        tags: Array.isArray(item.tags) ? item.tags : [],
      };
    })
    .filter(
      (
        item,
      ): item is {
        id: string;
        title: string;
        description: string;
        slug: string;
        category: string;
        tags: string[];
      } => Boolean(item),
    );
}

export async function GET() {
  let lastError = "LinkedIn service unavailable";

  for (const base of LINKEDIN_CANDIDATES) {
    try {
      const response = await fetch(`${base}/api/v1/pending`, {
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
        const pending = normalizePendingArticles(
          data?.articles || data?.pending || [],
        );
        return NextResponse.json({
          success: true,
          pending,
          count: pending.length,
        });
      }

      lastError =
        data?.error ||
        data?.detail ||
        data?.message ||
        `HTTP ${response.status}`;
    } catch (error) {
      lastError =
        error instanceof Error ? error.message : "Unknown request error";
    }
  }

  console.error("Error fetching pending articles:", lastError);
  return NextResponse.json(
    { success: false, error: lastError, pending: [], count: 0 },
    { status: 502 },
  );
}
