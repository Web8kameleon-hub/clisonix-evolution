# Release Pipeline, Immutable Deploy, Zero Config Drift

## Scope
Ky dokument standardizon release engineering për Clisonix pa downtime total.

## Principles
- Immutable artifacts: çdo release përdor image tags të ngrira dhe manifest të pandryshueshëm.
- No in-place mutation: prod nuk ndërtohet me source live.
- Drift detection: konfigurimet kritike hash-ohen periodikisht.
- Roll-forward/rollback by version: rollback bëhet me tag të mëparshëm, jo me patch manual.

## Required Inputs
- `immutable-manifest.json` nga workflow `release-immutable.yml`
- image tags për 3 produkte
- release version (`vYYYY.MM.DD-N`)

## Deployment Flow (Hetzner)
1. Fetch immutable manifest.
2. Pull tagged images.
3. Start parallel canary instance për shërbimin target.
4. Health gate (`/health`, `/status`, integration checks).
5. Shift traffic gradualisht (10% -> 50% -> 100%).
6. Stop old revision vetëm pasi gates kalojnë.

## Zero Drift Controls
- Baseline hash files:
  - `docker-compose.yml`
  - `docker-compose.75-services.yml`
  - `ocean-core/service_registry.py`
  - `ocean-core/bridge_engine.py`
  - `ocean-core/signal_schema.py`
- Drift monitor: workflow `drift-detection.yml` + server-side cron hash compare.
- Drift incident = SEV-2 nëse prek production runtime config.

## Runtime Change Policy
- Ndryshime live në server lejohen vetëm për emergency hotfix me incident ticket.
- Çdo hotfix duhet back-port në Git brenda 24h.

## Rollback Policy
- Trigger: error rate > SLO threshold ose critical dependency unhealthy > 3 min.
- Action: deploy previous immutable tag.
- RTO target: <= 10 min për 6 shërbimet kritike.

## Evidence / Audit
Ruaj për çdo deploy:
- release version
- git sha
- manifest hash
- start/end timestamps
- gate results
- rollback status
