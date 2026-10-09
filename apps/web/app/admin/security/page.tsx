'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';

type BackendSecurityStatus = {
  status: string;
  timestamp: string;
  middleware?: {
    enabled?: boolean;
    blocked_ips?: number;
    monitored_ips?: number;
    total_threats?: number;
    last_threat?: {
      ip?: string;
      threat_type?: string;
      threat_count?: number;
      timestamp?: number;
    } | null;
    last_updated?: number | null;
  };
  protections?: Record<string, boolean>;
  frontend?: {
    csp_report_endpoint?: string;
    security_page?: string;
    admin_dashboard?: string;
  };
};

type FrontendSecurityPosture = {
  timestamp: string;
  securityHeaders?: Record<string, string>;
  posture?: {
    hsts?: boolean;
    csp?: boolean;
    frameProtection?: boolean;
    contentTypeProtection?: boolean;
    referrerPolicy?: string | null;
    reportUri?: string | null;
  };
  cspDirectives?: Record<string, boolean>;
  recentReports?: Array<{
    documentUri?: string | null;
    violatedDirective?: string | null;
    effectiveDirective?: string | null;
    blockedUri?: string | null;
    sourceFile?: string | null;
    disposition?: string | null;
    originalPolicy?: string | null;
    userAgent?: string | null;
    receivedAt?: string;
  }>;
};

type BackendSecurityEvents = {
  count: number;
  events: Array<{
    ip?: string;
    threat_type?: string;
    threat_count?: number;
    blocked?: boolean;
    event?: string;
    timestamp?: number;
  }>;
};

function formatUnixTimestamp(value?: number | null) {
  if (!value) return 'Unavailable';
  return new Date(value * 1000).toLocaleString();
}

