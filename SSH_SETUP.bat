@echo off
REM HETZNER SSH SETUP - BATCH VERSION

setlocal enabledelayedexpansion

set "SSHDIR=%USERPROFILE%\.ssh"
set "KEYPATH=%SSHDIR%\hetzner_rsa"
set "SERVERIP=46.62.210.251"

echo.
echo ================================================================================
echo                    HETZNER SSH SETUP - WINDOWS
echo ================================================================================
echo.

REM Create .ssh directory
if not exist "%SSHDIR%" (
    echo Creating .ssh directory...
    mkdir "%SSHDIR%"
    echo Created: %SSHDIR%
    echo.
)

REM Check for existing key
if exist "%KEYPATH%" (
    echo [OK] SSH key already exists
    echo Location: %KEYPATH%
) else (
    echo Generating SSH keypair...
    ssh-keygen -t rsa -b 4096 -f "%KEYPATH%" -N ""
    echo.
    echo [OK] SSH keypair generated successfully!
)

echo.
echo ================================================================================
echo                       YOUR PUBLIC KEY
echo ================================================================================
type "%KEYPATH%.pub"
echo ================================================================================
echo.

REM Copy to clipboard (Windows 10+)
type "%KEYPATH%.pub" | clip
echo [OK] Public key copied to clipboard!
echo.

echo.
echo ================================================================================
echo                      NEXT STEPS IN HETZNER
echo ================================================================================
echo.
echo METHOD 1: Reset Password (EASIEST)
echo ───────────────────────────────────
echo 1. Go to: https://console.hetzner.cloud
echo 2. Servers ^> cpx62-hel1-2
echo 3. Click "Reset password"
echo 4. Check email for temporary password
echo 5. Run this command:
echo.
echo    ssh root@46.62.210.251
echo.
echo 6. When prompted, enter the temporary password from email
echo 7. Once logged in, run these commands:
echo.
echo    mkdir -p ~/.ssh
echo    nano ~/.ssh/authorized_keys
echo.
echo 8. Paste your public key (it's in clipboard)
echo    Press Ctrl+X, then Y, then Enter to save
echo 9. Then run:
echo.
echo    chmod 600 ~/.ssh/authorized_keys
echo    chmod 700 ~/.ssh
echo    exit
echo.
echo ================================================================================
echo                        TEST YOUR CONNECTION
echo ================================================================================
echo.
echo After setting up, test with:
echo.
echo    ssh -i "%KEYPATH%" root@%SERVERIP%
echo.
echo ================================================================================
echo.
echo [OK] SSH setup complete! You can now follow Method 1 above.
echo.

endlocal
