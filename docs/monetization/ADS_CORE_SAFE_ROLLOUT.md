# Ads Core Safe Rollout

This rollout keeps ads isolated from core AI paths and prevents application-wide failures.

## Architecture

- `services/ads_core`: independent FastAPI service (`8096`)
- `apps/web/app/api/ads/config/route.ts`: frontend proxy to ads-core config
- `apps/web/app/api/ads/track/route.ts`: frontend proxy to ads-core tracking
- `apps/web/src/components/ads/AdFooterSlot.tsx`: consent-gated footer slot only
- `apps/web/app/layout.tsx`: single global mount point

## Safety Guarantees

- No ad injection into AI model responses
- No hard dependency from chat pipeline to ads
- Explicit user consent required before loading ad scripts
- Feature-flag controlled (`ADS_ENABLED=false` by default)
- If ads-core is down, frontend continues without ads

## Start Commands

```bash
# Ensure external network exists
docker network create clisonix-net || true

# Start ads-core only
docker compose -f docker-compose.ads.yml up -d --build
```

## Runtime Check

```bash
curl http://localhost:8096/health
curl "http://localhost:8096/api/v1/ads/config?slot=footer&consent=true"
```

## Rollout Plan

1. Keep `ADS_ENABLED=false` in production.
2. Deploy ads-core + frontend changes.
3. Enable ads for internal traffic only (country allowlist + consent).
4. Monitor `/api/v1/ads/stats` for stability.
5. Gradually enable traffic if no regressions.

## Emergency Kill Switch

Set:

```env
ADS_ENABLED=false
```

Then restart only ads-core (or web if needed). Core app remains unaffected.
