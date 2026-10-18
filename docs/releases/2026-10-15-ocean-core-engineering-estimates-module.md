# 2026-10-15 — Fix: ocean-core crash-loop, missing engineering_estimates module

## Issue

`Hetzner Swarm rolling deploy`'s `ocean-core` service crash-looped
(`task: non-zero exit (1)`) with:

```
ModuleNotFoundError: No module named 'engineering_estimates'
```

This surfaced only after today's earlier fixes (production secrets,
`longo` compose entry, Swarm build-only image-tag resolution) let the
deploy progress far enough to actually run the `ocean-core` container
end-to-end for the first time.

## Documentation

`git log -S "from engineering_estimates import"` identifies commit
`8f08d6ae9` (2026-10-12, "fix(ocean): clarify no-fake-data scope and
remove fabricated fallbacks") as the commit that added this import to
`ocean_core_full.py`. The actual `ocean-core/engineering_estimates.py`
module was never committed alongside it — it sat as an untracked file
on local disk since that date, so every ocean-core image built from
`main` since then has been missing it. `ocean-core/Dockerfile`'s COPY
list was also never updated to package it.

This change commits the module as-is and adds one line to
`ocean-core/Dockerfile`'s COPY list. `ocean-core/Dockerfile.full` was
checked (`grep -r "Dockerfile.full"` across every `*.yml` in the repo)
and is not referenced by any compose file, so it is intentionally left
unmodified.

## Tests

- `python -m py_compile ocean-core/engineering_estimates.py`: clean —
  the module only imports `ast`, `decimal`, `re` from the standard
  library, no further missing dependencies.
- Built the real `ocean-core/Dockerfile` locally with this fix and ran
  the resulting image:
  - `python3 -c "import engineering_estimates"` succeeds.
  - `python3 -c "import ocean_core_full"` (the module that was
    crash-looping) now completes without `ModuleNotFoundError`,
    successfully loading MegaLayerEngine, RealAnswerEngine,
    ServiceRegistry, Albanian Dictionary, Knowledge Layer, and Module
    Core Registry.
- `grep` confirms all 5 imported names (`ESTIMATE_POLICY`,
  `insufficient_estimate_response`, `is_engineering_estimate`,
  `needs_public_estimate_evidence`, `review_engineering_estimate`) are
  genuinely used elsewhere in the committed `ocean_core_full.py`,
  confirming this is a real dependency, not dead code being reinstated.

## Edge cases

- The module's own arithmetic-verification helper (`_arithmetic`)
  parses only short literal numeric expressions via `ast.parse(...,
  mode="eval")` with an explicit length cap and a restricted node
  whitelist (constants and +/-/* BinOps only) — it does not evaluate
  arbitrary Python, so no new code-execution surface is introduced by
  committing this file as-is.

## Benchmark

Not applicable — this restores a previously-intended, already-written
module to its already-committed call sites; no new performance-
sensitive logic is introduced.

## Rollback

Two-file change (`ocean-core/Dockerfile` COPY line,
`ocean-core/engineering_estimates.py` addition). Reverting restores the
`ModuleNotFoundError` crash-loop for the ocean-core service, so a
revert must be paired with also reverting (or patching around) the
original `8f08d6ae9` import if this is ever rolled back.
