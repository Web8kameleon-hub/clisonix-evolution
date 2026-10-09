# Fork Patch Plan - Remove Perma-Diff at Module Level

This plan describes how to remove persistent drift noise by patching the upstream Cloudflare CDS Terraform module in a controlled fork.

## Goal

Make `terraform plan` converge cleanly (or near-cleanly) after apply, while preserving functional behavior.

## Why a Fork Is Needed

The recurring diffs are produced by resources defined inside the external module. Root module code cannot directly add lifecycle rules to nested resources.

## Implementation Steps

1. Fork source module repository

- Fork: `cloudflare/cf-product-infrastructure-templates`.
- Create branch: `cds-gcp-drift-hardening`.

1. Patch Cloud Run resources in fork

- Target files under `cds/terraform/gcp/modules/cloud_run`.
- Add `lifecycle.ignore_changes` for fields that are runtime-normalized by Cloud Run API.
- Start with the narrowest set:
  - `scaling`
  - optional metadata fields only if they keep reappearing and are proven safe.

1. Patch Cloud Scheduler resource in fork

- Target file under `cds/terraform/gcp/modules/cloud_scheduler`.
- Add narrow ignore for `http_target[0].oidc_token[0].audience` if perma-diff persists.

1. Keep IAM/network/security fields strict

- Do not ignore IAM bindings, VPC wiring, or queue/subscription identity fields.
- Keep these as hard drift signals.

1. Pin root module to fork ref

- Update `infra/terraform/cloudflare-cds-gcp/main.tf` module `source` to fork URL and pinned tag/commit.
- Example strategy: tag `v1.0.0-clx-driftfix1`.

1. Validate and rollout

- Run: `terraform init -upgrade`, `terraform validate`, `terraform plan`.
- Confirm no destructive changes.
- Apply once.
- Re-run plan and confirm drift reduction.

## Safety Gates

- Require PR review for every fork patch.
- Require manual apply approval.
- Require post-apply smoke checks (Cloud Run + Scheduler trigger).

## Rollback

- Keep previous upstream module ref documented.
- Roll back by restoring previous `module source` and re-running init+plan.

## Acceptance Criteria

- No destroy actions introduced by migration to fork.
- Known perma-diff reduced or eliminated.
- Services remain healthy after apply.
