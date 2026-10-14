"""Tracepoint security event API."""
from datetime import datetime, timedelta, timezone
import os
from secrets import compare_digest
from uuid import UUID
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from .storage import build_engine, initialize, record_event, get_summary, get_activity

app = FastAPI(title="Tracepoint", version="0.2.0")
engine = build_engine()
initialize(engine)

class SecurityEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: UUID
    source: str = Field(min_length=1, max_length=80)
    event_type: str = Field(min_length=1, max_length=100)
    timestamp: datetime
    actor_id: str | None = Field(default=None, max_length=128)
    source_ip: str | None = Field(default=None, max_length=45)

def require_api_key(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("TRACEPOINT_API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="API key not configured")
    if not x_api_key or not compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/events", status_code=201, dependencies=[Depends(require_api_key)])
def ingest_event(event: SecurityEvent):
    if event.timestamp.tzinfo is None:
        raise HTTPException(status_code=422, detail="Timestamp must include timezone")
    if event.timestamp > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise HTTPException(status_code=422, detail="Timestamp is too far in the future")
    created, alerts = record_event(engine, event)
    return {"status": "accepted" if created else "duplicate", "event_id": str(event.event_id), "alerts_created": alerts}

@app.get("/api/v1/summary", dependencies=[Depends(require_api_key)])
def summary():
    return get_summary(engine)

@app.get("/api/v1/activity", dependencies=[Depends(require_api_key)])
def activity(hours: int = 24):
    if not 1 <= hours <= 168:
        raise HTTPException(status_code=422, detail="hours must be between 1 and 168")
    return {"hours": hours, "buckets": get_activity(engine, hours)}
