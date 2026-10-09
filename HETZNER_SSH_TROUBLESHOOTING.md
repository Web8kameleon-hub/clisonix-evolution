# SSH Hetzner - Troubleshooting Guide

## Probleme të Zakonshme

### 1. Connection Refused

**Problem:**
```
ssh: connect to host 46.225.14.83 port 22: Connection refused
```

**Shënimet:**
- Server nuk është gati (prits 2-3 minuta pas krijimit)
- Firewall bllokon portin 22
- SSH service nuk është startuar

**Zgjidhje:**
```bash
# Test connectivity
ping 46.225.14.83

# Check if port 22 is open
telnet 46.225.14.83 22

# Wait for server initialization
sleep 120 && ssh root@46.225.14.83
```

---

### 2. Permission Denied (publickey)

**Problem:**
```
Permission denied (publickey).
```

**Shënimet:**
- SSH key nuk është në server
- Key permissions janë të gabuar
- Server pret password-authenticated login

**Zgjidhje:**

#### Windows:
```powershell
# Check key exists
Test-Path "$env:USERPROFILE\.ssh\hetzner_deploy_key"

# Fix key permissions
icacls "$env:USERPROFILE\.ssh\hetzner_deploy_key" /inheritance:r /grant:r "$env:USERNAME`:F"

# Try with verbose output
ssh.exe -v -i "$env:USERPROFILE\.ssh\hetzner_deploy_key" root@46.225.14.83
```

#### Linux/Mac:
```bash
# Check key permissions (should be 600)
ls -la ~/.ssh/hetzner_deploy_key
chmod 600 ~/.ssh/hetzner_deploy_key

# Check SSH dir permissions (should be 700)
ls -la ~/.ssh/
chmod 700 ~/.ssh

# Try with verbose output
ssh -v -i ~/.ssh/hetzner_deploy_key root@46.225.14.83
```

---

### 3. SSH Key Not Found

**Problem:**
```
load pubkey "/home/user/.ssh/hetzner_deploy_key": invalid format
```

**Shënimet:**
- Key nuk ekziston në specifikasin rrugën
- Key format nuk është i saktë
- SSH config tregon rrugë të gabuar

**Zgjidhje:**
```bash
# Verify key exists
ls -la ~/.ssh/hetzner_deploy_key*

# Regenerate key with correct format
ssh-keygen -t rsa -b 4096 -f ~/.ssh/hetzner_deploy_key -N ""

# If using Windows, convert to OpenSSH format
ssh-keygen -p -N "" -m pem -f ~/.ssh/hetzner_deploy_key
```

---

### 4. Host Key Verification Failed

**Problem:**
```
The authenticity of host '46.225.14.83' can't be established.
```

**Shënimet:**
- Server është i ri (first connection)
- SSH key e server-it ka ndryshuar
- Known hosts file është i korruptuar

**Zgjidhje:**
```bash
# Accept new host key
ssh -o StrictHostKeyChecking=accept-new root@46.225.14.83

# Or disable strictly (NOT recommended for production)
ssh -o StrictHostKeyChecking=no root@46.225.14.83

# Clear known_hosts if corrupted
rm ~/.ssh/known_hosts
ssh-keyscan 46.225.14.83 >> ~/.ssh/known_hosts 2>/dev/null
```

---

### 5. Timeout in Connecting

**Problem:**
```
ssh: connect to host 46.225.14.83 port 22: Operation timed out
```

**Shënimet:**
- Network latency problem
- Firewall filter packets
- Server is not responding

**Zgjidhje:**
```bash
# Increase timeout
ssh -o ConnectTimeout=30 root@46.225.14.83

# Test network connectivity
ping -c 4 46.225.14.83
traceroute 46.225.14.83

# Add to SSH config
Host hetzner-prod
    ConnectTimeout 30
    ServerAliveInterval 60
```

---

### 6. Too Many Authentication Failures

**Problem:**
```
Received disconnect from 46.225.14.83 port 22:2: Too many authentication failures
```

**Shënimet:**
- SSH agent ka shumë keys
- SSH server bllokon user-in pas disa tentativave

**Zgjidhje:**
```bash
# Try with specific key only
ssh -i ~/.ssh/hetzner_deploy_key -o IdentitiesOnly=yes root@46.225.14.83

# List keys in SSH agent
ssh-add -l

# Remove problematic keys from agent
ssh-add -d ~/.ssh/other_key
ssh-add -D  # Remove all keys

