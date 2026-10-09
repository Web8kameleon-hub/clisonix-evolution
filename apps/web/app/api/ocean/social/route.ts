import { NextRequest, NextResponse } from "next/server";

type Platform =
  | "youtube"
  | "tiktok"
  | "instagram"
  | "x"
  | "linkedin"
  | "facebook";

type MediaType = "all" | "video" | "image" | "photo" | "status";

const PLATFORM_URLS: Record<Platform, string> = {
  youtube: "https://www.youtube.com",
  tiktok: "https://www.tiktok.com",
  instagram: "https://www.instagram.com",
  x: "https://x.com",
  linkedin: "https://www.linkedin.com",
  facebook: "https://www.facebook.com",
};

const ENV_MAP: Record<Platform, string> = {
  youtube: "YOUTUBE_API_URL",
  tiktok: "TIKTOK_API_URL",
  instagram: "INSTAGRAM_API_URL",
  x: "X_API_URL",
  linkedin: "LINKEDIN_API_URL",
  facebook: "FACEBOOK_API_URL",
};

function buildSearchUrl(platform: Platform, query: string, mediaType: MediaType): string {
  const encoded = encodeURIComponent(query);

  if (platform === "youtube") {
    return `https://www.youtube.com/results?search_query=${encoded}`;
  }

  if (platform === "tiktok") {
    return `https://www.tiktok.com/search?q=${encoded}`;
  }

  if (platform === "instagram") {
    const tag = query.trim().replace(/\s+/g, "");
    return `https://www.instagram.com/explore/tags/${encodeURIComponent(tag)}/`;
  }

  if (platform === "x") {
    if (mediaType === "video") {
      return `https://x.com/search?q=${encoded}%20filter%3Avideos&src=typed_query`;
    }
    if (mediaType === "image" || mediaType === "photo") {
      return `https://x.com/search?q=${encoded}%20filter%3Aimages&src=typed_query`;
    }
    return `https://x.com/search?q=${encoded}&src=typed_query`;
  }

  if (platform === "linkedin") {
    return `https://www.linkedin.com/search/results/content/?keywords=${encoded}`;
  }

  return `https://www.facebook.com/search/top?q=${encoded}`;
}

export async function GET() {
  const connections = (Object.keys(PLATFORM_URLS) as Platform[]).map((platform) => {
    const apiEnv = ENV_MAP[platform];
    const apiUrl = process.env[apiEnv] || null;

    return {
      platform,
      website: PLATFORM_URLS[platform],
      apiConfigured: Boolean(apiUrl),
      apiUrl,
      status: apiUrl ? "ready" : "missing_config",
    };
  });

  return NextResponse.json({
    status: "ok",
    socialHub: "ocean-social-connect",
    connections,
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    if (body.action === "search" || typeof body.query === "string") {
      const query = String(body.query || "").trim();
      const mediaType = String(body.mediaType || "all").toLowerCase() as MediaType;

      if (!query) {
        return NextResponse.json(
          { status: "error", message: "Query is required" },
          { status: 400 },
        );
      }

      const supportedMedia: MediaType[] = ["all", "video", "image", "photo", "status"];
      if (!supportedMedia.includes(mediaType)) {
        return NextResponse.json(
          { status: "error", message: "Unsupported mediaType", supportedMedia },
          { status: 400 },
        );
      }

      const results = (Object.keys(PLATFORM_URLS) as Platform[]).map((platform) => ({
        platform,
        mediaType,
        url: buildSearchUrl(platform, query, mediaType),
      }));

      return NextResponse.json({
        status: "ok",
        query,
        mediaType,
        total: results.length,
        results,
      });
    }

    const platform = String(body.platform || "").toLowerCase() as Platform;

    if (!PLATFORM_URLS[platform]) {
      return NextResponse.json(
        {
          status: "error",
          message: "Unsupported platform",
          supported: Object.keys(PLATFORM_URLS),
        },
        { status: 400 },
      );
    }

    const endpoint = process.env[ENV_MAP[platform]];

    if (!endpoint) {
      return NextResponse.json(
        {
          status: "error",
          message: `Missing env ${ENV_MAP[platform]} for ${platform}`,
          website: PLATFORM_URLS[platform],
        },
        { status: 400 },
      );
    }

    return NextResponse.json({
      status: "ok",
      platform,
      website: PLATFORM_URLS[platform],
      endpoint,
      note: "Connection endpoint is configured. Attach OAuth + publishing worker next.",
    });
  } catch {
    return NextResponse.json(
      { status: "error", message: "Invalid request body" },
      { status: 400 },
    );
  }
}
