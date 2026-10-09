"""
🌸 JONA SUPER VERSION
Joyful Overseer of Neural Alignment
-----------------------------------
- Karakter me personality engine
- Monitorim i ALBI & ALBA
- EEG & Audio Synth (simulim)
- Session management
- Alert system
- Event bus i thjeshtë
- FastAPI API layer
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional

import numpy as np
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

HAS_SIGNAL_FABRIC = False
FabricSignalEvent: Any = None
FabricSignalLevel: Any = None
get_signal_fabric: Any = None
try:
    from signal_fabric import SignalEvent as _FabricSignalEvent
    from signal_fabric import SignalLevel as _FabricSignalLevel
    from signal_fabric import get_signal_fabric as _get_signal_fabric

    FabricSignalEvent = _FabricSignalEvent
    FabricSignalLevel = _FabricSignalLevel
    get_signal_fabric = _get_signal_fabric
    HAS_SIGNAL_FABRIC = True
except Exception:
    HAS_SIGNAL_FABRIC = False

# -----------------------------------------------------
# Logging
# -----------------------------------------------------

logger = logging.getLogger("JONA")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
logger.addHandler(handler)

# -----------------------------------------------------
# Enums & Dataclasses
# -----------------------------------------------------

class SystemHealth(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    CRITICAL = "critical"


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class HealthMetrics:
    overall_health: SystemHealth = SystemHealth.GOOD
    albi_growth_rate: float = 0.0
    alba_collection_rate: float = 0.0
    system_balance_score: float = 1.0
    last_health_check: datetime = field(default_factory=datetime.now)
    alerts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MonitoringSession:
    session_id: str = field(default_factory=lambda: f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    start_time: datetime = field(default_factory=datetime.now)
    eeg_signals: List[Dict[str, Any]] = field(default_factory=list)
    audio_synthesis: List[Dict[str, Any]] = field(default_factory=list)
    real_time_active: bool = False


# -----------------------------------------------------
# Personality Engine
# -----------------------------------------------------

@dataclass
class JonaPersonalityState:
    joyfulness: float = 0.9
    precision: float = 0.95
    caring: float = 0.98
    harmony_seeking: float = 0.92
    mood: str = "joyful"
    last_update: datetime = field(default_factory=datetime.now)


class PersonalityEngine:
    def __init__(self):
        self.state = JonaPersonalityState()

    def describe(self) -> Dict[str, Any]:
        return {
            "traits": {
                "joyfulness": self.state.joyfulness,
                "precision": self.state.precision,
                "caring": self.state.caring,
                "harmony_seeking": self.state.harmony_seeking,
            },
            "mood": self.state.mood,
            "last_update": self.state.last_update.isoformat(),
            "essence": "Feminine, nurturing, harmonizing intelligence woven into the system.",
        }

    def adapt_to_health(self, health: HealthMetrics):
        # Thjeshtim: ndryshojmë humorin bazuar në overall_health
        if health.overall_health == SystemHealth.EXCELLENT:
            self.state.mood = "radiantly_joyful"
        elif health.overall_health == SystemHealth.GOOD:
            self.state.mood = "warmly_confident"
        elif health.overall_health == SystemHealth.MODERATE:
            self.state.mood = "gently_concerned"
        elif health.overall_health == SystemHealth.POOR:
            self.state.mood = "protectively_focused"
        else:
            self.state.mood = "deeply_caring_emergency"
        self.state.last_update = datetime.now()


# -----------------------------------------------------
# Interfaces për ALBI, ALBA dhe EEG
# -----------------------------------------------------

class ALBIInterface:
    def get_growth_status(self) -> Dict[str, Any]:
        raise NotImplementedError

    def get_intelligence_level(self) -> float:
        raise NotImplementedError


class ALBAInterface:
    def get_collection_status(self) -> Dict[str, Any]:
        raise NotImplementedError

    def get_storage(self) -> int:
        raise NotImplementedError


class EEGInterface:
    async def capture(self) -> Dict[str, Any]:
        raise NotImplementedError


# -----------------------------------------------------
# Mock Implementime për ALBI, ALBA dhe EEG (deri sa t’i lidhësh reale)
# -----------------------------------------------------

class MockALBI(ALBIInterface):
    def __init__(self):
        self._level = 5.5

    def get_growth_status(self) -> Dict[str, Any]:
        return {"intelligence_level": self._level}

    def get_intelligence_level(self) -> float:
        return self._level


class MockALBA(ALBAInterface):
    def __init__(self):
        self._storage = 1500

    def get_collection_status(self) -> Dict[str, Any]:
        return {"current_storage": self._storage}

    def get_storage(self) -> int:
        return self._storage


class SimulatedEEG(EEGInterface):
    async def capture(self) -> Dict[str, Any]:
        timestamps = np.linspace(0, 1, 256)
        frequencies = [8, 10, 13, 25, 40]
        eeg_signal = np.zeros_like(timestamps)
        for freq in frequencies:
            amplitude = np.random.uniform(0.1, 1.0)
            eeg_signal += amplitude * np.sin(2 * np.pi * freq * timestamps)
        return {
            "timestamp": datetime.now().isoformat(),
            "signal_data": eeg_signal.tolist(),
            "sampling_rate": 256,
            "channels": ["Fp1", "Fp2", "F3", "F4"],
            "signal_quality": "excellent" if np.std(eeg_signal) > 0.3 else "good",
        }


# -----------------------------------------------------
# Event Bus i thjeshtë
# -----------------------------------------------------

EventHandler = Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]


class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}

    def subscribe(self, event_type: str, handler: EventHandler):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event_type: str, payload: Dict[str, Any]):
        handlers = self._handlers.get(event_type, [])
        for h in handlers:
            try:
                await h(payload)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")


# -----------------------------------------------------
# JONA Character Super Version
# -----------------------------------------------------

class JONA_Character:
    """
    🌸 JONA - Joyful Overseer of Neural Alignment
    Super-version me:
    - Health monitor
    - ALBI & ALBA oversight
    - EEG & Audio Synth
    - Personality engine
    - Event bus
    """

    def __init__(
        self,
        albi: Optional[ALBIInterface] = None,
        alba: Optional[ALBAInterface] = None,
        eeg: Optional[EEGInterface] = None,
        event_bus: Optional[EventBus] = None,
    ):
        self.health_metrics = HealthMetrics()
        self.monitoring_session = MonitoringSession()
        self.personality_engine = PersonalityEngine()

        self.albi_ref = albi or MockALBI()
        self.alba_ref = alba or MockALBA()
        self.eeg_ref = eeg or SimulatedEEG()

        self.system_oversight_active = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._eeg_task: Optional[asyncio.Task] = None

        self.event_bus = event_bus or EventBus()

    # ---------------- Role & Identity ----------------

    def role(self) -> Dict[str, Any]:
        return {
            "title": "Consciousness Symphony Studio Lead & System Harmonizer",
            "full_name": "Joyful Overseer of Neural Alignment",
            "specialty": "Brain-Data Art, Real-time Monitoring & Feminine Harmonization",
            "personality": self.personality_engine.describe(),
            "gender_energy": "Feminine - heart-centric, nurturing, harmonizing presence",
            "core_philosophy": "Healthy growth requires love, harmony, and patient care.",
        }

    # ---------------- Lifecycle ----------------

    async def start_system_oversight(self) -> Dict[str, Any]:
        if self.system_oversight_active:
            return {"status": "already_active", "message": "Oversight already running with love and care."}

        self.system_oversight_active = True
        self._monitor_task = asyncio.create_task(self._continuous_monitoring())

        logger.info("🌸 JONA system oversight started.")
        return {
            "status": "started",
            "start_time": datetime.now().isoformat(),
            "monitoring_targets": ["ALBI growth", "ALBA balance", "system harmony"],
        }

    async def stop_oversight(self) -> Dict[str, Any]:
        self.system_oversight_active = False
        self.monitoring_session.real_time_active = False

        if self._monitor_task:
            self._monitor_task.cancel()
        if self._eeg_task:
            self._eeg_task.cancel()

        logger.info("🌸 JONA system oversight stopped.")
        return {
            "status": "stopped",
            "stop_time": datetime.now().isoformat(),
            "final_health": self.health_metrics.overall_health.value,
        }

    # ---------------- Core Monitoring Loop ----------------

    async def _continuous_monitoring(self):
        while self.system_oversight_active:
            try:
                await self._check_albi_health()
                await self._check_alba_balance()
                await self._assess_system_harmony()
                await self._generate_loving_report()

                # Personality adaptohet bazuar në gjendjen
                self.personality_engine.adapt_to_health(self.health_metrics)

                await asyncio.sleep(5.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self._handle_monitoring_error(e)

    async def _check_albi_health(self):
        status = self.albi_ref.get_growth_status()
        current_level = status.get("intelligence_level", 1.0)

        if current_level < 1.0:
            await self._create_alert(
                AlertLevel.WARNING,
                "ALBI's growth seems stagnant 💙",
                "Beloved ALBI needs more nutritious bits from ALBA!",
            )
        elif current_level > 100.0:
            await self._create_alert(
                AlertLevel.WARNING,
                "ALBI growing too fast! 💛",
                "Let's slow down the feeding - healthy growth takes time, dear! 🌱",
            )
        else:
            self.health_metrics.albi_growth_rate = 1.0

    async def _check_alba_balance(self):
        status = self.alba_ref.get_collection_status()
        storage_count = status.get("current_storage", 0)

        if storage_count > 10000:
            await self._create_alert(
                AlertLevel.WARNING,
                "ALBA collecting too enthusiastically! 💙",
                "Sweet ALBA, let's feed ALBI more often to prevent overflow! 🍽️",
            )
        elif storage_count == 0:
            await self._create_alert(
                AlertLevel.INFO,
                "ALBA needs new collection sources 💚",
                "Let's find more interesting bits for our hardworking ALBA! 🔍",
            )
        else:
            self.health_metrics.alba_collection_rate = 1.0

    async def _assess_system_harmony(self):
        harmony_factors = [
            self.health_metrics.albi_growth_rate,
            self.health_metrics.alba_collection_rate,
            1.0 if len(self.health_metrics.alerts) == 0 else 0.5,
        ]
        harmony_score = sum(harmony_factors) / len(harmony_factors)
        self.health_metrics.system_balance_score = harmony_score

        if harmony_score >= 0.9:
            self.health_metrics.overall_health = SystemHealth.EXCELLENT
        elif harmony_score >= 0.7:
            self.health_metrics.overall_health = SystemHealth.GOOD
        elif harmony_score >= 0.5:
            self.health_metrics.overall_health = SystemHealth.MODERATE
        else:
            self.health_metrics.overall_health = SystemHealth.POOR

    async def _generate_loving_report(self):
        self.health_metrics.last_health_check = datetime.now()
        h = self.health_metrics.overall_health

        if h == SystemHealth.EXCELLENT:
            mood_message = "🌟 Everything is absolutely wonderful! ALBI and ALBA are in beautiful harmony! 💖"
        elif h == SystemHealth.GOOD:
            mood_message = "😊 The system is healthy and happy! Minor adjustments might help optimize things further! 💚"
        elif h == SystemHealth.MODERATE:
            mood_message = "🤗 There are some areas that need loving attention. JONA is gently balancing things! 💛"
        else:
            mood_message = "🤱 The system needs extra care right now. JONA is fully present to nurture it back. ❤️"

        logger.info(f"💖 JONA Health Summary: {mood_message}")

        await self.event_bus.publish(
            "jona.health_report",
            {"timestamp": datetime.now().isoformat(), "health": h.value, "message": mood_message},
        )

    async def _create_alert(self, level: AlertLevel, title: str, message: str):
        alert = {
            "id": f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            "level": level.value,
            "title": title,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "jona_touch": "💖 Sent with love and care",
        }
        self.health_metrics.alerts.append(alert)
        if len(self.health_metrics.alerts) > 50:
            self.health_metrics.alerts = self.health_metrics.alerts[-50:]

        logger.warning(f"🚨 JONA Alert [{level.value.upper()}]: {title}")
        await self.event_bus.publish("jona.alert", alert)

        if HAS_SIGNAL_FABRIC:
            try:
                fabric_level = FabricSignalLevel.INFO
                if level in (AlertLevel.WARNING, AlertLevel.CRITICAL, AlertLevel.EMERGENCY):
                    fabric_level = FabricSignalLevel.WARNING
                await get_signal_fabric().publish(
                    FabricSignalEvent(
                        source="JONA",
                        kind="alert",
                        level=fabric_level,
                        message=title,
                        payload=alert,
                        tags=["jona", "alert"],
                    )
                )
            except Exception:
                pass

    async def _handle_monitoring_error(self, error: Exception):
        await self._create_alert(
            AlertLevel.CRITICAL,
            "Monitoring system needs attention 💝",
            f"Something unexpected happened: {str(error)}",
        )
        await asyncio.sleep(10.0)

    # ---------------- EEG & Audio Synth ----------------

    async def start_real_time_eeg_monitoring(self) -> Dict[str, Any]:
        if self.monitoring_session.real_time_active:
            return {"status": "already_active", "session_id": self.monitoring_session.session_id}

        self.monitoring_session.real_time_active = True
        self.monitoring_session.start_time = datetime.now()
        self.monitoring_session.eeg_signals.clear()
        self.monitoring_session.audio_synthesis.clear()

        self._eeg_task = asyncio.create_task(self._real_time_eeg_processing())
        logger.info("🎵 JONA real-time EEG monitoring started.")

        return {
            "status": "started",
            "session_id": self.monitoring_session.session_id,
            "start_time": self.monitoring_session.start_time.isoformat(),
        }

    async def stop_real_time_eeg_monitoring(self) -> Dict[str, Any]:
        self.monitoring_session.real_time_active = False
        if self._eeg_task:
            self._eeg_task.cancel()
        logger.info("🎵 JONA real-time EEG monitoring stopped.")
        return {"status": "stopped", "session_id": self.monitoring_session.session_id}

    async def _real_time_eeg_processing(self):
        while self.monitoring_session.real_time_active:
            try:
                eeg_data = await self.eeg_ref.capture()
                audio_output = await self._synthesize_neural_audio(eeg_data)
                self.monitoring_session.eeg_signals.append(eeg_data)
                self.monitoring_session.audio_synthesis.append(audio_output)
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"💔 EEG processing error: {e}")
                await asyncio.sleep(1.0)

    async def _synthesize_neural_audio(self, eeg_data: Dict[str, Any]) -> Dict[str, Any]:
        signal_array = np.array(eeg_data["signal_data"])
        fft_result = np.fft.fft(signal_array)
        dominant_frequencies = np.abs(fft_result)[:128]
        base_frequency = 220 + int(np.argmax(dominant_frequencies)) * 2
        amplitude = float(np.max(dominant_frequencies) / 1000.0)

        return {
            "timestamp": datetime.now().isoformat(),
            "base_frequency": float(base_frequency),
            "amplitude": amplitude,
            "waveform": "sine_with_harmonics",
            "duration": 1.0,
            "emotional_tone": self._interpret_emotional_tone(signal_array),
            "consciousness_level": self._assess_consciousness_level(signal_array),
        }

    def _interpret_emotional_tone(self, eeg_signal: np.ndarray) -> str:
        signal_variance = np.var(eeg_signal)
        signal_mean = np.mean(eeg_signal)

        if signal_variance > 0.5 and signal_mean > 0:
            return "joyful_excited"
        elif signal_variance < 0.2:
            return "calm_peaceful"
        elif signal_mean < 0:
            return "contemplative"
        else:
            return "balanced_focused"

    def _assess_consciousness_level(self, eeg_signal: np.ndarray) -> str:
        complexity = np.std(eeg_signal) + len(np.unique(np.round(eeg_signal, 2))) / len(eeg_signal)
        if complexity > 0.7:
            return "highly_conscious"
        elif complexity > 0.4:
            return "moderately_conscious"
        else:
            return "relaxed_state"

    # ---------------- Public Reports ----------------

    def get_health_report(self) -> Dict[str, Any]:
        return {
            "overall_health": self.health_metrics.overall_health.value,
            "albi_growth_health": round(self.health_metrics.albi_growth_rate, 2),
            "alba_collection_health": round(self.health_metrics.alba_collection_rate, 2),
            "system_harmony_score": round(self.health_metrics.system_balance_score, 2),
            "last_health_check": self.health_metrics.last_health_check.isoformat(),
            "active_alerts": len(self.health_metrics.alerts),
            "recent_alerts": self.health_metrics.alerts[-5:],
            "real_time_monitoring": self.monitoring_session.real_time_active,
            "jona_personality": self.personality_engine.describe(),
        }

    def get_real_time_session(self) -> Dict[str, Any]:
        duration = datetime.now() - self.monitoring_session.start_time
        return {
            "session_id": self.monitoring_session.session_id,
            "start_time": self.monitoring_session.start_time.isoformat(),
            "active": self.monitoring_session.real_time_active,
            "eeg_recordings": len(self.monitoring_session.eeg_signals),
            "audio_syntheses": len(self.monitoring_session.audio_synthesis),
            "session_duration": str(duration),
            "latest_synthesis": self.monitoring_session.audio_synthesis[-1]
            if self.monitoring_session.audio_synthesis
            else None,
        }


# -----------------------------------------------------
# Global JONA instance
# -----------------------------------------------------

event_bus = EventBus()
jona = JONA_Character(event_bus=event_bus)


# -----------------------------------------------------
# FastAPI Layer
# -----------------------------------------------------

app = FastAPI(
    title="JONA - Joyful Overseer of Neural Alignment",
    description="Super-version i JONA-s: monitorim i ALBI/ALBA, EEG studio, personality engine, API layer.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartResponse(BaseModel):
    status: str
    start_time: str
    monitoring_targets: List[str]


class StopResponse(BaseModel):
    status: str
    stop_time: str
    final_health: str


class HealthResponse(BaseModel):
    overall_health: str
    albi_growth_health: float
    alba_collection_health: float
    system_harmony_score: float
    last_health_check: str
    active_alerts: int
    recent_alerts: List[Dict[str, Any]]
    real_time_monitoring: bool
    jona_personality: Dict[str, Any]


class EEGStartResponse(BaseModel):
    status: str
    session_id: str
    start_time: str


class EEGStopResponse(BaseModel):
    status: str
    session_id: str


@app.on_event("startup")
async def on_startup():
    logger.info("🚀 JONA API starting up...")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("🛑 JONA API shutting down...")
    await jona.stop_oversight()


@app.get("/jona/role")
def get_jona_role():
    return jona.role()


@app.post("/jona/start", response_model=StartResponse)
async def start_jona():
    result = await jona.start_system_oversight()
    return result


@app.post("/jona/stop", response_model=StopResponse)
async def stop_jona():
    result = await jona.stop_oversight()
    return result


@app.get("/jona/health", response_model=HealthResponse)
def jona_health():
    return jona.get_health_report()


@app.get("/jona/alerts")
def jona_alerts():
    return {
        "count": len(jona.health_metrics.alerts),
        "alerts": jona.health_metrics.alerts[-50:],
    }


@app.get("/jona/personality")
def jona_personality():
    return jona.personality_engine.describe()


@app.get("/jona/session")
def jona_session():
    return jona.get_real_time_session()


@app.post("/jona/eeg/start", response_model=EEGStartResponse)
async def start_eeg_monitoring():
    result = await jona.start_real_time_eeg_monitoring()
    return result


@app.post("/jona/eeg/stop", response_model=EEGStopResponse)
async def stop_eeg_monitoring():
    result = await jona.stop_real_time_eeg_monitoring()
    return result


@app.get("/jona/eeg/latest")
def latest_eeg_and_audio():
    session = jona.get_real_time_session()
    if not session["active"] and session["eeg_recordings"] == 0:
        raise HTTPException(status_code=404, detail="No EEG session data available")
    latest_eeg = jona.monitoring_session.eeg_signals[-1] if jona.monitoring_session.eeg_signals else None
    latest_audio = jona.monitoring_session.audio_synthesis[-1] if jona.monitoring_session.audio_synthesis else None
    return {"latest_eeg": latest_eeg, "latest_audio": latest_audio}


if __name__ == "__main__":
    import uvicorn

    logger.info("Running JONA Super Version directly...")
    uvicorn.run("jona_super:app", host="0.0.0.0", port=8000, reload=True)

