# KLOUD-RISC NOW Engineering Spec v1

Date: 2026-04-16
Status: Draft for execution
Scope: Immediate execution baseline (T+24h, T+72h) with 90-day FPGA sovereign edge roadmap

## 0. Mission and System Boundary

Build a distributed sovereign processing node based on RISC-V that is:

- Secure by design
- AI-capable at edge
- Measurably verifiable (attestation, policy, drift control)
- Cloud-coherent with deterministic sync

System boundary for v1:

- One FPGA-based node (PicoSoC path)
- One control-plane endpoint
- One signed sync channel
- One measurable secure boot and attestation pipeline

Out of scope for v1:

- Tape-out constraints
- Multi-node production scheduling
- Full PQ hardware accelerator

## 1. Interface Contracts (Block-to-Block)

### 1.1 Contract Rules

All interfaces MUST define:

- Ownership (producer, consumer)
- Clock/reset domain
- Data schema and version
- Latency budget
- Error semantics
- Security policy

All control interfaces MUST be versioned.
All runtime telemetry interfaces MUST include integrity metadata.

### 1.2 Interface Matrix

| ID | Producer | Consumer | Interface | Payload | Latency Budget | Security |
| --- | --- | --- | --- | --- | --- | --- |
| IF-001 | Boot ROM | Secure Monitor | ROM call ABI | boot_measurements, boot_state | < 1 ms | immutable ROM, hash chain |
| IF-002 | Secure Monitor | Attestation Engine | MMIO mailbox | nonce, pcr_values, device_id | < 2 ms | signed response, anti-replay nonce |
| IF-003 | Attestation Engine | Mesh Agent | local API | attestation_token, validity_window | < 5 ms | token signature verification |
| IF-004 | Mesh Agent | Control Plane | TLS/mTLS gRPC | heartbeat, attestation_token, node_health | < 100 ms WAN | mTLS + policy check |
| IF-005 | Pulse Timing Unit | Mesh Agent | IRQ + shared memory | pulse_tick, drift_ppm, tide_phase | deterministic tick | signed config, monotonic counter |
| IF-006 | RV64 Cluster | Vector Engine | coherent bus | vector ops, tensors, status | workload-dependent | privilege + PMP region checks |
| IF-007 | Key Vault | Crypto Runtime | key handle API | sign, verify, unwrap | < 3 ms op avg | no raw key export |
| IF-008 | Sync Engine | Storage Controller | DMA + queue | signed snapshots, rollback markers | < 20 ms local | integrity tag per block |

### 1.3 Interface Versioning Policy

- MAJOR increments break compatibility.
- MINOR increments add backward-compatible fields.
- PATCH increments do not change schema.
- Every message includes schema_version.

### 1.4 Error Contract

Standard error codes:

- E_AUTH_INVALID
- E_POLICY_DENY
- E_NONCE_REPLAY
- E_DRIFT_EXCEEDED
- E_KEY_UNAVAILABLE
- E_ATTEST_EXPIRED

Any E_AUTH_INVALID or E_NONCE_REPLAY event MUST trigger quarantine mode.

## 2. Threat Model (STRIDE)

### 2.1 Assets

- Root key material (device identity)
- Boot integrity chain
- Runtime policy state
- Sync payload integrity
- Telemetry authenticity

### 2.2 Trust Boundaries

- Boundary A: Boot ROM to mutable firmware
- Boundary B: Local node to control plane
- Boundary C: Runtime apps to key vault
- Boundary D: Sync fabric to storage

### 2.3 STRIDE Table

| Threat | Example | Impact | Control | Verification |
| --- | --- | --- | --- | --- |
| Spoofing | fake node identity | unauthorized mesh participation | device-bound keys + attestation | invalid token rejection rate |
| Tampering | modified boot stage | persistent compromise | measured boot + signed artifacts | boot hash mismatch alarm |
| Repudiation | node denies action | audit gap | signed event logs with monotonic counter | audit chain verification |
| Information Disclosure | key leakage | sovereign trust break | non-exportable key handles, memory isolation | key exfiltration test suite |
| Denial of Service | sync flood | node instability | rate limiting + priority control plane queue | sustained load soak test |
| Elevation of Privilege | app accesses vault | privilege escape | PMP/MMU policy + syscall mediation | privilege boundary fuzz tests |

### 2.4 Security Controls Baseline

Mandatory for v1:

- Secure boot with signature validation
- Measured boot evidence available to control plane
- mTLS node-to-control-plane channel
- Key handles only, no raw private key export
- Signed sync messages and anti-replay nonce window

### 2.5 Incident Modes

