# Deploy fixed docker-compose to server
$sshKey = "C:\Users\Admin\.ssh\id_ed25519_nopwd"
$server = "root@46.225.14.83"
$localFile = "C:\Users\Admin\Desktop\Clisonix-cloud\docker-compose.lean.yml"
$remoteDir = "/opt/clisonix-cloud/docker-compose.lean.yml"

Write-Host "📤 Uploading docker-compose..."
scp -o StrictHostKeyChecking=no -i $sshKey $localFile "${server}:${remoteDir}"

Write-Host "✅ Upload complete. Restarting services..."
ssh -o StrictHostKeyChecking=no -i $sshKey $server "cd /opt/clisonix-cloud && docker-compose -f docker-compose.lean.yml down && sleep 3 && docker-compose -f docker-compose.lean.yml up -d" 

Write-Host "⏳ Waiting for services to start..."
Start-Sleep -Seconds 15

Write-Host "📊 Service Status:"
ssh -o StrictHostKeyChecking=no -i $sshKey $server "docker-compose -f /opt/clisonix-cloud/docker-compose.lean.yml ps"
