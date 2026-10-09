# Kloud Bridge

Isolated microservice inside `clisonix-cloud` that connects platform workloads to the external `Kameleonlife/Kloud` sovereign fabric.

## Why isolated?

- `Kloud` remains the canonical sovereign runtime in its own repository.
- `kloud-bridge` only handles contracts, translation, and connectivity.
- This keeps infra IP and application IP separated.

## Default port

- `8889`

## Endpoints

Primary production aliases are available under **`/api/v1/...`** while the legacy unversioned paths remain active for compatibility.

- `GET /health` and `GET /api/v1/health`
- `GET /status` and `GET /api/v1/status`
- `GET /fabric/state` and `GET /api/v1/fabric/state`
- `GET /hardware/profile` and `GET /api/v1/hardware/profile`
- `GET /hardware/contracts/firmware-v0.1`
- `GET /hardware/nodes`
- `GET /hardware/nodes/{node_id}`
- `GET /admin/diagnostics` *(requires `x-admin-token` or Bearer token)*
- `POST /signals/publish`
- `POST /fabric/sync`
- `POST /v1/chat/completions` *(OpenAI-compatible remote LLM inference bridge)*
- `POST /api/generate` *(Ollama-compatible generate proxy for Ocean Core streaming)*
- `POST /hardware/nodes/register`
- `POST /hardware/nodes/heartbeat`

## Environment variables

- `PORT=8889`
- `KLOUD_UPSTREAM_URL=http://host.docker.internal:9080`
- `KLOUD_UPSTREAM_CANDIDATES=http://host.docker.internal:9080,http://127.0.0.1:9080`
- `KLOUD_BRIDGE_ADMIN_TOKEN=`
- `KLOUD_NODE_API_TOKEN=` *(optional hard-enforcement for hardware/node endpoints)*
- `KLOUD_SIGNAL_PATH=/submit`
- `KLOUD_STATUS_PATH=/status`
- `KLOUD_PEERS_PATH=/peers`
- `KLOUD_STATE_PATH=/state`
- `KLOUD_ISOLATED_MODE=true`
- `KLOUD_LLM_UPSTREAM_URL=http://clisonix-openmind:9999`
- `KLOUD_LLM_CHAT_PATH=/api/v1/chat`
- `KLOUD_LLM_TIMEOUT_SECONDS=30`
- `KLOUD_LLM_STREAM_CHUNK_CHARS=48`

## Hardware path

The bridge now includes a minimal **OceanCore + KLOUd hardware contract** for real edge prototypes:

- register a hardware node
- update heartbeat/telemetry state
- surface hardware readiness through `/status` and diagnostics
- optionally forward heartbeat envelopes into Ocean routing

This keeps the project aligned with the current concept:

- `Clisonix` = product + AI layer
- `Kloud` = sovereign runtime/fabric
- `kloud-bridge` = isolated hardware/cloud contract boundary

### Prototype runner

Local edge-node runners are available at:

- `scripts/hardware/oceancore_edge_node.py` *(Python reference runner)*
- `scripts/hardware/mesh_rollout.py` *(A/B/C/D multi-node rollout runner with sync + stress checks)*
- `scripts/hardware/rust_node_agent` *(Rust node agent v0.1)*
- sample profile: `scripts/hardware/profiles/oceancore_lab_01.json`
- controlled upstream stub: `scripts/hardware/kloud_upstream_stub.py`
- runbook: `docs/architecture/KLOUD_BRIDGE_PROOF_OF_LIFE_RUNBOOK.md`
- expanded runbook: `docs/architecture/KLOUD_MESH_ROLLOUT_ABCD.md`

Use either runner to register a node, emit heartbeats, and publish one proof-of-life signal into the bridge contract.

The bridge now keeps a **persistent node registry** on disk so registered nodes remain known entities across service restarts.

## Local run

```bash
uvicorn main:app --host 0.0.0.0 --port 8889
```

## Example publish

```bash
curl -X POST http://localhost:8889/signals/publish \
  -H "Content-Type: application/json" \
  -d '{"ops":["S"],"payload":{"signal":"alpha","source":"albi"}}'
```
