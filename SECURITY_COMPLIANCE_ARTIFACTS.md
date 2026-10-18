# Clisonix Cloud Security & Compliance Artifacts

Ky dokument liston të gjitha raportet, evidencat dhe dokumentet e nevojshme për auditim, certifikim dhe përputhshmëri ligjore të sistemit të sigurisë Clisonix Cloud.

## 1. Raporte Operacionale & Audit
- **ndb_transition_runbook.md**: Runbook i plotë për tranzicionin e sigurisë (faza, rollback, observability, audit).
- **ndb_shadow_baseline_report.py**: Gjeneron baseline report për Shadow Mode.
- **ndb_advisory_mismatch_review.py**: Analizë mismatch për Advisory Mode.
- **ndb_hybrid_rollback_monitor.py**: Log dhe raport SLO/rollback për Hybrid Enforcement.
- **ndb_resonance_audit_package.py**: Gjeneron audit package për legal/compliance.
- **.github/workflows/clisonix_security_cicd.yml**: CI/CD pipeline për testim, audit dhe ruajtje evidencash.
- **test_security_middleware.py**: Test suite për validim automatik të të gjitha fazave.

## 2. Evidenca & Telemetri
- Të gjitha eventet ruhen në file/DB reale (pa të dhëna të shpikura).
- Log rollback, baseline, mismatch, audit package – të gjitha të ruajtura për inspektim.

## 3. Licenca & Certifikime
- **ISO 27001**: Politikat dhe evidencat e implementimit të kontrollit të aksesit, auditimit, incident response.
- **GDPR**: Evidenca për përpunimin, ruajtjen dhe auditimin e të dhënave personale, log i aksesit, mekanizma për të drejtat e subjekteve.
- **Other**: Dokumentacion për përputhshmëri me kërkesat e industrisë (PCI DSS, HIPAA, etj. sipas rastit).

## 4. Politika & Prova
- Politika e no-fake-data (NO_FAKE_DATA_POLICY.md)
- Politika e rollback dhe fallback
- Evidenca e testimit të fallback path çdo javë
- Raporte të engineering/security/product/legal review (weekly governance)

## 5. Udhëzime për Audituesit
- Të gjitha skriptet, raportet dhe log-et janë të versionuara dhe të ruajtura në repo.
- Çdo fazë ka evidencë reale të ekzekutimit dhe rollback.
- Audit package mund të gjenerohet automatikisht me ndb_resonance_audit_package.py.

---

Për çdo kërkesë të veçantë (raport, eksport, dokumentacion për ISO/GDPR), kontakto engineering ose përdor skriptet përkatëse për të gjeneruar evidencën në kohë reale.
