const PRIMARY_OCEAN_URL = process.env.OCEAN_CORE_URL;
const OCEAN_INTERNAL_URL =
  process.env.OCEAN_INTERNAL_URL || "http://clisonix-ocean-core:8030";
const OCEAN_LOCAL_URL = "http://localhost:8030";
const PUBLIC_OCEAN_URL = process.env.NEXT_PUBLIC_OCEAN_API_URL;
const isDev = process.env.NODE_ENV !== "production";

export interface ResearchSource {
  title: string;
  url: string;
  snippet?: string;
  image?: string;
}

export interface WebResearchPacket {
  active: boolean;
  mode: "web-assisted";
  query: string;
  sources: ResearchSource[];
  browsedPage?: {
    title: string;
    url: string;
    excerpt: string;
  };
  summaryLines: string[];
}

const SHOPPING_PATTERNS = [
  /\b(shop|shopping|buy|purchase|price|deal|size|color|colour|in stock|available|best price|product)\b/i,
  /\b(nike|adidas|puma|new balance|reebok|asics|zara|hm|h\&m|amazon|zalando|ebay)\b/i,
  /\b(bli|blej|bleje|blerje|produkt|cmim|çmim|mas[ae]|ngjyr[ae]|stok)\b/i,
  /\b(kaufen|preis|größe|farbe|produkt|lager|verfügbar|verfuegbar)\b/i,
];

function buildUpstreamCandidates(): string[] {
  const ordered = [
    OCEAN_INTERNAL_URL,
    PRIMARY_OCEAN_URL,
    isDev ? OCEAN_LOCAL_URL : undefined,
    PUBLIC_OCEAN_URL,
  ]
    .filter((url): url is string => Boolean(url && url.trim()))
    .map((url) => url.replace(/\/+$/, ""));

  return [...new Set(ordered)];
}

const WEB_RESEARCH_PATTERNS = [
  /\b(latest|recent|current|today|news|update|updates|trend|trends|compare|comparison|source|sources|cite|citation|web|internet|online|website|search|look up|find out)\b/i,
  /\b(sot|aktual|aktuale|tani|lajm|lajme|përditësim|perditesim|trend|krahaso|krahasim|burim|burime|internet|web|online|kërko|kerko|gjej|ore|ora|kohe|koh[eë]|sport|sporti|kultur[eë]|kultura)\b/i,
  /\b(heute|aktuell|neueste|nachrichten|quelle|quellen|web|internet|online|suche|finden|vergleich)\b/i,
  /\b(time|clock|timezone|world time|sports|sport|football|soccer|basketball|tennis|culture|cultural|art|music|cinema)\b/i,
  /\b(loi|law|laws|legal|regulation|regulations|policy|policies|court|compliance)\b/i,
  ...SHOPPING_PATTERNS,
  /https?:\/\//i,
];

function isPrivateOrBlockedHost(hostname: string): boolean {
  const host = hostname.trim().toLowerCase();
  if (!host) return true;

  const blockedHosts = new Set([
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "clisonix-ocean-core",
    "ocean-core",
    "clisonix-api",
  ]);

  if (blockedHosts.has(host) || host.endsWith(".local")) {
    return true;
  }

  if (/^10\./.test(host)) return true;
  if (/^127\./.test(host)) return true;
  if (/^169\.254\./.test(host)) return true;
  if (/^192\.168\./.test(host)) return true;
  if (/^172\.(1[6-9]|2\d|3[0-1])\./.test(host)) return true;

  return false;
}

