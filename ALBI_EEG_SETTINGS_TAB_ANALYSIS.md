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

```typescript
// Current State Management (lines 42-52)
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

### Data Flow Architecture

```
┌─────────────────────────────────────────┐
│   ALBI EEG React Component (page.tsx)   │
│                                        │
│  ┌─────────────────┐                 │
│  │ Start Session   │                 │
│  └────────┬────────┘                 │
│           │                          │
│  ┌────────▼──────────────┐           │
│  │ Connect WebSocket     │ ──────┐  │
│  │ ws://6681/stream/{id} │       │  │
│  └──────────────────────┘       │  │
│           │                     │  │
│  ┌────────▼──────────────┐      │  │
│  │ Poll Metrics (1Hz)    │      │  │
│  │ GET /session/{id}/... │      │  │
│  └──────────────────────┘      │  │
│           │                     │  │
│  ┌────────▼──────────────┐      │  │
│  │ Render UI             │◄─────┘  │
│  │ - Live Channels       │         │
│  │ - Brainwave Dist.     │         │
│  │ - Quality Score       │         │
│  │ - Hemispheric Bal.    │         │
│  └──────────────────────┘         │
└─────────────────────────────────────────┘
```

**Current Limitations:**

- Settings exist but embedded in components
- No centralized settings state container
- No persistence layer between sessions
- No API settings sync

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
  deviceId: string;          // Serial number or network ID
  sampleRate: number;        // 250, 500, 1000 Hz
  channelCount: number;      // 8, 16, 32, 64 channels
  bufferSize: number;        // 512, 1024, 2048 samples
  enableReferencing: boolean; // Re-referencing mode
  enableFiltering: boolean;   // 0.5-100 Hz bandpass
  autoReconnect: boolean;     // Reconnect on disconnect
  connectionTimeout: number;  // Milliseconds (5000-30000)
  verifySSL: boolean;         // HTTPS verification
}
```

**UI Elements:**

- Text input for host/port
- Dropdown for device type
- Slider for sample rate
- Buttons for connection test
- Status indicator (green/yellow/red)

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
  showMetricsPanel: boolean;
  showQualityScore: boolean;
  showHemisphericBalance: boolean;
  autoScaleAmplitude: boolean;
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
  exportPath: string;         // Directory on backend
  compressionLevel: number;   // 0-9
  includeMetadata: boolean;
  includeEvents: boolean;
  dataEncryption: boolean;
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
  disconnectAlert: boolean;
  soundEnabled: boolean;
  soundVolume: number;       // 0-100
  enableDesktopNotification: boolean;
  enableEmailNotification: boolean;
  emailAddress: string;
}
```

#### Tab 5: **👤 PROFILES**

**Purpose:** Preset configurations for common scenarios

**Settings:**

```typescript
{
  profiles: [
    {
      id: "neurology-clinic",
      name: "Neurology Clinic",
      description: "Standard clinical EEG recording",
      settings: {...deviceSettings, ...displaySettings}
    },
    {
      id: "research-lab",
      name: "Research Lab",
      description: "High-resolution 64-channel research setup",
      settings: {...}
    },
    {
      id: "home-monitoring",
      name: "Home Monitoring",
      description: "Wireless, low-power mode",
      settings: {...}
    }
  ],
  activeProfile: string;
  allowCustomProfiles: boolean;
}
```

#### Tab 6: **📁 FILES**

**Purpose:** Session and data management

**Settings:**

```typescript
{
  autoSaveEnabled: boolean;
  autoSaveIntervalMinutes: number;
  localStorageLimit: number;      // MB
  cloudSyncEnabled: boolean;
  cloudStorageProvider: "aws"|"azure"|"gcs"|"local";
  sessionNaming: "auto"|"manual"|"mixed";
  archiveOlderThan: number;       // Days
  retentionPolicy: "30days"|"90days"|"1year"|"permanent";
}
```

---

## Implementation Roadmap

### Phase 1: Settings State Container (Week 1)

**File:** `context/AlbiSettingsContext.tsx` (NEW)

```typescript
// Phase 1: Core settings schema and context
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

