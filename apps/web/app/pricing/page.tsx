'use client';

import Link from 'next/link';
import Script from 'next/script';
import { useEffect } from 'react';
import { trackEconomy } from '@/lib/economy/track';

/**
 * PRICING PAGE - Stripe Pricing Table Integration
 *
 * Plans (via Stripe Pricing Table):
 * - Basic: €3.99/month
 * - Pro: €10.00/month
 * - Pro Yearly: €99.00/year
 */

export default function PricingPage() {
  const stripePublishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '';
  const stripePricingTableId = process.env.NEXT_PUBLIC_STRIPE_PRICING_TABLE_ID || '';

  useEffect(() => {
    trackEconomy({
      economy_code: 'CTS',
      slot: 'pricing',
      placement_id: 'pricing-page',
      provider: 'clisonix',
    });
  }, []);

  const faqs = [
    {
      q: 'Can I try Clisonix before paying?',
      a: 'Absolutely! The Free plan gives you access to selected public blog content before you subscribe.'
    },
    {
      q: 'What payment methods do you accept?',
      a: 'Primary billing runs through Stripe card checkout. SEPA and PayPal are enabled only when their operational integration paths are fully configured and verified.'
    },
    {
      q: 'Can I cancel anytime?',
      a: 'Yes! No contracts, no commitments. Cancel your subscription anytime and you\'ll keep access until the end of your billing period.'
    },
    {
      q: 'What plans do you offer for the blog?',
      a: 'Blog Basic is €3.99/month, Blog Pro is €10.00/month, and Blog Pro Yearly is €99.00/year with annual savings.'
    },
    {
      q: 'What is Curiosity Ocean?',
      a: 'Curiosity Ocean is our AI assistant powered by advanced language models. It can analyze documents, answer questions, and help with research using camera and microphone tools.'
    },
    {
      q: 'Do you offer refunds?',
      a: 'Yes, we offer a 14-day money-back guarantee. If you\'re not satisfied, contact us for a full refund.'
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
            <Link href="/why-clisonix" className="text-gray-400 hover:text-white transition-colors">Why Clisonix</Link>
            <Link href="/platform" className="text-gray-400 hover:text-white transition-colors">Platform</Link>
            <Link
              href="/modules"
              onClick={() =>
                trackEconomy({
                  economy_code: 'CLK',
                  slot: 'pricing',
                  placement_id: 'open-dashboard-nav',
                })
              }
              className="px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg transition-colors"
            >
              Open Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-8 px-6 text-center">
        <h1 className="text-5xl font-bold mb-4">
          Simple, Transparent Pricing
        </h1>
        <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
          Blog subscriptions: €3.99/month, €10.00/month, or €99/year. Cancel anytime.
        </p>
      </section>

      {/* Stripe Pricing Table */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <Script
            async
            src="https://js.stripe.com/v3/pricing-table.js"
            strategy="lazyOnload"
          />
          {stripePublishableKey && stripePricingTableId ? (
            <>
              {/* @ts-expect-error - Stripe custom element */}
              <stripe-pricing-table
                pricing-table-id={stripePricingTableId}
                publishable-key={stripePublishableKey}
              />
            </>
          ) : (
            <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">
              Billing setup in progress. Add <strong>NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY</strong> and <strong>NEXT_PUBLIC_STRIPE_PRICING_TABLE_ID</strong> to environment variables.
            </div>
          )}
        </div>
      </section>

      {/* Free Tier Info */}
      <section className="py-8 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <div className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700">
            <h3 className="text-xl font-bold mb-2">🆓 Free Tier Available</h3>
            <p className="text-gray-400 mb-4">
              Want to try before you buy? Get 10 free research articles and basic Curiosity Ocean access.
            </p>
            <Link
              href="/sign-up"
              onClick={() =>
                trackEconomy({
                  economy_code: 'CTA',
                  slot: 'pricing',
                  placement_id: 'start-free',
                })
              }
              className="inline-flex px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-xl font-semibold transition-colors"
            >
              Start Free →
            </Link>
          </div>
        </div>
      </section>

      {/* Trust Badges */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            <div className="text-center">
              <div className="text-2xl font-bold">99.97%</div>
              <div className="text-sm text-gray-400">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">&lt;100ms</div>
              <div className="text-sm text-gray-400">Latency</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">SOC2</div>
              <div className="text-sm text-gray-400">Compliant</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">GDPR</div>
              <div className="text-sm text-gray-400">Ready</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">24/7</div>
              <div className="text-sm text-gray-400">Support</div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQs */}
      <section className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>

          <div className="space-y-6">
            {faqs.map((faq) => (
              <div key={faq.q} className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
                <h3 className="font-semibold text-lg mb-2">{faq.q}</h3>
                <p className="text-gray-400">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 text-center">
        <h2 className="text-3xl font-bold mb-4">Still have questions?</h2>
        <p className="text-gray-400 mb-8">Our team is here to help you find the perfect plan.</p>
        <Link
          href="mailto:clisonix@pm.me"
          onClick={() =>
            trackEconomy({
              economy_code: 'CTC',
              slot: 'pricing',
              placement_id: 'contact-support',
            })
          }
          className="inline-flex px-8 py-4 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold transition-colors"
        >
          Contact Support
        </Link>
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








