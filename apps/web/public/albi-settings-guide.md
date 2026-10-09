# ALBI EEG Settings Tab - Integration Analysis Document

**Document Version:** 1.0  
**Date:** February 19, 2026  
**Module:** `apps/web/app/modules/albi-eeg-live/page.tsx`  
**API Endpoint:** `http://127.0.0.1:6681`  
**Component Type:** Real-time EEG Analysis Interface

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current Architecture Analysis](#current-architecture-analysis)
3. [Settings Tab Design Specification](#settings-tab-design-specification)
4. [Implementation Roadmap](#implementation-roadmap)
5. [Technical Integration Points](#technical-integration-points)
6. [UI/UX Framework](#uiux-framework)
7. [Data Persistence Strategy](#data-persistence-strategy)
8. [API Integration](#api-integration)

---

## Executive Summary

### Current State

The ALBI EEG module at `albi-eeg-live/page.tsx` is a **real-time clinical brainwave analyzer** with:

- **680 lines** of production React code
- **Zero placeholder data** - 100% live API integration
- **WebSocket streaming** for continuous EEG data
- **8-channel display** with real-time metrics polling (1Hz)
- **Professional dark UI** with clinical status indicators

### Gap Analysis

The module currently **lacks a Settings Tab** for user customization. Missing configuration layers:

| Feature | Status | Impact |
|---------|--------|--------|
| Channel selection persistence | Manual state only | Lost on page refresh |
| API endpoint configuration | Hardcoded (6681) | No multi-environment support |
| Display preferences | No UI controls | Light/dark/layout options unavailable |
| Sampling rate adjustment | Fixed backend | No user bandwidth control |
| Export format preferences | Single format | Limited data portability |
| Device/patient profiles | None | Hospital workflows unsupported |
| Notification settings | Not configurable | Alerts always on |
| Session metadata management | Minimal | No custom tags/notes |

### Proposed Solution

**Adaptive Settings Tab with Clinical Features:**

- Tabbed interface at module top
- Persisted to localStorage + backend database
- Hospital-grade device profiles
- Multi-environment API support
- Real-time settings application

---

## Current Architecture Analysis

### Component Structure

**Current State Management:**

```typescript
const [sessionId, setSessionId] = useState<string | null>(null);
const [isRecording, setIsRecording] = useState(false);
const [isPaused, setIsPaused] = useState(false);
const [metrics, setMetrics] = useState<SessionMetrics | null>(null);
const [channels, setChannels] = useState<string[]>([]);
const [channelData, setChannelData] = useState<ChannelData>({});
const [recentEvents, setRecentEvents] = useState<any[]>([]);
const [isConnected, setIsConnected] = useState(false);
const [error, setError] = useState<string | null>(null);
const [selectedChannels, setSelectedChannels] = useState<string[]>([...]);
```

**Analysis:**

- ✅ **Supports channel selection state** (`selectedChannels`)
- ✅ **WebSocket initialization ready** (wsRef `useRef`)
- ✅ **Error handling persistent** (error state visible)
- ❌ **No settings object** - scattered throughout component
- ❌ **No localStorage integration** - all ephemeral state
- ❌ **No settings persister** - state lost on page reload

### Key State Variables

| Variable | Type | Scope | Persistence |
|----------|------|-------|-------------|
| `sessionId` | string \| null | Session-scoped | ❌ Lost on reload |
| `selectedChannels` | string[] | Component-scoped | ❌ Hard reset to [Fp1, Fp2...] |
| `API_BASE` | const | Hardcoded | ❌ No env support |
| `isRecording` | boolean | Session-scoped | ❌ Resets to false |
| `metrics` | SessionMetrics | Session-scoped | ❌ Lost on reload |
| `displayPreferences` | ❌ MISSING | N/A | N/A |
| `apiEndpoints` | ❌ MISSING | N/A | N/A |
| `deviceProfile` | ❌ MISSING | N/A | N/A |

---

## Settings Tab Design Specification

### 1. Visual Layout

```
┌────────────────────────────────────────────────────────┐
│  ALBI EEG ANALYZER                          [⚙️ Settings]  │  ← Tab Button
├────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────┐ │
│ │ ⚙️ SETTINGS                                [✕ Close]│ │  ← Modal Header
│ ├──────────────────────────────────────────────────────┤ │
│ │                                                      │ │
│ │ 📟 DEVICE & API          🎨 DISPLAY       📊 DATA  │ │  ← Tab Navigation
│ │ 🔔 ALERTS               👤 PROFILES       📁 FILES  │ │
│ │                                                      │ │
│ ├──────────────────────────────────────────────────────┤ │
│ │ [Currently viewing: DEVICE & API tab]              │ │
│ │                                                      │ │
│ │ API Configuration:                                 │ │
│ │ ┌──────────────────────────────────────────────┐   │ │
│ │ │ Host: [127.0.0.1____]  Port: [6681___] ✓   │   │ │
│ │ │ Device Type: [Emotiv Pro ▼]                 │   │ │
│ │ │ Sample Rate: [250 Hz ▼] (max 500 Hz)       │   │ │
│ │ │ Channels: [8 ▼] channels                    │   │ │
│ │ └──────────────────────────────────────────────┘   │ │
│ │                                                      │ │
│ │ ✓ Connection Status: ✅ Connected & Verified       │ │
│ │                                                      │ │
│ │ [Test Connection]  [Save Settings]  [Reset]       │ │
│ └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

### 2. Tab Organization

#### Tab 1: **📟 DEVICE & API**

**Purpose:** Hardware and backend configuration

**Settings:**

```typescript
{
  apiHost: string;           // Default: "127.0.0.1"
  apiPort: number;           // Default: 6681
  deviceType: "emotiv"|"neurosky"|"muse"|"openbci"|"g-tec"|"natus"|"philips"|"ge";
  deviceId?: string;         // Serial number or network ID
  sampleRate: number;        // 250, 500, 1000 Hz
  channelCount: number;      // 8, 16, 32, 64 channels
  bufferSize: number;        // 512, 1024, 2048 samples
  enableReferencing: boolean; // Re-referencing mode
  enableFiltering: boolean;   // 0.5-100 Hz bandpass
  autoReconnect: boolean;     // Reconnect on disconnect
  connectionTimeout: number;  // Milliseconds (5000-30000)
}
```

#### Tab 2: **🎨 DISPLAY**

**Purpose:** UI/UX preferences

**Settings:**

```typescript
{
  theme: "dark"|"light"|"high-contrast";
  colorScheme: "clinical"|"research"|"relaxing"|"custom";
  channelLayout: "2x4"|"1x8"|"grid"|"waveform";
  showGrid: boolean;
  showLabels: boolean;
  refreshRate: number;     // 30, 60, 120 Hz display
  amplitudeScale: number;  // Microvolts per division
  timeScale: number;       // Seconds visible
  selectedChannels: string[]; // FP1, FP2, F3, F4, etc.
}
```

#### Tab 3: **📊 DATA**

**Purpose:** Recording and export settings

**Settings:**

```typescript
{
  recordingMode: "continuous"|"event-triggered"|"stimulus-response";
  bufferDuration: number;     // Seconds to keep in memory
  autoExportInterval: number; // 0 = manual, N = minutes
  exportFormats: ["json","csv","edf","eeglab"];
  compressionLevel: number;   // 0-9
  includeMetadata: boolean;
  includeEvents: boolean;
}
```

#### Tab 4: **🔔 ALERTS**

**Purpose:** Notification rules

**Settings:**

```typescript
{
  enableAnomalyAlerts: boolean;
  anomalyThreshold: number;  // 0-100%
  qualityThreshold: number;  // Alert if quality drops below
  enableDesktopNotification: boolean;
  soundEnabled: boolean;
  soundVolume: number;       // 0-100
}
```

#### Tab 5: **👤 PROFILES**

**Purpose:** Preset configurations for clinical scenarios

**Predefined Profiles:**

- **Clinical Standard** - 10-20 system, 8 channels, hospital grade
- **Research Lab** - High-resolution 64-channel setup
- **Home Monitoring** - Wireless, low-power mode
- **ICU Monitoring** - Real-time alerts, continuous recording
- **Neurology Clinic** - Specialized seizure detection settings

#### Tab 6: **📁 FILES**

**Purpose:** Session and data management

**Settings:**

```typescript
{
  autoSaveEnabled: boolean;
  autoSaveIntervalMinutes: number;
  sessionNaming: "auto"|"manual"|"mixed";
  archiveOlderThan: number;  // Days
}
```

---

## Implementation Roadmap

### Phase 1: Settings State Container (Week 1)

**Create:** `context/AlbiSettingsContext.tsx`

```typescript
interface AlbiSettings {
  device: DeviceSettings;
  display: DisplaySettings;
  data: DataSettings;
  alerts: AlertSettings;
  profiles: ProfilesSettings;
  files: FileSettings;
}

const AlbiSettingsContext = createContext<AlbiSettings | null>(null);
const useAlbiSettings = () => useContext(AlbiSettingsContext);
```

**Persistence Layer:**

- Save to localStorage under key `albi-settings:v1`
- Sync with backend PostgreSQL on save button
- Audit trail for compliance

### Phase 2: Settings UI Components (Week 2)

**Create:** `components/AlbiSettingsModal.tsx`

```typescript
export function AlbiSettingsModal({ isOpen, onClose }: Props) {
  const [activeTab, setActiveTab] = useState('device');
  
  const tabs = [
    { id: 'device', label: 'Device & API', icon: Radio },
    { id: 'display', label: 'Display', icon: Eye },
    { id: 'data', label: 'Data', icon: Database },
    { id: 'alerts', label: 'Alerts', icon: Bell },
    { id: 'profiles', label: 'Profiles', icon: Users },
    { id: 'files', label: 'Files', icon: Files }
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <TabNavigation tabs={tabs} active={activeTab} onChange={setActiveTab} />
      {/* Tab content panels */}
      <SettingsActionButtons onSave={...} onReset={...} />
    </Modal>
  );
}
```

### Phase 3: Integrate into Main Component (Week 2)

**Modify:** `albi-eeg-live/page.tsx`

```typescript
export default function ALBIEEGAnalyzer() {
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useAlbiSettings();
  
  useEffect(() => {
    // Apply settings on load
    applySettingsToComponent(settings);
  }, [settings]);

  return (
    <div className="space-y-6">
      <HeaderBar>
        <SettingsButton onClick={() => setShowSettings(true)} />
      </HeaderBar>
      
      <AlbiSettingsModal isOpen={showSettings} onClose={...} />
      {/* Rest of UI */}
    </div>
  );
}
```

### Phase 4: Backend Integration (Week 3)

**Extend:** `albi_user_api.py`

```python
@app.get("/settings/default")
async def get_default_settings():
    return {
        "device": {...},
        "display": {...},
        "data": {...},
        "alerts": {...}
    }

@app.post("/settings/save")
async def save_user_settings(settings: SettingsModel):
    # Persist to PostgreSQL
    # Return confirmation

@app.post("/settings/validate")
async def validate_settings(settings: SettingsModel):
    # Check API connectivity
    # Verify device availability
    # Test data export path

@app.get("/profiles")
async def list_hospital_profiles():
    return [
        {"id": "neurology", "name": "Neurology Ward", ...},
        {"id": "icu", "name": "ICU Monitoring", ...},
        {"id": "research", "name": "Research Lab", ...}
    ]
```

---

## Technical Integration Points

### 1. Channel Selection Persistence

**Current (Ephemeral):**

```typescript
const [selectedChannels, setSelectedChannels] = 
  useState<string[]>(['Fp1', 'Fp2', 'F3', 'F4', 'P3', 'P4', 'O1', 'O2']);
// Lost on: page refresh, browser close, component unmount
```

**Proposed (Persistent):**

```typescript
const { settings } = useAlbiSettings();

useEffect(() => {
  setSelectedChannels(settings.display.selectedChannels || defaultChannels);
}, [settings.display.selectedChannels]);

const handleChannelToggle = (channel: string) => {
  const updated = selectedChannels.includes(channel)
    ? selectedChannels.filter(c => c !== channel)
    : [...selectedChannels, channel];
  
  setSelectedChannels(updated);
  updateSetting('display.selectedChannels', updated);
};
```

### 2. API Endpoint Dynamic Configuration

**Current (Hardcoded):**

```typescript
const API_BASE = 'http://127.0.0.1:6681';  // Hardcoded at build time
```

**Proposed (Configurable):**

```typescript
const { settings } = useAlbiSettings();

const API_BASE = useMemo(() => {
  const { apiHost, apiPort } = settings.device;
  const protocol = settings.device.verifySSL ? 'https' : 'http';
  return `${protocol}://${apiHost}:${apiPort}`;
}, [settings.device]);

// Usage in fetch calls:
const response = await fetch(`${API_BASE}/session/start`, {...});
```

### 3. Display Preferences Application

```typescript
// Theme application
useEffect(() => {
  const root = document.documentElement;
  root.classList.toggle('dark', settings.display.theme === 'dark');
  root.classList.toggle('high-contrast', settings.display.theme === 'high-contrast');
}, [settings.display.theme]);

// UI element visibility
const shouldShowMetrics = settings.display.showMetricsPanel;
const shouldShowQuality = settings.display.showQualityScore;

// Amplitude scaling
const displayAmplitude = (value: number) => {
  const scale = settings.display.amplitudeScale;
  return (value * scale).toFixed(2);
};
```

---

## Data Persistence Strategy

### Layer 1: Browser LocalStorage

**Capacity:** ~10MB per domain  
**Retention:** Survives page reload, persists across sessions  

```typescript
const saveToLocalStorage = (settings: AlbiSettings) => {
  try {
    const serialized = JSON.stringify(settings);
    localStorage.setItem('albi-settings:v1', serialized);
  } catch (e) {
    console.error('LocalStorage write failed:', e);
  }
};
```

### Layer 2: Backend Database (PostgreSQL)

**Schema:**

```sql
ALTER TABLE users ADD COLUMN settings JSONB DEFAULT NULL;
CREATE INDEX idx_users_settings ON users USING GIN(settings);

CREATE TABLE settings_audit (
  id SERIAL PRIMARY KEY,
  user_id UUID NOT NULL,
  previous_settings JSONB,
  new_settings JSONB,
  change_timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## API Integration

### New Backend Endpoints Required

#### 1. **GET /settings/schema**

Returns complete settings schema with defaults and constraints

#### 2. **GET /settings/profiles**

Lists predefined hospital configuration profiles

#### 3. **POST /settings/validate**

Validates settings before applying (connection test, etc.)

#### 4. **POST /session/{id}/apply-settings**

Applies settings in real-time to active session

#### 5. **GET /settings/export**

Exports current settings as shareable file

#### 6. **POST /settings/import**

Imports settings from file/text

---

## Success Metrics

✅ **For Clinical Users:**

- Save device configuration between sessions
- Switch between hospital profiles with one click
- Configure alerts for patient monitoring
- Export session data in preferred format
- Multi-environment support

✅ **For Developers:**

- Centralized settings management
- Dynamic API endpoint configuration
- Device driver abstraction
- Extensible profile system
- Audit trail for compliance

✅ **For Hospital IT:**

- Hospital-wide profile deployment
- Settings backup and recovery
- Device compatibility matrix
- Usage analytics and compliance reporting
- Multi-site synchronization

---

**Document Version:** 1.0  
**Status:** Analysis Complete | Ready for Phase 1 Implementation  
**Last Updated:** February 19, 2026
