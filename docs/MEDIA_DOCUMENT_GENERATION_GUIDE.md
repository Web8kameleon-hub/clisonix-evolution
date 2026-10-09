## 🎬 Media Document Generation — Video & Voice Integration with Curiosity Ocean

### Overview
Curiosity Ocean now integrates with two video generation laboratories for creating multimedia documents:
- **Blerina** (video_generator_blerina.py) - Script-based video with Coqui TTS
- **Animated** (video_generator_animated.py) - Motion graphics with animations
- **Voice Engine** (Coqui TTS) - Text-to-speech audio synthesis

---

## Architecture

```
Curiosity Ocean (Port 8030)
├── /api/documents/generate (POST)
│   ├── Format: "video" → VideoAgent → VideoContract → Blerina/Animated
│   ├── Format: "voice" → VoiceAgent → VoiceContract → Coqui TTS
│   └── Format: {pdf|excel|csv|report} → (existing agents)
│
├── Video Generators
│   ├── video_generator_blerina.py
│   │   ├── ScriptGenerator (uses BLERINA content patterns)
│   │   ├── VideoProject (defines video structure)
│   │   ├── VideoSection (individual scenes)
│   │   └── TTS Integration (Coqui)
│   │
│   └── video_generator_animated.py
│       ├── AnimatedVideoGenerator
│       ├── AnimatedVideo (project definition)
│       ├── AnimationType (Zoom, Pan, Ken Burns effects)
│       └── Edge TTS Integration
│
└── Voice Engine
    ├── Coqui TTS (local, free)
    ├── Multi-voice styles (professional, friendly, narrator, energetic)
    └── 22050 Hz sample rate (customizable)
```

---

## Usage

### 1. Generate Video Document

**Request:**
```bash
curl -X POST http://localhost:8030/api/documents/generate \
  -H "Content-Type: application/json" \
  -d '{
    "format": "video",
    "contract_type": "video",
    "query": "Create an educational video about EEG brain waves",
    "language": "en"
  }'
```

**Response:**
```json
{
  "success": true,
  "validation_status": "ready_for_generation",
  "document": {
    "type": "video_project",
    "format": "mp4",
    "project": {
      "title": "Generated Video",
      "topic": "Create an educational video about EEG brain waves",
      "style": "educational",
      "language": "en",
      "sections": [...],
      "metadata": {
        "source": "ocean_document_generation",
        "contract_type": "video",
        "generated_at": "2026-03-12T10:30:45.123456"
      }
    },
    "generators": ["blerina", "animated"],
    "estimated_duration_seconds": 300
  },
  "provenance": {
    "agent": "VideoAgent",
    "timestamp": "2026-03-12T10:30:45.123456",
    "backend": ["video_generator_blerina", "video_generator_animated"]
  }
}
```

---

### 2. Generate Voice Document

**Request:**
```bash
curl -X POST http://localhost:8030/api/documents/generate \
  -H "Content-Type: application/json" \
  -d '{
    "format": "voice",
    "contract_type": "voice",
    "query": "Create a professional narration about Clisonix Cloud",
    "language": "en"
  }'
```

**Response:**
```json
{
  "success": true,
  "validation_status": "ready_for_generation",
  "document": {
    "type": "voice_project",
    "format": "wav",
    "project": {
      "title": "Generated Voice Document",
      "query": "Create a professional narration about Clisonix Cloud",
      "language": "en",
      "voice_styles": ["professional", "friendly", "narrator"],
      "segments": [
        {
          "type": "summary",
          "text": "...",
          "voice_style": "professional",
          "duration_estimate": 15.5
        }
      ],
      "metadata": {
        "tts_backend": "coqui_tts",
        "sample_rate": 22050,
        "format": "wav",
        "generated_at": "2026-03-12T10:30:45.123456"
      }
    },
    "total_duration_seconds": 45.3,
    "segments_count": 3
  },
  "provenance": {
    "agent": "VoiceAgent",
    "timestamp": "2026-03-12T10:30:45.123456",
    "tts_engine": "coqui_tts",
    "backends": "ocean_nanogrid /api/ocean/tts"
  }
}
```

---

## Video Contracts

### VideoContract
Controls video generation with:
- **Video Styles**: educational, documentary, tutorial, presentation, social_media
- **Voice Styles**: professional, friendly, narrator, energetic
- **Target Duration**: 10s - 3600s (default 300s = 5 min)
- **Scenes**: Individual scenes with narration, images, durations
- **Subtitles**: Enable/disable automatic subtitle generation
- **Languages**: Multilingual subtitle support

