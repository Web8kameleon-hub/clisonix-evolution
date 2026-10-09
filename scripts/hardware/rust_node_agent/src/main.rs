use std::error::Error;
use std::fs;
use std::path::PathBuf;
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use clap::Parser;
use reqwest::blocking::Client;
use reqwest::header::{HeaderMap, HeaderValue, CONTENT_TYPE};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

#[derive(Debug, Parser)]
#[command(name = "oceancore-edge-node")]
#[command(about = "Rust proof-of-life agent for the Clisonix KLOUd bridge contract")]
struct Args {
    #[arg(long, default_value = "http://127.0.0.1:8889")]
    bridge: String,

    #[arg(long, default_value = "scripts/hardware/profiles/oceancore_lab_01.json")]
    profile: PathBuf,

    #[arg(long, default_value_t = 1)]
    count: u32,

    #[arg(long, default_value_t = 5.0)]
    interval: f64,

    #[arg(long, default_value_t = false)]
    forward_to_ocean: bool,

    #[arg(long, default_value_t = false)]
    emit_signal: bool,

    #[arg(long, default_value_t = false)]
    wake_offline: bool,

    #[arg(long, default_value_t = false)]
    forever: bool,

    #[arg(long, default_value = "")]
    node_token: String,

    #[arg(long, default_value_t = false)]
    register_only: bool,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
struct NodeProfile {
    node_id: String,
    #[serde(default = "default_node_class")]
    node_class: String,
    #[serde(default = "default_architecture")]
    architecture: String,
    #[serde(default = "default_runtime")]
    runtime: String,
    #[serde(default = "default_transport")]
    transport: String,
    #[serde(default = "default_firmware_version")]
    firmware_version: String,
    #[serde(default = "default_capabilities")]
    capabilities: Vec<String>,
    #[serde(default)]
    metadata: ProfileMetadata,
    #[serde(default)]
    telemetry_defaults: TelemetryDefaults,
}

#[derive(Debug, Clone, Default, Deserialize, Serialize)]
struct ProfileMetadata {
    #[serde(default = "default_lab_id")]
    lab_id: String,
    #[serde(default = "default_deployment_target")]
    deployment_target: String,
    #[serde(default)]
    concept: String,
    #[serde(default)]
    role: String,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
struct TelemetryDefaults {
    #[serde(default = "default_temperature")]
    temperature_c: f64,
    #[serde(default = "default_power")]
    power_watts: f64,
    #[serde(default = "default_latency")]
    latency_ms: f64,
}

impl Default for TelemetryDefaults {
    fn default() -> Self {
        Self {
            temperature_c: default_temperature(),
            power_watts: default_power(),
            latency_ms: default_latency(),
        }
    }
}

fn default_node_class() -> String { "oceancore-edge".to_string() }
fn default_architecture() -> String { "riscv".to_string() }
fn default_runtime() -> String { "rust".to_string() }
fn default_transport() -> String { "http".to_string() }
fn default_firmware_version() -> String { "0.1.0".to_string() }
fn default_capabilities() -> Vec<String> {
    vec![
        "heartbeat".to_string(),
        "pulse".to_string(),
        "telemetry".to_string(),
        "signal-processing".to_string(),
    ]
}
fn default_lab_id() -> String { "lab-unknown".to_string() }
fn default_deployment_target() -> String { "prototype".to_string() }
fn default_temperature() -> f64 { 41.0 }
fn default_power() -> f64 { 6.0 }
fn default_latency() -> f64 { 8.0 }

fn load_profile(path: &PathBuf) -> Result<NodeProfile, Box<dyn Error>> {
    let raw = fs::read_to_string(path)?;
    let profile = serde_json::from_str::<NodeProfile>(&raw)?;
    Ok(profile)
}

fn build_client(node_token: &str) -> Result<Client, Box<dyn Error>> {
    let mut headers = HeaderMap::new();
    headers.insert(CONTENT_TYPE, HeaderValue::from_static("application/json"));
    if !node_token.trim().is_empty() {
        headers.insert("x-node-token", HeaderValue::from_str(node_token.trim())?);
    }

    let client = Client::builder()
        .default_headers(headers)
        .timeout(Duration::from_secs(10))
        .build()?;
    Ok(client)
}

fn get_json(client: &Client, base_url: &str, endpoint: &str) -> Result<Value, Box<dyn Error>> {
    let url = format!("{}{}", base_url.trim_end_matches('/'), endpoint);
    let response = client.get(url).send()?.error_for_status()?;
    Ok(response.json::<Value>()?)
}

fn post_json(client: &Client, base_url: &str, endpoint: &str, payload: &Value) -> Result<Value, Box<dyn Error>> {
    let url = format!("{}{}", base_url.trim_end_matches('/'), endpoint);
    let response = client.post(url).json(payload).send()?.error_for_status()?;
    Ok(response.json::<Value>()?)
}

fn heartbeat_variation(sequence: u32, scale: f64) -> f64 {
    let phase = (sequence % 5) as f64 - 2.0;
    phase * scale
}

fn build_registration(profile: &NodeProfile) -> Value {
    json!({
        "node_id": profile.node_id,
        "node_class": profile.node_class,
        "architecture": profile.architecture,
        "runtime": profile.runtime,
        "transport": profile.transport,
        "firmware_version": profile.firmware_version,
        "capabilities": profile.capabilities,
        "metadata": profile.metadata,
    })
}

fn build_heartbeat(profile: &NodeProfile, sequence: u32, forward_to_ocean: bool) -> Value {
    json!({
        "node_id": profile.node_id,
        "status": "online",
        "uptime_seconds": (sequence as f64) * 15.0,
        "temperature_c": round_two(profile.telemetry_defaults.temperature_c + heartbeat_variation(sequence, 0.15)),
        "power_watts": round_two(profile.telemetry_defaults.power_watts + heartbeat_variation(sequence + 1, 0.08)),
        "latency_ms": round_two(profile.telemetry_defaults.latency_ms + heartbeat_variation(sequence + 2, 0.35)),
        "telemetry": {
            "mode": "edge-active",
            "queue_depth": sequence % 4,
            "lab_id": profile.metadata.lab_id,
            "deployment_target": profile.metadata.deployment_target,
        },
        "forward_to_ocean": forward_to_ocean,
    })
}

fn build_pulse(profile: &NodeProfile, sequence: u32) -> Value {
    json!({
        "node_id": profile.node_id,
        "signal": "pulse",
        "latency_ms": round_two(profile.telemetry_defaults.latency_ms + heartbeat_variation(sequence + 3, 0.25)),
        "queue_depth": sequence % 4,
        "telemetry": {
            "mode": "edge-active",
            "lab_id": profile.metadata.lab_id,
            "deployment_target": profile.metadata.deployment_target,
            "runtime": profile.runtime,
        },
        "metadata": {
            "source": "rust-cargo-agent",
            "sequence": sequence,
        }
    })
}

fn build_signal(profile: &NodeProfile, sequence: u32, heartbeat: &Value) -> Value {
    json!({
        "ops": ["S"],
        "source": profile.node_id,
        "payload": {
            "signal_type": "hardware.proof-of-life",
            "node_id": profile.node_id,
            "sequence": sequence,
            "lab_id": profile.metadata.lab_id,
            "deployment_target": profile.metadata.deployment_target,
            "metrics": {
                "temperature_c": heartbeat["temperature_c"],
                "power_watts": heartbeat["power_watts"],
                "latency_ms": heartbeat["latency_ms"],
            },
            "timestamp": unix_timestamp(),
        }
    })
}

fn build_wake_signal(profile: &NodeProfile, sequence: u32) -> Value {
    json!({
        "ops": ["S"],
        "source": profile.node_id,
        "payload": {
            "signal_type": "hardware.wake.request",
            "node_id": profile.node_id,
            "sequence": sequence,
            "lab_id": profile.metadata.lab_id,
            "deployment_target": profile.metadata.deployment_target,
            "reason": "auto-wake-offline",
            "timestamp": unix_timestamp(),
        }
    })
}

fn get_node_runtime_state(client: &Client, base_url: &str, node_id: &str) -> Result<Option<String>, Box<dyn Error>> {
    let endpoint = format!("/api/v1/hardware/nodes/{node_id}");
    let payload = get_json(client, base_url, &endpoint)?;
    let state = payload
        .get("node")
        .and_then(|node| node.get("runtime_state"))
        .and_then(Value::as_str)
        .map(|value| value.to_string());
    Ok(state)
}

fn wake_node(client: &Client, base_url: &str, node_id: &str) -> Result<Value, Box<dyn Error>> {
    let payload = json!({
        "node_id": node_id,
        "action": "wake",
        "reason": "auto-wake-offline",
    });
    post_json(client, base_url, "/api/v1/hardware/nodes/control", &payload)
}

fn round_two(value: f64) -> f64 {
    (value * 100.0).round() / 100.0
}

fn unix_timestamp() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_secs())
        .unwrap_or(0)
}

