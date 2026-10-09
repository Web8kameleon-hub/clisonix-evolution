# SSH Hetzner-New - Quick Reference

## 🚀 Quick Start (5 minutes)

### Windows (PowerShell)
```powershell
# 1. Run setup script
.\setup-hetzner-ssh.ps1 -HetznerIP "YOUR_SERVER_IP"

# 2. Connect to server
ssh hetzner-new

# 3. Or connect to production
ssh hetzner-prod
```

### Linux/Mac (Bash)
```bash
# 1. Run setup script
bash setup-hetzner-ssh.sh

# 2. Connect to server
ssh hetzner-new

# 3. Or connect to production
ssh hetzner-prod
```

---

## 📋 Manual Setup

### Step 1: Generate SSH Key
```bash
# Generate key (same on Windows/Linux/Mac)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/hetzner_deploy_key -N ""
```

### Step 2: Get Public Key & Add to Hetzner
```bash
cat ~/.ssh/hetzner_deploy_key.pub
# Copy output → https://console.hetzner.com → SSH Keys → Add SSH Key
```

### Step 3: Test Connection
```bash
ssh -i ~/.ssh/hetzner_deploy_key root@YOUR_SERVER_IP
```

### Step 4: Add to SSH Config
Edit `~/.ssh/config` (create if doesn't exist):
```
Host hetzner-new
    HostName YOUR_SERVER_IP
    User root
    IdentityFile ~/.ssh/hetzner_deploy_key
    StrictHostKeyChecking no
```

### Step 5: Test Easy Connect
```bash
ssh hetzner-new
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Permission denied | Check SSH key permissions: `chmod 600 ~/.ssh/hetzner_deploy_key` |
| Connection refused | Verify server IP is correct, server is running, port 22 is open |
| Host not found | Check DNS resolution: `ping YOUR_SERVER_IP` |
| Timeout | Add to ~/.ssh/config: `ConnectTimeout 10` |

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `HETZNER_SSH_SETUP.md` | Complete documentation |
| `.ssh/config.template` | SSH config template |
| `setup-hetzner-ssh.sh` | Linux/Mac setup script |
| `setup-hetzner-ssh.ps1` | Windows PowerShell setup |

---

## 🔗 Resources

- Full Documentation: [HETZNER_SSH_SETUP.md](HETZNER_SSH_SETUP.md)
- Hetzner Console: https://console.hetzner.com
- SSH Config Template: [.ssh/config.template](.ssh/config.template)

---

## ✅ Verification Checklist

- [ ] SSH key generated at `~/.ssh/hetzner_deploy_key`
- [ ] Public key added to Hetzner console
- [ ] SSH config updated with host entry
- [ ] Connection test successful: `ssh hetzner-new`
- [ ] Can run remote commands: `ssh hetzner-new "docker ps"`

---

**Created:** March 28, 2026 | **Status:** Ready for Production
