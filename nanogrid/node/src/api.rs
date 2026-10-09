use axum::{
    extract::{Query, State},
    response::Html,
    routing::{get, post},
    Json, Router,
};
use base64::{engine::general_purpose::STANDARD as B64, Engine as _};
use protocol::{Message, TideLevel};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};
use tokio::sync::Mutex;

use crate::Metrics;

#[derive(Clone)]
pub struct ApiState {
    pub node_id: u64,
    pub metrics: Arc<Mutex<Metrics>>,
    pub tide_level: Arc<Mutex<TideLevel>>,
    pub external_tx: tokio::sync::mpsc::Sender<Message>,
    pub merge_sync: Arc<Mutex<super::merge_sync_engine::MergeSyncEngine>>,
    pub security_events: Arc<Mutex<Vec<SecurityEvent>>>,
}

#[derive(Clone, Serialize)]
pub struct SecurityEvent {
    pub timestamp_ms: u128,
    pub node_id: u64,
    pub endpoint: String,
    pub action: String,
    pub stigma_level: u8,
    pub ndb_score: f32,
    pub outcome: String,
}

#[derive(Deserialize)]
pub struct SubmitRequest {
    pub ops: Vec<String>, // e.g., ["S", "C"]
    pub payload: String,  // base64 encoded
    pub ttl: Option<u64>,
    pub stigma_level: Option<u8>,
}

#[derive(Serialize)]
pub struct StatusResponse {
    pub state: String, // "Active", etc.
    pub tide: String,
    pub metrics: Metrics,
    pub ndb_score: f32,
    pub ndb_delta: f32,
    pub ndb_threshold: f32,
}

#[derive(Serialize)]
pub struct StateResponse {
    pub state: std::collections::HashMap<String, String>, // key -> base64 value
}

#[derive(Deserialize)]
pub struct StatusQuery {
    pub stigma_level: Option<u8>,
}

#[derive(Deserialize)]
pub struct EventsQuery {
    pub limit: Option<usize>,
}

#[derive(Serialize)]
pub struct SecurityStatusResponse {
    pub node_id: u64,
    pub tide: String,
    pub ndb_score: f32,
    pub ndb_delta: f32,
    pub ndb_threshold: f32,
    pub high_risk: bool,
    pub event_count: usize,
}

pub fn create_router(state: ApiState) -> Router {
    Router::new()
        .route("/submit", get(get_submit_help).post(submit_op))
        .route("/status", get(get_status))
        .route("/security/status", get(get_security_status))
        .route("/security/events", get(get_security_events))
        .route("/peers", get(get_peers))
        .route("/state", get(get_state))
        .route("/dashboard", get(get_dashboard))
        .with_state(state)
}

async fn get_submit_help() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "error": "Method Not Allowed for browser GET",
        "hint": "Use POST /submit with JSON body",
        "example": {
            "ops": ["S", "C"],
            "payload": "AQID",
            "ttl": 10,
            "stigma_level": 2
        }
    }))
}

fn sanitize_stigma_level(level: Option<u8>) -> u8 {
    level.unwrap_or(2).clamp(1, 3)
}

fn compute_ndb_score(metrics: &Metrics) -> f32 {
    let latency_component = (metrics.avg_latency_ms as f32 / 250.0).min(1.0);
    let load_component = metrics.load.clamp(0.0, 1.0);
    let peer_component = (metrics.active_peers as f32 / 12.0).min(1.0);

    // Normalized 0..1 security pressure score.
    latency_component * 0.45 + load_component * 0.40 + peer_component * 0.15
}

fn ndb_threshold() -> f32 {
    0.65
}

fn ndb_delta(score: f32) -> f32 {
    score - ndb_threshold()
}

fn compact_float(value: f32) -> f32 {
    (value * 1000.0).round() / 1000.0
}

