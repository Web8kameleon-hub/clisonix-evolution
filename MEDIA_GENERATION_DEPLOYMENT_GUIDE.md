# 🚀 Ocean Core Media Generation - Production Deployment Guide

**Status**: Ready for Deployment  
**Version**: 2.0 Complete  
**Updated**: March 2025

## Quick Summary

✅ **9 Document Agents** Ready:
- PDF, Excel, CSV, Report (existing)
- Video, Voice (phase 1)
- Music, Painting, Animation (phase 2)

✅ **16 Format Mappings** Complete:
- Video formats: mp4, video
- Voice formats: wav, voice, audio
- Music formats: midi, music
- Painting formats: png, jpg, jpeg, painting, image
- Animation format: animation
- Legacy: pdf, xlsx, csv, report

✅ **5 Media Contracts** Implemented:
- VideoContract (unlimited concepts)
- VoiceContract (multi-style TTS)
- MusicContract (procedural composition)
- PaintingContract (image generation)
- AnimationContract (motion graphics)

✅ **All Endpoints** Functional:
- `GET /api/documents/agents` - List all 9 agents
- `POST /api/documents/generate` - Generate any format

## Prerequisites

### Local Environment
```bash
# Python 3.13
# ffmpeg system package
# Docker & Docker Compose
```

### Dependencies (in requirements.txt)
```
# Media Libraries
Pillow>=10.0.0          # Image generation
opencv-python>=4.8.0    # Animation/video
ffmpeg-python>=0.2.1    # Video processing
imageio>=2.34.0         # Image I/O
music21>=9.1.0          # Music composition
librosa>=0.10.0         # Audio processing
scipy>=1.11.0           # Scientific computing
```

## 1. Pre-Deployment Checks

### Local Validation

```bash
# 1. Test agents registration
cd ocean-core
python test_agents.py
# Expected: ✅ ALL TESTS PASSED

# 2. Test format/contract mappings
python test_mappings.py
# Expected: ✅ ALL MAPPINGS VALID - READY FOR DEPLOYMENT

# 3. Verify all modules import
python -c "
from document_agents import (
    list_agents, get_agent, PDFAgent, ExcelAgent, 
    CSVAgent, ReportAgent, VideoAgent, VoiceAgent,
    MusicAgent, PaintingAgent, AnimationAgent
)
from document_contracts import (
    VideoContract, VoiceContract, MusicContract,
    PaintingContract, AnimationContract,
    CPIReportContract, ResearchReportContract,
    GeneralReportContract
)
print('✓ All modules import successfully')
"
```

## 2. Git Operations

### Stage & Commit
```bash
cd /path/to/repo

# Stage all changes
git add ocean-core/document_agents.py \
        ocean-core/document_contracts.py \
        ocean-core/ocean_core_full.py \
        ocean-core/MEDIA_GENERATION_COMPLETE_GUIDE.md \
        requirements.txt

# Commit with descriptive message
git commit -m "feat(ocean): extend media generation with music, painting, animation agents + unlimited concepts"

# Verify commit
git log --oneline -1
```

### Push to GitHub
```bash
git push origin main

# Verify push
git log --oneline -5
```

## 3. Docker Deployment

### Option A: Deploy to Production Server (hetzner-new)

```bash
# SSH into hetzner-new
ssh root@hetzner-new

# Navigate to deployment folder
cd /app/clisonix-cloud

# Pull latest code
git fetch origin main
git checkout origin/main -- ocean-core/

# Rebuild ocean-core image
docker compose up -d --build ocean-core

# Monitor build progress
docker logs -f clisonix-ocean-core

# Wait for service to be ready (~60 seconds)
sleep 60

# Check container status
docker ps | grep ocean-core
```

### Option B: Local Docker Testing

```bash
# Build local image
docker build -t clisonix-ocean-core:test ocean-core/

# Run container
docker run -d \
  --name ocean-test \
  -p 8030:8030 \
  clisonix-ocean-core:test

# Check logs
docker logs -f ocean-test

# Test endpoints (see section 4)
```

## 4. Post-Deployment Testing

### Health Check
```bash
curl -s http://localhost:8030/health | jq .
# Expected: {"status": "healthy", ...}
```

### List Available Agents
```bash
curl -s http://localhost:8030/api/documents/agents | jq '.agents[] | {name, format, available, backends}'
```

**Expected Output:**
```json
{
  "name": "video",
  "format": "MP4 Video",
  "available": true,
  "backends": ["video_generator_blerina", "video_generator_animated"]
}
{
  "name": "voice",
  "format": "WAV Audio",
  "available": true,
  "backends": ["coqui_tts", "ocean_nanogrid_tts"]
}
{
  "name": "music",
  "format": "MIDI/MP3 Music",
  "available": true,
  "backends": ["music21", "procedural"]
}
{
  "name": "painting",
  "format": "PNG/JPG Image",
  "available": true,
  "backends": ["PIL", "procedural"]
}
{
  "name": "animation",
  "format": "MP4 Animation",
  "available": true,
  "backends": ["OpenCV", "procedural"]
}
```

## 5. Test Each Media Type

### 5.1 Video Generation
```bash
curl -X POST http://localhost:8030/api/documents/generate \
  -H "Content-Type: application/json" \
  -d '{
    "format": "video",
    "contract_type": "video",
    "query": "Introduction to cloud computing",
    "language": "en"
  }'
```

**Expected**: 
- `"success": true`
- `"validation_status": "ready_for_generation"`
- Document type: `"video_project"`

