import type { Metadata } from 'next';
import Link from 'next/link';

type DocsEntry = {
  title: string;
  href: string;
  summary: string;
  external?: boolean;
};

const productDocs: DocsEntry[] = [
  {
    title: 'Developer Portal',
    href: '/developers',
    summary: 'Live API endpoints, playground, code examples, and pricing tiers.',
  },
  {
    title: 'Modules How-to Use',
    href: '/modules/how-to-use',
    summary: 'Practical step-by-step usage instructions for each major module.',
  },
  {
    title: 'Platform Overview',
    href: '/platform',
    summary: 'High-level architecture and product capabilities for Clisonix.',
  },
  {
    title: 'Company Information',
    href: '/company',
    summary: 'Official brand and company context for trust and verification.',
  },
  {
    title: 'FAQ',
    href: '/faq',
    summary: 'Brand clarification and recurring questions about the platform.',
  },
];

const repositoryDocs: DocsEntry[] = [
  {
    title: 'CLISONIX_USER_GUIDE.md',
    href: 'https://github.com/Web8kameleon-hub/clisonix.com/blob/main/CLISONIX_USER_GUIDE.md',
    summary: 'User-level guide for platform usage and workflows.',
    external: true,
  },
  {
    title: 'API_DOCS.md',
    href: 'https://github.com/Web8kameleon-hub/clisonix.com/blob/main/API_DOCS.md',
    summary: 'API reference notes and integration context from repository docs.',
    external: true,
  },
  {
    title: 'DOCS_INDEX.md',
    href: 'https://github.com/Web8kameleon-hub/clisonix.com/blob/main/DOCS_INDEX.md',
    summary: 'Repository-level documentation index for broader navigation.',
    external: true,
  },
  {
    title: 'CLISONIX_INTELLIGENCE_README.md',
    href: 'https://github.com/Web8kameleon-hub/clisonix.com/blob/main/CLISONIX_INTELLIGENCE_README.md',
    summary: 'Intelligence architecture notes and system context.',
    external: true,
  },
  {
    title: 'BUILD.md',
    href: 'https://github.com/Web8kameleon-hub/clisonix.com/blob/main/BUILD.md',
    summary: 'Build and runtime operational guidance.',
    external: true,
  },
];

const allDocs = [...productDocs, ...repositoryDocs];

export const metadata: Metadata = {
  title: 'Enterprise Docs Index | Clisonix',
  description:
    'Central enterprise documentation index for Clisonix with product docs, module how-to guides, API references, and official repository documentation.',
  alternates: {
    canonical: '/developers/docs-index',
  },
  openGraph: {
    title: 'Clisonix Enterprise Docs Index',
    description:
      'Single source of truth for Clisonix documentation: platform guides, module usage, APIs, and repository docs.',
    url: 'https://www.clisonix.com/developers/docs-index',
  },
};

export default function EnterpriseDocsIndexPage() {
  const docsSchema = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'CollectionPage',
        name: 'Clisonix Enterprise Docs Index',
        description:
          'Central enterprise documentation index for Clisonix including platform docs, module guides, and repository references.',
        url: 'https://www.clisonix.com/developers/docs-index',
        hasPart: allDocs.map((doc, index) => ({
          '@type': 'CreativeWork',
          position: index + 1,
          name: doc.title,
          url: doc.external ? doc.href : `https://www.clisonix.com${doc.href}`,
          description: doc.summary,
        })),
      },
      {
        '@type': 'BreadcrumbList',
        itemListElement: [
          {
            '@type': 'ListItem',
            position: 1,
            name: 'Home',
            item: 'https://www.clisonix.com',
          },
          {
            '@type': 'ListItem',
            position: 2,
            name: 'Developers',
            item: 'https://www.clisonix.com/developers',
          },
          {
            '@type': 'ListItem',
            position: 3,
            name: 'Docs Index',
            item: 'https://www.clisonix.com/developers/docs-index',
          },
        ],
      },
    ],
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(docsSchema) }}
      />

      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="max-w-3xl">
          <nav className="mb-4 text-sm text-slate-400" aria-label="Breadcrumb">
            <Link href="/" className="hover:text-white">Home</Link>
            <span className="mx-2">/</span>
            <Link href="/developers" className="hover:text-white">Developers</Link>
            <span className="mx-2">/</span>
            <span className="text-slate-200">Docs Index</span>
          </nav>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-300">Enterprise Documentation</p>
          <h1 className="mt-4 text-4xl font-bold md:text-5xl">Clisonix Docs Index</h1>
          <p className="mt-5 text-lg text-slate-300 leading-8">
            Centralized documentation index optimized for enterprise onboarding, SEO discoverability, and operational clarity.
          </p>
        </div>

        <div className="mt-10 grid gap-8 md:grid-cols-2">
          <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
            <h2 className="text-2xl font-semibold">Product Documentation</h2>
            <p className="mt-2 text-sm text-slate-400">Official pages hosted on the Clisonix platform.</p>
            <div className="mt-5 space-y-3">
              {productDocs.map((doc) => (
                <Link
                  key={doc.title}
                  href={doc.href}
                  className="block rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 hover:border-emerald-500/50"
                >
                  <div className="font-semibold text-white">{doc.title}</div>
                  <div className="mt-1 text-sm text-slate-300">{doc.summary}</div>
                </Link>
              ))}
            </div>
          </section>

          <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
            <h2 className="text-2xl font-semibold">Repository Documentation</h2>
            <p className="mt-2 text-sm text-slate-400">Technical references and markdown docs from the official repository.</p>
            <div className="mt-5 space-y-3">
              {repositoryDocs.map((doc) => (
                <a
                  key={doc.title}
                  href={doc.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 hover:border-emerald-500/50"
                >
                  <div className="font-semibold text-white">{doc.title}</div>
                  <div className="mt-1 text-sm text-slate-300">{doc.summary}</div>
                </a>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
