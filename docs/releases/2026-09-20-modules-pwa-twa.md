# Clisonix Modules PWA/TWA Release Evidence

Date: 2026-09-20  
Release scope: `apps/web/app/modules`, web app manifest, service worker, Android TWA launch target.

## Delivered

- Reworked the modules shell for phone, tablet, standalone PWA, TWA, and desktop layouts.
- Added a mobile header and horizontally scrollable touch category navigation.
- Added an install action driven by the real `beforeinstallprompt` browser event.
- Made module actions permanently visible for touch and keyboard users.
- Removed the production-invalid `http://localhost:8030/chat` catalog entry.
- Changed the installed PWA identity and start URL to `/modules?source=pwa`.
- Changed the Android TWA launch URL to `/modules?source=twa`.
- Added a versioned offline modules shell and same-origin runtime asset caching.
- Authentication and API responses remain network-only and are never cached by the service worker.

## Acceptance checks

1. TypeScript build must accept the install prompt event contract and responsive JSX.
2. The module catalog must contain no `localhost` URL.
3. `manifest.json` must parse as JSON, use `display: standalone`, scope `/`, and start in `/modules`.
4. `sw.js` must exclude `/api/*` and sign-in/sign-up navigations from caching.
5. Android TWA must retain the verified `www.clisonix.com` origin and Digital Asset Links package `com.clisonix.app`.
6. Public health gate must remain green after deployment.

## Performance budget

- No new npm or Android dependency.
- No new blocking network request during initial render.
- PWA shell assets are cached once under `clisonix-shell-v2`.
- Mobile layout uses CSS breakpoints only; no layout-detection request or polling.
- Catalog removes one unreachable external card, reducing rendered DOM and eliminating a failed localhost navigation.

## Security and no-fake controls

- No placeholder runtime, synthetic provider, external LLM, or fabricated status was introduced.
- Internal authentication remains the only sign-in provider.
- Service worker ignores every API route and therefore cannot replay stale auth or health data.
- TWA trust continues to use the deployed Digital Asset Links certificate fingerprint.

## Rollback

Revert commits `064504eb489aa3b9eef9aa8680f781f00a80e3ad`, `8fc1f4f9575a68a6cf26de1ce4f54252093ff51c`, `c0c9b3e1102c367683a0ecf9554ca1187cc74cf4`, `7adc43b9256f174621bc690bb6b1d17397154ddb`, and `c35ee93b603cf2013d2d7735d778b8ca9cc0020e`. The service worker activation step will delete the v2 cache when a later cache version is deployed.
