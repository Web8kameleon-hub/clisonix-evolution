# SSH Hetzner-New - Dokumentacion Komplet

## 📚 Përmbajtja

Këto dokumente ofrojnë instruksione të plota për SSH setup në Hetzner Cloud:

---

## 📄 Dokumentet

### 1. **HETZNER_SSH_SETUP.md** (Komplet)
- Overview i SSH Hetzner configuration
- SSH key generation (Windows, Linux, Mac)
- SSH config file setup
- Server preparation checklist
- Security best practices
- Troubleshooting guide

**Përdorimi:** Lexo këtë per të kuptuar të gjithë sistemin

---

### 2. **HETZNER_SSH_QUICK_REF.md** (Quick)
- 5-minuta quick start
- Manual setup steps
- Verification checklist
- Fast troubleshooting reference

**Përdorimi:** Kur ke nxitim dhe duhet përgjigje të shpejta

---

### 3. **HETZNER_SSH_TROUBLESHOOTING.md** (Advanced)
- Probleme të zakonshme dhe zgjidhjet
- Advanced diagnostics
- Emergency access procedures
- Performance optimization

**Përdorimi:** Kur has probleme specifike

---

## 🛠️ Skriptet e Automatizimit

### 4. **setup-hetzner-ssh.sh** (Linux/Mac)
Automatizore të plotë:
- Gjeneron SSH key
- Dëshiron public key në clipboard
- Prova të lidhjes
- Përditëson SSH config
- Shton key në SSH agent

**Përdorimi:**
```bash
bash setup-hetzner-ssh.sh
```

---

### 5. **setup-hetzner-ssh.ps1** (Windows)
PowerShell equivalent i skriptit Bash:
- Windows-optimized
- SSH agent integration
- Clipboard support
- Colorized output

**Përdorimi:**
```powershell
.\setup-hetzner-ssh.ps1 -HetznerIP "YOUR_IP"
```

---

### 6. **.ssh/config.template**
SSH config template për setup të shpejtë:
- Predefined hosts: hetzner-prod, hetzner-new, hetzner-dev
- Optimal settings (compression, keep-alive, timeouts)
- Global defaults

**Përdorimi:**
```bash
# Copy template to actual config
cp .ssh/config.template ~/.ssh/config
# Edit .ssh/config and replace placeholders
nano ~/.ssh/config
```

---

## 🚀 Fillesimi i Shpejtë

### Për Windows (PowerShell)
```powershell
# 1. Run automated setup
.\setup-hetzner-ssh.ps1

# 2. Connect to server
ssh hetzner-new
```

### Për Linux/Mac (Bash)
```bash
# 1. Run automated setup
bash setup-hetzner-ssh.sh

# 2. Connect to server
ssh hetzner-new
```

### Manual Setup (Të gjitha platformat)
```bash
# 1. Generate key
ssh-keygen -t rsa -b 4096 -f ~/.ssh/hetzner_deploy_key -N ""

# 2. Get public key
cat ~/.ssh/hetzner_deploy_key.pub
# Copy to Hetzner console

# 3. Setup SSH config
# Edit ~/.ssh/config, add host entry

# 4. Test connection
ssh hetzner-new
```

---

## 📋 Stepsë të Menjëhershme

1. **Generate SSH Key** (1 min)
   - Bash: `bash setup-hetzner-ssh.sh`
   - PowerShell: `.\setup-hetzner-ssh.ps1`

2. **Add to Hetzner** (2 min)
   - Go to: https://console.hetzner.com
   - Add SSH key to account
   - Create server with key selected

3. **Test Connection** (1 min)
   - `ssh hetzner-new`
   - Or: `ssh root@YOUR_SERVER_IP`

4. **Server Setup** (10 min)
   - Update system
   - Install Docker
   - Configure firewall
   - See: HETZNER_SSH_SETUP.md, Step 4-6

---

## 🎯 Përdorimet e Zakonshme

| Detyrë | Komanda |
|--------|---------|
| Connect | `ssh hetzner-new` |
| Run command | `ssh hetzner-new "docker ps"` |
| Copy file | `scp file.txt hetzner-new:/tmp/` |
| Copy folder | `scp -r folder/ hetzner-new:/tmp/` |
| Database tunnel | `ssh -L 5432:localhost:5432 hetzner-new` |
| SFTP access | `sftp hetzner-new` |
| View logs | `ssh hetzner-new "tail -f /var/log/auth.log"` |

