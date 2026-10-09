# JONA Neural Synthesis Settings Tab - Integration Analysis Document

**Document Version:** 1.0  
**Date:** February 19, 2026  
**Module:** `apps/web/app/modules/jona-neural/page.tsx`  
**API Endpoint:** `http://127.0.0.1:7777`  
**Component Type:** Real-time Neural Audio Synthesis Interface

---

## 📋 Table of Contents
1. [Executive Summary](#executive-summary)
2. [Current Architecture Analysis](#current-architecture-analysis)
3. [Settings Tab Design Specification](#settings-tab-design-specification)
4. [Implementation Roadmap](#implementation-roadmap)
5. [Technical Integration Points](#technical-integration-points)
6. [Audio Processing Pipeline](#audio-processing-pipeline)
7. [Data Persistence Strategy](#data-persistence-strategy)
8. [API Integration](#api-integration)

---

## Executive Summary

### Current State
The JONA Neural Synthesis module is a **professional audio synthesis engine** for brainwave entrainment with:
- **Real-time neural audio generation** with multiple waveform types
- **Frequency control** from 0.5 Hz (Delta) to 50 Hz (Gamma)
- **6 therapeutic presets** optimized for specific mental states
- **4 waveform synthesis modes** (Sine Wave, Binaural Beats, Isochronic Tones, Pink Noise)
- **Live brainwave band monitoring** (Delta, Theta, Alpha, Beta, Gamma)
- **Audio file library** with export capabilities
- **Connected status tracking** with real-time metrics

### Gap Analysis
The module currently **lacks a Settings Tab** for advanced audio configuration. Missing configuration layers:

| Feature | Status | Impact |
|---------|--------|--------|
| Audio output device selection | Manual only | No device flexibility |
| Synthesis algorithm tuning | Fixed presets | Limited customization |
| Waveform mixing ratios | Hardcoded | Cannot blend waveforms |
| Volume normalization | Fixed | No dynamic range control |
| Recording settings | No configuration | Limited audio capture |
| Frequency sweep patterns | Static only | No dynamic frequency shifts |
| Binaural beat carrier frequency | Fixed | Limited audio quality |
| Pink noise filtering | Not configurable | Standard only |
| Audio file format preferences | Single format | Limited portability |
| Preset management | Read-only | Cannot create custom presets |

### Proposed Solution
**Advanced Audio Settings with Neural Synthesis Control:**
- Tabbed interface for advanced audio configuration
- Persisted to localStorage + backend database
- Hospital-grade synthesis profiles (therapeutic protocols)
- Multi-device audio routing
- Real-time synthesis parameter tuning
- Custom preset creation and management

---

## Current Architecture Analysis

### Component Structure

**Current Features:**
- ✅ Real-time audio synthesis (multiple waveforms)
- ✅ Preset system (6 therapeutic presets)
- ✅ Brainwave band display with live metrics
- ✅ Frequency control slider (0.5-50 Hz)
- ✅ Audio file library
- ✅ Export functionality
- ❌ **No settings container** - configuration scattered
- ❌ **No persistence** - all ephemeral state
- ❌ **No advanced audio controls** - limited customization
- ❌ **No device routing** - single output only

### Audio Processing Pipeline

```
┌──────────────────────────────────────────┐
│     JONA Neural Synthesis Engine         │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ Frequency Input (0.5-50 Hz)        │ │
│  │ + Preset Selection (6 options)     │ │
│  └──────────┬─────────────────────────┘ │
│             │                           │
│  ┌──────────▼─────────────────────────┐ │
│  │ Waveform Generator                 │ │
│  │ • Sine Wave (pure tone)             │ │
│  │ • Binaural Beats (stereo)          │ │
│  │ • Isochronic Tones (pulsing)       │ │
│  │ • Pink Noise (ambient)              │ │
│  └──────────┬─────────────────────────┘ │
│             │                           │
│  ┌──────────▼─────────────────────────┐ │
│  │ Audio Processing                   │ │
│  │ • Frequency Analysis (FFT)          │ │
│  │ • Brainwave Band Detection         │ │
│  │ • Volume Normalization             │ │
│  │ • Real-time Metrics                │ │
│  └──────────┬─────────────────────────┘ │
│             │                           │
│  ┌──────────▼─────────────────────────┐ │
│  │ Audio Output                       │ │
│  │ • Speaker/Headphone Output         │ │
│  │ • File Recording (WAV/MP3/OGG)    │ │
│  │ • Real-time Streaming              │ │
│  └────────────────────────────────────┘ │
│             │                           │
│  ┌──────────▼─────────────────────────┐ │
│  │ Metrics Display                    │ │
│  │ • Signals Processed                │ │
│  │ • Audio Files Generated            │ │
│  │ • Uptime Counter                   │ │
│  │ • Brainwave Distribution           │ │
│  └────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

### Key State Variables

| Variable | Type | Scope | Persistence |
|----------|------|-------|-------------|
| `targetFrequency` | number | Session-scoped | ❌ Lost on reload |
| `waveformType` | string | Session-scoped | ❌ Resets to default |
| `activePreset` | string | Session-scoped | ❌ Lost on switching tabs |
| `isSynthesizing` | boolean | Session-scoped | ❌ Resets to false |
| `audioLibrary` | AudioFile[] | Session-scoped | ❌ Ephemeral |
| `brainwaveBands` | BandMetrics | Real-time only | ❌ Not stored |
| `audioSettings` | ❌ MISSING | N/A | N/A |
| `deviceConfiguration` | ❌ MISSING | N/A | N/A |
| `synthesisProfiles` | ❌ MISSING | N/A | N/A |

---

## Settings Tab Design Specification

### Visual Layout

```
┌────────────────────────────────────────────────────────┐
│  JONA NEURAL SYNTHESIS                  [⚙️ Settings]  │  ← Tab Button
├────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────┐ │
│ │ ⚙️ NEURAL SYNTHESIS SETTINGS           [✕ Close]   │ │  ← Modal Header
│ ├──────────────────────────────────────────────────────┤ │
│ │                                                      │ │
│ │ 🔊 AUDIO          🌊 WAVEFORM      🧠 NEURAL      │ │  ← Tab Navigation
│ │ 🎛️ PRESETS       📊 METRICS       💾 FILES        │ │
│ │                                                      │ │
│ ├──────────────────────────────────────────────────────┤ │
│ │ [Currently viewing: AUDIO tab]                      │ │
│ │                                                      │ │
│ │ Audio Output Configuration:                         │ │
│ │ ┌──────────────────────────────────────────────┐   │ │
│ │ │ Device: [Speakers ▼]                        │   │ │
│ │ │ Sample Rate: [44100 Hz ▼]                   │   │ │
│ │ │ Bit Depth: [24-bit ▼]                       │   │ │
│ │ │ Volume: [75 ▼]%                             │   │ │
│ │ │ Normalization: [Dynamic ▼]                  │   │ │
│ │ └──────────────────────────────────────────────┘   │ │
│ │                                                      │ │
│ │ [Test Audio]  [Save Settings]  [Reset]            │ │
│ └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

### Tab 1: **🔊 AUDIO**
**Purpose:** Audio device and output configuration

**Settings:**
```typescript
{
  outputDevice: string;           // Speaker, Headphones, Line-out, etc.
  sampleRate: 44100 | 48000 | 96000;  // Hz (CD, Pro, HD)
  bitDepth: 16 | 24 | 32;        // bits
  channels: 1 | 2;               // Mono or Stereo
  bufferSize: 256 | 512 | 1024 | 2048;  // Samples
  volume: number;                // 0-100
  normalization: "static" | "dynamic" | "peak";
  enableDithering: boolean;       // For 16-bit output
  headphoneMode: boolean;         // Binaural optimization
  balanceLR: number;              // -50 to +50 (Left/Right)
}
```

### Tab 2: **🌊 WAVEFORM**
**Purpose:** Advanced waveform synthesis and mixing

**Settings:**
```typescript
{
  primaryWaveform: "sine" | "binaural" | "isochronic" | "pink_noise";
  secondaryWaveform?: "sine" | "binaural" | "isochronic" | "pink_noise";
  waveformBlend: number;          // 0-100 (primary to secondary)
  
  // Sine Wave params
  sine: {
    pureFrequency: number;        // Base frequency
    harmonics: number[];          // Optional overtones
    phaseShift: number;           // 0-360 degrees
  },
  
  // Binaural Beats params
  binaural: {
    carrierFrequency: number;     // 200-2000 Hz (left + right)
    beatFrequency: number;        // Target brainwave freq
    stereoPhaseOffset: number;    // Phase difference
  },
  
  // Isochronic Tones params
  isochronic: {
    baseFrequency: number;        // Foundation tone
    pulseRate: number;            // Target brainwave freq
    pulseWidth: number;           // 0.0-1.0
  },
  
  // Pink Noise params
  pinkNoise: {
    noiseFloor: number;           // dB minimum
    spectralBalance: "flat" | "warm" | "bright";
  }
}
```

### Tab 3: **🧠 NEURAL**
**Purpose:** Neural entrainment and brainwave targeting

**Settings:**
```typescript
{
  targetBand: "delta" | "theta" | "alpha" | "beta" | "gamma";
  frequencyRange: [number, number];  // Min/max Hz
  entrainmentMode: "direct" | "binaural" | "isochronic" | "hybrid";
  rampUpTime: number;             // Seconds to reach target
  rampDownTime: number;           // Seconds to exit
  sustainDuration: number;        // Duration at target frequency
  sessionProfile: "therapeutic" | "research" | "meditation" | "focus";
  enableFrequencySweep: boolean;  // Dynamic frequency shifts
  sweepRange: number;             // ±Hz around target
  sweepRate: number;              // Hz/second
}
```

### Tab 4: **🎛️ PRESETS**
**Purpose:** Preset management and custom profile creation

**Built-in Presets:**
```typescript
[
  {
    id: "deep-sleep",
    name: "Deep Sleep",
    frequency: 2.5,
    waveformType: "isochronic",
    description: "Delta waves for deep, restorative sleep"
  },
  {
    id: "meditation",
    name: "Meditation",
    frequency: 6.0,
    waveformType: "binaural",
    description: "Theta waves for deep meditation state"
  },
  {
    id: "relaxation",
    name: "Relaxation",
    frequency: 10.0,
    waveformType: "sine",
    description: "Alpha waves for calm relaxation"
  },
  {
    id: "focus",
    name: "Focus",
    frequency: 14.0,
    waveformType: "isochronic",
    description: "Low Beta for concentration and focus"
  },
  {
    id: "alertness",
    name: "Alertness",
    frequency: 20.0,
    waveformType: "binaural",
    description: "High Beta for alertness and energy"
  },
  {
    id: "cognition",
    name: "Cognition",
    frequency: 40.0,
    waveformType: "isochronic",
    description: "Gamma waves for cognitive enhancement"
  }
]
```

**Custom Presets:**
```typescript
{
  customPresets: [
    {
      id: "user-custom-1",
      name: "My Focus Session",
      frequency: 13.5,
      waveformType: "binaural",
      parameters: {...}
    }
  ],
  allowCustomCreation: boolean;
  sharingEnabled: boolean;
}
```

### Tab 5: **📊 METRICS**
**Purpose:** Synthesis quality and performance monitoring

**Settings:**
```typescript
{
  enableMetricsCollection: boolean;
  recordingMetrics: boolean;
  metricsRefreshRate: 100 | 250 | 500 | 1000;  // ms
  trackFrequencyAccuracy: boolean;
  trackHarmonicContent: boolean;
  trackTotalHarmonic: boolean;     // THD measurement
  alertOnQualityIssues: boolean;
  qualityThreshold: number;        // % minimum
}
```

### Tab 6: **💾 FILES**
**Purpose:** Audio recording and file management

**Settings:**
```typescript
{
  recordingFormat: "wav" | "mp3" | "ogg" | "flac" | "aac";
  recordingQuality: "high" | "medium" | "low";
  autoRecordSessions: boolean;
  autoSaveFormat: "wav" | "mp3";
  sessionNaming: "auto" | "manual" | "mixed";
  includeMetadata: boolean;
  compressionLevel: 0 | 5 | 9;     // MP3/OGG/FLAC
  autoArchiveAge: number;          // Days before archiving
}
```

---

## Implementation Roadmap

### Phase 1: Settings State Container (Week 1)

**Create:** `context/JonaSettingsContext.tsx`

```typescript
interface JonaSettings {
  audio: AudioSettings;
  waveform: WaveformSettings;
  neural: NeuralSettings;
  presets: PresetsSettings;
  metrics: MetricsSettings;
  files: FileSettings;
}

const JonaSettingsContext = createContext<JonaSettings | null>(null);
const useJonaSettings = () => useContext(JonaSettingsContext);
```

### Phase 2: Settings UI Components (Week 2)

**Create:** `components/JonaSettingsModal.tsx`

Components needed:
- Audio Device Selector
- Waveform Mixing Controls
- Frequency Range Sliders
- Preset Manager
- Audio Quality Visualizer
- Recording Format Selector

### Phase 3: Main Component Integration (Week 2)

**Modify:** JONA module to apply settings in real-time

### Phase 4: Backend Integration (Week 3)

**Endpoints:** 6 new API routes for settings management

---

## Audio Processing Pipeline Integration

### Current Signal Flow
```
Frequency Input → Waveform Generator → Audio Engine → Output
                       ↓
                  Metrics Analysis ← Brainwave Detector
```

### Enhanced Signal Flow (with Settings)
```
Settings (Device, Waveform, Neural) ↓
Frequency Input → Waveform Generator → Audio Processor → Output Device
                       ↓              ↓
                  Metrics Analysis ← Brainwave Detector
                       ↓
                  Quality Monitor → Alert System
```

### New Capabilities
1. **Audio Device Routing** - Select output device at runtime
2. **Waveform Mixing** - Blend multiple synthesis types
3. **Frequency Sweeping** - Dynamic frequency transitions
4. **Quality Monitoring** - Real-time THD and accuracy metrics
5. **Preset Management** - Create/save/load custom synthesis profiles
6. **Format Selection** - Record in preferred audio format

---

## Data Persistence Strategy

### Layer 1: Browser LocalStorage
```typescript
const saveJonaSettings = (settings: JonaSettings) => {
  localStorage.setItem('jona-settings:v1', JSON.stringify(settings));
};

const loadJonaSettings = (): JonaSettings | null => {
  const stored = localStorage.getItem('jona-settings:v1');
  return stored ? JSON.parse(stored) : null;
};
```

### Layer 2: Backend Database (PostgreSQL)
```sql
ALTER TABLE users ADD COLUMN jona_settings JSONB DEFAULT NULL;
CREATE TABLE jona_presets (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  preset_name VARCHAR(255),
  frequency FLOAT,
  waveform_type VARCHAR(50),
  parameters JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Layer 3: Audio File Management
```sql
CREATE TABLE audio_files (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  filename VARCHAR(255),
  preset_id UUID,
  duration_seconds FLOAT,
  file_size_mb FLOAT,
  format VARCHAR(10),  -- wav, mp3, ogg, flac
  uploaded_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (preset_id) REFERENCES jona_presets(id)
);
```

---

## API Integration

### New Backend Endpoints (6 Total)

#### 1. **GET /neural/settings/default**
Returns default JONA synthesis settings with audio device enumeration

**Response:**
```json
{
  "audio": {
    "outputDevices": ["Speakers", "Headphones", "Line-out"],
    "sampleRates": [44100, 48000, 96000],
    "defaults": {...}
  },
  "presets": [...]
}
```

#### 2. **GET /neural/presets**
Lists available presets (built-in and user custom)

#### 3. **POST /neural/presets/create**
Creates a custom synthesis preset

#### 4. **POST /neural/synthesis/validate**
Validates synthesis parameters before applying

#### 5. **POST /neural/audio/export**
Exports audio file in specified format

#### 6. **GET /neural/metrics/quality**
Returns real-time synthesis quality metrics (THD, accuracy, etc.)

---

## Benefits Summary

### For Audio Engineers
✅ Professional-grade synthesis parameter control  
✅ Real-time frequency and waveform adjustment  
✅ Quality metrics and monitoring  
✅ Custom preset creation and management  
✅ Format selection for portability

### For Clinicians  
✅ Therapeutic protocol presets  
✅ Standardized neural entrainment protocols  
✅ Patient-specific session customization  
✅ Audio file archival with metadata  
✅ Compliance-tracked settings management

### For Researchers
✅ Detailed synthesis parameter logging  
✅ Accurate frequency and amplitude control  
✅ Custom experimental protocols  
✅ Data export for analysis  
✅ Reproducible session settings

### For Developers
✅ Centralized settings management  
✅ Extensible waveform synthesis framework  
✅ Real-time parameter updates  
✅ Audit trail for compliance  
✅ Multi-device support

---

## Recommended Implementation Timeline

**Week 1:** Settings state container, localStorage persistence  
**Week 2:** UI components (6 tabs), modal interface  
**Week 2:** Integration into JONA module  
**Week 3:** Backend API endpoints, database schema  
**Week 3:** Testing with therapeutic protocols  
**Week 4:** Documentation, deployment  

---

**Document Version:** 1.0  
**Status:** Analysis Complete | Ready for Phase 1 Implementation  
**Last Updated:** February 19, 2026  
**Module:** JONA Neural Synthesis Engine  
**API Port:** 7777
