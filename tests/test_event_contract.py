"""Language-neutral event contract checks.

Known Python/Rust differences are strict expected failures until the Python
validation hardening is merged and both implementations agree.
"""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from tracepoint.main import SecurityEvent


CASES = json.loads(
    (Path(__file__).resolve().parents[1] / "contracts" / "security_event_cases.json").read_text()
)
KNOWN_GAPS = {
    "bad_ip": "Python currently accepts malformed source_ip values",
    "invalid_timestamp": "Python's Pydantic model accepts naive timestamps; HTTP layer rejects them",
}


@pytest.mark.parametrize(
    "case",
    [
        pytest.param(
            case,
            id=case["name"],
            marks=(
                pytest.mark.xfail(strict=True, reason=KNOWN_GAPS[case["name"]])
                if case["name"] in KNOWN_GAPS
                else ()
            ),
        )
        for case in CASES
    ],
)
def test_python_event_contract(case):
    try:
        SecurityEvent.model_validate(case["input"])
        accepted = True
    except ValidationError:
        accepted = False
    assert accepted is case["valid"]
