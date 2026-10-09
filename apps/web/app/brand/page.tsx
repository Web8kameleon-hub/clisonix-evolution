import type { Metadata } from 'next';
import Link from 'next/link';

const brandFacts = [
  { label: 'Official domain', value: 'https://www.clisonix.com' },
  { label: 'Category', value: 'AI, neuroscience, research, and developer software' },
  { label: 'Operator', value: 'Clisonix Cloud (registered legal entity: ABA GmbH)' },
];

export const metadata: Metadata = {
  title: 'Brand Verification | Clisonix',
  description:
    'Official brand verification for Clisonix. Clisonix is the AI and neuroscience software platform at www.clisonix.com and is not related to Clarisonic beauty devices.',
  alternates: {
    canonical: '/brand',
  },
  openGraph: {
    title: 'Clisonix Brand Verification',
    description:
      'Verify the official Clisonix domain, company identity, and brand disambiguation for search engines, partners, and users.',
    url: 'https://www.clisonix.com/brand',
  },
};

export default function BrandPage() {
  const brandSchema = {
    '@context': 'https://schema.org',
    '@type': 'Brand',
    name: 'Clisonix',
    alternateName: ['Clisonix Cloud', 'Clisonix AI'],
    url: 'https://www.clisonix.com/brand',
    logo: 'https://www.clisonix.com/apple-touch-icon.png',
    description:
      'Clisonix is an AI and neuroscience software platform for research, EEG analysis, neural workflows, and real-time analytics.',
    disambiguatingDescription:
      'Clisonix is unrelated to Clarisonic skin-care devices, beauty products, and other similarly named brands.',
    sameAs: ['https://github.com/Web8kameleon-hub/clisonix.com'],
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(brandSchema) }}
      />

      <div className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-20">
        <div className="max-w-4xl">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-300">Official brand verification</p>
          <h1 className="mt-4 text-4xl font-bold md:text-5xl">Clisonix is the official AI and neuroscience platform at www.clisonix.com</h1>
          <p className="mt-6 text-lg leading-8 text-slate-300">
            This page exists to help search engines, partners, and users clearly distinguish <strong className="text-white">Clisonix</strong>
            {' '}from similarly named brands such as <strong className="text-white">Clarisonic</strong> and unrelated third-party services.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {brandFacts.map((fact) => (
            <div key={fact.label} className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-5">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-emerald-200">{fact.label}</p>
              <p className="mt-3 text-base text-slate-100">{fact.value}</p>
            </div>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
            <h2 className="text-2xl font-semibold">What Clisonix is</h2>
            <ul className="mt-4 space-y-3 text-slate-300">
              <li>• AI workflows and research tools</li>
              <li>• EEG analysis, neural synthesis, and cognitive tooling</li>
              <li>• Real-time analytics, APIs, SDKs, and production infrastructure</li>
            </ul>
          </section>

          <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6">
            <h2 className="text-2xl font-semibold">What Clisonix is not</h2>
            <ul className="mt-4 space-y-3 text-slate-300">
              <li>• Not affiliated with Clarisonic facial cleansing brushes or beauty products</li>
              <li>• Not a skincare, cosmetics, or beauty-device company</li>
              <li>• Not the same entity as other similarly named organizations</li>
            </ul>
          </section>
        </div>

        <section className="rounded-3xl border border-blue-500/20 bg-blue-500/10 p-6">
          <h2 className="text-2xl font-semibold text-white">Need more verification?</h2>
          <p className="mt-3 max-w-3xl text-slate-200">
            Review the company profile, FAQ, and platform pages for consistent ownership, product descriptions, and links from the official Clisonix domain.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link href="/company" className="rounded-lg bg-emerald-600 px-4 py-2 font-semibold text-white hover:bg-emerald-500">
              Company page
            </Link>
            <Link href="/faq" className="rounded-lg border border-slate-600 px-4 py-2 font-semibold text-slate-100 hover:border-emerald-400 hover:text-emerald-300">
              FAQ
            </Link>
            <Link href="/modules" className="rounded-lg border border-slate-600 px-4 py-2 font-semibold text-slate-100 hover:border-emerald-400 hover:text-emerald-300">
              Platform modules
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
