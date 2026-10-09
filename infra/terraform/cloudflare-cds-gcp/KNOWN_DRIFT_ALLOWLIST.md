# Terraform Known Drift Allowlist (CDS GCP)

This allowlist documents Terraform plan diffs that are currently accepted as safe for this stack.

## Allowed Drift Patterns

1. Cloud Run v2 scaling null-normalization

- Pattern: `min_instance_count = 0 -> null`
- Why: Cloud Run v2 / provider normalization between explicit default and omitted default.
- Risk: Low.

1. Cloud Scheduler OIDC audience null-normalization

- Pattern: `oidc_token.audience = "..." -> null`
- Why: Scheduler/Cloud Run integration now treats default audience as implicit.
- Risk: Low, but scheduler trigger should be smoke-tested after apply.

## Not Allowlisted

Any plan change outside the patterns above is not automatically safe and requires manual review.

Examples of manual-review changes:

- Any destroy action.
- New resources not expected by release scope.
- IAM policy/member changes not part of approved change request.
- Network/firewall/VPC topology changes.

## Operational Rule

If Terraform plan includes changes and they are not fully covered by this allowlist, treat as NO-GO until reviewed.