### Example Video Contract Usage
```python
from document_contracts import VideoContract

contract = VideoContract()
contract.set_video_style("educational")
contract.target_duration = 180  # 3 minutes
contract.add_scene(
    title="Introduction",
    narration="Welcome to our deep dive into brain waves.",
    image_prompt="colorful brain visualization",
    duration=10.0
)
contract.add_scene(
    title="EEG Basics",
    narration="EEG measures electrical activity in the brain.",
    image_prompt="EEG electrode placement diagram",
    duration=15.0
)
```

---

## Voice Contracts

### VoiceContract
Controls voice/audio generation with:
- **Voice Styles**: professional, friendly, narrator, energetic
- **Languages**: multilingual support (en, al, de, fr, etc.)
- **Sample Rate**: 8000, 16000, 22050, 44100, 48000 Hz
- **Format**: wav (primary), mp3, m4a (extensible)
- **Effects**: background_music, sound_effects toggles
- **Segments**: Individual narration segments with styles

### Example Voice Contract Usage
```python
from document_contracts import VoiceContract

contract = VoiceContract()
contract.set_voice_style("professional")
contract.language = "en"
contract.add_segment(
    text="Clisonix Cloud is an industrial AI platform.",
    style="professional",
    duration=5.0
)
contract.add_segment(
    text="It powers neuroscience research globally.",
    style="narrator"
)
```

---

## Linked Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/documents/generate` | POST | Generate video/voice documents |
| `/api/documents/agents` | GET | List available agents (includes video, voice) |
| `/api/documents/capabilities` | GET | Document pipeline capabilities |
| `/api/ocean/tts` | POST | Direct TTS via nanogrid |
| `/api/ocean/voice` | POST | Voice synthesis endpoint |
| `/api/ocean/audio` | POST | Audio processing |

---

## File Structure

```
ocean-core/
├── document_agents.py              # Core agents
│   ├── DocumentAgent (base)
│   ├── PDFAgent
│   ├── ExcelAgent
│   ├── CSVAgent
│   ├── ReportAgent
│   ├── VideoAgent ⭐ NEW
│   └── VoiceAgent ⭐ NEW
│
├── document_contracts.py           # Contract governance
│   ├── DocumentContract (base)
│   ├── CPIReportContract
│   ├── ResearchReportContract
│   ├── GeneralReportContract
│   ├── VideoContract ⭐ NEW
│   └── VoiceContract ⭐ NEW
│
├── video_generator_blerina.py      # Linked: BLERINA video
├── video_generator_animated.py     # Linked: Animated motion graphics
└── ocean_api.py                     # Updated: /documents/generate endpoint
```

---

## Integration Points

### VideoAgent Links to:
- `video_generator_blerina.py` - ScriptGenerator, VideoProject, VideoStyle
- `video_generator_animated.py` - AnimatedVideoGenerator, AnimationType
- Coqui TTS (via both generators)

### VoiceAgent Links to:
- `ocean_nanogrid.py` `/api/ocean/tts` - Text-to-speech
- Coqui TTS backend
- Edge TTS backend (fallback)

### Ocean Document API Updates:
- `format_map`: Added `"mp4": "video"`, `"wav": "voice"`, `"audio": "voice"`
- `contract_map`: Added `"video"` → VideoContract, `"voice"` → VoiceContract
- Error messages updated to include video/voice formats

---

## Testing Checklist

- [x] VideoAgent created and registered
- [x] VoiceAgent created and registered
- [x] VideoContract with scene management
- [x] VoiceContract with segment management
- [x] ocean_api.py updated with video/voice support
- [ ] Test `/api/documents/agents` returns video/voice agents
- [ ] Test `/api/documents/generate` with format="video"
- [ ] Test `/api/documents/generate` with format="voice"
- [ ] Integration with Blerina BLERINA script generator
- [ ] Integration with Animated motion graphics
- [ ] Verify TTS output quality

---

## Next Steps

1. **Frontend Integration**: Add UI controls for video/voice generation
2. **Template Library**: Pre-built scenes and narration templates
3. **Streaming Output**: Real-time progress updates during generation
4. **Quality Metrics**: Confidence scores for generated content
5. **Caching**: Cache generated videos/audio for quick retrieval
6. **Marketplace**: Share generated templates community-wide

---

**Date**: March 12, 2026  
**Version**: 1.0  
**Maintainer**: Clisonix Cloud Dev Team  
**Status**: ✅ LIVE
