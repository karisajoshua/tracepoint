from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi.testclient import TestClient
import pytest
from tracepoint import main
from tracepoint.storage import Base, build_engine, get_summary

@pytest.fixture(autouse=True)
def database(monkeypatch, tmp_path):
    monkeypatch.setenv("TRACEPOINT_API_KEY", "test-only-secret")
    engine = build_engine(f"sqlite:///{tmp_path / 'events.db'}")
    Base.metadata.create_all(engine)
    monkeypatch.setattr(main, "engine", engine)
    yield
    engine.dispose()

client = TestClient(main.app)
HEADERS = {"X-API-Key": "test-only-secret"}

def event(timestamp=None):
    return {"event_id": str(uuid4()), "source": "barakaz-test",
            "event_type": "auth.login_failed", "source_ip": "192.0.2.5",
            "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat()}

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_authentication():
    assert client.get("/api/v1/summary").status_code == 401

def test_duplicate_is_idempotent():
    payload = event()
    assert client.post("/api/v1/events", json=payload, headers=HEADERS).status_code == 201
    assert client.post("/api/v1/events", json=payload, headers=HEADERS).json()["status"] == "duplicate"
    assert client.get("/api/v1/summary", headers=HEADERS).json()["total_events"] == 1

def test_brute_force_rule():
    now = datetime.now(timezone.utc) - timedelta(minutes=1)
    responses = [client.post("/api/v1/events", json=event(now + timedelta(seconds=i)), headers=HEADERS) for i in range(10)]
    assert all(r.status_code == 201 for r in responses)
    assert responses[-1].json()["alerts_created"] == 1
    assert client.get("/api/v1/summary", headers=HEADERS).json()["total_alerts"] == 1

def test_rejects_naive_timestamp():
    payload = event()
    payload["timestamp"] = "2026-10-14T12:00:00"
    assert client.post("/api/v1/events", json=payload, headers=HEADERS).status_code == 422

def test_activity():
    client.post("/api/v1/events", json=event(), headers=HEADERS)
    result = client.get("/api/v1/activity?hours=24", headers=HEADERS)
    assert result.status_code == 200
    assert sum(b["events"] for b in result.json()["buckets"]) == 1

def test_persistence(tmp_path):
    client.post("/api/v1/events", json=event(), headers=HEADERS)
    reopened = build_engine(str(main.engine.url))
    try:
        assert get_summary(reopened)["total_events"] == 1
    finally:
        reopened.dispose()

def test_alert_and_event_lists():
    now = datetime.now(timezone.utc) - timedelta(minutes=1)
    for i in range(10):
        response = client.post("/api/v1/events", json=event(now + timedelta(seconds=i)), headers=HEADERS)
        assert response.status_code == 201
    alerts = client.get("/api/v1/alerts", headers=HEADERS)
    events = client.get("/api/v1/events?limit=5", headers=HEADERS)
    assert alerts.status_code == 200
    assert len(alerts.json()["items"]) == 1
    assert events.status_code == 200
    assert len(events.json()["items"]) == 5

def test_invalid_list_limit():
    assert client.get("/api/v1/events?limit=201", headers=HEADERS).status_code == 422
