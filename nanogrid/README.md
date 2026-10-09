# Nanogrid: Sovereign PQ-Secure Adaptive Distributed Fabric

Nanogrid është një fabric i shpërndarë, sovereign, post-quantum secure dhe adaptive që funksionon si një organizëm i gjallë. Është ndërtuar me Rust për performancë dhe siguri maksimale.

## Features

- **Post-Quantum Security**: Dilithium2 për signing, Kyber512 për KEM, AES-256-GCM për encryption.
- **Adaptive Behavior**: Tide Engine (High/Normal/Low) bazuar në metrics (peers, latency, bandwidth, load).
- **Tri-Channel Gossip**: Digest/Delta/Bulk për shpërndarje efikase.
- **CRDT Merge**: Deterministic merge për konsistencë pa konflikte.
- **Zero-Copy & Async**: Tokio, CBOR serialization, append-only storage.
- **API & Dashboard**: REST API dhe HTML dashboard për kontroll.
- **Real Metrics & Key Management**: Metrics nga transport, key store për PQ verify.
- **Performance Optimized**: Connection pooling, persistent TCP.

## Architecture

### Core Components

- **Algebra**: Σᴜ ops (S/C/R/E/P/M/F/J/L/D/T/X).
- **Security**: PQ primitives (sign/verify/KEM/encrypt).
- **Protocol**:
  - Transport: TCP/QUIC me connection pooling.
  - Memory Log: Append-only in-memory.
  - Execution Pipeline: Ops execution me policy.
  - Routing Engine: Peer selection inteligjent.
  - Storage Engine: Persistent, tide-aware, CRDT-friendly.
  - Replication Engine: Shpërndarje adaptive.
  - Merge-Sync Engine: Ribashkim pas partitions.
- **Node**: State machine, metrics, Tide compute, API.

### Tide Levels

- **High**: Aggressive (fast gossip, all ops, high replication).
- **Normal**: Balanced.
- **Low**: Conservative (slow, minimal ops, energy-saving).

## Installation

```bash
git clone <repo>
cd nanogrid
cargo build --release
```

## Usage

### Single Node

```bash
cargo run
```

### Multi-Node Test

```powershell
.\scripts\run_multi_node.ps1
```

### API Endpoints

- `POST /submit`: Submit ops (JSON: {"ops":["S","C"], "payload":"base64_data"}).
- `GET /status`: Node status (metrics, tide).
- `GET /peers`: Peer list.
- `GET /state`: Local state (key-value).
- `GET /dashboard`: HTML dashboard.

## Configuration

Përdor environment variables:

- `NODE_ID`: Node ID (default: 1).
- `LISTEN_PORT`: TCP listen port (default: 8080).
- `PEERS`: Comma-separated peer list (default: 2:8081,3:8082,4:8083,5:8084).

## Monitoring

- Prometheus: `prometheus.yml` për scraping nodes.
- Dashboard: Built-in HTML at `/dashboard`.

## Security

- Çdo mesazh është signed dhe encrypted me PQ.
- Key management për peer verification.
- Sovereign: Pa varësi nga central authorities.

## Performance

- Async Tokio me connection pooling.
- Real metrics nga transport (latency, bandwidth).
- Zero-copy CBOR, append-only logs.

## Compute Policy (Chipsets)

Repo policy nuk kufizohet vetem te RISC-V. Nanogrid targeton performancen me te larte ne keto familje chip-esh:

- **NVIDIA Hopper/Blackwell (H100/H200/B100/B200)**: prioritet per inference/training throughput dhe batching agresiv.
- **AMD Instinct (MI300X/MI325X)**: prioritet per memory-bandwidth te larte dhe workloads vektoriale.
- **Intel Xeon + AMX / Gaudi**: prioritet per backend nodes enterprise dhe mixed CPU/accelerator deployments.
- **Apple Silicon (M3/M4 Max/Ultra)**: prioritet per edge orchestrators me performance-per-watt te larte.
- **ARM Neoverse (AWS Graviton4, AmpereOne)**: prioritet per cloud efficiency dhe horizontal scale.
- **x86_64 server-class (EPYC Genoa/Turin, Xeon Sapphire/Emerald Rapids)**: baseline i forte per throughput dhe memory-heavy services.
- **RISC-V (server dhe embedded profiles)**: mbetet target strategjik, por jo targeti i vetem.

Rregull i detyrueshem i repo-s:

- Feature-t e reja duhet te funksionojne ne menyre portabile te pakten ne `x86_64` dhe `ARM64`.
- Optimizimet hardware-specific aktivizohen me feature flags pa thyer fallback-un portabil.
- Nuk lejohet vendor lock-in ne rrugen kritike te ekzekutimit.

## Roadmap

- PQ verify full activation.
- Grafana dashboard.
- QUIC transport.
- Global deployment specs.

Ky është fabric-i i gjeneratës së ardhshme – sovereign, adaptive, ultra-secure. 🚀

- **Deploy Global**: Spec-e për deployment prodhim.
- **Hardware Integration**: Integrim multi-arch (x86_64, ARM64, RISC-V, GPU backends), node low-power.

Fabric-u është gati për prototip dhe zgjerim! 🌊
