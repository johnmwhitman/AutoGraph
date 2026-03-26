# analytics.py -- Thumbprint lightweight JSONL event logger
# Append-only event log. Zero dependencies beyond stdlib.
# Storage: C:\AI\logs\thumbprint_analytics.jsonl
#
# Usage:
#   from analytics import log_event
#   log_event("portrait_delivered", client_slug="alex_rivera", tier="standard", round=1)
#   log_event("chat_session_started", client_slug="alex_rivera", session_id="abc123")
#   log_event("page_view", path="/", ip_hash="a1b2c3d4", user_agent_short="Chrome/124")

import hashlib
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

ANALYTICS_FILE = Path(r"C:\AI\logs\thumbprint_analytics.jsonl")
_write_lock = threading.Lock()

# Valid event types and their required fields
EVENT_SCHEMA = {
    "portrait_delivered":   {"required": ["client_slug"], "optional": ["tier", "round"]},
    "round2_purchased":     {"required": ["client_slug"], "optional": ["revenue"]},
    "round2_delivered":     {"required": ["client_slug"], "optional": []},
    "chat_session_started": {"required": ["client_slug", "session_id"], "optional": []},
    "chat_session_returned":{"required": ["client_slug", "session_id"], "optional": ["turns"]},
    "page_view":            {"required": ["path"], "optional": ["ip_hash", "user_agent_short"]},
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def hash_ip(ip: str) -> str:
    """Return first 8 chars of SHA-256 of the IP for privacy-safe logging."""
    return hashlib.sha256(ip.encode()).hexdigest()[:8]


def log_event(event_type: str, **kwargs) -> bool:
    """
    Append an event to thumbprint_analytics.jsonl.
    Returns True on success, False on error (never raises).

    Examples:
        log_event("portrait_delivered", client_slug="alex_rivera", tier="standard", round=1)
        log_event("round2_purchased", client_slug="alex_rivera", revenue=148)
        log_event("chat_session_started", client_slug="alex_rivera", session_id="abc123")
        log_event("page_view", path="/", ip_hash="a1b2c3d4", user_agent_short="Chrome/124")
    """
    try:
        record = {
            "event":     event_type,
            "timestamp": _utc_now(),
        }
        record.update(kwargs)

        # Validate event type (warn but don't block unknown events)
        if event_type not in EVENT_SCHEMA:
            record["_unknown_event"] = True

        ANALYTICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False) + "\n"

        with _write_lock:
            with open(ANALYTICS_FILE, "a", encoding="utf-8") as f:
                f.write(line)
        return True

    except Exception as e:
        # Never let analytics break the main flow
        print(f"[ANALYTICS ERROR] {e}")
        return False


def read_events(event_type: str = None) -> list:
    """Read all events from the JSONL file. Optionally filter by event_type."""
    if not ANALYTICS_FILE.exists():
        return []
    events = []
    with open(ANALYTICS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                if event_type is None or ev.get("event") == event_type:
                    events.append(ev)
            except json.JSONDecodeError:
                continue
    return events


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Thumbprint Analytics -- smoke test")
    print(f"Log file: {ANALYTICS_FILE}")
    log_event("portrait_delivered", client_slug="test_client", tier="standard", round=1)
    log_event("round2_purchased",   client_slug="test_client", revenue=148)
    log_event("chat_session_started", client_slug="test_client", session_id="test_sess_001")
    log_event("page_view", path="/", ip_hash="deadbeef", user_agent_short="Chrome/124")
    events = read_events()
    print(f"Total events in log: {len(events)}")
    for ev in events[-4:]:
        print(f"  {ev['timestamp']} | {ev['event']}")
    print("OK")
