#!/usr/bin/env python3
"""Director: engram mode-selector cron.

Pure deterministic pre-run. Writes a decision file and, if a send-mode is
selected, triggers the matching actuator cron job. Idle ticks consume zero LLM
tokens.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engram_state import (
    REPO_ROOT,
    ensure_state,
    get_actuator_outcome,
    load_state,
    now_utc,
    record_outcome,
    run_accounting,
    select_mode,
)

DECISION_PATH = REPO_ROOT / "cron_decision.json"
LOG_PATH = REPO_ROOT / "cron_output" / "selector.log"

# Actuator routing, collapsed 2026-09-04 with the skill consolidation: modes B–H
# share the single parameterized mode-execution actuator (the former per-mode
# stubs are gone); Mode A keeps its dedicated tool-less interview-probe
# actuator. The hermes cron *job IDs* (needed for outcome polling via
# get_actuator_outcome) are install-time values — the one below is from the
# 2026-08-28 throwaway round. Rebind at install; while an ID is unknown the
# director triggers by name and skips outcome polling (logged as
# outcome_missing:no_job_id).
ACTUATORS = {
    "A": ("interview-probe", "1bf4019bdabb"),
    "B": ("mode-execution", None),
    "C": ("mode-execution", None),
    "D": ("mode-execution", None),
    "E": ("mode-execution", None),
    "F": ("mode-execution", None),
    "G": ("mode-execution", None),
    "H": ("mode-execution", None),
}


def log_line(line: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{now_utc().isoformat()} {line}\n")


def trigger_actuator(name: str) -> None:
    """Non-blocking trigger of an actuator cron job by name (or job ID)."""
    import subprocess

    subprocess.run(
        ["hermes", "--profile", "engram", "cron", "run", name],
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    summary = run_accounting()
    state = load_state()
    decision = select_mode(state)
    decision["accounting_summary"] = summary
    decision["timestamp"] = now_utc().isoformat()

    DECISION_PATH.parent.mkdir(parents=True, exist_ok=True)
    DECISION_PATH.write_text(json.dumps(decision, indent=2, sort_keys=True))

    if decision.get("stop") or decision.get("mode") == "I":
        log_line(f"silence:{decision.get('reason', 'unknown')}")
        print(json.dumps({"result": "silence", "reason": decision.get("reason")}))
        return 0

    actuator = ACTUATORS.get(decision["mode"])
    if not actuator:
        log_line(f"silence:no_actuator_for_mode:{decision['mode']}")
        print(json.dumps({"result": "silence", "reason": f"no_actuator_for_mode:{decision['mode']}"}))
        return 0
    actuator_name, actuator_id = actuator

    selected_gap_id = (decision.get("selected_gap") or {}).get("id")

    log_line(f"selected:{decision['mode']}:{decision.get('reason', '')}")
    print(json.dumps({"result": "selected", "mode": decision["mode"], "actuator": actuator_name}))

    # Trigger and capture the actuator outcome so the engine can update
    # last_contact_ts, mode_last_sent, and session fields.
    trigger_actuator(actuator_name)
    if actuator_id is None:
        log_line("outcome_missing:no_job_id")
        return 0
    import time
    time.sleep(2)  # Let the DB row commit settle before polling.
    outcome, status = get_actuator_outcome(actuator_id)
    if outcome:
        record_outcome(outcome, decision["mode"], gap_id=selected_gap_id)
        log_line(f"outcome:{outcome}")
    else:
        log_line(f"outcome_missing:{status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
