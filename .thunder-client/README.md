# Thunder Client Collection - Clisonix Cloud

## ⚡ Si ta përdorësh

### 1. Aktivizo Git Sync

1. Hap Thunder Client (ikona ⚡ në sidebar)
2. Click ⚙️ Settings
3. Enable **"Save To Workspace"**
4. Folder: `.thunder-client`

### 2. Zgjidh Environment

- **Clisonix Production**: Server live (46.225.14.83:8000)
- **Clisonix Local**: localhost:8000

### 3. APIs të disponueshme

| Folder | Endpoints |
| ------ | --------- |
| 📋 Health & Status | `/health`, `/status`, `/api/system-status` |
| 🧠 ASI Trinity | `/asi/status`, `/asi/health`, `/asi/alba/metrics` |
| 🌊 Ocean AI | `/api/ocean/status`, `/api/ocean/session/create`, `/api/ocean/labs/execute` |
| 💳 Monetization | `/api/v1/plans`, `/api/v1/register`, `/api/v1/checkout`, `/api/v1/entitlements/*`, `/api/v1/chat` |
| 📊 Excel | `/api/excel/health`, `/api/excel/generate` |
| 💳 Billing | `/billing/stripe/payment-intent`, `/billing/paypal/order` |
| 🔬 Neural | `/neural-symphony`, `/api/ask` |
| 🏭 Content Factory | `/analyze`, `/process`, `/publish`, `/pipeline` |

## 🔐 Environment Variables

- `base_url` - Server URL
- `billing_url` - Billing Core URL (default `:8095`)
- `ocean_url` - Ocean Core URL (default `:8030`)
- `auth_token` - JWT Token (nëse nevojitet)
- `api_key` - API Key (nëse nevojitet)

## ✅ Rendi Profesional i Testimit (Thunder)

1. `Billing Core Health`
2. `List Plans`
3. `Register + Issue API Key` (kopjo `api_key` në environment)
4. `Resolve Entitlements (Header)`
5. `Ocean v1 Chat (with API Key)`
6. `Ocean v1 Query (with API Key)`

## 📦 Import Postman Collection (Opsionale)

Nëse dëshiron të importosh koleksionin e plotë Postman:

1. Click "..." → Import
2. Zgjidh `clisonix-ultra-mega-collection.json`
3. Thunder Client do ta konvertojë automatikisht

---

**Falas. Pa limit. Direkt në VS Code.** 🚀
