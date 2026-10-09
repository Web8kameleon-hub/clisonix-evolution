# CLX.I (Independent Icon Intelligence)

CLX.I is a standalone CLX service for image/icon analysis.
It uses Ollama vision transport compatible with LLaVA-style models while keeping CLX-specific control.

## Key Modes

- Stigma levels (output volume control):
  - `1`: concise short explanation
  - `2`: practical bullet summary
  - `3`: ultra-compact output
- Mirror levels (event logging depth):
  - `1`: metadata only
  - `2`: metadata + prompt
  - `3`: metadata + prompt + bounded response

## Environment Variables

- `CLXI_OLLAMA_HOST` default: `http://localhost:11434`
- `CLXI_VISION_MODEL` default: `clx-i:latest`
- `CLXI_TIMEOUT_SECONDS` default: `60`
- `CLXI_MAX_IMAGE_BASE64_LEN` default: `15000000`
- `CLXI_MIRROR_FILE` default: `.clx_i/mirror_events.jsonl`
- `CLXI_SELFLEARNING_ENABLED` default: `1`
- `CLXI_SELFLEARNING_FILE` default: `.clx_i/selflearning_events.jsonl`

## Run

```bash
uvicorn clx_i_service:app --host 0.0.0.0 --port 8048
```

## Health

```bash
curl -s http://localhost:8048/health
```

## Analyze Icon

```bash
curl -s -X POST http://localhost:8048/api/v1/icons/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "<BASE64_IMAGE>",
    "prompt": "Analyze this app icon for UX and brand meaning.",
    "stigma_level": 2,
    "mirror_level": 2
  }'
```

## No Fake Data Rule

- If model/upstream fails, service returns real error (`503`), never synthetic response.
- Empty upstream response is treated as error.

## Self-Learning

- Self-learning logs only real successful inference metadata.
- No synthetic labels or fabricated training targets are generated.
