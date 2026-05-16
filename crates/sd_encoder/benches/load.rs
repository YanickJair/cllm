use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion, Throughput};
use sd_encoder::{
    encoder::{SDEncoder, SDEncoderV2},
    types::{FieldImportance, SDCompressionConfig},
};
use serde_json::{json, Value};
use std::{hint::black_box, thread, time::Duration};

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

fn payload_size_benchmark(c: &mut Criterion) {
    let encoder = SDEncoderV2::new(load_config(), ",");
    let mut group = c.benchmark_group("encode_payload_size");
    group.sample_size(30);
    group.measurement_time(Duration::from_secs(5));

    for rows in [10_usize, 100, 1_000, 5_000] {
        let payload = catalog_payload(rows);
        group.throughput(Throughput::Elements(rows as u64));
        group.bench_with_input(BenchmarkId::new("catalog_rows", rows), &payload, |b, data| {
            b.iter(|| {
                let output = encoder.encode(black_box(data));
                black_box(output.compressed.len())
            });
        });
    }

    for rows in [10_usize, 100, 1_000] {
        let payload = nested_ticket_payload(rows);
        group.throughput(Throughput::Elements(rows as u64));
        group.bench_with_input(BenchmarkId::new("nested_ticket_rows", rows), &payload, |b, data| {
            b.iter(|| {
                let output = encoder.encode(black_box(data));
                black_box(output.compressed.len())
            });
        });
    }

    group.finish();
}

fn parallel_load_benchmark(c: &mut Criterion) {
    let payload = catalog_payload(100);
    let worker_batch_size = 16_u64;
    let mut group = c.benchmark_group("encode_parallel_load");
    group.sample_size(20);
    group.measurement_time(Duration::from_secs(5));

    for workers in [1_usize, 2, 4, 8] {
        group.throughput(Throughput::Elements(worker_batch_size * workers as u64));
        group.bench_with_input(BenchmarkId::from_parameter(workers), &workers, |b, &workers| {
            b.iter(|| {
                thread::scope(|scope| {
                    for _ in 0..workers {
                        scope.spawn(|| {
                            let encoder = SDEncoderV2::new(load_config(), ",");
                            for _ in 0..worker_batch_size {
                                let output = encoder.encode(black_box(&payload));
                                black_box(output.compressed.len());
                            }
                        });
                    }
                });
            });
        });
    }

    group.finish();
}

criterion_group!(benches, payload_size_benchmark, parallel_load_benchmark);
criterion_main!(benches);
