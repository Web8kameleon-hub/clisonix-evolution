# 2026-10-14 — Fix: canonical services list missing `longo`

## Issue

`Hetzner Swarm rolling deploy` failed its next gate immediately after
`beac9f85c` fixed the missing `longo` service: `repo_integrity_guard.py`
reported `CANONICAL_SERVICE_LIST_MISMATCH` because
`scripts/guardrails/compose-hosting.services.txt` -- a separately
maintained canonical list the guard cross-checks against
`compose-hosting.yml` -- still did not list `longo`.

## Documentation

`scripts/guardrails/compose-hosting.services.txt` is read by
`repo_integrity_guard.py` (`read_service_list`) and compared against
the actual `services:` keys parsed from `compose-hosting.yml`. Any
service present in one but not the other fails the gate. Added `longo`
in alphabetical order (between `loki` and `marketplace`, matching the
file's existing sorted, one-service-per-line convention).

## Tests

- `python scripts/guardrails/repo_integrity_guard.py`: now PASSes
  (previously failed with `CANONICAL_SERVICE_LIST_MISMATCH`).
- `python scripts/guardrails/no_fake_data_policy_gate.py`: PASS.
- `bash scripts/guardrails/no_fake_fallback_gate.sh`: PASS.

## Edge cases

- The guard's `read_service_list` sorts and deduplicates the file's
  contents before comparison, so exact on-disk ordering doesn't affect
  correctness -- the alphabetical placement here is for human
  readability/convention only, not a functional requirement.

## Benchmark

Not applicable -- single-line addition to a plain-text list file.

## Rollback

Single-line addition; `git revert` removes it cleanly. Must be
reverted together with `beac9f85c` (the compose-hosting.yml `longo`
service addition) to keep both files aligned, or the guard will fail
again in the opposite direction.
