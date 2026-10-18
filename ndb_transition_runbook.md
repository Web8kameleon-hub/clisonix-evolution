
<!-- Operational Runbook Generator for WWWMMM/NDB/Stigma/Nanogrid Transition -->
<!-- Gjeneron runbook real për çdo fazë, me hapa, kritere, rollback, observability dhe audit – vetëm mbi evidencë reale -->

# Clisonix Cloud Transition Runbook (WWWMMM/NDB/Stigma/Nanogrid)

## Faza 1: Shadow Mode
- Aktivizo NDB_SHADOW_ENABLED=1 për endpoint-et e zgjedhura.
- Monitoro eventet reale me ndb_shadow_sidecar.py.
- Analizo telemetry me ndb_shadow_observability.py dhe prodho baseline report.
- Kriter daljeje: 14 ditë telemetry pa gap, raport i miratuar nga engineering/security.
- Rollback: çaktivizo flag, asnjë impakt prodhimi.

## Faza 2: Advisory Mode
- Aktivizo NDB_ADVISORY_ENABLED=1.
- Middleware ndb_advisory_middleware.py logon rekomandimet dhe mismatch-et.
- Analizo mismatch-et me ndb_advisory_mismatch_review.py.
- Tuning vetëm mbi evidencë reale, çdo ndryshim me changelog dhe miratim.
- Rollback: çaktivizo flag, asnjë impakt prodhimi.

## Faza 3: Hybrid Enforcement
- Aktivizo NDB_HYBRID_ENFORCE_ENABLED=1, vendos rrugët dhe përqindjen e rollout-it.
- Middleware ndb_hybrid_enforcement.py enforce-on canary routes, fallback garantuar.
- Monitoro SLO me ndb_hybrid_rollback_monitor.py (latency, 5xx).
- Rollback automatik nëse tejkalohen pragjet, log i detajuar.
- Incident postmortem për çdo rollback.

## Faza 4: Resonance-First Default
- Aktivizo NDB_RESONANCE_DEFAULT_ENABLED=1, vendos validated routes.
- Middleware ndb_resonance_default.py enforce-on primary, legacy si fallback.
- Gjenero audit package me ndb_resonance_audit_package.py për legal/compliance.
- Freeze interface contracts (openapi.json).
- Testo fallback path çdo javë.

## Observability & Audit
- Të gjitha eventet ruhen në file/DB reale, pa asnjë të dhënë të shpikur.
- Raportet dhe audit package prodhohen vetëm nga telemetry reale.
- Çdo fazë ka rollback të menjëhershëm me flag.

## Weekly Governance
- Engineering: review telemetry, thresholds, drift, incidents.
- Security: review anomaly classes, risk posture.
- Product: review user-impact, route coverage.
- Legal/compliance: kontrollo evidencën dhe audit completeness.

## Definition of Done
- Tranzicioni përfundon pa ndërprerje shërbimi.
- Modeli i ri është i matshëm dhe i auditueshëm.
- Fallback legacy është gjithmonë operacional dhe i testuar.
- Runbook i miratuar dhe i adoptuar nga të gjithë route owners.
"""

with open(RUNBOOK_FILE, "w", encoding="utf-8") as f:
    f.write(runbook)

print(f"Operational runbook generated: {RUNBOOK_FILE}")
