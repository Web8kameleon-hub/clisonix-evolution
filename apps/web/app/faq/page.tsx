import type { Metadata } from 'next';

const questions = [
  {
    question: 'What is Clisonix?',
    answer:
      'Clisonix is a neural intelligence platform for AI workflows, EEG analysis, research tools, and real-time analytics, available at www.clisonix.com.',
  },
  {
    question: 'Is Clisonix related to Clarisonic?',
    answer:
      'No. Clisonix is an independent AI and neuroscience software platform and has no affiliation with Clarisonic facial-cleansing devices, skincare products, or beauty brands.',
  },
  {
    question: 'Is Clisonix the same as Clionix?',
    answer:
      'No. Clisonix is a separate platform and brand. The official Clisonix website is www.clisonix.com.',
  },
  {
    question: 'What does Clisonix focus on?',
    answer:
      'Clisonix focuses on AI-assisted research, neural and EEG tooling, modular intelligence workflows, and production-oriented developer infrastructure.',
  },
  {
    question: 'Where can I verify the official Clisonix website?',
    answer:
      'The official website is https://www.clisonix.com. Company, platform, FAQ, and product details on this domain describe the official Clisonix platform.',
  },
  {
    question: 'Which GitHub repository is the official Clisonix repository?',
    answer:
      'The official public repository is https://github.com/Web8kameleon-hub/clisonix.com. Always verify that a repository or page links back to www.clisonix.com before treating it as official.',
  },
  {
    question: 'Does Clisonix sell skincare or beauty devices?',
    answer:
      'No. Clisonix is a software and research platform focused on AI, neuroscience, analytics, and developer tools. It does not sell Clarisonic-style beauty or skincare devices.',
  },
  {
    question: 'How can I contact Clisonix?',
    answer:
      'You can contact the team at clisonix@pm.me for general questions, partnerships, and security-related communication.',
  },
];

export const metadata: Metadata = {
  title: 'Clisonix FAQ',
  description:
    'Frequently asked questions about Clisonix, including the official website, platform scope, and clarification versus Clarisonic or similarly named brands.',
  alternates: {
    canonical: '/faq',
  },
  openGraph: {
    title: 'Clisonix FAQ',
    description:
      'Answers to common questions about Clisonix, including what the platform is and how it differs from similar names.',
    url: 'https://www.clisonix.com/faq',
  },
};

export default function FAQPage() {
  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: questions.map((item) => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.answer,
      },
    })),
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <div className="mx-auto flex max-w-5xl flex-col gap-10 px-6 py-20">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-300">Clisonix FAQ</p>
          <h1 className="mt-4 text-4xl font-bold md:text-5xl">Clear answers about the official Clisonix platform</h1>
          <p className="mt-6 text-lg leading-8 text-slate-300">
            This page exists to make the official Clisonix identity easier to verify for search engines,
            social platforms, partners, and users.
          </p>
        </div>

        <div className="rounded-3xl border border-emerald-500/20 bg-emerald-500/10 p-6 text-slate-100">
          <p className="font-semibold text-emerald-200">Official domain</p>
          <p className="mt-2 text-lg">https://www.clisonix.com</p>
        </div>

        <div className="grid gap-6">
          {questions.map((item) => (
            <section key={item.question} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
              <h2 className="text-2xl font-semibold text-white">{item.question}</h2>
              <p className="mt-4 leading-8 text-slate-300">{item.answer}</p>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}

