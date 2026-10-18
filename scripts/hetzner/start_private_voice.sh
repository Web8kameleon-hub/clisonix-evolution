#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."

if [[ $(id -u) != 0 ]]; then
  echo "Run as root on the production host so NVIDIA services can be checked." >&2
  exit 1
fi

docker volume inspect clisonix_ollama_data >/dev/null
nvidia-smi
systemctl start nvidia-persistenced
systemctl restart nvidia-cdi-refresh.service

base=(docker compose -p clisonixcom -f compose-hosting.yml -f docker-compose.75-services.yml -f docker-compose.unified.yml -f compose.runtime-repair.yml -f compose.ollama-private.yml)
"${base[@]}" config --format json | python3 -c '
import json,sys
d=json.load(sys.stdin); s=d["services"]["ollama"]
assert not s.get("ports"), "Ollama must not publish a host port"
assert s.get("gpus"), "GPU configuration is required"
assert any(v.get("source")=="ollama_existing" and v.get("target")=="/root/.ollama" for v in s["volumes"]), "Existing model volume required"
assert d["volumes"]["ollama_existing"]["name"]=="clisonix_ollama_data"
print("Private Ollama configuration verified")
'
"${base[@]}" up -d --no-deps --no-build --pull never ollama
docker compose -p clisonixcom -f docker-compose.unified.yml -f compose.ollama-private.yml up -d --no-deps --no-build --pull never ollama-multi-api
docker compose -p clisonixcom -f compose.voice-gpu.yml up -d --no-deps --no-build --pull never voice-stt

docker exec clisonix-ocean-core python3 -c '
import json,urllib.request
base="http://clisonix-ollama:11434"
model="huihui_ai/gemma-4-abliterated:12b"
payload={"model":model,"prompt":"","stream":False,"think":False,"keep_alive":"24h","options":{"num_ctx":4096,"num_gpu":999}}
with urllib.request.urlopen(urllib.request.Request(base+"/api/generate",data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"}),timeout=120) as r:
    json.load(r)
with urllib.request.urlopen(base+"/api/ps",timeout=10) as r:
    d=json.load(r)
m=next(x for x in d["models"] if x["name"]==model)
assert m["size"]>0 and m["size_vram"]>=m["size"], "Voice law requires full GPU residency; CPU fallback is forbidden"
print("Voice model warmed on GPU")
'
echo "Voice page: https://clisonix.com/modules/curiosity-ocean/voice"
