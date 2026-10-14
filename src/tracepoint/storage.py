from datetime import datetime, timedelta, timezone
import os
from sqlalchemy import create_engine, String, DateTime, Integer, ForeignKey, select, func
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