// Phase 1: Persistence layer
const AlbiSettingsPersister = {
  save: async (settings: AlbiSettings) => {
    localStorage.setItem('albi-settings', JSON.stringify(settings));
    await fetch(`${API_BASE}/settings/save`, {...});
  },
  load: async () => {
    const stored = localStorage.getItem('albi-settings');
    return stored ? JSON.parse(stored) : await fetchDefaults();
  }
};
```

### Phase 2: Settings UI Components (Week 2)

**File:** `components/AlbiSettingsModal.tsx` (NEW)

```typescript
// Phase 2: Tab-based settings interface
export function AlbiSettingsModal({ isOpen, onClose }: Props) {
  const [activeTab, setActiveTab] = useState('device');
  const [settings, setSettings] = useAlbiSettings();
  
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
      {activeTab === 'device' && <DeviceSettingsPanel {...} />}
      {activeTab === 'display' && <DisplaySettingsPanel {...} />}
      {/* ... other tabs ... */}
      <SettingsActionButtons onSave={...} onReset={...} />
    </Modal>
  );
}
```

### Phase 3: Integrate into Main Component (Week 2)

**File:** `albi-eeg-live/page.tsx` (MODIFY)

```typescript
// Phase 3: Add settings button to header
export default function ALBIEEGAnalyzer() {
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useAlbiSettings();
  
  useEffect(() => {
    // Apply settings on load
    applySettingsToComponent(settings);
  }, [settings]);

  return (
    <div className="space-y-6">
      {/* Settings button in header */}
      <HeaderBar>
        <SettingsButton onClick={() => setShowSettings(true)} />
      </HeaderBar>
      
      {/* Settings modal */}
      <AlbiSettingsModal isOpen={showSettings} onClose={...} />
      
      {/* Existing UI with dynamic settings applied */}
      {/* ... */}
    </div>
  );
}
```

### Phase 4: Backend Integration (Week 3)

**File:** `albi_user_api.py` (EXTEND)

```python
# Phase 4: Add settings endpoints to FastAPI
@app.get("/settings/default")
async def get_default_settings():
    """Retrieve default settings based on device type"""
    return {
        "device": {...},
        "display": {...},
        "data": {...},
        "alerts": {...},
        "profiles": [...]
    }

@app.post("/settings/save")
async def save_user_settings(settings: SettingsModel):
    """Persist user settings to database"""
    # Save to PostgreSQL users.settings column
    # Return confirmation

@app.post("/settings/validate")
async def validate_settings(settings: SettingsModel):
    """Validate settings before applying"""
    # Check API connectivity
    # Verify device availability
    # Test data export path

@app.get("/profiles")
async def list_hospital_profiles():
    """Return predefined hospital deployment profiles"""
    return [
        {"id": "neurology", "name": "Neurology Ward", ...},
        {"id": "icu", "name": "ICU Monitoring", ...},
        {"id": "research", "name": "Research Lab", ...}
    ]
```

---

## Technical Integration Points

### 1. State Management Flow

```
┌─────────────────────────────────────────────────────┐
│         React Component (page.tsx)                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ AlbiSettingsContext  │
        │  (useState + useEffect)│
        └──────┬───────────────┘
               │
        ┌──────┴──────────────┐
        ▼                     ▼
   localStorage          Backend API
   (sessionStorage)      (PostgreSQL)
        │                     │
        └─────────┬───────────┘
                  ▼
        ┌──────────────────────┐
        │  Persister Service   │
        └──────────────────────┘
```

### 2. Channel Selection Persistence

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
  // Load from settings on mount
  setSelectedChannels(settings.display.selectedChannels || defaultChannels);
}, [settings.display.selectedChannels]);

const handleChannelToggle = (channel: string) => {
  const updated = selectedChannels.includes(channel)
    ? selectedChannels.filter(c => c !== channel)
    : [...selectedChannels, channel];
  
  setSelectedChannels(updated);
  
  // Persist to settings
  updateSetting('display.selectedChannels', updated);
};
```

