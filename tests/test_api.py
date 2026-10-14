from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest

from tracepoint import main


@pytest.fixture(autouse=True)
def reset_state(monkeypatch):
    monkeypatch.setenv("TRACEPOINT_API_KEY", "test-only-secret")
    main._events.clear()
    main._alerts.clear()
    yield
    main._events.clear()
    main._alerts.clear()


client = TestClient(main.app)
HEADERS = {"X-API-Key": "test-only-secret"}


def event(event_type="auth.login_failed", source_ip="192.0.2.5", timestamp=None):
    return {
        "event_id": str(uuid4()),
        "source": "barakaz-test",
        "event_type": event_type,
        "source_ip": source_ip,
        "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat(),
    }


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_requires_authentication():
    assert client.get("/api/v1/summary").status_code == 401


def test_duplicate_is_idempotent():
    payload = event()
    assert client.post("/api/v1/events", json=payload, headers=HEADERS).status_code == 201
    response = client.post("/api/v1/events", json=payload, headers=HEADERS)
    assert response.json()["status"] == "duplicate"
    assert client.get("/api/v1/summary", headers=HEADERS).json()["total_events"] == 1


def test_brute_force_rule():
    now = datetime.now(timezone.utc)
    results = [
        client.post("/api/v1/events", json=event(timestamp=now + timedelta(seconds=i)), headers=HEADERS)
        for i in range(10)
    ]
    assert all(r.status_code == 201 for r in results)
    assert results[-1].json()["alerts_created"] == 1
    summary = client.get("/api/v1/summary", headers=HEADERS).json()
    assert summary["total_alerts"] == 1
    assert summary["alerts_by_severity"] == {"high": 1}


def test_rejects_naive_timestamp():
    payload = event()
    payload["timestamp"] = "2026-10-14T12:00:00"
    assert client.post("/api/v1/events", json=payload, headers=HEADERS).status_code == 422
