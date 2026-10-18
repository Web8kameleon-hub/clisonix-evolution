param(
  [string]$ComposeRoot = ".",
  [ValidateSet("llama", "qwen")]
  [string]$Preset = "llama",
  [string]$TextModel = "",
  [string]$StreamModel = "llama3.2:3b",
  [string]$VisionModel = "llava:7b"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($TextModel)) {
  if ($Preset -eq "qwen") {
    $TextModel = "qwen2.5:14b"
  } else {
    $TextModel = "llama3.1:8b"
  }
}

$env:LOCAL_TEXT_MODEL = $TextModel
$env:LOCAL_STREAM_MODEL = $StreamModel

Push-Location $ComposeRoot
try {
  Write-Host "[1/5] Pulling models into Ollama..."
  Write-Host "    Text model: $TextModel"
  Write-Host "    Stream model: $StreamModel"
  Write-Host "    Vision model: $VisionModel"
  docker compose exec -T ollama ollama pull $TextModel
  docker compose exec -T ollama ollama pull $StreamModel
  docker compose exec -T ollama ollama pull $VisionModel

  Write-Host "[2/5] Starting local-first stack with override..."
  docker compose -f docker-compose.yml -f docker-compose.local-llama.yml up -d --build ocean-core ocean-core-multimodal clx-i

  Write-Host "[3/5] Service status..."
  docker compose ps --format "table {{.Service}}\t{{.Status}}" ocean-core ocean-core-multimodal clx-i ollama

  Write-Host "[4/5] LLM inventory..."
  docker compose exec -T ollama ollama list

  Write-Host "[5/5] Smoke tests..."
  curl.exe -sS -m 20 http://127.0.0.1:8030/health
  curl.exe -sS -m 20 http://127.0.0.1:8030/api/v1/integrations/status
}
finally {
  Pop-Location
}