### 5.2 Voice Generation
```bash
curl -X POST http://localhost:8030/api/documents/generate \
  -H "Content-Type: application/json" \
  -d '{
    "format": "voice",
    "contract_type": "voice",
    "query": "Professional business narration",
    "language": "en"
  }'
```

**Expected**:
- `"success": true`
- Document type: `"voice_project"`
- `"total_duration_seconds": > 0`

### 5.3 Music Generation
```bash
curl -X POST http://localhost:8030/api/documents/generate \
  -H "Content-Type: application/json" \
  -d '{
    "format": "music",
    "contract_type": "music",
    "query": "Ambient background music",
    "language": "en"
  }'
```

**Expected**:
- `"success": true`
- Document format: `"midi"`
- Metadata includes: `music_engine`, `bpm`, `mood`

### 5.4 Painting Generation
```bash
curl -X POST http://localhost:8030/api/documents/generate \
  -H "Content-Type: application/json" \
  -d '{
    "format": "painting",
    "contract_type": "painting",
    "query": "Abstract representation of AI",
    "language": "en"
  }'
```

**Expected**:
- `"success": true`
- Document format: `"png"`
- Includes: `style`, `theme`, `color_palette`

### 5.5 Animation Generation
```bash
curl -X POST http://localhost:8030/api/documents/generate \
  -H "Content-Type: application/json" \
  -d '{
    "format": "animation",
    "contract_type": "animation",
    "query": "Data pipeline animation",
    "language": "en"
  }'
```

**Expected**:
- `"success": true`
- Document format: `"mp4"`
- Includes: `fps`, `duration`, `total_frames`

## 6. Multiformat Request Testing

```bash
# Test format aliases
for fmt in mp4 midi png animation wav; do
  echo "Testing format: $fmt"
  curl -X POST http://localhost:8030/api/documents/generate \
    -d "{\"format\": \"$fmt\", \"contract_type\": \"generic\", \"query\": \"test\"}" \
    | jq '.success'
done
```

## 7. Integration with Ocean Services

### Translation Support
The system automatically integrates with:
```
http://clisonix-translation-node:8036
```

For multilingual generation:
```bash
# Generate in Spanish
curl -X POST http://localhost:8030/api/documents/generate \
  -d '{
    "format": "video",
    "contract_type": "video",
    "query": "Guía de computación en la nube",
    "language": "es"
  }'
```

### TTS Backend
Uses Coqui TTS service at:
```
http://clisonix-coqui-tts:8300
```

## 8. Monitoring & Logs

### View Container Logs
```bash
# Last 100 lines
docker logs --tail 100 clisonix-ocean-core

# Follow live logs
docker logs -f clisonix-ocean-core

# Search for errors
docker logs clisonix-ocean-core | grep ERROR
```

### Performance Metrics
Generation times typically:
- Video: 10-30 seconds
- Voice: 2-5 seconds per segment
- Music: 5-15 seconds
- Painting: 3-8 seconds
- Animation: 10-20 seconds

### Health Metrics
```bash
# Get comprehensive status
curl -s http://localhost:8030/status | jq .

# Get metrics (Prometheus format)
curl -s http://localhost:8030/metrics | grep ocean
```

## 9. Troubleshooting

| Issue | Solution |
|-------|----------|
| Module import error | Check requirements.txt, rebuild image |
| "Agent unavailable" | Verify format_map in ocean_core_full.py |
| "Contract not supported" | Add to contract_map in ocean_core_full.py |
| Long generation times | Increase timeout, check system resources |
| Connection to TTS failed | Verify coqui-tts container is running |
| Video generation fails | Ensure ffmpeg is installed in container |

## 10. Rollback Procedure

If issues occur:

```bash
# Stop current container
docker compose down

# Checkout previous version
git checkout HEAD~1 -- ocean-core/

# Rebuild from previous commit
docker compose up -d --build ocean-core

# Verify rollback
curl http://localhost:8030/health
```

## 11. Success Criteria

✅ All checks passed when:

- [ ] All 9 agents registered in `/api/documents/agents`
- [ ] All 5 media agents (video, voice, music, painting, animation) available
- [ ] All 16 format mappings working
- [ ] Test requests return success=true
- [ ] No ERROR- level logs in container
- [ ] Response times within expected range
- [ ] Container health check passing

## 12. Production Monitoring

### Daily Checks
```bash
# Health status
curl http://localhost:8030/health

# Agent availability
curl http://localhost:8030/api/documents/agents | jq '.agents[].available' | grep false

# Recent errors
docker logs clisonix-ocean-core | tail -20 | grep ERROR
```

### Weekly Review
- Response time metrics
- Error rates
- Resource utilization
- Feature usage statistics

## 13. Support & Documentation

- **Complete Guide**: `MEDIA_GENERATION_COMPLETE_GUIDE.md`
- **API Reference**: Generated in `/api/docs`
- **Source Code**: `document_agents.py`, `document_contracts.py`
- **Test Coverage**: `test_agents.py`, `test_mappings.py`

---

## Deployment Checklist

- [ ] Pre-deployment tests pass locally
- [ ] Code committed to main branch
- [ ] All changes pushed to GitHub
- [ ] Docker image builds successfully
- [ ] All endpoints return success
- [ ] Media generation agents functional
- [ ] Logs show no errors
- [ ] Health check passing
- [ ] All test requests succeed
- [ ] Performance metrics acceptable
- [ ] Documentation current

---

**Status**: ✅ READY FOR PRODUCTION DEPLOYMENT
