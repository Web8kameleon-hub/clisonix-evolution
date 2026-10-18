# CLX Runtime Deploy (No-Dependencies, Zero-Downtime Style)

Target: `root@178.105.52.245`

## Scope

Deploy only isolated CLX runtime services (profile `clx-runtime`):

- `clx-agent` (`clisonix-clx-agent`, port `7778`):
  Agjent kryesor, mësim dhe CLX Memory.
- `clx-i` (`clisonix-clx-i`, port `8048`):
  Inference engine për WWWMMM / NDB mode.
- `clx-hybrid` (`clisonix-clx-hybrid`, port `8058`):
  Bridge për NodeDB Fluid dhe Stigma Fluid.

Do not restart unrelated services and do not run full-stack `up`.

## Preconditions

1. `NODEDB_FLUID_URL` set in server `.env` nëse NodeDB external sink është aktiv.
2. `STIGMA_FLUID_MEMORY_URL` set në `.env` nëse Stigma Fluid Memory është aktive.
3. Stack bazë healthy (`ocean-core`, `api`, Ollama).

## Komponentët CLX dhe env vars

### clx-agent — CLX Memory + Self-Learning
```
PORT=7778
CLX_MEMORY_DIR=/data/.clx
CLX_MEMORY_PATH=/data/.clx/training-memory.json
CLX_AUTO_LEARN=true
CLX_LEARN_DURATION=14400      # sekonda sesioni mësues
CLX_LEARN_INTERVAL=60         # interval polling (s)
CLX_TEACHER_BACKEND=qwen
CLX_TEACHER_MODEL=qwen2.5:1.5b
CLX_TEACHER_OLLAMA_HOST=http://clisonix-ollama:11434
CLX_TEACHER_TIMEOUT_SECONDS=45
CLX_DEFAULT_LANGUAGE=en
```
Volume i persistuar: `clx_memory:/data/.clx`

### clx-i — Inference / WWWMMM / NDB
```
CLXI_OLLAMA_HOST=http://clisonix-ollama:11434
CLXI_VISION_MODEL=llava:latest
CLXI_MODE=wwwmmm_ndb           # modaliteti kryesor
CLXI_SELFLEARNING_ENABLED=1
CLXI_SELFLEARNING_FILE=/data/selflearning_events.jsonl
CLXI_MIRROR_FILE=/data/mirror_events.jsonl
```
Volume: `./data/clx-i:/data`

### clx-hybrid — NodeDB Fluid + Stigma Fluid Memory + Resonance Bridge
```
CLX_HYBRID_API_URL=http://clisonix-api:8000
CLX_HYBRID_OCEAN_URL=http://clisonix-ocean-core:8030
CLX_HYBRID_CLX_AGENT_URL=http://clisonix-clx-agent:7778
CLX_HYBRID_CLXI_URL=http://clisonix-clx-i:8048
NODEDB_FLUID_URL=<external>        # NodeDB Fluid sink — opsionale
STIGMA_FLUID_MEMORY_URL=<external> # Stigma Fluid Memory — opsionale
RESONANCE_ENDPOINT=<external>      # Resonance layer — opsionale
```
Volume: `./data/clx-hybrid:/data`

Nëse `NODEDB_FLUID_URL` / `STIGMA_FLUID_MEMORY_URL` / `RESONANCE_ENDPOINT` mungojnë,
`clx-hybrid` raporton `status = not_configured` — **jo fake data, jo fallback**.

## Build Only Targeted Services

```bash
# Build të tre
ssh root@178.105.52.245 \
  "cd /root/Clisonix-cloud && \
   docker compose --profile clx-runtime build clx-agent clx-i clx-hybrid"

# Build vetëm clx-i dhe clx-hybrid
ssh root@178.105.52.245 \
  "cd /root/Clisonix-cloud && \
   docker compose --profile clx-runtime build clx-i clx-hybrid"
```

## Rolling Start/Update (No Deps)

```bash
# Start/update clx-i dhe clx-hybrid
ssh root@178.105.52.245 \
  "cd /root/Clisonix-cloud && \
   docker compose --profile clx-runtime up -d --no-deps clx-i clx-hybrid"

# Start/update të tre pa prekur shërbime tjera
ssh root@178.105.52.245 \
  "cd /root/Clisonix-cloud && \
   docker compose --profile clx-runtime up -d --no-deps clx-agent clx-i clx-hybrid"
```

CLX agent refresh i veçuar:

```bash
ssh root@178.105.52.245 \
  "cd /root/Clisonix-cloud && \
   docker compose build clx-agent && \
   docker compose up -d --no-deps clx-agent"
```

## Health Verification

```bash
# clx-i (inference / WWWMMM / NDB)
ssh root@178.105.52.245 "curl -fsS http://localhost:8048/health"

# clx-hybrid (NodeDB Fluid / Stigma Fluid / Resonance)
ssh root@178.105.52.245 "curl -fsS http://localhost:8058/health"

# clx-agent (CLX Memory / Self-Learning)
ssh root@178.105.52.245 "curl -fsS http://localhost:7778/health"

# Statusi i plotë i të gjithë stack-ut CLX
ssh root@178.105.52.245 \
  "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' \
   | grep -E 'clx|NAMES'"
```

## NodeDB / Stigma Fluid / Resonance — Shënim

Këta komponentë janë **external sinks**.
Vendosen vetëm me env vars në `.env` të serverit:

```env
NODEDB_FLUID_URL=http://<nodedb-host>:<port>
STIGMA_FLUID_MEMORY_URL=http://<stigma-host>:<port>
RESONANCE_ENDPOINT=http://<resonance-host>:<port>
```

Pa këto variabla, `clx-hybrid` vazhdon të funksionojë me status
`not_configured` — asnjë fallback, asnjë fake data.
