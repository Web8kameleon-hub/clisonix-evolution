'use client';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-white">
      <div className="max-w-4xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Terms of Use</h1>
          <p className="text-slate-400">Clisonix Cloud</p>
          <p className="text-sm text-slate-500 mt-2">Last updated: May 2026</p>
        </div>

        <div className="space-y-8 text-slate-300">
          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">1. Intellectual Property</h2>
            <p className="mb-4">
              All software, APIs, SDKs, models, documentation, designs, and other materials
              provided under Clisonix are protected by intellectual property law and remain
              the exclusive property of <strong className="text-white">Ledjan Ahmati / Clisonix Cloud</strong>,
              unless explicitly stated otherwise.
            </p>
            <p>
              No ownership rights are transferred to users by accessing the platform.
            </p>
            <p className="mt-4">
              <strong className="text-white">Registered legal entity:</strong> ABA GmbH.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">2. Permitted Uses</h2>
            <ul className="list-disc list-inside space-y-2">
              <li>Using Clisonix services through the official web app, API, and approved SDKs</li>
              <li>Using free-tier access within published limits</li>
              <li>Using paid features according to your active plan and usage limits</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">3. Prohibited Uses</h2>
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6">
              <ul className="list-disc list-inside space-y-2">
                <li>Unauthorized copying, resale, redistribution, reverse engineering, or sublicensing</li>
                <li>Bypassing authentication, metering, billing, quotas, or security controls</li>
                <li>Automated scraping or abuse outside documented endpoints and limits</li>
                <li>Using the service for illegal activity, malware, fraud, or harmful automation</li>
                <li>Using Clisonix trademarks or branding without written authorization</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">4. API Access and Metering</h2>
            <p className="mb-4">
              API usage is usage-based (pay-per-use) and may include free-tier quotas.
              Usage is metered by requests, compute operations, streamed events, generated output,
              or other published billing units.
            </p>
            <ul className="list-disc list-inside space-y-2">
              <li>Metered usage is billed according to the active public pricing page or enterprise contract</li>
              <li>You are responsible for API key security and all activity under your account</li>
              <li>Abusive usage may be rate-limited, suspended, or terminated</li>
              <li>Refunds, if any, follow the published refund policy or written enterprise agreement</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">5. Plans, Payments, and Changes</h2>
            <p className="mb-4">
              We may update pricing, plan limits, features, and service configuration over time.
              Material changes are reflected on public pages and/or account notices.
            </p>
            <p>
              Taxes, payment processor fees, and local obligations may apply based on jurisdiction.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">6. Availability and Service Limits</h2>
            <p className="mb-4">
              Clisonix aims for high availability, but uninterrupted access is not guaranteed.
              Service may be affected by maintenance, upstream outages, abuse protection,
              or force majeure.
            </p>
            <p>
              We may enforce technical limits (for example rate limits, request size, queue depth,
              and concurrency) to keep the platform stable and secure.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">7. Data and Privacy</h2>
            <p>
              Personal data processing is described in the Privacy Policy. By using Clisonix,
              you agree that operational logs and usage telemetry may be processed for security,
              billing, reliability, and abuse prevention.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">8. Enforcement</h2>
            <p>
              Violations of these terms will be pursued under applicable copyright,
              intellectual property, and trade secret laws in all applicable jurisdictions.
              We actively monitor for unauthorized use and will take legal action when necessary.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">9. Disclaimer and Liability</h2>
            <p className="mb-4">
              The service is provided &ldquo;as is&rdquo; and &ldquo;as available&rdquo; without warranties of any kind,
              to the maximum extent permitted by law.
            </p>
            <p>
              To the maximum extent permitted by law, Clisonix is not liable for indirect,
              incidental, special, consequential, or exemplary damages.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">10. Contact</h2>
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-6">
              <p className="mb-2">For legal, licensing, or enterprise requests:</p>
              <p className="font-mono">clisonix@pm.me</p>
            </div>
          </section>
        </div>

        <div className="mt-16 pt-8 border-t border-slate-700 text-center text-slate-500">
          <p>© 2026 Clisonix Cloud. All rights reserved.</p>
          <p className="mt-2">Terms of Use and API Commercial Terms</p>
        </div>
      </div>
    </div>
  );
}

