'use client';

import Link from 'next/link';
import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

const SUPPORT_EMAIL = process.env.NEXT_PUBLIC_SUPPORT_EMAIL || '';
const PUBLIC_DOMAIN = process.env.NEXT_PUBLIC_PUBLIC_DOMAIN || '';

const MODULES = [
  {
    id: 'curiosity-ocean',
    name: 'Curiosity Ocean',
    description: 'AI-powered chat interface for exploring knowledge',
    icon: '🌊',
    color: 'from-emerald-500 to-teal-600',
    category: 'AI Chat',
    featured: true,
  },
  {
    id: 'web-reader',
    name: 'Web Reader',
    description: 'Browse any webpage, search the web, chat with page content with Ocean Core',
    icon: '🌐',
    color: 'from-blue-500 to-cyan-600',
    category: 'AI Chat',
    isNew: true,
    featured: true,
  },
  {
    id: 'archive',
    name: 'Archive & Research',
    description: 'Search ArXiv, Wikipedia, PubMed and 5000+ global data sources',
    icon: '📜',
    color: 'from-indigo-500 to-violet-600',
    category: 'Research',
    isNew: true,
    featured: false,
  },
  {
    id: 'eeg-analysis',
    name: 'EEG Analysis',
    description: 'Real-time brainwave pattern analysis',
    icon: '🧠',
    color: 'from-purple-500 to-pink-600',
    category: 'Neuroscience',
    featured: false,
  },
  {
    id: 'neural-synthesis',
    name: 'Neural Synthesis',
    description: 'Synthesize neural patterns and waveforms',
    icon: '⚡',
    color: 'from-yellow-500 to-orange-600',
    category: 'Neuroscience',
    featured: false,
  },
  {
    id: 'weather-dashboard',
    name: 'Weather & Cognitive',
    description: 'How weather impacts cognitive performance',
    icon: '🌤️',
    color: 'from-sky-500 to-teal-600',
    category: 'Environment',
    featured: false,
  },
  {
    id: 'account',
    name: 'Account & Billing',
    description: 'Manage your profile, subscriptions, payment methods and settings',
    icon: '👤',
    color: 'from-emerald-500 to-teal-600',
    category: 'Account',
    featured: false,
  },
  {
    id: 'my-data-dashboard',
    name: 'My Data Dashboard',
    description: 'IoT devices, API integrations, LoRa/GSM networks',
    icon: '📊',
    color: 'from-green-500 to-teal-600',
    category: 'Data',
    featured: false,
  },
  {
    id: 'developer-docs',
    name: 'Developer Documentation',
    description: 'API Reference, SDKs, Quick Start Guide',
    icon: '👨‍💻',
    color: 'from-purple-500 to-pink-600',
    category: 'Developer',
    featured: false,
  },
] as const;

const NAV_ITEMS = [
  { href: '#asi-trinity', label: 'ASI Trinity', accent: 'emerald', isRoute: false },
  { href: '#modules', label: 'Tools', accent: 'emerald', isRoute: false },
  { href: '#tech-stack', label: 'Why Us', accent: 'emerald', isRoute: false },
  { href: '/modules', label: 'Dashboard', accent: 'emerald', isRoute: true },
] as const;

const WHY_US_PILLARS = [
  {
    icon: '🏗️',
    title: 'Multi-Service by Design',
    description: 'The repo is organized as an industrial multi-service platform: API, Ocean, ALBA, ALBI, JONA, payments, analytics, content, observability and more — orchestrated with Docker Compose instead of a single fragile app.',
    proof: 'Real service boundaries and isolated containers'
  },
  {
    icon: '📈',
    title: 'Built-In Observability',
    description: 'Prometheus, Grafana, Loki, Jaeger, Tempo and health/status endpoints are part of the platform story, so operations and debugging are first-class instead of an afterthought.',
    proof: 'Monitoring stack and health endpoints already documented'
  },
  {
    icon: '🧰',
    title: 'Developer-First Delivery',
    description: 'Clisonix ships with OpenAPI, official Python and TypeScript SDKs, developer docs, and integration-friendly APIs so teams can plug in quickly without reverse engineering the platform.',
    proof: 'SDKs + API docs + module docs in repo'
  },
  {
    icon: '💳',
    title: 'Real Business Workflows',
    description: 'This is not a demo-only AI site. The repo includes authentication, billing, Stripe/PayPal/SEPA flows, quotas, webhooks and user/account flows needed for production software.',
    proof: 'Payments, auth and quotas are already implemented'
  },
] as const;

