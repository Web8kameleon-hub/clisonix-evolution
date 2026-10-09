import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Clisonix Developers | API Reference, Endpoints, and Integration Docs',
  description:
    'Official developer page for Clisonix APIs, endpoint coverage, integration guidance, and production-ready AI platform tooling.',
  alternates: {
    canonical: '/developers',
  },
  openGraph: {
    title: 'Clisonix Developers | API Reference, Endpoints, and Integration Docs',
    description:
      'Build on Clisonix with live API endpoints, integration docs, and production-ready developer tooling.',
    url: 'https://www.clisonix.com/developers',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Clisonix Developers | API Reference, Endpoints, and Integration Docs',
    description:
      'Build on Clisonix with live API endpoints, integration docs, and production-ready developer tooling.',
  },
};

export default function DevelopersLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return children;
}