async fn append_security_event(
    state: &ApiState,
    endpoint: &str,
    action: &str,
    stigma_level: u8,
    ndb_score: f32,
    outcome: &str,
) {
    let mut events = state.security_events.lock().await;
    events.push(SecurityEvent {
        timestamp_ms: SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis(),
        node_id: state.node_id,
        endpoint: endpoint.to_string(),
        action: action.to_string(),
        stigma_level,
        ndb_score: compact_float(ndb_score),
        outcome: outcome.to_string(),
    });

    // Keep bounded in-memory event list.
    if events.len() > 2000 {
        let overflow = events.len() - 2000;
        events.drain(0..overflow);
    }
}

async fn submit_op(
    State(state): State<ApiState>,
    Json(req): Json<SubmitRequest>,
) -> Json<serde_json::Value> {
    let stigma_level = sanitize_stigma_level(req.stigma_level);
    let metrics = *state.metrics.lock().await;
    let score = compute_ndb_score(&metrics);

    // Map string ops to u8
    let ops: Vec<u8> = req.ops.iter().filter_map(|op| match op.as_str() {
        "S" => Some(1),
        "C" => Some(2),
        "R" => Some(3),
        "E" => Some(4),
        "P" => Some(5),
        "M" => Some(6),
        "F" => Some(7),
        "J" => Some(8),
        "L" => Some(9),
        "D" => Some(10),
        "T" => Some(11),
        "X" => Some(12),
        _ => None,
    }).collect();

    if ops.is_empty() {
        append_security_event(
            &state,
            "/submit",
            "submit-op",
            stigma_level,
            score,
            "rejected-invalid-ops",
        ).await;
        return Json(serde_json::json!({"error": "Invalid ops"}));
    }

    // Decode payload
    let payload = match base64::decode(&req.payload) {
        Ok(p) => p,
        Err(_) => {
            append_security_event(
                &state,
                "/submit",
                "submit-op",
                stigma_level,
                score,
                "rejected-invalid-payload",
            ).await;
            return Json(serde_json::json!({"error": "Invalid payload base64"}));
        }
    };

    let msg = Message {
        ops,
        payload,
        ttl: req.ttl.unwrap_or(10),
        clock: 0, // TODO: real clock
        sig: vec![], // TODO: sign
        node_id: 1, // TODO: real node_id
        flags: 0,
    };

    // Send to external channel
    if let Err(_) = state.external_tx.send(msg).await {
        append_security_event(
            &state,
            "/submit",
            "submit-op",
            stigma_level,
            score,
            "failed-channel-closed",
        ).await;
        return Json(serde_json::json!({"error": "Failed to submit"}));
    }

    append_security_event(
        &state,
        "/submit",
        "submit-op",
        stigma_level,
        score,
        "accepted",
    ).await;

    let response = match stigma_level {
        1 => serde_json::json!({
            "status": "submitted",
            "summary": "accepted"
        }),
        2 => serde_json::json!({
            "status": "submitted",
            "accepted_ops": req.ops,
            "ndb_score": compact_float(score),
            "ndb_delta": compact_float(ndb_delta(score))
        }),
        _ => serde_json::json!({
            "ok": true,
            "n": compact_float(score)
        }),
    };

    Json(response)
}

async fn get_status(
    State(state): State<ApiState>,
    Query(query): Query<StatusQuery>,
) -> Json<serde_json::Value> {
    let stigma_level = sanitize_stigma_level(query.stigma_level);
    let metrics = *state.metrics.lock().await;
    let tide = *state.tide_level.lock().await;
    let score = compute_ndb_score(&metrics);
    let delta = ndb_delta(score);

    let rich = StatusResponse {
        state: "Active".to_string(), // TODO: real state
        tide: format!("{:?}", tide),
        metrics,
        ndb_score: compact_float(score),
        ndb_delta: compact_float(delta),
        ndb_threshold: ndb_threshold(),
    };

    let payload = match stigma_level {
        1 => serde_json::json!({
            "state": rich.state,
            "tide": rich.tide,
            "summary": "stable",
            "ndb_score": rich.ndb_score
        }),
        2 => serde_json::to_value(rich).unwrap_or_else(|_| serde_json::json!({"error": "serialize"})),
        _ => serde_json::json!({
            "t": format!("{:?}", tide),
            "n": compact_float(score)
        }),
    };

    append_security_event(
        &state,
        "/status",
        "read-status",
        stigma_level,
        score,
        "ok",
    ).await;

    Json(payload)
}

