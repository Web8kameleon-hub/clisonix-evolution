/**
 * ASI Demo Layout
 * ===============
 * 
 * Layout configuration for ASI demo page
 */

import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Clisonix ASI Demo',
  description: 'Interactive demonstration of Clisonix Artificial Superintelligence system with Trinity architecture',
  keywords: ['ASI', 'AI', 'Clisonix', 'Neural', 'Trinity', 'Intelligence'],
};

export default function ASIDemoLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}








