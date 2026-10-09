# GPU Cluster Runbook (Sovereign Mesh)

Date: 2026-04-16
Status: Operational baseline
Rule: No fake metrics, no synthetic success claims, evidence required for every gate.

## 1. Scope

This runbook defines real operational controls for GPU clusters that serve sovereign LLM and edge-coordination workloads.

In scope:

- Capacity classes and admission controls
- Scheduling and isolation policies
- Health and incident gates
- Evidence collection for GO/NO-GO

Out of scope:

- Vendor marketing benchmarks
- Fabricated throughput or latency claims

## 2. Capacity Classes

- Class A (Critical Inference): latency-sensitive control-plane and safety workflows
- Class B (Interactive Inference): user-facing LLM responses
- Class C (Batch/Training-lite): asynchronous indexing, embedding, and background jobs

Policy:

- Class A has highest priority and preemption rights over B/C.
- Class C must be throttled first under pressure.

## 3. Scheduling Policy

- Use queue-based admission with per-class quotas.
- Enforce hard limits per tenant and per model.
- Reject over-quota requests with explicit error code and retry budget.

Required scheduler outputs (real-time):

- Pending queue depth by class
- GPU utilization by node
- Admission reject count
- Preemption count

## 4. Isolation and Security Controls

- Tenant isolation: namespace-level separation + service account boundaries
- Model artifact integrity: signed artifact requirement before activation
- Secret handling: keys from vault only, never plain-text in runtime config
- Audit trail: immutable event logs for deployment, routing, and policy changes

## 5. Health Gates

Hard NO-GO conditions:

- No attestation evidence for active node
- No signed artifact provenance for active model
- Repeated scheduler policy bypass events

GO conditions:

- All active nodes healthy
- Queue growth within defined threshold windows
- Error budget not exhausted

## 6. Incident Response Tiers

- Tier 1 (Degradation): latency spike or queue growth, no data integrity issue
- Tier 2 (Integrity Risk): signature/provenance mismatch, immediate quarantine
- Tier 3 (Control Plane Failure): routing instability or policy engine failure

Actions:

- Tier 1: reduce Class C, rebalance routes, preserve Class A
- Tier 2: isolate affected model/node, block deployment path
- Tier 3: activate failover cluster and read-only policy mode

## 7. Evidence Pack (Mandatory)

Before GO decision, collect:

- Scheduler snapshot (queue depth + utilization)
- Error and reject counters (time-bounded)
- Node health report with timestamps
- Deployment provenance report (signatures)

No evidence pack means NO-GO.

## 8. Commands (Operator Template)

Use your production CLI/observability stack; record exact commands used in runbook logs.

Minimum required record per command:

- UTC timestamp
- Operator ID
- Command executed
- Output artifact path

## 9. Definition of Done

Runbook is effective when:

- Operators can execute incident response without guesswork
- GO/NO-GO can be decided from evidence pack only
- No step depends on unverifiable or fabricated data
