# OceanCore Rust Node Agent

Minimal Rust-based edge agent for the `kloud-bridge` hardware contract.

## Features

- loads the shared JSON node profile
- fetches the firmware contract from the bridge
- registers a node over `/api/v1/hardware/nodes/register`
- sends one-shot or repeated heartbeats
- emits lightweight proof-of-life pulse frames over `/api/v1/hardware/nodes/pulse`
- can emit a proof-of-life signal through `/api/v1/signals/publish`

## Build

```bash
cargo build --manifest-path scripts/hardware/rust_node_agent/Cargo.toml
```

## Run

```bash
cargo run --manifest-path scripts/hardware/rust_node_agent/Cargo.toml -- \
  --bridge http://127.0.0.1:8889 \
  --profile scripts/hardware/profiles/oceancore_lab_01.json \
  --count 3 --interval 5 --emit-signal
```

## Docker runtime

For a restart-safe production node, build and run the Cargo agent in Docker so it keeps registering, pulsing, and heartbeating after bridge restarts.

## Production cadence and wake behavior

- `--interval` is in seconds. Use `300` for every 5 minutes.
- `--wake-offline` checks `/api/v1/hardware/nodes/{node_id}` each loop.
- If node `runtime_state` is `offline`, the agent sends:
  - `POST /api/v1/hardware/nodes/control` with action `wake`
  - optional wake signal through `/api/v1/signals/publish` when `--emit-signal` is enabled
