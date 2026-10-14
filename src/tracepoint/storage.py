from sqlalchemy import create_engine, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class EventRow(Base):
    __tablename__ = 'security_events'
    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source: Mapped[str] = mapped_column(String(80), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
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