### 3. API Endpoint Dynamic Configuration

**Current (Hardcoded):**

```typescript
const API_BASE = 'http://127.0.0.1:6681';  // Line 57 - hardcoded
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

### 4. Display Preferences Application

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

## UI/UX Framework

### Component Hierarchy

```
ALBIEEGAnalyzer
├── Header
│   ├── TitleBar
│   └── SettingsButton ← New
│
├── AlbiSettingsModal ← New
│   ├── TabNavigation ← New
│   ├── TabContent
│   │   ├── DeviceSettingsPanel ← New
│   │   ├── DisplaySettingsPanel ← New
│   │   ├── DataSettingsPanel ← New
│   │   ├── AlertsSettingsPanel ← New
│   │   ├── ProfilesSettingsPanel ← New
│   │   └── FilesSettingsPanel ← New
│   ├── SettingsActionButtons ← New
│   └── StatusIndicator ← New
│
├── MetricsHeader (existing)
├── ControlPanel (existing)
└── MainContent (existing)
```

### Settings Button Design

```
┌──────────────────────────────────────────────┐
│  ALBI EEG ANALYZER         [🌡️ 92%] [⚙️] [?] │  ← Header buttons
└──────────────────────────────────────────────┘
                              │    │   │
                              │    │   └─ Help/Info
                              │    └───── Settings (NEW)
                              └────────── Quality Score
```

**Button Specification:**

| Property | Value |
|----------|-------|
| Icon | Gear (⚙️) from lucide-react |
| Position | Header top-right |
| Behavior | Click → Modal overlay |
| Keyboard | Ctrl+, (comma) to open/close |
| Mobile | Icon only, no text |
| State | - Default (gray) / Hover (cyan) / Active (blue) |

### Modal Specification

```typescript
interface AlbiSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  size?: 'small' | 'medium' | 'large';  // Default: 'large' (80vw)
  allowClickOutsideToClose?: boolean;   // Default: false (require explicit X)
}
```

**Modal Styling:**

- Overlay: Semi-transparent dark background (rgba(0,0,0,0.7))
- Modal: slate-900/95 background, border-slate-700
- Width: 80vw max, 400px min
- Height: 80vh scrollable
- Z-index: 50 (above existing UI)
- Animation: Slide-in from right (300ms)

### Form Control Standards

**Text Inputs:**

```tsx
<input
  type="text"
  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-white"
  placeholder="127.0.0.1"
/>
```

**Dropdown/Select:**

```tsx
<select className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-white">
  <option>Emotiv Pro</option>
  <option>NeuroSky MindWave</option>
</select>
```

**Toggle/Checkbox:**

```tsx
<label className="flex items-center gap-2 cursor-pointer">
  <input type="checkbox" className="w-4 h-4 bg-slate-800" />
  <span className="text-white text-sm">Enable Auto-Save</span>
</label>
```

**Slider/Range:**

```tsx
<input
  type="range"
  min="250"
  max="1000"
  step="250"
  className="w-full"
/>
```

---

## Data Persistence Strategy

### Layer 1: Browser LocalStorage

**Purpose:** Immediate user preferences cache  
**Capacity:** ~10MB per domain  
**Reliability:** Survives page reload, persists across sessions  
**Format:** JSON string

**Implementation:**

```typescript
const saveToLocalStorage = (settings: AlbiSettings) => {
  try {
    const serialized = JSON.stringify(settings);
    if (serialized.length > 1000000) { // 1MB safety limit
      console.warn('Settings too large - truncating');
    }
    localStorage.setItem('albi-settings:v1', serialized);
  } catch (e) {
    console.error('LocalStorage write failed:', e);
  }
};

