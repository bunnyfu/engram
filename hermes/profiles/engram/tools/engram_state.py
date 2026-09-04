#!/usr/bin/env python3
"""Shared deterministic state/accounting helpers for Engram cron tooling.

No LLM calls. Reads/writes engagement_state.json, queries the raw archive,
applies the session-boundary spec (see the "Session exchange budget and wind-down"
section of the engram-engagement-engine skill), and returns structured JSON
summaries for director scripts to consume.

Repo layout: this file lives at hermes/profiles/engram/tools/, so the profile
root (skills/, cron/, gaps.md, runtime state) is one directory up. At deployment
the profile installs to ~/.hermes/profiles/engram while runtime state may live
elsewhere — rebind ENGRAM_STATE_ROOT below at install time if the two split.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(os.environ.get("ENGRAM_STATE_ROOT", str(ROOT)))
PROFILE_ROOT = ROOT
STATE_PATH = REPO_ROOT / "engagement_state.json"
ARCHIVE_DIR = REPO_ROOT / "archive"
ARCHIVE_INDEX = ARCHIVE_DIR / "index.jsonl"

DEFAULT_THRESHOLDS = {
    "session_recency_threshold_seconds": 900,
    "contact_window_hours": 24,
    "cooling_window_minutes": 30,
    "wind_down_nudge_threshold": 4,
    "wind_down_close_threshold": 6,
    "max_ignored_count": 3,
}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s: str | None) -> datetime | None:
    if s is None:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


def load_state() -> dict[str, Any]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {}


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True))


def ensure_state() -> dict[str, Any]:
    """Initialize engagement_state.json if missing and return it."""
    state = load_state()
    if state:
        return state
    state = initial_state()
    save_state(state)
    return state


def initial_state() -> dict[str, Any]:
    return {
        "last_contact_ts": None,
        "last_mode": None,
        "mode_history": [],
        "mode_last_sent": {m: None for m in "ABCDEFGHIJ"},
        "mode_j_eligible": None,
        "pending_revisits": [],
        "last_probe_ts": None,
        "ignored_count": 0,
        "passive_mode": False,
        "redaction_cooldown_until": None,
        "last_user_contact_ts": None,
        "session_active": False,
        "session_thread_id": None,
        "session_opened_at": None,
        "session_opened_by": None,
        "session_exchange_count": 0,
        "session_agent_turn_count": 0,
        "session_last_agent_mode": None,
        "session_wind_down_phase": None,
        "session_close_sent_at": None,
        "session_close_mode": None,
        "wind_down_nudge_threshold": DEFAULT_THRESHOLDS["wind_down_nudge_threshold"],
        "wind_down_close_threshold": DEFAULT_THRESHOLDS["wind_down_close_threshold"],
        "cooling_window_minutes": DEFAULT_THRESHOLDS["cooling_window_minutes"],
        "cooling_until": None,
        "session_recency_threshold_seconds": DEFAULT_THRESHOLDS[
            "session_recency_threshold_seconds"
        ],
        "contact_window_hours": DEFAULT_THRESHOLDS["contact_window_hours"],
    }


def load_archive_index() -> list[dict[str, Any]]:
    if not ARCHIVE_INDEX.exists():
        return []
    lines = ARCHIVE_INDEX.read_text().strip().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def append_artifact(artifact: dict[str, Any]) -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(ARCHIVE_INDEX, "a") as f:
        f.write(json.dumps(artifact, default=str) + "\n")


def resolve_mikoshi_channel_id() -> str:
    """Read MIKOSHI channel ID from engram channel_directory.json."""
    channel_dir = PROFILE_ROOT / "channel_directory.json"
    if channel_dir.exists():
        data = json.loads(channel_dir.read_text())
        for item in data.values():
            if isinstance(item, dict) and item.get("name") == "caleb":
                return item["id"]
            if isinstance(item, str):
                # simpler flat format
                continue
    return "11q5an3haffxfpo6kfradxp75y"


def thread_id_tuple(artifact: dict[str, Any]) -> tuple[str, str, str | None]:
    return (
        artifact.get("platform", "mattermost"),
        artifact.get("channel_id", resolve_mikoshi_channel_id()),
        artifact.get("thread_id"),
    )


def _artifact_ts(a: dict[str, Any]) -> datetime:
    ts = parse_iso(a.get("timestamp"))
    if ts is None:
        return datetime.min.replace(tzinfo=timezone.utc)
    return ts


def query_latest_artifact() -> dict[str, Any] | None:
    """Return the newest artifact in the archive by timestamp, or None."""
    idx = load_archive_index()
    if not idx:
        return None
    # sort by timestamp descending
    return max(idx, key=_artifact_ts)


def query_subject_artifacts_after(ts: datetime | None) -> list[dict[str, Any]]:
    """Return subject artifacts newer than ts."""
    idx = load_archive_index()
    if ts is None:
        return [a for a in idx if a.get("sender") == "subject"]
    return [
        a
        for a in idx
        if a.get("sender") == "subject"
        and (parse_iso(a.get("timestamp")) or datetime.min.replace(tzinfo=timezone.utc)) > ts
    ]


def query_agent_artifacts() -> list[dict[str, Any]]:
    return [a for a in load_archive_index() if a.get("sender") == "agent"]


def compute_wind_down_phase(exchange_count: int, state: dict[str, Any]) -> str:
    nudge = state.get("wind_down_nudge_threshold", DEFAULT_THRESHOLDS["wind_down_nudge_threshold"])
    close = state.get("wind_down_close_threshold", DEFAULT_THRESHOLDS["wind_down_close_threshold"])
    if exchange_count >= close:
        return "closing"
    if exchange_count >= nudge:
        return "nudging"
    return "open"


def run_accounting() -> dict[str, Any]:
    """Deterministic pre-wake accounting. Returns a structured summary."""
    state = ensure_state()
    now = now_utc()
    changed = False
    summary = {"now": iso(now), "actions": []}

    # 1. Clear expired cooling lock.
    cooling_until = parse_iso(state.get("cooling_until"))
    if cooling_until is not None and now > cooling_until:
        state["cooling_until"] = None
        if not state.get("session_active", False):
            state["session_wind_down_phase"] = None
        changed = True
        summary["actions"].append("cleared_expired_cooling")

    # 2. Query latest artifact.
    latest = query_latest_artifact()
    session_recency = state.get(
        "session_recency_threshold_seconds",
        DEFAULT_THRESHOLDS["session_recency_threshold_seconds"],
    )

    if latest is None:
        # No artifacts at all.
        if state.get("session_active", False):
            state["session_active"] = False
            changed = True
            summary["actions"].append("closed_session_no_artifacts")
        if changed:
            save_state(state)
        summary["session_active"] = state.get("session_active", False)
        summary["state"] = state
        return summary

    last_ts = parse_iso(latest.get("timestamp"))
    if last_ts is None:
        last_ts = now
    last_thread = thread_id_tuple(latest)
    current_thread = state.get("session_thread_id")

    # 3. Detect subject-initiated contact disarm.
    subject_after = query_subject_artifacts_after(parse_iso(state.get("last_user_contact_ts")))
    if subject_after:
        state["last_user_contact_ts"] = iso(max(parse_iso(a["timestamp"]) for a in subject_after if parse_iso(a["timestamp"])))
        state["ignored_count"] = 0
        state["passive_mode"] = False
        changed = True
        summary["actions"].append("subject_contact_disarm")

    # 4. Session boundary logic per spec.
    current_thread_tuple = tuple(current_thread) if current_thread is not None else None
    if current_thread_tuple is None or last_thread != current_thread_tuple:
        # New thread.
        if (
            state.get("cooling_until")
            and cooling_until is not None
            and now <= cooling_until
            and last_thread == current_thread_tuple
        ):
            # Same thread as just-closed session, still cooling.
            summary["actions"].append("skipped_cooling_lock_same_thread")
        else:
            # Start new session.
            state["session_active"] = True
            state["session_thread_id"] = list(last_thread)
            state["session_opened_at"] = iso(last_ts)
            state["session_opened_by"] = latest.get("sender", "unknown")
            state["session_exchange_count"] = 1
            state["session_agent_turn_count"] = 0
            state["session_last_agent_mode"] = None
            state["session_wind_down_phase"] = "open"
            state["session_close_sent_at"] = None
            state["session_close_mode"] = None
            state["cooling_until"] = None
            changed = True
            summary["actions"].append("started_new_session")
    else:
        # Same thread. Check recency.
        if (now - last_ts).total_seconds() <= session_recency:
            # Cooling-lock guard: never resurrect a session that is actively cooling.
            if state.get("session_wind_down_phase") == "cooling" and cooling_until is not None and now <= cooling_until:
                summary["actions"].append("skipped_cooling_lock_same_thread")
            elif not state.get("session_active", False):
                state["session_active"] = True
                state["session_opened_at"] = iso(last_ts)
                state["session_opened_by"] = latest.get("sender", "unknown")
                state["session_exchange_count"] = 1
                state["session_agent_turn_count"] = 0
                state["session_last_agent_mode"] = None
                state["session_wind_down_phase"] = "open"
                state["session_close_sent_at"] = None
                state["session_close_mode"] = None
                state["cooling_until"] = None
                changed = True
                summary["actions"].append("resurrected_session")
            else:
                # Active session; if latest is subject after agent turn, increment exchange count.
                agent_artifacts = [a for a in load_archive_index() if a.get("sender") == "agent"]
                latest_agent_ts = max(
                    [t for t in (parse_iso(a.get("timestamp")) for a in agent_artifacts) if t],
                    default=None,
                )
                if latest.get("sender") == "subject" and (latest_agent_ts is None or last_ts > latest_agent_ts):
                    state["session_exchange_count"] = state.get("session_exchange_count", 0) + 1
                    changed = True
                    summary["actions"].append("incremented_exchange_count")
        else:
            # Session expired.
            if state.get("session_active", False):
                state["session_active"] = False
                changed = True
                summary["actions"].append("session_expired")

    # 5. Recompute wind-down phase if active and not cooling.
    if state.get("session_active", False) and state.get("session_wind_down_phase") != "cooling":
        new_phase = compute_wind_down_phase(state.get("session_exchange_count", 0), state)
        if state.get("session_wind_down_phase") != new_phase:
            state["session_wind_down_phase"] = new_phase
            changed = True
            summary["actions"].append(f"wind_down_phase:{new_phase}")

    if changed:
        save_state(state)

    summary["session_active"] = state.get("session_active", False)
    summary["session_wind_down_phase"] = state.get("session_wind_down_phase")
    summary["cooling_until"] = state.get("cooling_until")
    summary["session_exchange_count"] = state.get("session_exchange_count", 0)
    summary["state"] = state
    return summary


def cap_checks(state: dict[str, Any], now: datetime | None = None) -> tuple[bool, str]:
    """Run selector cap checks in order. Returns (passed, reason)."""
    if now is None:
        now = now_utc()

    if state.get("passive_mode", False):
        return False, "passive_mode"

    redaction = parse_iso(state.get("redaction_cooldown_until"))
    if redaction is not None and now <= redaction:
        return False, "redaction_cooldown"

    last_contact = parse_iso(state.get("last_contact_ts"))
    window = timedelta(hours=state.get("contact_window_hours", DEFAULT_THRESHOLDS["contact_window_hours"]))
    if last_contact is not None and (now - last_contact) < window:
        return False, "contact_window"

    if state.get("session_active", False):
        return False, "active_session"

    cooling = parse_iso(state.get("cooling_until"))
    if cooling is not None and now <= cooling:
        return False, "cooling_lock"

    return True, ""


def load_gaps() -> list[dict[str, Any]]:
    gaps_path = REPO_ROOT / "gaps.md"
    if not gaps_path.exists():
        return []
    text = gaps_path.read_text()
    # Parse simple YAML-like frontmatter blocks separated by ---
    entries = []
    for raw in re.split(r"\n---\s*\n", text):
        raw = raw.strip()
        if not raw:
            continue
        try:
            entry = {}
            for line in raw.splitlines():
                if ":" in line and not line.startswith("#"):
                    key, val = line.split(":", 1)
                    entry[key.strip()] = val.strip().strip('"')
            if "id" in entry:
                entries.append(entry)
        except Exception:
            continue
    return entries


def select_mode(state: dict[str, Any]) -> dict[str, Any]:
    """Deterministic mode selection. Returns decision dict."""
    now = now_utc()
    passed, reason = cap_checks(state, now)
    if not passed:
        return {"mode": "I", "reason": f"cap:{reason}", "stop": True}

    # Event-driven modes: for now, no event seeds in archive -> skip.
    # Relationship modes: require USER.md anchors and cadence; for Phase 1 kickoff,
    # only Mode A is reachable from a high-priority gap.
    gaps = load_gaps()
    high_priority = [g for g in gaps if g.get("priority", "").lower() == "high" and g.get("status", "open").lower() == "open"]
    if high_priority:
        return {"mode": "A", "reason": "high_priority_gap", "stop": False, "selected_gap": high_priority[0]}

    return {"mode": "I", "reason": "no_strong_anchor", "stop": True}


def record_send(mode: str, phase: str | None = None, gap_id: str | None = None) -> dict[str, Any]:
    """Update state after a confirmed send. Pure deterministic write."""
    state = load_state()
    now = now_utc()
    state["last_contact_ts"] = iso(now)
    state["last_mode"] = mode
    if mode != "I":
        state["mode_history"] = (state.get("mode_history", []) + [mode])[-7:]
    state["mode_last_sent"][mode] = iso(now)
    if mode == "A":
        state["last_probe_ts"] = iso(now)

    # Session accounting for agent-initiated opener.
    if mode != "I":
        if not state.get("session_active", False):
            state["session_active"] = True
            state["session_thread_id"] = ["mattermost", resolve_mikoshi_channel_id(), None]
            state["session_opened_at"] = iso(now)
            state["session_opened_by"] = "agent"
            state["session_exchange_count"] = 1
            state["session_agent_turn_count"] = 1
            state["session_last_agent_mode"] = mode
            state["session_wind_down_phase"] = "open"
            state["session_close_sent_at"] = None
            state["session_close_mode"] = None
            state["cooling_until"] = None
        else:
            state["session_agent_turn_count"] = state.get("session_agent_turn_count", 0) + 1
            state["session_last_agent_mode"] = mode

    if phase == "closing":
        state["session_close_sent_at"] = iso(now)
        state["session_close_mode"] = mode
        state["session_wind_down_phase"] = "cooling"
        state["cooling_until"] = iso(now + timedelta(minutes=state.get("cooling_window_minutes", 30)))

    save_state(state)
    return state


def record_outcome(outcome: str, mode: str, phase: str | None = None, gap_id: str | None = None) -> dict[str, Any]:
    """Parse an actuator outcome string and update state accordingly."""
    if outcome.startswith("sent:"):
        parts = outcome.split(":")
        sent_mode = parts[1] if len(parts) > 1 else mode
        sent_phase = parts[2] if len(parts) > 2 else phase
        return record_send(sent_mode, sent_phase, gap_id)
    if outcome.startswith("declined:"):
        state = load_state()
        now = now_utc()
        state["last_contact_ts"] = iso(now)
        state["last_mode"] = mode
        if mode != "I":
            state["mode_history"] = (state.get("mode_history", []) + [mode])[-7:]
        state["mode_last_sent"][mode] = iso(now)
        save_state(state)
        return state
    if outcome == "redaction":
        state = load_state()
        state["redaction_cooldown_until"] = iso(now_utc() + timedelta(hours=1))
        save_state(state)
        return state
    return load_state()


def set_mode_j_eligible(slot_id: str | None) -> dict[str, Any]:
    """Persist Mode J eligibility (sole writer boundary: engram-engagement-engine)."""
    state = load_state()
    state["mode_j_eligible"] = slot_id
    save_state(state)
    return state


def get_actuator_outcome(job_id: str, timeout: float = 60.0, poll_interval: float = 1.0) -> tuple[str | None, str]:
    """Poll the engram state DB for the most recent completed cron run of job_id.

    Returns (outcome_line, status) where outcome_line is the parsed sent/declined/redaction
    token from the last assistant message, and status describes the poll result.
    """
    import sqlite3
    import time

    deadline = time.time() + timeout
    db_path = PROFILE_ROOT / "state.db"
    session_id: str | None = None
    while time.time() < deadline:
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        c.execute(
            "SELECT id, ended_at, end_reason FROM sessions WHERE source='cron' AND id LIKE ? ORDER BY started_at DESC LIMIT 1",
            (f"cron_{job_id}_%",),
        )
        row = c.fetchone()
        conn.close()
        if row and row[1] is not None:
            session_id = row[0]
            break
        time.sleep(poll_interval)

    if session_id is None:
        return None, "timeout"

    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute(
        "SELECT content FROM messages WHERE session_id=? AND role='assistant' ORDER BY id DESC LIMIT 1",
        (session_id,),
    )
    row = c.fetchone()
    conn.close()
    if not row:
        return None, "no_assistant_message"

    text = row[0] or ""
    # Look for the last line matching an outcome token.
    for line in reversed(text.strip().splitlines()):
        line = line.strip()
        if line.startswith("sent:") or line.startswith("declined:") or line == "redaction":
            return line, "ok"
    return None, "no_outcome_token"


if __name__ == "__main__":
    # CLI for quick accounting dry-run
    summary = run_accounting()
    print(json.dumps(summary, indent=2))
