'use client';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-white">
      <div className="max-w-4xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Privacy Policy</h1>
          <p className="text-slate-400">Clisonix Cloud</p>
          <p className="text-sm text-slate-500 mt-2">Last updated: April 2026</p>
        </div>

        <div className="space-y-8 text-slate-300">
          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">1. Overview</h2>
            <p>
              Clisonix Cloud respects your privacy. This policy explains what information we collect,
              how we use it, and how we protect it when you visit <strong className="text-white">www.clisonix.com</strong>
              or sign in to the platform.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">2. Information We Collect</h2>
            <ul className="list-disc list-inside space-y-2">
              <li>Basic account information such as your name, email address, and profile image when you sign in with Google or Apple.</li>
              <li>Technical information such as browser type, device information, IP address, and usage logs for security and diagnostics.</li>
              <li>Optional interaction data needed to provide Clisonix features, analytics, and account-related support.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">3. How We Use Information</h2>
            <ul className="list-disc list-inside space-y-2">
              <li>To authenticate users and keep accounts secure.</li>
              <li>To operate, maintain, and improve the Clisonix platform.</li>
              <li>To provide customer support and respond to inquiries.</li>
              <li>To detect abuse, fraud, security incidents, and service issues.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">4. Google OAuth and Third-Party Sign-In</h2>
            <p className="mb-4">
              If you choose to sign in with Google, Clisonix receives only the information necessary
              to authenticate your account, such as your Google email address, name, and profile image,
              subject to the permissions granted by you.
            </p>
            <p>
              Clisonix does not sell your Google user data and uses it only for authentication,
              account access, and core platform functionality.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">5. Data Sharing</h2>
            <p>
              We do not sell personal information. Data may be shared only with infrastructure,
              authentication, analytics, or security providers when required to operate the service,
              comply with the law, or protect users and the platform.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">6. Data Retention and Security</h2>
            <p className="mb-4">
              We retain information only as long as reasonably necessary for service delivery,
              legal compliance, dispute resolution, and security.
            </p>
            <p>
              Clisonix uses administrative, technical, and organizational safeguards to help protect
              personal information against unauthorized access, alteration, disclosure, or destruction.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">7. Your Rights</h2>
            <p>
              Depending on your jurisdiction, you may have rights to access, correct, delete,
              or object to the processing of your personal data. You may contact us to request help
              with privacy-related questions.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">8. Contact</h2>
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-6">
              <p>For privacy questions or requests, contact:</p>
              <p className="font-mono mt-2">clisonix@pm.me</p>
            </div>
          </section>
        </div>

        <div className="mt-16 pt-8 border-t border-slate-700 text-center text-slate-500">
          <p>© 2026 Clisonix. All rights reserved.</p>
          <p className="mt-2">Privacy Policy for Clisonix Cloud</p>
        </div>
      </div>
    </div>
  );
}