- Mode GREEN: normal operation
- Mode AMBER: degraded, sync read-only
- Mode RED: quarantine, control-plane-only operations

Transition to RED when:

- Attestation invalid
- Replay detected beyond threshold
- Boot measurement mismatch

## 3. KPI and GO/NO-GO Criteria

### 3.1 Performance KPI

| KPI | Target | Gate |
| --- | --- | --- |
| Boot-to-attested-ready | <= 4 s | GO if met in 95th percentile |
| Control-plane heartbeat latency | <= 120 ms p95 | GO if met under nominal load |
| Signed sync apply latency | <= 50 ms local p95 | GO if met in soak |
| Vector job speedup vs scalar baseline | >= 1.8x | GO if met on reference workload |

### 3.2 Security KPI

| KPI | Target | Gate |
| --- | --- | --- |
| Secure boot verification failures undetected | 0 | hard NO-GO |
| Replay acceptance rate | 0 | hard NO-GO |
| Key export incidents | 0 | hard NO-GO |
| Attestation validation success | >= 99.9% | GO threshold |

### 3.3 Reliability KPI

| KPI | Target | Gate |
| --- | --- | --- |
| 24h soak uptime | >= 99.5% | GO threshold |
| Crash-free runtime in reference profile | >= 12 h | GO threshold |
| Mean recovery time from AMBER | <= 60 s | GO threshold |

### 3.4 Determinism KPI

| KPI | Target | Gate |
| --- | --- | --- |
| Pulse drift | <= 25 ppm equivalent | GO threshold |
| Tide phase sync error | <= 5 ms | GO threshold |

### 3.5 Gate Logic

GO requires:

- All hard NO-GO controls passed
- >= 90% of non-hard KPIs met
- No unresolved critical vulnerabilities

## 4. Milestones and Weekly Plan (90 Days)

### Phase A: Architecture Freeze (Weeks 1-2)

Week 1:

- Freeze block diagram and trust boundaries
- Freeze interface IDs IF-001..IF-008
- Define schema_version policy

Week 2:

- Finalize STRIDE controls and incident modes
- Approve KPI table and gate criteria
- Review sign-off: architecture board

Exit criteria:

- Signed architecture packet
- Signed security baseline

### Phase B: Platform Bring-up (Weeks 3-6)

Week 3:

- FPGA platform baseline and toolchain reproducibility
- Boot ROM scaffold + measurement hooks

Week 4:

- Secure monitor and attestation mailbox integration
- First local attestation token generation

Week 5:

- Mesh agent transport with mTLS
- Heartbeat and health contract implementation

Week 6:

- Pulse/tide timing unit integration (v1)
- Signed sync envelope prototype

Exit criteria:

- End-to-end boot -> attestation -> heartbeat demo

### Phase C: Security Hardening and Determinism (Weeks 7-10)

Week 7:

- Anti-replay nonce windows + failure handling
- Red-mode quarantine transition logic

Week 8:

- PMP/MMU policy tests and privilege fuzzing
- Key-handle only API enforcement

Week 9:

- Determinism tests (pulse drift, tide phase)
- Soak tests under sync load

Week 10:

- Threat simulation drills (tamper, spoof, DoS)
- KPI recalibration and bug burn-down

Exit criteria:

- No hard NO-GO failures in 7-day test span

### Phase D: Operationalization (Weeks 11-13)

Week 11:

- CI gates for attestation and signed sync integrity
- Release artifact signing and provenance metadata

Week 12:

- Control-plane policy enforcement rollout
- Incident runbooks GREEN/AMBER/RED

Week 13:

- Final GO/NO-GO review for v1 release
- Architecture v1.1 backlog capture

Exit criteria:

- GO decision packet
- Evidence bundle attached

## 5. Immediate Next Actions (Next 7 Days)

1. Assign owners per interface contract IF-001..IF-008.
2. Create attestation token schema v0.1 and validation tests.
3. Define signed sync envelope format and replay policy.
4. Stand up KPI dashboard for boot, heartbeat, sync, and security events.
5. Run first architecture review and lock open decisions.

## 6. Open Decisions Requiring Owner Approval

1. CORE-V reuse vs custom core evolution timeline.
2. Initial vector acceleration strategy (pure RVV vs partial custom datapath).
3. Key vault implementation path for v1 (soft-hardened FPGA path vs external secure element).
4. Control-plane deployment model (single region vs dual region active-standby).

## 7. Definition of Done for v1

v1 is complete when:

- Secure boot evidence is measurable and verifiable from control plane.
- Node identity and signed sync are enforced end-to-end.
- KPI gates pass and GO packet is approved.
- Incident modes are tested and operational runbooks are validated.

