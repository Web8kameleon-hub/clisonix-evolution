# Kloud Upstream Runtime

Production-grade sovereign upstream runtime for the `kloud-bridge` mesh.

## Purpose

This service is the **real upstream runtime**, not a stub and not a mock layer. It maintains:

- real node registry
- peer visibility
- coordinator state
- live submit intake
- persistent JSON-backed state for bootstrap deployments

## Core endpoints

- `GET /health`
- `GET /status`
- `GET /peers`
- `GET /state`
- `GET /nodes`
- `POST /nodes/register`
- `POST /nodes/heartbeat`
- `POST /submit`

## Suggested deployment target

Deploy this service on the `aiagi.io` machine (`hetzner-old`) as the primary sovereign runtime.

## Recommended environment

```env
PORT=9080
KLOUD_RUNTIME_NODE_ID=aiagi-node-01
KLOUD_RUNTIME_ROLE=coordinator
KLOUD_RUNTIME_REGION=eu-central
KLOUD_RUNTIME_PUBLIC_BASE_URL=https://aiagi.io
KLOUD_RUNTIME_STATE_PATH=/app/data/runtime-state.json
```

## Bridge wiring

On the bridge host, point the upstream to the real runtime:

```env
KLOUD_UPSTREAM_URL=http://<private-ip-of-hetzner-old>:9080
KLOUD_UPSTREAM_CANDIDATES=http://<private-ip-of-hetzner-old>:9080,https://aiagi.io
```

## Run locally

```bash
uvicorn main:app --host 0.0.0.0 --port 9080
```
