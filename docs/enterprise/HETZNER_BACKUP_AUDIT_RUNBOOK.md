# Hetzner Backup + Audit Runbook (No-Downtime)

## Objectives
- Daily backup of critical state
- Fast restore path
- Deployment audit trail

## Backup Targets
- `/opt/clisonix-cloud` (configuration + compose)
- database and volume snapshots
- immutable release manifests

## Schedule
- Incremental: every 6h
- Full snapshot: daily 02:00 UTC
- Retention: 14 daily + 8 weekly

## Pre-backup checks
- Verify core service health endpoints
- Verify disk free space
- Record release version + commit hash

## Post-backup verification
- Validate archive checksum
- Run sample restore on isolated path

## Audit Trail Fields
- operator
- timestamp
- release version
- commit SHA
- checksum
- result

## No-downtime rule
- Never stop all core services together
- Prefer rolling restarts and canary validation
