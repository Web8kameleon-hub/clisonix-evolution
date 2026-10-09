# DNS Configuration Guide - STRATO → Hetzner

**Domain:** clisonix.com  
**Hosting:** Hetzner Cloud  
**DNS Provider:** STRATO

---

## 🎯 Objective

Point `clisonix.com` domain (registered at STRATO) to Hetzner server.

---

## 📋 Prerequisites

- ✅ Hetzner server created and IP address obtained
- ✅ Access to STRATO account
- ✅ Domain `clisonix.com` active

---

## 🔧 Step 1: Login to STRATO

1. Go to: https://www.strato.de/apps/CustomerService
2. Login with:
   - **Kundennummer:** K1266374525
   - **Email:** clisonix@pm.me
   - **Password:** [Your STRATO password]

---

## 🔧 Step 2: Navigate to DNS Settings

1. Click on **"Domains"** in the menu
2. Find **"clisonix.com"**
3. Click **"Verwalten"** (Manage)
4. Select **"DNS-Verwaltung"** or **"DNS Settings"**

---

## 🔧 Step 3: Configure A Records

Add the following DNS records:

### Record 1: Root Domain (@)
```
Type: A
Hostname: @
Value: [HETZNER_SERVER_IP]
TTL: 3600 (1 hour)
```

### Record 2: WWW Subdomain
```
Type: A
Hostname: www
Value: [HETZNER_SERVER_IP]
TTL: 3600
```

### Record 3: API Subdomain
```
Type: A
Hostname: api
Value: [HETZNER_SERVER_IP]
TTL: 3600
```

### Record 4: Grafana Subdomain (Optional)
```
Type: A
Hostname: grafana
Value: [HETZNER_SERVER_IP]
TTL: 3600
```

---

## 🔧 Step 4: Remove Conflicting Records

**IMPORTANT:** Remove any existing A or CNAME records for:
- `@` (root)
- `www`
- `api`
- `grafana`

That point to STRATO's servers (e.g., `570523285.swh.strato-hosting.eu`)

---

## 🔧 Step 5: Save Changes

1. Click **"Speichern"** (Save)
2. Confirm changes

---

## ⏱️ DNS Propagation Time

- **Local:** 5-15 minutes
- **Global:** 30 minutes - 48 hours (usually < 2 hours)

---

## ✅ Verification

### Check DNS Propagation

**Windows:**
```powershell
nslookup clisonix.com
nslookup www.clisonix.com
nslookup api.clisonix.com
```

**Linux/macOS:**
```bash
dig clisonix.com +short
dig www.clisonix.com +short
dig api.clisonix.com +short
```

**Online Tools:**
- https://www.whatsmydns.net/#A/clisonix.com
- https://dnschecker.org/#A/clisonix.com

---

## 🎯 Expected Result

All domains should return your Hetzner server IP:

```
clisonix.com → [HETZNER_IP]
www.clisonix.com → [HETZNER_IP]
api.clisonix.com → [HETZNER_IP]
```

---

## 🔐 SSL Certificate (After DNS Propagation)

Once DNS is propagated, run on Hetzner server:

```bash
# Install Certbot
apt install -y certbot

# Get certificates
certbot certonly --standalone -d clisonix.com -d www.clisonix.com --email clisonix@pm.me --agree-tos

certbot certonly --standalone -d api.clisonix.com --email clisonix@pm.me --agree-tos

# Auto-renewal
certbot renew --dry-run
```

Certificates will be saved to:
- `/etc/letsencrypt/live/clisonix.com/fullchain.pem`
- `/etc/letsencrypt/live/clisonix.com/privkey.pem`
- `/etc/letsencrypt/live/api.clisonix.com/fullchain.pem`
- `/etc/letsencrypt/live/api.clisonix.com/privkey.pem`

---

## 📊 Final Architecture

```
User Request
    ↓
DNS (STRATO)
    ↓
Hetzner Server (IP: XXX.XXX.XXX.XXX)
    ↓
Nginx Reverse Proxy (SSL/TLS)
    ├── clisonix.com → Next.js Frontend (Port 3000)
    └── api.clisonix.com → FastAPI Backend (Port 8000)
```

---

## 🆘 Troubleshooting

### DNS not updating
1. Clear browser cache
2. Flush DNS: `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (macOS)
3. Wait longer (up to 48h)
4. Check STRATO for typos in DNS records

### SSL certificate fails
1. Ensure DNS is fully propagated first
2. Check firewall allows ports 80/443
3. Stop nginx before running certbot: `docker compose stop nginx`
4. Run certbot again
5. Restart nginx: `docker compose up -d nginx`

---

**Last Updated:** December 11, 2025  
**Author:** Clisonix Cloud DevOps Team

