import Link from 'next/link';

import { getModuleGuideById } from '../../lib/module-docs';

type ModuleHowToCardProps = {
  moduleId: string;
  variant?: 'light' | 'dark';
};

export default function ModuleHowToCard({ moduleId, variant = 'light' }: ModuleHowToCardProps) {
  const guide = getModuleGuideById(moduleId);

  if (!guide) {
    return null;
  }

  const isDark = variant === 'dark';

  return (
    <section
      className={isDark
        ? 'rounded-xl border border-violet-500/30 bg-violet-500/10 p-4'
        : 'rounded-xl border border-slate-200 bg-white p-4'}
      aria-label={`How to use ${guide.name}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className={isDark ? 'text-xs font-semibold uppercase tracking-wide text-violet-300' : 'text-xs font-semibold uppercase tracking-wide text-slate-500'}>
            How to use
          </p>
          <h2 className={isDark ? 'mt-1 text-lg font-semibold text-white' : 'mt-1 text-lg font-semibold text-slate-900'}>{guide.name}</h2>
          <p className={isDark ? 'mt-1 text-sm text-slate-300' : 'mt-1 text-sm text-slate-600'}>{guide.summary}</p>
        </div>
        <Link
          href="/modules/how-to-use"
          className={isDark
            ? 'whitespace-nowrap rounded-lg border border-violet-400/40 bg-violet-500/10 px-3 py-2 text-xs font-semibold text-violet-200 hover:bg-violet-500/20'
            : 'whitespace-nowrap rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100'}
        >
          Full docs
        </Link>
      </div>

      <ol className={isDark ? 'mt-3 space-y-1.5 text-sm text-slate-200' : 'mt-3 space-y-1.5 text-sm text-slate-700'}>
        <li>1. {guide.howTo[0]}</li>
        <li>2. {guide.howTo[1]}</li>
        <li>3. {guide.howTo[2]}</li>
      </ol>
    </section>
  );
}
