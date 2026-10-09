"use client";

import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import {
  acceptAllConsent,
  canRequestAds,
  hasAnsweredConsent,
  readConsentState,
  rejectAllConsent,
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

export default function AdFooterSlot() {
  const [consentState, setConsentState] = useState<ConsentState>(readConsentState);
  const [config, setConfig] = useState<AdConfig | null>(null);
  const [isMounted, setIsMounted] = useState(false);

  const shouldRequest = useMemo(() => canRequestAds(consentState), [consentState]);
  const hasAnswered = useMemo(() => hasAnsweredConsent(consentState), [consentState]);

  useEffect(() => {
    setConsentState(readConsentState());
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!shouldRequest) {
      return;
    }

    let active = true;
    const run = async () => {
      const response = await fetch(`/api/ads/config?slot=footer&consent=true`, {
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
          slot: "footer",
          fallback_text: "Ad unavailable",
        });
      }
    });

    return () => {
      active = false;
    };
  }, [shouldRequest]);

  useEffect(() => {
    if (!config?.enabled || !config.ad_slot) return;

    fetch("/api/ads/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        event: "impression",
        economy_code: "CTS",
        slot: "footer",
        provider: config.provider,
        placement_id: config.ad_slot,
        page: typeof window !== "undefined" ? window.location.pathname : "",
      }),
    }).catch(() => {});
  }, [config]);

  const accept = () => {
    try {
      setConsentState(acceptAllConsent());
    } catch {
      setConsentState({
        necessary: true,
        analytics: true,
        ads: true,
        adPersonalization: true,
        decision: "accepted_all",
        updatedAt: new Date().toISOString(),
        version: 2,
      });
    }
  };

  const decline = () => {
    try {
      setConsentState(rejectAllConsent());
    } catch {
      setConsentState({
        necessary: true,
        analytics: false,
        ads: false,
        adPersonalization: false,
        decision: "rejected_all",
        updatedAt: new Date().toISOString(),
        version: 2,
      });
    }
  };

  if (!hasAnswered) {
    if (!isMounted) {
      return null;
    }

    return createPortal(
      <div className="fixed inset-x-0 bottom-4 z-[2147483647] flex justify-center px-2">
        <div
          role="dialog"
          aria-modal="false"
          aria-label="Advertising consent"
          className="w-[95%] max-w-2xl rounded-xl border border-gray-300 bg-white p-4 shadow-lg"
        >
          <p className="text-sm text-gray-700">
            We use limited advertising to support the platform. You can accept or decline non-essential ads.
          </p>
          <div className="mt-3 flex gap-2">
            <button
              type="button"
              onClick={accept}
              className="rounded-md bg-emerald-600 px-3 py-2 text-sm text-white hover:bg-emerald-700"
            >
              Accept Ads
            </button>
            <button
              type="button"
              onClick={decline}
              className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
            >
              Decline
            </button>
          </div>
        </div>
      </div>,
      document.body,
    );
  }

  if (!shouldRequest) {
    return null;
  }

  if (!config?.enabled) {
    return null;
  }

  if (!config.ad_slot) {
    return null;
  }

  if (!isMounted) {
    return null;
  }

  return createPortal(
    <div
      className="fixed bottom-0 left-0 right-0 z-[2147483600] border-t border-gray-200 bg-white/95 px-2 py-2 text-center text-xs text-gray-500 backdrop-blur"
      onClick={() => {
        fetch("/api/ads/track", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            event: "click",
            economy_code: "CLK",
            slot: "footer",
            provider: config.provider,
            placement_id: config.ad_slot || "",
            page: typeof window !== "undefined" ? window.location.pathname : "",
          }),
        }).catch(() => {});
      }}
    >
      <div className="mx-auto max-w-[980px]">
        <AdSenseSlot slot={config.ad_slot} format="horizontal" minHeight={90} className="w-full" />
      </div>
    </div>,
    document.body,
  );
}
