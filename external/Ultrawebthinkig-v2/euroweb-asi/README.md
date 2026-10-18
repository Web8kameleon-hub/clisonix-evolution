# EuroWeb • ASI (Alba/Albi/Jona/Core)

Industrial Intelligence System - 100% JavaScript

## 🧠 Architecture

euroweb-asi/
├─ package.json
├─ .env.example
├─ server.js                # API + Prometheus /metrics + scheduler
├─ lib/
│  ├─ log.js                # logging i pastër me nivele
│  ├─ ringbuffer.js         # ring buffer pa GC presion
│  ├─ stats.js              # EWMA, z-score, IQR, percentiles
│  └─ prometheus-parse.js   # parser i shpejtë për text exposition
└─ agi/
   ├─ core.js               # ASI orchestrator (life-cycle)
   ├─ monitor.js            # heartbeats + state machine
   └─ mind/
      ├─ alba.js            # Bits Pool: ingest + memory (file + ring)
      ├─ albi.js            # Born Intelligence: analiza shkencore
      └─ jona.js            # Balance/Ethics: guard-rails + policies

## 🚀 Quick Start

```bash
# Navigate to euroweb-asi directory
cd euroweb-asi

# Install dependencies
npm install

# Setup environment
cp .env.example .env

# Edit PROM_SOURCE to point to your existing dashboard's /metrics endpoint
# nano .env

# Start ASI system
npm run dev
```

## 🔧 Configuration

Edit `.env` file:

```env
PORT=8088                                    # ASI server port
HOST=0.0.0.0                                # Listen on all interfaces
PROM_SOURCE=http://localhost:8080/metrics   # Your dashboard's metrics endpoint
MEMORY_FILE=./agi/memory.jsonl              # Persistent memory storage
CYCLE_MS=5000                               # ASI cycle interval (5 seconds)
MAX_INMEM_SAMPLES=2048                      # Ring buffer size
CPU_Z_THRESHOLD=3.0                         # CPU anomaly detection threshold
MEM_Z_THRESHOLD=3.0                         # Memory anomaly detection threshold
EWMA_ALPHA=0.2                              # Exponential moving average smoothing
```

## 📊 API Endpoints

- `GET /api/asi/frame` - Complete ASI state (bits + analysis + decision)
- `GET /api/asi/analysis` - Scientific analysis from Albi
- `GET /api/asi/decision` - Policy decisions from Jona
- `GET /api/health` - System health check
- `GET /metrics` - Prometheus metrics export

## 🧩 Mind Components

### Alba (Bits Pool)

- **Function**:
 Data ingestion and memory management

- **Features**: Prometheus metrics collection, ring buffer storage, persistent memory
- **Output**: Raw system metrics (CPU, memory, event loop lag)

### Albi (Born Intelligence)

- **Function**

: Scientific analysis and pattern recognition

- **Features**:  

Statistical analysis, z-score anomaly detection, trend analysis

- **Output**:

 System state classification and insights

### Jona (Balance/Ethics)

- **Function**: Policy enforcement and decision making
- **Features**: Alert generation, system protection, load balancing recommendations
- **Output**: Actions and ethical guidelines

## 🔍 Monitoring

The ASI system exposes Prometheus metrics:

- `asi_cpu_last` - Current CPU load
- `asi_cpu_ewma` - CPU exponential moving average
- `asi_mem_last_gb` - Current memory usage (GB)
- `asi_mem_ewma_gb` - Memory exponential moving average (GB)
- `asi_evloop_p99` - Event loop lag p99 percentile
- `asi_alerts_total` - Total alerts fired (by type and reason)

## 🛡️ System Protection

Jona automatically monitors and protects against:

- **CPU Anomalies**: Z-score threshold violations
- **Memory Anomalies**: Excessive memory usage patterns
- **Event Loop Lag**: Node.js performance degradation
- **Load Spikes**: Automatic load redistribution recommendations

## 🔄 Real-time Operation

The ASI system operates in continuous cycles:

1. **Alba** collects system metrics from Prometheus source
2. **Albi** analyzes data using statistical methods and detects anomalies
3. **Jona** enforces policies and generates protective actions
4. Results are exposed via API and Prometheus metrics

## 🎯 Use Cases

- Real-time system monitoring and anomaly detection
- Automated performance optimization recommendations
- Predictive system health analysis
- Industrial-grade observability and alerting

## 📈 Performance

- **Memory Efficient**: Ring buffer prevents memory leaks
- **Low Latency**: Sub-second analysis cycles
- **Scalable**: Handles thousands of metrics per second
- **Resilient**: Graceful error handling and recovery

---

**🔬 EuroWeb ASI** - Where artificial intelligence meets industrial reliability.
