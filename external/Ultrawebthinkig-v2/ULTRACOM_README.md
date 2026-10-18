# 🚀 UltraCom Communication System

Complete **Client ↔ Technician** real-time communication system with FastAPI backend and React frontend.

## 🏗️ Architecture

```
Klienti 👤 ─┐
            ├──► WebSocket Gateway ───► Tekniku 🧑‍🔧
            │                            ▲
            │                            │
            └──► AGI Core (përgjigje automatike)
```

### Backend (FastAPI + Python)
- **WebSocket** real-time communication
- **JWT** authentication with role-based access
- **SQLAlchemy** database with SQLite/PostgreSQL
- **Role system**: Client, Technician, Admin
- **REST API** fallback for reliability

### Frontend (React + TypeScript)
- **Web8 Motion** animated UI components
- **Real-time** message updates via WebSocket
- **Auto-reconnection** with exponential backoff
- **Responsive design** with professional styling

## 🚀 Quick Start

### 1. Start Backend Server

```powershell
# Run the PowerShell launcher (Windows)
.\start-ultracom.ps1
```

**Or manually:**
```bash
cd ultracom
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or .\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
cp .env.example .env
python start.py
```

### 2. Frontend Integration

```typescript
import { UltraComChat } from '../components/UltraComChat';

// Use the component
<UltraComChat
  baseUrl="http://localhost:8080"
  token="your-jwt-token"
  room="support-ACME-42"
  userRole="client"
  userName="client-007"
/>
```

## 🔐 Authentication

### Generate JWT Tokens

```python
from app.auth import create_token

# Client token
client_token = create_token("your-secret", "client-007", "client")

# Technician token  
tech_token = create_token("your-secret", "tech-ops-1", "technician")

# Admin token
admin_token = create_token("your-secret", "admin-ultra", "admin")
```

### Token Usage

**WebSocket:**
```javascript
const ws = new WebSocket('ws://localhost:8080/chat/ws/support-ACME-42?token=' + jwt_token);
```

**REST API:**
```javascript
fetch('/chat/history?room=support-ACME-42', {
  headers: { 'x-auth-token': jwt_token }
});
```

## 📡 API Endpoints

### WebSocket
- `ws://localhost:8080/chat/ws/{room}` - Real-time chat

### REST API
- `GET /health` - System health check
- `POST /chat/send` - Send message via REST
- `GET /chat/history` - Get message history

### Message Format

**Send Message (WebSocket):**
```json
{ "text": "Përshëndetje! Si mund t'ju ndihmoj?" }
```

**Receive Message:**
```json
{
  "type": "message",
  "data": {
    "id": 123,
    "room": "support-ACME-42", 
    "role": "technician",
    "sender": "tech-ops-1",
    "text": "U rregullua sensori Gamma.",
    "ts": "2025-10-21T10:10:10Z"
  }
}
```

## 👥 Role System

### Client (`client`)
- Can only send messages as client role
- Can receive messages from technicians/admins
- Limited to their own messages

### Technician (`technician`) 
- Can send messages as any role
- Full access to chat history
- Can impersonate system messages

### Admin (`admin`)
- Complete system access
- Can send messages as any role
- Full administrative privileges

## 🎨 Frontend Components

### UltraComChat Component

```typescript
interface UltraComChatProps {
  baseUrl: string;          // Backend URL
  token: string;            // JWT token
  room: string;             // Chat room ID
  userRole: 'client' | 'technician' | 'admin';
  userName: string;         // User identifier
  className?: string;       // CSS classes
}
```

### Features
- ✅ **Animated messages** with Web8 Motion
- ✅ **Role-based styling** (color coding)
- ✅ **Real-time typing** indicators  
- ✅ **Auto-scroll** to new messages
- ✅ **Connection status** indicators
- ✅ **Error handling** with user feedback

## 🔧 Configuration

### Environment Variables (`.env`)

```env
JWT_SECRET=change_me_ultracom_super_secret
DB_URL=sqlite+aiosqlite:///./ultracom.db
CORS_ORIGINS=*
```

### Production Setup

```env
JWT_SECRET=your-production-secret-key
DB_URL=postgresql+asyncpg://user:pass@host:5432/ultracom
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## 🐳 Docker Deployment

### Development
```bash
docker build -t ultracom-backend .
docker run -p 8080:8080 ultracom-backend
```

### Production (Docker Compose)
```yaml
version: "3.9"
services:
  backend:
    build: ./ultracom
    ports: ["8080:8080"]
    env_file: .env.prod
    depends_on: [postgres, redis]
  
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: ultracom
      POSTGRES_USER: ultra
      POSTGRES_PASSWORD: ultra
```

## 🛡️ Security Features

- **JWT Authentication** with expiration
- **Role-based access control**
- **CORS protection** 
- **Input validation** with Pydantic
- **SQL injection prevention** with SQLAlchemy
- **WebSocket security** with token validation

## 📊 Monitoring & Logging

### Health Check
```bash
curl http://localhost:8080/health
```

Response:
```json
{
  "ok": true,
  "service": "UltraCom", 
  "ts": "2025-10-21T10:10:10Z"
}
```

### Message History
```bash
curl -H "x-auth-token: YOUR_JWT" \
     "http://localhost:8080/chat/history?room=support-ACME-42&limit=20"
```

## 🚀 Production Extensions

### Redis for Scaling
```python
# Multi-instance WebSocket scaling
class ConnectionManager:
    async def start_bus(self):
        self.redis = await aioredis.from_url(REDIS_URL)
        # Publish messages across instances
```

### PostgreSQL + Vector Search
```python
# Add AI-powered message search
class Message(Base):
    embedding: Mapped[str] = mapped_column(String(3000))  # Vector embeddings
```

### File Storage (MinIO)
```python
# Handle file attachments
def upload_file(file_data: bytes) -> str:
    return S3.put_object(Bucket="ultracom", Body=file_data)
```

## 🔥 Usage Examples

### Initialize Client
```typescript
const client = new UltraComClient({
  baseUrl: 'http://localhost:8080',
  token: 'your-jwt-token',
  room: 'support-ACME-42',
  onMessage: (msg) => console.log('New message:', msg),
  onConnect: () => console.log('Connected!'),
});

await client.connect();
client.sendMessage('Përshëndetje!');
```

### Send System Alert (REST)
```bash
curl -X POST http://localhost:8080/chat/send \
 -H "Content-Type: application/json" \
 -H "x-auth-token: TECHNICIAN_JWT" \
 -d '{
  "room": "support-ACME-42",
  "role": "system", 
  "sender": "AGI-Core",
  "text": "ALERT: Temperatura në Gamma: 33.7°C"
}'
```

## 📝 Development

### Add New Features
1. **Backend:** Add routes in `app/routers/`
2. **Database:** Update models in `app/models.py`  
3. **Frontend:** Extend components in `components/`
4. **Authentication:** Modify `app/auth.py`

### Testing
```bash
# Run backend tests
cd ultracom
python -m pytest

# Test WebSocket connection
wscat -c "ws://localhost:8080/chat/ws/test-room?token=YOUR_JWT"
```

---

## 🎯 Next Steps

1. **Start the system:** `.\start-ultracom.ps1`
2. **Open frontend:** Navigate to your Next.js app
3. **Test communication:** Send messages between client/technician
4. **Deploy to production:** Use Docker Compose setup
5. **Scale with Redis:** Add multi-instance support

**Ready for production deployment! 🚀**
