# Model Governance Workflow

## Scope

Ky dokument përkufizon skeletin fillestar për `model governance` në Clisonix.

Objektivat:

- `risk-based` lifecycle control
- `human approval` për prodhim
- `specialized reviewer` për domain-e sensitive
- `licensed approver` për workload-e health / clinical / biosignal në prodhim

## Lifecycle

Rrjedha e aprovuar:

`draft -> risk_review -> compliance_review -> approved -> production -> deprecated`

## Human Approval Policy

### Human approval kërkohet kur

- modeli promovohet në `production`
- risku është `medium`, `high`, ose `critical`
- intended use ose `domain_tags` përfshijnë `health`, `telehealth`, `medical`, `clinical`, `biosignal`, `eeg`, `patient-facing`
- mungon evidenca e nevojshme (`explainability`, `bias`, `validation`, `adversarial`)

### Specialized reviewer kërkohet kur

- modeli prek vendime ose outputs në domain sensitive
- sistemi operon në `healthtech`, `biosignals`, `clinical`, ose `patient-facing` use-cases

### Licensed approver kërkohet kur

- workload-i sensitive kalon në `production`
- promotion shkon drejt përdorimit që mund të ndikojë pacient, biosignal interpretation, ose workflow me peshë compliance

## Reviewer Matrix

| Transition | Required reviewers |
| --- | --- |
| `draft -> risk_review` | `risk_owner` |
| `risk_review -> compliance_review` | `compliance_owner` + specialist sipas riskut |
| `approved -> production` | `risk_owner` + `compliance_owner` + specialist/licensed sipas policy |

## Evidence Bundle (Skeleton)

Çdo model duhet të ketë gradualisht:

- `explainability_report`
- `bias_assessment_report`
- `validation_report`
- `adversarial_test_report`
- `approval_notes`
- `attached_artifacts`

## Implementation Notes

- Policy qendrore: [model_governance.py](model_governance.py)
- `apps/api` bridge: [apps/api/services/model_governance_bridge.py](apps/api/services/model_governance_bridge.py)
- Registry aktual: [ai_model_versioning.py](ai_model_versioning.py)

## Next Phase

Faza tjetër duhet të bëjë:

1. persistencë për approvals dhe evidence
2. audit events immutable për çdo transition
3. API endpoints për submit/review/approve/promote
4. lidhje me `AuditLog` database table dhe provenance layer
