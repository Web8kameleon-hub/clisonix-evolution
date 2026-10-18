# Hosting and Ocean recovery — 2026-09-16

## Issue

The production origin returned 521 after its web and Nginx containers stopped. The January Swarm manifest did not describe the current 198-service hosting manifest. Ocean chat also timed out before its first streamed token while Ollama ran on CPU.
An old Nginx rule returned 403 for the exact `/api/ocean` path, blocking the new JSON chat request even while the web endpoint itself was healthy.

## Documentation

`docs/production/hosting-v2.md` describes the current inventory, deployment check, required environment values, and optional GPU overlay. The bridge now distinguishes a reachable public domain from a working JSON integration.

## Tests

The repository integrity guard passed. The web build completed on the production host and its container became healthy. An internal `POST /api/ocean` with `allow_non_stream: true` returned JSON. The origin `/status` returned HTTP 200 after recovery. After recreating Nginx to refresh its bind mount, `nginx -t` passed and the origin `POST /api/ocean` returned HTTP 200 JSON. The public bridge domain probe returned HTTP 200 with Neurosonic `api_ready: true` and aiagi `api_ready: false`.
The security transition workflow previously stopped during job setup because GitHub rejects `actions/upload-artifact@v3`; the workflow now requests v4.
The service integration matrix probes documented OS-CLX and Neurosonic read-only APIs and reports unavailable integrations individually. The canonical Lightning SPP repository is `Web8kameleon-hub/Lightning-SPP-3.14`; its standalone production service is not currently listening on the documented host port.

## Edge cases

The full 198-service deployment remains blocked because `NODEDB_FLUID_URL` and `ULTRA_MS_POSTGRES_PASSWORD` are absent from `.env.production`. The NVIDIA GPU is detected, but Ollama remains CPU-only until the host driver mismatch is repaired. Cloudflare may still challenge automated public requests. The public domains `www.neurosonic.eu` and `www.aiagi.io` must not be labelled as working two-way fabric connections solely because their home pages respond.

## Benchmark

The production inventory found 198 services in the current Compose manifest and 77 matching active Compose containers at inspection time. No throughput or 1 GiB upload benchmark was completed; neither is claimed as verified.

## Rollback

The previous production Git revision is available in Git history. The server retains the pre-deploy tracked-file stash. Rebuild and recreate only the affected service from the prior revision if regression is observed; preserve production volumes and environment files.
