# Clisonix API Contract Standard

## Goal

Create one predictable response contract across frontend gateway routes and backend services.

## Success envelope

```json
{
  "success": true,
  "data": {},
  "meta": {
    "timestamp": "2026-03-24T12:00:00.000Z",
    "version": "2026-03-v1"
  }
}
```

## Error envelope

```json
{
  "success": false,
  "error": {
    "code": "UPSTREAM_UNAVAILABLE",
    "message": "Main API health upstream is unavailable",
    "details": {}
  },
  "meta": {
    "timestamp": "2026-03-24T12:00:00.000Z",
    "version": "2026-03-v1"
  }
}
```

## Degraded envelope

Use this when the route can still return fallback data, but the upstream path is unhealthy.

```json
{
  "success": false,
  "data": {},
  "error": {
    "code": "UPSTREAM_UNAVAILABLE",
    "message": "Fallback returned because upstream failed"
  },
  "meta": {
    "timestamp": "2026-03-24T12:00:00.000Z",
    "version": "2026-03-v1",
    "degraded": true,
    "fallback": true
  }
}
```

## Required fields

- `success`
- `meta.timestamp`
- `meta.version`

## Error rules

- `error.code` must be stable and machine-readable.
- `error.message` must be human-readable.
- `error.details` is optional and should not expose secrets.

## Health contract

Health endpoints should return the success envelope with `data` shaped like this:

```json
{
  "service": "jona",
  "status": "healthy",
  "checks": {
    "upstream": {
      "status": "healthy"
    },
    "redis": {
      "status": "healthy"
    }
  },
  "degraded_reason": null
}
```

### Health rules

- `status` should be one of `healthy`, `degraded`, `error`.
- `checks` should list important dependencies.
- `degraded_reason` should be `null` when healthy.
- Fallback data must use the degraded envelope.

## Initial rollout

Start with these gateway routes:

- `/api/system-status`
- `/api/proxy/health`
- `/api/jona/metrics`
- `/api/service-discovery`

Then extend the same contract to backend FastAPI services.
