#!/usr/bin/env python3
"""Director: Mode I silence / cooling-lock monitor.

Deterministic heartbeat. Logs the current cooling state and clears any expired
cooling lock via the shared accounting path. Never wakes the Engram profile.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engram_state import REPO_ROOT, load_state, now_utc, parse_iso, run_accounting

LOG_PATH = REPO_ROOT / "cron_output" / "mode_i.log"


def log_line(line: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{now_utc().isoformat()} {line}\n")


def main() -> int:
    summary = run_accounting()
    state = load_state()
    cooling_until = parse_iso(state.get("cooling_until"))
    now = now_utc()

    if cooling_until is None:
        log_line("silence:no_cooling_lock")
        print(json.dumps({"result": "silence", "reason": "no_cooling_lock"}))
        return 0

    if now <= cooling_until:
        remaining = int((cooling_until - now).total_seconds())
        log_line(f"cooling:active:{remaining}s")
        print(json.dumps({"result": "silence", "reason": f"cooling_lock_active:{remaining}s"}))
    else:
        log_line("cooling:expired")
        print(json.dumps({"result": "silence", "reason": "cooling_lock_expired"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
