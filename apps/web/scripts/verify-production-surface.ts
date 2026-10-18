import { readFileSync } from 'node:fs';
import { performance } from 'node:perf_hooks';

const started = performance.now();
const root = new URL('../', import.meta.url);
const read = (path: string) => readFileSync(new URL(path, root), 'utf8');

const workspace = read('app/app/AppWorkspaceClient.tsx');
const home = read('app/NewHomePageClient.tsx');
const pricing = read('app/pricing/page.tsx');
const platformMap = read('src/lib/modules/platform-map.ts');
const canonicalWebhook = read('app/api/billing/webhook/route.ts');
const aliasWebhook = read('app/api/webhooks/stripe/route.ts');
const oceanStreamRoute = read('app/api/ocean/stream/route.ts');

const forbidden: Array<[string, string, string]> = [
  ['workspace', workspace, 'Investor brief'],
  ['workspace', workspace, 'Send draft to Gmail'],
  ['workspace', workspace, 'PRODUCT_CATALOG'],
  ['workspace', workspace, 'localhost:8001'],
  ['homepage', home, 'All systems online'],
  ['homepage', home, '99.97% uptime'],
  ['homepage', home, 'Ocean Online'],
  ['homepage', home, 'Platform Online'],
  ['pricing', pricing, 'PRODUCT_CATALOG'],
  ['module map', platformMap, 'http://localhost:8030/chat'],
];

const violations = forbidden.filter(([, content, value]) => content.includes(value));
if (violations.length) {
  for (const [surface, , value] of violations) {
    console.error(`NO_FAKE violation in ${surface}: ${value}`);
  }
  process.exit(1);
}

const required: Array<[string, string, string]> = [
  ['workspace', workspace, 'useServiceDiscovery'],
  ['workspace', workspace, 'No jobs have been created in this session.'],
  ['pricing', pricing, "fetch('/api/billing/checkout'"],
  ['pricing', pricing, 'Pricing temporarily unavailable'],
  ['pricing', pricing, 'Stripe-verified pricing'],
  ['canonical webhook', canonicalWebhook, 'throw new Error("Internal billing sync not configured")'],
  ['webhook alias', aliasWebhook, 'export { POST } from "../../billing/webhook/route"'],
  ['Ocean relay', oceanStreamRoute, 'xlc_enabled: false'],
  ['Ocean relay', oceanStreamRoute, '"llama3.1:8b"'],
];

const missing = required.filter(([, content, value]) => !content.includes(value));
if (missing.length) {
  for (const [surface, , value] of missing) {
    console.error(`Production contract missing in ${surface}: ${value}`);
  }
  process.exit(1);
}

const elapsedMs = performance.now() - started;
console.log(`Production surface verification passed (${forbidden.length + required.length} assertions, ${elapsedMs.toFixed(2)} ms)`);
