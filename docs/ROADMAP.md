# Tracepoint Engineering Roadmap

This document is a prioritized **plan**, not a claim of completed functionality.

## Phase 0 — Open-source foundation

- [x] Public source repository, contributor guide, issue and PR templates
- [x] Python API tests and dashboard build CI
- [x] Synthetic public dashboard preview
- [x] Interactive 2D mapping and initial 3D map implementation
- [x] Publish Apache License 2.0 (previous revisions used MIT)
- [ ] Verify clean-room contributor setup and map build/deployment
- [ ] Add branch protection and required checks (repository administrator)
- [x] Configure automated dependency review, Dependabot, CodeQL and packaging checks (verify workflow execution)
- [ ] Add accessible automated frontend tests

## Phase 1 — Production foundations

- [ ] Reconcile SQLAlchemy models with Supabase and introduce versioned migrations
- [ ] Implement secure analyst login, RBAC and scoped ingestion credentials
- [ ] Add rate limiting, validation limits, event retention and privacy controls
- [ ] Implement backend integration and deployment verification
- [ ] Publish a stable versioned event schema and OpenAPI examples

## Phase 2 — Detection and investigation

- [ ] Extract dashboard widgets and feature modules
- [ ] Build a pluggable, testable detection rule interface
- [ ] Improve incident auditability and evidence provenance
- [ ] Add advanced filtering, saved workspaces and server-side preferences
- [ ] Enrich events with geolocation and show real map markers with source attribution

## Phase 3 — Operations and ecosystem

- [ ] Health and ingestion observability, structured logs, error budgets
- [ ] Threat intelligence connectors and integration contract tests
- [ ] Performance/load testing and documented resource requirements
- [ ] Security review, release process, changelog and contributor recognition

## Suggested contribution difficulty

**Good first issue:** accessibility improvements, docs, reproducible UI bugs, test fixtures.

**Intermediate:** widget extraction, filter UX, API validation tests, event schema docs.

**Advanced:** migrations, auth/RBAC, ingestion hardening, secure geolocation enrichment, rule engine.

Claim an issue before starting large changes. See [CONTRIBUTING.md](../CONTRIBUTING.md).
