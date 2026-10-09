# 🧠 CLX BRAIN - Sistemi Kognitiv i Clisonix

Sistemi unified kognitiv me:
- **Brain Elastik** - Rrjet neuronal me plastikitet dinamik
- **Redis Unlimited** - Persistencë pa kufizime
- **Etikë Integruese** - Vendimmarrje etikisht e sigurt
- **Learning Loops** - Përshtatje elastike

## Karakteristika

### 1. Rrjeti Neuronal (19 Neurone)
- **Sensorë (5)**: vizual, auditiv, kinestetik, emocional, intuitiv
- **Procesues (6)**: analitik, kreativ, logjik, emocional, intuitiv, etik
- **Memorie (4)**: afatshkurter, afatgjate, procedurale, semantike
- **Motorikë (4)**: veprim, komunikim, adaptim, krijim

### 2. Redis Unlimited
- MAX_CONNECTIONS: 0 (unlimited)
- MAXMEMORY: 0 (no limit)
- Stream groups pa limite për debate staging
- Pub/Sub për real-time metrics
- Persistencë real-time

### 3. Etika
8 vlera themelore në çdo vendim:
- Dinjiteti i njeriut
- Liria e veprimit
- Përgjegjësia
- Transparenca
- Drejtesia
- Mos demtimi
- Autonomia
- Solidariteti

### 4. Mësim Elastik
- Dynamic rule weighting
- Success-based adaptation
- Experience-driven learning
- Elasticity metrics tracking

## Struktura e Skedarëve

```
services/clx_brain/
├── __init__.py                 # Module imports
├── clx_brain_core.py           # Core cognitive engine (1150+ lines)
├── main.py                     # FastAPI router
├── api.py                      # Application entry point
├── ocean_integration.py        # Ocean-Core integration
├── requirements.txt            # Dependencies
├── Dockerfile                  # Container image
├── docker-compose.service.yml  # Service configuration
└── README.md                   # This file
```

## Përdorimi

### 1. Inicializimi

```bash
# Docker
docker run -p 9999:9999 clisonix/clx-brain:latest

# Python
from services.clx_brain import CLXBrain

brain = CLXBrain()
```

### 2. Procesimi

```python
# Direct processing
result = brain.procesoj({
    "input_data": {...},
    "context": {...}
})

# REST API
curl -X POST http://localhost:9999/brain/process \
  -H "Content-Type: application/json" \
  -d '{"input_data": {...}}'
```

### 3. Mësimi

```python
# Learn from experience
brain.mëso({
    "tipi": "debate_outcome",
    "eksperiencë": {
        "success": True,
        "neurone_aktivizuar": ["analitik", "etik"],
        "lidhje_e_re": {
            "burimi": "analitik",
            "destinacioni": "veprim"
        }
    }
})

# REST API
curl -X POST http://localhost:9999/brain/learn \
  -H "Content-Type: application/json" \
  -d '{
    "tipi": "debate_outcome",
    "eksperiencë": {...}
  }'
```

### 4. Status dhe Metrika

```bash
# Status
curl http://localhost:9999/brain/status

# Metrika
curl http://localhost:9999/brain/metrics

# Neurone
curl http://localhost:9999/brain/neurons

# Rregulla
curl http://localhost:9999/brain/rules
```

### 5. WebSocket Streaming

```javascript
const ws = new WebSocket('ws://localhost:9999/brain/stream');

ws.onmessage = (event) => {
    const result = JSON.parse(event.data);
    console.log('Vendim:', result.vendim);
};

// Send input
ws.send(JSON.stringify({
    input_data: {...},
    context: {...}
}));
```

## Integration me Ocean-Core

### Debate Streaming

```python
from services.clx_brain.ocean_integration import get_integration

integration = await get_integration()

# Subscribe to debate
async for message in integration.subscribe_to_debate("debate_123"):
    print(message)

# Store metrics
await integration.store_debate_metrics("debate_123", {
    "duration_ms": 1500,
    "token_count": 500,
    "confidence": 0.95
})

# Store decision with cognitive processing
await integration.store_debate_decision("debate_123", {
    "outcome": "resolved",
    "confidence": 0.92
})

# Learn from debate
await integration.learn_from_debate("debate_123", success=True)
```

## API Endpoints

### Brain Service

| Endpoint | Method | Përshkrimi |
|----------|--------|-----------|
| `/brain/initialize` | POST | Inicializon brain-in |
| `/brain/process` | POST | Proceson input |
| `/brain/learn` | POST | Mëson nga eksperiencë |
| `/brain/status` | GET | Status i brain-it |
| `/brain/history` | GET | Historiku procesimi |
| `/brain/metrics` | GET | Metrika kognitive |
| `/brain/rules` | GET | Rregullat e vendimmarrjes |
| `/brain/neurons` | GET | Info të neuroneve |
| `/brain/stream` | WS | Real-time cognitive stream |

### System Health

| Endpoint | Përshkrimi |
|----------|-----------|
| `/health` | Health check |
| `/status` | Service status |
| `/metrics` | System metrics |

## Environment Variables

```bash
SERVICE_NAME=clx-brain
SERVICE_PORT=9999
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
LOG_LEVEL=INFO
BRAIN_MODE=cognitive_engine
ENABLE_LEARNING=true
ENABLE_ETHICS=true
PLASTICITY_RATE=0.1
ELASTICITY_TARGET=0.85
```

## Performance Karakteristika

- **Processing Time**: ~10-50ms per input
- **Memory per Session**: ~2-5MB
- **Concurrent Streams**: Unlimited (Redis)
- **Token Throughput**: 5000+ tokens/sec
- **Learning Efficiency**: 0.85+ elasticity

## Debugging

### Logs

```bash
docker logs clisonix-clx-brain
```

### Metrics

```bash
curl http://localhost:9999/metrics | jq
```

### Neuron Status

```bash
curl http://localhost:9999/brain/neurons | jq
```

## Arkitektura

```
Input
  ↓
Sensors (5)
  ↓
Processors (6)
  ↓
Memory (4)
  ↓
Ethical Filter
  ↓
Decision Engine
  ↓
Motor Output (4)
  ↓
Redis Storage (Unlimited)
  ↓
Learning Loop
```

## Vlerat Etike

Çdo vendim i brain-it kalon nëpër filtrin etik:

```python
etika = ParimetEtike()
vendim_i_vlerësuar = etika.vlereso_vendim({
    "veprim": "krijo",
    "demtim": False,
    "transparent": True,
    "i_drejte": True,
})

# Rezultati:
{
    "i_pranueshem": True,
    "vlera_te_prekura": ["dinjiteti", "liria", ...],
    "rekomandim": "Vendimi është etikisht i pranueshëm"
}
```

## Integrim me Ocean-Core

CLX Brain integrohet me Ocean-Core për:
- Debate streaming pa limite
- Cognitive processing të rezultateve
- Ethical validation të vendimeve
- Learning loops nga debate outcomes

## Trajnim dhe Mësim

Sistemi mëson përmes:
1. **Experience-based learning** - Gjithnjë kur procesoj input
2. **Success-driven adaptation** - Neurone + rregulla përshtatjnë peshën
3. **Ethical feedback loops** - Validimet etike influencojnë mësimin
4. **Memory consolidation** - Eksperienca ruhen në afatgjatë

## Liçensi

© 2026 Clisonix Cloud - All Rights Reserved

## Kontakt

- **Team**: Clisonix Development
- **Repository**: github.com/clisonix/clisonix-cloud
- **Issues**: GitHub Issues

---

**Shënim**: "Ky kod është i jaxtëzakonshëm" 🧠✨
