# Client Batch BYOC Runbook

## Objective

Enable Clisonix to prepare analysis, studies, and business documents for clients while executing batch workloads on client servers.

## Principle

- Compute location: client server
- Data location: client server
- Clisonix role: orchestration, job control, billing, and status UI

## What Clisonix Stores

- Encrypted key/token reference
- Runner enrollment metadata
- Job status metadata
- Usage counters for billing

## What Clisonix Does Not Store (Default)

- Raw files/documents
- Generated report content
- Source datasets

## User Journey

1. Client opens dashboard and sends command.
2. Command maps to a job profile (Excel/Word/PDF/PPT).
3. Job is queued in Clisonix control plane.
4. Client runner pulls and executes job locally.
5. Runner posts completion metadata and client-hosted result link.
6. Dashboard displays result to client.

## Minimal APIs

- `POST /api/v1/runner/enroll`
- `POST /api/v1/runner/heartbeat`
- `GET /api/v1/runner/jobs/next`
- `POST /api/v1/runner/jobs/{job_id}/start`
- `POST /api/v1/runner/jobs/{job_id}/complete`
- `POST /api/v1/runner/jobs/{job_id}/fail`

## Runner Deployment (Client)

- Docker image: `clisonix-runner`
- Network posture: outbound only
- Secrets: per-client token injected via environment
- Storage: local path or client object storage

## Security Controls

- KMS-encrypted secrets at rest
- Short-lived signed job claims
- Tenant-scoped API tokens
- Audit log for enroll, start, complete, fail

## Compliance Posture

- "Data never leaves client environment" mode available.
- Optional content retention must be explicit opt-in.
- Metadata-only mode enabled by default.

## Operational SLO (V1)

- Runner heartbeat interval: 30s
- Job pickup latency (p95): < 10s
- Job completion event delivery (p95): < 2s after local finish

## Sales Message

"Clisonix prepares your reports and studies, but your data stays on your infrastructure. We orchestrate and bill usage without taking custody of your documents."
