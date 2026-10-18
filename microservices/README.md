# EuroWeb Microservices 🚀

Arkitekturë microservices për platformën EuroWeb - Shërbime të pavarura pa konflikte.

## 📦 Struktura

```text
microservices/
├── gateway/        # API Gateway (Port 4000)
├── auth/           # Authentication Service (Port 4001)
├── agi/            # AGI Intelligence Service (Port 4002)
├── data/           # Data Processing Service (Port 4003)
├── realtime/       # WebSocket Service (Port 4004)
└── shared/         # Shared utilities & config
```

## 🚀 Portet

| Service   | Port | Përshkrimi                        |
|-----------|------|-----------------------------------|
| Gateway   | 4000 | API Gateway - Pika hyrëse kryesore|
| Auth      | 4001 | Autentifikimi & JWT               |
| AGI       | 4002 | Artificial General Intelligence   |
| Data      | 4003 | Data storage & processing         |
| Realtime  | 4004 | WebSocket real-time communication |

## 🛠️ Instalimi

```bash
cd microservices
npm install
```

## ▶️ Ekzekutimi

### Të gjitha shërbimet njëkohësisht

```bash
npm run dev:all
```

### Shërbime individuale

```bash
npm run dev:gateway   # Gateway only
npm run dev:auth      # Auth only
npm run dev:agi       # AGI only
npm run dev:data      # Data only
npm run dev:realtime  # Realtime only
```

## 🐳 Docker

```bash
docker-compose up -d
```

## 📡 API Endpoints

### Gateway (localhost:4000)

- `GET /health` - Health check
- `GET /services` - Service discovery
- `GET /api/auth/*` - Proxy to Auth
- `GET /api/agi/*` - Proxy to AGI
- `GET /api/data/*` - Proxy to Data

### Auth (localhost:4001)

- `POST /register` - Regjistro përdorues
- `POST /login` - Kyçu
- `POST /refresh` - Rifresko token
- `GET /me` - Merr përdoruesin aktual
- `POST /logout` - Dil

### AGI (localhost:4002)

- `GET /status` - AGI status
- `POST /process` - Proceso me AGI (auth required)
- `POST /query` - Query AGI
- `GET /layers` - Info për shtresat
- `GET /metrics` - Real-time metrics

### Data (localhost:4003)

- `POST /store` - Ruaj data
- `GET /store/:id` - Merr data
- `PUT /store/:id` - Update data
- `DELETE /store/:id` - Fshi data
- `GET /store` - Lista e të dhënave
- `POST /search` - Kërko
- `POST /batch` - Batch operations

### Realtime (ws://localhost:4004)

WebSocket messages:

- `join` - Hyj në kanal
- `leave` - Dil nga kanali
- `message` - Dërgo mesazh
- `ping/pong` - Heartbeat

## 🔐 Autentifikimi

Përdor JWT tokens. Shembull:

```javascript
// Register
const res = await fetch('http://localhost:4000/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'test@example.com', password: 'secret123' })
});

const { token } = await res.json();

// Use token
const agi = await fetch('http://localhost:4000/api/agi/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({ input: 'Analyze this data' })
});
```

## ⚡ WebSocket

```javascript
const ws = new WebSocket('ws://localhost:4004');

ws.onopen = () => {
  // Join a channel
  ws.send(JSON.stringify({ type: 'join', channel: 'updates' }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Message:', data);
};

// Send message
ws.send(JSON.stringify({
  type: 'message',
  channel: 'updates',
  data: { content: 'Hello!' }
}));
```

## 🏗️ Pse Microservices?

1. **Pa konflikte** - Çdo shërbim ka portin e vet
2. **Skalim i pavarur** - Skaloni vetëm ato që duhen
3. **Zhvillim i pavarur** - Ekipe të ndryshme punojnë pa pengesa
4. **Fault isolation** - Nëse bie një, të tjerat vazhdojnë
5. **Teknologji të ndryshme** - Çdo shërbim mund të përdorë stack të ndryshëm

---

Made with ❤️ for EuroWeb Platform
