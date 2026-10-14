"""Generate synthetic failed-login events against a local Tracepoint API.

Never point this script at a production service.
"""
import argparse
from datetime import datetime, timedelta, timezone
import os
import sys
from uuid import uuid4

import httpx

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()
    if args.count < 1 or args.count > 100:
        parser.error("--count must be 1..100")
    if args.url.rstrip("/") not in {"http://127.0.0.1:8000", "http://localhost:8000"}:
        parser.error("Only local Tracepoint API URLs are allowed")
    key = os.getenv("TRACEPOINT_API_KEY")
    if not key:
        sys.exit("Set TRACEPOINT_API_KEY first")
    now = datetime.now(timezone.utc) - timedelta(seconds=args.count)
    with httpx.Client(timeout=10) as client:
        for i in range(args.count):
            payload = {"event_id": str(uuid4()), "source": "synthetic-demo",
                "event_type": "auth.login_failed",
                "timestamp": (now + timedelta(seconds=i)).isoformat(),
                "source_ip": "192.0.2.10", "actor_id": "demo-user"}
            response = client.post(args.url.rstrip("/") + "/api/v1/events",
                json=payload, headers={"X-API-Key": key})
            response.raise_for_status()
            print(i + 1, response.json()["status"], response.json()["alerts_created"])
    print("Synthetic events sent. Refresh the local dashboard.")

if __name__ == "__main__":
    main()
