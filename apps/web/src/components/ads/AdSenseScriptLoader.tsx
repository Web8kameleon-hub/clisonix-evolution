"use client";

import { useEffect, useState } from "react";
import { getAdsenseScriptUrl } from "../../lib/ads/config";
import {
  canRequestAds,
  CONSENT_STATE_CHANGE_EVENT,
  readConsentState,
  type ConsentState,
} from "../../lib/consent/state";

const ADSENSE_SCRIPT_ID = "clisonix-adsense-script";

type AdSenseScriptLoaderProps = {
  publisherId: string;
};

export default function AdSenseScriptLoader({ publisherId }: AdSenseScriptLoaderProps) {
  const [consentState, setConsentState] = useState<ConsentState>(readConsentState);
  const adsAllowed = canRequestAds(consentState);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const syncConsentState = () => {
      setConsentState(readConsentState());
    };

    syncConsentState();
    window.addEventListener(CONSENT_STATE_CHANGE_EVENT, syncConsentState);
    window.addEventListener("storage", syncConsentState);

    return () => {
      window.removeEventListener(CONSENT_STATE_CHANGE_EVENT, syncConsentState);
      window.removeEventListener("storage", syncConsentState);
    };
  }, []);

  useEffect(() => {
    if (!publisherId || !adsAllowed || typeof document === "undefined") {
      return;
    }

    const existingScript = document.getElementById(ADSENSE_SCRIPT_ID);
    if (existingScript) {
      return;
    }

    const script = document.createElement("script");
    script.id = ADSENSE_SCRIPT_ID;
    script.async = true;
    script.crossOrigin = "anonymous";
    script.src = getAdsenseScriptUrl(publisherId);
    document.head.appendChild(script);
  }, [adsAllowed, publisherId]);

  return null;
}
