use std::env;
use std::net::SocketAddr;

use axum::extract::Path;
use axum::http::StatusCode;
use axum::routing::{get, post};
use axum::{Json, Router};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

const UPSTREAM_HEALTH: &str = "/health";
const UPSTREAM_STATUS: &str = "/status";
const UPSTREAM_NODES: &str = "/nodes";
const UPSTREAM_SUBMIT: &str = "/submit";

#[derive(Serialize)]
struct HealthResponse {
    status: &'static str,
    service: &'static str,
    mode: &'static str,
    upstream: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
struct QuantumCircuitRequest {
    qubits: u8,
    #[serde(default)]
    gates: Vec<String>,
    measurements: u32,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: &'static str,
    message: String,
}

#[tokio::main]
async fn main() {
    let upstream = env::var("QUANTUM_UPSTREAM_URL").ok().filter(|v| !v.trim().is_empty());
    let client = Client::builder()
        .timeout(std::time::Duration::from_secs(8))
        .build()
        .expect("failed to build HTTP client");

    let app = Router::new()
        .route("/", get(root))
        .route("/health", get(health))
        .route("/backends", get(backends))
        .route("/algorithms", get(algorithms))
        .route("/simulate", post(simulate))
        .route("/random/{num_bits}", get(random_not_available))
        .route("/entanglement", get(entanglement))
        .with_state(AppState { upstream, client });

    let addr = SocketAddr::from(([0, 0, 0, 0], 8008));
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

#[derive(Clone)]
struct AppState {
    upstream: Option<String>,
    client: Client,
}

async fn root() -> Json<Value> {
    Json(json!({
        "service": "Quantum Computing Service",
        "version": "1.1.0",
        "mode": "real-services-only",
        "status": "operational"
    }))
}

async fn health(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<(StatusCode, Json<HealthResponse>), (StatusCode, Json<ErrorResponse>)> {
    let upstream = state.upstream.clone();
    let Some(base) = upstream.clone() else {
        return Err(error_response(
            StatusCode::SERVICE_UNAVAILABLE,
            "REAL_UPSTREAM_REQUIRED",
            "QUANTUM_UPSTREAM_URL is not configured",
        ));
    };

    let url = format!("{}{}", base.trim_end_matches('/'), UPSTREAM_HEALTH);
    let response = state.client.get(url).send().await.map_err(|_| {
        error_response(
            StatusCode::SERVICE_UNAVAILABLE,
            "UPSTREAM_UNREACHABLE",
            "Real quantum upstream is unreachable",
        )
    })?;

    if !response.status().is_success() {
        return Err(error_response(
            StatusCode::SERVICE_UNAVAILABLE,
            "UPSTREAM_UNHEALTHY",
            "Real quantum upstream health check failed",
        ));
    }

    Ok((
        StatusCode::OK,
        Json(HealthResponse {
            status: "healthy",
            service: "quantum",
            mode: "real-services-only",
            upstream,
        }),
    ))
}

async fn backends(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<(StatusCode, Json<Value>), (StatusCode, Json<ErrorResponse>)> {
    proxy_get(&state, UPSTREAM_NODES).await
}

async fn algorithms(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<(StatusCode, Json<Value>), (StatusCode, Json<ErrorResponse>)> {
    proxy_get(&state, UPSTREAM_STATUS).await
}

async fn simulate(
    axum::extract::State(state): axum::extract::State<AppState>,
    Json(payload): Json<QuantumCircuitRequest>,
) -> Result<(StatusCode, Json<Value>), (StatusCode, Json<ErrorResponse>)> {
    if payload.qubits == 0 || payload.qubits > 64 {
        return Err(error_response(
            StatusCode::UNPROCESSABLE_ENTITY,
            "INVALID_QUBIT_COUNT",
            "Supported qubit range is 1..=64",
        ));
    }

    proxy_post(
        &state,
        UPSTREAM_SUBMIT,
        json!({
            "source": "quantum-rust",
            "ops": ["quantum.simulate"],
            "payload": payload,
            "tags": ["quantum", "real-upstream-only"]
        }),
    )
    .await
}

async fn entanglement(
    axum::extract::State(state): axum::extract::State<AppState>,
) -> Result<(StatusCode, Json<Value>), (StatusCode, Json<ErrorResponse>)> {
    proxy_post(
        &state,
        UPSTREAM_SUBMIT,
        json!({
            "source": "quantum-rust",
            "ops": ["quantum.entanglement.read"],
            "payload": {"request": "entanglement"},
            "tags": ["quantum", "real-upstream-only"]
        }),
    )
    .await
}

async fn random_not_available(
    axum::extract::State(state): axum::extract::State<AppState>,
    Path(num_bits): Path<u8>,
) -> Result<(StatusCode, Json<Value>), (StatusCode, Json<ErrorResponse>)> {
    proxy_post(
        &state,
        UPSTREAM_SUBMIT,
        json!({
            "source": "quantum-rust",
            "ops": ["quantum.random"],
            "payload": {"num_bits": num_bits},
            "tags": ["quantum", "real-upstream-only"]
        }),
    )
    .await
}

async fn proxy_get(
    state: &AppState,
    path: &str,
) -> Result<(StatusCode, Json<Value>), (StatusCode, Json<ErrorResponse>)> {
    let Some(base) = state.upstream.as_ref() else {
        return Err(error_response(
            StatusCode::SERVICE_UNAVAILABLE,
            "REAL_UPSTREAM_REQUIRED",
            "QUANTUM_UPSTREAM_URL is not configured",
        ));
    };

    let url = format!("{}{}", base.trim_end_matches('/'), path);
    let response = state.client.get(url).send().await.map_err(|_| {
        error_response(
            StatusCode::SERVICE_UNAVAILABLE,
            "UPSTREAM_UNREACHABLE",
            "Real quantum upstream is unreachable",
        )
    })?;

    let status = StatusCode::from_u16(response.status().as_u16()).unwrap_or(StatusCode::BAD_GATEWAY);
    let payload = response
        .json::<Value>()
        .await
        .unwrap_or_else(|_| json!({ "error": "UPSTREAM_INVALID_JSON" }));
    Ok((status, Json(payload)))
}

fn error_response(code: StatusCode, error: &'static str, message: &str) -> (StatusCode, Json<ErrorResponse>) {
    (
        code,
        Json(ErrorResponse {
            error,
            message: message.to_string(),
        }),
    )
}

async fn proxy_post(
    state: &AppState,
    path: &str,
    body: Value,
) -> Result<(StatusCode, Json<Value>), (StatusCode, Json<ErrorResponse>)> {
    let Some(base) = state.upstream.as_ref() else {
        return Err(error_response(
            StatusCode::SERVICE_UNAVAILABLE,
            "REAL_UPSTREAM_REQUIRED",
            "QUANTUM_UPSTREAM_URL is not configured",
        ));
    };

    let url = format!("{}{}", base.trim_end_matches('/'), path);
    let response = state
        .client
        .post(url)
        .json(&body)
        .send()
        .await
        .map_err(|_| {
            error_response(
                StatusCode::SERVICE_UNAVAILABLE,
                "UPSTREAM_UNREACHABLE",
                "Real quantum upstream is unreachable",
            )
        })?;

    let status = StatusCode::from_u16(response.status().as_u16()).unwrap_or(StatusCode::BAD_GATEWAY);
    let payload = response
        .json::<Value>()
        .await
        .unwrap_or_else(|_| json!({ "error": "UPSTREAM_INVALID_JSON" }));
    Ok((status, Json(payload)))
}
