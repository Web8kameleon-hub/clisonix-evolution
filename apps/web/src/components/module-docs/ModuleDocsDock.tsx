'use client';

import { ChevronUp } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';

import { getModuleGuideByHref } from '../../lib/module-docs';

function toTitleFromSlug(slug: string): string {
  return slug
    .split('-')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

export default function ModuleDocsDock() {
  const pathname = usePathname() || '';
  const [collapsed, setCollapsed] = useState(false);

  const shouldRenderDock =
    pathname.startsWith('/modules/') &&
    pathname !== '/modules' &&
    pathname !== '/modules/how-to-use';

  const normalizedPath = pathname.endsWith('/') ? pathname.slice(0, -1) : pathname;
  const staticGuide = getModuleGuideByHref(normalizedPath);
  const slug = normalizedPath.split('/')[2] || '';

  const name = staticGuide?.name || toTitleFromSlug(slug) || 'Module';
  const summary =
    staticGuide?.summary ||
    'Practical usage guide for this module, including a simple operational flow and best-practice execution order.';
  const howTo =
    staticGuide?.howTo ||
    (['Open this module', 'Configure inputs and required settings', 'Run workflow and review outputs'] as [string, string, string]);

  useEffect(() => {
    if (!shouldRenderDock) {
      return;
    }

    try {
      const persisted = window.localStorage.getItem('clisonix.moduleDocsDock.collapsed');
      if (persisted === '1') {
        setCollapsed(true);
        return;
      }
      if (persisted === '0') {
        setCollapsed(false);
        return;
      }

      const isMobileViewport = window.matchMedia('(max-width: 767px)').matches;
      setCollapsed(isMobileViewport);
    } catch {
      setCollapsed(false);
    }
  }, [shouldRenderDock]);

  if (!shouldRenderDock) {
    return null;
  }

  const toggleCollapsed = () => {
    setCollapsed((prev) => {
      const next = !prev;
      try {
        window.localStorage.setItem('clisonix.moduleDocsDock.collapsed', next ? '1' : '0');
      } catch {
      }
      return next;
    });
  };

  return (
    <aside
      className={`fixed bottom-4 right-4 z-[70] rounded-xl border border-emerald-500/40 bg-slate-950/95 shadow-2xl backdrop-blur transition-all duration-300 ease-out ${
        collapsed ? 'w-[220px] p-3' : 'w-[330px] p-4'
      }`}
    >
      {collapsed ? (
        <div className="flex items-center justify-between gap-2">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wide text-emerald-300">How to use</p>
            <p className="text-xs text-slate-200">{name}</p>
          </div>
          <button
            type="button"
            onClick={toggleCollapsed}
            className="inline-flex items-center gap-1 rounded-md border border-emerald-400/50 px-2 py-1 text-[11px] font-semibold text-emerald-200 hover:bg-emerald-500/20"
            aria-label="Expand module docs"
          >
            <ChevronUp className="h-3 w-3 rotate-180 transition-transform duration-300" />
            Open
          </button>
        </div>
      ) : (
        <>
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-wide text-emerald-300">How to use</p>
              <h3 className="mt-1 text-sm font-semibold text-white">{name}</h3>
              <p className="mt-1 text-xs text-slate-300 leading-5">{summary}</p>
            </div>
            <Link
              href="/modules/how-to-use"
              className="rounded-md border border-emerald-400/50 px-2 py-1 text-[11px] font-semibold text-emerald-200 hover:bg-emerald-500/20"
            >
              Docs
            </Link>
          </div>

          <div className="mt-3 flex items-center justify-end">
            <button
              type="button"
              onClick={toggleCollapsed}
              className="inline-flex items-center gap-1 rounded-md border border-emerald-400/40 px-2 py-1 text-[11px] font-semibold text-emerald-200 hover:bg-emerald-500/20"
              aria-label="Collapse module docs"
            >
              <ChevronUp className="h-3 w-3 transition-transform duration-300" />
              Minimize
            </button>
          </div>

          <ol className="mt-3 space-y-1.5 text-xs text-slate-200">
            <li>1. {howTo[0]}</li>
            <li>2. {howTo[1]}</li>
            <li>3. {howTo[2]}</li>
          </ol>
        </>
      )}
    </aside>
  );
}
