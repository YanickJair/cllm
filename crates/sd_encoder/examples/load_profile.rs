use sd_encoder::{
    encoder::{SDEncoder, SDEncoderV2},
    types::{FieldImportance, SDCompressionConfig},
};
use std::{fs::File, io::Write};

use serde_json::{json, Value};
use std::time::{Duration, Instant};

struct Scenario {
    input_type: &'static str,
    rows: usize,
    iterations: usize,
    payload: Value,
}

struct ProfileResult {
    input_type: &'static str,
    rows: usize,
    iterations: usize,
    avg_ms: f64,
    p95_ms: f64,
    encodes_per_sec: f64,
    original_tokens: u32,
    compressed_tokens: u32,
    compression_ratio: f32,
    compressed_bytes: usize,
}

fn load_config() -> SDCompressionConfig {
    SDCompressionConfig::new(
        None,
        Some(true),
        Some(false),
        Some(FieldImportance::MEDIUM),
        None,
        Some(vec![
            "debug_payload".to_string(),
            "raw_log".to_string(),
            "trace".to_string(),
        ]),
        Some(320),
        Some(true),
        None,
        vec![
            "id".to_string(),
            "title".to_string(),
            "status".to_string(),
            "priority".to_string(),
        ],
    )
}

fn flat_record_payload() -> Value {
    json!({
        "id": "T-42",
        "title": "Login fails after password reset",
        "status": "open",
        "priority": "high",
        "category": "authentication",
        "description": "Customer cannot log in after resetting their password. The login endpoint returns a generic failure.",
        "owner": "support",
        "updated_at": "2026-05-13T09:00:00Z",
        "debug_payload": "internal diagnostic field excluded from output"
    })
}

fn catalog_payload(rows: usize) -> Value {
    let records: Vec<Value> = (0..rows)
        .map(|i| {
            json!({
                "id": format!("SKU-{i:06}"),
                "title": format!("Industrial sensor model {i}"),
                "status": if i % 7 == 0 { "backorder" } else { "active" },
                "priority": if i % 11 == 0 { "high" } else { "normal" },
                "category": if i % 2 == 0 { "hardware" } else { "software" },
                "description": format!(
                    "Sensor package {i} with calibration notes, warranty terms, deployment hints, and integration details."
                ),
                "metadata": {
                    "region": if i % 3 == 0 { "eu" } else { "us" },
                    "revision": i % 13,
                    "updated_at": "2026-05-13T09:00:00Z"
                },
                "debug_payload": format!("internal diagnostic field that should be excluded for row {i}")
            })
        })
        .collect();

    Value::Array(records)
}

fn nested_ticket_payload(rows: usize) -> Value {
    let tickets: Vec<Value> = (0..rows)
        .map(|i| {
            json!({
                "id": format!("T-{i:06}"),
                "title": format!("Customer escalation {i}"),
                "status": if i % 5 == 0 { "waiting" } else { "open" },
                "priority": if i % 9 == 0 { "critical" } else { "medium" },
                "owner": {
                    "id": format!("U-{:04}", i % 200),
                    "name": format!("Agent {}", i % 200),
                    "department": if i % 4 == 0 { "support" } else { "success" }
                },
                "events": [
                    {"type": "created", "status": "open", "notes": "Initial customer report with account context."},
                    {"type": "triaged", "status": "open", "notes": "Reproduced and assigned to product team."},
                    {"type": "updated", "status": "waiting", "notes": "Waiting for customer confirmation and logs."}
                ],
                "raw_log": format!("verbose diagnostic log for ticket {i}")
            })
        })
        .collect();

    json!({
        "account": {
            "id": "A-4242",
            "name": "Example Enterprise",
            "status": "active"
        },
        "tickets": tickets,
        "trace": "request trace excluded from benchmark output"
    })
}

