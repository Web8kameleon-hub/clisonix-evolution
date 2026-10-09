# Model Governance DB + Audit Skeleton

## Qëllimi

Kjo fazë shton shtresën minimale të persistencës për `model governance`.

Nuk zëvendëson ende registry-n me file, por krijon bazën për:

- `DB mirror` të state-it të governance
- approvals të ruajtura
- event log për transition-et
- lidhje me `audit_logs`

## Tabelat e reja

Shtohen në [apps/api/database/models.py](apps/api/database/models.py):

- `ModelGovernanceRecord`
- `ModelGovernanceApproval`
- `ModelGovernanceEvent`

## Çfarë ruhet

### `ModelGovernanceRecord`

- `model_id`
- `model_version`
- `risk_level`
- `approval_stage`
- `deployment_target`
- `intended_use`
- `domain_tags`
- `requires_specialized_reviewer`
- `requires_licensed_approver`
- `evidence_bundle`
- `registry_snapshot`

### `ModelGovernanceApproval`

- kush aprovoi
- me çfarë roli
- nëse ishte `approved`, `rejected`, ose `needs_changes`
- `reviewer_license_id` kur nevojitet

### `ModelGovernanceEvent`

- action i lifecycle-it
- `from_stage`
- `to_stage`
- actor metadata
- `details`
- referencë opsionale te `AuditLog`

## Service Skeleton

Service-i i ri është [apps/api/services/model_governance_store.py](apps/api/services/model_governance_store.py).

Funksionet bazë:

- `upsert_governance_record()`
- `create_governance_audit_log()`
- `append_governance_event()`
- `add_governance_approval()`
- `persist_registration()`

## Enforcement Engine

Enforcement-i i fazës aktuale tani bllokon transition-et kur mungojnë:

- approvals të role-ve të kërkuara
- `reviewer_license_id` për `licensed_approver`
- evidence completeness sipas stage-it target

Në skeletin aktual pragjet janë:

- `compliance_review` -> minimum `0.25`
- `approved` -> minimum `0.50`
- `production` -> minimum `1.00`

Kontrolli ekzekutohet nga policy layer te [model_governance.py](model_governance.py) dhe përdoret nga [ai_model_versioning.py](ai_model_versioning.py).

Gjithashtu u shtua regjistrimi i approvals në registry përmes `add_model_approval()`.

## Status i fazës aktuale

Faza e verifikimit të reviewer-it është implementuar:

- approval endpoint-et lidhen me user-in e autentikuar
- `reviewer_id` duhet të përputhet me identitetin e user-it aktiv
- reviewer profile menaxhohet përmes endpoint-eve të dedikuara
- approvals pa profil/rol/licencë valide refuzohen

## Hapi tjetër

Faza pasuese duhet të bëjë:

1. immutable workflow checks para promotion në `production`
2. role-based authorization më granular për admin/compliance operations
3. lidhje me UI/admin workflow
4. test suite për path-et e auth + governance enforcement
