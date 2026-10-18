//! Trust module for Clisonix Security Sidecar
//! NO_FAKE_DATA_POLICY enforced: trust scores must be calculated from real telemetry only.

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone, Copy, PartialEq, Eq)]
pub enum TrustLevel {
    Trusted,
    Known,
    Unknown,
    Suspicious,
    Hostile,
    Quarantine,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct TrustScore {
    pub score: u8, // 0-100
    pub level: TrustLevel,
}

impl TrustScore {
    pub fn classify(score: u8) -> TrustLevel {
        match score {
            90..=100 => TrustLevel::Trusted,
            70..=89 => TrustLevel::Known,
            40..=69 => TrustLevel::Unknown,
            20..=39 => TrustLevel::Suspicious,
            1..=19 => TrustLevel::Hostile,
            _ => TrustLevel::Quarantine,
        }
    }
    pub fn new(score: u8) -> Self {
        let level = Self::classify(score);
        Self { score, level }
    }
}
