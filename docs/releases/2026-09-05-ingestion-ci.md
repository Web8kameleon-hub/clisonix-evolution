# Deterministic ingestion lint

## Issue

The scheduled `ingestion-ci` workflow installed an unpinned Ruff release. The same workflow failed concurrently in `clisonix.com` and `Kloud`, making the result depend on external tool releases instead of repository state.

## Documentation

The workflow now records the exact Ruff version and emits GitHub-native annotations. Pull requests that change the ingestion workflow or Airflow DAGs run the same lint gate before merge.

## Tests

- `ingestion-ci` passed on commit `01ca63eab8b072091aba1332d4b551a48bc5ca61`.
- Repo Integrity Guard passed on the same commit.
- News Branch CI now scopes Markdown sanity checks to newsroom documentation and passed on commit `8772f21bfebd9f66b708cb16aa567cdf755ad37b`.
- The equivalent `Kloud` ingestion workflow passed on commit `aea541978f2f6e471f2027a239e16ba1fe1eb75a`.

## Edge cases

- Scheduled and manually dispatched runs retain their existing behavior.
- DAG-only pull requests now receive lint validation.
- The workflow remains independent of Airflow runtime dependencies because Ruff performs static checks only.
- No production service, deployment, network, authentication, billing, or DAG execution behavior changes.

## Benchmark

The lint scope remains `airflow/dags`; no additional runtime workload is introduced. Pinning avoids resolver variability and keeps the job deterministic.

## Rollback

Revert the two CI commits in this release branch or restore `.github/workflows/ingestion.yml` from `be8c445f1678110046ca046309e954a2a8aff962`. No runtime rollback or service restart is required.
