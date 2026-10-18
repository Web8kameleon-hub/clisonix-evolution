# Ultraweb Platform Vercel Deployment

## Project
- URL: https://ultraweb-platform-m60oqcm8v-ledjan-ahmatis-projects.vercel.app
- Domains:
  - ultra.clisonix.com
  - www.ultra.clisonix.com
- Status: Ready
- Required backend env for isolated deploy:
  - ULTRA_BACKEND_ORIGIN=https://your-ultra-backend-host
  - Self-hosted example: ULTRA_BACKEND_ORIGIN=http://127.0.0.1:7116

## Source Path in Repo
- external/Ultrawebthinkig-v2

## Deploy Commands
Run from repository root:

```bash
cd external/Ultrawebthinkig-v2
vercel --prod
```

## Domain Binding Commands (if needed)

```bash
vercel domains add ultra.clisonix.com ultraweb-platform
vercel domains add www.ultra.clisonix.com ultraweb-platform
```

## Notes
- The Vercel project config is in external/Ultrawebthinkig-v2/vercel.json.
- /backend/* now routes through the local proxy route /api/backend/[...path].
- Ultra no longer hardcodes api.clisonix.com as its backend origin.
- Docker microservice compose uses external/Ultrawebthinkig-v2/Dockerfile.microservices.
