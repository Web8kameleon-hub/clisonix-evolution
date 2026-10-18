# 2026-10-14 — Fix: missing `longo` service in compose-hosting.yml

## Issue

`Hetzner Swarm rolling deploy` has failed every run since 2026-09-03
with `no such service: longo` at the "Validate and build selected
service images" step. The failure was masked until today by a separate,
unrelated missing-production-secrets gate failing earlier in the same
script, so this specific breakage was never actually reached or
visible until that secrets issue was fixed.

## Documentation

Commit `ca341957d` ("migrate production stack to Longo") added `longo`
to `scripts/hetzner-swarm-deploy.sh`'s default `SERVICES_CSV` list, but
only defined the actual `longo` service in `docker-compose.75-services.yml`
-- a separate, different compose file from the one the Swarm deploy
script actually targets (`COMPOSE_FILE` defaults to `compose-hosting.yml`).
This left `compose-hosting.yml` permanently missing a service its own
deploy script expects to build and run.

This change ports the real `longo` service definition (a Java-based
key-value store built from `./java-longo/Dockerfile`) into
`compose-hosting.yml`, matching that file's existing conventions
(`./data/longo:/data` bind mount, implicit `clisonix-net` via the
default network, no host port exposure -- identical to the original
definition, which also never exposed a host port).

## Tests

- `python -c "import yaml; yaml.safe_load(open('compose-hosting.yml'))"`:
  parses cleanly, 199 services total (was 198), `longo` present with
  the exact expected fields (build context, environment, volumes,
  healthcheck, restart policy, resource limits).
- Confirmed `java-longo/Dockerfile` exists on disk at the referenced
  build context.
- Confirmed via live SSH inspection of the production server that no
  existing service currently references `LONGO_URL` or depends on
  `longo`'s prior absence, so this is purely additive.

## Edge cases

- `grep -n LONGO compose-hosting.yml` before this change returned zero
  matches, confirming no other service in this file was silently
  relying on `longo` being absent or defined under a different name.
- No host port is published, matching the original Longo definition in
  `docker-compose.75-services.yml` -- this service remains
  internal-network-only, so no new external attack surface is added.

## Benchmark

Not applicable -- this is a deployment-configuration correctness fix,
not a performance-sensitive code path.

## Rollback

Single-file, single-hunk addition to `compose-hosting.yml`. `git revert`
removes the `longo` service block cleanly; no other service in this
file currently references it, so reverting has no cascading effect.
