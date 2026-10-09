"use client";

import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import {
  canRequestAds,
  hasAnsweredConsent,
  readConsentState,
  type ConsentState,
} from "../../lib/consent/state";
import AdSenseSlot from "./AdSenseSlot";

type AdConfig = {
  enabled: boolean;
  reason: string;
  provider: string;
  slot: string;
  ad_slot?: string;
  render_mode?: string;
  script_url?: string;
  script_attrs?: Record<string, string>;
  fallback_text?: string;
};

export default function AdSidebarSlot() {
  const [consentState, setConsentState] = useState<ConsentState>(readConsentState);
  const [config, setConfig] = useState<AdConfig | null>(null);
  const [isMounted, setIsMounted] = useState(false);

  const shouldRequest = useMemo(() => canRequestAds(consentState), [consentState]);
  const hasAnswered = useMemo(() => hasAnsweredConsent(consentState), [consentState]);

  const track = (event: "impression" | "click", side: "left" | "right") => {
    if (!config?.ad_slot) return;
    fetch("/api/ads/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        event,
        economy_code: event === "impression" ? "CTS" : "CLK",
        slot: "sidebar",
        provider: config.provider,
        placement_id: `${config.ad_slot}-${side}`,
        page: typeof window !== "undefined" ? window.location.pathname : "",
      }),
    }).catch(() => {});
  };

  useEffect(() => {
    setConsentState(readConsentState());
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!shouldRequest || !hasAnswered) {
      return;
    }

    let active = true;
    const run = async () => {
      const response = await fetch(`/api/ads/config?slot=sidebar&consent=true`, {
        method: "GET",
        cache: "no-store",
      });
      const data = (await response.json()) as AdConfig;
      if (active) {
        setConfig(data);
      }
    };

    run().catch(() => {
      if (active) {
        setConfig({
          enabled: false,
          reason: "client_error",
          provider: "none",
          slot: "sidebar",
          fallback_text: "Ad unavailable",
        });
      }
    });

    return () => {
      active = false;
    };
  }, [hasAnswered, shouldRequest]);

  useEffect(() => {
    if (!config?.enabled || !config.ad_slot) return;

    track("impression", "right");
    track("impression", "left");
  }, [config]);

  if (!isMounted || !hasAnswered || !shouldRequest || !config?.enabled || !config.ad_slot) {
    return null;
  }

  return createPortal(
    <>
      <aside
        className="hidden 2xl:block fixed right-4 top-1/2 -translate-y-1/2 z-[2147483000] w-[300px]"
        aria-label="Sponsored Right"
        onClick={() => track("click", "right")}
      >
        <div className="rounded-xl border border-gray-200 bg-white/95 p-2 shadow-sm backdrop-blur">
          <AdSenseSlot
            slot={config.ad_slot}
            format="vertical"
            minHeight={280}
            className="w-full"
          />
        </div>
      </aside>

      <aside
        className="hidden 3xl:block fixed left-4 top-1/2 -translate-y-1/2 z-[2147483000] w-[300px]"
        aria-label="Sponsored Left"
        onClick={() => track("click", "left")}
      >
        <div className="rounded-xl border border-gray-200 bg-white/95 p-2 shadow-sm backdrop-blur">
          <AdSenseSlot
            slot={config.ad_slot}
            format="vertical"
            minHeight={280}
            className="w-full"
          />
        </div>
      </aside>
    </>,
    document.body,
  );
}
