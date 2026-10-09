# KLOUd Bridge Proof-of-Life Runbook

**Goal:** turn the bridge from a static contract surface into a living system with:

1. one active node,
2. one real signal,
3. one controlled upstream integration target.

---

## Step 1 — Start a controlled upstream stub

```powershell
Set-Location c:\Users\Admin\Desktop\Clisonix-cloud
c:/Users/Admin/Desktop/Clisonix-cloud/.venv/Scripts/python.exe scripts/hardware/kloud_upstream_stub.py
```

Default stub URL:

- `http://127.0.0.1:9081/status`
- `http://127.0.0.1:9081/peers`
- `http://127.0.0.1:9081/state`
- `http://127.0.0.1:9081/submit`

---

## Step 2 — Point `kloud-bridge` to the stub

```powershell
$env:KLOUD_UPSTREAM_URL='http://127.0.0.1:9081'
Set-Location c:\Users\Admin\Desktop\Clisonix-cloud\services\kloud_bridge
c:/Users/Admin/Desktop/Clisonix-cloud/.venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8892
```

---

## Step 3 — Start one live node and emit one real signal

### Python runner

```powershell
Set-Location c:\Users\Admin\Desktop\Clisonix-cloud
c:/Users/Admin/Desktop/Clisonix-cloud/.venv/Scripts/python.exe scripts/hardware/oceancore_edge_node.py --bridge http://127.0.0.1:8892 --profile scripts/hardware/profiles/oceancore_lab_01.json --count 3 --interval 5 --emit-signal
```

### Rust runner

```powershell
Set-Location c:\Users\Admin\Desktop\Clisonix-cloud
cargo run --manifest-path scripts/hardware/rust_node_agent/Cargo.toml -- --bridge http://127.0.0.1:8892 --profile scripts/hardware/profiles/oceancore_lab_01.json --count 3 --interval 5 --emit-signal
```

This will:

- register `oceancore-lab-01`
- send heartbeats
- publish one proof-of-life signal through `/api/v1/signals/publish`
- persist the node identity in the bridge registry

### Direct verification checks

After registration, verify:

- `GET /api/v1/hardware/nodes`
- `GET /api/v1/hardware/registry`

Expected outcome:

- `status: "registered"` from register
- `status: "heartbeat-recorded"` from heartbeat
- `registered_nodes >= 1`
- `online_nodes >= 1`
- `binding_state: "bound"`

---

## What success looks like

`GET /api/v1/status` should begin showing:

- `registered_nodes: 1`
- `online_nodes: 1`
- `network_health: "healthy"`
- `service_truth.proof_of_life: "active"`
- `service_truth.sync_status: "synchronized"` or `"partial"`
- `service_truth.last_signal` populated

---

## Why this matters

This runbook proves the bridge is not just a static API shell. It demonstrates:

- a node lifecycle,
- a real signal in motion,
- a service-truth surface that reacts to live integration state.
