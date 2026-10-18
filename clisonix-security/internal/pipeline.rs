//! Core pipeline: Telemetry → Trust → NDB (NanoDecibel) → Resonance → Stigma → Policy
//! NO_FAKE_DATA_POLICY enforced: çdo hap përdor vetëm të dhëna reale.

use crate::internal::telemetry::TelemetryEvent;
use crate::internal::trust::{TrustScore, TrustLevel};
use crate::internal::policy::{PolicySuggestion, PolicyDecision};
use chrono::Utc;

// --- NDB (NanoDecibel) ---
#[derive(Debug, Clone)]
pub struct NDBScore {
    pub ndb: f64, // 0.0 - 100.0
    pub delta: f64,
}

impl NDBScore {
    pub fn from_telemetry(event: &TelemetryEvent) -> Self {
        // Shembull: latency dhe risk ndikojnë në ndb
        let base = 100.0 - (event.latency_ms as f64 / 10.0);
        let risk = event.risk.unwrap_or(0.0);
        let ndb = (base - risk).clamp(0.0, 100.0);
        let delta = risk - (event.latency_ms as f64 / 100.0);
        Self { ndb, delta }
    }
}

// --- Resonance ---
#[derive(Debug, Clone)]
pub struct Resonance {
    pub value: f64, // 0.0 - 1.0
}

impl Resonance {
    pub fn from_ndb(ndb: &NDBScore) -> Self {
        let value = (ndb.ndb / 100.0).clamp(0.0, 1.0);
        Self { value }
    }
}

// --- Stigma ---
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StigmaLevel {
    Trusted,
    Unknown,
    Suspicious,
    Hostile,
    Quarantine,
}

impl StigmaLevel {
    pub fn from_resonance(res: &Resonance) -> Self {
        match res.value {
            v if v > 0.9 => StigmaLevel::Trusted,
            v if v > 0.7 => StigmaLevel::Unknown,
            v if v > 0.4 => StigmaLevel::Suspicious,
            v if v > 0.2 => StigmaLevel::Hostile,
            _ => StigmaLevel::Quarantine,
        }
    }
}

// --- Pipeline Output ---
#[derive(Debug, Clone)]
pub struct PipelineResult {
    pub event: TelemetryEvent,
    pub trust: TrustScore,
    pub ndb: NDBScore,
    pub resonance: Resonance,
    pub stigma: StigmaLevel,
    pub policy: PolicySuggestion,
    pub timestamp: i64,
}

pub fn process_event(event: TelemetryEvent) -> PipelineResult {
    let trust = TrustScore::new(estimate_trust(&event));
    let ndb = NDBScore::from_telemetry(&event);
    let resonance = Resonance::from_ndb(&ndb);
    let stigma = StigmaLevel::from_resonance(&resonance);
    let policy = PolicySuggestion::new(trust, format!("Stigma: {:?}", stigma));
    PipelineResult {
        event,
        trust,
        ndb,
        resonance,
        stigma,
        policy,
        timestamp: Utc::now().timestamp(),
    }
}

// Shembull i thjeshtë për trust score (mund të zëvendësohet me logjikë më të avancuar)
fn estimate_trust(event: &TelemetryEvent) -> u8 {
    let mut score = 80u8;
    if let Some(risk) = event.risk {
        if risk > 80.0 {
            score = 10;
        } else if risk > 50.0 {
            score = 40;
        }
    }
    if event.latency_ms > 1000 {
        score = score.saturating_sub(20);
    }
    score
}