async function fetchPreviewImageFromPage(
  targetUrl: string,
): Promise<string | undefined> {
  let parsed: URL;
  try {
    parsed = new URL(targetUrl);
  } catch {
    return undefined;
  }

  if (
    !/^https?:$/.test(parsed.protocol) ||
    isPrivateOrBlockedHost(parsed.hostname)
  ) {
    return undefined;
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 3500);

  try {
    const response = await fetch(parsed.toString(), {
      method: "GET",
      headers: {
        "User-Agent": "ClisonixOceanWebReader/1.0",
        Accept: "text/html,application/xhtml+xml",
      },
      cache: "no-store",
      signal: controller.signal,
    });

    if (!response.ok) {
      return undefined;
    }

    const html = await response.text();

    const ogMatch = html.match(
      /<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)["'][^>]*>/i,
    );
    const twitterMatch = html.match(
      /<meta[^>]+name=["']twitter:image(?::src)?["'][^>]+content=["']([^"']+)["'][^>]*>/i,
    );
    const fallbackImg = html.match(/<img[^>]+src=["']([^"']+)["'][^>]*>/i);

    const candidate = ogMatch?.[1] || twitterMatch?.[1] || fallbackImg?.[1];
    if (!candidate) {
      return undefined;
    }

    const absolute = new URL(candidate, parsed).toString();
    if (!/^https?:\/\//i.test(absolute)) {
      return undefined;
    }

    return absolute;
  } catch {
    return undefined;
  } finally {
    clearTimeout(timer);
  }
}

async function enrichSourcesWithImages(
  sources: ResearchSource[],
): Promise<ResearchSource[]> {
  if (!sources.length) {
    return sources;
  }

  const limit = Math.min(3, sources.length);
  const previews = await Promise.all(
    sources.slice(0, limit).map(async (source) => ({
      url: source.url,
      image: await fetchPreviewImageFromPage(source.url),
    })),
  );

  const previewMap = new Map(previews.map((item) => [item.url, item.image]));
  return sources.map((source) => ({
    ...source,
    image: previewMap.get(source.url) || source.image,
  }));
}

function extractDirectUrls(text: string): string[] {
  const matches = text.match(/https?:\/\/[^\s)\]"'>]+/gi) || [];
  const sanitized = matches.map((url) => url.replace(/[.,;!?]+$/, "").trim());
  return Array.from(new Set(sanitized)).slice(0, 3);
}

export function shouldUseWebResearch(question: string): boolean {
  const normalized = question.trim();
  if (!normalized) return false;
  return WEB_RESEARCH_PATTERNS.some((pattern) => pattern.test(normalized));
}

export function shouldUseShoppingFastLane(question: string): boolean {
  const normalized = question.trim();
  if (!normalized) return false;
  return SHOPPING_PATTERNS.some((pattern) => pattern.test(normalized));
}

async function fetchOceanJson(path: string): Promise<any> {
  let lastError = "No upstream candidates configured";

  for (const upstream of buildUpstreamCandidates()) {
    try {
      const response = await fetch(`${upstream}${path}`, {
        headers: { Accept: "application/json" },
        cache: "no-store",
      });

      if (!response.ok) {
        lastError = `${response.status} from ${upstream}`;
        continue;
      }

      return await response.json();
    } catch (error) {
      lastError =
        error instanceof Error ? error.message : "Unknown upstream error";
    }
  }

  throw new Error(lastError);
}

function normalizeSources(raw: any): ResearchSource[] {
  const results = Array.isArray(raw?.results)
    ? raw.results
    : Array.isArray(raw?.data?.results)
      ? raw.data.results
      : [];

  return results
    .map((item: any) => ({
      title:
        typeof item?.title === "string" ? item.title.trim() : "Untitled source",
      url: typeof item?.url === "string" ? item.url.trim() : "",
      snippet:
        typeof item?.snippet === "string" ? item.snippet.trim() : undefined,
    }))
    .filter((item: ResearchSource) => item.url.length > 0)
    .slice(0, 4);
}

function buildSummaryLines(sources: ResearchSource[]): string[] {
  return sources.slice(0, 3).map((source, index) => {
    const snippet = source.snippet ? ` — ${source.snippet}` : "";
    return `${index + 1}. ${source.title}${snippet}`;
  });
}

export async function performWebResearch(
  question: string,
): Promise<WebResearchPacket | null> {
  const query = question.trim();
  if (!query) return null;

  const directUrls = extractDirectUrls(query);

  if (directUrls.length > 0) {
    const firstUrl = directUrls[0];

    try {
      const browsePayload = await fetchOceanJson(
        `/api/v1/browse?url=${encodeURIComponent(firstUrl)}&max_chars=5000`,
      );

      const title =
        typeof browsePayload?.title === "string" && browsePayload.title.trim()
          ? browsePayload.title.trim()
          : "Direct link from user";
      const content =
        typeof browsePayload?.content === "string" ? browsePayload.content : "";

      const sources: ResearchSource[] = directUrls.map((url, index) => ({
        title: index === 0 ? title : `User provided link ${index + 1}`,
        url,
        snippet:
          index === 0 && content
            ? content.slice(0, 220).replace(/\s+/g, " ").trim()
            : "Direct URL provided by user",
      }));

      const sourcesWithImages = await enrichSourcesWithImages(sources);

      return {
        active: true,
        mode: "web-assisted",
        query,
        sources: sourcesWithImages,
        browsedPage: {
          title,
          url: firstUrl,
          excerpt: content.slice(0, 1200),
        },
        summaryLines: buildSummaryLines(sourcesWithImages),
      };
    } catch {
      const fallbackSources = directUrls.map((url, index) => ({
        title: `User provided link ${index + 1}`,
        url,
        snippet: "URL captured for research context",
      }));
      const fallbackWithImages = await enrichSourcesWithImages(fallbackSources);

      return {
        active: true,
        mode: "web-assisted",
        query,
        sources: fallbackWithImages,
        summaryLines: directUrls.map(
          (url, index) => `${index + 1}. Direct link provided: ${url}`,
        ),
      };
    }
  }

  // No direct URL in message -> skip external search completely.
  // Internal agent pipelines should provide research context.
  return null;
}

export function buildShoppingFastLaneSystemMessage(
  question: string,
  packet: WebResearchPacket | null,
): string | null {
  if (!shouldUseShoppingFastLane(question)) {
    return null;
  }

  const options = (packet?.sources || []).slice(0, 3);
  const sourceLines = options.length
    ? options
        .map((item, idx) => {
          const imageLine = item.image
            ? `\\n   image: ![${item.title}](${item.image})`
            : "";
          return `${idx + 1}) ${item.title} -> ${item.url}${imageLine}`;
        })
        .join("\\n")
    : "No verified source links available yet.";

  return [
    "Shopping fast-lane mode is active.",
    "Respond in the user's language.",
    "Do not ask extra questions when enough signals already exist.",
    "Answer format:",
    "1) One-line direct recommendation first.",
    "2) Up to 3 shopping options with clickable URLs.",
    "3) Include markdown image lines only when a real image URL is available.",
    "4) Keep answer concise and action-oriented.",
    "Verified candidate sources:",
    sourceLines,
  ].join("\n");
}

export function buildWebResearchSystemMessage(
  packet: WebResearchPacket | null,
): string | null {
  if (!packet?.active || packet.sources.length === 0) {
    return null;
  }

  const sourceBlock = packet.summaryLines.join("\n");
  const browseBlock = packet.browsedPage
    ? `\nBrowsed page focus:\nTitle: ${packet.browsedPage.title}\nURL: ${packet.browsedPage.url}\nExcerpt:\n${packet.browsedPage.excerpt}`
    : "";

  return [
    "Web research packet attached.",
    `Use these current external signals carefully for the query: ${packet.query}`,
    "Prefer the provided evidence over guesswork, and be explicit about uncertainty.",
    "Search summary:",
    sourceBlock,
    browseBlock,
  ]
    .filter(Boolean)
    .join("\n\n");
}
