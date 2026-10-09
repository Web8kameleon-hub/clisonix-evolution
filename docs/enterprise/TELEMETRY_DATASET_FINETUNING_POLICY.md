# Unified Telemetry, Dataset Curation, Fine-Tuning Policy

## Unified Telemetry Schema
Every interaction event should include:
- `event_id`, `timestamp`, `product`, `tenant_id`
- `prompt`, `model_output`, `route_targets`, `latency_ms`
- `quality_labels` (optional), `feedback_score` (optional)
- `policy_decisions` and `guard_flags`

## Prompt/Outcome Data Paths
- Raw ingestion: Redis/Kafka stream -> durable storage
- Sanitization: remove secrets/PII before long-term storage
- Analytics table: aggregate for model quality and product KPIs

## Dataset Curation Pipeline
1. Ingest candidate records.
2. Deduplicate by semantic hash.
3. Safety and policy filter.
4. Quality scoring (correctness, relevance, tone).
5. Human review sample for high-impact domains.
6. Versioned dataset release (`dataset_vYYYYMMDD_n`).

## Fine-Tuning Policy
- Allowed only on approved dataset versions.
- Every fine-tune job needs:
  - objective
  - dataset version
  - evaluation baseline
  - rollback model reference
- Promotion to production requires:
  - no regression on safety
  - >= target gain on task quality metrics
  - sign-off from model owner + governance owner

## Data Retention
- Raw prompt/outcome: 30–90 days (tenant-configurable)
- Aggregated metrics: 12 months
- Audit evidence: contract-driven retention

## Prohibited Data
- Plain credentials, API secrets, payment card data
- Clinical identifiers without explicit legal basis
- Customer confidential docs outside approved scope
