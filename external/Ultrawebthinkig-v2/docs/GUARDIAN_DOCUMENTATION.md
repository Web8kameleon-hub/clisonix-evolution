# Guardian Security System v8.0.0

🛡️ **Industrial-grade DDoS Protection & Threat Monitoring System**

Guardian është sistemi më i avancuar i mbrojtjes për platformën EuroWeb, i projektuar për të mbrojtur aplikacionet industriale nga sulmet e ndryshme kibernetike.

## 🚀 Karakteristikat Kryesore

### 🔒 Mbrojtja e Avancuar
- **DDoS Protection**: Mbrojtje në kohë reale nga sulmet e shërbimit të mohuar
- **Rate Limiting**: Kontroll i inteligjent i frekuencës së kërkesave
- **IP Blacklisting**: Bllokimi automatik dhe manual i IP-ve keqdashëse
- **Geo-blocking**: Bllokimi i trafikut nga shtete të caktuara

### 🕵️ Zbulimi i Kërcënimeve
- **SQL Injection**: Zbulim i tentativave të injektimit SQL
- **XSS Detection**: Mbrojtje nga sulmet Cross-Site Scripting
- **Path Traversal**: Parandalimi i aksesit të paautorizuar në fajlla
- **Suspicious User Agents**: Identifikimi i agjentëve keqdashës

### 📊 Monitorimi i Avancuar
- **Real-time Dashboard**: Panel kontrolli në kohë reale
- **Threat Analytics**: Analiza e detajuar e kërcënimeve
- **Performance Metrics**: Metrika të performancës së sistemit
- **Alert System**: Sistem paralajmërimesh të automatizuara

## 🛠️ Instalimi dhe Konfigurimi

### Instalimi Bazë

```typescript
import { Guardian } from './backend/guardian/Guardian';

// Krijimi i instancës së Guardian
const guardian = new Guardian({
  maxRequestsPerMinute: 100,
  maxPayloadSize: 512000, // 500KB
  blockDuration: 3600000, // 1 orë
  enableGeoBlocking: true,
  blockedCountries: ['CN', 'RU', 'KP']
});

// Integrimi në Express
app.use(guardian.middleware());
```

### Konfigurimi i Avancuar

```typescript
const guardian = new Guardian({
  // Rate Limiting
  maxRequestsPerMinute: 50,
  rateLimitWindowMs: 60000,
  maxConnections: 1000,
  
  // Payload Control
  maxPayloadSize: 1024000, // 1MB
  
  // Security Settings
  blockDuration: 7200000, // 2 orë
  enableGeoBlocking: true,
  blockedCountries: ['CN', 'RU', 'KP', 'IR'],
  
  // Suspicious Patterns
  suspiciousUserAgents: [
    /python|curl|wget|scanner|bot|crawler/i,
    /sqlmap|nikto|nmap|masscan/i,
    /burp|zap|metasploit/i
  ],
  
  // Logging
  logPath: './logs/guardian.log',
  blocklistPath: './data/blocklist.json'
});
```

## 📚 API Reference

### Guardian Class

#### Konstruktori
```typescript
new Guardian(config?: Partial<GuardianConfig>)
```

#### Metodat Kryesore

##### `middleware()`
Kthen middleware-in e Express për mbrojtjen e aplikacionit.

```typescript
app.use(guardian.middleware());
```

##### `getStats()`
Kthen statistikat aktuale të Guardian.

```typescript
const stats = guardian.getStats();
console.log(stats.totalRequests, stats.blockedRequests);
```

##### `getThreatLogs(limit?)`
Kthen log-et e kërcënimeve të fundit.

```typescript
const threats = guardian.getThreatLogs(50);
```

##### `getDashboard()`
Kthen të dhënat e plota për dashboard.

```typescript
const dashboard = guardian.getDashboard();
```

##### `manualBlockIP(ip, reason)`
Bllokon manualisht një IP.

```typescript
guardian.manualBlockIP('192.168.1.100', 'Malicious activity detected');
```

##### `manualUnblockIP(ip)`
Heq bllokimin e një IP-je.

```typescript
guardian.manualUnblockIP('192.168.1.100');
```

##### `setActive(active)`
Aktivizon ose deaktivizon Guardian.

```typescript
guardian.setActive(false); // Deaktivizon
guardian.setActive(true);  // Aktivizon
```

## 🎯 Përdorimi në Praktikë

### Integrimi në Next.js

```typescript
// pages/api/guardian/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { guardian } from '../../../backend/guardian/Guardian';

export async function GET() {
  const dashboard = guardian.getDashboard();
  return NextResponse.json({ success: true, data: dashboard });
}

export async function POST(request: NextRequest) {
  const { action, ip, reason } = await request.json();
  
  switch (action) {
    case 'block':
      guardian.manualBlockIP(ip, reason);
      break;
    case 'unblock':
      guardian.manualUnblockIP(ip);
      break;
  }
  
  return NextResponse.json({ success: true });
}
```

### Dashboard Component

```typescript
import GuardianDashboard from '../components/GuardianDashboard';

export default function SecurityPage() {
  return (
    <div>
      <h1>Security Dashboard</h1>
      <GuardianDashboard />
    </div>
  );
}
```

## 🔧 Konfigurimi i Avancuar

### Environment Variables

```bash
# .env
GUARDIAN_MAX_REQUESTS=100
GUARDIAN_BLOCK_DURATION=3600000
GUARDIAN_LOG_LEVEL=info
GUARDIAN_ENABLE_GEO_BLOCKING=true
GUARDIAN_BLOCKED_COUNTRIES=CN,RU,KP,IR
```

### Docker Integration

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package.json yarn.lock .yarnrc.yml ./
COPY .yarn .yarn
RUN yarn install --immutable --production