export default function AdminSecurityPage() {
  const [backend, setBackend] = useState<BackendSecurityStatus | null>(null);
  const [frontend, setFrontend] = useState<FrontendSecurityPosture | null>(null);
  const [eventHistory, setEventHistory] = useState<BackendSecurityEvents | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const [backendResponse, frontendResponse] = await Promise.all([
          fetch('/api/security/status', { cache: 'no-store' }),
          fetch('/api/security/posture', { cache: 'no-store' }),
        ]);

        const eventsResponse = await fetch('/api/security/events?limit=20', { cache: 'no-store' });

        if (!backendResponse.ok) {
          throw new Error(`backend_security_${backendResponse.status}`);
        }

        if (!frontendResponse.ok) {
          throw new Error(`frontend_security_${frontendResponse.status}`);
        }

        if (!eventsResponse.ok) {
          throw new Error(`security_events_${eventsResponse.status}`);
        }

        const [backendPayload, frontendPayload, eventsPayload] = await Promise.all([
          backendResponse.json() as Promise<BackendSecurityStatus>,
          frontendResponse.json() as Promise<FrontendSecurityPosture>,
          eventsResponse.json() as Promise<BackendSecurityEvents>,
        ]);

        if (!cancelled) {
          setBackend(backendPayload);
          setFrontend(frontendPayload);
          setEventHistory(eventsPayload);
        }
      } catch (fetchError) {
        if (!cancelled) {
          setError(fetchError instanceof Error ? fetchError.message : 'security_fetch_failed');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    const interval = window.setInterval(load, 15000);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, []);

  const backendProtections = useMemo(() => Object.entries(backend?.protections ?? {}), [backend]);
  const cspDirectives = useMemo(() => Object.entries(frontend?.cspDirectives ?? {}), [frontend]);
  const recentCspReports = useMemo(() => frontend?.recentReports ?? [], [frontend]);
  const keyHeaders = useMemo(
    () =>
      [
        'Strict-Transport-Security',
        'Content-Security-Policy',
        'X-Frame-Options',
        'X-Content-Type-Options',
        'Referrer-Policy',
        'Permissions-Policy',
        'Cross-Origin-Opener-Policy',
        'X-Guardian-Status',
      ].map((name) => ({ name, value: frontend?.securityHeaders?.[name] ?? null })),
    [frontend],
  );

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-cyan-400">Admin Security</p>
            <h1 className="mt-2 text-4xl font-semibold tracking-tight">Real Security Posture</h1>
            <p className="mt-3 max-w-3xl text-sm text-neutral-400">
              This page reads only live Clisonix security state from the backend middleware and the frontend CSP/header pipeline.
            </p>
          </div>
          <div className="flex gap-3">
            <Link href="/admin" className="rounded-lg border border-neutral-700 px-4 py-2 text-sm text-neutral-300 hover:border-neutral-500 hover:text-white">
              Back to Admin
            </Link>
            <button
              onClick={() => window.location.reload()}
              className="rounded-lg border border-cyan-700 bg-cyan-500/10 px-4 py-2 text-sm text-cyan-300 hover:bg-cyan-500/20"
            >
              Refresh
            </button>
          </div>
        </div>

        {loading && (
          <div className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6 text-sm text-neutral-300">
            Loading live security posture...
          </div>
        )}

        {error && !loading && (
          <div className="rounded-2xl border border-red-900 bg-red-950/40 p-6 text-sm text-red-300">
            Unable to fetch live security posture: {error}
          </div>
        )}

        {!loading && !error && backend && frontend && (
          <div className="space-y-8">
            <div className="grid gap-4 md:grid-cols-4">
              <div className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-5">
                <p className="text-xs uppercase tracking-[0.18em] text-neutral-500">Middleware</p>
                <p className="mt-3 text-3xl font-semibold text-emerald-400">{backend.middleware?.enabled ? 'On' : 'Off'}</p>
              </div>
              <div className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-5">
                <p className="text-xs uppercase tracking-[0.18em] text-neutral-500">Blocked IPs</p>
                <p className="mt-3 text-3xl font-semibold text-orange-300">{backend.middleware?.blocked_ips ?? 0}</p>
              </div>
              <div className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-5">
                <p className="text-xs uppercase tracking-[0.18em] text-neutral-500">Monitored IPs</p>
                <p className="mt-3 text-3xl font-semibold text-cyan-300">{backend.middleware?.monitored_ips ?? 0}</p>
              </div>
              <div className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-5">
                <p className="text-xs uppercase tracking-[0.18em] text-neutral-500">Threats Seen</p>
                <p className="mt-3 text-3xl font-semibold text-rose-300">{backend.middleware?.total_threats ?? 0}</p>
              </div>
            </div>

            <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
              <section className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <h2 className="text-xl font-semibold">Backend Protection Surface</h2>
                    <p className="mt-2 text-sm text-neutral-400">Live state from `/api/security/status`.</p>
                  </div>
                  <span className="rounded-full border border-emerald-800 bg-emerald-500/10 px-3 py-1 text-xs uppercase tracking-[0.18em] text-emerald-300">
                    {backend.status}
                  </span>
                </div>

                <div className="mt-6 grid gap-3 sm:grid-cols-2">
                  {backendProtections.map(([name, enabled]) => (
                    <div key={name} className="rounded-xl border border-neutral-800 bg-neutral-950/60 px-4 py-3">
                      <p className="text-sm text-neutral-300">{name.replaceAll('_', ' ')}</p>
                      <p className={`mt-2 text-sm font-medium ${enabled ? 'text-emerald-300' : 'text-red-300'}`}>
                        {enabled ? 'Enabled' : 'Disabled'}
                      </p>
                    </div>
                  ))}
                </div>

                <div className="mt-6 rounded-xl border border-neutral-800 bg-neutral-950/60 p-4">
                  <h3 className="text-sm font-semibold text-white">Last Threat</h3>
                  {backend.middleware?.last_threat ? (
                    <div className="mt-3 space-y-2 text-sm text-neutral-300">
                      <p>IP: <span className="text-white">{backend.middleware.last_threat.ip ?? 'Unavailable'}</span></p>
                      <p>Type: <span className="text-white">{backend.middleware.last_threat.threat_type ?? 'Unavailable'}</span></p>
                      <p>Threat count: <span className="text-white">{backend.middleware.last_threat.threat_count ?? 'Unavailable'}</span></p>
                      <p>Seen at: <span className="text-white">{formatUnixTimestamp(backend.middleware.last_threat.timestamp)}</span></p>
                    </div>
                  ) : (
                    <p className="mt-3 text-sm text-neutral-400">No threats recorded in the current in-memory runtime.</p>
                  )}
                </div>
              </section>

              <section className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6">
                <h2 className="text-xl font-semibold">Frontend Security Posture</h2>
                <p className="mt-2 text-sm text-neutral-400">Live output from the CSP and security-header generator used by the web app.</p>

                <div className="mt-6 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-xl border border-neutral-800 bg-neutral-950/60 px-4 py-3">
                    <p className="text-sm text-neutral-300">HSTS</p>
                    <p className={`mt-2 text-sm font-medium ${frontend.posture?.hsts ? 'text-emerald-300' : 'text-red-300'}`}>
                      {frontend.posture?.hsts ? 'Enabled' : 'Disabled'}
                    </p>
                  </div>
                  <div className="rounded-xl border border-neutral-800 bg-neutral-950/60 px-4 py-3">
                    <p className="text-sm text-neutral-300">CSP</p>
                    <p className={`mt-2 text-sm font-medium ${frontend.posture?.csp ? 'text-emerald-300' : 'text-red-300'}`}>
                      {frontend.posture?.csp ? 'Enabled' : 'Disabled'}
                    </p>
                  </div>
                  <div className="rounded-xl border border-neutral-800 bg-neutral-950/60 px-4 py-3">
                    <p className="text-sm text-neutral-300">Frame Protection</p>
                    <p className={`mt-2 text-sm font-medium ${frontend.posture?.frameProtection ? 'text-emerald-300' : 'text-red-300'}`}>
                      {frontend.posture?.frameProtection ? 'Enabled' : 'Disabled'}
                    </p>
                  </div>
                  <div className="rounded-xl border border-neutral-800 bg-neutral-950/60 px-4 py-3">
                    <p className="text-sm text-neutral-300">CSP Report URI</p>
                    <p className="mt-2 text-sm font-medium text-cyan-300">{frontend.posture?.reportUri ?? 'Unavailable'}</p>
                  </div>
                </div>

                <div className="mt-6 rounded-xl border border-neutral-800 bg-neutral-950/60 p-4">
                  <h3 className="text-sm font-semibold text-white">CSP Directives</h3>
                  <div className="mt-3 grid gap-2">
                    {cspDirectives.map(([name, enabled]) => (
                      <div key={name} className="flex items-center justify-between text-sm text-neutral-300">
                        <span>{name}</span>
                        <span className={enabled ? 'text-emerald-300' : 'text-neutral-500'}>{enabled ? 'Present' : 'Missing'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </section>
            </div>

            <section className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6">
              <h2 className="text-xl font-semibold">Observed Security Headers</h2>
              <p className="mt-2 text-sm text-neutral-400">These values come from the active header generator, not from hardcoded UI counters.</p>

              <div className="mt-6 overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead className="border-b border-neutral-800 text-neutral-500">
                    <tr>
                      <th className="pb-3 pr-6 font-medium">Header</th>
                      <th className="pb-3 font-medium">Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {keyHeaders.map((header) => (
                      <tr key={header.name} className="border-b border-neutral-900 align-top">
                        <td className="py-3 pr-6 font-mono text-cyan-300">{header.name}</td>
                        <td className="py-3 text-neutral-300 break-all">{header.value ?? 'Unavailable'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <div className="grid gap-8 lg:grid-cols-2">
              <section className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6">
                <h2 className="text-xl font-semibold">Backend Event History</h2>
                <p className="mt-2 text-sm text-neutral-400">Persisted `.jsonl` threat events from the backend middleware.</p>

                <div className="mt-6 space-y-3">
                  {(eventHistory?.events ?? []).length > 0 ? (
                    eventHistory?.events.map((event, index) => (
                      <div key={`${event.timestamp ?? 'event'}-${index}`} className="rounded-xl border border-neutral-800 bg-neutral-950/60 p-4 text-sm text-neutral-300">
                        <div className="flex items-center justify-between gap-4">
                          <span className="font-medium text-white">{event.event ?? event.threat_type ?? 'security_event'}</span>
                          <span className="text-xs text-neutral-500">{formatUnixTimestamp(event.timestamp)}</span>
                        </div>
                        <div className="mt-2 grid gap-1 text-xs text-neutral-400">
                          <p>IP: <span className="text-neutral-200">{event.ip ?? 'Unavailable'}</span></p>
                          <p>Threat type: <span className="text-neutral-200">{event.threat_type ?? 'Unavailable'}</span></p>
                          <p>Threat count: <span className="text-neutral-200">{event.threat_count ?? 'Unavailable'}</span></p>
                          <p>Blocked: <span className="text-neutral-200">{typeof event.blocked === 'boolean' ? String(event.blocked) : 'Unavailable'}</span></p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-neutral-400">No persisted backend security events yet.</p>
                  )}
                </div>
              </section>

              <section className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6">
                <h2 className="text-xl font-semibold">CSP Report History</h2>
                <p className="mt-2 text-sm text-neutral-400">Persisted browser CSP reports received by the web app.</p>

                <div className="mt-6 space-y-3">
                  {recentCspReports.length > 0 ? (
                    recentCspReports.map((report, index) => (
                      <div key={`${report.receivedAt ?? 'csp'}-${index}`} className="rounded-xl border border-neutral-800 bg-neutral-950/60 p-4 text-sm text-neutral-300">
                        <div className="flex items-center justify-between gap-4">
                          <span className="font-medium text-white">{report.effectiveDirective ?? report.violatedDirective ?? 'csp_report'}</span>
                          <span className="text-xs text-neutral-500">{report.receivedAt ? new Date(report.receivedAt).toLocaleString() : 'Unavailable'}</span>
                        </div>
                        <div className="mt-2 grid gap-1 text-xs text-neutral-400">
                          <p>Document: <span className="text-neutral-200 break-all">{report.documentUri ?? 'Unavailable'}</span></p>
                          <p>Blocked URI: <span className="text-neutral-200 break-all">{report.blockedUri ?? 'Unavailable'}</span></p>
                          <p>Disposition: <span className="text-neutral-200">{report.disposition ?? 'Unavailable'}</span></p>
                          <p>User agent: <span className="text-neutral-200 break-all">{report.userAgent ?? 'Unavailable'}</span></p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-neutral-400">No persisted CSP reports yet.</p>
                  )}
                </div>
              </section>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
