# KLOUd Bridge Production Readiness Checklist

**Service:** `services/kloud_bridge`  
**Date:** 2026-04-04  
**Intent:** turn the bridge from a strong prototype into a production-grade contract boundary for cloud, fabric, and future edge hardware.

---

## 1. API Versioning

- [x] Add primary aliases under ` /api/v1/... `
- [x] Keep legacy unversioned routes for backward compatibility
- [ ] Decide deprecation policy for legacy paths
- [ ] Publish a stable versioning policy in external docs

## 2. Security and Access Control

- [x] Admin diagnostics guarded by `x-admin-token` or Bearer token
- [x] Optional node enforcement via `KLOUD_NODE_API_TOKEN`
- [x] Expose role model: `operator`, `node`, `admin`
- [ ] Rotate secrets through a centralized secret manager
- [ ] Add request signing or attestation model for hardware nodes
- [ ] Add audit logging for admin and node-auth failures

## 3. Runtime Safety

- [x] `live_only` posture exposed clearly
- [x] `mode = production-live`
- [x] `enforcement = hard`
- [ ] Add startup validation for required production environment variables
- [ ] Add rate limiting for sensitive endpoints

## 4. Observability and SLO/SLI

- [x] Health and status endpoints available
- [x] Hardware metrics now expose `registered_nodes`, `online_nodes`, `offline_nodes`, `network_health`, and `last_heartbeat_latency_ms`
- [ ] Export these metrics to Prometheus / Grafana dashboards
- [ ] Define SLOs for bridge availability and heartbeat freshness
- [ ] Add alert thresholds for upstream connectivity loss and node silence

## 5. Hardware / Edge Contract

- [x] Canonical firmware contract endpoint exists: `GET /hardware/contracts/firmware-v0.1`
- [x] Node registration and heartbeat endpoints exist
- [x] Local edge-node runner exists for contract verification
- [ ] Freeze the v0.1 schema and add JSON Schema validation docs
- [ ] Add public-key identity and future attestation model
- [ ] Add streaming telemetry or batched pulse ingestion path

## 6. Scaling and Reliability

- [ ] Add persistent store or cache for node state if multi-instance deployment is required
- [ ] Add readiness probes distinct from liveness probes
- [ ] Verify behavior behind reverse proxies and Cloudflare
- [ ] Validate timeouts and retries for upstream Kloud and Ocean paths
- [ ] Add load-test baseline for publish and sync endpoints

## 7. OpenAPI and Documentation

- [ ] Export a clean OpenAPI contract snapshot
- [ ] Add example payloads for every hardware and signal route
- [ ] Publish operator runbook for node onboarding and diagnostics
- [ ] Add error-code matrix for `401`, `404`, `502`, and `503` scenarios

---

## Recommended Next Move

The next highest-value step is:

1. freeze the `v0.1` hardware/firmware schema,
2. add operator-level auth/audit logging,
3. export the OpenAPI contract,
4. connect status metrics to the observability stack.