const loadFromLocalStorage = (): AlbiSettings | null => {
  try {
    const stored = localStorage.getItem('albi-settings:v1');
    return stored ? JSON.parse(stored) : null;
  } catch (e) {
    console.error('LocalStorage read failed:', e);
    return null;
  }
};
```

### Layer 2: Backend Database (PostgreSQL)

**Purpose:** Persistent user profile across devices  
**Retention:** User account lifetime  
**Reliability:** ACID transactions, backups  
**Sync:** One-way from client (on save button)

**Schema:**

```sql
-- In existing users table
ALTER TABLE users ADD COLUMN settings JSONB DEFAULT NULL;
ALTER TABLE users ADD COLUMN settings_updated_at TIMESTAMP DEFAULT NOW();
CREATE INDEX idx_users_settings ON users USING GIN(settings);

-- New audit table
CREATE TABLE settings_audit (
  id SERIAL PRIMARY KEY,
  user_id UUID NOT NULL,
  previous_settings JSONB,
  new_settings JSONB,
  change_timestamp TIMESTAMP DEFAULT NOW(),
  change_source VARCHAR(50) -- 'ui', 'import', 'api', 'admin'
);
```

**API Save Endpoint:**

```python
@app.post("/settings/save")
async def save_settings(
    settings: SettingsModel,
    current_user: User = Depends(get_current_user)
):
    """Save user settings to database with audit trail"""
    # 1. Validate settings schema
    try:
        validated = SettingsModel.parse_obj(settings)
    except ValidationError as e:
        return {"error": str(e)}, 400
    
    # 2. Get previous settings for audit
    previous = current_user.settings
    
    # 3. Update database
    db.users.update_one(
        {"_id": current_user.id},
        {
            "$set": {
                "settings": validated.dict(),
                "settings_updated_at": datetime.now()
            }
        }
    )
    
    # 4. Create audit log
    db.settings_audit.insert_one({
        "user_id": current_user.id,
        "previous_settings": previous,
        "new_settings": validated.dict(),
        "change_timestamp": datetime.now(),
        "change_source": "ui"
    })
    
    return {"success": True, "message": "Settings saved"}
```

### Layer 3: Cloud Sync (Optional)

**Purpose:** Cross-device synchronization  
**Providers:** AWS S3 / Azure Blob / Google Cloud Storage  
**Trigger:** Manual sync button or auto-sync on close  

**Implementation:**

```typescript
const syncToCloud = async (settings: AlbiSettings) => {
  const timestamp = new Date().toISOString();
  const key = `albi-settings/${userId}/${timestamp}.json`;
  
  try {
    await fetch(`${API_BASE}/settings/sync-cloud`, {
      method: 'POST',
      body: JSON.stringify({ settings, key })
    });
  } catch (e) {
    console.error('Cloud sync failed:', e);
  }
};
```

---

## API Integration

### New Backend Endpoints Required

#### 1. **GET /settings/schema**

**Purpose:** Retrieve complete settings schema with defaults and constraints

**Response:**

```json
{
  "device": {
    "apiHost": {
      "type": "string",
      "default": "127.0.0.1",
      "description": "API server hostname or IP",
      "pattern": "^([a-zA-Z0-9-\\.]+|\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})$"
    },
    "deviceType": {
      "type": "enum",
      "options": ["emotiv", "neurosky", "muse", "openbci"],
      "default": "emotiv"
    },
    "sampleRate": {
      "type": "number",
      "options": [250, 500, 1000],
      "default": 250
    }
  }
}
```

#### 2. **GET /settings/profiles**

**Purpose:** List predefined hospital configuration profiles

**Response:**

```json
{
  "profiles": [
    {
      "id": "neurology-standard",
      "name": "Neurology Standard Clinical",
      "description": "10-20 system, 8 channels, clinical grade",
      "recommended_for": ["neurology", "general"],
      "device": {...},
      "display": {...},
      "data": {...}
    }
  ]
}
```

#### 3. **POST /settings/validate**

**Purpose:** Validate settings before applying (connection test, etc.)

**Request:**

```json
{
  "device": {
    "apiHost": "127.0.0.1",
    "apiPort": 6681,
    "deviceType": "emotiv"
  }
}
```

**Response:**

```json
{
  "valid": true,
  "warnings": [],
  "errors": [],
  "diagnostics": {
    "api_connection": "✓ OK (45ms)",
    "device_detected": "✓ Emotiv Pro detected",
    "channels_available": 14,
    "sample_rate_supported": [250, 500, 1000]
  }
}
```

#### 4. **POST /session/{id}/apply-settings**

**Purpose:** Apply settings in real-time to active session

**Request:**

```json
{
  "channels_to_enable": ["Fp1", "Fp2", "F3", "F4"],
  "sample_rate": 500,
  "filtering": true
}
```

#### 5. **GET /settings/export**

**Purpose:** Export current settings as shareable file

**Query Params:**

- `format`: 'json' | 'yaml' | 'toml'

**Response:** File download

#### 6. **POST /settings/import**

**Purpose:** Import settings from file/text

**Request:** (multipart form or JSON)

```json
{
  "settings_file_content": {...}
}
```

---

## Implementation Considerations

### Performance Impact

| Setting | Performance Impact | Mitigation |
|---------|-------------------|-----------|
| Real-time settings application | Possible UI lag | Debounce changes (500ms) |
| Large settings object serialization | Memory overhead | Compress using LZ4 or GZIP |
| Frequent localStorage writes | I/O blocking | Write throttling (max 1/sec) |
| WebSocket reconnection on settings change | Connection interruption | Implement graceful reconnect |

### Security Considerations

```typescript
// 1. Sanitize user inputs
const sanitizeSettings = (settings: any): AlbiSettings => {
  return {
    device: {
      apiHost: sanitizeHostname(settings.device.apiHost),
      apiPort: clampNumber(settings.device.apiPort, 1024, 65535),
      // ...
    }
  };
};

