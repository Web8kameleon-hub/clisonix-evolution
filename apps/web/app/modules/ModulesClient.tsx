'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import {
  Brain,
  Settings,
  ChevronRight,
  Search,
  Command,
  ExternalLink,
  User,
} from 'lucide-react';
import {
  PLATFORM_LABELS,
  getModulePlatformById,
  getModulePlatformByRoute,
} from '../../src/lib/modules/platform-map';
import { moduleCatalog, accentColors } from './modules-catalog';

interface SessionUser {
  id: string;
  name: string;
  email: string;
}

const SUPPORT_EMAIL = process.env.NEXT_PUBLIC_SUPPORT_EMAIL || '';
const PRIVATE_MODULE_IDS = new Set(['account', 'my-data-dashboard', 'mymirror-now']);

export default function ModulesClient() {
  const [currentUser, setCurrentUser] = useState<SessionUser | null>(null);
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    let active = true;

    const loadProfile = async () => {
      try {
        const response = await fetch('/api/user/profile', { cache: 'no-store' });
        if (!response.ok) { if (active) setCurrentUser(null); return; }

        const payload = await response.json();
        const data =
          payload && typeof payload === 'object' && 'data' in payload
            ? (payload as { data?: SessionUser }).data
            : (payload as SessionUser);

        if (active && data?.id) setCurrentUser(data);
      } catch {
        if (active) setCurrentUser(null);
      }
    };

    loadProfile();
    return () => { active = false; };
  }, []);

  const visibleModules = currentUser
    ? moduleCatalog
    : moduleCatalog.filter((m) => !PRIVATE_MODULE_IDS.has(m.id));

  const categories = ['all', ...new Set(visibleModules.map((m) => m.category))];

  const filteredModules = visibleModules.filter((m) => {
    const matchesCategory = activeCategory === 'all' || m.category === activeCategory;
    const matchesSearch =
      m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-white text-slate-900">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-gray-50 border-r border-slate-200 z-50">
        <div className="h-16 flex items-center px-5 border-b border-slate-200">
          <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold tracking-tight">Clisonix</span>
          </Link>
        </div>

        <nav className="p-4 space-y-1">
          <div className="text-[11px] font-medium text-black uppercase tracking-wider px-3 mb-3">
            Modules
          </div>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                activeCategory === cat
                  ? 'bg-gray-100 text-black border-2 border-black'
                  : 'text-black hover:text-black hover:bg-gray-100'
              }`}
            >
              {cat === 'all' ? 'All Modules' : cat}
            </button>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-200">
          {currentUser ? (
            <Link
              href="/modules/account"
              className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-black hover:bg-gray-100 transition-all"
            >
              <Settings className="w-4 h-4" />
              Settings
            </Link>
          ) : (
            <Link
              href="/sign-in"
              className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-black hover:bg-gray-100 transition-all"
            >
              <User className="w-4 h-4" />
              Sign in
            </Link>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64">
        {/* Top Bar */}
        <header className="h-16 flex items-center justify-between px-8 border-b border-slate-200 bg-white/80 backdrop-blur-xl sticky top-0 z-40">
          <div className="relative w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-black" />
            <input
              type="text"
              placeholder="Search modules..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-10 pl-10 pr-4 bg-slate-50 border border-slate-200 rounded-lg text-sm text-black placeholder:text-black/50 focus:outline-none focus:border-black transition-colors"
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 text-black">
              <Command className="w-3 h-3" />
              <span className="text-xs">K</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {currentUser ? (
              <Link
                href="/modules/account"
                className="flex items-center gap-3 rounded-lg border border-slate-200 px-3 py-2 text-sm hover:bg-slate-50 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center text-sm font-medium text-white">
                  {currentUser.name?.trim()?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <div className="text-left leading-tight">
                  <div className="font-medium text-black">{currentUser.name || currentUser.email}</div>
                  <div className="text-xs text-black/60">Account</div>
                </div>
              </Link>
            ) : (
              <Link
                href="/sign-in"
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-black hover:bg-slate-50 transition-colors"
              >
                Sign in
              </Link>
            )}
          </div>
        </header>

        {/* Content */}
        <div className="p-8">
          <div className="mb-8">
            <h1 className="text-2xl font-semibold tracking-tight mb-2">
              {activeCategory === 'all' ? 'All Modules' : activeCategory}
            </h1>
            <p className="text-black text-sm">
              {filteredModules.length}{' '}
              {filteredModules.length === 1 ? 'module' : 'modules'} available
            </p>
            <div className="mt-3">
              <Link
                href="/modules/how-to-use"
                className="inline-flex items-center gap-2 text-sm font-medium text-black hover:text-black/70 transition-colors"
              >
                Module how-to documentation
                <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* Modules Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filteredModules.map((module) => {
              const colors = accentColors[module.accent as keyof typeof accentColors];
              const Icon = module.icon;
              const isExternal = 'external' in module && module.external;
              const platformInfo =
                getModulePlatformById(module.id) || getModulePlatformByRoute(module.href);
              const platformLabel = platformInfo
                ? PLATFORM_LABELS[platformInfo.platform]
                : 'Unmapped';

              const CardContent = (
                <>
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-10 h-10 rounded-lg ${colors.bg} flex items-center justify-center`}>
                      <Icon className={`w-5 h-5 ${colors.icon}`} aria-hidden="true" />
                    </div>
                    <div className="flex items-center gap-2">
                      {isExternal && <ExternalLink className="w-3 h-3 text-slate-500" aria-hidden="true" />}
                      <span className={`px-2 py-1 rounded text-[11px] font-medium ${colors.badge}`}>
                        {module.category}
                      </span>
                      <span className="px-2 py-1 rounded text-[11px] font-medium bg-gray-200 text-black">
                        {platformLabel}
                      </span>
                    </div>
                  </div>

                  <h3 className="text-[15px] font-medium mb-1.5 group-hover:text-white transition-colors">
                    {module.name}
                  </h3>
                  <p className="text-sm text-black leading-relaxed mb-4">{module.description}</p>

                  <div className={`flex items-center gap-1 text-sm font-medium ${colors.text} opacity-0 group-hover:opacity-100 transition-opacity`}>
                    <span>{isExternal ? 'Open in new tab' : 'Open'}</span>
                    {isExternal ? (
                      <ExternalLink className="w-4 h-4" aria-hidden="true" />
                    ) : (
                      <ChevronRight className="w-4 h-4" aria-hidden="true" />
                    )}
                  </div>
                </>
              );

              return isExternal ? (
                <a
                  key={`${module.id}-${module.href}`}
                  href={module.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`group relative p-5 rounded-lg border-2 border-black bg-white shadow-sm ${colors.border} ${colors.borderHover} transition-all duration-200 hover:bg-gray-100`}
                >
                  {CardContent}
                </a>
              ) : (
                <Link
                  key={`${module.id}-${module.href}`}
                  href={module.href}
                  className={`group relative p-5 rounded-lg border-2 border-black bg-white shadow-sm ${colors.border} ${colors.borderHover} transition-all duration-200 hover:bg-gray-100`}
                >
                  {CardContent}
                </Link>
              );
            })}
          </div>

          {filteredModules.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16">
              <div className="w-12 h-12 rounded-lg bg-slate-800 flex items-center justify-center mb-4">
                <Search className="w-6 h-6 text-black" aria-hidden="true" />
              </div>
              <h3 className="text-lg font-medium mb-2">No modules found</h3>
              <p className="text-black text-sm">Try adjusting your search or filter criteria</p>
            </div>
          )}
        </div>

        <footer className="border-t border-slate-200 mt-8">
          <div className="px-8 py-6 flex items-center justify-between text-sm text-black">
            <div className="flex items-center gap-6">
              <Link href="/developers" className="hover:text-black transition-colors">
                Documentation
              </Link>
              <Link href="/modules/how-to-use" className="hover:text-black transition-colors">
                How to Use Modules
              </Link>
              <a
                href="https://github.com/Web8kameleon-hub/clisonix.com"
                className="hover:text-black transition-colors"
              >
                GitHub
              </a>
              {SUPPORT_EMAIL ? (
                <a
                  href={`mailto:${SUPPORT_EMAIL}`}
                  className="hover:text-black transition-colors"
                >
                  {SUPPORT_EMAIL}
                </a>
              ) : (
                <span className="text-black/60">Support unavailable</span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span>Clisonix</span>
              <span className="text-black">·</span>
              <span className="text-black">© 2026</span>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
