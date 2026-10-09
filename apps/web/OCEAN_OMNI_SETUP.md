# Ocean Omni Setup (Realtime + Multimodal + Social)

Ky setup aktivizon një eksperiencë moderne për `Ocean` me:
- zë real bashkëbiseduesi,
- kamera + ekran live,
- dokumente, figura, script dhe audio/music,
- social media connect (YouTube, TikTok, Instagram, X, LinkedIn, Facebook).

## 1) Realtime (LiveKit + WebRTC)

Vendos env vars në runtime (frontend server):

- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `LIVEKIT_URL` ose `NEXT_PUBLIC_LIVEKIT_URL`

Endpoint:
- `POST /api/ocean/realtime`

Payload shembull:
```json
{
  "room": "ocean-live",
  "identity": "user-123",
  "name": "Admin"
}
```

## 2) Unified Omni Hub

Endpoint i unifikuar:
- `GET /api/ocean/omni` (capabilities)
- `POST /api/ocean/omni` (action router)

`action` të mbështetura:
- `realtime_token`
- `voice`
- `audio_transcribe`
- `vision`
- `document`
- `tts`
- `web_browse`
- `web_search`
- `social_status`
- `social_connect`

## 3) Social Connect Environment

Vendos sipas platformave që do aktivizosh:
- `YOUTUBE_API_URL`
- `TIKTOK_API_URL`
- `INSTAGRAM_API_URL`
- `X_API_URL`
- `LINKEDIN_API_URL`
- `FACEBOOK_API_URL`

Endpoints:
- `GET /api/ocean/social`
- `POST /api/ocean/social` me `{ "platform": "linkedin" }`

## 4) Existing Ocean Proxies

Already integrated:
- `POST /api/ocean/voice`
- `POST /api/ocean/audio`
- `POST /api/ocean/vision`
- `POST /api/ocean/document`
- `POST /api/ocean/tts`
- `GET/POST /api/ocean/web-reader`

## 5) Next Step (Production-grade)

Për "fjala e fundit" komplet, shto:
- LiveKit ingress + egress recording,
- Voice Activity Detection + echo cancellation profile,
- social OAuth flows + secure token vault,
- moderation/review pipeline para publikimit automatik,
- observability (p95/p99) për audio/video latency.
