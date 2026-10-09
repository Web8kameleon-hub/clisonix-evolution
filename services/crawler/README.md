# Clisonix Crawler Service

Internal crawler service for discovering and measuring coverage of Clisonix pages.

## Endpoints

- `POST /crawl` — enqueue a crawl job
- `GET /status` — queue and global job status
- `GET /status/{job_id}` — per-job status
- `GET /coverage` — global coverage summary
- `GET /coverage/{job_id}` — coverage summary for one job
- `GET /health` — health check

## Example

```bash
curl -X POST http://localhost:9211/crawl \
  -H "Content-Type: application/json" \
  -d '{"seed_url":"https://clisonix.com/modules", "max_pages": 80, "same_domain_only": true}'
```

## Storage

SQLite database path:

- `/data/crawler.db` in container
- `CRAWLER_DB_PATH` to override
