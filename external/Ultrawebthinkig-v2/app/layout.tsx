/**
 * Web8 Root Layout - Real Data Architecture
 * NO artificial metadata, ONLY verified runtime data
 */

import * as React from 'react';
import PerformanceMonitor from '@/components/PerformanceMonitor';
import type { Metadata, Viewport } from 'next';

interface RootLayoutProps {
  children: React.ReactNode;
}

export const metadata: Metadata = {
  title: 'UltraWebThinking NeuroSonix - Neural Enhanced AGI Platform',
  description: 'Neural frequency enhanced cognitive processing with ASI and NeuroSonix integration',
  icons: {
    icon: [{ url: '/favicon.svg', type: 'image/svg+xml' }],
  },
  manifest: '/site.webmanifest',
};

export const viewport: Viewport = {
  themeColor: '#6366f1',
  width: 'device-width',
  initialScale: 1,
};

// Web8 Dynamic Export - NO default exports
function RootLayout({ children }: RootLayoutProps) {

  return (
    <html lang="en">
      <body className="web8-accelerated" suppressHydrationWarning={true}>
        {/* Web8 Pure Children - NO artificial providers */}
        {children}

        {/* Web8 Performance Monitor - Global System Monitoring */}
        <React.Suspense fallback={null}>
          <PerformanceMonitor />
        </React.Suspense>
      </body>
    </html>
  );
}

// Web8 Dynamic Export - NO default exports (Named export)
export { RootLayout };

// Next.js App Router compatibility requirement
export default RootLayout;
