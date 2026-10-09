"use client";

/**
 * AdSenseSlot — Google AdSense ad unit component
 *
 * Usage:
 *   <AdSenseSlot slot="1234567890" format="auto" />
 *
 * The publisher ID is read from NEXT_PUBLIC_GOOGLE_ADSENSE_ID,
 * with fallback GOOGLE_ADSENSE_PUBLISHER_ID.
 * Nothing renders if:
 *   - Publisher ID is not configured
 *   - User has declined consent
 *   - Ad blocker suppresses the ins element (silent)
 */

import { useEffect, useRef, useState } from "react";
import { getAdsensePublisherId } from "../../lib/ads/config";
import {
  canRequestAds,
  CONSENT_STATE_CHANGE_EVENT,
  readConsentState,
  type ConsentState,
} from "../../lib/consent/state";

type AdFormat = "auto" | "fluid" | "rectangle" | "vertical" | "horizontal";

interface AdSenseSlotProps {
  /** AdSense ad unit slot ID (numeric string from Google) */
  slot: string;
  format?: AdFormat;
  /** Override CSS width / height for fixed-size placements */
  style?: React.CSSProperties;
  /** Responsive auto-sizing (default: true) */
  responsive?: boolean;
  /** Reserved minimum height to avoid CLS (default: 250px) */
  minHeight?: number;
  className?: string;
}

export default function AdSenseSlot({
  slot,
  format = "auto",
  style,
  responsive = true,
  minHeight = 250,
  className,
}: AdSenseSlotProps) {
  const publisherId = getAdsensePublisherId(process.env);
  const insRef = useRef<HTMLModElement | null>(null);
  const [consentState, setConsentState] = useState<ConsentState>(readConsentState);
  const [pushed, setPushed] = useState(false);
  const adsAllowed = canRequestAds(consentState);

  useEffect(() => {
    if (typeof window === "undefined") return;

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
    if (!publisherId || !adsAllowed || pushed) return;

    // Push ad after a tick so the DOM is ready
    const timer = setTimeout(() => {
      try {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        ((window as any).adsbygoogle = (window as any).adsbygoogle || []).push({});
        setPushed(true);
      } catch {
        /* ad blocker or network error — fail silently */
      }
    }, 0);

    return () => clearTimeout(timer);
  }, [adsAllowed, publisherId, pushed]);

  // Don't render if no publisher ID or ads are not allowed by consent state
  if (!publisherId || !adsAllowed) return null;

  return (
    <div
      className={className}
      style={{
        display: "block",
        textAlign: "center",
        overflow: "hidden",
        position: "relative",
        minHeight,
        backgroundColor: "#f9fafb",
        ...style,
      }}
    >
      {!pushed && (
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#9ca3af",
            fontSize: "12px",
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            pointerEvents: "none",
          }}
        >
          Advertisement
        </div>
      )}
      <ins
        ref={insRef}
        className="adsbygoogle"
        style={{ display: "block", position: "relative", zIndex: 1 }}
        data-ad-client={publisherId}
        data-ad-slot={slot}
        data-ad-format={format}
        data-full-width-responsive={responsive ? "true" : "false"}
      />
    </div>
  );
}
