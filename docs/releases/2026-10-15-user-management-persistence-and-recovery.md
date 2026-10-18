# 2026-10-15 — User-management persistence and password recovery

## Issue

`services/user-management/user_core.py` stored every account, profile,
session, and usage record in plain in-memory Python dicts
(`self._accounts = {}`, etc. — the code literally commented "in
production: database"). Any container restart or redeploy wiped all
registered users. There was also no password-recovery path anywhere in
the codebase: a user who forgot their password had no way to regain
access.

## Documentation

- Added `services/user-management/db.py`: a stdlib `sqlite3` connection
  manager (WAL mode, foreign keys on) with the real schema (`accounts`,
  `profiles`, `sessions`, `usage`, `password_reset_tokens`). File path is
  controlled by `CLISONIX_USER_DB` (defaults to `./data/users.db`).
- Added `services/user-management/email_sender.py`: real `smtplib`-based
  mail sending. Raises `EmailNotConfigured` when `SMTP_HOST` is unset and
  `EmailSendFailed` on real SMTP errors — no fake "email sent" success
  state is ever returned.
- Rewrote `services/user-management/user_core.py` to read/write through
  `db.py` instead of in-memory dicts, preserving the existing public API
  and the existing `{salt}${sha256}` password hash format. Added
  `request_password_reset()`, `reset_password()`, and `change_password()`,
  plus a `RecoveryEmailUnavailable` exception that is raised (not
  swallowed) when SMTP isn't configured, per `NO_FAKE_DATA_POLICY.md`.
- Added three endpoints to `services/user-management/main.py`:
  `/api/users/password/forgot`, `/api/users/password/reset`,
  `/api/users/password/change`.
- Added Next.js proxy routes
  (`apps/web/app/api/auth/password/{forgot,reset}/route.ts`) using the
  existing `fetchFromCandidates({ group: "auth" })` upstream pattern, plus
  two new pages (`/forgot-password`, `/reset-password`) and a "Forgot your
  password?" link on `/sign-in`.
- Fixed a related gap found while wiring this: `AUTH_INTERNAL_URL` for the
  `web` service in `compose-hosting.yml` was never set, so the auth proxy
  helper had no upstream to call. Added
  `AUTH_INTERNAL_URL: http://user-management:8070` and a
  `depends_on: user-management (service_healthy)` entry. Added
  `CLISONIX_USER_DB`, `PUBLIC_WEB_URL`, `CLISONIX_BOOTSTRAP_ADMIN_*`, and
  `SMTP_*` environment variables plus a `./data/user-management:/app/data`
  volume to the `user-management` service block so the SQLite file
  persists across container restarts.

## Tests

- `python -m pytest services/user-management/tests/test_persistence_and_recovery.py -v`
  — 5/5 real tests pass (no mocks): data persists across a simulated
  restart, honest failure when SMTP is unconfigured, a full
  register→request→real-SMTP-email→extract-token→reset→login flow against
  a hand-rolled stdlib SMTP test server, anti-enumeration on the forgot
  endpoint, and change-password requiring the current password.
- Manually verified the same flow over real HTTP against a live `uvicorn`
  instance of the service plus a local SMTP listener on port 2525.
- `python scripts/guardrails/repo_integrity_guard.py` → PASS (service
  counts: `deploy_service_count` 198 → 199, reflecting the real current
  compose-hosting.yml service count).
- `python -c "import yaml; yaml.safe_load(open('compose-hosting.yml'))"` →
  YAML OK.
- `npx tsc --noEmit -p tsconfig.json` in `apps/web` → no new errors (the
  only reported errors are pre-existing in `middleware.ts`, unrelated to
  this change, confirmed present on `origin/main` before this commit).

## Edge cases

- Anti-enumeration: `/api/users/password/forgot` returns the same generic
  "if this email exists" response regardless of whether the account
  exists, so the endpoint cannot be used to probe registered emails.
- Honest failure instead of fake success: if `SMTP_HOST` is unset,
  `request_password_reset()` raises `RecoveryEmailUnavailable`, which
  `main.py` maps to a real HTTP 503 — never a fabricated "email sent".
- Reset tokens are single-use: `reset_password()` invalidates the token
  row after a successful reset, so a captured token cannot be replayed.
- `change_password()` requires the caller to supply the current password
  before accepting a new one, independent of the token-based reset flow.
- Quoted-printable email bodies (triggered by Albanian diacritics in the
  email text) soft-wrap the reset URL; the token is extracted by decoding
  the real MIME payload (`email.message_from_string(...).get_payload(decode=True)`)
  rather than naive line-scanning, verified against a real SMTP payload in
  tests.

## Benchmark

Not applicable — this is a persistence/correctness change (in-memory
dict → SQLite on local disk) for a low-traffic account-management
service, not a hot path with throughput targets.

## Rollback

Twelve-file change, all additive or backward-compatible at the API
level (`user_core.py`'s existing public methods keep the same
signatures). Reverting restores the pre-existing in-memory-only storage
and removes the three new password endpoints and web pages; any accounts
registered via SQLite during the time this was live would need to be
re-created after a rollback, since the in-memory implementation has no
knowledge of the SQLite file.
