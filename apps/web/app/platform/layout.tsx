import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Clisonix Platform | Official AI Infrastructure Overview',
  description:
    'Official platform overview for Clisonix at www.clisonix.com, covering AI infrastructure, EEG tooling, APIs, analytics, and production modules.',
  alternates: {
    canonical: '/platform',
  },
  keywords: [
    'clisonix platform',
    'official clisonix platform',
    'clisonix.com',
    'ai infrastructure overview',
    'eeg and analytics platform',
  ],
  openGraph: {
    title: 'Clisonix Platform | Official AI Infrastructure Overview',
    description:
      'Learn how the official Clisonix platform combines AI workflows, research systems, analytics, and infrastructure modules at www.clisonix.com.',
    url: 'https://www.clisonix.com/platform',
    siteName: 'Clisonix',
    type: 'website',
  },
};

export default function PlatformLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
