# 🔑 Hetzner SSH Configuration Guide

**Dokumentim Komplet i SSH Setup për Hetzner Cloud**

---

## 📌 Overview

| Komponenta | Vlera |
|---|---|
| **Server Provider** | Hetzner Cloud (console.hetzner.com) |
| **Default Host** | 46.225.14.83 (rocky-32gb-nbg1-1) |
| **Default User** | root |
| **Default Port** | 22 (SSH) |
| **SSH Key Path** | `$HOME/.ssh/hetzner_deploy_key` |
| **Operating System** | Ubuntu 24.04 LTS |

---

## 🔧 SSH Setup - Hetzner-New

### Prerequisites

```powershell
# Windows: Check if SSH is available
ssh -V

# If not installed:
# 1. Windows 10 (1803+): SSH integrated
# 2. Windows 10 <1803: Install OpenSSH from Microsoft Store
# 3. Or use PuTTY/Git Bash
```

### Step 1: Generate SSH Key

```bash
# Generate new SSH key (Linux/Mac/Git Bash)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/hetzner_deploy_key -N ""

# PowerShell (Windows)
ssh-keygen.exe -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\hetzner_deploy_key" -N '""'
```

### Step 2: Get Public Key

```bash
# Linux/Mac/Git Bash
cat ~/.ssh/hetzner_deploy_key.pub

# PowerShell
Get-Content "$env:USERPROFILE\.ssh\hetzner_deploy_key.pub"
```

**Copy output to Hetzner Console:**
1. Login to https://console.hetzner.com
2. Go to **SSH Keys** section
3. Click **Add SSH Key**
4. Paste the public key content

### Step 3: Add SSH Key to Hetzner Server

When creating new server in Hetzner:
1. Select **SSH Key** section
2. Choose the SSH key you just added (hetzner_deploy_key)
3. Complete server creation

### Step 4: Test SSH Connection

```bash
# Linux/Mac/Git Bash
ssh -i ~/.ssh/hetzner_deploy_key root@46.225.14.83

# PowerShell
ssh -i "$env:USERPROFILE\.ssh\hetzner_deploy_key" root@46.225.14.83

# Expected output:
# root@rocky-32gb-nbg1-1:~#
```

---

## 🛠️ SSH Configuration File (~/.ssh/config)

Create or edit `~/.ssh/config` for easier access:

```ssh
# Hetzner Production Server
Host hetzner-prod
    HostName 46.225.14.83
    User root
    Port 22
    IdentityFile ~/.ssh/hetzner_deploy_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

# Hetzner New Server (Template for new setups)
Host hetzner-new
    HostName YOUR_NEW_SERVER_IP
    User root
    Port 22
    IdentityFile ~/.ssh/hetzner_deploy_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

# Development Hetzner
Host hetzner-dev
    HostName YOUR_DEV_SERVER_IP
    User root
    Port 22
    IdentityFile ~/.ssh/hetzner_deploy_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

**Usage after SSH config setup:**
```bash
ssh hetzner-prod
ssh hetzner-new
ssh hetzner-dev
```

---

## 📝 Hetzner-New Server Setup Checklist

### 1. Initial Access

```bash
# Connect to new server
ssh -i ~/.ssh/hetzner_deploy_key root@YOUR_NEW_IP

# Or use SSH config
ssh hetzner-new  # (after updating ~/.ssh/config)
```

### 2. System Preparation

```bash
# Update system packages
apt update && apt upgrade -y

# Install essential tools
apt install -y curl wget git htop vim nano tmux

# Set timezone
timedatectl set-timezone Europe/Berlin

# Create deployment user
adduser clisonix --disabled-password --gecos ""
usermod -aG docker clisonix
usermod -aG sudo clisonix

# Add your SSH key to clisonix user
sudo -u clisonix mkdir -p /home/clisonix/.ssh
sudo tee /home/clisonix/.ssh/authorized_keys > /dev/null <<< "$(cat ~/.ssh/hetzner_deploy_key.pub)"
sudo chown -R clisonix:clisonix /home/clisonix/.ssh
sudo chmod 700 /home/clisonix/.ssh
sudo chmod 600 /home/clisonix/.ssh/authorized_keys
```

### 3. Install Docker & Dependencies

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
bash get-docker.sh
rm get-docker.sh

# Install Docker Compose
apt install -y docker-compose-plugin

# Verify installation
docker --version
docker compose version

# Add root to docker group (if using root)
usermod -aG docker root
newgrp docker
```

### 4. Install Programming Languages

```bash
# Python 3.13
add-apt-repository ppa:deadsnakes/ppa -y
apt install -y python3.13 python3.13-venv python3-pip

# Node.js 24.x
curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
apt install -y nodejs

# Verify
python3.13 --version
node --version
npm --version
```

### 5. Install Web Server & SSL

```bash
# Nginx + Certbot
apt install -y nginx certbot python3-certbot-nginx

# Enable Nginx
systemctl enable nginx
systemctl start nginx

# Create SSL certificate (after DNS is configured)
certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com
```

### 6. Firewall Configuration

