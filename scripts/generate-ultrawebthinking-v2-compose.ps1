$templates = @(
  @{ id='backend'; file='backend-server.js'; internal=8000; envVar=$null },
  @{ id='simple-backend'; file='simple-backend.js'; internal=3008; envVar=$null },
  @{ id='gateway'; file='gateway-api-server.js'; internal=3003; envVar=$null },
  @{ id='simple-gateway'; file='simple-gateway-server.js'; internal=3003; envVar=$null },
  @{ id='internal-api'; file='internal-api-server.js'; internal=3002; envVar=$null },
  @{ id='api-gateway'; file='api-gateway/server.js'; internal='dynamic'; envVar='PORT' },
  @{ id='asi-agent'; file='asi-agent.js'; internal=3004; envVar=$null },
  @{ id='asi-ultra'; file='asi-agent-ultra.js'; internal='dynamic'; envVar='ASI_PORT' },
  @{ id='asi-ultra-native'; file='asi-agent-ultra-native.js'; internal='dynamic'; envVar='ASI_PORT' },
  @{ id='asi-producer'; file='asi-api-producer.js'; internal=3005; envVar=$null },
  @{ id='chat-native'; file='chat-server-native.js'; internal='dynamic'; envVar='CHAT_PORT' },
  @{ id='chat-ws'; file='ultraweb-chat-server.js'; internal='dynamic'; envVar='CHAT_WS_PORT' },
  @{ id='secure-comms'; file='ultraweb-secure-comms.js'; internal='dynamic'; envVar='PORT' },
  @{ id='ultracom'; file='ultracom-server.js'; internal='dynamic'; envVar='PORT' },
  @{ id='joan-asi'; file='euroweb-asi/server.js'; internal='dynamic'; envVar='PORT' },
  @{ id='neurosonix'; file='ultracom/neurosonix-server.js'; internal='dynamic'; envVar='PORT' }
)

$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('name: ultrawebthinking-v2-microservices')
$lines.Add('')
$lines.Add('x-ultra-common: &ultra-common')
$lines.Add('  build:')
$lines.Add('    context: ./external/Ultrawebthinkig-v2')
$lines.Add('    dockerfile: Dockerfile.microservices')
$lines.Add('  working_dir: /app')
$lines.Add('  restart: unless-stopped')
$lines.Add('  networks:')
$lines.Add('    - ultra-ms-net')
$lines.Add('')
$lines.Add('services:')

for ($p = 7111; $p -le 7161; $p++) {
  $t = $templates[($p - 7111) % $templates.Count]
  $internalPort = if ($t.internal -eq 'dynamic') { $p } else { $t.internal }

  $lines.Add("  ultra-ms-${p}:")
  $lines.Add('    <<: *ultra-common')
  $lines.Add('    environment:')
  $lines.Add('      NODE_ENV: production')
  $lines.Add("      ULTRA_SERVICE_ID: '$($t.id)'")
  $lines.Add("      ULTRA_SERVICE_PORT: '${p}'")
  if ($t.envVar) {
    $lines.Add("      $($t.envVar): '${p}'")
  }
  $lines.Add('    command:')
  $lines.Add('      - node')
  $lines.Add("      - $($t.file)")
  $lines.Add('    ports:')
  $lines.Add("      - '${p}:$internalPort'")
}

$lines.Add('')
$lines.Add('  ultra-ms-redis:')
$lines.Add('    image: redis:7-alpine')
$lines.Add('    restart: unless-stopped')
$lines.Add('    ports:')
$lines.Add("      - '7162:6379'")
$lines.Add('    networks:')
$lines.Add('      - ultra-ms-net')
$lines.Add('')
$lines.Add('  ultra-ms-postgres:')
$lines.Add('    image: postgres:15-alpine')
$lines.Add('    restart: unless-stopped')
$lines.Add('    environment:')
$lines.Add('      POSTGRES_DB: ultraweb')
$lines.Add('      POSTGRES_USER: ultraweb')
$lines.Add('      POSTGRES_PASSWORD: ultraweb_secure_2026')
$lines.Add('    ports:')
$lines.Add("      - '7163:5432'")
$lines.Add('    volumes:')
$lines.Add('      - ultra_ms_pg:/var/lib/postgresql/data')
$lines.Add('    networks:')
$lines.Add('      - ultra-ms-net')
$lines.Add('')
$lines.Add('volumes:')
$lines.Add('  ultra_ms_pg:')
$lines.Add('')
$lines.Add('networks:')
$lines.Add('  ultra-ms-net:')
$lines.Add('    driver: bridge')

$target = 'docker-compose.ultrawebthinking-v2.yml'
$lines -join "`n" | Set-Content -Path $target
Write-Host "Generated $target with ports 7111-7161"
