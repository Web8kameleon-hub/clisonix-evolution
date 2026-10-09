# Nanogridata + Bridge + Ocean Mapping (Official)

Version: 1.0.0  
Date: 2026-03-05

## 1) Official Module Roles

- **Nanogridata Protocol v1**: Clisonix Edge wire protocol for industrial/biomedical devices.
- **Bridge Engine**: signal router and policy point for pulse distribution.
- **Ocean Nanogrid v3**: Ocean Enterprise API core (chat + stream) for tenant-facing AI responses.

## 2) Ingestion Flow (Edge → Platform)

1. Device sends Nanogridata packet (magic, version, model_id, payload_type, flags, timestamp, payload, MAC).
2. Decoder validates:
   - magic/version/length
   - timestamp window / anti-replay policy
   - security level MAC (CRC / HMAC / HMAC+timestamp)
3. Valid packet is normalized to pulse envelope:
   - `id`
   - `source` (device or gateway)
   - `type` (mapped signal_type)
   - `timestamp`
   - `payload`
   - `metadata` (model_id, payload_type, security_level, lab_id, device_id)
4. Pulse is published to Bridge Engine (`/signals/publish` or Redis channel).
5. Bridge resolves targets by `signal_types` (or manual route rules) and forwards to consumers.

## 3) Canonical Signal Type Mapping

- `payload_type=TELEMETRY` → `telemetry.pressure`, `telemetry.gas`, `telemetry.device`
- `payload_type=EVENT` → `event.alarm`, `event.device`, `event.security`
- `payload_type=CONFIG` → `config.update`, `config.calibration`
- `payload_type=COMMAND` → `command.execute`
- `payload_type=CALIBRATION` → `calibration.run`

## 4) Consumer Mapping (Initial)

- `telemetry.*` → `advanced-analytics`, `asi-realtime`, `monitoring`
- `event.*` → `api`, `saas-api`, `monitoring`
- `config.*` / `calibration.*` → `ocean-core`, `advanced-cycle-alignments`
- `command.*` → policy-gated delivery (only explicit allowlist rules)

## 5) Ocean Enterprise API v1 Surface

Service: **Ocean Nanogrid v3**

- `POST /api/v1/chat`
- `POST /api/v1/chat/stream`
- `GET /health`
- `GET /api/v1/status`
- `DELETE /api/v1/memory/{session_id}`

SLA/SLO target class: **critical API service**.

## 6) Ingestion Audit Fields (Minimum)

For each valid decoded packet, persist:

- `ingest_id`
- `received_at`
- `model_id`
- `payload_type`
- `security_level`
- `lab_id`
- `device_id`
- `packet_timestamp`
- `bridge_pulse_id`
- `validation_result`

## 7) Security Notes

- No default secrets for HMAC keys.
- Reject malformed/invalid MAC packets.
- Enforce timestamp skew policy before route.
- Keep command routing disabled by default unless policy explicitly allows it.
