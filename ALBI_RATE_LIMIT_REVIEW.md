# 🧠 ALBI EEG Rate Limit Review & Recommendations

## Analysis: Is ALBI EEG Affected by Rate Limiting?

### Current Status

ALBI EEG endpoints are exposed through the main API gateway and are subject to the **120 requests/minute rate limit** (after JONA fix):

| Endpoint | Path | Rate Limit |
|----------|------|-----------|
| EEG Analysis | `/api/albi/eeg/analysis` | 120 req/min |
| Brainwave Visualization | `/api/albi/eeg/waves` | 120 req/min |
| Signal Quality Check | `/api/albi/eeg/quality` | 120 req/min |
| ALBI Health | `/api/albi/health` | 120 req/min |

### Direct User API

Separate standalone API on **port 6681** (`albi_user_api.py`):

- WebSocket real-time EEG streaming
- No rate limiting (separate application)
- Direct connection bypasses main API gateway

---

## Risk Assessment

### 🟡 MEDIUM RISK

**Real-time EEG streaming** might trigger rate limit issues if:

1. Client opens WebSocket connection (multiple TCP connections)
2. Rapid polling for new samples (e.g., every 100ms)
3. Multiple concurrent EEG streams from different channels
4. High-frequency updates for spectrogram computation

### Estimated Request Rate

- **Single channel, 100Hz sampling**: ~100 req/sec without batching
- **8-16 channels realtime**: Could spike to 800-1600 req/min

### Threshold

- 120 req/min == 2 requests/second
- **EEG real-time will likely exceed this**

---

## Recommendation: Create Separate Decision

### Option 1: Exempt ALBI Like JONA (Recommended)

Add `/api/albi/eeg/` to exempt paths - treat similar to JONA:

```python
RATE_LIMIT_EXEMPT_PATHS = {
    "/api/jona/",           # JONA services - no rate limit
    "/api/albi/eeg/",       # ALBI EEG real-time - no rate limit ← ADD THIS
    "/api/health",
    "/api/status",
    "/metrics",
    "/health",
}
```

**Pros**: Real-time performance guaranteed
**Cons**: No protection against abuse of EEG endpoints

### Option 2: Higher Limit for ALBI (Conservative)

Increase limit specifically for ALBI, keep JONA exempt:

```python
# In middleware, check if path starts with /api/albi/eeg/
if path.startswith("/api/albi/eeg/"):
    limit = 500  # 500 req/min for real-time EEG
else:
    limit = 120  # 120 req/min for others
```

**Pros**: Still protected against abuse, but allows real-time
**Cons**: More complex middleware logic

### Option 3: Monitor & Alert (Current)

Keep 120 req/min limit, monitor for issues:

```python
# Keep current implementation
# Alert if /api/albi/eeg/* returns 429 errors
# Real-time clients should use port 6681 directly
```

**Pros**: Simpler, protects against abuse
**Cons**: May have user experience issues during peak EEG activity

---

## Current Implementation Recommendation

**Status**: ✅ **WORKING AS-IS FOR NOW**

### Why

1. **Most users use port 6681 WebSocket** - Real-time streaming bypasses rate limit
2. **120 req/min is adequate** for polling-based EEG analysis (not real-time)
3. **JONA fix is higher priority** - Eliminates hard blocking

### Monitor for Issues

```bash
# Watch for 429 errors on ALBI endpoints
docker logs -f clisonix-api | grep -A2 "429.*albi"

# If errors occur, apply Option 1 (exempt /api/albi/eeg/)
```

---

## Follow-up Action Items

### If You See ALBI Rate Limit Errors

Apply this immediate patch:

```python
# File: apps/api/main.py, lines 1850-1855

RATE_LIMIT_EXEMPT_PATHS = {
    "/api/jona/",           # JONA services - no rate limit
    "/api/albi/eeg/",       # ALBI EEG analysis - no rate limit
    "/api/health",          
    "/api/status",          
    "/metrics",             
    "/health",              
}
```

### Testing Commands

```bash
# Rapid ALBI EEG analysis requests
for i in {1..20}; do
  curl -s http://localhost:8000/api/albi/eeg/analysis | jq .
done

# Monitor for 429 responses
```

---

## Comparison Matrix

| Service | Method | Rate Limit | Decision |
|---------|--------|-----------|----------|
| **JONA Audio** | Download (REST) | Exempt (∞) | ✅ FIXED |
| **ALBI EEG Real-time** | WebSocket (6681) | None (∞) | ✅ SEPARATE PORT |
| **ALBI EEG Analysis** | REST polling | 120 req/min | 🔄 MONITOR |

---

## Summary

**Current Fix Status**:

- ✅ JONA audio library: **FIXED** - Exempt from rate limiting
- ✅ Health/status endpoints: **EXEMPT** - No rate limit
- 🔄 ALBI EEG: **MONITORING** - 120 req/min currently adequate
- ⏳ Additional adjustments: Only if user experiences issues

**Next Steps**:

1. Deploy JONA fix (restart API)
2. Monitor ALBI error logs for 24-48 hours
3. Apply ALBI exemption if 429 errors detected
4. Document findings in production runbook

---

**TL;DR**: ALBI's real-time users connect directly to port 6681 (no rate limit). ALBI's REST analysis endpoints are subject to 120 req/min - sufficient for typical usage. Monitor and escalate if needed.
