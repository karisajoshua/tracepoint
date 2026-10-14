"""Regression tests for the event schema and its API boundary."""
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from tracepoint.schemas import SecurityEvent


def sample(**overrides):
    data = {
        "event_id": str(uuid4()),
        "source": "example-service",
        "event_type": "auth.login_failed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_ip": "192.0.2.10",
    }
    data.update(overrides)
    return data


@pytest.mark.parametrize("invalid", [
    "127.0.0.1:443", "not-an-ip", "999.1.1.1", "10.0.0.1; DROP TABLE",
    "", "fe80::zzzz",
])
def test_rejects_malformed_source_ips(invalid):
    with pytest.raises(ValidationError):
        SecurityEvent.model_validate(sample(source_ip=invalid))


def test_normalizes_ipv6():
    event = SecurityEvent.model_validate(sample(source_ip="2001:0DB8:0000:0000:0000:0000:0000:0001"))
    assert event.source_ip == "2001:db8::1"


def test_optional_ip_is_supported():
    assert SecurityEvent.model_validate(sample(source_ip=None)).source_ip is None


@pytest.mark.parametrize("field", ["source", "event_type"])
def test_rejects_control_characters(field):
    with pytest.raises(ValidationError):
        SecurityEvent.model_validate(sample(**{field: "unsafe\nvalue"}))


def test_forbids_unrecognized_fields():
    with pytest.raises(ValidationError):
        SecurityEvent.model_validate(sample(admin=True))


def test_rejects_whitespace_only_source():
    with pytest.raises(ValidationError):
        SecurityEvent.model_validate(sample(source="   "))
