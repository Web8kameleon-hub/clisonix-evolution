import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'My Data Dashboard Overview | Clisonix Modules',
  description:
    'Public overview of Clisonix My Data Dashboard for IoT streams, API integrations, and operational telemetry workflows.',
  alternates: {
    canonical: '/modules/my-data-dashboard/overview',
  },
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    title: 'My Data Dashboard Overview | Clisonix',
    description:
      'See how Clisonix My Data Dashboard connects IoT and API data before you sign in.',
    url: 'https://www.clisonix.com/modules/my-data-dashboard/overview',
    type: 'website',
  },
};

export default function MyDataOverviewPage() {
  const schema = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'WebPage',
        name: 'Clisonix My Data Dashboard Overview',
        url: 'https://www.clisonix.com/modules/my-data-dashboard/overview',
        description:
          'Public product overview for Clisonix telemetry and integrations dashboard.',
      },
      {
        '@type': 'BreadcrumbList',
        itemListElement: [
          { '@type': 'ListItem', position: 1, name: 'Home', item: 'https://www.clisonix.com/' },
          { '@type': 'ListItem', position: 2, name: 'Modules', item: 'https://www.clisonix.com/modules' },
          { '@type': 'ListItem', position: 3, name: 'My Data Dashboard Overview', item: 'https://www.clisonix.com/modules/my-data-dashboard/overview' },
        ],
      },
    ],
  };

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-16 text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />

      <div className="mx-auto max-w-4xl">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-300">Public Module Overview</p>
        <h1 className="mt-4 text-4xl font-bold md:text-5xl">My Data Dashboard</h1>
        <p className="mt-6 text-lg leading-8 text-slate-300">
          Connect data sources, monitor IoT metrics, and track API-based telemetry with a single operational dashboard.
        </p>

        <div className="mt-10 grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-5">
            <h2 className="text-xl font-semibold">Key capabilities</h2>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-slate-300">
              <li>IoT and sensor stream aggregation</li>
              <li>API source monitoring and health checks</li>
              <li>Operational metrics with export workflows</li>
            </ul>
          </div>
          <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-5">
            <h2 className="text-xl font-semibold">Access model</h2>
            <p className="mt-3 text-slate-300">
              This module is account-protected because it can expose user-owned telemetry and private integrations.
            </p>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/sign-up" className="rounded-lg bg-cyan-600 px-4 py-2 font-semibold text-white hover:bg-cyan-500">
            Create account
          </Link>
          <Link href="/sign-in" className="rounded-lg border border-slate-600 px-4 py-2 font-semibold text-slate-100 hover:border-cyan-400 hover:text-cyan-300">
            Sign in
          </Link>
          <Link href="/modules" className="rounded-lg border border-slate-600 px-4 py-2 font-semibold text-slate-100 hover:border-cyan-400 hover:text-cyan-300">
            All modules
          </Link>
        </div>
      </div>
    </main>
  );
}