fn api_response_payload(rows: usize) -> Value {
    let items: Vec<Value> = (0..rows)
        .map(|i| {
            json!({
                "id": format!("evt-{i:06}"),
                "type": if i % 3 == 0 { "payment.failed" } else { "payment.succeeded" },
                "status": if i % 3 == 0 { "failed" } else { "processed" },
                "priority": if i % 17 == 0 { "high" } else { "normal" },
                "source": "billing-api",
                "details": {
                    "account_id": format!("acct-{:05}", i % 500),
                    "amount": 1999 + i,
                    "currency": "USD",
                    "message": "Webhook event generated from the billing processor."
                },
                "created_at": "2026-05-13T09:00:00Z",
                "trace": format!("trace-{i:06}")
            })
        })
        .collect();

    json!({
        "request_id": "req-load-profile",
        "status": "ok",
        "items": items,
        "pagination": {
            "limit": rows,
            "next_cursor": "cursor-next-page"
        }
    })
}

fn scenarios() -> Vec<Scenario> {
    vec![
        Scenario {
            input_type: "flat_record",
            rows: 1,
            iterations: 2_000,
            payload: flat_record_payload(),
        },
        Scenario {
            input_type: "catalog_table",
            rows: 10,
            iterations: 1_000,
            payload: catalog_payload(10),
        },
        Scenario {
            input_type: "catalog_table",
            rows: 100,
            iterations: 300,
            payload: catalog_payload(100),
        },
        Scenario {
            input_type: "catalog_table",
            rows: 1_000,
            iterations: 50,
            payload: catalog_payload(1_000),
        },
        Scenario {
            input_type: "nested_tickets",
            rows: 10,
            iterations: 1_000,
            payload: nested_ticket_payload(10),
        },
        Scenario {
            input_type: "nested_tickets",
            rows: 100,
            iterations: 300,
            payload: nested_ticket_payload(100),
        },
        Scenario {
            input_type: "nested_tickets",
            rows: 1_000,
            iterations: 50,
            payload: nested_ticket_payload(1_000),
        },
        Scenario {
            input_type: "api_response",
            rows: 100,
            iterations: 300,
            payload: api_response_payload(100),
        },
    ]
}

fn percentile_95(durations: &[Duration]) -> Duration {
    let idx = ((durations.len() * 95).div_ceil(100)).saturating_sub(1);
    durations[idx]
}

fn profile_scenario(encoder: &SDEncoderV2, scenario: &Scenario) -> ProfileResult {
    for _ in 0..10 {
        let _ = encoder.encode(&scenario.payload);
    }

    let mut durations = Vec::with_capacity(scenario.iterations);
    let mut total = Duration::ZERO;

    for _ in 0..scenario.iterations {
        let start = Instant::now();
        let output = encoder.encode(&scenario.payload);
        let elapsed = start.elapsed();
        std::hint::black_box(output.compressed.len());
        total += elapsed;
        durations.push(elapsed);
    }

    durations.sort_unstable();
    let output = encoder.encode(&scenario.payload);
    let avg_ms = total.as_secs_f64() * 1_000.0 / scenario.iterations as f64;
    let p95_ms = percentile_95(&durations).as_secs_f64() * 1_000.0;
    to_file(&scenario.payload.to_string(), &scenario.input_type);
    ProfileResult {
        input_type: scenario.input_type,
        rows: scenario.rows,
        iterations: scenario.iterations,
        avg_ms,
        p95_ms,
        encodes_per_sec: 1_000.0 / avg_ms,
        original_tokens: output.n_tokens(),
        compressed_tokens: output.c_tokens(),
        compression_ratio: output.compression_ratio(),
        compressed_bytes: output.compressed.len(),
    }
}

fn to_file(data: &String, f_name: &str) {
    let mut file = File::create(f_name).expect("Could not create file");
    file.write_all(data.as_bytes()).expect("Cannot write to file");
}

fn main() {
    let encoder = SDEncoderV2::new(load_config(), ",");
    let results: Vec<ProfileResult> = scenarios()
        .iter()
        .map(|scenario| profile_scenario(&encoder, scenario))
        .collect();

    println!("| input_type | rows | iterations | avg_ms | p95_ms | encodes/sec | original_tokens | compressed_tokens | compression_ratio | compressed_bytes |");
    println!("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|");

    for result in results {
        println!(
            "| {} | {} | {} | {:.3} | {:.3} | {:.1} | {} | {} | {:.1}% | {} |",
            result.input_type,
            result.rows,
            result.iterations,
            result.avg_ms,
            result.p95_ms,
            result.encodes_per_sec,
            result.original_tokens,
            result.compressed_tokens,
            result.compression_ratio,
            result.compressed_bytes
        );
    }
}
