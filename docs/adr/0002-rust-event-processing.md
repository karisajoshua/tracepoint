# ADR-0002: Rust as an isolated event normalization component

- **Status:** Proposed (not yet deployed)
- **Date:** 2026-10-16
- **Scope:** Event validation, normalization, and high-throughput detection

## Context

Tracepoint currently uses FastAPI and SQLAlchemy for HTTP ingestion and persistence. The new Rust crate performs deterministic validation without external side effects. A new language adds operational and contributor complexity; it should be justified by measurable benefits.

## Options considered

1. **Keep Python only:** least deployment complexity, mature integration; may suffice at current scale.
2. **PyO3/maturin Python extension:** in-process calls and minimal serialization overhead, but platform-specific wheels and native crashes affect the API process.
3. **Standalone Rust worker:** independent scaling, isolation and explicit backpressure, but introduces queues, retries, schema versioning and operations overhead.

## Proposed decision

**Do not integrate Rust into production yet.** First publish a versioned event contract, shared conformance fixtures and reproducible throughput benchmarks. Keep Python as the system of record for API authorization and incident workflows. If profiling demonstrates a real CPU bottleneck, prefer a standalone worker for high-volume asynchronous enrichment/detection; consider PyO3 only if in-process latency dominates and packaging can be maintained.

## Security and correctness

- Never let Rust bypass API authorization, event size limits, or persistence invariants.
- Explicitly version the event schema; compare Python/Rust canonicalization and rejection behavior.
- Bound queues and batch sizes; implement retry limits, idempotency and dead-letter handling before worker rollout.
- Keep source timestamps and source IPs provenance-aware; do not invent geolocation.
- Avoid introducing native extension dependencies into the public dashboard.

## Verification and rollback

- Rust: cargo fmt, clippy and tests.
- Python: existing API tests and contract conformance tests.
- Benchmarks: report throughput, p95 latency, memory and hardware under equivalent workloads.
- Rollout: shadow mode, compare outputs, then gradual opt-in with metrics.
- Rollback: disable Rust processing and use the existing Python path without schema changes.

## Consequences

Tracepoint gains an independently testable Rust component now, without premature infrastructure changes. Production adoption requires further evidence and a separate reviewed implementation.