```bash
# Enable UFW firewall
apt install -y ufw
ufw default deny incoming
ufw default allow outgoing

# Allow SSH
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow application ports
ufw allow 8000/tcp   # API
ufw allow 3000/tcp   # Frontend
ufw allow 5000/tcp   # Additional services
ufw allow 8030/tcp   # Ocean Core
ufw allow 6680/tcp   # ALBI
ufw allow 7777/tcp   # JONA
ufw allow 5555/tcp   # ALBA

# Enable firewall
ufw enable

# Verify rules
ufw status
```

---

## 🚀 Deployment Scripts Usage

### Using Bash Script (Linux/Mac/Git Bash)

```bash
# Option 1: Use default configuration (46.225.14.83)
bash HETZNER_DEPLOY_v2.sh

# Option 2: Custom server
bash HETZNER_DEPLOY_v2.sh "your.server.ip" "root" 22

# Option 3: With SSH key
bash HETZNER_DEPLOY_v2.sh "your.server.ip" "root" 22 "/path/to/key"
```

### Using PowerShell Script (Windows)

```powershell
# Option 1: Use default
.\HETZNER_DEPLOY_v2.ps1

# Option 2: Custom parameters
.\HETZNER_DEPLOY_v2.ps1 -HetznerHost "your.server.ip" -HetznerUser "root" -HetznerPort 22 -SSHKeyPath "$env:USERPROFILE\.ssh\hetzner_deploy_key"
```

---

## 🔐 Security Best Practices

### 1. SSH Hardening

```bash
# Edit sshd_config
vi /etc/ssh/sshd_config

# Recommended changes:
PermitRootLogin no              # Disable root SSH (use clisonix user)
PasswordAuthentication no       # Key-based auth only
X11Forwarding no               # Disable X11
MaxAuthTries 3                 # Limit login attempts
MaxSessions 5                  # Limit concurrent sessions
ClientAliveInterval 300        # Keep-alive every 5 min
ClientAliveCountMax 2          # Disconnect after 2 missed

# Restart SSH
systemctl restart ssh

# Verify
systemctl status ssh
```

### 2. SSH Key Management

```bash
# Backup SSH key
mkdir -p ~/clisonix-backups
cp ~/.ssh/hetzner_deploy_key ~/clisonix-backups/hetzner_deploy_key.backup
chmod 600 ~/clisonix-backups/hetzner_deploy_key.backup

# Rotate SSH key quarterly
ssh-keygen -t rsa -b 4096 -f ~/.ssh/hetzner_deploy_key_new
# Update in Hetzner console and ~/.ssh/config
```

### 3. Monitor SSH Activity

```bash
# On Hetzner server
tail -f /var/log/auth.log | grep sshd

# Failed login attempts
grep "Failed password" /var/log/auth.log | wc -l

# Successful logins
grep "Accepted publickey\|Accepted password" /var/log/auth.log
```

---

## 🐛 Troubleshooting

### Connection Issues

```bash
# Test SSH connectivity with verbose output
ssh -v -i ~/.ssh/hetzner_deploy_key root@46.225.14.83

# Check if port 22 is open
telnet 46.225.14.83 22

# Verify SSH key permissions
ls -la ~/.ssh/
# hetzner_deploy_key should be 600
# hetzner_deploy_key.pub should be 644

# Fix permissions if needed
chmod 600 ~/.ssh/hetzner_deploy_key
chmod 644 ~/.ssh/hetzner_deploy_key.pub
```

### Permission Denied

```bash
# Wrong key format
ssh-keygen -p -f ~/.ssh/hetzner_deploy_key -m pem -N "" -P ""

# Wrong key permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/hetzner_deploy_key
chmod 644 ~/.ssh/hetzner_deploy_key.pub

# SSH agent (on Windows)
# Ensure OpenSSH Authentication Agent is running
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
ssh-add "$env:USERPROFILE\.ssh\hetzner_deploy_key"
```

### Slow SSH Connection

```bash
# Check network latency
ping -c 4 46.225.14.83

# Use faster cipher
ssh -c aes128-ctr -i ~/.ssh/hetzner_deploy_key root@46.225.14.83

# Disable DNS lookups
ssh -o UseDNS=no -i ~/.ssh/hetzner_deploy_key root@46.225.14.83
```

---

## 📋 Quick Reference Commands

| Komanda | Përshkrimi |
|---|---|
| `ssh hetzner-new` | Connect (if SSH config set up) |
| `scp -i key file.txt root@IP:/tmp/` | Copy file to server |
| `ssh-keygen -l -f ~/.ssh/hetzner_deploy_key` | Show key fingerprint |
| `ssh-keygen -p -f ~/.ssh/hetzner_deploy_key` | Change passphrase |
| `ssh root@IP "docker ps"` | Run single command |
| `ssh root@IP "bash -s" < script.sh` | Run script on server |

---

## 🎯 Next Steps After SSH Setup

1. ✅ Test SSH connection
2. ✅ Update ~/.ssh/config with new server info
3. ✅ Run initial system setup
4. ✅ Deploy Docker containers
5. ✅ Configure firewall
6. ✅ Setup monitoring (Prometheus/Grafana)
7. ✅ Configure SSL certificates

---

**Last Updated:** March 28, 2026  
**Author:** Ledjan Ahmati | Clisonix DevOps Team
