# Clisonix Workers for Platforms Bootstrap

This folder maps the Cloudflare Workers for Platforms requirements into versioned config.

## What this covers

- Dispatcher binding via `DISPATCH_NAMESPACE`
- KV binding (`BINDING_NAME`)
- D1 binding (`DB` -> `dbclisonix`)
- R2 buckets (`vibesdk-templates`, `clisonixbucket`)
- Safe env var placeholders and secret setup

## Setup

1. Copy `wrangler.toml.example` to `wrangler.toml`.
2. Replace IDs for KV and D1 with real Cloudflare IDs.
3. Ensure R2 buckets exist in dashboard:
   - `vibesdk-templates`
   - `clisonixbucket`
4. Set secrets:

```bash
wrangler secret put GOOGLE_AI_STUDIO_API_KEY
wrangler secret put JWT_SECRET
wrangler secret put WEBHOOK_SECRET
```

5. Deploy:

```bash
bun run build
bun run deploy
```

## R2 note

If dashboard says R2 is not enabled for the account plan, enable/upgrade R2 first. Without R2 subscription, bindings are configured but runtime access will fail.

## Git policy

Do not commit `wrangler.toml` with real IDs/secrets for production tenants.
Keep only templated configuration in git.
