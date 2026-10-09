# `@clisonix/nanogrid`

Shared `NanoGrid` protocol bundle for Clisonix repositories.

## Isolation model

- `Kameleonlife/Kloud` is the **standalone sovereign Rust fabric** and should stay fully isolated.
- `@clisonix/nanogrid` is the **interop package** for Clisonix-side reuse, API bridges, and protocol compatibility.
- The bulk sync script skips `Kloud` by default to preserve that separation.

## Purpose

This package is the canonical reuse point for:
- packet framing
- CBOR payload encoding/decoding
- HMAC / CRC verification
- model ID and payload enums
- cross-repo synchronization

## Quick usage

```ts
import {
  createNanoGridPacket,
  parseNanoGridPacket,
  decodeNanoGridPayload,
  NanoGridModelId,
} from '@clisonix/nanogrid'

const packet = createNanoGridPacket(
  { temperature: 22.4, humidity: 40 },
  { modelId: NanoGridModelId.ESP32_PRESSURE }
)

const parsed = parseNanoGridPacket(packet.raw)
const payload = decodeNanoGridPayload(parsed)
console.log(payload)
```

## Canonical source files in this repo

- `nanogridata_protocol_v1.ts`
- `nanogridata_protocol_v1.py`
- `nanogridata_protocol_v1.c`
- `nanogridata_config.h`
- `nanogridata_gateway.ts`

## Cross-repo sync

Use:

```powershell
pwsh ./scripts/sync-nanogrid-profile.ps1 -GitHubOwner Web8kameleon-hub
```

> By default the sync script clones or updates repos locally and copies `packages/nanogrid` into them without pushing changes automatically.
