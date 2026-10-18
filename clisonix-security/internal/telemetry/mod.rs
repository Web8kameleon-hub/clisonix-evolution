//! Telemetry module for Clisonix Security Sidecar
//! NO_FAKE_DATA_POLICY enforced: all telemetry must be real, no mock or synthetic data.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct TelemetryEvent {
    pub timestamp: DateTime<Utc>,
    pub source_ip: String,
    pub endpoint: String,
    pub latency_ms: u64,
    pub method: String,
    pub status: u16,
    pub route: String,
    pub auth: Option<String>,
    pub risk: Option<f64>,
    pub error: Option<String>,
    pub correlation_id: Option<String>,
}

impl TelemetryEvent {
    pub fn new(
        source_ip: String,
        endpoint: String,
        latency_ms: u64,
        method: String,
        status: u16,
        route: String,
        auth: Option<String>,
        risk: Option<f64>,
        error: Option<String>,
        correlation_id: Option<String>,
    ) -> Self {
        Self {
            timestamp: Utc::now(),
            source_ip,
            endpoint,
            latency_ms,
            method,
            status,
            route,
            auth,
            risk,
            error,
            correlation_id,
        }
    }
}
