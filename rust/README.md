# Rust in Tracepoint

Tracepoint retains React/TypeScript for the SOC dashboard and Python/FastAPI for HTTP APIs, incident workflows and integrations. Rust is introduced **incrementally** for CPU-intensive, deterministic event processing.

## Initial crate

`tracepoint-events` validates and normalizes the JSON event contract without network or database access.

```bash
cd rust/tracepoint-events
cargo fmt --all -- --check
cargo clippy --all-targets -- -D warnings
cargo test
```

Run the optional normalization microbenchmark with `cargo run --release --example throughput -- 100000`. This measures a single Rust code path only; do not compare it with API throughput or Python without matching workloads and hardware. Shared fixtures live in `contracts/security_event_cases.json` and are exercised by the Rust test suite. Python parity is a separate acceptance gate because the existing Python API still has validation differences.

Requires a maintained Rust stable toolchain. The crate is not yet invoked by the Python API, and no throughput improvement is claimed.

## Integration strategy

1. Stabilize the event contract and compare Python/Rust behavior using shared fixtures.
2. Benchmark realistic event batches against the Python implementation.
3. Introduce an explicit integration boundary only if benchmarks justify it: a separate Rust worker via a queue, or a PyO3 extension. Document deployment and failure handling in an ADR.
4. Preserve Python as the API and incident orchestration layer, with PostgreSQL as the persistence boundary.
5. Never silently fall back to processing malformed events or claim Rust is active in production before integration is verified.

## Security expectations

Use bounded payloads at ingress, reject malformed inputs, avoid unsafe Rust without an approved design, audit dependencies, and test canonicalization consistency. This crate deliberately has no access to production credentials or Supabase.

## Architectural decision

See [ADR-0002](../docs/adr/0002-rust-event-processing.md) for the decision gates and tradeoffs between keeping Python, PyO3 and a standalone Rust worker.
