#!/usr/bin/env python3
"""T6 — Cooling-lock same-thread resurrection trap.

Verifies that a subject artifact arriving in the same thread while the cooling lock
is still active does NOT resurrect the session or clear cooling_until. This is a
regression trap for the RED finding in engram_state.py:263-278.
"""
from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "test-evidence"
EVIDENCE_FILE = EVIDENCE_DIR / "trap-t6-cooling-resurrect.json"

BASE_TIME = datetime(2026, 8, 28, 12, 0, 0, tzinfo=timezone.utc)


def make_state(ts: datetime) -> dict:
    return {
        "last_contact_ts": (ts - timedelta(hours=25)).isoformat(),
        "last_mode": "C",
        "mode_history": ["B", "C"],
        "mode_last_sent": {
            "A": None, "B": (ts - timedelta(days=2)).isoformat(),
            "C": ts.isoformat(), "D": None, "E": None, "F": None,
            "G": None, "H": None, "I": None, "J": None,
        },
        "mode_j_eligible": None,
        "pending_revisits": [],
        "last_probe_ts": (ts - timedelta(days=2)).isoformat(),
        "ignored_count": 0,
        "passive_mode": False,
        "redaction_cooldown_until": (ts - timedelta(hours=1)).isoformat(),
        "last_user_contact_ts": ts.isoformat(),
        "session_active": False,
        "session_opened_at": (ts - timedelta(minutes=20)).isoformat(),
        "session_opened_by": "agent",
        "session_exchange_count": 6,
        "session_agent_turn_count": 3,
        "session_last_agent_mode": "C",
        "session_thread_id": ["mattermost", "11q5an3haffxfpo6kfradxp75y", "thread-abc"],
        "session_wind_down_phase": "cooling",
        "session_close_sent_at": ts.isoformat(),
        "session_close_mode": "C",
        "wind_down_nudge_threshold": 4,
        "wind_down_close_threshold": 6,
        "cooling_window_minutes": 30,
        "session_recency_threshold_seconds": 900,
        "contact_window_hours": 24,
    }


def make_artifact(ts: datetime) -> dict:
    return {
        "platform": "mattermost",
        "channel_id": "11q5an3haffxfpo6kfradxp75y",
        "thread_id": "thread-abc",
        "sender": "subject",
        "content": "Actually, one thing did come to mind.",
        "timestamp": ts.isoformat(),
    }


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence: dict = {"timestamp": BASE_TIME.isoformat(), "steps": [], "passed": False, "errors": []}
    errors: list[str] = []

    # Snapshot live state so we can restore it.
    state_path = ROOT / "engagement_state.json"
    archive_path = ROOT / "archive" / "index.jsonl"
    old_state = state_path.read_text() if state_path.exists() else "{}"
    old_archive = archive_path.read_text() if archive_path.exists() else ""

    try:
        # Inject synthetic state and archive using real time so run_accounting does not
        # treat the cooling_until as expired.
        sys.path.insert(0, str(ROOT / "tools"))
        from engram_state import run_accounting

        # Patch engram_state to use a fixed clock so evidence is deterministic.
        import engram_state
        engram_state.now_utc = lambda: BASE_TIME

        now_real = BASE_TIME
        subject_ts = now_real + timedelta(minutes=5)
        state = make_state(now_real)
        state["cooling_until"] = (now_real + timedelta(minutes=30)).isoformat()
        state_path.write_text(json.dumps(state, indent=2, sort_keys=True))
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_text(json.dumps(make_artifact(subject_ts)) + "\n")

        summary = run_accounting()
        state_after = json.loads(state_path.read_text())

        evidence["steps"].append({
            "step": 1,
            "description": "subject artifact in same thread while cooling lock active",
            "summary_actions": summary.get("actions", []),
            "session_active_before": False,
            "session_active_after": state_after.get("session_active"),
            "cooling_until_after": state_after.get("cooling_until"),
            "session_wind_down_phase_after": state_after.get("session_wind_down_phase"),
        })

        if state_after.get("session_active") is not False:
            errors.append("step-1: session was resurrected during active cooling lock")
        if state_after.get("session_wind_down_phase") != "cooling":
            errors.append("step-1: wind-down phase changed away from cooling")
        if state_after.get("cooling_until") != state["cooling_until"]:
            errors.append("step-1: cooling_until was cleared or changed")
        if "skipped_cooling_lock_same_thread" not in summary.get("actions", []):
            errors.append("step-1: accounting did not log skipped_cooling_lock_same_thread")
    finally:
        state_path.write_text(old_state)
        archive_path.write_text(old_archive)

    evidence["passed"] = len(errors) == 0
    evidence["errors"] = errors
    EVIDENCE_FILE.write_text(json.dumps(evidence, indent=2) + "\n")

    print("TRAP T6 COOLING-LOCK RESURRECTION VALIDATION")
    if not errors:
        print("PASSED")
        print(f"Evidence: {EVIDENCE_FILE.relative_to(ROOT)}")
        return 0
    print("FAILED")
    for err in errors:
        print(f"  - {err}")
    print(f"Evidence: {EVIDENCE_FILE.relative_to(ROOT)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
