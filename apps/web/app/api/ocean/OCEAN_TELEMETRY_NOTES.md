# Ocean API Telemetry Notes

This module now exposes response diagnostics to track real service quality (speed + reliability + language consistency).

## Stream route

- Endpoint: `/api/ocean/stream`
- Response headers:
  - `X-Ocean-Route`: `orchestrated | chat | native-stream | retry-direct | none`
  - `X-Ocean-Language`: resolved response language
  - `X-Ocean-Latency-Ms`: total route latency for this request
  - `X-Ocean-Upstream-Ms`: upstream call latency of selected route
  - `X-Ocean-Policy-Retry`: `1` if policy retry was applied

## Non-stream route

- Endpoint: `/api/ocean`
- Response headers:
  - `X-Ocean-Route`
  - `X-Ocean-Language`
  - `X-Ocean-Latency-Ms`
  - `X-Ocean-Route-Latency-Ms`
  - `X-Ocean-Policy-Retry`
- JSON payload includes:
  - `diagnostics.route_used`
  - `diagnostics.route_latency_ms`
  - `diagnostics.total_latency_ms`
  - `diagnostics.policy_retry`

## Language guard behavior

A conservative language-policy validator now retries direct answer generation when output appears to violate language lock policy (e.g., meta-language statements or obvious greeting-language mismatch).

## Upstream timeout

Stream route upstream calls use timeout protection (`UPSTREAM_TIMEOUT_MS = 120000`) to avoid long hangs and improve responsiveness under failure.
