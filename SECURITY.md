# Security Policy

Tracepoint is a security-focused research and development project. It is **not production-ready**. Do not connect sensitive production systems, payment data, customer identities, or secrets to the public preview.

## Supported versions

There is no stable supported release yet. Security fixes are prioritized on the default branch.

## Reporting vulnerabilities

**Do not open a public GitHub issue** for exploitable vulnerabilities, credentials, or customer data. Prefer GitHub's **Report a vulnerability** / private vulnerability reporting workflow under the repository Security tab, **if enabled**. If unavailable, contact the maintainer through a private channel listed on their GitHub profile. Do not publish exploit details until coordinated disclosure.

A useful private report includes:
- Affected component and revision
- Reproduction steps using synthetic data
- Security impact and realistic attack conditions
- Suggested mitigation, if known

Do not scan or attack public Tracepoint infrastructure or any third-party system without authorization.

## Security boundaries and known limitations

- The public React preview is synthetic; it is **not** a live threat feed.
- The backend currently uses a shared API key for development, **not** per-analyst authentication.
- Production-grade RBAC, tenant isolation, rate limiting, migrations, and audit protections remain outstanding.
- The dedicated Supabase database exists, but its integration with the deployed API has not been validated.
- Secrets belong in backend environment variables only. Never embed ingestion keys in browser code.
- Geolocation search and mapping can send search queries to third-party providers; avoid sensitive addresses.
- Map tiles and external CDN scripts have availability and supply-chain considerations. Production deployments should use reviewed dependencies and providers.

See [the roadmap](docs/ROADMAP.md) for planned mitigations.
