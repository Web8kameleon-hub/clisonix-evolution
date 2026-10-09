import type { Metadata } from 'next';
import NewHomePageClient from './NewHomePageClient';

const HOME_OG_IMAGE = 'https://www.clisonix.com/icons/icon-512x512.png';

export const metadata: Metadata = {
  title: 'Clisonix | Automated Business Reports',
  description:
    'Clisonix generates automated reports from public data and documents. From one command to Excel, Word, PDF, or PowerPoint.',
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'Clisonix | Automated Business Reports',
    description:
      'Generate client-ready reports from real data in minutes, not days.',
    url: 'https://www.clisonix.com',
    images: [
      {
        url: HOME_OG_IMAGE,
        width: 512,
        height: 512,
        alt: 'Clisonix report automation platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Clisonix | Automated Business Reports',
    description:
      'From one command to Excel, Word, PDF, or PowerPoint.',
    images: [HOME_OG_IMAGE],
  },
};

export default function HomePage() {
  return <NewHomePageClient />;
}
