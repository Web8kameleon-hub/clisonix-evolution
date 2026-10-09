export const CONSENT_STORAGE_KEY = "clisonix_ads_consent_v1";
export const CONSENT_STATE_CHANGE_EVENT = "clisonix:consent-state-change";

export type ConsentDecision = "unknown" | "accepted_all" | "rejected_all" | "customized";

export interface ConsentState {
  necessary: true;
  analytics: boolean;
  ads: boolean;
  adPersonalization: boolean;
  decision: ConsentDecision;
  updatedAt: string | null;
  version: 2;
}

type LegacyConsentState = "accepted" | "declined" | "unknown" | null;

const DEFAULT_CONSENT_STATE: ConsentState = {
  necessary: true,
  analytics: false,
  ads: false,
  adPersonalization: false,
  decision: "unknown",
  updatedAt: null,
  version: 2,
};

function isTruthyEnvValue(raw?: string): boolean {
  const value = (raw ?? "").trim().toLowerCase();
  return value === "1" || value === "true" || value === "yes" || value === "on";
}

function isReviewAdsModeEnabled(): boolean {
  return (
    isTruthyEnvValue(process.env.NEXT_PUBLIC_ADSENSE_REVIEW_MODE) ||
    isTruthyEnvValue(process.env.NEXT_PUBLIC_ADSENSE_AUTO_ADS)
  );
}

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

function isConsentState(value: unknown): value is Partial<ConsentState> {
  return typeof value === "object" && value !== null;
}

function migrateLegacyConsentState(value: LegacyConsentState): ConsentState {
  if (value === "accepted") {
    return {
      necessary: true,
      analytics: true,
      ads: true,
      adPersonalization: true,
      decision: "accepted_all",
      updatedAt: new Date().toISOString(),
      version: 2,
    };
  }

  if (value === "declined") {
    return {
      necessary: true,
      analytics: false,
      ads: false,
      adPersonalization: false,
      decision: "rejected_all",
      updatedAt: new Date().toISOString(),
      version: 2,
    };
  }

  return { ...DEFAULT_CONSENT_STATE };
}

function normalizeConsentState(value: Partial<ConsentState>): ConsentState {
  const ads = value.ads === true;
  const adPersonalization = ads && value.adPersonalization === true;

  return {
    necessary: true,
    analytics: value.analytics === true,
    ads,
    adPersonalization,
    decision: value.decision ?? "customized",
    updatedAt: typeof value.updatedAt === "string" ? value.updatedAt : new Date().toISOString(),
    version: 2,
  };
}

export function getDefaultConsentState(): ConsentState {
  if (isReviewAdsModeEnabled()) {
    return {
      necessary: true,
      analytics: false,
      ads: true,
      adPersonalization: false,
      decision: "customized",
      updatedAt: null,
      version: 2,
    };
  }

  return { ...DEFAULT_CONSENT_STATE };
}

export function readConsentState(): ConsentState {
  if (!isBrowser()) {
    return getDefaultConsentState();
  }

  let raw: string | null = null;
  try {
    raw = window.localStorage.getItem(CONSENT_STORAGE_KEY);
  } catch {
    return getDefaultConsentState();
  }

  if (!raw) {
    return getDefaultConsentState();
  }

  if (raw === "accepted" || raw === "declined" || raw === "unknown") {
    const migrated = migrateLegacyConsentState(raw);
    writeConsentState(migrated);
    return migrated;
  }

  try {
    const parsed: unknown = JSON.parse(raw);
    if (!isConsentState(parsed)) {
      return getDefaultConsentState();
    }

    return normalizeConsentState(parsed);
  } catch {
    return getDefaultConsentState();
  }
}

export function writeConsentState(state: ConsentState): void {
  if (!isBrowser()) {
    return;
  }

  try {
    window.localStorage.setItem(CONSENT_STORAGE_KEY, JSON.stringify(state));
  } catch {
    // localStorage may be blocked (e.g. strict privacy mode); continue with in-memory event updates
  }

  try {
    window.dispatchEvent(
      new CustomEvent(CONSENT_STATE_CHANGE_EVENT, { detail: state }),
    );
  } catch {
    // no-op
  }
}

export function acceptAllConsent(): ConsentState {
  const nextState: ConsentState = {
    necessary: true,
    analytics: true,
    ads: true,
    adPersonalization: true,
    decision: "accepted_all",
    updatedAt: new Date().toISOString(),
    version: 2,
  };
  writeConsentState(nextState);
  return nextState;
}

export function rejectAllConsent(): ConsentState {
  const nextState: ConsentState = {
    necessary: true,
    analytics: false,
    ads: false,
    adPersonalization: false,
    decision: "rejected_all",
    updatedAt: new Date().toISOString(),
    version: 2,
  };
  writeConsentState(nextState);
  return nextState;
}

export function canRequestAds(consentState: ConsentState): boolean {
  return consentState.ads || isReviewAdsModeEnabled();
}

export function hasAnsweredConsent(consentState: ConsentState): boolean {
  return consentState.decision !== "unknown" || isReviewAdsModeEnabled();
}
