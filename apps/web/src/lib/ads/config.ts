export const ADSENSE_ID_PATTERN = /^ca-pub-\d{16}$/;

export type AdSlotName =
  | "footer"
  | "sidebar"
  | "article_top"
  | "article_bottom";

type AdsConfigEnv = Record<string, string | undefined>;

function isTruthyEnvValue(raw?: string): boolean {
  const value = (raw ?? "").trim().toLowerCase();
  return value === "1" || value === "true" || value === "yes" || value === "on";
}

export type AdsenseConfigSource = "next_public" | "server_runtime" | "none";

export interface AdsenseConfigStatus {
  publisherId: string;
  source: AdsenseConfigSource;
  isConfigured: boolean;
}

export function resolveAdsensePublisherId(raw?: string): string {
  const value = (raw ?? "")
    .trim()
    .replace(/^['\"]+|['\"]+$/g, "")
    .replace(/\s+/g, "");
  if (!value) return "";
  if (value.includes("XXXXXXXX")) return "";
  if (!ADSENSE_ID_PATTERN.test(value)) return "";
  return value;
}

export function getAdsenseConfigStatus(
  env: AdsConfigEnv = process.env,
): AdsenseConfigStatus {
  const nextPublicPublisherId = resolveAdsensePublisherId(
    env.NEXT_PUBLIC_GOOGLE_ADSENSE_ID,
  );
  if (nextPublicPublisherId) {
    return {
      publisherId: nextPublicPublisherId,
      source: "next_public",
      isConfigured: true,
    };
  }

  const runtimePublisherId = resolveAdsensePublisherId(
    env.GOOGLE_ADSENSE_PUBLISHER_ID,
  );
  if (runtimePublisherId) {
    return {
      publisherId: runtimePublisherId,
      source: "server_runtime",
      isConfigured: true,
    };
  }

  return {
    publisherId: "",
    source: "none",
    isConfigured: false,
  };
}

export function getAdsensePublisherId(env: AdsConfigEnv = process.env): string {
  return getAdsenseConfigStatus(env).publisherId;
}

export function getAdsensePublisherAccountId(
  env: AdsConfigEnv = process.env,
): string {
  const publisherId = getAdsensePublisherId(env);
  return publisherId.startsWith("ca-") ? publisherId.slice(3) : publisherId;
}

export function getAdsenseScriptUrl(publisherId: string): string {
  return `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${publisherId}`;
}

export function isAdsenseReviewMode(env: AdsConfigEnv = process.env): boolean {
  return (
    isTruthyEnvValue(env.NEXT_PUBLIC_ADSENSE_REVIEW_MODE) ||
    isTruthyEnvValue(env.ADSENSE_REVIEW_MODE)
  );
}

export function isAdsenseAutoAdsEnabled(
  env: AdsConfigEnv = process.env,
): boolean {
  return (
    isTruthyEnvValue(env.NEXT_PUBLIC_ADSENSE_AUTO_ADS) ||
    isTruthyEnvValue(env.ADSENSE_AUTO_ADS) ||
    isAdsenseReviewMode(env)
  );
}

export function getAdsenseSlots(
  env: AdsConfigEnv = process.env,
): Record<AdSlotName, string> {
  return {
    footer: env.ADSENSE_SLOT_FOOTER ?? "",
    sidebar: env.ADSENSE_SLOT_SIDEBAR ?? "",
    article_top: env.ADSENSE_SLOT_ARTICLE_TOP ?? "",
    article_bottom: env.ADSENSE_SLOT_ARTICLE_BOTTOM ?? "",
  };
}

export function getAdsenseSlotId(
  slot: AdSlotName,
  env: AdsConfigEnv = process.env,
): string {
  return getAdsenseSlots(env)[slot] ?? "";
}
