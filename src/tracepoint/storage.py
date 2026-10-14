from datetime import datetime, timedelta, timezone
import os
from sqlalchemy import create_engine, String, DateTime, Integer, ForeignKey, Text, select, func
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class EventRow(Base):
    __tablename__ = 'security_events'
    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source: Mapped[str] = mapped_column(String(80), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actor_id: Mapped[str | None] = mapped_column(String(128))
    source_ip: Mapped[str | None] = mapped_column(String(45), index=True)

class AlertRow(Base):
    __tablename__ = 'security_alerts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey('security_events.event_id'))
    source: Mapped[str] = mapped_column(String(80))
    event_type: Mapped[str] = mapped_column(String(100))
    severity: Mapped[str] = mapped_column(String(12))
    reason: Mapped[str] = mapped_column(String(250))
    detected_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

class IncidentRow(Base):
    __tablename__ = "incidents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_id: Mapped[int] = mapped_column(Integer, ForeignKey("security_alerts.id"), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    owner: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class IncidentNoteRow(Base):
    __tablename__ = "incident_notes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_id: Mapped[int] = mapped_column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class IncidentAuditRow(Base):
    __tablename__ = "incident_audit"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_id: Mapped[int] = mapped_column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

def build_engine(url=None):
    return create_engine(url or os.getenv("TRACEPOINT_DATABASE_URL", "sqlite:///./tracepoint.db"), pool_pre_ping=True)

def initialize(engine):
    Base.metadata.create_all(engine)

def record_event(engine, event):
    with Session(engine) as session, session.begin():
        if session.get(EventRow, str(event.event_id)) is not None:
            return False, 0
        session.add(EventRow(event_id=str(event.event_id), source=event.source, event_type=event.event_type,
                             timestamp=event.timestamp, actor_id=event.actor_id, source_ip=event.source_ip))
        session.flush()
        if event.event_type != "auth.login_failed" or not event.source_ip:
            return True, 0
        count = session.scalar(select(func.count()).select_from(EventRow).where(
            EventRow.source == event.source, EventRow.event_type == "auth.login_failed",
            EventRow.source_ip == event.source_ip,
            EventRow.timestamp >= event.timestamp - timedelta(minutes=2),
            EventRow.timestamp <= event.timestamp))
        if count == 10:
            session.add(AlertRow(event_id=str(event.event_id), source=event.source,
                event_type="auth.brute_force_suspected", severity="high",
                reason="10 failed logins from one source IP in 2 minutes",
                detected_at=datetime.now(timezone.utc)))
            return True, 1
        return True, 0

def get_summary(engine):
    with Session(engine) as session:
        events = dict(session.execute(select(EventRow.event_type, func.count()).group_by(EventRow.event_type)).all())
        alerts = dict(session.execute(select(AlertRow.severity, func.count()).group_by(AlertRow.severity)).all())
        return {"total_events": sum(events.values()), "total_alerts": sum(alerts.values()),
                "events_by_type": events, "alerts_by_severity": alerts}

def get_activity(engine, hours=24):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    with Session(engine) as session:
        timestamps = session.scalars(select(EventRow.timestamp).where(EventRow.timestamp >= since)).all()
    counts = {}
    for stamp in timestamps:
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        bucket = stamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:00:00Z")
        counts[bucket] = counts.get(bucket, 0) + 1
    return [{"time": k, "events": v} for k, v in sorted(counts.items())]

def list_alerts(engine, limit=50):
    with Session(engine) as session:
        rows = session.scalars(select(AlertRow).order_by(AlertRow.detected_at.desc()).limit(limit)).all()
        return [{"id": a.id, "event_id": a.event_id, "source": a.source,
                 "event_type": a.event_type, "severity": a.severity,
                 "reason": a.reason, "detected_at": a.detected_at.isoformat()} for a in rows]

def list_events(engine, limit=50):
    with Session(engine) as session:
        rows = session.scalars(select(EventRow).order_by(EventRow.timestamp.desc()).limit(limit)).all()
        return [{"event_id": e.event_id, "source": e.source, "event_type": e.event_type,
                 "timestamp": e.timestamp.isoformat(), "actor_id": e.actor_id,
                 "source_ip": e.source_ip} for e in rows]

def incident_detail(session, incident):
    alert = session.get(AlertRow, incident.alert_id)
    notes = session.scalars(select(IncidentNoteRow).where(
        IncidentNoteRow.incident_id == incident.id).order_by(IncidentNoteRow.created_at)).all()
    return {"id": incident.id, "alert_id": incident.alert_id, "status": incident.status,
            "owner": incident.owner, "created_at": incident.created_at.isoformat(),
            "updated_at": incident.updated_at.isoformat(),
            "severity": alert.severity, "source": alert.source,
            "event_type": alert.event_type, "reason": alert.reason,
            "notes": [{"id": n.id, "author": n.author, "body": n.body,
                       "created_at": n.created_at.isoformat()} for n in notes]}

def create_incident(engine, alert_id, actor="api-client"):
    with Session(engine) as session, session.begin():
        alert = session.get(AlertRow, alert_id)
        if alert is None:
            return None
        existing = session.scalar(select(IncidentRow).where(IncidentRow.alert_id == alert_id))
        if existing:
            return incident_detail(session, existing)
        now = datetime.now(timezone.utc)
        row = IncidentRow(alert_id=alert_id, status="open", created_at=now, updated_at=now)
        session.add(row)
        session.flush()
        session.add(IncidentAuditRow(incident_id=row.id, action="created", actor=actor,
            detail="Incident opened from alert", created_at=now))
        return incident_detail(session, row)

def get_incident(engine, incident_id):
    with Session(engine) as session:
        row = session.get(IncidentRow, incident_id)
        return incident_detail(session, row) if row else None

def list_incidents(engine, limit=50):
    with Session(engine) as session:
        rows = session.scalars(select(IncidentRow).order_by(IncidentRow.updated_at.desc()).limit(limit)).all()
        return [incident_detail(session, row) for row in rows]

def update_incident(engine, incident_id, status=None, owner=None, change_owner=False, actor="api-client"):
    with Session(engine) as session, session.begin():
        row = session.get(IncidentRow, incident_id)
        if row is None:
            return None
        if status is not None:
            row.status = status
        if change_owner:
            row.owner = owner
        row.updated_at = datetime.now(timezone.utc)
        session.add(IncidentAuditRow(incident_id=row.id, action="updated", actor=actor,
            detail=f"status={row.status}; owner={row.owner or 'unassigned'}", created_at=row.updated_at))
        session.flush()
        return incident_detail(session, row)

def add_incident_note(engine, incident_id, author, body):
    with Session(engine) as session, session.begin():
        row = session.get(IncidentRow, incident_id)
        if row is None:
            return None
        now = datetime.now(timezone.utc)
        note = IncidentNoteRow(incident_id=incident_id, author=author, body=body, created_at=now)
        session.add(note)
        row.updated_at = now
        session.add(IncidentAuditRow(incident_id=row.id, action="note_added", actor=author,
            detail=f"note_id={note.id}", created_at=now))
        session.flush()
        return incident_detail(session, row)

def list_incident_audit(engine, incident_id):
    with Session(engine) as session:
        if session.get(IncidentRow, incident_id) is None:
            return None
        rows = session.scalars(select(IncidentAuditRow).where(
            IncidentAuditRow.incident_id == incident_id).order_by(IncidentAuditRow.id)).all()
        return [{"id": a.id, "action": a.action, "actor": a.actor,
                 "detail": a.detail, "created_at": a.created_at.isoformat()} for a in rows]
