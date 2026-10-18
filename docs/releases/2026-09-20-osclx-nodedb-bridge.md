# OS-CLX NodeDB bridge — 2026-09-20

## Issue

`clx-hybrid` required `NODEDB_FLUID_URL`, but its only writer emitted a private binary payload. The canonical OS-CLX runtime at `aiagi.io` accepts JSON telemetry at `POST /v1/ndb/nodes/{nodeId}/telemetry`, so the old writer could not form a real integration.

## Documentation

The production Compose default now targets the canonical `clisonix-hybrid` telemetry node and declares the `osclx_json` transport. Legacy binary sinks remain available when selected explicitly or when auto detection receives a non-telemetry URL.
Writes carry the required OS-CLX `operator` role. Optional API key and HMAC variables support stricter runtime policy without storing credentials in the repository.

## Tests

The contract tests validate canonical field names, pressure and resonance normalization, task routing metadata, burst policy, clamping, and the operator header. A live operator-role probe returned HTTP 200 and the `clisonix-hybrid` node was read back from OS-CLX NodeDB.
The initial container probe also found that the image listened on `11438` while Compose and its health check used `8058`; production Compose now sets `PORT=8058` explicitly.

## Edge cases

Resonance is clamped to the OS-CLX `0..1` range. Unknown transport names fail closed. A configured endpoint that rejects telemetry keeps the scan result in a 503 state rather than reporting persistence that did not happen.

## Benchmark

This change adds one bounded JSON POST per completed hybrid scan. No throughput improvement is claimed. Runtime latency and response status are returned by the existing NodeDB persistence result.

## Rollback

Set `NODEDB_FLUID_TRANSPORT=binary` and restore the previous sink URL for a legacy receiver, or roll the `clx-hybrid` image back to its prior tag. Do not delete OS-CLX NodeDB history during rollback.