async fn get_security_status(
    State(state): State<ApiState>,
) -> Json<SecurityStatusResponse> {
    let metrics = *state.metrics.lock().await;
    let tide = *state.tide_level.lock().await;
    let score = compute_ndb_score(&metrics);
    let delta = ndb_delta(score);
    let threshold = ndb_threshold();
    let event_count = state.security_events.lock().await.len();

    Json(SecurityStatusResponse {
        node_id: state.node_id,
        tide: format!("{:?}", tide),
        ndb_score: compact_float(score),
        ndb_delta: compact_float(delta),
        ndb_threshold: threshold,
        high_risk: score > threshold,
        event_count,
    })
}

async fn get_security_events(
    State(state): State<ApiState>,
    Query(query): Query<EventsQuery>,
) -> Json<Vec<SecurityEvent>> {
    let max_limit = 200;
    let limit = query.limit.unwrap_or(25).clamp(1, max_limit);
    let events = state.security_events.lock().await;
    let mut result: Vec<SecurityEvent> = events.iter().rev().take(limit).cloned().collect();
    result.reverse();
    Json(result)
}

async fn get_peers(
    State(state): State<ApiState>,
) -> Json<serde_json::Value> {
    let metrics = *state.metrics.lock().await;
    let peers: Vec<u64> = (1..=metrics.active_peers as u64).collect();
    Json(serde_json::json!({
        "active_peer_count": metrics.active_peers,
        "peers": peers
    }))
}

async fn get_state(
    State(state): State<ApiState>,
) -> Json<StateResponse> {
    let raw_state = state.merge_sync.lock().await.get_state().clone();
    let mut encoded: HashMap<String, String> = HashMap::new();
    for (k, v) in raw_state {
        encoded.insert(k, B64.encode(v));
    }

    Json(StateResponse { state: encoded })
}

async fn get_dashboard(
    State(state): State<ApiState>,
) -> Html<String> {
    let metrics = state.metrics.lock().await.clone();
    let tide = *state.tide_level.lock().await;
    let state_map = state.merge_sync.lock().await.get_state().clone();

    let mut state_html = String::new();
    for (k, v) in &state_map {
        state_html.push_str(&format!("<li>{}: {}</li>", k, B64.encode(v)));
    }

    let html = format!(
        r#"
        <!DOCTYPE html>
        <html>
        <head>
            <title>Nanogrid Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ background: #f0f0f0; padding: 10px; margin: 10px 0; }}
                .tide {{ color: {}; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>Nanogrid Sovereign Fabric Dashboard</h1>
            <div class="metric">
                <h2>Status</h2>
                <p>State: Active</p>
                <p>Tide: <span class="tide">{:?}</span></p>
            </div>
            <div class="metric">
                <h2>Metrics</h2>
                <p>Active Peers: {}</p>
                <p>Avg Latency: {} ms</p>
                <p>Bandwidth: {} kbps</p>
                <p>Load: {:.2}</p>
            </div>
            <div class="metric">
                <h2>Local State</h2>
                <ul>{}</ul>
            </div>
        </body>
        </html>
        "#,
        match tide {
            protocol::TideLevel::High => "green",
            protocol::TideLevel::Normal => "orange",
            protocol::TideLevel::Low => "red",
        },
        tide,
        metrics.active_peers,
        metrics.avg_latency_ms,
        metrics.bandwidth_kbps,
        metrics.load,
        state_html
    );

    Html(html)
}