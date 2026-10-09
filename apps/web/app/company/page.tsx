import type { Metadata } from 'next';
import Link from 'next/link';

/**
 * COMPANY PAGE - About Clisonix
 * Trust, credibility, and story
 */

export const metadata: Metadata = {
  title: 'About Clisonix',
  description:
    'Company overview for Clisonix, the official AI and neuroscience platform at www.clisonix.com.',
  keywords: [
    'Clisonix founder',
    'Clisonix CEO',
    'Ledjan Ahmati',
    'public safety engineer',
    'civil safety engineer',
    'ISO EuroNorm TUV specialist',
    'civil emergency specialist',
    'emergency readiness expert',
  ],
  alternates: {
    canonical: '/company',
  },
  openGraph: {
    title: 'About Clisonix',
    description:
      'Learn what Clisonix builds, who operates the platform, and how to contact the team.',
    url: 'https://www.clisonix.com/company',
  },
};

export default function CompanyPage() {
  const milestones = [
    { year: '2024', title: 'Founded', desc: 'Clisonix founded with vision to democratize AI' },
    { year: '2024', title: 'ASI Trinity', desc: 'Core AI architecture developed (Neural Trinity System)' },
    { year: '2025', title: 'Platform Launch', desc: '15+ modules released, platform goes live' },
    { year: '2026', title: 'Public Beta', desc: 'Open access with 6-month free trial for early adopters' },
  ];

  const values = [
    {
      icon: '🎯',
      title: 'Developer First',
      desc: 'Every decision starts with "How does this help developers?"'
    },
    {
      icon: '🔒',
      title: 'Security by Design',
      desc: 'Security isn\'t an afterthought - it\'s foundational'
    },
    {
      icon: '⚡',
      title: 'Performance Obsessed',
      desc: 'We measure everything in milliseconds'
    },
    {
      icon: '🤝',
      title: 'Transparent',
      desc: 'Open pricing, honest communication, no surprises'
    },
    {
      icon: '🌍',
      title: 'Global Mindset',
      desc: 'Built for the world, not just one market'
    },
    {
      icon: '🚀',
      title: 'Continuous Innovation',
      desc: 'Ship fast, learn faster, never stop improving'
    },
  ];

  const stats = [
    { value: '15+', label: 'AI Modules' },
    { value: '150+', label: 'API Endpoints' },
    { value: '24/7', label: 'Monitoring' },
    { value: '<100ms', label: 'Avg Latency' },
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
            <Link href="/modules" className="px-4 py-2 bg-blue-800 hover:bg-blue-700 rounded-lg transition-colors">
              Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6 text-center">
        <h1 className="text-5xl font-bold mb-6">
          About Clisonix
        </h1>
        <p className="text-xl text-gray-400 max-w-3xl mx-auto">
          We&apos;re building the future of AI infrastructure — powerful, accessible,
          and designed for developers who demand excellence.
        </p>
        <div className="mt-8 max-w-3xl mx-auto rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-6 py-5 text-left">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-300">Brand clarity</p>
          <p className="mt-3 text-gray-200 leading-7">
            Clisonix is the official platform available at <span className="font-semibold text-white">www.clisonix.com</span>.
            It is distinct from Clarisonic, Clionix, and other unrelated brands or services with similar names.
          </p>
          <p className="mt-3 text-gray-300 leading-7">
            Registered legal entity: <span className="font-semibold text-white">ABA GmbH</span>.
          </p>
        </div>
      </section>

      {/* Mission */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="p-12 rounded-3xl bg-gradient-to-b from-blue-700/10 to-slate-800/50 border border-blue-700/20">
            <h2 className="text-3xl font-bold mb-6">Our Mission</h2>
            <p className="text-xl text-gray-300 leading-relaxed">
              To democratize artificial superintelligence by providing
              <span className="text-blue-600"> enterprise-grade AI infrastructure</span> that&apos;s
              accessible to every developer, from solo hackers to Fortune 500 enterprises.
            </p>
          </div>
        </div>
      </section>

      {/* Founder Profile */}
      <section className="py-10 px-6">
        <div className="max-w-4xl mx-auto rounded-3xl border border-emerald-500/20 bg-emerald-500/10 p-8">
          <h2 className="text-3xl font-bold">Founder and CEO Profile</h2>
          <p className="mt-4 text-lg text-gray-200 leading-8">
            Ledjan Ahmati is a public and civil safety engineer and self-employed specialist with 21 years of field experience.
            His specialization includes ISO, EuroNorm, and TUV-aligned compliance, with an operational background in civil emergency
            and natural emergency readiness.
          </p>
          <ul className="mt-5 list-disc pl-6 text-gray-200 space-y-2">
            <li>Public and civil safety engineering leadership</li>
            <li>ISO, EuroNorm, and TUV-focused systems and compliance</li>
            <li>Civil emergency and natural emergency response readiness</li>
            <li>Production-grade risk, resilience, and continuity mindset for AI infrastructure</li>
          </ul>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 px-6 bg-slate-900/50">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">{stat.value}</div>
              <div className="text-gray-400">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Story */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Our Story</h2>

          <div className="prose prose-invert max-w-none">
            <p className="text-lg text-gray-300 mb-6">
              Clisonix was born from a simple frustration: why is AI infrastructure so
              complex, expensive, and fragmented? We believed developers deserved better.
            </p>
            <p className="text-lg text-gray-300 mb-6">
              In 2024, we set out to build something different — a unified AI platform
              that combines the power of multiple specialized systems (what we call the
              ASI Trinity: Core-A, Core-B, and Core-C) into a single, coherent API.
            </p>
            <p className="text-lg text-gray-300 mb-6">
              Today, Clisonix powers applications across industries — from healthcare
              to fintech, from startups to enterprises. Our 15+ modules provide
              everything developers need: neural processing, vision AI, workflow
              automation, and much more.
            </p>
            <p className="text-lg text-gray-300">
              But we&apos;re just getting started. Our roadmap includes expanding into new
              regions, launching additional modules, and continuing to push the
              boundaries of what&apos;s possible with AI infrastructure.
            </p>
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Milestones</h2>

          <div className="space-y-8">
            {milestones.map((milestone, idx) => (
              <div
                key={idx}
                className="flex items-start gap-6 relative"
              >
                <div className="flex-shrink-0 w-20 text-blue-600 font-bold text-lg">
                  {milestone.year}
                </div>
                <div className="flex-shrink-0 w-4 h-4 mt-1 rounded-full bg-blue-700"></div>
                <div className="pb-8 border-l border-slate-700 pl-6 -ml-2">
                  <h3 className="font-semibold text-lg">{milestone.title}</h3>
                  <p className="text-gray-400">{milestone.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Our Values</h2>
          <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
            The principles that guide every decision we make
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {values.map((value) => (
              <div
                key={value.title}
                className="p-6 rounded-xl bg-slate-800/50 border border-slate-700"
              >
                <div className="text-3xl mb-3">{value.icon}</div>
                <h3 className="font-semibold text-lg mb-2">{value.title}</h3>
                <p className="text-gray-400">{value.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact */}
      <section className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Get in Touch</h2>
          <p className="text-center text-gray-400 mb-10 max-w-2xl mx-auto">
            One inbox, direct contact, and no corporate maze. If it matters to Clisonix, it reaches us at the same address.
          </p>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 text-center">
              <div className="text-3xl mb-3">📧</div>
              <h3 className="font-semibold mb-2">General</h3>
              <a href="mailto:clisonix@pm.me" className="text-blue-600 hover:underline">
                clisonix@pm.me
              </a>
            </div>
            <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 text-center">
              <div className="text-3xl mb-3">💼</div>
              <h3 className="font-semibold mb-2">Partnerships</h3>
              <a href="mailto:clisonix@pm.me?subject=Partnership" className="text-blue-600 hover:underline">
                clisonix@pm.me
              </a>
            </div>
            <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 text-center">
              <div className="text-3xl mb-3">🔒</div>
              <h3 className="font-semibold mb-2">Security</h3>
              <a href="mailto:clisonix@pm.me?subject=Security" className="text-blue-600 hover:underline">
                clisonix@pm.me
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to Build with Us?</h2>
        <p className="text-gray-400 mb-8 max-w-xl mx-auto">
          Join thousands of developers building the future with Clisonix.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            href="/modules"
            className="px-8 py-4 bg-blue-800 hover:bg-blue-700 rounded-xl font-semibold transition-colors"
          >
            Start Building
          </Link>
          <Link
            href="/pricing"
            className="px-8 py-4 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold transition-colors"
          >
            View Pricing
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-slate-800">
        <div className="max-w-6xl mx-auto text-center text-gray-500 text-sm">
          © 2026 Clisonix. All rights reserved. |
          <Link href="/security" className="hover:text-blue-600 ml-2">Security</Link> |
          <Link href="/status" className="hover:text-blue-600 ml-2">Status</Link> |
          <Link href="/platform" className="hover:text-blue-600 ml-2">Platform</Link>
        </div>
      </footer>
    </div>
  );
}








