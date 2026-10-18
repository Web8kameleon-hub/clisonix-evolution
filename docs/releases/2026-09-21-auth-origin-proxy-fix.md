# Internal auth reverse-proxy origin fix — 2026-09-21

## Release

Fixes false `cross_site_blocked` responses for same-origin registration requests
served through Cloudflare/Nginx. Internal password authentication remains the only
provider. Google authentication is not restored, and Redis is not changed.

## Security behavior

- Exact-origin comparison only; no suffix or wildcard trust.
- Trust inputs are the request origin, canonical Auth.js URLs, the public app URL,
  and the proxy-provided host/protocol.
- Missing Origin/Referer retains the existing non-browser compatibility behavior.
- `Sec-Fetch-Site: cross-site` remains blocked by middleware.

## Tests and edge cases

`npm run test:auth-origin` covers canonical production origin, forwarded origin,
apex/canonical mismatch, malicious domain suffixes, malformed URLs, and absent
Origin/Referer.

## Benchmark

Run `npm run benchmark:auth-origin` for 100,000 real origin comparisons. The
benchmark fails if any legitimate comparison is rejected and reports measured
throughput from the executing runner; no static performance result is claimed.

## Deployment scope correction

Web release evidence and the dedicated auth workflow are classified as web-only
changes. This prevents unrelated full-swarm secret validation from blocking an
auth UI/middleware rollout. The dedicated auth restore workflow now watches the
middleware and exact-origin helper.
