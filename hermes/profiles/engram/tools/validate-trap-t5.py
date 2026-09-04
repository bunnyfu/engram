#!/usr/bin/env python3
"""T5 — Mode I cooling-lock trap for Engram wind-down.

Synthetic state-injection harness. Verifies that once the exchange budget hits the
close threshold, the closing beat fires, the engine sets the cooling lock,
and both the proactive-engagement cron and the session conversation routing suppress further
agent output until cooling_until expires. Includes a break-test that disables the
lock and confirms the trap would fail.

Post-consolidation (2026-09-04): the former state-accounting / mode-selector /
conversation-handler / mode-silence skills all live in
engram-engagement-engine/SKILL.md, so all skill clauses assert against it.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "test-evidence"
EVIDENCE_FILE = EVIDENCE_DIR / "trap-t5-cooling-lock.json"

# Required greppable contract clauses across the skill/cron files.
REQUIRED_CLAUSES = [
    (
        ROOT / "skills" / "engram" / "engram-engagement-engine" / "SKILL.md",
        r"session_wind_down_phase\s*=\s*cooling",
        "engine sets cooling phase",
    ),
    (
        ROOT / "skills" / "engram" / "engram-engagement-engine" / "SKILL.md",
        r"cooling_until\s*=\s*now\s*\+\s*cooling_window_minutes",
        "engine sets cooling_until",
    ),
    (
        ROOT / "skills" / "engram" / "engram-engagement-engine" / "SKILL.md",
        r"now\s*>\s*cooling_until",
        "engine enforces cooling_until cap (cap check 5)",
    ),
    (
        ROOT / "skills" / "engram" / "engram-engagement-engine" / "SKILL.md",
        r"skipped:cooling-lock",
        "engine (conversation routing) logs skipped:cooling-lock",
    ),
    (
        ROOT / "skills" / "engram" / "engram-engagement-repertoire" / "SKILL.md",
        r"skipped:cooling-lock",
        "repertoire (Mode I) recognizes skipped:cooling-lock",
    ),
    (
        ROOT / "cron" / "proactive-engagement.prompt.md",
        r"now\s*<=\s*cooling_until",
        "proactive-engagement cron lists cooling_until stop condition",
    ),
]


# Fixed timestamp for deterministic, reproducible evidence output.
BASE_TIME = datetime(2026, 8, 28, 12, 0, 0, tzinfo=timezone.utc)


def now() -> datetime:
    return BASE_TIME


def check_clauses() -> list[str]:
    """Verify the wind-down contract is present in the skills/cron files."""
    errors: list[str] = []
    for path, pattern, description in REQUIRED_CLAUSES:
        text = path.read_text()
        if not re.search(pattern, text):
            errors.append(f"missing clause: {description} in {path.relative_to(ROOT)}")
    return errors


def make_base_state(ts: datetime) -> dict:
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
        "session_active": True,
        "session_opened_at": (ts - timedelta(minutes=20)).isoformat(),
        "session_opened_by": "agent",
        "session_exchange_count": 6,
        "session_agent_turn_count": 3,
        "session_last_agent_mode": "C",
        "session_wind_down_phase": "closing",
        "session_close_sent_at": None,
        "session_close_mode": None,
        "wind_down_nudge_threshold": 4,
        "wind_down_close_threshold": 6,
        "cooling_window_minutes": 30,
        "cooling_until": None,
    }


def apply_closing_send(state: dict, ts: datetime) -> None:
    """Simulate engine write on sent:<mode>:closing."""
    mode = state["session_last_agent_mode"]
    state["session_close_sent_at"] = ts.isoformat()
    state["session_close_mode"] = mode
    state["session_wind_down_phase"] = "cooling"
    state["cooling_until"] = (ts + timedelta(minutes=state["cooling_window_minutes"])).isoformat()
    state["mode_last_sent"][mode] = ts.isoformat()
    state["session_agent_turn_count"] += 1


def selector_cap5_passes(state: dict, ts: datetime) -> bool:
    """Cap check 5: now > cooling_until (no active cooling lock)."""
    cooling_until = datetime.fromisoformat(state["cooling_until"]) if state["cooling_until"] else None
    return cooling_until is None or ts > cooling_until


def handler_suppressed(state: dict, ts: datetime) -> bool:
    """Conversation handler stop condition: cooling phase and lock still active."""
    cooling_until = datetime.fromisoformat(state["cooling_until"]) if state["cooling_until"] else None
    return state["session_wind_down_phase"] == "cooling" and cooling_until is not None and ts <= cooling_until


def run_trap() -> tuple[bool, dict, list[str]]:
    """Run T5 trap and return (passed, evidence dict, errors)."""
    errors = check_clauses()
    evidence: dict = {"timestamp": now().isoformat(), "steps": [], "passed": False}

    t0 = now()
    state = make_base_state(t0)

    # Step 1: closing beat fires and cooling lock is set.
    apply_closing_send(state, t0)
    evidence["steps"].append({
        "step": 1,
        "description": "closing beat fires; engine writes cooling lock",
        "state_after": {k: state[k] for k in [
            "session_wind_down_phase", "cooling_until", "session_close_mode",
            "session_close_sent_at",
        ]},
        "assertions": {
            "phase_is_cooling": state["session_wind_down_phase"] == "cooling",
            "cooling_until_set": state["cooling_until"] is not None,
            "close_mode_matches": state["session_close_mode"] == "C",
            "mode_last_sent_updated": state["mode_last_sent"]["C"] == t0.isoformat(),
        },
    })
    for name, ok in evidence["steps"][-1]["assertions"].items():
        if not ok:
            errors.append(f"step-1 assertion failed: {name}")

    # Step 2: before expiry, selector cap check 5 must fail.
    t1 = t0 + timedelta(minutes=15)
    cap_passes = selector_cap5_passes(state, t1)
    evidence["steps"].append({
        "step": 2,
        "description": "selector cap check 5 before cooling_until expiry",
        "ts": t1.isoformat(),
        "cap5_passes": cap_passes,
        "expected": False,
    })
    if cap_passes:
        errors.append("step-2: selector cap5 passed while cooling lock active")

    # Step 3: before expiry, conversation handler must be suppressed.
    suppressed = handler_suppressed(state, t1)
    evidence["steps"].append({
        "step": 3,
        "description": "conversation handler before cooling_until expiry",
        "ts": t1.isoformat(),
        "handler_suppressed": suppressed,
        "expected": True,
    })
    if not suppressed:
        errors.append("step-3: conversation handler not suppressed while cooling lock active")

    # Step 4: after expiry, selector cap check 5 must pass.
    t2 = t0 + timedelta(minutes=31)
    cap_passes_after = selector_cap5_passes(state, t2)
    evidence["steps"].append({
        "step": 4,
        "description": "selector cap check 5 after cooling_until expiry",
        "ts": t2.isoformat(),
        "cap5_passes": cap_passes_after,
        "expected": True,
    })
    if not cap_passes_after:
        errors.append("step-4: selector cap5 did not pass after cooling lock expired")

    # Step 5: break-test — disable the lock and confirm trap would fail.
    broken_state = make_base_state(t0)
    apply_closing_send(broken_state, t0)
    broken_state["cooling_until"] = None  # simulate broken lock
    broken_state["session_wind_down_phase"] = "open"
    broken_suppressed = handler_suppressed(broken_state, t1)
    broken_cap_fails = not selector_cap5_passes(broken_state, t1)
    evidence["steps"].append({
        "step": 5,
        "description": "break-test: lock disabled/reset early",
        "handler_suppressed": broken_suppressed,
        "selector_cap5_failed": broken_cap_fails,
        "expected_both_false": True,
    })
    if broken_suppressed or broken_cap_fails:
        errors.append("step-5: break-test did not demonstrate lock failure")

    evidence["passed"] = len(errors) == 0
    evidence["errors"] = errors
    return len(errors) == 0, evidence, errors


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    passed, evidence, errors = run_trap()
    EVIDENCE_FILE.write_text(json.dumps(evidence, indent=2) + "\n")

    print("TRAP T5 COOLING-LOCK VALIDATION")
    if passed:
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
