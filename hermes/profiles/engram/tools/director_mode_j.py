#!/usr/bin/env python3
"""Director: Mode J naming-the-silence eligibility scanner.

Deterministic scan of gaps.md + archive for a tier-1/2 handle-with-care slot that
has zero mentions in the archive and is in an active warm exchange. Updates
engagement_state.json.mode_j_eligible. Never wakes the Engram profile.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engram_state import (
    REPO_ROOT,
    _parse_gaps_text,
    load_archive_index,
    load_state,
    now_utc,
    set_mode_j_eligible,
)

LOG_PATH = REPO_ROOT / "cron_output" / "mode_j.log"


def log_line(line: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{now_utc().isoformat()} {line}\n")


def load_gaps() -> list[dict[str, str]]:
    """Re-export of the shared ledger parser (engram_state._parse_gaps_text).

    Defect D1 (t2-findings.md): this module carried its own naive `key: value`
    splitter, so it parsed the canonical `avoidance_named: null` as the truthy
    STRING "null" and skipped every slot — the Mode J eligibility predicate was
    dead as shipped. One parser, both consumers.
    """
    gaps_path = REPO_ROOT / "gaps.md"
    if not gaps_path.exists():
        return []
    return _parse_gaps_text(gaps_path.read_text())


def has_zero_mentions(slot: dict[str, str]) -> bool:
    idx = load_archive_index()
    topic = slot.get("topic") or slot.get("id") or ""
    aliases = [a.strip() for a in (slot.get("aliases") or "").split(",") if a.strip()]
    terms = [topic] + aliases
    if not terms or not terms[0]:
        return True
    for artifact in idx:
        text = f"{artifact.get('content', '')} {artifact.get('sender', '')}".lower()
        for term in terms:
            if term.lower() in text:
                return False
    return True


def main() -> int:
    state = load_state()
    eligible = None
    reason = "no_eligible_slot"

    gaps = load_gaps()
    for slot in gaps:
        status = slot.get("status", "open").lower()
        sensitivity = slot.get("sensitivity", "").lower()
        tier = slot.get("tier")
        avoidance = slot.get("avoidance_named")
        try:
            tier_int = int(tier) if tier is not None else 1
        except ValueError:
            tier_int = 1
        if sensitivity != "handle-with-care":
            continue
        if tier_int > 2:
            continue
        if status in ("declined", "closed", "versioned", "deferred-open"):
            continue
        if avoidance is not None:
            # Explicit skip condition — D1 lesson: a truthiness test here read
            # the parsed "null" STRING as set and skipped every slot. Bare
            # none/null normalizes to Python None (no avoidance named); any
            # other value (a timestamp) means the subject dodged this topic.
            continue
        if not has_zero_mentions(slot):
            continue
        # Require active warm exchange (subject sent in current session).
        if not state.get("session_active") or state.get("session_opened_by") != "subject":
            continue
        eligible = slot
        reason = f"eligible:{slot['id']}"
        break

    set_mode_j_eligible(eligible["id"] if eligible else None)
    log_line(reason)
    print(json.dumps({"result": "scan", "mode_j_eligible": state["mode_j_eligible"], "reason": reason}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
