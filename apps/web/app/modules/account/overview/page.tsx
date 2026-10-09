import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Account & Billing Overview | Clisonix Modules',
  description:
    'Public overview of Clisonix Account & Billing module: profile controls, subscriptions, invoices, and payment settings.',
  alternates: {
    canonical: '/modules/account/overview',
  },
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    title: 'Account & Billing Overview | Clisonix',
    description:
      'Learn what the Clisonix account module provides before signing in.',
    url: 'https://www.clisonix.com/modules/account/overview',
    type: 'website',
  },
};

export default function AccountOverviewPage() {
  const schema = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'WebPage',
        name: 'Clisonix Account & Billing Overview',
        url: 'https://www.clisonix.com/modules/account/overview',
        description:
          'Public product overview for Clisonix account and billing controls.',
      },
      {
        '@type': 'BreadcrumbList',
        itemListElement: [
          { '@type': 'ListItem', position: 1, name: 'Home', item: 'https://www.clisonix.com/' },
          { '@type': 'ListItem', position: 2, name: 'Modules', item: 'https://www.clisonix.com/modules' },
          { '@type': 'ListItem', position: 3, name: 'Account Overview', item: 'https://www.clisonix.com/modules/account/overview' },
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
        <h1 className="mt-4 text-4xl font-bold md:text-5xl">Account & Billing</h1>
        <p className="mt-6 text-lg leading-8 text-slate-300">
          Manage profile identity, subscriptions, billing history, and payment methods in one secure dashboard.
        </p>

        <div className="mt-10 grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-5">
            <h2 className="text-xl font-semibold">What you can do</h2>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-slate-300">
              <li>Review active plans and invoices</li>
              <li>Manage payment methods and billing address</li>
              <li>Access subscription and portal controls</li>
            </ul>
          </div>
          <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-5">
            <h2 className="text-xl font-semibold">Access model</h2>
            <p className="mt-3 text-slate-300">
              This module requires account authentication to protect personal and financial data.
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
