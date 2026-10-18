# 2026-10-14 — Fix: Swarm stack rendering for build-only service images

## Issue

`Hetzner Swarm rolling deploy` has never succeeded (confirmed: all 100
most recent runs ended in "failure" or "skipped", never "success").
After earlier fixes today resolved missing production secrets and a
missing `longo` compose service, the deploy progressed further and hit
`Service 'web' has no deployable image` -- and the identical failure
would have hit every other core application service next (`api`,
`jona`, `ocean-core`, `ocean-core-multimodal`,
`kloud-upstream-runtime`, `kloud-bridge`, `curiosity`,
`user-management`), since none of them declare an explicit `image:` in
`compose-hosting.yml` — they are all build-only service definitions.

## Documentation

`scripts/render-swarm-stack.py` required every selected service to
already carry a resolved `image` field from `docker compose config
--format json`. Compose only populates that field automatically for
services that declare an explicit `image:` key; build-only services
have no such field in the config JSON, even though `docker compose
build` (which runs immediately before this script in
`scripts/hetzner-swarm-deploy.sh`) does tag them, using the convention
`<project-name>-<service-name>` — confirmed against the real
production server's own build output: `Image clisonixcom-web Built`,
`Image clisonixcom-api Built`, etc.

The fix reads the authoritative Compose project name directly from the
same resolved compose JSON's top-level `"name"` field (confirmed via
SSH to equal `clisonixcom` on the production server) and computes the
identical `<project>-<service>` tag for any selected service that has a
`build` key but no explicit `image`. Nothing is hardcoded: if the
deploy path or project name ever changes, this still resolves
correctly because it reads the real value Compose itself already
computed, rather than assuming a fixed string. Services with neither
`image` nor `build` still fail closed with the original error.

## Tests

- `python -m py_compile scripts/render-swarm-stack.py`: clean.
- Ran the real script against the actual resolved compose JSON pulled
  live from the production server (not a synthetic fixture) for all 10
  default Swarm services: every service resolved a correct image
  (`longo` kept its explicit `clisonix-longo:latest`; the other 9
  resolved to `clisonixcom-<service>`, matching already-built tags).

## Edge cases

- A synthetic service with neither `image` nor `build` still raises
  `Service '<name>' has no deployable image` — fail-closed behavior is
  preserved, this change only adds a legitimate second way to resolve
  a real image, not a bypass.
- A service missing `healthcheck` still raises `has no real
  healthcheck; refusing zero-downtime deployment`, confirming that
  check (untouched by this change) still runs before the image
  resolution logic.

## Benchmark

Not applicable — this is a deploy-script correctness fix with no
runtime performance implication.

## Rollback

Single-file, localized change to `scripts/render-swarm-stack.py`.
`git revert` restores the strict `image`-field-required check; combined
with today's earlier `longo` fixes, that would again fail on `web` (and
every other build-only service) the next time Swarm deploy runs.
