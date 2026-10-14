"""Validation helpers for untrusted security telemetry.

Keep event contracts independent from persistence and HTTP routing so contributors
can test them in isolation. These rules reject malformed network identities before
events enter the detection pipeline.
"""
from ipaddress import ip_address
from pydantic import BaseModel, ConfigDict, Field, field_validator
from uuid import UUID
from datetime import datetime


class SecurityEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    event_id: UUID
    source: str = Field(min_length=1, max_length=80)
    event_type: str = Field(min_length=1, max_length=100)
    timestamp: datetime
    actor_id: str | None = Field(default=None, max_length=128)
    source_ip: str | None = Field(default=None, max_length=45)

    @field_validator("source_ip")
    @classmethod
    def valid_ip(cls, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            return str(ip_address(value))
        except ValueError as exc:
            raise ValueError("source_ip must be a valid IPv4 or IPv6 address") from exc

    @field_validator("source", "event_type")
    @classmethod
    def reject_control_characters(cls, value: str) -> str:
        if any(ord(char) < 32 or ord(char) == 127 for char in value):
            raise ValueError("Control characters are not allowed")
        return value