# Add only Hetzner key
ssh-add ~/.ssh/hetzner_deploy_key
```

---

### 7. SSH Agent Issues (Windows)

**Problem:**
```
Could not open a connection to your authentication agent.
```

**Zgjidhje:**
```powershell
# Check if SSH agent is running
Get-Service ssh-agent

# Start SSH agent
Start-Service ssh-agent

# Set to auto-start
Set-Service -Name ssh-agent -StartupType Automatic

# Add key to agent
ssh-add $env:USERPROFILE\.ssh\hetzner_deploy_key

# Verify key is loaded
ssh-add -l
```

---

### 8. Wrong SSH Key Format

**Problem:**
```
Invalid private key file format
```

**Shënimet:**
- Key është në OpenSSH PEM format
- Aplikacioni pret PuTTY format
- Key génération përdori wrong algorithm

**Zgjidhje:**
```bash
# Convert to PEM format (if needed)
ssh-keygen -p -m pem -f ~/.ssh/hetzner_deploy_key -N "" -P ""

# Convert to OpenSSH format
ssh-keygen -p -m RFC4716 -f ~/.ssh/hetzner_deploy_key

# Or regenerate în correct format
ssh-keygen -t rsa -b 4096 -f ~/.ssh/hetzner_deploy_key -m pem -N ""
```

---

## Advanced Diagnostics

### Verbose SSH Output

```bash
# Show detailed connection process
ssh -v root@46.225.14.83

# Very verbose (debug mode)
ssh -vvv root@46.225.14.83

# Example output interpretation:
# "debug1: Key loaded from ~/.ssh/hetzner_deploy_key" → Key found ✓
# "debug1: Trying private key ~/.ssh/hetzner_deploy_key" → Attempting ✓
# "debug1: Authentication succeeded" → Success ✓
```

### Test Server Connectivity

```bash
# Network level
ping 46.225.14.83

# Port level
telnet 46.225.14.83 22
nc -zv 46.225.14.83 22

# DNS level
nslookup 46.225.14.83
dig 46.225.14.83

# For server name (if using hostname)
ssh -v -G hetzner-prod | grep hostname
```

### Monitor SSH Logs (on server)

```bash
# Real-time log monitoring
ssh root@46.225.14.83 'tail -f /var/log/auth.log'

# Failed connection attempts
ssh root@46.225.14.83 'grep "Failed password\|Invalid user" /var/log/auth.log'

# Successful connections
ssh root@46.225.14.83 'grep "Accepted publickey\|Accepted password" /var/log/auth.log'
```

---

## Prevention Checklist

- [ ] Always use SSH keys, never password-based auth
- [ ] Keep SSH keys with permissions 600 (files) and 700 (directory)
- [ ] Regularly backup SSH keys
- [ ] Use key passphrases on critical systems
- [ ] Monitor SSH logs for intrusion attempts
- [ ] Disable root SSH login after setup
- [ ] Use different keys for different environments
- [ ] Rotate SSH keys quarterly
- [ ] Keep SSH client updated
- [ ] Review ~/.ssh/known_hosts regularly

---

## Performance Optimization

```bash
# Add to ~/.ssh/config for faster connections
Host hetzner-*
    # Compression (slower internet)
    Compression yes
    
    # Connection pooling (reuse connections)
    ControlMaster auto
    ControlPath ~/.ssh/control-%h-%p-%r
    ControlPersist 600
    
    # Keep-alive settings
    ServerAliveInterval 60
    ServerAliveCountMax 3
    
    # Fast cipher for fast networks
    Ciphers aes128-ctr,aes256-ctr
    
    # Disable IPv6 if not needed (faster)
    AddressFamily inet
```

---

## Emergency Access

Nëse SSH nuk funksionon fare:

### 1. Hetzner Recovery Console
```
Go to: https://console.hetzner.com → Server → Recovery
Boot into recovery system, fix configurations manually
```

### 2. Reset Root Password
```
Hetzner Console → Server → Reset Root Password
Set new password, login via console, fix SSH issues
```

### 3. Reinstall Server
```
Hetzner Console → Server → Reset → Click Reset
Reinstall OS, reconfigure SSH from scratch
```

---

## Support Resources

- **Hetzner Support:** https://support.hetzner.com
- **SSH Documentation:** https://linux.die.net/man/1/ssh
- **OpenSSH FAQ:** https://www.openssh.com/faq.html
- **Clisonix Docs:** HETZNER_SSH_SETUP.md

---

**Last Updated:** March 28, 2026
**Tested on:** Windows PowerShell 7.x, Ubuntu 24.04 LTS, macOS 14.x
