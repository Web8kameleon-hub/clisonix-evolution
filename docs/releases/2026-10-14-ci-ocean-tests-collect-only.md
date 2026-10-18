# 2026-10-14 — CI fix: restore collect-only for Ocean runtime tests

## Issue

`Zero Regression Gate` has failed on every push to `main` since
2026-09-26 with `Failed: Ocean Core not reachable at
http://localhost:8030`. The `Critical Ocean runtime integration tests`
step executed the real multilingual/warm-reaction pytest suites against
`localhost:8030` and related service ports, but no step in the job
starts those services, so every run failed with a connection-refused
error before any of today's unrelated fixes (guard, automation tooling,
lockfile resync) were even pushed.

## Documentation

Git history shows this is a deliberate, previously-tried-and-reverted
design decision, not a new regression:

1. `d7c5bb066` added a real `docker compose up --wait` startup step for
   `translation-node`/`ocean-core`/`api`/`asi`/`openmind`/`excel`/`web`
   ahead of the test run.
2. Eleven minutes later, `54243f2e5` removed that step entirely and
   switched the test invocation to `--collect-only`, stating: "Hosted
   CI cannot truthfully build the Hetzner-only CLX runtime. The same
   suites execute against the real shadow Swarm in
   `scripts/hetzner-swarm-deploy.sh` before deployment can pass."
3. A later, unrelated revert (`e38b9d98c`, "restore ci-green.yml before
   autodeploy experiment") reverted `--collect-only` back to a real
   `-q --maxfail=1` run without restoring the docker-compose startup
   step, silently breaking the gate from that point on.

This change restores the documented, deliberate hosted-CI behavior:
`--collect-only` verifies both suites still import and parametrize
correctly (a real collection error still fails the gate), instead of
pretending to exercise a live multi-service stack that was already
proven infeasible to build truthfully on a GitHub-hosted runner. Real
live-service exercise of these same suites remains enforced by the
Hetzner shadow Swarm gate in `scripts/hetzner-swarm-deploy.sh` before
deployment, per the original design.

## Tests

- `python -m pytest ocean-core/tests/test_ocean_core_multilingual.py
  ocean-core/tests/test_ocean_warm_reaction.py --collect-only -q`
  locally: 65 tests collected, 0 errors, no live service required.
- Confirmed via `git log -S` that no other workflow step currently
  starts the Ocean stack before this test step, so `--collect-only` is
  the only truthful option for the hosted runner today.

## Edge cases

- A genuine Python import/collection error (e.g. a broken fixture or
  syntax error) still fails this step under `--collect-only`, so the
  gate is not a no-op — it still fails closed on structurally broken
  test files, per `NO_FAKE_DATA_POLICY.md`'s "fail closed, never
  silently skip" requirement enforced by the preceding "Reject skipped
  critical runtime tests" step in the same job.
- This does not weaken production verification: the real, live-service
  execution of these exact suites still runs and still blocks
  deployment via the Hetzner shadow Swarm gate.

## Benchmark

Not applicable — this is a CI-step correctness fix, not a
performance-sensitive code path. The before/after signal is the CI
gate's pass/fail state itself.

## Rollback

Single-file change (`.github/workflows/ci-green.yml`), one hunk;
`git revert` restores the real (currently always-failing-on-hosted-CI)
invocation with no other side effects.
