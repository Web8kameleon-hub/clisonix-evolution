# Production revenue surface — 2026-09-21

## Scope

This release moves the Clisonix customer surface away from beta/demo presentation and toward a fail-closed production funnel.

## User-visible changes

- Replaced simulated workspace accounts, projects, approvals, progress states, recommendations, and plan states.
- Workspace now renders only service-discovery observations, backend-created report jobs, and actual Ocean responses.
- Added honest empty and unavailable states.
- Removed browser-facing localhost fallbacks and the localhost-only specialized-chat catalog route.
- Removed unverified homepage availability and uptime claims.
- Rebuilt pricing around one configured Stripe price retrieved at request time.
- Pricing is withheld when Stripe cannot confirm an active recurring price.

## Billing integrity

- Checkout accepts only the configured Stripe price.
- Both public Stripe webhook paths now use one canonical handler.
- Webhook delivery fails with a retryable server error when internal subscription/entitlement synchronization fails.
- No payment event is acknowledged as successfully processed when entitlement persistence is unavailable.

## Data provenance

| Surface | Runtime source | Failure behavior |
| --- | --- | --- |
| Service availability | service-discovery plus health probes | unavailable/unverified |
| Report activity | reports and command APIs | empty/error |
| Ocean answers | /api/ocean | explicit unavailable message |
| Product price | Stripe Prices API | pricing unavailable |
| Subscription access | Stripe webhook plus internal billing API | webhook 500 for retry |

## Compatibility

- Internal authentication remains the only identity path.
- Redis configuration and runtime behavior are unchanged.
- Existing report job and Ocean API contracts are preserved.
- Kloud registry entries are not presented as online without health evidence.

## Verification

Automated repository CI, security scanning, build, and deployment gates are the release authority. This document records scope; it does not claim a passing build before those jobs complete.

## Performance and benchmark impact

No synthetic benchmark number is published. The UI adds the existing 30-second service-discovery polling and one Stripe price lookup on the pricing page. Production latency and availability must come from live telemetry after deployment.

## Rollback

Revert the commits listed by the release comparison if CI or production health gates fail. Do not substitute static status, pricing, project, or account data during rollback.

## Automated regression contract

Run `npm run test:production-surface` from `apps/web`. The contract rejects simulated workspace entities, static availability claims, static price catalogs, browser-facing localhost routes, duplicate webhook logic, and silent entitlement-sync failures. The benchmark form reports assertion runtime without inventing service-performance claims.

## Issue

The customer-facing application presented simulated accounts, projects, approvals, product states, availability, and pricing as if they were live. Billing webhooks could also acknowledge delivery after an internal entitlement sync failure.

## Documentation

This release evidence is the canonical summary for the production revenue surface. Runtime truth sources and fail-closed behavior are documented above.

## Tests

- `npm run test:production-surface`
- Web TypeScript check and production build in Zero Regression Gate
- GHCR web image build and health smoke test
- Stripe webhook signature and entitlement-sync behavior remain enforced by the route contract

## Edge cases

- Stripe secret or configured price missing: pricing returns 503 and the UI withholds the amount.
- Configured Stripe price inactive or non-recurring: pricing returns 503.
- Internal entitlement API unavailable: webhook returns 500 so Stripe retries.
- Service discovery unavailable: UI displays unavailable and does not infer health.
- Empty account/session activity: UI displays honest empty states.

## Benchmark

Run `npm run benchmark:production-surface`. It reports only local contract assertion time. No service latency, uptime, throughput, or revenue figure is inferred from this check.

### Recoverable dirty-server deployment

The Swarm workflow preserves tracked and untracked server-side changes in a named Git stash before fast-forwarding main. It does not reset or delete the dirty worktree. The stash name includes the triggering commit SHA for recovery.

### Web-only rollout

The final customer-surface rollout changes only `apps/web/**` and release evidence, so production uses the isolated web Swarm deployment path. It does not require or mutate the Ultra PostgreSQL stack.


## Ocean Curiosity production recovery

### Issue
- Live chat returned `empty_stream_payload` although Ollama health was green.
- Root cause: the default XLC gate consumed every SSE request and returned `no_route_match` for normal language prompts, preventing the configured model from running.

### Documentation
- XLC remains available for registered commands such as `START`, `RESET`, and `MODE`.
- Unmatched natural-language prompts now fall through to the configured Ocean model.

### Tests
- Added `ocean-core/tests/test_xlc_chat_gate.py` covering matched commands, ordinary questions, and router failure.

### Edge cases
- Empty command lists, empty prompts, router-construction errors, and route-evaluation errors safely fall through to model chat.
- A matched command still retains the existing XLC scanner/security/stream path.

### Benchmark
- Live isolation before fix: XLC path ended in about 7 seconds with `no_route_match`; the same request with XLC disabled produced real model tokens in about 11 seconds.
- Acceptance gate after deployment: public `/api/ocean/stream` must emit at least one usable model chunk and must not emit `empty_stream_payload`.


## Ocean isolated production rollout

- Added `scripts/hetzner/deploy_ocean_swarm.sh` so Ocean-only changes no longer invoke the unrelated full-stack database gate.
- Rollout uses Swarm start-first update and automatic rollback.
- The deploy gate now sends a normal prompt with default XLC settings and fails unless at least one real model text chunk is emitted.
- Redis, PostgreSQL, and unrelated services are not recreated or modified by this rollout.


## Public Curiosity relay recovery

- Production verification showed `api.clisonix.com/ocean` still targets a legacy Ocean instance whose default XLC gate consumes unmatched prompts.
- The public Curiosity relay now explicitly sets `xlc_enabled: false` for natural-language chat, allowing the already-running `llama3.1:8b` model to answer.
- XLC endpoints and explicit control-command flows remain available; only the user chat relay bypasses the legacy command gate.
- Added a production-surface assertion so this compatibility flag cannot disappear silently before proxy convergence.


## Verified public text model

- The legacy public Ocean inventory serves `llama3.1:8b`; `qwen2.5:7b` timed out and is not declared ready.
- Curiosity now defaults to the verified `llama3.1:8b` model unless production explicitly configures another model.
- LLaVA remains unavailable until its model artifact is installed and verified; it is not advertised by this recovery.
