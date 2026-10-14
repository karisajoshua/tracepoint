# Tracepoint

**Security Monitoring & Threat Analysis** — *Every event tells a story.*

Tracepoint is an open-source security event monitoring and incident investigation project, built with Python/FastAPI, SQLAlchemy/PostgreSQL and React/TypeScript. It is under active development and **not production-ready**.

**[Live dashboard preview](https://tracepoint-beryl.vercel.app)** · **[Contribute](CONTRIBUTING.md)** · **[Issues](https://github.com/karisajoshua/tracepoint/issues)**

## What works today

- Authenticated event ingestion with idempotency and a basic failed-login detection rule
- Event and alert summaries, hourly activity and investigation endpoints
- Persistent incident cases with status, ownership, notes and change history
- Responsive dashboard with event chart, severity filters and investigation details
- **Read-only sample-data preview** for contributors and visitors (synthetic data only)
- Automated Python tests and dashboard build checks

## Local development

Requirements: Python 3.12+ and Node.js 20+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
export TRACEPOINT_API_KEY='local-development-secret'
uvicorn tracepoint.main:app --reload
```

Then in a second terminal:

```bash
cd dashboard
npm install
npm run dev
```

The dashboard's **Explore sample dashboard** option works without an API connection. The Vite dev proxy forwards `/api` to `localhost:8000`. On Windows, activate the virtual environment using `.venv\\Scripts\\activate` and set environment variables with your shell.

For a local demonstration with synthetic events:

```bash
python scripts/demo_events.py
```

The generator accepts only a local API URL. Use `TRACEPOINT_DATABASE_URL` for a PostgreSQL connection; otherwise the backend uses a local SQLite database for development.

## API endpoints

- `GET /health`
- `POST /api/v1/events`
- `GET /api/v1/summary`
- `GET /api/v1/activity`
- `GET /api/v1/events`, `GET /api/v1/alerts`
- `GET/POST /api/v1/incidents`
- `GET/PATCH /api/v1/incidents/{id}`
- `POST /api/v1/incidents/{id}/notes`
- `GET /api/v1/incidents/{id}/audit`

All `/api/v1` endpoints currently use a shared `X-API-Key` development credential. This is **not suitable as a production browser authentication design**.

## Roadmap

Analyst identity and RBAC, migrations, production-safe API routing, event pipeline hardening, detection expansion, accessible investigation workflows, and real-time monitoring.

## Contributing

Contributions, bug reports, design improvements, documentation and tests are welcome. Read **[CONTRIBUTING.md](CONTRIBUTING.md)** before submitting a pull request. Please report security vulnerabilities privately rather than opening a public issue.

## Security and data privacy

Never send production credentials, personal information, payment data, or customer security events to the public demo. The dashboard preview uses **synthetic data only**. Barakaz is not connected to Tracepoint.
