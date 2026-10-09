import type { Metadata } from "next";
import { headers } from "next/headers";
import { Inter } from "next/font/google";
import "./globals.css";
import { CONSENT_STATE_CHANGE_EVENT, CONSENT_STORAGE_KEY } from "../src/lib/consent/state";
import { DynamicFavicon } from "../src/components/DynamicFavicon";

const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL?.replace(/\/+$/, "") ||
  "https://www.clisonix.com";
const SITE_NAME = "Clisonix";
const SITE_PRODUCT_NAME = "Clisonix Cloud";
const SITE_DESCRIPTION =
  "Official Clisonix Cloud website and software platform at www.clisonix.com for AI workflows, neuroscience research, EEG analysis, neural tooling, real-time analytics, and developer infrastructure.";
const SITE_DISAMBIGUATION =
  "Clisonix is the official AI and neuroscience platform at www.clisonix.com and is not affiliated with Clarisonic beauty devices or other similarly named brands.";
const SEO_KEYWORDS = [
  "Clisonix",
  "Clisonix Cloud",
  "clisonix.com",
  "Clisonix official website",
  "Clisonix official site",
  "Clisonix platform",
  "Clisonix AI",
  "Curiosity Ocean",
  "KLOUd Bridge",
  "neural intelligence platform",
  "AI workflow platform",
  "EEG analysis software",
  "neural synthesis",
  "real-time analytics",
  "industrial intelligence",
  "developer AI platform",
  "brand verification",
  "Ledjan Ahmati",
  "Clisonix founder",
  "Clisonix CEO",
  "public safety engineer",
  "civil safety engineer",
  "ISO compliance specialist",
  "EuroNorm specialist",
  "TUV specialist",
  "civil emergency specialist",
  "natural emergency response",
  "industrial emergency readiness",
];
const SITE_OG_IMAGE = `${SITE_URL}/icons/icon-512x512.png`;
const SITE_LOGO = `${SITE_URL}/apple-touch-icon.png`;
const SUPPORT_EMAIL = process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "";
const GOOGLE_SITE_VERIFICATION =
  process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION ||
  process.env.GOOGLE_SITE_VERIFICATION ||
  undefined;

const CONSENT_MODE_BOOTSTRAP_SCRIPT = `
  (function () {
    if (typeof window === 'undefined') return;

    window.dataLayer = window.dataLayer || [];
    function gtag(){window.dataLayer.push(arguments);}
    window.gtag = window.gtag || gtag;

    function applyConsentMode(consentState) {
      var adsEnabled = !!(consentState && consentState.ads);
      var analyticsEnabled = !!(consentState && consentState.analytics);
      var adPersonalizationEnabled = !!(consentState && consentState.adPersonalization && adsEnabled);

      window.gtag('consent', 'update', {
        ad_storage: adsEnabled ? 'granted' : 'denied',
        analytics_storage: analyticsEnabled ? 'granted' : 'denied',
        ad_user_data: adsEnabled ? 'granted' : 'denied',
        ad_personalization: adPersonalizationEnabled ? 'granted' : 'denied'
      });
    }

    function getStoredConsentState() {
      try {
        var raw = window.localStorage.getItem('${CONSENT_STORAGE_KEY}');
        if (!raw) return null;

        if (raw === 'accepted') {
          return {
            analytics: true,
            ads: true,
            adPersonalization: true
          };
        }

        if (raw === 'declined') {
          return {
            analytics: false,
            ads: false,
            adPersonalization: false
          };
        }

        return JSON.parse(raw);
      } catch (error) {
        return null;
      }
    }

    window.gtag('consent', 'default', {
      ad_storage: 'denied',
      analytics_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      wait_for_update: 500
    });

    var initialConsent = getStoredConsentState();
    if (initialConsent) {
      applyConsentMode(initialConsent);
    }

    window.addEventListener('${CONSENT_STATE_CHANGE_EVENT}', function (event) {
      if (event && event.detail) {
        applyConsentMode(event.detail);
      }
    });

    window.addEventListener('storage', function (event) {
      if (!event || event.key !== '${CONSENT_STORAGE_KEY}') return;
      var nextConsent = getStoredConsentState();
      if (nextConsent) {
        applyConsentMode(nextConsent);
        return;
      }

      window.gtag('consent', 'update', {
        ad_storage: 'denied',
        analytics_storage: 'denied',
        ad_user_data: 'denied',
        ad_personalization: 'denied'
      });
    });
  })();
`;

import AppProviders from '../src/components/AppProviders';


