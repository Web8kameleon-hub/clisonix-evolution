# Clisonix Cloud — Official Postman Collection Description

This repository contains the official API collection for Clisonix Cloud. The collection covers core services (Ocean, Brain, EEG & Audio, Monitoring, Monetization, Kitchen test runner) and is intended for developers and integrators to rapidly evaluate and automate workflows.

Key goals
- Provide a single collection with reusable environment variables (`baseUrl`, `auth_token`, `api_key`).
- Include example request/response pairs for common success and failure scenarios.
- Be production-ready: collection references `{{baseUrl}}` so it can run against local dev or production with a single environment switch.

Quick start
1. Import `Clisonix_Cloud_API.postman_collection.json` into Postman.
2. Import `clisonix-environment-production.json` (or create a `Local` environment with `baseUrl=http://localhost:8000`).
3. Select the environment and run requests.

Authentication
- Most endpoints require Bearer authentication. Set `auth_token` in the environment and include `Authorization: Bearer {{auth_token}}` in requests or enable the collection-level pre-request script that injects the header.

Example success response — Health Check
```
GET {{baseUrl}}/health

200 OK
{
  "timestamp": "2026-03-14T12:00:00Z",
  "instance_id": "instance-1",
  "status": "active",
  "uptime": "2h 15m",
  "memory": { "used": 20379, "total": 65317 },
  "system": { "cpu_percent": 6.6, "memory_percent": 31.2 }
}
```

Common error cases
- 401 Unauthorized: missing/invalid `auth_token`.
- 400 Bad Request: malformed payload (check Content-Type and JSON body).
- 500 Internal Server Error: unexpected server failure — include trace_id in bug reports.

Contribution
- To add endpoints, edit the collection file under `postman-collections/` and add a short `description` with an example response.
- Run the Kitchen worker to validate collections in CI.

Contact
- For questions about endpoints or expected payloads, open an issue or contact the engineering team.
