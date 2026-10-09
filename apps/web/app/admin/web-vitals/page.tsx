"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

interface MetricSummary {
  metric: "CLS" | "FCP" | "INP" | "LCP" | "TTFB";
  count: number;
  quantiles: {
    p75: number | null;
    p95: number | null;
    average: number | null;
  };
  sloTarget: number;
  sloPassRate: number | null;
  ratingBreakdown: {
    good: number;
    needsImprovement: number;
    poor: number;
    unknown: number;
  };
}

interface SummaryWindow {
  window: "24h" | "7d";
  totalEvents: number;
  generatedAt: string;
  metrics: MetricSummary[];
}

interface ReportResponse {
  hasData: boolean;
  totalStoredEvents: number;
  generatedAt: string;
  windows: SummaryWindow[];
}

function formatValue(metric: MetricSummary["metric"], value: number | null): string {
  if (value === null) return "-";

  if (metric === "CLS") {
    return value.toFixed(3);
  }

  return `${Math.round(value)} ms`;
}

function formatTarget(metric: MetricSummary["metric"], value: number): string {
  if (metric === "CLS") return value.toFixed(3);
  return `${value} ms`;
}

function formatPercent(value: number | null): string {
  if (value === null) return "-";
  return `${value.toFixed(1)}%`;
}

export default function WebVitalsAdminPage() {
  const [authorized, setAuthorized] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<ReportResponse | null>(null);

  const fetchReport = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/telemetry/web-vitals/report", {
        cache: "no-store",
      });

      if (response.status === 204) {
        setReport(null);
        setLoading(false);
        return;
      }

      if (!response.ok) {
        throw new Error(`report_status_${response.status}`);
      }

      const data = (await response.json()) as ReportResponse;
      setReport(data);
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : "report_unavailable");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const authStatus = sessionStorage.getItem("admin_authenticated");
    if (authStatus !== "true") {
      window.location.href = "/admin";
      return;
    }

    setAuthorized(true);
    fetchReport();

    const interval = setInterval(fetchReport, 10000);
    return () => clearInterval(interval);
  }, []);

  const windows = useMemo(() => report?.windows ?? [], [report]);

  if (!authorized) {
    return null;
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 px-4 py-8 text-white">
      <div className="mx-auto max-w-7xl">
        <header className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-cyan-300">Admin Observability</p>
            <h1 className="mt-2 text-3xl font-bold">Web Vitals Report</h1>
            <p className="mt-2 text-sm text-slate-300">INP, CLS, LCP, FCP, TTFB aggregated for 24h and 7d windows.</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={fetchReport}
              className="rounded-lg border border-cyan-500/40 px-4 py-2 text-sm font-medium text-cyan-200 hover:border-cyan-300 hover:text-white"
            >
              Refresh
            </button>
            <Link
              href="/admin"
              className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-200 hover:border-cyan-300 hover:text-cyan-200"
            >
              Back to Admin
            </Link>
          </div>
        </header>

        <section className="mb-6 grid gap-4 md:grid-cols-3">
          <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-4">
            <p className="text-xs uppercase tracking-[0.15em] text-slate-400">Status</p>
            <p className="mt-2 text-lg font-semibold">{loading ? "Loading..." : "Live"}</p>
          </div>
          <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-4">
            <p className="text-xs uppercase tracking-[0.15em] text-slate-400">Stored Events</p>
            <p className="mt-2 text-lg font-semibold">{report?.totalStoredEvents ?? 0}</p>
          </div>
          <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-4">
            <p className="text-xs uppercase tracking-[0.15em] text-slate-400">Last Update</p>
            <p className="mt-2 text-lg font-semibold">{report?.generatedAt ?? "-"}</p>
          </div>
        </section>

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-300">
            Unable to load report: {error}
          </div>
        )}

        {!loading && !error && !report && (
          <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-6 text-slate-300">
            No web vitals data captured yet.
          </div>
        )}

        <div className="space-y-6">
          {windows.map((window) => (
            <section key={window.window} className="rounded-2xl border border-slate-700 bg-slate-900/70 p-5">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold">Window: {window.window}</h2>
                <span className="text-sm text-slate-300">Events: {window.totalEvents}</span>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-700 text-slate-300">
                      <th className="px-3 py-2">Metric</th>
                      <th className="px-3 py-2">Count</th>
                      <th className="px-3 py-2">P75</th>
                      <th className="px-3 py-2">P95</th>
                      <th className="px-3 py-2">Avg</th>
                      <th className="px-3 py-2">SLO Target</th>
                      <th className="px-3 py-2">SLO Pass</th>
                      <th className="px-3 py-2">Good / NI / Poor / U</th>
                    </tr>
                  </thead>
                  <tbody>
                    {window.metrics.map((metric) => (
                      <tr key={metric.metric} className="border-b border-slate-800/70">
                        <td className="px-3 py-2 font-semibold text-cyan-200">{metric.metric}</td>
                        <td className="px-3 py-2">{metric.count}</td>
                        <td className="px-3 py-2">{formatValue(metric.metric, metric.quantiles.p75)}</td>
                        <td className="px-3 py-2">{formatValue(metric.metric, metric.quantiles.p95)}</td>
                        <td className="px-3 py-2">{formatValue(metric.metric, metric.quantiles.average)}</td>
                        <td className="px-3 py-2">{formatTarget(metric.metric, metric.sloTarget)}</td>
                        <td className="px-3 py-2">{formatPercent(metric.sloPassRate)}</td>
                        <td className="px-3 py-2">
                          {metric.ratingBreakdown.good} / {metric.ratingBreakdown.needsImprovement} / {metric.ratingBreakdown.poor} / {metric.ratingBreakdown.unknown}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          ))}
        </div>
      </div>
    </main>
  );
}
