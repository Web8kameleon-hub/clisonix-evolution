import type { Metadata } from 'next';
import Link from 'next/link';

type AuditEvent = {
  article_hash: string;
  title: string;
  category: string;
  icon: string;
  platform: string;
  status: string;
  lab_id: number;
  timestamp: string;
};

type NewsroomAuditResponse = {
  total_events: number;
  recent: AuditEvent[];
  timestamp: string;
};

export const metadata: Metadata = {
  title: 'Clisonix News',
  description: 'Live newsroom events from Clisonix AI Newsroom service.',
};

export const dynamic = 'force-dynamic';

async function getNewsEvents(): Promise<AuditEvent[]> {
  const baseUrl = process.env.NEWSROOM_PUBLIC_URL ?? 'http://localhost:9800';

  try {
    const response = await fetch(`${baseUrl}/audit?limit=50`, {
      cache: 'no-store',
      next: { revalidate: 0 },
    });

    if (!response.ok) {
      return [];
    }

    const payload = (await response.json()) as NewsroomAuditResponse;

    return (payload.recent ?? [])
      .filter((event) => event.platform === 'blog' && event.status === 'success')
      .slice()
      .reverse();
  } catch {
    return [];
  }
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

export default async function NewsPage() {
  const events = await getNewsEvents();

  return (
    <main className="min-h-screen bg-black text-white px-6 py-10">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight">Clisonix News</h1>
          <p className="text-gray-400 mt-2">
            Integrated newsroom feed from the main Clisonix platform.
          </p>
        </header>

        <section className="mb-8 rounded-xl border border-cyan-900/60 bg-gradient-to-br from-cyan-950/70 to-slate-950 p-6">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-300">
            Featured enterprise editorial
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-white">
            Reliability, Not Rhetoric: The New Operating Discipline of Industrial AI
          </h2>
          <p className="mt-3 max-w-3xl text-gray-300">
            A serious editorial on why the next phase of AI competition will be defined less by
            spectacle and more by uptime, resilience, auditability, and cost discipline.
          </p>
          <div className="mt-4">
            <Link
              href="/news/reliability-not-rhetoric-industrial-ai"
              className="inline-flex items-center rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-400"
            >
              Read editorial →
            </Link>
          </div>
        </section>

        {events.length === 0 ? (
          <section className="rounded-xl border border-gray-800 bg-gray-950 p-6">
            <h2 className="text-xl font-semibold">No published events yet</h2>
            <p className="text-gray-400 mt-2">
              Newsroom is connected, but there are no successful blog publish events at the moment.
            </p>
          </section>
        ) : (
          <section className="grid gap-4 md:grid-cols-2">
            {events.map((event) => (
              <article
                key={`${event.article_hash}-${event.timestamp}`}
                className="rounded-xl border border-gray-800 bg-gray-950 p-5"
              >
                <div className="flex items-center justify-between gap-4">
                  <p className="text-sm text-emerald-400 font-medium">
                    {event.icon} {event.category}
                  </p>
                  <p className="text-xs text-gray-500">Lab #{event.lab_id}</p>
                </div>
                <h3 className="text-lg font-semibold mt-2">{event.title}</h3>
                <div className="mt-3 text-sm text-gray-400 flex items-center justify-between gap-2">
                  <span>Platform: {event.platform}</span>
                  <span>{formatDate(event.timestamp)}</span>
                </div>
              </article>
            ))}
          </section>
        )}
      </div>
    </main>
  );
}
