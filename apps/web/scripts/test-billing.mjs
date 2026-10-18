import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, resolve } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import ts from "typescript";

const require = createRequire(import.meta.url);
const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
function load(relative, mocks = {}) {
  const filename = resolve(root, relative);
  const compiled = ts.transpileModule(readFileSync(filename, "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true },
  }).outputText;
  const module = { exports: {} };
  const localRequire = name => {
    if (name in mocks) return mocks[name];
    if (name.startsWith("@/lib/billing/")) return load(`src/${name.slice(2)}.ts`, mocks);
    return require(name);
  };
  new Function("require", "module", "exports", compiled)(localRequire, module, module.exports);
  return module.exports;
}

test("webhook proxy preserves signed bytes and persistence failure status", async () => {
  const original = globalThis.fetch;
  process.env.API_INTERNAL_URL = "http://api.test";
  const raw = '{ "signed": "exact bytes" }';
  globalThis.fetch = async (url, options) => {
    assert.equal(url, "http://api.test/api/v1/billing/webhook");
    assert.equal(Buffer.from(options.body).toString(), raw);
    assert.equal(options.headers["Stripe-Signature"], "signed");
    return Response.json({ error: "Persistence offline" }, { status: 503 });
  };
  try {
    const { forwardStripeWebhook } = load("src/lib/billing/stripe-webhook.ts");
    const result = await forwardStripeWebhook(new Request("https://web.test/api/webhooks/stripe", {
      method: "POST", headers: { "stripe-signature": "signed" }, body: raw,
    }));
    assert.equal(result.status, 503);
    assert.equal((await result.json()).error, "Persistence offline");
  } finally { globalThis.fetch = original; }
});

test("checkout authenticates before calling Stripe and rejects foreign redirects", async () => {
  let calls = 0;
  let current = null;
  class Stripe { constructor() { calls++; } }
  const { POST } = load("app/api/billing/checkout/route.ts", {
    "@/lib/auth/server": { currentUser: async () => current }, stripe: Stripe,
  });
  process.env.NEXT_PUBLIC_APP_URL = "https://web.test";
  process.env.STRIPE_PRICE_PROFESSIONAL_MONTHLY = "price_pro";
  const request = value => new Request("https://web.test/api/billing/checkout", {
    method: "POST", body: JSON.stringify(value),
  });
  assert.equal((await POST(request({ plan: "professional" }))).status, 401);
  current = { id: "usr_one", emailAddresses: [{ emailAddress: "buyer@example.com" }] };
  assert.equal((await POST(request({ plan: "professional", successUrl: "https://foreign.test" }))).status, 400);
  assert.equal(calls, 0);
});

test("subscription checkout carries durable account identity and scoped idempotency", async () => {
  let captured;
  let requestOptions;
  const sdk = {
    prices: { retrieve: async () => ({ active: true, recurring: { interval: "month" } }) },
    customers: { list: async () => ({ data: [{ id: "cus_one", metadata: { user_id: "usr_one" } }] }) },
    subscriptions: { list: async () => ({ data: [] }) },
    checkout: { sessions: { create: async (params, options) => {
      captured = params; requestOptions = options; return { id: "cs_one", url: "https://checkout.stripe.com/session" };
    } } },
  };
  class Stripe { constructor() { return sdk; } }
  process.env.STRIPE_SECRET_KEY = "sk_test_unit_only";
  process.env.STRIPE_PRICE_PROFESSIONAL_MONTHLY = "price_pro";
  const { POST } = load("app/api/billing/checkout/route.ts", {
    stripe: Stripe,
    "@/lib/auth/server": { currentUser: async () => ({ id: "usr_one", emailAddresses: [{ emailAddress: "buyer@example.com" }] }) },
  });
  const result = await POST(new Request("https://web.test/api/billing/checkout", {
    method: "POST", body: JSON.stringify({ plan: "professional" }), headers: { "idempotency-key": "request-one" },
  }));
  assert.equal(result.status, 200);
  assert.equal(captured.metadata.user_id, "usr_one");
  assert.equal(captured.subscription_data.metadata.plan, "professional");
  assert.equal(requestOptions.idempotencyKey, "sub:usr_one:request-one");
});

test("one-time checkout rejects invalid quantities before creating a session", async () => {
  const { POST } = load("app/api/stripe/checkout/one-time/route.ts", {
    "@/lib/auth/server": { currentUser: async () => ({ id: "usr_one", emailAddresses: [{ emailAddress: "buyer@example.com" }] }) },
  });
  for (const quantity of [-1, 0, 1.5, 101, "2"]) {
    const result = await POST(new Request("https://web.test/api/stripe/checkout/one-time", {
      method: "POST", body: JSON.stringify({ price: "price_one", quantity }),
    }));
    assert.equal(result.status, 400);
  }
});

test("Auth.js refreshes plans and rejects revoked central sessions", async () => {
  let config;
  const original = globalThis.fetch;
  process.env.AUTH_INTERNAL_URL = "http://users.test";
  load("src/lib/auth/core.ts", {
    "next-auth": options => { config = options; return {}; },
    "next-auth/providers/credentials": options => options,
  });
  let phase = "login";
  globalThis.fetch = async (_url, options) => {
    if (phase === "login") return Response.json({ success: true, access_token: "private-backend-token",
      user: { user_id: "usr_one", email: "buyer@example.com", role: "superadmin", plan: "free" } });
    assert.equal(options.headers.Authorization, "Bearer private-backend-token");
    if (phase === "revoked") return new Response(null, { status: 401 });
    return Response.json({ valid: true, user: { user_id: "usr_one", plan: "professional", role: "user" } });
  };
  try {
    const user = await config.providers[0].authorize({ email: "buyer@example.com", password: "test-only" });
    assert.equal(user.role, "admin");
    phase = "paid";
    const token = await config.callbacks.jwt({ token: {}, user });
    assert.equal(token.plan, "professional");
    const session = await config.callbacks.session({ session: { user: {} }, token });
    assert.equal(session.user.plan, "professional");
    assert.equal(session.user.internalAccessToken, undefined);
    phase = "revoked";
    assert.equal(await config.callbacks.jwt({ token }), null);
  } finally { globalThis.fetch = original; }
});
