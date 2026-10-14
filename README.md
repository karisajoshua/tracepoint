# Tracepoint

**Security Monitoring & Threat Analysis** — Every event tells a story.

Tracepoint is a Python-based security event monitoring and incident investigation platform. The first milestone provides a FastAPI event ingestion service, authentication, basic rule-based detections and tests.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
export TRACEPOINT_API_KEY='replace-with-a-long-random-secret'
uvicorn tracepoint.main:app --reload
pytest
```

On Windows, activate with `.venv\Scripts\activate` and set the environment variable using your shell's syntax.

## API

- `GET /health` — service health
- `POST /api/v1/events` — submit a security event (`X-API-Key` header required)
- `GET /api/v1/summary` — aggregated event and alert counts (`X-API-Key` header required)

## Security note

This initial prototype uses **in-memory storage**. Do not connect production applications or send personal information, credentials, payment information or other sensitive data. Persistent storage, tenant isolation, a durable queue and production-grade authentication are planned.

## Barakaz integration

Barakaz will eventually send minimal, sanitized security events via a server-side adapter. No production integration is active.
