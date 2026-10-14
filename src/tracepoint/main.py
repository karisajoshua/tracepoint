"""Tracepoint prototype API. Data is in-memory; not for production."""
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from enum import Enum
import os
from threading import RLock
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Tracepoint", version="0.1.0")


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class SecurityEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: UUID
    source: str = Field(min_length=1, max_length=80)
    event_type: str = Field(min_length=1, max_length=100)
    timestamp: datetime
    actor_id: str | None = Field(default=None, max_length=128)
    source_ip: str | None = Field(default=None, max_length=45)
    metadata: dict[str, str | int | bool] = Field(default_factory=dict)


class Alert(BaseModel):
    event_id: UUID
    source: str
    event_type: str
    severity: Severity
    reason: str
    detected_at: datetime


_events: dict[UUID, SecurityEvent] = {}
_alerts: list[Alert] = []
_lock = RLock()


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    from secrets import compare_digest
    expected = os.getenv("TRACEPOINT_API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="API key not configured")
    if not x_api_key or not compare_digest(x_api_key, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/events", status_code=201, dependencies=[Depends(require_api_key)])
def ingest_event(event: SecurityEvent) -> dict:
    if event.timestamp.tzinfo is None:
        raise HTTPException(status_code=422, detail="Timestamp must include timezone")
    now = datetime.now(timezone.utc)
    if event.timestamp > now + timedelta(minutes=5):
        raise HTTPException(status_code=422, detail="Timestamp is too far in the future")

    with _lock:
        if event.event_id in _events:
            return {"status": "duplicate", "event_id": str(event.event_id), "alerts_created": 0}

        _events[event.event_id] = event
        created = 0
        # One alert when the 10th failure occurs in a 2-minute window.
        if event.event_type == "auth.login_failed":
            window_start = event.timestamp - timedelta(minutes=2)
            matches = [
                e for e in _events.values()
                if e.source == event.source
                and e.event_type == "auth.login_failed"
                and e.source_ip == event.source_ip
                and e.source_ip is not None
                and window_start <= e.timestamp <= event.timestamp
            ]
            if len(matches) == 10:
                _alerts.append(Alert(
                    event_id=event.event_id,
                    source=event.source,
                    event_type="auth.brute_force_suspected",
                    severity=Severity.high,
                    reason="10 failed logins from one source IP in 2 minutes",
                    detected_at=now,
                ))
                created = 1

        return {"status": "accepted", "event_id": str(event.event_id), "alerts_created": created}


@app.get("/api/v1/summary", dependencies=[Depends(require_api_key)])
def summary() -> dict:
    with _lock:
        return {
            "total_events": len(_events),
            "total_alerts": len(_alerts),
            "events_by_type": dict(Counter(e.event_type for e in _events.values())),
            "alerts_by_severity": dict(Counter(a.severity.value for a in _alerts)),
        }
