//! Lightweight, reproducible normalization microbenchmark.
//! Usage: cargo run --release --example throughput -- 100000
//! This is NOT an end-to-end ingestion or Python comparison benchmark.
use std::env;
use std::time::Instant;
use tracepoint_events::parse_and_normalize;

fn main() {
    let iterations: usize = env::args()
        .nth(1)
        .unwrap_or_else(|| "100000".to_owned())
        .parse()
        .expect("iterations must be a positive integer");
    assert!(
        (1..=10_000_000).contains(&iterations),
        "iterations out of range"
    );

    let payload = r#"{"event_id":"123e4567-e89b-42d3-a456-426614174000","source":"auth-service","event_type":"auth.login_failed","timestamp":"2026-10-16T00:00:00Z","actor_id":"user-1","source_ip":"2001:db8::1"}"#;

    // Warm up allocation paths before measuring.
    for _ in 0..1000 {
        std::hint::black_box(parse_and_normalize(payload).expect("valid sample"));
    }

    let started = Instant::now();
    for _ in 0..iterations {
        std::hint::black_box(
            parse_and_normalize(std::hint::black_box(payload)).expect("valid sample"),
        );
    }
    let seconds = started.elapsed().as_secs_f64();
    println!(
        "iterations={iterations} elapsed_s={seconds:.6} events_per_second={:.0}",
        iterations as f64 / seconds
    );
    println!("This measures Rust JSON normalization only; no API, network, database or queue.");
}
