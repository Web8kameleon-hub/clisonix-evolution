import type { Metadata } from 'next';
import Link from 'next/link';
import { BUSINESS_IDENTITY } from '../lib/business-identity';

export const metadata: Metadata = {
  title: 'Refund and Return Policy | Clisonix',
  description:
    'Refund and return policy for Clisonix subscriptions, cancellations, billing corrections, and disputes.',
  alternates: {
    canonical: '/refund-policy',
  },
};

export default function RefundPolicyPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 px-6 py-16 text-white">
      <div className="mx-auto max-w-4xl">
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-bold">Refund and Return Policy</h1>
          <p className="mt-3 text-slate-300">{BUSINESS_IDENTITY.brandName} / {BUSINESS_IDENTITY.legalName}</p>
          <p className="mt-1 text-sm text-slate-400">Last updated: April 20, 2026</p>
        </header>

        <div className="space-y-8 text-slate-200">
          <section>
            <h2 className="mb-3 text-2xl font-semibold text-white">1. Scope</h2>
            <p>
              This policy applies to paid digital services and subscriptions purchased through the Clisonix platform.
            </p>
          </section>

          <section>
            <h2 className="mb-3 text-2xl font-semibold text-white">2. Subscription Cancellation</h2>
            <ul className="list-disc space-y-2 pl-5">
              <li>You can cancel at any time before the next billing cycle.</li>
              <li>Cancellation stops future billing; previously billed periods are generally non-refundable.</li>
              <li>Access remains active until the end of the paid period unless terminated for abuse or legal reasons.</li>
            </ul>
          </section>

          <section>
            <h2 className="mb-3 text-2xl font-semibold text-white">3. Eligible Refund Cases</h2>
            <ul className="list-disc space-y-2 pl-5">
              <li>Duplicate payment or billing error caused by system or processor issues.</li>
              <li>Unauthorized charge confirmed after security and account investigation.</li>
              <li>Service outage materially preventing paid feature usage for an extended period.</li>
            </ul>
          </section>

          <section>
            <h2 className="mb-3 text-2xl font-semibold text-white">4. Non-Refundable Cases</h2>
            <ul className="list-disc space-y-2 pl-5">
              <li>Partial usage of a billing period where service remained available.</li>
              <li>Change of mind after successful delivery of digital services.</li>
              <li>Violations of Terms & Conditions leading to account restrictions.</li>
            </ul>
          </section>

          <section>
            <h2 className="mb-3 text-2xl font-semibold text-white">5. How to Request a Refund</h2>
            <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-5">
              <p>Email: {BUSINESS_IDENTITY.supportEmail}</p>
              <p className="mt-2">Subject line: Refund Request - [Account Email]</p>
              <p className="mt-2">
                Include invoice/reference ID, payment date, and reason for refund. We typically respond within
                5 business days.
              </p>
            </div>
          </section>

          <section>
            <h2 className="mb-3 text-2xl font-semibold text-white">6. Buyer Protection Channels</h2>
            <ul className="list-disc space-y-2 pl-5">
              {BUSINESS_IDENTITY.buyerProtection.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>
        </div>

        <div className="mt-12 border-t border-slate-800 pt-6 text-sm text-slate-400">
          <p>
            See also <Link href="/terms" className="text-emerald-300 hover:text-emerald-200">Terms & Conditions</Link> and{' '}
            <Link href="/contact" className="text-emerald-300 hover:text-emerald-200">Contact</Link>.
          </p>
        </div>
      </div>
    </main>
  );
}
