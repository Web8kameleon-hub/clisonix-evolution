//! Policy module for Clisonix Security Sidecar
//! NO_FAKE_DATA_POLICY enforced: all policy suggestions must be based on real telemetry and trust data.

use serde::{Deserialize, Serialize};
use crate::internal::trust::TrustScore;

#[derive(Debug, Serialize, Deserialize, Clone, Copy, PartialEq, Eq)]
pub enum PolicyDecision {
    Allow,
    Monitor,
    Throttle,
    Block,
    Quarantine,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct PolicySuggestion {
    pub decision: PolicyDecision,
    pub trust: TrustScore,
    pub reason: String,
}

impl PolicySuggestion {
    pub fn new(trust: TrustScore, reason: String) -> Self {
        let decision = match trust.level {
            crate::internal::trust::TrustLevel::Trusted | crate::internal::trust::TrustLevel::Known => PolicyDecision::Allow,
            crate::internal::trust::TrustLevel::Unknown => PolicyDecision::Monitor,
            crate::internal::trust::TrustLevel::Suspicious => PolicyDecision::Throttle,
            crate::internal::trust::TrustLevel::Hostile => PolicyDecision::Block,
            crate::internal::trust::TrustLevel::Quarantine => PolicyDecision::Quarantine,
        };
        Self { decision, trust, reason }
    }
}