fn main() -> Result<(), Box<dyn Error>> {
    let args = Args::parse();
    let profile = load_profile(&args.profile)?;
    let client = build_client(&args.node_token)?;

    let contract = get_json(&client, &args.bridge, "/api/v1/hardware/contracts/firmware-v0.1")?;
    println!("== Firmware Contract ==");
    println!("{}", serde_json::to_string_pretty(&contract)?);

    let registration = build_registration(&profile);
    let registration_response = post_json(&client, &args.bridge, "/api/v1/hardware/nodes/register", &registration)?;
    println!("== Registration ==");
    println!("{}", serde_json::to_string_pretty(&registration_response)?);

    if args.register_only {
        return Ok(());
    }

    let mut sequence = 1u32;
    loop {
        if args.wake_offline {
            match get_node_runtime_state(&client, &args.bridge, &profile.node_id) {
                Ok(Some(state)) if state == "offline" => {
                    match wake_node(&client, &args.bridge, &profile.node_id) {
                        Ok(response) => {
                            println!("== Wake Action ({}) ==", profile.node_id);
                            println!("{}", serde_json::to_string_pretty(&response)?);
                        }
                        Err(error) => {
                            eprintln!(
                                "Wake action failed for {}: {error}. Continuing with heartbeat/pulse cycle.",
                                profile.node_id
                            );
                        }
                    }

                    if args.emit_signal {
                        let wake_signal = build_wake_signal(&profile, sequence);
                        match post_json(&client, &args.bridge, "/api/v1/signals/publish", &wake_signal) {
                            Ok(signal_response) => {
                                println!("== Wake Signal ({}) ==", profile.node_id);
                                println!("{}", serde_json::to_string_pretty(&signal_response)?);
                            }
                            Err(error) => {
                                eprintln!(
                                    "Wake signal publish failed for {}: {error}. Continuing with heartbeat/pulse cycle.",
                                    profile.node_id
                                );
                            }
                        }
                    }
                }
                Ok(_) => {}
                Err(error) => {
                    eprintln!(
                        "Node state check failed for {}: {error}. Continuing with heartbeat/pulse cycle.",
                        profile.node_id
                    );
                }
            }
        }

        let heartbeat = build_heartbeat(&profile, sequence, args.forward_to_ocean);
        let heartbeat_response = post_json(&client, &args.bridge, "/api/v1/hardware/nodes/heartbeat", &heartbeat)?;
        let total_display = if args.forever { "∞".to_string() } else { args.count.to_string() };
        println!("== Heartbeat {sequence}/{total_display} ==");
        println!("{}", serde_json::to_string_pretty(&heartbeat_response)?);

        let pulse = build_pulse(&profile, sequence);
        let pulse_response = post_json(&client, &args.bridge, "/api/v1/hardware/nodes/pulse", &pulse)?;
        println!("== Pulse {sequence}/{total_display} ==");
        println!("{}", serde_json::to_string_pretty(&pulse_response)?);

        if args.emit_signal && sequence == 1 {
            let signal = build_signal(&profile, sequence, &heartbeat);
            match post_json(&client, &args.bridge, "/api/v1/signals/publish", &signal) {
                Ok(signal_response) => {
                    println!("== Proof-of-Life Signal ==");
                    println!("{}", serde_json::to_string_pretty(&signal_response)?);
                }
                Err(error) => {
                    eprintln!(
                        "Proof-of-life signal publish skipped: {error}. The hardware node will continue sending heartbeats and pulses."
                    );
                }
            }
        }

        if !args.forever && sequence >= args.count {
            break;
        }

        sequence += 1;
        thread::sleep(Duration::from_secs_f64(args.interval));
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample_profile() -> NodeProfile {
        NodeProfile {
            node_id: "oceancore-lab-01".to_string(),
            node_class: default_node_class(),
            architecture: default_architecture(),
            runtime: default_runtime(),
            transport: default_transport(),
            firmware_version: default_firmware_version(),
            capabilities: default_capabilities(),
            metadata: ProfileMetadata {
                lab_id: "bochum-lab-01".to_string(),
                deployment_target: "prototype-lab".to_string(),
                concept: "OceanCore + KLOUd".to_string(),
                role: "edge execution and telemetry node".to_string(),
            },
            telemetry_defaults: TelemetryDefaults::default(),
        }
    }

    #[test]
    fn heartbeat_contains_contract_fields() {
        let heartbeat = build_heartbeat(&sample_profile(), 2, true);
        assert_eq!(heartbeat["node_id"], "oceancore-lab-01");
        assert_eq!(heartbeat["status"], "online");
        assert_eq!(heartbeat["forward_to_ocean"], true);
        assert!(heartbeat["telemetry"]["lab_id"].is_string());
    }

    #[test]
    fn pulse_contains_contract_fields() {
        let pulse = build_pulse(&sample_profile(), 3);
        assert_eq!(pulse["node_id"], "oceancore-lab-01");
        assert_eq!(pulse["signal"], "pulse");
        assert!(pulse["queue_depth"].is_number());
    }

    #[test]
    fn signal_uses_hardware_proof_of_life_type() {
        let heartbeat = build_heartbeat(&sample_profile(), 1, false);
        let signal = build_signal(&sample_profile(), 1, &heartbeat);
        assert_eq!(signal["payload"]["signal_type"], "hardware.proof-of-life");
        assert_eq!(signal["source"], "oceancore-lab-01");
    }
}
