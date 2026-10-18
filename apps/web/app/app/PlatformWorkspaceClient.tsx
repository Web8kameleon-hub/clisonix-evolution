'use client';

import { useState } from 'react';
import PlatformHome from './PlatformHome';
import AppWorkspaceClient from './AppWorkspaceClient';

export default function PlatformWorkspaceClient() {
  const [showReports, setShowReports] = useState(false);

  if (showReports) {
    return (
      <div>
        <div className="mx-auto max-w-7xl px-5 pt-5">
          <button
            type="button"
            onClick={() => setShowReports(false)}
            className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-800 hover:bg-slate-50"
          >
            ← Back to workspace
          </button>
        </div>
        <AppWorkspaceClient />
      </div>
    );
  }

  return <PlatformHome onReports={() => setShowReports(true)} />;
}
