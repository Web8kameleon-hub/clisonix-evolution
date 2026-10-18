# Clisonix Release Policy

## Branch model

- `main` is the only long-lived branch and the production source of truth.
- Release candidates use short-lived `release/YYYY-MM-DD-topic` branches.
- A release branch starts from current `origin/main`, is merged by fast-forward or pull request, and is deleted after successful production verification.
- Existing remote branches are inventoried before removal. Unmerged work is never deleted automatically.

## Zero-regression gate

Every code or configuration change must include one file under `docs/releases/` with these sections:

1. `Issue` links the problem or records a stable local identifier.
2. `Documentation` describes behavior and operational configuration.
3. `Tests` lists reproducible commands and results.
4. `Edge cases` records boundary and failure behavior.
5. `Benchmark` records performance evidence or a justified `N/A`.
6. `Rollback` gives a concrete recovery path.

The release cannot deploy until syntax/type checks, focused regression tests, build, and applicable benchmarks pass. A known failing integration test must be documented and resolved or explicitly kept out of the release; it is never reported as green.

## Release flow

```text
origin/main -> release/* -> evidence gate -> CI -> main -> deploy -> health gate
```

Production deployment always checks out `main`. Failed CI or health checks stop promotion. After deployment, the release branch is deleted and the release note remains as the durable audit record.

## Branch cleanup

Run `python scripts/release/branch_inventory.py` to classify remote branches. The command is read-only and reports branches already merged into `origin/main` separately from branches that still contain unique commits. Delete only the merged list after reviewing the report.
