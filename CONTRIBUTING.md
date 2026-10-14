# Contributing to Tracepoint

Thanks for helping build Tracepoint, an open-source security event monitoring and investigation platform.

## Quick start

Requirements: Python 3.12+, Node.js 20+, npm, Git.

```bash
git clone https://github.com/karisajoshua/tracepoint.git
cd tracepoint
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
export TRACEPOINT_API_KEY='local-development-only-secret'
uvicorn tracepoint.main:app --reload
```

In another terminal:

```bash
cd dashboard
npm install
npm run dev
```

Open the Vite development URL (typically http://localhost:5173). Use **Explore sample dashboard** to inspect the interface without a backend. The Vite development proxy forwards `/api` to the local FastAPI server.

## Before opening a pull request

1. Check existing issues and discussions to avoid duplicate work.
2. For large changes, open an issue describing the problem and proposed solution.
3. Create a focused feature branch; avoid unrelated changes.
4. Run `pytest -q` for Python changes and `npm run build` in `dashboard/` for frontend changes.
5. Explain the change, how you tested it, and include before/after screenshots for visual work.
6. Do not commit credentials, personal data, real customer events, or private vulnerability details.

## Areas where help is welcome

- Accessible, responsive dashboard components and charts
- Incident investigation workflows and filters
- Detection rules with reproducible tests
- PostgreSQL migrations and reliable event ingestion
- Documentation, developer experience and CI
- Security architecture and threat modeling

## Code review expectations

Use clear, descriptive names and small, reviewable pull requests. Add tests for behavior changes. Treat user-provided security events as untrusted. Avoid dependencies or telemetry that leak data. Never put the backend ingestion API key in browser bundles.

## Security reports

Please do **not** open a public issue with exploitable vulnerabilities, secrets, or private data. Use GitHub's private vulnerability reporting feature if enabled, or contact the repository maintainer privately.

## Community conduct

Be respectful and constructive. Critique code and ideas rather than people. Harassment, discrimination, and sharing others' private information are not acceptable.

## Project status

Tracepoint is under active development and is **not production-ready**. The sample dashboard is a demonstration; it is not a live threat feed.
