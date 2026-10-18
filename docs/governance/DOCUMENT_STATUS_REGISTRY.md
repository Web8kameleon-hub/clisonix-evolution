# Document Status Registry

Track critical documents and their ownership/lifecycle.

| Document                                               | Owner             | Status | Last Reviewed | Review Due | Source of Truth | Notes                       |
| ------------------------------------------------------ | ----------------- | ------ | ------------- | ---------- | --------------- | --------------------------- |
| README.md                                              | platform-team     | active | 2026-05-23    | 2026-06-22 | true            | Entry point                 |
| docs/architecture/ARCHITECTURE_RUNTIME_WIRING_INDEX.md | architecture-team | active | 2026-05-23    | 2026-07-07 | true            | Runtime wiring baseline     |
| SECURITY.md                                            | security-team     | active | 2026-05-23    | 2026-06-22 | true            | Security policy             |
| docs/DEPLOYMENT.md                                     | devops-team       | active | 2026-05-23    | 2026-06-22 | true            | Deployment baseline         |
| API-COMPLETE-REFERENCE.md                              | api-team          | active | 2026-05-23    | 2026-07-07 | true            | API reference               |
| CONTRIBUTING.md                                        | platform-team     | active | 2026-05-23    | 2026-07-22 | true            | Contribution policy         |
| CODE_OF_CONDUCT.md                                     | platform-team     | active | 2026-05-23    | 2026-08-21 | true            | Community behavior baseline |
| CHANGELOG.md                                           | release-team      | active | 2026-05-23    | 2026-06-22 | true            | Release history             |
| SUPPORT.md                                             | support-team      | active | 2026-05-23    | 2026-07-22 | true            | Support entry points        |
| SECURITY_CONTACT.md                                    | security-team     | active | 2026-05-23    | 2026-06-22 | true            | Private disclosure route    |
| RELEASE_POLICY.md                                      | release-team      | active | 2026-05-23    | 2026-06-22 | true            | Release/rollback gates      |
| docs/operations/INCIDENT_RESPONSE_RUNBOOK.md           | devops-team       | active | 2026-05-23    | 2026-06-22 | true            | Incident handling standard  |
| docs/operations/ONCALL_ROTATION_GUIDE.md               | devops-team       | active | 2026-05-23    | 2026-06-22 | true            | On-call handoff baseline    |
| docs/validation/DOCS_RUNTIME_VALIDATION.md             | docs-team         | active | 2026-05-23    | 2026-06-22 | true            | Drift control policy        |
| scripts/validate_docs_paths.ps1                        | docs-team         | active | 2026-05-23    | 2026-06-22 | true            | No-deps docs link check     |
| docs/eeg/EEG_SPORT_VALIDATION_PROTOCOL.md              | eeg-team          | active | 2026-05-23    | 2026-07-22 | true            | Evidence protocol           |
| docs/eeg/EEG_PUBLIC_CLAIMS_BOUNDARIES.md               | eeg-team          | active | 2026-05-23    | 2026-07-22 | true            | Claims boundaries           |
| DOCS_INDEX.md                                          | docs-team         | active | 2026-05-23    | 2026-06-22 | false           | Navigation index            |
| DOCUMENTATION_INDEX.md                                 | docs-team         | draft  | 2026-05-23    | 2026-06-07 | false           | Needs contradiction cleanup |

## Maintenance Rules

- Update this file when creating or deprecating critical docs.
- Keep status and review dates current.
- Resolve any row where Source of Truth is unclear.
