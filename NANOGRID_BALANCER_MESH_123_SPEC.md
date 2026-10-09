# Nanogrid 1-2-3 Balancer Mesh Spec

## Goal

Align the runtime with the requested 1-2-3 hierarchy:

- Node 1: ingress + discovery
- Node 2: pulse + liveness arbitration
- Node 3: mesh federation + routing

And include batica/zbatica flow control (tide mode) plus NodeSMS concept.

## Source Alignment

This mapping is grounded in existing materials from our Git profile:

- Ultrawebthinkig-v2: mesh hierarchy and discovery/handshake patterns (`backend/mesh/MeshActivator.ts`, `app/api/continental-mesh/route.ts`)
- BledjonaAhmati/Ultrawebthinking (private template): conceptual WEB8 framing ("fakt ne ide dhe ne realitet") used as design context, not as direct runtime contract
- Kloud: tide-aware routing and fanout (`protocol/src/routing_engine.rs`, `node/src/policy_engine.rs`)
- Clisonix services: balancer + pulse + mesh hq contracts (`balancer_nodes_3334.py`, `balancer_pulse_3336.py`, `backend/mesh/server.py`)

## Runtime Contract

Implemented endpoint:

- `GET /api/hierarchy/123`

Response sections:

- `nodes.node_1_ingress`
- `nodes.node_2_pulse`
- `nodes.node_3_mesh`
- `flow_control.batica_zbatica`
- `riscv`
- `governance_labor`
- `upstream`

## Node Responsibilities

### Node 1 (Ingress / Discovery)

- Local node registry (`/api/nodes/*`)
- Vendor edge registry (`/api/vendor-nodes/*`)
- NodeSMS coverage counter from vendor metadata/capabilities/type

### Node 2 (Pulse / Liveness)

- Pulls real pulse status from balancer pulse service
- Exposes alive/dead counts from real heartbeat stream
- No synthetic fallback when pulse service is unavailable

### Node 3 (Mesh / Federation)

- Tracks external mesh nodes and offline queues
- Pulls mesh node list from Mesh HQ when available
- Keeps source availability explicit in payload

## Batica/Zbatica Mapping

- Batica/Zbatica is represented as tide mode:

  - `high` -> aggressive fanout profile
  - `normal` -> balanced profile
  - `low` -> conservative profile

- Tide is read from Kloud status upstream when available.

## NodeSMS Note

- NodeSMS is now first-class in user data backend/frontend and counted in Node 1 ingress coverage.
- If StarBooking-specific NodeSMS schema is required, it should be attached as a formal contract example and then wired into vendor registration metadata validation.

## Governance + Labor Capability Matrix

Based on the repositories you shared, the following capability families should be treated as part of the reference architecture vocabulary for Nanogrid/Balancer planning:

- Governance/Control: quantum + DDoS + mesh HQ + ONNX orchestration language across Web8 layers
- Labor-Vision: YOLO, ResNet50, EasyOCR
- Labor-NLP: BERT, BART, sentiment analysis
- Labor-Audio: Whisper speech-to-text
- Labor-Synthesis: GPT-2 generation
- Security/Fabric baseline: Dilithium/Kyber post-quantum model + tide-aware sovereign fabric
- Power/Fabric mode: WEB8 fluid hybrid inverter concept for adaptive runtime behavior

### Truthfulness and Runtime Status

- Present in source repos as concepts/contracts/examples: yes
- Already enforced in this local runtime endpoint (`GET /api/hierarchy/123`): partial (hierarchy/tide/mesh/pulse are live)
- Not yet wired as verified local execution contracts: model-specific Labor adapters (YOLO/ResNet50/EasyOCR/BERT/BART/Whisper/GPT-2), ONNX execution graph, and fluid-inverter control loop

This means the architecture is aligned semantically, but model execution should be marked as planned until each adapter has concrete endpoint + health + test coverage in this repository.

## RISC-V + Governance Runtime Extension

The hierarchy endpoint now exposes runtime fields for RISC-V readiness and governance/labor controls.

### RISC-V

- `riscv.target_arch`
- `riscv.hardware_mode`
- `riscv.secure_elements`
- `riscv.vector_extension`
- `riscv.bitmanip_extension`
- `riscv.readiness_score`

These values are environment-driven and provide operational truth (no synthetic fallback scoring).

### Governance + Labor

- `governance_labor.governance.quantum_enabled`
- `governance_labor.governance.ddos_enabled`
- `governance_labor.governance.mesh_hq_enabled`
- `governance_labor.governance.onnx_runtime_enabled`
- `governance_labor.labor.*_models` and readiness flags

This allows direct observability of the features requested earlier (quantum/ddos/mesh HQ/ONNX + labor model stacks) through the same `GET /api/hierarchy/123` contract.
