import type { Metadata } from 'next';
import { BUSINESS_IDENTITY, formatBusinessAddress } from '../lib/business-identity';

export const metadata: Metadata = {
  title: 'Contact | Clisonix',
  description:
    'Official contact page with verified business identity, address, support email, and phone.',
  alternates: {
    canonical: '/contact',
  },
};

export default function ContactPage() {
  const officeAddress = formatBusinessAddress();

  const contactSchema = {
    '@context': 'https://schema.org',
    '@type': 'ContactPage',
    name: 'Clisonix Contact',
    url: `${BUSINESS_IDENTITY.domain}/contact`,
    about: {
      '@type': 'Organization',
      name: BUSINESS_IDENTITY.legalName,
      telephone: BUSINESS_IDENTITY.supportPhone,
      email: BUSINESS_IDENTITY.supportEmail,
      address: {
        '@type': 'PostalAddress',
        streetAddress: BUSINESS_IDENTITY.address.street,
        postalCode: BUSINESS_IDENTITY.address.postalCode,
        addressLocality: BUSINESS_IDENTITY.address.city,
        addressRegion: BUSINESS_IDENTITY.address.region,
        addressCountry: BUSINESS_IDENTITY.address.country,
      },
      sameAs: BUSINESS_IDENTITY.socialProfiles.map((profile) => profile.url),
    },
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 px-6 py-16 text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(contactSchema) }}
      />

      <div className="mx-auto max-w-5xl">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold md:text-5xl">Contact</h1>
          <p className="mt-4 text-lg text-slate-300">
            Official business contact details for {BUSINESS_IDENTITY.brandName}.
          </p>
        </header>

        <div className="grid gap-6 md:grid-cols-2">
          <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
            <h2 className="text-2xl font-semibold">Business Identity</h2>
            <dl className="mt-4 space-y-3 text-slate-200">
              <div>
                <dt className="text-sm uppercase tracking-[0.16em] text-slate-400">Legal Name</dt>
                <dd className="font-medium text-white">{BUSINESS_IDENTITY.legalName}</dd>
              </div>
              <div>
                <dt className="text-sm uppercase tracking-[0.16em] text-slate-400">Registration</dt>
                <dd className="font-medium text-white">{BUSINESS_IDENTITY.registrationNumber}</dd>
              </div>
              <div>
                <dt className="text-sm uppercase tracking-[0.16em] text-slate-400">Tax/VAT</dt>
                <dd className="font-medium text-white">{BUSINESS_IDENTITY.taxId}</dd>
              </div>
            </dl>
          </section>

          <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
            <h2 className="text-2xl font-semibold">Direct Contacts</h2>
            <ul className="mt-4 space-y-3 text-slate-200">
              <li>
                Support: <a href={`mailto:${BUSINESS_IDENTITY.supportEmail}`} className="text-emerald-300 hover:text-emerald-200">{BUSINESS_IDENTITY.supportEmail}</a>
              </li>
              <li>
                Privacy: <a href={`mailto:${BUSINESS_IDENTITY.privacyEmail}`} className="text-emerald-300 hover:text-emerald-200">{BUSINESS_IDENTITY.privacyEmail}</a>
              </li>
              <li>
                Legal: <a href={`mailto:${BUSINESS_IDENTITY.legalEmail}`} className="text-emerald-300 hover:text-emerald-200">{BUSINESS_IDENTITY.legalEmail}</a>
              </li>
              <li>Phone: {BUSINESS_IDENTITY.supportPhone}</li>
            </ul>
          </section>

          <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 md:col-span-2">
            <h2 className="text-2xl font-semibold">Operational Office</h2>
            <p className="mt-3 text-slate-200">{officeAddress}</p>
            <p className="mt-4 text-sm text-slate-400">
              For legal correspondence, include your account email (if applicable) and your request subject.
            </p>
          </section>

          <section className="rounded-2xl border border-blue-500/20 bg-blue-500/10 p-6 md:col-span-2">
            <h2 className="text-2xl font-semibold">Official Social Profiles</h2>
            <ul className="mt-4 flex flex-wrap gap-3 text-sm">
              {BUSINESS_IDENTITY.socialProfiles.map((profile) => (
                <li key={profile.name}>
                  <a
                    href={profile.url}
                    className="inline-flex rounded-full border border-blue-400/40 px-4 py-2 text-blue-100 hover:border-blue-300 hover:text-white"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {profile.name}
                  </a>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </div>
    </main>
  );
}