const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: `${SITE_PRODUCT_NAME} | Official Clisonix Platform`,
    template: `%s | ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,
  keywords: SEO_KEYWORDS,
  applicationName: SITE_PRODUCT_NAME,
  icons: {
    icon: [
      { url: '/favicon.svg?v=3', type: 'image/svg+xml' },
      { url: '/icons/icon-192x192.png?v=3', sizes: '192x192', type: 'image/png' },
    ],
    shortcut: ['/icons/icon-192x192.png?v=3'],
    apple: [{ url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' }],
  },
  manifest: '/manifest.json',
  category: 'Technology',
  verification: GOOGLE_SITE_VERIFICATION ? {
    google: GOOGLE_SITE_VERIFICATION,
  } : undefined,
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const nonce = (await headers()).get("x-nonce") ?? undefined;

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta httpEquiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="description" content={SITE_DESCRIPTION} />
        <meta name="keywords" content={SEO_KEYWORDS.join(", ")} />
        <link rel="icon" href="/favicon.svg?v=3" type="image/svg+xml" />
        <link rel="icon" href="/icons/icon-192x192.png?v=3" sizes="192x192" type="image/png" />
        <link rel="shortcut icon" href="/icons/icon-192x192.png?v=3" type="image/png" />
        {/* Schema.org Structured Data for Rich Snippets */}
        <script
          nonce={nonce}
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebSite",
              "name": SITE_NAME,
              "alternateName": ["Clisonix Cloud", "Clisonix AI"],
              "url": SITE_URL,
              "description": SITE_DESCRIPTION,
              "disambiguatingDescription": SITE_DISAMBIGUATION,
              "inLanguage": ["en", "sq"],
              "potentialAction": {
                "@type": "SearchAction",
                "target": `${SITE_URL}/modules/curiosity-ocean?topic={search_term_string}`,
                "query-input": "required name=search_term_string"
              },
              "publisher": {
                "@type": "Organization",
                "name": SITE_NAME,
                "url": SITE_URL,
                "logo": SITE_LOGO,
                "sameAs": [
                  SITE_URL,
                  "https://github.com/Web8kameleon-hub/clisonix.com"
                ]
              }
            })
          }}
        />
        <script
          nonce={nonce}
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              "name": SITE_PRODUCT_NAME,
              "applicationCategory": "DeveloperApplication",
              "operatingSystem": "Web",
              "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
              },
              "description": SITE_DESCRIPTION,
              "disambiguatingDescription": SITE_DISAMBIGUATION,
              "url": SITE_URL,
              "author": {
                "@type": "Organization",
                "name": SITE_NAME,
                "url": SITE_URL
              }
            })
          }}
        />
        {/* Organization Schema */}
        <script
          nonce={nonce}
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "Organization",
              "name": SITE_NAME,
              "alternateName": ["Clisonix Cloud", "Clisonix AI"],
              "url": SITE_URL,
              "logo": SITE_LOGO,
              "description": SITE_DESCRIPTION,
              "disambiguatingDescription": SITE_DISAMBIGUATION,
              "knowsAbout": [
                "AI workflows",
                "neuroscience software",
                "EEG analysis",
                "developer APIs",
                "real-time analytics",
                "public safety engineering",
                "civil emergency systems",
                "ISO and EuroNorm compliance"
              ],
              "founder": {
                "@type": "Person",
                "name": "Ledjan Ahmati",
                "jobTitle": "Founder and CEO",
                "worksFor": {
                  "@type": "Organization",
                  "name": SITE_NAME,
                  "url": SITE_URL
                },
                "description": "Public and civil safety engineer, self-employed for 21 years, specialized in ISO, EuroNorm, TUV standards, and emergency readiness for civil and natural emergency scenarios.",
                "knowsAbout": [
                  "Public safety engineering",
                  "Civil safety engineering",
                  "ISO standards",
                  "EuroNorm standards",
                  "TUV compliance",
                  "Civil emergency response",
                  "Natural emergency readiness"
                ]
              },
              ...(SUPPORT_EMAIL ? { "email": SUPPORT_EMAIL } : {}),
              "sameAs": [
                "https://github.com/Web8kameleon-hub/clisonix.com"
              ],
              ...(SUPPORT_EMAIL
                ? {
                    "contactPoint": {
                      "@type": "ContactPoint",
                      "contactType": "customer support",
                      "email": SUPPORT_EMAIL,
                      "availableLanguage": ["English", "Albanian"]
                    }
                  }
                : {})
            })
          }}
        />
        <script
          nonce={nonce}
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "Person",
              "name": "Ledjan Ahmati",
              "jobTitle": "Founder and CEO",
              "description": "Public and civil safety engineer, self-employed for 21 years, specialized in ISO, EuroNorm, TUV standards, and emergency readiness for civil and natural emergency scenarios.",
              "worksFor": {
                "@type": "Organization",
                "name": SITE_NAME,
                "url": SITE_URL
              },
              "knowsAbout": [
                "Public safety engineering",
                "Civil safety engineering",
                "ISO standards",
                "EuroNorm standards",
                "TUV compliance",
                "Civil emergency response",
                "Natural emergency readiness",
                "AI safety operations"
              ]
            })
          }}
        />
        <meta name="theme-color" content="#6366f1" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <link rel="icon" href="/favicon.svg?v=3" type="image/svg+xml" sizes="any" />
        <link rel="icon" href="/icons/icon-192x192.png?v=3" sizes="192x192" type="image/png" />
        <link rel="shortcut icon" href="/icons/icon-192x192.png?v=3" type="image/png" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180" />
        <link rel="manifest" href="/manifest.json" />
        <script
          nonce={nonce}
          id="clisonix-consent-mode-bootstrap"
          dangerouslySetInnerHTML={{
            __html: CONSENT_MODE_BOOTSTRAP_SCRIPT,
          }}
        />
        <script
          nonce={nonce}
          dangerouslySetInnerHTML={{
            __html: `
              if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
                window.addEventListener('load', function () {
                  navigator.serviceWorker.register('/sw-music-studio.js').catch(function () {});
                });
              }
            `,
          }}
        />
      </head>
      <body
        className={`${inter.variable} antialiased`}
        suppressHydrationWarning
      >
        <AppProviders>
          <DynamicFavicon />
          {children}
        </AppProviders>
      </body>
    </html>
  );
}









