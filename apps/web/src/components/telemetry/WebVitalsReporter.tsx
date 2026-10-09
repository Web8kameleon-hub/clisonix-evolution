"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { useReportWebVitals } from "next/web-vitals";
import { readConsentState } from "../../lib/consent/state";

type MetricPayload = {
  id: string;
  name: string;
  value: number;
  rating?: string;
  delta?: number;
  navigationType?: string;
  pathname: string;
  href: string;
  userAgent: string;
  timestamp: string;
};

const ENDPOINT = "/api/telemetry/web-vitals";

function canSendAnalyticsTelemetry(): boolean {
  try {
    return readConsentState().analytics === true;
  } catch {
    return false;
  }
}

function toMetricPayload(metric: {
  id: string;
  name: string;
  value: number;
  rating?: string;
  delta?: number;
  navigationType?: string;
}, pathname: string): MetricPayload {
  const href = typeof window !== "undefined" ? window.location.href : "";
  const userAgent = typeof navigator !== "undefined" ? navigator.userAgent : "";

  return {
    id: metric.id,
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    delta: metric.delta,
    navigationType: metric.navigationType,
    pathname,
    href,
    userAgent,
    timestamp: new Date().toISOString(),
  };
}

function sendMetric(payload: MetricPayload): void {
  if (typeof window === "undefined") {
    return;
  }

  const body = JSON.stringify(payload);

  if (navigator.sendBeacon) {
    const blob = new Blob([body], { type: "application/json" });
    navigator.sendBeacon(ENDPOINT, blob);
    return;
  }

  fetch(ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
    keepalive: true,
    cache: "no-store",
  }).catch(() => {
    // Ignore telemetry transport failures to avoid impacting UX.
  });
}

export function WebVitalsReporter() {
  const pathname = usePathname();

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const onConsentChange = () => {
      // Consent is read at send time; listener keeps this component active through consent updates.
    };

    window.addEventListener("clisonix:consent-state-change", onConsentChange);
    return () => {
      window.removeEventListener("clisonix:consent-state-change", onConsentChange);
    };
  }, []);

  useReportWebVitals((metric) => {
    if (!canSendAnalyticsTelemetry()) {
      return;
    }

    const payload = toMetricPayload(metric, pathname || "/");
    sendMetric(payload);
  });

  return null;
}
