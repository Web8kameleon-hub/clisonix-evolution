# Clisonix Governance Packages Index

This index organizes the complete package set for GEN6-GEN9 governance and laboratory protocol operations.

## Package set

1. [Core Governance Package](CORE_GOVERNANCE_PACKAGE.md)
2. [Laboratory Protocol Package](LABORATORY_PROTOCOL_PACKAGE.md)
3. [Audit and Compliance Package](AUDIT_COMPLIANCE_PACKAGE.md)
4. [Academic Publication Package](ACADEMIC_PUBLICATION_PACKAGE.md)
5. [Visual Communication Package](VISUAL_COMMUNICATION_PACKAGE.md)
6. [Training and Onboarding Package](TRAINING_ONBOARDING_PACKAGE.md)
7. [Data Integrity Package](DATA_INTEGRITY_PACKAGE.md)
8. [Biomarker Validation Package](BIOMARKER_VALIDATION_PACKAGE.md)
9. [Comparative Outcomes Package](COMPARATIVE_OUTCOMES_PACKAGE.md)
10. [Publication Governance Package](PUBLICATION_GOVERNANCE_PACKAGE.md)

## Mandatory cross-package rules

- Publication gates are mandatory and enforced via GEN6-GEN9 and QC layer checks.
- Image assets must be dynamic per article/version (real or generated), not fixed global placeholders.
- Every package must include version, owner, review date, and change log.

## Dynamic image policy (applies to all packages)

Allowed image sources:

1. Real images from verified sources with citation/credit.
2. Generated images for process diagrams, architecture maps, and educational visuals.
3. Dynamic seeded fallback images only when no preferred source is available.

Required metadata for each image:

- `image_id`
- `source_type` (`real` or `generated`)
- `source_url`
- `license_or_usage`
- `generated_prompt` (if generated)
- `version`
- `updated_at`
