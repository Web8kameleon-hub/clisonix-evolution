'use client';

import Link from 'next/link';

/**
 * WHY CLISONIX - Enterprise Value Proposition
 * SEO-optimized landing page for conversions
 */

export default function WhyClisonixPage() {
  const proofPoints = [
    {
      title: 'Industrial multi-service architecture',
      description: 'The repo is structured as a real multi-service platform with API, Ocean, ALBA, ALBI, JONA, monitoring, payments, content, analytics and supporting services orchestrated through Docker Compose.',
      proof: 'Architecture + service isolation, not a single monolith',
      link: '/platform'
    },
    {
      title: 'Observable by default',
      description: 'Prometheus, Grafana, Loki, Jaeger and Tempo are part of the platform narrative together with `/health` and `/status` endpoints across services.',
      proof: 'Built-in operational visibility and diagnostics',
      link: '/status'
    },
    {
      title: 'Developer delivery is already there',
      description: 'The codebase includes developer documentation, OpenAPI-friendly APIs, and official Python and TypeScript SDKs for faster adoption.',
      proof: 'Docs + SDKs + module pages available now',
      link: '/developers'
    },
    {
      title: 'Real product workflows, not demo flows',
      description: 'Authentication, quotas, Stripe, PayPal, SEPA, webhook handling and account/billing flows are already represented in the repository.',
      proof: 'Business logic exists alongside AI features',
      link: '/pricing'
    },
  ];

  const competitors = [
    { name: 'Traditional Cloud', latency: 'Generic', uptime: 'Infra only', ai: 'Limited', price: '$$$' },
    { name: 'Generic AI APIs', latency: 'Model only', uptime: 'Vendor-defined', ai: 'Single layer', price: '$$$$' },
    { name: 'Clisonix', latency: 'Platform-aware', uptime: 'Health-driven', ai: 'ALBA + ALBI + JONA', price: 'Better stack value' },
  ];

  const benefits = [
    {
      icon: '🧠',
      title: 'ASI Trinity Architecture',
      description: 'ALBA, ALBI and JONA are presented as distinct engines for collection, analysis and orchestration instead of one generic AI box.',
      metric: 'Three-role AI structure'
    },
    {
      icon: '🏗️',
      title: 'Production Architecture',
      description: 'Dockerized service boundaries, dedicated containers and isolated dependencies make the system easier to operate and scale.',
      metric: 'Compose-based orchestration'
    },
    {
      icon: '🔒',
      title: 'Security & Controls',
      description: 'Auth, quotas, middleware, billing controls and secret-driven configuration are included as first-class platform concerns.',
      metric: 'Auth + quota + payment controls'
    },
    {
      icon: '📊',
      title: 'Operational Observability',
      description: 'Metrics, tracing, logs and dashboard tooling are represented in the repo, so supportability is part of the product.',
      metric: 'Prometheus + Grafana + Loki + Jaeger'
    },
    {
      icon: '🌐',
      title: 'Real Data & Research Workflows',
      description: 'The platform spans EEG, audio, research, dashboards, archive/search and intelligent assistants instead of one isolated feature.',
      metric: 'Multiple domain modules'
    },
    {
      icon: '🔌',
      title: 'API-First Design',
      description: 'Python and TypeScript SDKs, docs and integration surfaces reduce time from evaluation to implementation.',
      metric: 'Python + TypeScript SDKs'
    }
  ];

  const useCases = [
    {
      industry: 'Healthcare & Biotech',
      icon: '🏥',
      description: 'EEG analysis, neural pattern recognition, patient monitoring systems',
      companies: 'Research labs, hospitals, biotech startups'
    },
    {
      industry: 'Financial Services',
      icon: '🏦',
      description: 'Real-time fraud detection, market analysis, algorithmic trading support',
      companies: 'Banks, fintech, hedge funds'
    },
    {
      industry: 'Industrial & IoT',
      icon: '🏭',
      description: 'Predictive maintenance, sensor data processing, anomaly detection',
      companies: 'Manufacturing, energy, logistics'
    },
    {
      industry: 'Research & Academia',
      icon: '🎓',
      description: 'Data synthesis, pattern analysis, research acceleration',
      companies: 'Universities, research institutes, think tanks'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-3">
            <span className="text-2xl">🧠</span>
            <span className="text-xl font-bold">Clisonix</span>
          </Link>
          <div className="flex items-center gap-6">
            <Link href="/platform" className="text-gray-400 hover:text-white transition-colors">Platform</Link>
            <Link href="/pricing" className="text-gray-400 hover:text-white transition-colors">Pricing</Link>
            <Link href="/modules" className="px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg transition-colors">
              Open Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/30 mb-8">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
            <span className="text-violet-300 text-sm">ASI Trinity Online • 99.97% Uptime</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Why Leading Companies Choose{' '}
            <span className="bg-gradient-to-r from-violet-400 to-violet-400 bg-clip-text text-transparent">
              Clisonix
            </span>
          </h1>

          <p className="text-xl text-gray-400 mb-10 max-w-3xl mx-auto">
            Clisonix is stronger than a generic “AI app” because the repository already shows the platform layers behind the product: distinct AI engines, monitoring, billing, docs, SDKs, health endpoints and production orchestration.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/modules"
              className="px-8 py-4 bg-gradient-to-r from-violet-600 to-violet-600 hover:from-violet-500 hover:to-violet-500 rounded-xl font-semibold text-lg transition-all shadow-lg shadow-violet-500/25"
            >
              Start Free Trial
            </Link>
            <Link
              href="/developers"
              className="px-8 py-4 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold text-lg transition-colors border border-slate-700"
            >
              View Documentation
            </Link>
          </div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">How We Compare</h2>
          <p className="text-gray-400 text-center mb-12">The difference is not just the model. It is the surrounding platform already present in this codebase.</p>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">Platform</th>
                  <th className="text-center py-4 px-6 text-gray-400 font-medium">Latency</th>
                  <th className="text-center py-4 px-6 text-gray-400 font-medium">Uptime</th>
                  <th className="text-center py-4 px-6 text-gray-400 font-medium">AI Integration</th>
                  <th className="text-center py-4 px-6 text-gray-400 font-medium">Value</th>
                </tr>
              </thead>
              <tbody>
                {competitors.map((comp, i) => (
                  <tr
                    key={comp.name}
                    className={`border-b border-slate-800 ${i === 2 ? 'bg-violet-500/10' : ''}`}
                  >
                    <td className="py-4 px-6 font-medium">
                      {i === 2 && <span className="mr-2">🏆</span>}
                      {comp.name}
                    </td>
                    <td className="text-center py-4 px-6">{comp.latency}</td>
                    <td className="text-center py-4 px-6">{comp.uptime}</td>
                    <td className="text-center py-4 px-6">{comp.ai}</td>
                    <td className="text-center py-4 px-6">{comp.price}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Proof Section */}
      <section className="py-20 px-6 border-y border-slate-800/80 bg-slate-950/60">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Why us — with actual proof</h2>
          <p className="text-gray-400 text-center mb-12 max-w-3xl mx-auto">
            If you open this repository, you do not just find marketing pages. You find services, monitoring, SDKs, developer docs, account flows and deployable infrastructure.
          </p>

          <div className="grid md:grid-cols-2 gap-6">
            {proofPoints.map((item) => (
              <div key={item.title} className="rounded-2xl border border-slate-700 bg-slate-800/50 p-6">
                <h3 className="text-xl font-semibold mb-3">{item.title}</h3>
                <p className="text-gray-300 mb-4">{item.description}</p>
                <div className="flex items-center justify-between gap-4 flex-wrap">
                  <span className="inline-flex px-3 py-1 rounded-full bg-violet-500/20 text-violet-300 text-sm">
                    {item.proof}
                  </span>
                  <Link href={item.link} className="text-violet-300 hover:text-violet-200 transition-colors">
                    Explore →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Grid */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Enterprise-Grade Capabilities</h2>
          <p className="text-gray-400 text-center mb-12">Everything you need to build intelligent applications</p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {benefits.map((benefit) => (
              <div
                key={benefit.title}
                className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700 hover:border-violet-500/50 transition-colors"
              >
                <div className="text-4xl mb-4">{benefit.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{benefit.title}</h3>
                <p className="text-gray-400 mb-4">{benefit.description}</p>
                <div className="inline-flex px-3 py-1 rounded-full bg-violet-500/20 text-violet-300 text-sm">
                  {benefit.metric}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Built for Your Industry</h2>
          <p className="text-gray-400 text-center mb-12">Trusted by teams across diverse sectors</p>

          <div className="grid md:grid-cols-2 gap-6">
            {useCases.map((uc) => (
              <div
                key={uc.industry}
                className="p-6 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-800/50 border border-slate-700"
              >
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-3xl">{uc.icon}</span>
                  <h3 className="text-xl font-semibold">{uc.industry}</h3>
                </div>
                <p className="text-gray-300 mb-3">{uc.description}</p>
                <p className="text-sm text-gray-500">{uc.companies}</p>
              </div>
            ))}
          </div>

          <div className="mt-12 rounded-2xl border border-slate-700 bg-slate-800/40 p-8">
            <h3 className="text-2xl font-semibold text-center mb-6">What teams can point to immediately</h3>
            <div className="grid md:grid-cols-4 gap-4 text-center">
              <div className="rounded-xl bg-slate-900/60 border border-slate-700 p-4">
                <div className="text-xl font-bold text-violet-300">AI Engines</div>
                <p className="text-sm text-gray-400 mt-2">ALBA, ALBI and JONA as explicit platform components</p>
              </div>
              <div className="rounded-xl bg-slate-900/60 border border-slate-700 p-4">
                <div className="text-xl font-bold text-violet-300">Observability</div>
                <p className="text-sm text-gray-400 mt-2">Prometheus, Grafana, Loki, Jaeger and Tempo in stack design</p>
              </div>
              <div className="rounded-xl bg-slate-900/60 border border-slate-700 p-4">
                <div className="text-xl font-bold text-violet-300">SDKs</div>
                <p className="text-sm text-gray-400 mt-2">Official Python and TypeScript client paths already present</p>
              </div>
              <div className="rounded-xl bg-slate-900/60 border border-slate-700 p-4">
                <div className="text-xl font-bold text-violet-300">Ops Endpoints</div>
                <p className="text-sm text-gray-400 mt-2">`/health` and `/status` patterns across services for real operations</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Experience the Difference?
          </h2>
          <p className="text-xl text-gray-400 mb-10">
            Join hundreds of teams already using Clisonix to build smarter applications.
            Start free, scale when ready.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/modules"
              className="px-8 py-4 bg-gradient-to-r from-violet-600 to-violet-600 hover:from-violet-500 hover:to-violet-500 rounded-xl font-semibold text-lg transition-all"
            >
              Start Building Today
            </Link>
            <Link
              href="mailto:clisonix@pm.me"
              className="px-8 py-4 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold text-lg transition-colors"
            >
              Contact Sales
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-slate-800">
        <div className="max-w-6xl mx-auto text-center text-gray-500 text-sm">
          © 2026 Clisonix. All rights reserved. |
          <Link href="/security" className="hover:text-violet-400 ml-2">Security</Link> |
          <Link href="/status" className="hover:text-violet-400 ml-2">Status</Link> |
          <Link href="/company" className="hover:text-violet-400 ml-2">Company</Link>
        </div>
      </footer>
    </div>
  );
}