# Krijoni direktoriet për logs dhe data
RUN mkdir -p logs data

COPY . .
EXPOSE 3000

CMD ["yarn", "start"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: euroweb-with-guardian
spec:
  replicas: 3
  selector:
    matchLabels:
      app: euroweb
  template:
    metadata:
      labels:
        app: euroweb
    spec:
      containers:
      - name: euroweb
        image: euroweb:latest
        ports:
        - containerPort: 3000
        env:
        - name: GUARDIAN_MAX_REQUESTS
          value: "200"
        - name: GUARDIAN_ENABLE_GEO_BLOCKING
          value: "true"
        volumeMounts:
        - name: guardian-logs
          mountPath: /app/logs
        - name: guardian-data
          mountPath: /app/data
      volumes:
      - name: guardian-logs
        emptyDir: {}
      - name: guardian-data
        persistentVolumeClaim:
          claimName: guardian-data-pvc
```

## 📊 Monitorimi dhe Alertet

### Prometheus Metrics

Guardian eksporton metrika për Prometheus:

```bash
# Metrikat e disponueshme
guardian_total_requests_total
guardian_blocked_requests_total
guardian_response_time_histogram
guardian_active_connections_gauge
guardian_system_health_gauge
```

### Grafana Dashboard

Konfigurimi i dashboard në Grafana:

```json
{
  "dashboard": {
    "title": "Guardian Security Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(guardian_total_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Block Rate",
        "type": "graph", 
        "targets": [
          {
            "expr": "rate(guardian_blocked_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

## 🧪 Testimi

### Unit Tests

```bash
yarn test guardian
```

### Load Testing

```bash
# Testimi me Artillery
artillery run tests/load/guardian-stress.yml
```

### Security Testing

```bash
# Testimi i mbrojtjes SQL Injection
curl -X POST "http://localhost:3000/api/test" \
  -H "Content-Type: application/json" \
  -d '{"query": "'; DROP TABLE users; --"}'

# Testimi i mbrojtjes XSS
curl -X GET "http://localhost:3000/search?q=<script>alert(1)</script>"

# Testimi i Rate Limiting
for i in {1..150}; do
  curl "http://localhost:3000/api/test" &
done
```

## 🚨 Alertet dhe Notifications

### Slack Integration

```typescript
// Web8 Proactive Polling Configuration
const guardian = new Guardian({
  web8ProactivePolling: true,
  pollingEndpoint: process.env.WEB8_POLLING_ENDPOINT,
  alertThreshold: {
    requestRate: 1000, // requests/minute
    blockRate: 50,     // blocked/minute
    errorRate: 10      // errors/minute
  }
});
```

### Email Alerts

```typescript
// Konfigurimi i email alerts
const guardian = new Guardian({
  emailConfig: {
    smtp: process.env.SMTP_SERVER,
    from: 'security@euroweb.com',
    to: ['admin@euroweb.com', 'security@euroweb.com']
  }
});
```

## 📈 Performance Tuning

### Optimizimi i Memorjes

```typescript
// Konfigurimi për aplikacione me trafik të lartë
const guardian = new Guardian({
  maxRequestsPerMinute: 1000,
  rateLimitWindowMs: 30000, // Reduktimi i dritares
  maxThreatLogs: 500,       // Reduktimi i log-eve në memorie
  cleanupInterval: 60000    // Pastrimi më i shpeshtë
});
```

### Database Integration

```typescript
// Integrimi me Redis për skalabilitet
const guardian = new Guardian({
  redisConfig: {
    host: 'redis.euroweb.com',
    port: 6379,
    db: 0
  },
  useRedisForRateLimit: true,
  useRedisForBlocklist: true
});
```

## 🔐 Siguria dhe Compliance

### GDPR Compliance

Guardian respekton rregullat e GDPR:
- Log-et e IP-ve nuk ruhen më shumë se sa nevojitet
- Përdoruesit mund të kërkojnë fshirjen e të dhënave
- Enkriptimi i të dhënave sensitive

### Security Headers

Guardian vendos automatikisht header-at e sigurisë:

```http
X-Guardian-Status: Active
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

## 🐛 Troubleshooting

### Problemet e Zakonshme

#### 1. Guardian bllokon përdorues legimitë
```typescript
// Rritni limitin e kërkesave
const guardian = new Guardian({
  maxRequestsPerMinute: 200, // Nga 100
  rateLimitWindowMs: 90000   // Nga 60000
});
```

#### 2. Performance i ngadalshëm
```typescript
// Aktivizoni optimizimin
const guardian = new Guardian({
  enableOptimizations: true,
  asyncLogging: true,
  batchSize: 100
});
```

#### 3. Log files të mëdha
```bash
# Konfiguroni log rotation
echo "0 0 * * * /usr/bin/logrotate /etc/logrotate.d/guardian" | crontab -
```

### Debug Mode

```typescript
const guardian = new Guardian({
  debug: true,
  verboseLogging: true,
  logLevel: 'debug'
});
```

## 📞 Kontakti dhe Suporti

- **Author**: Ledjan Ahmati
- **Email**: dealsjona@gmail.com
- **Telegram**: @ledijonbibaj
- **Version**: 8.0.0
- **License**: MIT

## 🔄 Update dhe Maintenance

### Automatic Updates

```bash
# Përditësimi i Guardian
yarn upgrade @euroweb/guardian

# Restart i sistemit
pm2 restart euroweb-app
```

### Backup dhe Recovery

```bash
# Backup i konfigurimit
tar -czf guardian-backup-$(date +%Y%m%d).tar.gz logs/ data/

# Recovery
tar -xzf guardian-backup-20241201.tar.gz
```

---

**© 2024 EuroWeb Platform - Guardian Security System v8.0.0**
