/**
 * Clisonix Modules Layout
 * Advanced neuroacoustic processing, EEG analysis, and industrial monitoring
 */

import { Metadata } from 'next'
import ModuleDocsDock from '../../src/components/module-docs/ModuleDocsDock'

export const metadata: Metadata = {
  alternates: {
    canonical: '/modules',
  },
}

export default function ModulesLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {children}
      </div>
      <ModuleDocsDock />
    </div>
  )
}








