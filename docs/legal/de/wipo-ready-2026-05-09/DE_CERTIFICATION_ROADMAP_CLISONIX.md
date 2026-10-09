# Germany Certification and Compliance Roadmap

Document type: Certification planning pack for Germany and EU market readiness
Date: 2026-05-09

## Legal Note
This is an engineering and governance preparation roadmap, not legal certification advice.

## 1. Recommended Certification Tracks

### Track A (Immediate, broad trust baseline)
1. ISO/IEC 27001 (ISMS)
2. ISO/IEC 27701 (privacy extension) optional but recommended
3. VAPT + secure SDLC evidence package

### Track B (AI governance)
1. ISO/IEC 42001 (AI management system)
2. EU AI Act readiness dossier (risk classification, human oversight, logging, post-market monitoring)

### Track C (German cloud/public-sector credibility)
1. BSI C5 attestation preparation (if cloud/SaaS target includes DE enterprise or public-sector buyers)

### Track D (if healthcare workflow is intended)
1. Medical device pre-assessment under MDR + IEC 62304 + ISO 14971 + ISO 13485 path
2. Clinical safety and performance documentation as required by device class

## 2. What Your Current Stack Already Supports

1. Runtime security profiles and policy actions:
- sdist/clx-ai/clx/security/monitor.py line 15
- sdist/clx-ai/clx/security/monitor.py line 162

2. Traceable processing pipeline with security gates:
- sdist/clx-ai/clx/core.py line 61
- sdist/clx-ai/clx/core.py line 108

3. Metrics and event logging in CLX.I:
- clx_i_service.py line 58
- clx_i_service.py line 68
- clx_i_service.py line 153
- clx_i_service.py line 170

4. No-fake-data and atomic persistence controls:
- sdist/clx-ai/examples/ecosystem_ops_10min.py line 8
- sdist/clx-ai/examples/ecosystem_ops_10min.py line 68

## 3. Certification Deliverables to Prepare

### ISMS (ISO 27001)
1. Information security policy set.
2. Asset inventory and data flow map.
3. Risk register and treatment plan.
4. Access control, key management, incident response SOPs.
5. Logging, monitoring, backup/restore evidence.
6. Internal audit reports + management review minutes.

### AI Governance (ISO 42001 / EU AI Act readiness)
1. AI system inventory and intended-use statements.
2. Risk management records per model/service.
3. Data governance and provenance records.
4. Performance monitoring, drift detection, and override procedures.
5. Transparency notices and human oversight procedures.

### BSI C5 readiness
1. Control mapping from your existing controls to C5 domains.
2. Evidence collection matrix (technical + organizational).
3. Gap closure plan with owners and deadlines.

## 4. 90-Day Execution Plan

### Days 1-30
1. Define scope boundary (which services and environments).
2. Build unified control matrix (27001 + 42001 + C5 overlap).
3. Start evidence repository and naming convention.

### Days 31-60
1. Complete risk assessment and policy baseline.
2. Run tabletop incident exercise and access review.
3. Close high-risk technical gaps (auth, logs, backup, monitoring).

### Days 61-90
1. Internal pre-audit and corrective actions.
2. Select certification body / audit partner.
3. Freeze evidence package and schedule stage-1 audit.

## 5. Germany-Specific Practical Next Steps
1. Engage a DE-based Patentanwalt for patent filing finalization.
2. Engage a DE/EU certification body for ISO 27001 scoping call.
3. Run a legal screening for EU AI Act role (provider/deployer/importer).
4. If health claims are planned, run MDR classification with notified-body strategy early.

## 6. Priority Order (Recommended)
1. Patent filing draft finalization (to secure priority date).
2. ISO 27001 groundwork (improves trust and procurement readiness).
3. ISO 42001 + AI Act documentation layer.
4. BSI C5 mapping for enterprise/public-sector opportunities.

This roadmap follows secure SDLC practices and includes VAPT checkpoints
before release.

The package is distributed as an sdist and validated in CI for reproducible
builds.

Legal review with a Patentanwalt is required before filing and publication,
based on counsel advice.

{
  "cSpell.words": [
    "VAPT",
    "SDLC",
    "sdist",
    "Patentanwalt"
  ]
}
