# 🧠 Clisonix Cloud

Industrial Backend & Payment System

## Industrial-Grade FastAPI Backend with Real Business Integration

## 📧 Contact & Support

- **Email:** <clisonix@pm.me>
- **Support:** <clisonix@pm.me>
- **Website:** [clisonix.com](https://clisonix.com)

## 💰 Support This Project

**SEPA Bank Transfer:**

- **IBAN:** DE72 xxxx xxxx xxxx xxxx xx
- **BIC:** WELADEDxxxx
- **Account Holder:** Configured via secrets

**PayPal:**

- **Email:** Configured via secrets

> 💡 For real payment details, contact: <clisonix@pm.me>

---

**Business Information:**

- **Owner:** Ledjan Ahmati (Geschäftsführer / Inhaber)
- **Brand:** Clisonix
- **Registered Legal Entity:** ABA GmbH
- **Registration:** Amtsgericht Bochum HRB: 21069
- **SEPA IBAN:** `${SEPA_IBAN}` (Configured via secrets)
- **PayPal:** `${PAYPAL_EMAIL}` (Configured via secrets)
- **Data Policy:** Production credentials managed via secrets - See SECURITY.md

---

## 🚀 Real Industrial Features

### 🧠 AI Character Engines (ALBI/ALBA/JONA)

- **ALBI:** Advanced Learning & Brain Intelligence - Cognitive pattern analysis
- **ALBA:** Adaptive Learning & Brain Analysis - Real-time EEG processing  
- **JONA:** Joint Oscillatory Neural Analysis - Multi-modal signal correlation

### 🚀 LLM Inference Engines

- **Ollama:** Local LLM inference (llama3.1:8b) - CPU optimized
- **vLLM:** High-throughput GPU inference engine ([vllm.ai](https://vllm.ai)) - Requires NVIDIA GPU
- **Curiosity Ocean:** Hybrid multilingual AI assistant v8.0

### 🔬 ML/AI Stack

- **PyTorch:** Deep learning framework (CPU/CUDA)
- **Transformers:** Hugging Face models integration
- **Sentence-Transformers:** Semantic embeddings

### 💳 Payment System Integration

- **SEPA Payments:** Direct bank transfers with real IBAN validation
- **PayPal Integration:** Real business account processing
- **Stripe Checkout:** Subscription management with plan-based quotas
- **Webhook Processing:** Real-time payment verification

### 📊 Live System Monitoring

- **Real-time Metrics:** CPU, memory, disk, network monitoring with psutil
- **Health Scoring:** Industrial-grade system health algorithms
- **Performance Tracking:** Live efficiency and stability measurements
- **Process Monitoring:** Complete system process analysis

### 🔐 Authentication & Security

- **JWT Authentication:** Refresh token support with secure handling
- **Plan-Based Quotas:** Subscription tier restrictions
- **Rate Limiting:** Industrial middleware for API protection
- **CORS Security:** Production-ready cross-origin handling

---

## 🔐 Security

**⚠️ IMPORTANT: This project handles sensitive data and payment processing.**

### Getting Started Securely

1. **Never commit secrets** - Use `.secrets` file (see `.secrets.template`)
2. **Read SECURITY.md** - Comprehensive security guidelines
3. **Use Docker Secrets** - For production deployments
4. **Enable pre-commit hooks** - Prevent accidental secret exposure

```bash
# Setup secrets (first time only)
cp .secrets.template .secrets
# Edit .secrets with your real values

# Install security tools
cp scripts/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Scan for exposed secrets
python scripts/scan-secrets.py
```

### Security Resources

- 📖 **[SECURITY.md](SECURITY.md)** - Full security policy
- 🔍 **Secret Scanning** - Automated with GitHub Actions
- 🔐 **Secrets Management** - Docker secrets, Vault integration
- 🛡️ **Vulnerability Scanning** - Trivy + dependency monitoring

**Report security issues**: See [SECURITY.md](SECURITY.md#reporting-security-vulnerabilities)

---

## 🏗️ Architecture

Clisonix-cloud/
├── app/
│   ├── main.py              # Industrial FastAPI backend with live monitoring
│   ├── settings.py          # Configuration with business integration
│   ├── auth/                # JWT authentication system
│   ├── billing/            # SEPA/PayPal/Stripe payment processing
│   ├── middleware/         # Quota gate + security middleware
│   └── ...
├── worker/                 # Background job processing
├── scripts/               # Deployment and utility scripts
├── requirements.txt       # Industrial-grade dependencies
├── docker-compose.yml     # Multi-service orchestration
└── start_server.py        # Backend launcher script

---

## ⚡ Quick Start

### 1. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Or use the launcher (auto-installs)
python start_server.py
```

### 2. Start Industrial Backend

```bash
# Method 1: Use launcher script
python start_server.py

# Method 2: Direct uvicorn
uvicorn app.master:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access Industrial Backend

- **Backend:** <http://localhost:8000>
- **API Docs:** <http://localhost:8000/docs> (development only)
- **Health Check:** <http://localhost:8000/health>

---

## 🌟 Industrial Endpoints

### System Information

```bash
GET /                        # Complete system overview + business info
GET /health                  # Industrial health check with real metrics
GET /status                  # Full ecosystem status with performance data
GET /api/v1/info            # Complete API capabilities
```

### AI Character Engines  

```bash
GET /api/albi/info          # ALBI Intelligence Engine status
GET /api/alba/info          # ALBA Data Collector metrics
GET /api/jona/info          # JONA System Monitor details
GET /api/ecosystem/status   # Complete ecosystem overview
```

### Real Data Processing

```bash
POST /api/uploads/eeg/process    # Real EEG analysis (ALBI+ALBA engines)
POST /api/uploads/audio/process  # Real audio processing (JONA+ALBA engines)
```

### Payment Processing

```bash
POST /billing/create        # Create SEPA/PayPal payment
POST /billing/process/:id   # Process payment with real verification
GET /billing/payment/:id    # Payment status tracking
GET /billing/stats          # Payment system statistics
```

### Authentication

```bash
POST /auth/login           # JWT authentication
POST /auth/register        # User registration with plan assignment
GET /auth/me              # Current user information
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/Clisonix

# Redis Configuration  
REDIS_URL=redis://localhost:6379

# Payment Integration (Use .secrets file - see .secrets.template)
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}

# Business Configuration (NEVER commit real values)
BUSINESS_OWNER=${BUSINESS_OWNER}
BUSINESS_COMPANY=${BUSINESS_COMPANY}
SEPA_IBAN=${SEPA_IBAN}
PAYPAL_EMAIL=${PAYPAL_EMAIL}

# Security (Generate strong random keys)
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256

# System Settings
ENVIRONMENT=production
DEBUG=false
API_VERSION=1.0.0
```

---

## 🏭 Industrial Features

### Real System Monitoring

- **CPU Monitoring:** Real-time CPU usage with psutil
- **Memory Tracking:** Live memory consumption analysis
- **Disk Analytics:** Storage utilization monitoring
- **Network Metrics:** Connection and traffic analysis
- **Process Monitoring:** Complete system process tracking

### Payment System

- **SEPA Integration:** Enterprise bank account (configured via secrets)
- **PayPal Processing:** Business account integration (see SECURITY.md)
- **Stripe Subscriptions:** Plan-based quota management
- **Webhook Verification:** Secure payment status updates

### Data Processing

- **EEG Analysis:** Real neural signal processing (no mock data)
- **Audio Processing:** Industrial-grade audio analysis
- **Multi-modal Integration:** ALBI/ALBA/JONA engine coordination
- **Real-time Classification:** Live signal analysis and feedback

---

## 📈 Performance Metrics

### System Health Scoring

```python
# Industrial health algorithm
cpu_score = max(0, 100 - cpu_usage) * 0.3
memory_score = max(0, 100 - memory_usage) * 0.4  
uptime_score = min(30, uptime_hours) * 0.3
total_health = cpu_score + memory_score + uptime_score
```

### Live Ecosystem Tracking

- **ALBI Jobs:** Real processing job counter
- **ALBA Data Points:** Live data collection metrics  
- **JONA Alerts:** System monitoring alert handling
- **Payment Transactions:** Real business transaction tracking

---

## 🔒 Security & Compliance

### Authentication Security

- **JWT Tokens:** Secure authentication with refresh tokens
- **Plan Quotas:** Subscription-based API limiting
- **CORS Protection:** Production-ready cross-origin policies
- **Request Tracing:** Complete request ID tracking

### Payment Security

- **Webhook Verification:** Stripe signature validation
- **SEPA Compliance:** European payment standard compliance
- **PayPal Integration:** Business account secure processing
- **Transaction Logging:** Complete payment audit trails

---

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build and deploy full stack
docker-compose up -d

# Scale services
docker-compose up -d --scale worker=3

# Monitor logs
docker-compose logs -f api
```

### Services

- **API:** FastAPI backend with industrial monitoring
- **Worker:** Background job processing
- **PostgreSQL:** Production database
- **Redis:** Caching and session storage
- **MinIO:** S3-compatible file storage

---

## 📊 Business Integration

### Real Business Data

```json
{
  "owner": "Ledjan Ahmati",
  "company": "WEB8euroweb GmbH", 
  "sepa_iban": "DE72xxxxxxxxxxx63",
  "sepa_bic": "XXX",
  "sepa_bank": "Sparkasse Bochum",
  "paypal_email": "axxxxgmail.com",
  "data_policy": "REAL DATA ONLY - NO MOCK"
}
```

 Payment Processing

- **SEPA Transfers:** Direct European bank integration
- **PayPal Payments:** Real business account processing  
- **Stripe Subscriptions:** Plan-based recurring billing
- **Transaction Tracking:** Complete payment lifecycle monitoring

---

## 🛠️ Development

### Local Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Start development server
python start_server.py

# Run with auto-reload
uvicorn app.master:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Run test suite
pytest tests/

# Test specific modules
pytest tests/test_api.py -v

# Test payment integration
pytest tests/test_billing.py -v
```

---

## 🔍 System Status

**Live Monitoring Available:**

- Real-time system metrics at `/health`
- Complete ecosystem status at `/status`
- AI engine monitoring at `/api/*/info`
- Payment system status at `/billing/stats`

**No Mock Data:** This is an industrial-grade backend using real business integration, actual system monitoring, and live payment processing. All metrics, business information, and processing capabilities are real and functional. - FastAPI + Worker + Docker Compose

