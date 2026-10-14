# Barakaz integration plan

Status: **design only**. No live connection.

1. Instrument selected server-side security actions (authentication failures, authorization denials, webhook signature failures).
2. Sanitize payloads: no passwords, tokens, payment data, personal addresses, KYC documents or full request bodies.
3. Enqueue events in a durable Barakaz-side outbox; deliver asynchronously over HTTPS.
4. Authenticate using a per-application secret kept only in server-side configuration. Rotate credentials periodically.
5. Include unique event IDs for idempotency; retry with bounded exponential backoff.
6. Validate timestamps and schemas; enforce rate limits and tenant isolation in Tracepoint.
7. Run the first tests against synthetic data and a non-production Barakaz environment.

## Prototype event example

```json
{
  "event_id": "7e16ad24-f7e8-4a85-9977-b69e917c7b02",
  "source": "barakaz-test",
  "event_type": "auth.login_failed",
  "timestamp": "2026-10-14T12:00:00Z",
  "actor_id": "test-user",
  "source_ip": "192.0.2.5"
}
```

The current prototype stores events in memory and **must not** receive production data.
