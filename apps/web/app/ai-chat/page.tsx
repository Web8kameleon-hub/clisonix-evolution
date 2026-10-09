import type { Metadata } from 'next';
import Link from 'next/link';

const AI_CHAT_MODULES = [
  {
    name: 'Curiosity Ocean',
    href: '/modules/curiosity-ocean',
    description: 'General-purpose AI chat for deep exploration and contextual answers.',
  },
  {
    name: 'Web Reader',
    href: '/modules/web-reader',
    description: 'Chat with live web pages and pull structured insights from online sources.',
  },
  {
    name: 'Specialized Expert Chat',
    href: '/modules/specialized-chat',
    description: 'Domain-focused AI chat experiences for advanced problem solving.',
  },
  {
    name: 'OpenMind',
    href: '/modules/openmind',
    description: 'Behavioral and cognitive AI workflows with chat-first interaction.',
  },
  {
    name: 'Archive & Research',
    href: '/modules/archive',
    description: 'Research chat across scientific and public knowledge datasets.',
  },
];

export const metadata: Metadata = {
  title: 'AI Chat Platform | Clisonix Modules for Research, Web and Expert Conversations',
  description:
    'Discover Clisonix AI chat modules for research workflows, document and web reading, and specialized expert conversations on www.clisonix.com.',
  alternates: {
    canonical: '/ai-chat',
  },
  keywords: [
    'ai chat platform',
    'enterprise ai chat',
    'research ai chat',
    'chat with web pages',
    'chat with documents',
    'expert ai chat',
    'clisonix ai chat',
  ],
  openGraph: {
    title: 'AI Chat Platform | Clisonix',
    description:
      'Access AI chat modules for web reading, research, and expert workflows in one platform.',
    url: 'https://www.clisonix.com/ai-chat',
    type: 'website',
    images: [
      {
        url: 'https://www.clisonix.com/icons/icon-512x512.png',
        width: 512,
        height: 512,
        alt: 'Clisonix AI chat platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Chat Platform | Clisonix',
    description:
      'AI chat modules for research, web reading, and specialized expert workflows.',
    images: ['https://www.clisonix.com/icons/icon-512x512.png'],
  },
};

export default function AIChatLandingPage() {
  const aiChatSchema = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'WebPage',
        name: 'Clisonix AI Chat Platform',
        description:
          'Landing page for Clisonix AI chat modules including research, web reader, and expert chat workflows.',
        url: 'https://www.clisonix.com/ai-chat',
      },
      {
        '@type': 'ItemList',
        name: 'Clisonix AI Chat Modules',
        itemListElement: AI_CHAT_MODULES.map((module, index) => ({
          '@type': 'ListItem',
          position: index + 1,
          name: module.name,
          url: `https://www.clisonix.com${module.href}`,
        })),
      },
    ],
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 px-6 py-16 text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(aiChatSchema) }}
      />

      <div className="mx-auto max-w-5xl">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-300">AI Chat Hub</p>
        <h1 className="mt-4 text-4xl font-bold md:text-5xl">Clisonix AI chat modules for research, web reading, and expert workflows</h1>
        <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300">
          This page groups the highest-value AI chat modules in the Clisonix platform so users and search engines can
          discover practical chat workflows faster.
        </p>

        <div className="mt-10 grid gap-5 md:grid-cols-2">
          {AI_CHAT_MODULES.map((module) => (
            <Link
              key={module.href}
              href={module.href}
              className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 transition-colors hover:border-cyan-400/70"
            >
              <h2 className="text-xl font-semibold text-white">{module.name}</h2>
              <p className="mt-3 leading-7 text-slate-300">{module.description}</p>
              <p className="mt-4 text-sm font-medium text-cyan-300">Open module</p>
            </Link>
          ))}
        </div>

        <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h2 className="text-2xl font-semibold">Need the full module directory?</h2>
          <p className="mt-3 text-slate-300">
            Explore all available modules, including EEG, analytics, weather, infrastructure, and developer tooling.
          </p>
          <Link
            href="/modules"
            className="mt-5 inline-flex rounded-lg bg-cyan-600 px-4 py-2 font-semibold text-white hover:bg-cyan-500"
          >
            Browse all modules
          </Link>
        </div>
      </div>
    </main>
  );
}
