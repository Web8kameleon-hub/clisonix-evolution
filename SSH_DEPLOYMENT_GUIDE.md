# Clisonix Newsroom v5.0 - SSH & Deployment Troubleshooting

## 🔴 Current Issue: SSH Authentication Failure

**Symptom**: 
```
Connection closed by 46.225.14.83 port 22 (Connection reset by peer)
```

**Possible Causes**:
1. ✅ SSH keys exist locally but NOT authorized on server
2. ✅ Key permissions incorrect (should be 600)
3. ✅ Key format mismatch (OpenSSH vs PuTTY)
4. ✅ Server has PasswordAuthentication disabled

---

## 🔧 Solution Options

### Option 1: Re-authorize SSH Key (RECOMMENDED)

**Step 1: Generate fresh SSH key** (if needed)
```bash
# On your Windows machine (PowerShell):
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\id_hetzner" -N ""
```

**Step 2: Copy public key to Hetzner server**
```bash
# Use Hetzner web console (if available) or:
cat ~/.ssh/id_hetzner.pub | ssh root@46.225.14.83 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

**Step 3: Test SSH connection**
```bash
ssh -i "$env:USERPROFILE\.ssh\id_hetzner" root@46.225.14.83 "echo 'SSH OK'"
```

### Option 2: Use Hetzner Web Console

1. Log in to Hetzner control panel
2. Find server 46.225.14.83
3. Use "Rescue/Console" option
4. Access web terminal
5. Manually add your SSH key to `/root/.ssh/authorized_keys`

### Option 3: Use Hetzner Control Panel or Alternative Access

1. Go to https://console.hetzner.cloud/
2. Select server: 46.225.14.83
3. Use "Recovery Console" or "Rescue Mode"
4. Upload SSH key OR execute deployment script directly

---

## 📋 SSH Key Checklist

Run these commands on your Windows machine:

```powershell
# 1. Check if SSH keys exist
Get-ChildItem "$env:USERPROFILE\.ssh\id_hetzner*"

# 2. Check key permissions (should show 600 or -rw-------)
ls -la "$env:USERPROFILE\.ssh\id_hetzner"

# 3. Test SSH verbosely
ssh -vv hetzner-new "whoami"

# 4. Check SSH config
Get-Content "$env:USERPROFILE\.ssh\config" | Select-String "hetzner-new" -Context 3
```

---

## 🚀 Deployment Options When SSH Works

### Option A: Remote Script Execution (Fast)
```powershell
# Run deployment script on Hetzner
ssh hetzner-new 'curl https://raw.githubusercontent.com/Clisonix-cloud/...DEPLOY_NEWSROOM.sh | bash'
```

Or locally on server:
```bash
bash /root/DEPLOY_NEWSROOM.sh
```

### Option B: Manual Step-by-Step (Safe)
```powershell
# SSH into server
ssh hetzner-new

# Then execute these commands:
cd /root/Clisonix-cloud
git pull origin blackboxai/fix-slo-sli-gate-errors
docker compose up -d --build newsroom
curl http://localhost:9800/health
```

### Option C: Docker Direct Push (If SSH Unavailable)

```powershell
# Build locally, push to Docker Hub, pull on Hetzner via web console
docker build -t yourusername/newsroom:latest ./services/newsroom
docker push yourusername/newsroom:latest

# Then on Hetzner (via web console):
docker pull yourusername/newsroom:latest
docker run -d -p 9800:9800 -e NEWSROOM_PORT=9800 yourusername/newsroom:latest
```

---

## 📞 Quick Commands Once SSH is Fixed

```powershell
# Test connection
ssh hetzner-new "echo 'SSH Working!'"

# Deploy Newsroom
ssh hetzner-new "cd /root/Clisonix-cloud && docker compose up -d --build newsroom"

# Check health
ssh hetzner-new "curl http://localhost:9800/health"

# Trigger first articles
ssh hetzner-new "curl -X POST http://localhost:9800/publish -d '{\"posts\":10}'"

# View logs
ssh hetzner-new "docker logs -f clisonix-newsroom"

# Audit log
ssh hetzner-new "curl http://localhost:9800/audit?limit=10"
```

---

## 🆘 If All Else Fails

**Contact Hetzner Support**:
- Email: support@hetzner.com
- Reset SSH access through web console
- Request password access for server

**Alternative**: Use local testing first, then deploy when connection is fixed

---

## ✅ Verification Checklist

Once SSH connection is established:

- [ ] `ssh hetzner-new "whoami"` returns "root"
- [ ] `ssh hetzner-new "docker ps"` shows running containers  
- [ ] `ssh hetzner-new "ls -la /root/Clisonix-cloud"` lists project files
- [ ] `ssh hetzner-new "docker compose --version"` shows Docker Compose available
- [ ] Deployment script runs without errors

---

## 📊 Status

| Item | Status | Notes |
|------|--------|-------|
| SSH Keys Generated | ✅ | id_hetzner + pub exist |
| SSH Config | ✅ | hetzner-new configured |
| Network Connectivity | 🔴 | Connection closed (auth issue) |
| Deployment Script Ready | ✅ | DEPLOY_NEWSROOM.sh created |
| Next Action | ⏳ | Fix SSH key authorization |

---

**Next Step**: Re-authorize SSH key or use Hetzner web console to add public key to `/root/.ssh/authorized_keys`

Once SSH works, deployment takes <5 minutes!
