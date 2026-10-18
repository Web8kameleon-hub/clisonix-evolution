# 📚 ULTRA BACKEND API DOCUMENTATION

## 🚀 Server Infrastructure

### Primary Servers
1. **Frontend (Next.js)**: `http://localhost:3000`
2. **Backend (UltraCom FastAPI)**: `http://localhost:8080`
3. **Development**: `yarn ultra` (starts both servers)

### Available Startup Commands
```bash
# Main command (recommended)
yarn ultra           # Starts both frontend (3000) + backend (8080)
yarn dev            # Next.js development server only
yarn build          # Build production version
yarn start          # Start production server

# Alternative ultra commands
yarn ultra:dev      # Ultra SaaS launcher
yarn ultra:main     # Next.js main only
yarn ultra:frontend # ASI SaaS frontend (port 3111)
yarn ultra:platform # Both main + frontend platforms
```

---

## 🏗️ BACKEND API ENDPOINTS

### 🔥 UltraCom FastAPI (Port 8080)

#### Health & Status
```http
GET  /health                    # Basic health check
GET  /manager/health           # AI Manager system status
POST /manager/handle           # AI Manager processing
GET  /api/system-layers        # System layers monitoring
```

#### Alba Network Integration
```http
GET  /api/alba-network         # Alba Network status
POST /api/alba-network         # Alba Network processing
```

---

### 🌐 Next.js API Routes (Port 3000)

#### 🤖 AI & Chat Systems
```http
GET  /api/ai-manager           # AI Manager status
POST /api/ai-manager           # AI Manager processing
GET  /api/chat/smart           # Smart chat status
POST /api/chat/smart           # Smart chat processing
GET  /api/neural               # Neural network status
POST /api/neural               # Neural processing
PUT  /api/neural               # Neural updates
```

#### 🔍 Search & Intelligence
```http
GET  /api/neural-search        # Neural search status
POST /api/neural-search        # Perform neural search
DELETE /api/neural-search      # Delete search data
GET  /api/web-services         # Web services status
POST /api/web-services         # Web services processing
```

#### 🛡️ Security & Guardian
```http
GET  /api/guardian             # Guardian security dashboard
GET  /api/security/shield      # Security shield status
```

#### ⚡ Advanced Processing
```http
GET  /api/agi-advanced         # AGI advanced status
POST /api/agi-advanced         # AGI advanced processing
GET  /api/quantum-processing   # Quantum processing status
POST /api/quantum-processing   # Quantum operations
```

#### 🏭 Industrial & Systems
```http
GET  /api/ultra-industrial     # Ultra industrial status
POST /api/ultra-industrial     # Industrial processing
GET  /api/system/real          # Real system data
POST /api/system/real          # System operations
```

#### 📡 Network & Communication
```http
GET  /api/lora-mesh           # LoRa mesh network status
POST /api/lora-mesh           # LoRa mesh operations
GET  /api/websocket           # WebSocket connections
```

#### 🧬 Science & Research
```http
GET  /api/life-sciences-hub   # Life sciences data
GET  /api/web8/intelligence   # Web8 intelligence
```

#### 📊 Project Management
```http
POST /api/projects/create     # Create new project
GET  /api/revolution/status   # Revolution status
```

#### 🌍 Cultural & Hub Systems
```http
GET  /api/cultural-hub        # Cultural hub data
GET  /api/alba-asi-hub        # Alba ASI hub integration
```

#### 🔐 Authentication
```http
POST /api/auth                # Authentication processing
```

#### 📈 Analytics & Data
```http
GET  /pages/api/real-analytics # Real analytics data
GET  /pages/api/aggregate      # Aggregated data
```

---

## 🏷️ REQUEST/RESPONSE EXAMPLES

### Alba Network Integration
```javascript
// GET /api/alba-network
{
  "status": "ACTIVE",
  "network": "Alba Network",
  "connections": 12,
  "timestamp": "2025-10-24T..."
}

// POST /api/alba-network
{
  "message": "Process data",
  "clientId": "client-001"
}
```

### Guardian Security
```javascript
// GET /api/guardian
{
  "activeConnections": 15,
  "openPorts": [3000, 8080, 443],
  "memoryUsage": 45,
  "cpuUsage": 30,
  "securityAlerts": [...]
}
```

### AI Manager
```javascript
// POST /manager/handle
{
  "message": "Analyze system",
  "clientId": "client-001"
}

// Response
{
  "response": "Analysis complete",
  "processed": true,
  "timestamp": "..."
}
```

---

## 🔧 STARTUP CONFIGURATIONS

### yarn ultra (Recommended)
- Starts Next.js frontend on port 3000
- Starts UltraCom FastAPI on port 8080
- Auto-reload enabled for both
- CORS configured for cross-origin requests

### yarn ultra:dev
- Ultra SaaS launcher with enhanced features
- Advanced development environment
- Integrated workspace management

### yarn ultra:platform
- Dual platform setup (Main + Frontend)
- Port 3000 (main) + Port 3111 (frontend)
- Complete ecosystem deployment

### yarn dev / build / start
- Standard Next.js commands
- Production-ready deployment options
- Optimized for performance

---

## 🎯 REAL DATA POLICY

**⚠️ ZERO FAKE DATA POLICY**
- All endpoints return 100% real data
- No mock responses or simulated data
- Real system metrics and actual processing
- Authentic API integrations only

---

## 🔗 Integration Points

### External APIs
- **Alba Network**: Real-time integration
- **ASI Engine**: Advanced AI processing  
- **OpenMind Client**: Cognitive services
- **Ollama**: Local AI models (port 11434)
- **OpenAI API**: Cloud AI services

### Internal Systems
- **Guardian Security**: Browser-based real monitoring
- **System Layers**: Multi-layer architecture tracking
- **Neural Networks**: Advanced processing pipelines
- **Quantum Processing**: Quantum computing interfaces

---

## 📱 Frontend Integration

### Key Pages
- `/agi-tunnel` - AGI processing interface
- `/system-layers` - System monitoring dashboard  
- `/guardian-demo` - Security monitoring
- `/alba-asi-hub` - Alba/ASI integration
- `/api-gateway` - API management interface

### Real-time Features
- WebSocket connections for live updates
- Performance monitoring with real metrics
- Layer activity tracking across systems
- Security threat monitoring and alerts

---

**🔥 All APIs are production-ready with zero simulation - 100% real data processing!**
