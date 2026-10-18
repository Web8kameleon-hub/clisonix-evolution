# Guardian Engine Integration

## Përshkrimi

Guardian Engine është një sistem i integruar i mbrojtjes kundër sulmeve DDoS dhe monitorimit të sigurisë së rrjetit për platformën EuroWeb. Ky sistem ofron mbrojtje në kohë reale dhe analiza të detajuara të aktiviteteve të dyshimta.

## Karakteristikat

### 🛡️ Mbrojtje në Kohë Reale
- Monitorim automatik i të gjitha kërkesave HTTP
- Zbulim i aktiviteteve të dyshimta
- Bllokimi automatik i IP-ve të rrezikshme
- Ruajtja e logeve të sigurisë

### 📊 Monitoring dhe Raportim
- Dashboard interaktiv për statusin e sistemit
- Statistika të detajuara të kërkesave
- Lista e IP-ve të bllokotuara
- Llogari në kohë reale të aktiviteteve

### ⚙️ Konfigurimi
- Madhësia maksimale e payload: 512KB
- Norma maksimale e kërkesave: 100 req/min
- Kohëzgjatja e bllokimit: 1 orë
- Zbulimi i User Agent të dyshimtë

## Integrimi

### Backend Integration

Guardian Engine është integruar plotësisht në backend server:

```typescript
// Middleware aplikohet për të gjitha kërkesat
app.use(guardianMiddleware);

// API endpoints për monitoring
app.get('/api/guardian/dashboard', guardianDashboard);
app.get('/api/guardian/logs', guardianLogsHandler);
app.get('/api/guardian/stats', guardianStatsHandler);
```

### Frontend Integration

Komponentet e frontend-it për monitoring:

- `GuardianMonitor.tsx` - Dashboard kryesor
- `AGIXForm.tsx` - Formular për analizë mjekësore
- `AGIXResults.tsx` - Shfaqje e rezultateve

### API Endpoints

#### Guardian Status
```
GET /api/guardian/status
```

#### Guardian Dashboard
```
GET /api/guardian/dashboard
```

#### Guardian Logs
```
GET /api/guardian/logs?level=critical&limit=100
```

#### Guardian Stats
```
GET /api/guardian/stats
```

#### AGIXmed Analysis
```
POST /api/agixmed/analyze
Content-Type: application/json

{
  "symptoms": "përshkrimi i simptomave"
}
```

## Përdorimi

### Startimi i Sistemit

```bash
# Vetëm frontend
yarn dev

# Vetëm backend
yarn dev:backend

# Frontend dhe backend së bashku
yarn dev:full
```

### Konfigurimi

Kopjo `.env.example` në `.env` dhe ndrysho vlerat sipas nevojës:

```bash
cp .env.example .env
```

### Testimi

```bash
# Type checking
yarn type-check

# Linting
yarn lint

# Tests
yarn test
```

## Struktura e Fileve

```
backend/
├── ddos/
│   ├── guardian.ts      # Guardian Engine core
│   ├── middleware.ts    # Express middleware
│   └── tsconfig.json    # TypeScript config
└── server.ts            # Main server

components/
├── AGIXmed/
│   ├── AGIXForm.tsx     # Medical analysis form
│   └── AGIXResults.tsx  # Results display
├── GuardianMonitor.tsx  # Security dashboard
└── ui/                  # Reusable UI components

blocked/                 # Blocked IPs storage
logs/                   # Application logs
```

## Siguria

- Të gjitha IP-të e bllokotuara ruhen me hash SHA-256
- Llogjet e sigurisë ruhen lokalisht dhe në cloud
- Enkriptimi i të dhënave në transit dhe në storage
- Kontroll i aksesit bazuar në role

## Maintenance

### Log Rotation
Llogjet rrotullohen automatikisht çdo 30 ditë.

### Database Cleanup
Të dhënat e vjetra pastrohen automatikisht bazuar në konfigurim.

### Backup
Backup automatik i konfigurimeve dhe logeve.

## Support

Për pyetje ose probleme:
- Email: dealsjona@gmail.com
- Autor: Ledjan Ahmati
- Version: 8.0.0 Industrial
- License: MIT