// 2. Encrypt sensitive data
const encryptSensitiveFields = (settings: AlbiSettings) => {
  if (settings.device.deviceId) {
    settings.device.deviceId = encrypt(settings.device.deviceId);
  }
};

// 3. CORS validation for API calls
const validateAPIEndpoint = async (host: string, port: number) => {
  try {
    const response = await fetch(
      `http://${host}:${port}/health`,
      { timeout: 5000 }
    );
    return response.status === 200;
  } catch {
    return false;
  }
};
```

### Error Handling

```typescript
try {
  const settings = await loadSettings();
  applySettings(settings);
} catch (error) {
  if (error instanceof SettingsValidationError) {
    showErrorAlert('Invalid settings configuration');
    revertToDefaults();
  } else if (error instanceof StorageError) {
    showWarningAlert('Could not save settings - using temporary storage');
    useInMemoryStorage();
  }
}
```

---

## Adaptation Benefits Summary

### For Clinical Users

✅ Save device configuration between sessions  
✅ Switch between hospital profiles with one click  
✅ Configure alerts for patient monitoring  
✅ Export session data in preferred format  
✅ Multi-environment support (clinic, home, lab)

### For Developers

✅ Centralized settings management  
✅ Dynamic API endpoint configuration  
✅ Device driver abstraction  
✅ Extensible profile system  
✅ Audit trail for compliance

### For Hospital IT

✅ Hospital-wide profile deployment  
✅ Settings backup and recovery  
✅ Device compatibility matrix  
✅ Usage analytics and compliance reporting  
✅ Multi-site synchronization

---

## Recommended Next Steps

1. **Week 1:** Implement `AlbiSettingsContext` and persistence layer
2. **Week 2:** Build Settings Tab UI components
3. **Week 3:** Backend integration and API endpoints
4. **Week 4:** Testing and clinical validation
5. **Week 5:** Documentation and deployment

---

## Document Control

**Document ID:** ALBI-SETTINGS-001  
**Version:** 1.0 (Initial Draft)  
**Last Updated:** 2026-02-19  
**Status:** Analysis Complete | Ready for Phase 1 Implementation  
**Author:** Clisonix Cloud Development Team  
**Review Cycle:** Quarterly or as requirements change
