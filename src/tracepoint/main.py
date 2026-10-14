"""Tracepoint security event API."""
from datetime import datetime, timedelta, timezone
import os
from secrets import compare_digest
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from .schemas import SecurityEvent
from .storage import build_engine, initialize, record_event, get_summary, get_activity, list_alerts, list_events, create_incident, get_incident, list_incidents, update_incident, add_incident_note, list_incident_audit

app = FastAPI(title="Tracepoint", version="0.2.0")
engine = build_engine()
initialize(engine)

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

@app.get("/api/v1/alerts", dependencies=[Depends(require_api_key)])
def alerts(limit: int = 50):
    if not 1 <= limit <= 200:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 200")
    return {"items": list_alerts(engine, limit)}

@app.get("/api/v1/events", dependencies=[Depends(require_api_key)])
def events(limit: int = 50):
    if not 1 <= limit <= 200:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 200")
    return {"items": list_events(engine, limit)}

class IncidentCreate(BaseModel):
    alert_id: int = Field(ge=1)

class IncidentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str | None = None
    owner: str | None = Field(default=None, max_length=100)

class IncidentNoteCreate(BaseModel):
    author: str = Field(min_length=1, max_length=100)
    body: str = Field(min_length=1, max_length=4000)

@app.post("/api/v1/incidents", status_code=201, dependencies=[Depends(require_api_key)])
def open_incident(payload: IncidentCreate):
    result = create_incident(engine, payload.alert_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result

@app.get("/api/v1/incidents", dependencies=[Depends(require_api_key)])
def incidents(limit: int = 50):
    if not 1 <= limit <= 200:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 200")
    return {"items": list_incidents(engine, limit)}

@app.get("/api/v1/incidents/{incident_id}", dependencies=[Depends(require_api_key)])
def incident(incident_id: int):
    result = get_incident(engine, incident_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return result

@app.patch("/api/v1/incidents/{incident_id}", dependencies=[Depends(require_api_key)])
def change_incident(incident_id: int, payload: IncidentUpdate):
    if payload.status is not None and payload.status not in {"open", "investigating", "resolved", "closed"}:
        raise HTTPException(status_code=422, detail="Invalid incident status")
    changes = payload.model_fields_set
    if not changes:
        raise HTTPException(status_code=422, detail="No changes supplied")
    result = update_incident(engine, incident_id, status=payload.status,
                             owner=payload.owner, change_owner="owner" in changes)
    if result is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return result

@app.post("/api/v1/incidents/{incident_id}/notes", status_code=201, dependencies=[Depends(require_api_key)])
def create_note(incident_id: int, payload: IncidentNoteCreate):
    result = add_incident_note(engine, incident_id, payload.author, payload.body)
    if result is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return result

@app.get("/api/v1/incidents/{incident_id}/audit", dependencies=[Depends(require_api_key)])
def incident_audit(incident_id: int):
    result = list_incident_audit(engine, incident_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"items": result}
