# 🚀 QUICK API REFERENCE

## Startup Commands

| Command |
Description | Ports |
|---------|-------------|-------|
| `yarn ultra` | **Main (Recommended)** - Both frontend + backend | 3000, 8080 |
| `yarn dev` | Next.js development only | 3000 |
| `yarn ultra:platform` | Dual platform (Main + Frontend) | 3000, 3111 |
| `yarn ultra:dev` | Ultra SaaS launcher | Various |

## Core API Endpoints

### 🔥 UltraCom Backend (Port 8080)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Basic health check |
| GET | `/manager/health` | AI Manager status |
| POST | `/manager/handle` | AI Manager processing |
| GET | `/api/alba-network` | Alba Network status |
| POST | `/api/alba-network` | Alba Network processing |
| GET | `/api/system-layers` | System layers monitoring |

### 🌐 Next.js Frontend APIs (Port 3000)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/ai-manager` | AI Manager interface |
| GET/POST | `/api/chat/smart` | Smart chat system |
| GET/POST/PUT | `/api/neural` | Neural network processing |
| GET/POST/DELETE | `/api/neural-search` | Neural search operations |
| GET | `/api/guardian` | Security monitoring |
| GET/POST | `/api/agi-advanced` | Advanced AGI processing |
| GET/POST | `/api/quantum-processing` | Quantum operations |
| GET/POST | `/api/ultra-industrial` | Industrial systems |
| GET/POST | `/api/system/real` | Real system data |
| GET/POST | `/api/lora-mesh` | LoRa mesh network |
| GET/POST | `/api/web-services` | Web services |

## Test Your APIs

### Quick Health Check
```bash
# Backend health
curl http://localhost:8080/health

# Alba Network status  
curl http://localhost:8080/api/alba-network

# AI Manager health
curl http://localhost:8080/manager/health
```

### Frontend API Tests
```bash
# Guardian security
curl http://localhost:3000/api/guardian

# Neural network status
curl http://localhost:3000/api/neural

# AI Manager frontend
curl http://localhost:3000/api/ai-manager
```

## Real Data Policy ⚠️
- **100% Real Data** - Zero fake/mock responses
- **Live System Metrics** - Actual CPU, memory, network data
- **Real API Integration** - Alba Network, ASI Engine, OpenAI
- **Authentic Processing** - No simulations or random data

## Key Features
- 🔒 **Guardian Security**: Real browser-based monitoring
- 🌐 **Alba Network**: Live external API integration
- ⚡ **System Layers**: Multi-layer architecture tracking  
- 🤖 **AI Manager**: Complete autonomous processing
- 🧠 **Neural Processing**: Advanced AI capabilities
- 🏭 **Industrial Systems**: Production-ready APIs