## 8. Ready-Now Execution Plan (T+24h)

Objective: produce a working PicoSoC simulation baseline plus measurable evidence artifacts in one day.

### 8.1 Environment Separation Rule (Mandatory)

Do not mix shells or syntax:

- Cloud Shell: bash + Linux paths only.
- Local Windows: PowerShell + Windows paths only.
- Terraform HCL blocks go only in .tf files, never in terminal.

### 8.1.1 Top 3 Operator Errors and Fixes

Error 1: `-bash: Plan:: command not found`

- Cause: pasting Terraform output (`Plan: ...`) as if it were a command.
- Fix: run only real Terraform commands like `terraform plan -out=tfplan` and `terraform apply tfplan`.

Error 2: `-bash: lifecycle: command not found`

- Cause: pasting HCL config (`lifecycle { ... }`) directly in terminal.
- Fix: put `lifecycle { ... }` only inside `.tf` resource blocks, then run `terraform plan`.

Error 3: shell/path mixup or typo (`scoop`, `&`, `C:\...` in Cloud Shell, or `kdir`)

- Cause: mixing Windows PowerShell syntax with Linux bash syntax, plus command typo.
- Fix in Cloud Shell: use bash + Linux paths only.

```bash
mkdir -p ~/kloud-risc-evidence/day0
cd ~/picorv32/picosoc
```

### 8.2 Day-0 Deliverables

By end of T+24h, the team MUST produce:

1. PicoSoC simulation pass log (`make test` successful).
2. Toolchain manifest (compiler, simulator, and versions).
3. Initial attestation token schema draft (v0.1 JSON format).
4. Signed sync envelope draft (header and integrity fields).
5. Evidence folder with timestamped logs.

### 8.3 Cloud Shell Command Set (Simulation Baseline)

Run only in Cloud Shell:

```bash
cd ~/picorv32/picosoc
sudo apt-get update
sudo apt-get install -y make build-essential iverilog gcc-riscv64-unknown-elf binutils-riscv64-unknown-elf
make clean
make test RISCV_GCC_PREFIX=riscv64-unknown-elf-
```

Evidence capture:

```bash
mkdir -p ~/kloud-risc-evidence/day0
date -u +"%Y-%m-%dT%H:%M:%SZ" > ~/kloud-risc-evidence/day0/timestamp.txt
iverilog -V > ~/kloud-risc-evidence/day0/iverilog-version.txt
riscv64-unknown-elf-gcc --version > ~/kloud-risc-evidence/day0/riscv-gcc-version.txt
```

### 8.4 Gate for T+24h

GO if all pass:

1. `make test` exits with code 0.
2. Evidence files exist and are complete.
3. No unresolved toolchain mismatch.

NO-GO if any fail:

1. Build breaks without workaround documented.
2. Missing evidence artifacts.
3. Mixed environment errors repeat (bash vs PowerShell vs HCL).

## 9. Ready-Now Execution Plan (T+72h)

Objective: transition from simulation baseline to security and sync proof-of-capability.

### 9.1 Deliverables by T+72h

1. Attestation token schema v0.1 finalized.
2. Token verification utility (host-side) implemented.
3. Signed sync envelope parser and verifier stub implemented.
4. First KPI report with baseline values for boot, heartbeat, and sync latency.

### 9.2 Minimum Data Schemas

Attestation token fields (v0.1):

- `schema_version`
- `device_id`
- `boot_measurement_hash`
- `nonce`
- `issued_at_utc`
- `expires_at_utc`
- `signature_alg`
- `signature`

Signed sync envelope fields (v0.1):

- `schema_version`
- `node_id`
- `sequence_number`
- `monotonic_counter`
- `payload_hash`
- `policy_epoch`
- `signature_alg`
- `signature`

### 9.3 KPI Capture Template

Track at least:

1. Boot-to-ready latency (ms)
2. Token verification latency (ms)
3. Sync envelope verification latency (ms)
4. Replay rejection rate (%)

### 9.4 Gate for T+72h

GO if all pass:

1. Token and envelope verifiers run on reference samples.
2. Replay tests reject invalid nonce and stale counter.
3. KPI report generated with reproducible method.

NO-GO if any fail:

1. Signatures not verifiable.
2. Replay path not blocked.
3. KPI method not reproducible.

## 10. Command and Artifact Discipline

All execution must follow this discipline:

1. Every run gets a UTC timestamp and operator ID.
2. Every decision references evidence artifact paths.
3. Every NO-GO includes corrective action and owner.
4. Every GO includes rollback path and monitoring window.