---

## ✅ Verification Checklist

Before proceeding to deployment:

- [ ] SSH key generated: `ls ~/.ssh/hetzner_deploy_key`
- [ ] Public key added to Hetzner console
- [ ] SSH config updated: `cat ~/.ssh/config | grep hetzner`
- [ ] Connection successful: `ssh hetzner-new "echo OK"`
- [ ] Can run commands: `ssh hetzner-new "docker --version"`
- [ ] System updated: `ssh hetzner-new "apt update && apt upgrade -y"`
- [ ] Docker installed: `ssh hetzner-new "docker ps"`
- [ ] Firewall configured: `ssh hetzner-new "ufw status"`

---

## 🔐 Security Checklist

- [ ] SSH key permissions: `chmod 600 ~/.ssh/hetzner_deploy_key`
- [ ] SSH dir permissions: `chmod 700 ~/.ssh`
- [ ] No password-based auth on server
- [ ] Root SSH login disabled (after setup)
- [ ] Firewall restricts SSH to needed IPs
- [ ] SSH logs monitored regularly
- [ ] Key backed up to encryption storage
- [ ] Different keys for different environments

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Wait 2-3 min for server startup |
| Permission denied | Check key permissions: `chmod 600` |
| Host not found | Verify server IP is correct |
| Timeout | Increase timeout: `ssh -o ConnectTimeout=30` |
| Too many auth failures | Use `-o IdentitiesOnly=yes` |

**Full troubleshooting:** See HETZNER_SSH_TROUBLESHOOTING.md

---

## 📞 Support & Resources

| Resource | Link |
|----------|------|
| **Hetzner Console** | https://console.hetzner.com |
| **Hetzner Support** | https://support.hetzner.com |
| **SSH Documentation** | https://linux.die.net/man/1/ssh |
| **Clisonix Docs** | HETZNER_SSH_SETUP.md |

---

## 📊 Deployment Architecture

```
┌─────────────────────────────────────────┐
│  Your Computer (Windows/Linux/Mac)      │
│  ├─ ~/.ssh/hetzner_deploy_key (private) │
│  └─ SSH client configured               │
└────────────│────────────────────────────┘
             │ SSH Port 22
             │ (Encrypted)
             ▼
┌─────────────────────────────────────────┐
│  Hetzner Cloud Server                   │
│  ├─ Ubuntu 24.04 LTS                    │
│  ├─ SSH public key authorized           │
│  ├─ Docker installed                    │
│  ├─ Docker Compose installed            │
│  ├─ Firewall configured                 │
│  └─ Ready for deployment                │
└─────────────────────────────────────────┘
```

---

## 🎓 Learning Path

1. **Beginner:** Start with "Quick Reference"
2. **Intermediate:** Read "SSH Setup" documentation
3. **Advanced:** Study "Troubleshooting" guide
4. **Expert:** Customize configs, optimize performance

---

## 📅 Maintenance Schedule

| Task | Frequency | Documentation |
|------|-----------|---|
| Update system | Monthly | HETZNER_SSH_SETUP.md |
| Rotate SSH keys | Quarterly | HETZNER_SSH_TROUBLESHOOTING.md |
| Review SSH logs | Weekly | HETZNER_SSH_SETUP.md, Security section |
| Backup SSH keys | Monthly | HETZNER_SSH_TROUBLESHOOTING.md |
| Test disaster recovery | Quarterly | HETZNER_SSH_TROUBLESHOOTING.md, Emergency section |

---

## 📝 Recent Changes

- **March 28, 2026:** Complete SSH documentation created
- Added automated setup scripts (Windows & Linux)
- Added comprehensive troubleshooting guide
- Added SSH config template
- Added security best practices

---

## 🎯 Next Steps

1. **Choose your setup method:**
   - Automated: Run setup script
   - Manual: Follow quick reference

2. **Verify setup:**
   - Test SSH connection
   - Run remote commands
   - Check system status

3. **Deploy application:**
   - Use HETZNER_DEPLOY_v2.sh
   - Or manual setup per deployment guide

4. **Monitor and maintain:**
   - Check logs regularly
   - Keep system updated
   - Rotate keys quarterly

---

**Status:** ✅ Ready for Production  
**Last Updated:** March 28, 2026  
**Maintained By:** Clisonix DevOps Team
