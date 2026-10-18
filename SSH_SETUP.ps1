#!/usr/bin/env powershell
# HETZNER SSH SETUP - SIMPLE VERSION

param(
    [string]$ServerIP = "46.62.210.251",
    [string]$SSHUser = "root"
)

$SSHHome = "$env:USERPROFILE\.ssh"
$KeyPath = "$SSHHome\hetzner_rsa"

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          HETZNER SSH SETUP - WINDOWS                                    ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Create .ssh directory if needed
if (-not (Test-Path $SSHHome)) {
    Write-Host "Creating .ssh directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $SSHHome -Force | Out-Null
    Write-Host "Created: $SSHHome`n" -ForegroundColor Green
}

# Check for existing key
if (Test-Path "$KeyPath") {
    Write-Host "SSH key already exists: $KeyPath" -ForegroundColor Green
}
else {
    Write-Host "Generating SSH keypair..." -ForegroundColor Yellow
    cmd /c "ssh-keygen -t rsa -b 4096 -f `"$KeyPath`" -N `"`""
    Write-Host "SSH keypair generated successfully!`n" -ForegroundColor Green
}

# Display public key
Write-Host "Your PUBLIC KEY:" -ForegroundColor Magenta
Write-Host "════════════════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Get-Content "$KeyPath.pub"
Write-Host "════════════════════════════════════════════════════════════════════════════`n" -ForegroundColor Gray

# Copy to clipboard
$PublicKey = Get-Content "$KeyPath.pub"
$PublicKey | Set-Clipboard
Write-Host "✓ Public key copied to clipboard!" -ForegroundColor Green
Write-Host ""

# Instructions
Write-Host "NEXT STEPS IN HETZNER CONSOLE:" -ForegroundColor Yellow
Write-Host "═════════════════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "METHOD 1: Reset Password (EASIEST)" -ForegroundColor Green
Write-Host "  1. Go to: https://console.hetzner.cloud" -ForegroundColor Gray
Write-Host "  2. Servers → cpx62-hel1-2" -ForegroundColor Gray
Write-Host "  3. Click 'Reset password'" -ForegroundColor Gray
Write-Host "  4. Check email for temporary password" -ForegroundColor Gray
Write-Host "  5. Run command below and paste your public key when done:`n" -ForegroundColor Gray

Write-Host "     ssh root@46.62.210.251" -ForegroundColor Cyan
Write-Host "     # Enter temporary password when prompted" -ForegroundColor Gray
Write-Host "     mkdir -p ~/.ssh" -ForegroundColor Cyan
Write-Host "     nano ~/.ssh/authorized_keys" -ForegroundColor Cyan
Write-Host "     # Paste public key, save (Ctrl+X, Y, Enter)" -ForegroundColor Gray
Write-Host "     chmod 600 ~/.ssh/authorized_keys" -ForegroundColor Cyan
Write-Host "     chmod 700 ~/.ssh" -ForegroundColor Cyan
Write-Host "     exit`n" -ForegroundColor Cyan

Write-Host "METHOD 2: Rescue Mode (MORE SECURE)" -ForegroundColor Green
Write-Host "  1. Go to: https://console.hetzner.cloud" -ForegroundColor Gray
Write-Host "  2. Servers → cpx62-hel1-2" -ForegroundColor Gray
Write-Host "  3. Click 'Rescue' tab → Enable Rescue Mode" -ForegroundColor Gray
Write-Host "  4. Reboot server" -ForegroundColor Gray
Write-Host "  5. Note the RESCUE_IP from console" -ForegroundColor Gray
Write-Host "  6. Run in PowerShell:`n" -ForegroundColor Gray

$pubkey = Get-Content "$KeyPath.pub" -Raw
Write-Host "     ssh -l root RESCUE_IP" -ForegroundColor Cyan
Write-Host "     mkdir -p /mnt/root/.ssh" -ForegroundColor Cyan
Write-Host "     echo '$pubkey' >> /mnt/root/.ssh/authorized_keys" -ForegroundColor Cyan
Write-Host "     exit`n" -ForegroundColor Cyan

Write-Host "═════════════════════════════════════════════════════════════════════════════`n" -ForegroundColor Gray

Write-Host "TEST CONNECTION:" -ForegroundColor Yellow
Write-Host "  After setting up the public key, test with:" -ForegroundColor Gray
Write-Host "  ssh -i `"$KeyPath`" root@$ServerIP`n" -ForegroundColor Cyan

Write-Host "KEY SUMMARY:" -ForegroundColor Magenta
Write-Host "  Private Key: $KeyPath" -ForegroundColor Gray
Write-Host "  Public Key:  $KeyPath.pub" -ForegroundColor Gray
Write-Host "  Server:      $ServerIP" -ForegroundColor Gray
Write-Host "  User:        $SSHUser`n" -ForegroundColor Gray

Write-Host "✓ SSH setup ready! Follow Method 1 or 2 above." -ForegroundColor Green
Write-Host ""
