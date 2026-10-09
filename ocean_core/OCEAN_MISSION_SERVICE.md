# Ocean Mission Service

Generic mission execution layer for **all user request types**.

## What it adds

- Persistent mission state (`sqlite`)
- Async mission queue worker
- Retry handling per step
- Pluggable tool registry
- API for submit/status/resume/list

## Service

- Container: `clisonix-ocean-mission`
- Port: `9500`
- Health: `/health`

## Start

```bash
docker compose up -d ocean-mission-service
```

## Core endpoints

- `GET /health`
- `GET /missions/tools`
- `POST /missions/submit`
- `GET /missions/{mission_id}`
- `POST /missions/{mission_id}/resume`
- `GET /missions?limit=20`

## Submit example

```json
{
  "user_id": "user_123",
  "query": "Generate excel and publish report",
  "max_retries": 2,
  "steps": [
    {
      "name": "Generate Excel",
      "tool": "python_script",
      "params": { "script": "investor-pack/build_investor_excel.py" }
    },
    {
      "name": "Check Ocean health",
      "tool": "http_health_check",
      "params": { "url": "http://localhost:8030/health" }
    }
  ]
}
```

## Built-in tools

- `http_health_check`
- `python_script`
- `file_exists`
- `sleep`

You can extend tools in `ocean_mission_service.py` without changing the API.
