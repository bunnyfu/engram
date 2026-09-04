#!/usr/bin/env python3
"""Generic actuator pre-run: load the director decision and print a concise summary.

The actual drafting and send is performed by the agent prompt, which receives this
script output as context.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Profile root (hermes/profiles/engram) — one directory up from tools/.
DECISION_PATH = Path(__file__).resolve().parents[1] / "cron_decision.json"

def main() -> int:
    if not DECISION_PATH.exists():
        print("No director decision found. Exit silently.")
        return 0
    decision = json.loads(DECISION_PATH.read_text())
    mode = decision.get("mode")
    reason = decision.get("reason", "")
    selected_gap = decision.get("selected_gap")
    phase = decision.get("phase", "open")
    artifact = decision.get("artifact")

    print(f"DIRECTOR DECISION: mode={mode} phase={phase} reason={reason}")
    if selected_gap:
        print(f"SELECTED GAP: {json.dumps(selected_gap)}")
    if artifact:
        print(f"SUBJECT ARTIFACT: {json.dumps(artifact)}")
    print(f"FULL DECISION: {json.dumps(decision)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
