# ═══════════════════════════════════════════════════════════════════════════════
# HETZNER SSH SETUP - WINDOWS POWERSHELL
# ═══════════════════════════════════════════════════════════════════════════════
#
# Problem: Permission denied (publickey,gssapi-keyex,gssapi-with-mic)
# Solution: Setup SSH keypair + Password authentication as fallback
#
# This script sets up secure SSH access to your Hetzner server
# ═══════════════════════════════════════════════════════════════════════════════

# STEP 1: GENERATE SSH KEY (if you don't have one)
# ═════════════════════════════════════════════════════════════════════════════

Write-Host "`n╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          HETZNER SSH SETUP - WINDOWS (PowerShell)                        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$SSHHome = "$env:USERPROFILE\.ssh"
$KeyPath = "$SSHHome\hetzner_rsa"
$ServerIP = "46.62.210.251"
$SSHUser = "root"

Write-Host "Step 1: Checking for existing SSH keys..." -ForegroundColor Yellow

if (-not (Test-Path $SSHHome)) {
    Write-Host "  Creating .ssh directory..." -ForegroundColor Gray
    New-Item -ItemType Directory -Path $SSHHome -Force | Out-Null
    Write-Host "  ✓ Created: $SSHHome`n" -ForegroundColor Green
}

if (Test-Path "$KeyPath") {
    Write-Host "  ✓ Found existing SSH key: $KeyPath" -ForegroundColor Green
}
else {
    Write-Host "  ✗ No SSH key found. Generating new keypair..." -ForegroundColor Yellow

    # Generate SSH key using ssh-keygen
    # Note: On Windows 11 or with Windows OpenSSH installed
    $GenerateCmd = @"
ssh-keygen -t rsa -b 4096 -f "$KeyPath" -N """""
"@

    Write-Host "  Running: ssh-keygen -t rsa -b 4096 -f `"$KeyPath`" -N `"`"`n" -ForegroundColor Gray

    try {
        # Use PowerShell to call ssh-keygen
        cmd /c "ssh-keygen -t rsa -b 4096 -f `"$KeyPath`" -N `""`""
        Write-Host "  ✓ SSH keypair generated successfully!`n" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Error generating SSH key: $_" -ForegroundColor Red
        Write-Host "  Make sure you have Windows OpenSSH installed or Git Bash available`n" -ForegroundColor Yellow
        exit 1
    }
}

# STEP 2: GET PUBLIC KEY
# ═════════════════════════════════════════════════════════════════════════════

Write-Host "Step 2: Reading public key..." -ForegroundColor Yellow

$PublicKeyPath = "$KeyPath.pub"
if (Test-Path $PublicKeyPath) {
    $PublicKey = Get-Content $PublicKeyPath
    Write-Host "  ✓ Public key found`n" -ForegroundColor Green
    Write-Host "  Public Key Content:" -ForegroundColor Gray
    Write-Host "  $PublicKey`n" -ForegroundColor Cyan
} else {
    Write-Host "  ✗ Public key not found at: $PublicKeyPath`n" -ForegroundColor Red
    exit 1
}

# STEP 3: SETUP SSH CONFIG
# ═════════════════════════════════════════════════════════════════════════════

Write-Host "Step 3: Creating SSH config..." -ForegroundColor Yellow

$ConfigPath = "$SSHHome\config"
$ConfigEntry = @"
        Host hetzner
        HostName 46.62.210.251
        User root
        IdentityFile ~/.ssh/hetzner_rsa
        StrictHostKeyChecking accept-new
        UserKnownHostsFile ~/.ssh/known_hosts
        "@

if (Test-Path $ConfigPath) {
    Write-Host "  SSH config already exists at: $ConfigPath" -ForegroundColor Gray
    Write-Host "  Current content:" -ForegroundColor Gray
    Get-Content $ConfigPath | Write-Host
    Write-Host ""
} else {
    Write-Host "  Creating SSH config file..." -ForegroundColor Gray
    Add-Content -Path $ConfigPath -Value $ConfigEntry
    Write-Host "  ✓ Created: $ConfigPath`n" -ForegroundColor Green
}

# STEP 4: INSTRUCTIONS FOR UPLOADING PUBLIC KEY
# ═════════════════════════════════════════════════════════════════════════════

Write-Host "`n╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║             NEXT: ADD PUBLIC KEY TO SERVER                               ║" -ForegroundColor Cyan
Write-Host "║                                                                           ║" -ForegroundColor Cyan
Write-Host "║  Use ONE of the following methods:                                       ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "METHOD 1: Via Hetzner Web Console (RECOMMENDED)" -ForegroundColor Yellow
Write-Host "  1. Go to: https://console.hetzner.cloud/projects"
Write-Host "  2. Select your project → Servers → cpx62-hel1-2"
Write-Host "  3. Click 'Rescue' tab → Enable Rescue mode"
Write-Host "  4. Reboot into rescue mode"
Write-Host "  5. From Windows PowerShell, run:"
Write-Host "     ssh -l root RESCUE_IP 'mkdir -p /root/.ssh && echo ""$PublicKey"" >> /root/.ssh/authorized_keys'`n" -ForegroundColor Gray

Write-Host "METHOD 2: Using Password Authentication First" -ForegroundColor Yellow
Write-Host "  1. Get temporary root password from Hetzner console"
Write-Host "  2. Connect via SSH with password:"
Write-Host "     ssh root@46.62.210.251"
Write-Host "  3. When prompted for password, enter the temporary password from console"
Write-Host "  4. Once connected, run:"
Write-Host "     mkdir -p ~/.ssh"
Write-Host "     echo '$PublicKey' >> ~/.ssh/authorized_keys"
Write-Host "     chmod 600 ~/.ssh/authorized_keys"
Write-Host "     chmod 700 ~/.ssh`n" -ForegroundColor Gray

Write-Host "METHOD 3: Automated via Reset Password" -ForegroundColor Yellow
Write-Host "  1. In Hetzner console, click 'Reset password' on the server"
Write-Host "  2. Check email for new temporary password"
Write-Host "  3. Run from Windows:"
Write-Host "     ssh root@46.62.210.251"
Write-Host "  4. Enter the temporary password when prompted"
Write-Host "  5. Then add your public key as in Method 2`n" -ForegroundColor Gray

Write-Host "═══════════════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# STEP 5: QUICK TEST
# ═════════════════════════════════════════════════════════════════════════════

Write-Host "Step 4: Ready to test SSH connection`n" -ForegroundColor Yellow

Write-Host "Once you've added the public key to the server, test with:" -ForegroundColor Gray
Write-Host "  ssh hetzner`n" -ForegroundColor Cyan
Write-Host "Or using full details:" -ForegroundColor Gray
Write-Host "  ssh -i `"$KeyPath`" root@$ServerIP`n" -ForegroundColor Cyan

Write-Host "═══════════════════════════════════════════════════════════════════════════`n" -ForegroundColor Green

# STEP 6: SAVE CREDENTIALS
# ═════════════════════════════════════════════════════════════════════════════

Write-Host "📝 SSH Key Summary:" -ForegroundColor Magenta
Write-Host "  Private Key: $KeyPath" -ForegroundColor Gray
Write-Host "  Public Key:  $PublicKeyPath" -ForegroundColor Gray
Write-Host "  Server:      $ServerIP" -ForegroundColor Gray
Write-Host "  User:        $SSHUser" -ForegroundColor Gray
Write-Host "  Config:      $ConfigPath`n" -ForegroundColor Gray

Write-Host "✓ SSH setup ready! Follow the methods above to add your key to the server." -ForegroundColor Green

