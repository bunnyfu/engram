#!/usr/bin/env python3
"""Director: engram conversation-handler cron — ABSORBED 2026-09-04.

The cron fold (6 prompts -> 2) dissolved the conversation-handler cron:
mid-session reply routing is in-session behavior owned by the SOUL plus the
engram-engagement-engine / engram-engagement-repertoire skills (engine skill,
"Session conversation routing" section) — no cron fires for it. This file is
retained as the reference for the deterministic reply-routing checks (cooling
lock, unanswered subject artifact, already-replied). The throwaway-round
(2026-08-28) actuator job ID/name below is historical; rebind or delete at
install.

Pure deterministic pre-run. Checks whether an active, non-cooling session has
an unanswered subject artifact. If yes, triggers the conversation-handler
actuator. Idle ticks consume zero LLM tokens.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engram_state import (
    REPO_ROOT,
    get_actuator_outcome,
    load_archive_index,
    load_state,
    now_utc,
    parse_iso,
    record_outcome,
    run_accounting,
)

LOG_PATH = REPO_ROOT / "cron_output" / "conversation.log"
# Throwaway-round (2026-08-28) hermes cron job ID/name for the conversation
# handler actuator — rebind at install.
ACTUATOR_ID = "bd863ac74aa2"
ACTUATOR_NAME = "conversation-handler-actuator"


def log_line(line: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{now_utc().isoformat()} {line}\n")


def trigger_actuator(name: str) -> None:
    subprocess.run(
        ["hermes", "--profile", "engram", "cron", "run", name],
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    summary = run_accounting()
    state = load_state()
    now = now_utc()

    # Stop condition: cooling lock active.
    cooling_until = parse_iso(state.get("cooling_until"))
    if state.get("session_wind_down_phase") == "cooling" and cooling_until is not None and now <= cooling_until:
        log_line("skipped:cooling-lock")
        print(json.dumps({"result": "silence", "reason": "cooling-lock"}))
        return 0

    if not state.get("session_active", False):
        log_line("skipped:no_active_session")
        print(json.dumps({"result": "silence", "reason": "no_active_session"}))
        return 0

    # Find newest subject artifact in current session thread.
    session_thread_id = state.get("session_thread_id")
    if not session_thread_id:
        log_line("skipped:no_session_thread")
        print(json.dumps({"result": "silence", "reason": "no_session_thread"}))
        return 0

    channel_id = session_thread_id[1]
    thread_id = session_thread_id[2]

    subject_artifacts = [
        a
        for a in load_archive_index()
        if a.get("sender") == "subject"
        and a.get("channel_id") == channel_id
        and a.get("thread_id") == thread_id
    ]
    if not subject_artifacts:
        log_line("skipped:no_subject_artifact")
        print(json.dumps({"result": "silence", "reason": "no_subject_artifact"}))
        return 0

    latest_subject = max(subject_artifacts, key=lambda a: parse_iso(a.get("timestamp")) or now)
    latest_subject_ts = parse_iso(latest_subject.get("timestamp")) or now

    # Check if already replied.
    agent_artifacts = [
        a
        for a in load_archive_index()
        if a.get("sender") == "agent"
        and a.get("channel_id") == channel_id
        and a.get("thread_id") == thread_id
    ]
    latest_agent_ts = max(
        [t for t in (parse_iso(a.get("timestamp")) for a in agent_artifacts) if t],
        default=None,
    )
    if latest_agent_ts is not None and latest_agent_ts >= latest_subject_ts:
        log_line("skipped:already_replied")
        print(json.dumps({"result": "silence", "reason": "already_replied"}))
        return 0

    # Determine wind-down phase for the actuator.
    phase = state.get("session_wind_down_phase", "open")
    log_line(f"trigger:reply phase={phase}")
    decision = {
        "result": "trigger",
        "reason": "subject_artifact_pending",
        "mode": state.get("session_last_agent_mode"),
        "phase": phase,
        "artifact": latest_subject,
    }
    REPO_ROOT.mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / "cron_decision.json").write_text(json.dumps(decision, indent=2, sort_keys=True))
    print(json.dumps(decision))

    trigger_actuator(ACTUATOR_NAME)
    import time
    time.sleep(2)  # Let the DB row commit settle before polling.
    mode = decision.get("mode") or state.get("session_last_agent_mode") or "I"
    outcome, status = get_actuator_outcome(ACTUATOR_ID)
    if outcome:
        record_outcome(outcome, mode, phase=decision.get("phase"))
        log_line(f"outcome:{outcome}")
    else:
        log_line(f"outcome_missing:{status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
