export type WebVitalName = "CLS" | "FCP" | "INP" | "LCP" | "TTFB";

export type WebVitalsPayload = {
  id: string;
  name: WebVitalName;
  value: number;
  rating?: "good" | "needs-improvement" | "poor";
  delta?: number;
  navigationType?: string;
  pathname: string;
  href: string;
  userAgent: string;
  timestamp: string;
};

type StoredMetric = WebVitalsPayload & {
  receivedAtMs: number;
};

type Quantiles = {
  p75: number | null;
  p95: number | null;
  average: number | null;
};

type RatingBreakdown = {
  good: number;
  needsImprovement: number;
  poor: number;
  unknown: number;
};

type WindowMetricSummary = {
  metric: WebVitalName;
  count: number;
  quantiles: Quantiles;
  sloTarget: number;
  sloPassRate: number | null;
  ratingBreakdown: RatingBreakdown;
};

type SummaryWindow = {
  window: "24h" | "7d";
  totalEvents: number;
  generatedAt: string;
  metrics: WindowMetricSummary[];
};

const METRIC_NAMES: WebVitalName[] = ["CLS", "FCP", "INP", "LCP", "TTFB"];
const SLO_TARGETS: Record<WebVitalName, number> = {
  CLS: 0.1,
  FCP: 1800,
  INP: 200,
  LCP: 2500,
  TTFB: 800,
};

const DEFAULT_MAX_EVENTS = 25000;
const store = {
  all: [] as StoredMetric[],
};

function getMaxEvents(): number {
  const raw = process.env.WEB_VITALS_MAX_EVENTS;
  if (!raw) return DEFAULT_MAX_EVENTS;

  const parsed = Number(raw);
  if (!Number.isFinite(parsed) || parsed < 1000) {
    return DEFAULT_MAX_EVENTS;
  }

  return Math.floor(parsed);
}

function trimStoreIfNeeded() {
  const maxEvents = getMaxEvents();
  const extra = store.all.length - maxEvents;
  if (extra > 0) {
    store.all.splice(0, extra);
  }
}

function toSortedValues(events: StoredMetric[]): number[] {
  return events
    .map((event) => event.value)
    .filter((value) => Number.isFinite(value))
    .sort((a, b) => a - b);
}

function calculatePercentile(sortedValues: number[], percentile: number): number | null {
  if (sortedValues.length === 0) {
    return null;
  }

  const rank = Math.ceil(percentile * sortedValues.length) - 1;
  const bounded = Math.min(Math.max(rank, 0), sortedValues.length - 1);
  return sortedValues[bounded];
}

function calculateAverage(values: number[]): number | null {
  if (values.length === 0) return null;
  const total = values.reduce((sum, value) => sum + value, 0);
  return total / values.length;
}

function toRatingBreakdown(events: StoredMetric[]): RatingBreakdown {
  return events.reduce<RatingBreakdown>(
    (acc, event) => {
      if (event.rating === "good") {
        acc.good += 1;
      } else if (event.rating === "needs-improvement") {
        acc.needsImprovement += 1;
      } else if (event.rating === "poor") {
        acc.poor += 1;
      } else {
        acc.unknown += 1;
      }

      return acc;
    },
    {
      good: 0,
      needsImprovement: 0,
      poor: 0,
      unknown: 0,
    },
  );
}

function toMetricSummary(metric: WebVitalName, events: StoredMetric[]): WindowMetricSummary {
  const values = toSortedValues(events);
  const average = calculateAverage(values);
  const p75 = calculatePercentile(values, 0.75);
  const p95 = calculatePercentile(values, 0.95);

  const target = SLO_TARGETS[metric];
  const passingEvents = events.filter((event) => event.value <= target).length;
  const passRate = events.length > 0 ? (passingEvents / events.length) * 100 : null;

  return {
    metric,
    count: events.length,
    quantiles: {
      p75,
      p95,
      average,
    },
    sloTarget: target,
    sloPassRate: passRate,
    ratingBreakdown: toRatingBreakdown(events),
  };
}

function summarizeWindow(cutoffMs: number, label: "24h" | "7d", nowIso: string): SummaryWindow {
  const windowEvents = store.all.filter((event) => event.receivedAtMs >= cutoffMs);

  return {
    window: label,
    totalEvents: windowEvents.length,
    generatedAt: nowIso,
    metrics: METRIC_NAMES.map((metric) => {
      const metricEvents = windowEvents.filter((event) => event.name === metric);
      return toMetricSummary(metric, metricEvents);
    }),
  };
}

export function recordWebVital(payload: WebVitalsPayload): void {
  store.all.push({
    ...payload,
    receivedAtMs: Date.now(),
  });
  trimStoreIfNeeded();
}

export function getWebVitalsSummary() {
  const nowMs = Date.now();
  const nowIso = new Date(nowMs).toISOString();

  const summary24h = summarizeWindow(nowMs - 24 * 60 * 60 * 1000, "24h", nowIso);
  const summary7d = summarizeWindow(nowMs - 7 * 24 * 60 * 60 * 1000, "7d", nowIso);

  return {
    hasData: store.all.length > 0,
    totalStoredEvents: store.all.length,
    generatedAt: nowIso,
    windows: [summary24h, summary7d],
  };
}