const WHY_US_REFERENCES = [
  { label: 'Platform', href: '/platform' },
  { label: 'Developer Docs', href: '/modules/developer-docs' },
  { label: 'Modules', href: '/modules' },
  { label: 'Why Clisonix', href: '/why-clisonix' },
] as const;

export default function HomePageClient() {
  const router = useRouter();

  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [greeting, setGreeting] = useState<string>('Welcome');
  const [query, setQuery] = useState<string>('');
  const [wsConnected, setWsConnected] = useState(false);
  const [streamProbeOk, setStreamProbeOk] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const seqRef = useRef<number>(0);
  const debounceRef = useRef<number | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const shouldReconnectRef = useRef<boolean>(true);
  const [recent, setRecent] = useState<string[]>([]);

  const categories = ['all', ...new Set(MODULES.map((module) => module.category))];
  const filteredModules = selectedCategory === 'all' ? MODULES : MODULES.filter((module) => module.category === selectedCategory);

  useEffect(() => {
    const h = new Date().getHours();
    setGreeting(h < 12 ? 'Good morning' : h < 18 ? 'Good afternoon' : 'Good evening');

    try {
      const raw = localStorage.getItem('clx_recent_modules');
      if (raw) setRecent(JSON.parse(raw));
    } catch (e) {
      // ignore
    }
  }, []);

  useEffect(() => {
    let stopped = false;

    const probe = async () => {
      try {
        const response = await fetch('/api/debate/stream', {
          method: 'GET',
          cache: 'no-store',
        });
        if (stopped) return;
        setStreamProbeOk(response.status === 405 || response.ok);
      } catch {
        if (!stopped) setStreamProbeOk(false);
      }
    };

    void probe();
    const timer = window.setInterval(() => {
      void probe();
    }, 30000);

    return () => {
      stopped = true;
      window.clearInterval(timer);
    };
  }, []);

  // WebSocket streaming connection with auto-reconnect
  useEffect(() => {
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.host;
    const url = `${proto}://${host}/ws/input`;
    const scheduleReconnect = () => {
      if (!shouldReconnectRef.current) return;
      const attempt = reconnectAttemptsRef.current + 1;
      reconnectAttemptsRef.current = attempt;
      const delayMs = Math.min(5000, 250 * Math.pow(2, Math.min(attempt, 5)));
      if (reconnectTimerRef.current) window.clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = window.setTimeout(() => {
        connect();
      }, delayMs);
    };

    const connect = () => {
      try {
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          reconnectAttemptsRef.current = 0;
          setWsConnected(true);
          console.info('[stream] ws open', url);
        };

        ws.onmessage = (ev) => {
          try {
            const data = JSON.parse(ev.data);
            console.debug('[stream] partial', data);
          } catch (e) {}
        };

        ws.onerror = () => {
          try { ws.close(); } catch (e) {}
        };

        ws.onclose = () => {
          setWsConnected(false);
          if (wsRef.current === ws) wsRef.current = null;
          scheduleReconnect();
        };
      } catch (e) {
        console.warn('ws connection failed', e);
        wsRef.current = null;
        scheduleReconnect();
      }
    };

    shouldReconnectRef.current = true;
    connect();

    return () => {
      shouldReconnectRef.current = false;
      if (reconnectTimerRef.current) {
        window.clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
      if (wsRef.current) {
        try { wsRef.current.close(); } catch (e) {}
        wsRef.current = null;
      }
    };
  }, []);

  const sendChunk = (text: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    seqRef.current += 1;
    const payload = { type: 'chunk', seq: seqRef.current, text, sessionId: 'web-client' };
    try { wsRef.current.send(JSON.stringify(payload)); } catch (e) {}
  };

  // Debounced streaming sender for hero input
  const onQueryChange = (v: string) => {
    setQuery(v);
    if (debounceRef.current) window.clearTimeout(debounceRef.current);
    // send partials after short pause
    debounceRef.current = window.setTimeout(() => {
      if (v && v.trim().length > 0) sendChunk(v.trim());
    }, 80);
  };

  const recordVisit = (id: string) => {
    try {
      const raw = localStorage.getItem('clx_recent_modules');
      const arr: string[] = raw ? JSON.parse(raw) : [];
      const filtered = [id, ...arr.filter((x) => x !== id)].slice(0, 5);
      localStorage.setItem('clx_recent_modules', JSON.stringify(filtered));
      setRecent(filtered);
    } catch (e) {
      // ignore
    }
  };

  const sortedModules = [...filteredModules].sort((a, b) => {
    // featured first
    if (a.featured && !b.featured) return -1;
    if (!a.featured && b.featured) return 1;
    // then by recent visits
    const ai = recent.indexOf(a.id);
    const bi = recent.indexOf(b.id);
    if (ai !== -1 || bi !== -1) return (bi === -1 ? -1 : bi) - (ai === -1 ? -1 : ai);
    return a.name.localeCompare(b.name);
  });

  const handleHeroSearch = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!query || query.trim().length === 0) {
      // scroll to modules
      const el = document.getElementById('modules');
      if (el) return el.scrollIntoView({ behavior: 'smooth' });
      return router.push('/modules/web-reader');
    }
    // go to Web Reader with query param
    const encoded = encodeURIComponent(query.trim());
    router.push(`/modules/web-reader?q=${encoded}`);
  };

  const streamingOnline = wsConnected || streamProbeOk;

  const handleStartExploring = (e?: React.MouseEvent) => {
    e?.preventDefault();
    router.push('/modules/curiosity-ocean');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-gray-50 to-white text-black">
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
                  <span className="text-2xl">🧠</span>
                </div>
                <div>
                  <span className="text-xl font-bold bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent">
                    Clisonix
                  </span>
                  <span className="text-xs text-gray-600 block -mt-1">Neural Intelligence</span>
                </div>
              </Link>
            </div>

            <div className="hidden md:flex items-center gap-8">
              {NAV_ITEMS.map((item) => {
                const className = 'text-gray-600 hover:text-emerald-600 transition-colors';

                return item.isRoute ? (
                  <Link key={item.href} href={item.href} className={className}>
                    {item.label}
                  </Link>
                ) : (
                  <a key={item.href} href={item.href} className={className}>
                    {item.label}
                  </a>
                );
              })}
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-2 text-xs">
                <span className={`w-2 h-2 rounded-full ${streamingOnline ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`}></span>
                <span className="text-gray-600">{streamingOnline ? 'Ocean Online' : 'Offline'}</span>
              </div>
              <Link
                href="/modules"
                className="text-gray-600 hover:text-emerald-600 font-medium transition-colors flex items-center gap-1"
              >
                <span>←</span> Browse
              </Link>
              <Link
                href="/modules/web-reader"
                className="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 rounded-lg font-medium transition-all shadow-lg shadow-blue-500/25 text-white text-sm"
              >
                Web Reader
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <section className="pt-28 pb-16 px-4 relative overflow-hidden">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>

        <div className="max-w-7xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-3 px-5 py-2.5 rounded-full bg-gray-100/50 border border-emerald-500/30 mb-8">
            <span className="w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse"></span>
            <span className="text-sm text-emerald-600 font-medium">Platform Online • 99.97% Uptime</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            <span className="bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-500 bg-clip-text text-transparent">
              Clisonix
            </span>
            <br />
            <span className="text-3xl md:text-5xl text-gray-700">Neural Intelligence Platform</span>
          </h1>

          <p className="text-lg text-gray-600 max-w-3xl mx-auto mb-6">
            Powered by ASI Trinity — Three artificial superintelligences working in harmony for neuroscience research, cognitive analysis, and AI-driven insights.
          </p>

          <form onSubmit={handleHeroSearch} className="max-w-2xl mx-auto mb-6">
            <div className="flex items-center gap-3">
              <input
                value={query}
                onChange={(e) => onQueryChange(e.target.value)}
                placeholder="Search the web or try: 'latest neuroscience breakthroughs'"
                className="flex-1 px-4 py-3 rounded-l-lg border border-gray-300 focus:outline-none"
                aria-label="Quick web browse search"
              />
              <button
                type="submit"
                className="px-4 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-black font-semibold rounded-r-lg"
              >
                Web Browse Search
              </button>
            </div>
            <div className="text-sm text-gray-500 mt-2">Try a quick search — we&apos;ll open Web Reader with your query.</div>
          </form>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-6">
            <Link
              href="/modules/curiosity-ocean"
              onClick={handleStartExploring}
              className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 rounded-xl font-semibold text-lg text-black transition-all shadow-lg shadow-emerald-500/30 flex items-center justify-center gap-2"
            >
              <span>🌊</span>
              Start Exploring
            </Link>
            <Link
              href="/modules"
              className="w-full sm:w-auto px-8 py-4 bg-gray-100 hover:bg-gray-200 border border-gray-300 hover:border-emerald-500 rounded-xl font-semibold text-lg text-gray-700 transition-all flex items-center justify-center gap-2"
            >
              <span>📊</span>
              View All Modules
            </Link>
          </div>

          <div className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-emerald-100 border border-emerald-300">
            <span className={`w-2 h-2 rounded-full ${streamingOnline ? 'bg-green-400 animate-pulse' : 'bg-gray-300'}`}></span>
            <span className="text-green-400 font-medium">All Systems Online</span>
            <span className="ml-2 text-xs text-gray-500">{streamingOnline ? 'streaming enabled' : 'streaming offline'}</span>
          </div>
        </div>
      </section>

      <section id="asi-trinity" className="py-20 px-4 bg-gradient-to-b from-transparent to-gray-100/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-emerald-500 to-teal-400 bg-clip-text text-transparent">
              Powered by AI
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">Advanced neural intelligence powering your experience</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Link href="/modules/eeg-analysis" className="p-8 rounded-2xl bg-gray-100/50 border border-gray-300 hover:border-emerald-500 hover:shadow-xl hover:shadow-emerald-500/10 transition-all text-center cursor-pointer">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center mb-6 shadow-lg">
                <span className="text-3xl">🔬</span>
              </div>
              <h3 className="text-xl font-bold text-black mb-2">Smart Analysis</h3>
              <p className="text-gray-600">Pattern recognition and data insights</p>
            </Link>
            <Link href="/modules/curiosity-ocean" className="p-8 rounded-2xl bg-gray-100/50 border border-gray-300 hover:border-teal-500 hover:shadow-xl hover:shadow-teal-500/10 transition-all text-center cursor-pointer">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-teal-400 to-emerald-500 flex items-center justify-center mb-6 shadow-lg">
                <span className="text-3xl">🎨</span>
              </div>
              <h3 className="text-xl font-bold text-black mb-2">Creative Tools</h3>
              <p className="text-gray-600">AI-powered creative assistance</p>
            </Link>
            <Link href="/modules" className="p-8 rounded-2xl bg-gray-100/50 border border-gray-300 hover:border-orange-500 hover:shadow-xl hover:shadow-orange-500/10 transition-all text-center cursor-pointer">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center mb-6 shadow-lg">
                <span className="text-3xl">✨</span>
              </div>
              <h3 className="text-xl font-bold text-black mb-2">Seamless Experience</h3>
              <p className="text-gray-600">Unified and harmonious interface</p>
            </Link>
          </div>
        </div>
      </section>

      <section aria-labelledby="official-clisonix" className="px-4 py-16">
        <div className="mx-auto max-w-7xl rounded-3xl border border-emerald-500/20 bg-gradient-to-br from-emerald-50 via-white to-teal-50 p-8 shadow-sm">
          <div className="grid gap-8 lg:grid-cols-[1.4fr_0.9fr] lg:items-center">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-700">Official Clisonix Platform</p>
              <h2 id="official-clisonix" className="mt-3 text-3xl font-bold text-black md:text-4xl">
                Clisonix Cloud combines AI workflows, neuroscience tools, and production infrastructure in one place
              </h2>
              <p className="mt-4 max-w-3xl text-base leading-7 text-gray-700">
                The official Clisonix experience at www.clisonix.com brings together Curiosity Ocean, Web Reader, KLOUd Bridge,
                EEG analysis, developer APIs, billing, and health-monitored cloud services. This gives search engines and visitors a clear,
                branded entry point for understanding what Clisonix is, what the platform actually offers, and that it is not affiliated with Clarisonic or beauty-device brands.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link href="/about-us" className="rounded-lg bg-emerald-600 px-4 py-2 font-semibold text-white shadow-sm hover:bg-emerald-500">
                  About Clisonix
                </Link>
                <Link href="/company" className="rounded-lg border border-gray-300 bg-white px-4 py-2 font-semibold text-gray-700 hover:border-emerald-500 hover:text-emerald-700">
                  Company
                </Link>
                <Link href="/brand" className="rounded-lg border border-gray-300 bg-white px-4 py-2 font-semibold text-gray-700 hover:border-emerald-500 hover:text-emerald-700">
                  Brand Verification
                </Link>
                <Link href="/developers/docs-index" className="rounded-lg border border-gray-300 bg-white px-4 py-2 font-semibold text-gray-700 hover:border-emerald-500 hover:text-emerald-700">
                  Docs Index
                </Link>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
              <div className="rounded-2xl border border-emerald-200 bg-white/80 p-4">
                <p className="text-sm font-semibold text-black">AI + Research</p>
                <p className="mt-1 text-sm text-gray-600">Curiosity Ocean, Archive, and Web Reader for assisted discovery.</p>
              </div>
              <div className="rounded-2xl border border-emerald-200 bg-white/80 p-4">
                <p className="text-sm font-semibold text-black">Neural Systems</p>
                <p className="mt-1 text-sm text-gray-600">EEG, neural synthesis, and cognitive tooling for differentiated workflows.</p>
              </div>
              <div className="rounded-2xl border border-emerald-200 bg-white/80 p-4">
                <p className="text-sm font-semibold text-black">Production Ops</p>
                <p className="mt-1 text-sm text-gray-600">Health endpoints, SDKs, auth, billing, and observability built into the stack.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="modules" className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent">
              Platform Modules
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto mb-8">Real-time data, no fake values, production-ready tools</p>

            <div className="flex flex-wrap items-center justify-center gap-2">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    selectedCategory === category
                      ? 'bg-emerald-500 text-black shadow-lg shadow-emerald-500/25'
                      : 'bg-gray-100 text-gray-600 hover:text-black hover:bg-gray-200'
                  }`}
                >
                  {category === 'all' ? 'All Modules' : category}
                </button>
              ))}
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedModules.map((module) => (
              <Link
                  key={module.id}
                  href={`/modules/${module.id}`}
                  onClick={() => recordVisit(module.id)}
                  className={`p-6 rounded-2xl bg-gray-100/50 border hover:shadow-xl hover:shadow-emerald-500/10 transition-all group relative ${
                    ('isNew' in module && module.isNew) ? 'border-green-500/50 hover:border-green-400 ring-1 ring-green-500/20' : 'border-gray-300 hover:border-emerald-500'
                  }`}
                >
                  {('isNew' in module && module.isNew) && (
                    <div className="absolute -top-2 -right-2 px-3 py-1 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full text-xs font-bold text-black shadow-lg animate-pulse">
                      NEW ✨
                    </div>
                  )}
                  <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${module.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg`}>
                    <span className="text-2xl">{module.icon}</span>
                  </div>
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-xl font-semibold text-black">{module.name}</h3>
                    <span className="px-2 py-0.5 text-xs rounded-full bg-emerald-500/20 text-emerald-600">{module.category}</span>
                  </div>
                  <p className="text-gray-600">{module.description}</p>
                  <div className="mt-4 flex items-center gap-2 text-emerald-600 group-hover:gap-3 transition-all">
                    <span className="text-sm font-medium">Open Module</span>
                    <span>→</span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
        <section id="entry-points" className="py-20 px-4">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent">
                Choose Your Entry Point
              </h2>
              <p className="text-gray-600 text-lg max-w-2xl mx-auto mb-8">Pick one focused path — Clisonix is a 5-layer Modular Intelligence System. Start where it matters.</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
              {/* 1. Intelligence Core */}
              <div className="p-6 rounded-2xl bg-gradient-to-br from-emerald-50 to-white border border-emerald-200">
                <h3 className="font-bold text-lg mb-2">🧠 Intelligence Core</h3>
                <p className="text-sm text-gray-600 mb-4">Zürich Engine, Trinity Debate, Curiosity Ocean, OpenMind — the heart of reasoning and multi-persona AI.</p>
                <ul className="space-y-2">
                  <li><Link href="/modules/curiosity-ocean" className="text-emerald-600">🌊 Curiosity Ocean</Link></li>
                  <li><Link href="/debate" className="text-emerald-600">⚖️ Trinity Debate</Link></li>
                  <li><Link href="/modules/zurich-engine" className="text-emerald-600">⚙️ Zürich Engine</Link></li>
                </ul>
              </div>

              {/* 2. Research & Knowledge Systems */}
              <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-50 to-white border border-blue-200">
                <h3 className="font-bold text-lg mb-2">🔬 Research & Knowledge</h3>
                <p className="text-sm text-gray-600 mb-4">Archive, Web Reader and expert chat for deep research and verified data.</p>
                <ul className="space-y-2">
                  <li><Link href="/modules/archive" className="text-blue-600">📜 Archive & Research</Link></li>
                  <li><Link href="/modules/web-reader" className="text-blue-600">🌐 Web Reader</Link></li>
                  <li><Link href="/modules/specialized-chat" className="text-blue-600">🧾 Specialized Expert Chat</Link></li>
                </ul>
              </div>

              {/* 3. Neuroscience & Cognitive Systems */}
              <div className="p-6 rounded-2xl bg-gradient-to-br from-purple-50 to-white border border-purple-200">
                <h3 className="font-bold text-lg mb-2">🧬 Neuroscience & Cognitive</h3>
                <p className="text-sm text-gray-600 mb-4">EEG, neural synthesis and cognitive modeling — your unique differentiation.</p>
                <ul className="space-y-2">
                  <li><Link href="/modules/eeg-analysis" className="text-purple-600">🔬 EEG Analysis</Link></li>
                  <li><Link href="/modules/neural-synthesis" className="text-purple-600">⚡ Neural Synthesis</Link></li>
                  <li><Link href="/modules/weather-dashboard" className="text-purple-600">🌤️ Weather & Cognitive</Link></li>
                </ul>
              </div>

              {/* 4. Environment & Real-world Data */}
              <div className="p-6 rounded-2xl bg-gradient-to-br from-sky-50 to-white border border-sky-200">
                <h3 className="font-bold text-lg mb-2">🌍 Environment & Real Data</h3>
                <p className="text-sm text-gray-600 mb-4">Aviation weather, device dashboards and other real-world ingestion layers.</p>
                <ul className="space-y-2">
                  <li><a href="/modules/aviation-weather" className="text-sky-600">✈️ Aviation Weather</a></li>
                  <li><Link href="/modules/my-data-dashboard" className="text-sky-600">📊 My Data Dashboard</Link></li>
                </ul>
              </div>

              {/* 5. Infrastructure & Control */}
              <div className="p-6 rounded-2xl bg-gradient-to-br from-gray-50 to-white border border-gray-200">
                <h3 className="font-bold text-lg mb-2">⚙️ Infrastructure & Control</h3>
                <p className="text-sm text-gray-600 mb-4">Billing, account, developer docs and enterprise controls for production use.</p>
                <ul className="space-y-2">
                  <li><Link href="/modules/account" className="text-gray-700">👤 Account & Billing</Link></li>
                  <li><Link href="/modules/developer-docs" className="text-gray-700">👨‍💻 Developer Docs</Link></li>
                  <li><a href="/modules/mymirror-now" className="text-gray-700">🔁 MyMirror Now</a></li>
                </ul>
              </div>
            </div>

            <div className="mt-10 text-center">
              <p className="text-sm text-gray-600">Tip: Pick one entry point — a focused start increases retention and conversion.</p>
              <div className="mt-4 flex items-center justify-center gap-4">
                <Link href="/modules/curiosity-ocean" className="px-5 py-3 bg-emerald-600 text-black rounded-lg font-semibold">Start with Curiosity Ocean</Link>
                <Link href="/modules" className="px-5 py-3 border border-gray-300 rounded-lg">View all modules</Link>
              </div>
            </div>
          </div>
        </section>

      <section id="tech-stack" className="py-20 px-4 bg-gradient-to-b from-transparent to-gray-100/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-emerald-500 to-teal-400 bg-clip-text text-transparent">Why Choose Clisonix?</h2>
            <p className="text-gray-600 text-lg max-w-3xl mx-auto">Not just a landing page claim: this repo already contains the system pieces teams usually ask for — multi-service architecture, observability, SDKs, health endpoints, billing, and production-oriented AI modules.</p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            {WHY_US_PILLARS.map((pillar) => (
              <div key={pillar.title} className="p-6 rounded-2xl bg-gray-100/50 border border-gray-300 hover:border-emerald-500 transition-all">
                <div className="text-3xl mb-3">{pillar.icon}</div>
                <h4 className="font-semibold text-black text-lg">{pillar.title}</h4>
                <p className="text-sm text-gray-600 mt-2">{pillar.description}</p>
                <p className="text-xs font-medium text-emerald-700 mt-4">{pillar.proof}</p>
              </div>
            ))}
          </div>

          <div className="mt-12 rounded-2xl border border-gray-200 bg-white/70 p-8 shadow-sm">
            <h3 className="text-xl font-semibold mb-4 text-center text-black">What already exists in the repo</h3>
            <div className="grid md:grid-cols-4 gap-4 text-center mb-8">
              <div className="p-4 rounded-xl bg-gray-50 border border-gray-200">
                <div className="text-2xl font-bold text-emerald-600">ALBA · ALBI · JONA</div>
                <div className="text-sm text-gray-600 mt-1">Distinct AI engines for collection, analysis and orchestration</div>
              </div>
              <div className="p-4 rounded-xl bg-gray-50 border border-gray-200">
                <div className="text-2xl font-bold text-emerald-600">Python + TS SDKs</div>
                <div className="text-sm text-gray-600 mt-1">Official SDKs and API-first delivery</div>
              </div>
              <div className="p-4 rounded-xl bg-gray-50 border border-gray-200">
                <div className="text-2xl font-bold text-emerald-600">Health + Status</div>
                <div className="text-sm text-gray-600 mt-1">Operational endpoints across services for support and monitoring</div>
              </div>
              <div className="p-4 rounded-xl bg-gray-50 border border-gray-200">
                <div className="text-2xl font-bold text-emerald-600">Payments + Auth</div>
                <div className="text-sm text-gray-600 mt-1">Google sign-in, quotas, Stripe, PayPal, SEPA and webhooks</div>
              </div>
            </div>

            <h3 className="text-xl font-semibold mb-4 text-center text-black">Common Use Cases</h3>
            <div className="flex flex-wrap items-center justify-center gap-3 mb-6">
              <span className="px-4 py-2 bg-gray-100 rounded-lg text-sm text-gray-700">Neuroscience Research</span>
              <span className="px-4 py-2 bg-gray-100 rounded-lg text-sm text-gray-700">Clinical EEG Analytics</span>
              <span className="px-4 py-2 bg-gray-100 rounded-lg text-sm text-gray-700">AI-Assisted Web Experiences</span>
              <span className="px-4 py-2 bg-gray-100 rounded-lg text-sm text-gray-700">Real-time Monitoring & Alerts</span>
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
              <Link
                href="/developers"
                className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 rounded-lg font-semibold text-white shadow-lg"
              >
                Read Docs
              </Link>
              {WHY_US_REFERENCES.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="px-6 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 bg-white"
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="p-8 rounded-2xl bg-gradient-to-br from-gray-100 to-gray-50 border border-emerald-500/30 shadow-lg shadow-emerald-500/10">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-black mb-2">🚀 Ready to Start?</h2>
              <p className="text-gray-600">Explore our tools and start your journey</p>
            </div>

            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-gray-200/50 border border-gray-300 text-center">
                <p className="text-3xl mb-2">📱</p>
                <p className="text-gray-800 text-sm font-medium">Mobile Friendly</p>
                <p className="text-xs text-gray-600">Use on any device</p>
              </div>
              <div className="p-4 rounded-lg bg-gray-200/50 border border-gray-300 text-center">
                <p className="text-3xl mb-2">🌟</p>
                <p className="text-gray-800 text-sm font-medium">Free to Try</p>
                <p className="text-xs text-gray-600">No credit card needed</p>
              </div>
              <div className="p-4 rounded-lg bg-gray-200/50 border border-gray-300 text-center">
                <p className="text-3xl mb-2">⚡</p>
                <p className="text-gray-800 text-sm font-medium">Instant Access</p>
                <p className="text-xs text-gray-600">Start immediately</p>
              </div>
            </div>

            <div className="mt-8 text-center">
              <Link
                href="/modules/account"
                className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 rounded-xl font-semibold text-lg transition-all shadow-lg shadow-emerald-500/30"
              >
                Get Started
                <span>→</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-gray-200 py-12 px-4 bg-gray-50/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">🧠</span>
                <span className="text-lg font-bold text-black">Clisonix</span>
              </div>
              <p className="text-gray-600 text-sm leading-6">
                Neural Intelligence Platform
                <br />
                Industrial AI, research workflows, and tools with a little more pulse.
              </p>
              <div className="mt-4 inline-flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">
                ✨ Built for real operators, researchers, and curious teams
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-black">Platform</h4>
              <ul className="space-y-2 text-gray-600 text-sm">
                <li><Link href="/modules" className="hover:text-emerald-600 transition-colors">Dashboard</Link></li>
                <li><Link href="/modules/curiosity-ocean" className="hover:text-emerald-600 transition-colors">Curiosity Ocean</Link></li>
                <li><Link href="/modules/eeg-analysis" className="hover:text-emerald-600 transition-colors">EEG Analysis</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-black">Resources</h4>
              <ul className="space-y-2 text-gray-600 text-sm">
                <li><Link href="/developers" className="hover:text-emerald-600 transition-colors">Documentation</Link></li>
                <li><Link href="/developers/docs-index" className="hover:text-emerald-600 transition-colors">Docs Index</Link></li>
                <li><Link href="/about-us" className="hover:text-emerald-600 transition-colors">About Clisonix</Link></li>
                <li><Link href="/why-clisonix" className="hover:text-emerald-600 transition-colors">Why Clisonix</Link></li>
                <li><Link href="/marketplace" className="hover:text-emerald-600 transition-colors">Marketplace</Link></li>
                <li><Link href="/company" className="hover:text-emerald-600 transition-colors">Company</Link></li>
                <li><Link href="/faq" className="hover:text-emerald-600 transition-colors">FAQ</Link></li>
                <li><Link href="/privacy" className="hover:text-emerald-600 transition-colors">Privacy Policy</Link></li>
                <li><Link href="/terms" className="hover:text-emerald-600 transition-colors">Terms of Use</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-black">Company</h4>
              <ul className="space-y-2 text-gray-600 text-sm">
                <li><span className="text-gray-700 font-medium">Clisonix Cloud</span></li>
                <li><span className="text-gray-700">Clisonix operator</span></li>
                <li><span className="text-gray-700">Registered legal entity: ABA GmbH</span></li>
                {PUBLIC_DOMAIN && <li><span className="text-gray-700">Official domain: {PUBLIC_DOMAIN}</span></li>}
                {SUPPORT_EMAIL && <li><a href={`mailto:${SUPPORT_EMAIL}`} className="hover:text-emerald-600 transition-colors">{SUPPORT_EMAIL}</a></li>}
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-gray-200 text-center text-gray-500 text-sm">
            <div>© 2026 Clisonix Cloud. All rights reserved.</div>
            <div className="mt-2">Clisonix is the official platform at www.clisonix.com and is not affiliated with Clarisonic or other similarly named organizations.</div>
          </div>
        </div>
      </footer>
    </div>
  );
}
