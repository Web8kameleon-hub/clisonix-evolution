# ASI Real Service (Standalone)

This document describes the standalone ASI service powered by `asi_api_server.py` and `asi_core.py`.

## Purpose

- Canonical ASI microservice for real telemetry and node status
- Mesh registration and telemetry forwarding
- Optional combined ASI + JONA real-monitor snapshot

## Run

```bash
uvicorn asi_api_server:app --host 0.0.0.0 --port 9094 --reload
```

## Endpoints

- `GET /health` — service health summary
- `GET /status` — realtime ASI status
- `GET /metrics` — raw realtime engine metrics
- `GET /nodes` — node status map
- `GET /logs` — last ASI logs
- `GET /system` — host CPU/RAM/Disk/Network metrics
- `POST /mesh/register` — register ASI node to mesh service
- `POST /mesh/send` — send current telemetry to mesh service
- `GET /asi/joint-status` — ASI snapshot + JONA real health/harmony

API aliases are also exposed under `/api/v1/*` for selected endpoints.

## Environment Variables

These variables are consumed by `ASIConfig` in `asi_core.py`:

- `ASI_HQ_EVENT_URL` (default in Docker: `http://clisonix-api:8000/mesh/status`)
- `ASI_HQ_REGISTER_URL` (default in Docker: `http://clisonix-api:8000/mesh/register`)
- `ASI_HQ_STATUS_URL` (default in Docker: `http://clisonix-api:8000/mesh/status`)
- `ASI_AUDIO_UPLOAD_URL` (default: `https://clisonix.com/api/uploads/audio/process`)
- `ASI_EEG_UPLOAD_URL` (default: `https://clisonix.com/api/uploads/eeg/process`)
- `ASI_REQUEST_TIMEOUT_SECONDS` (default: `5`)
- `ASI_REQUEST_MAX_RETRIES` (default: `3`)
- `ASI_REQUEST_RETRY_BACKOFF_SECONDS` (default: `0.5`)

## Reliability Model

- All outbound ASI HTTP calls use retry + incremental backoff
- 5xx responses are retried until max attempts are reached
- Missing `requests` or `psutil` is handled gracefully with explicit error payloads/logs

## Integration Notes

- Main API also exposes parity route: `GET /api/asi/joint-status`
- JONA integration uses `apps.api.services.jona_real_monitor.create_jona_real`
- If JONA service-layer import fails, ASI returns a graceful degraded `jona.available=false` envelope
