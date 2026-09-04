#!/usr/bin/env python3
"""T8 — Promotion-velocity (sigmoid) trap for Engram stage transitions.

Verifies the tooling-enforced dwell minimums and the one-rung-per-review cap in
`record_stage_transition` (engine stage model, promotion-velocity section):

- ->confidant requires >= 14 days at friendly (a friendly entry <14 days old is
  rejected with a dwell reason; a 2-day-old entry likewise).
- ->friendly requires >= 3 days at neutral (a 1-day-old neutral is rejected).
- A 4-day-old neutral -> friendly IS accepted (non-vacuity).
- A 15-day-old friendly -> confidant IS accepted (non-vacuity).
- Demotion friendly -> unfriendly on one strong negative IS accepted (one
  severity step: a strong negative from any non-negative stage falls to
  unfriendly), while friendly -> hostile is rejected with a one-rung reason
  (two severity steps — no hostile whiplash). Additional demotion pins:
  unfriendly -> hostile IS accepted (the legal second step); confidant ->
  hostile is rejected; neutral -> unfriendly is accepted (adjacent rung).
- unknown-resolution is exempt from dwell: unknown -> friendly is accepted with
  an empty history (nothing to dwell in); unknown -> confidant stays rejected
  (confidant always requires the friendly dwell below it).
- A rejection writes nothing: state and stage_history are unchanged.

Synthetic state injection harness: snapshots engagement_state.json, injects
fixtures, calls the real record_stage_transition with a fixed clock, restores.
Writes evidence to test-evidence/trap-t8-velocity.json.
"""
from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "test-evidence"
EVIDENCE_FILE = EVIDENCE_DIR / "trap-t8-velocity.json"

BASE_TIME = datetime(2026, 9, 4, 12, 0, 0, tzinfo=timezone.utc)
VERIFIED_EXEMPLAR = "eng_20260902_001"


def base_state(stage: str, entered_days_ago: float | None) -> dict:
    """Fixture: current `stage` with a stage_history entry recording when it
    was entered (None = stage present but no history establishing it)."""
    history = []
    if entered_days_ago is not None:
        history.append(
            {
                "stage": stage,
                "ts": (BASE_TIME - timedelta(days=entered_days_ago)).isoformat(),
                "direction": "up",
                "evidence_ref": VERIFIED_EXEMPLAR,
            }
        )
    return {
        "relationship_stage": stage,
        "stage_history": history,
        "last_stage_review_ts": None,
    }


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT / "tools"))
    import engram_state as es

    state_path = ROOT / "engagement_state.json"
    old_state = state_path.read_text() if state_path.exists() else ""

    evidence: dict = {"timestamp": BASE_TIME.isoformat(), "arms": [], "passed": False}
    errors: list[str] = []

    def run_arm(
        arm: str,
        description: str,
        fixture: dict,
        target: str,
        direction: str,
        expect_ok: bool,
        reason_prefix: str | None,
    ) -> None:
        state_path.write_text(json.dumps(fixture, indent=2, sort_keys=True))
        result = es.record_stage_transition(
            target, direction, VERIFIED_EXEMPLAR, now=BASE_TIME
        )
        after = json.loads(state_path.read_text())
        ok = result.get("ok") is expect_ok
        reason = result.get("reason")
        reason_ok = True
        if reason_prefix is not None:
            reason_ok = isinstance(reason, str) and reason.startswith(reason_prefix)
        unchanged = (
            after.get("relationship_stage") == fixture["relationship_stage"]
            and after.get("stage_history") == fixture["stage_history"]
        )
        assertions = {
            "ok_matches_expectation": ok,
            "reason_matches_prefix": reason_ok,
            "rejection_wrote_nothing": unchanged if not expect_ok else True,
        }
        evidence["arms"].append(
            {
                "arm": arm,
                "description": description,
                "transition": f"{fixture['relationship_stage']}->{target}:{direction}",
                "result": result if not expect_ok else {"ok": True},
                "reason": reason,
                "assertions": assertions,
            }
        )
        failed = [name for name, a in assertions.items() if not a]
        if failed:
            errors.append(f"{arm}: assertion failed: {', '.join(failed)}")

    try:
        # Dwell: ->confidant requires >=14 days at friendly.
        run_arm(
            "1-confidant-dwell-10d",
            "friendly entered 10 days ago -> confidant",
            base_state("friendly", 10), "confidant", "up",
            expect_ok=False, reason_prefix="dwell:",
        )
        run_arm(
            "2-confidant-dwell-2d",
            "friendly entered 2 days ago -> confidant",
            base_state("friendly", 2), "confidant", "up",
            expect_ok=False, reason_prefix="dwell:",
        )
        # Dwell: ->friendly requires >=3 days at neutral.
        run_arm(
            "3-friendly-dwell-1d",
            "neutral entered 1 day ago -> friendly",
            base_state("neutral", 1), "friendly", "up",
            expect_ok=False, reason_prefix="dwell:",
        )
        # Non-vacuity: legal dwells ARE accepted.
        run_arm(
            "4-friendly-dwell-4d",
            "neutral entered 4 days ago -> friendly",
            base_state("neutral", 4), "friendly", "up",
            expect_ok=True, reason_prefix=None,
        )
        run_arm(
            "5-confidant-dwell-15d",
            "friendly entered 15 days ago -> confidant",
            base_state("friendly", 15), "confidant", "up",
            expect_ok=True, reason_prefix=None,
        )
        # One transition per review, both directions.
        run_arm(
            "6-demotion-one-rung",
            "friendly -> unfriendly on one strong negative",
            base_state("friendly", 10), "unfriendly", "down",
            expect_ok=True, reason_prefix=None,
        )
        run_arm(
            "7-demotion-two-rungs",
            "friendly -> hostile (two severity steps down) is whiplash",
            base_state("friendly", 10), "hostile", "down",
            expect_ok=False, reason_prefix="one_rung_max:",
        )
        run_arm(
            "7b-demotion-adjacent-rung",
            "neutral -> unfriendly (adjacent rung down)",
            base_state("neutral", 10), "unfriendly", "down",
            expect_ok=True, reason_prefix=None,
        )
        run_arm(
            "7c-demotion-second-severity-step",
            "unfriendly -> hostile (the legal second step, next night)",
            base_state("unfriendly", 10), "hostile", "down",
            expect_ok=True, reason_prefix=None,
        )
        run_arm(
            "7d-demotion-confidant-to-hostile",
            "confidant -> hostile is whiplash regardless of current warmth",
            base_state("confidant", 20), "hostile", "down",
            expect_ok=False, reason_prefix="one_rung_max:",
        )
        # unknown-resolution exempt from dwell.
        run_arm(
            "8-unknown-resolves-friendly",
            "unknown (no history) -> friendly: no rung to dwell in",
            base_state("unknown", None), "friendly", "up",
            expect_ok=True, reason_prefix=None,
        )
        run_arm(
            "9-unknown-never-confidant",
            "unknown -> confidant: confidant always needs the friendly dwell",
            base_state("unknown", None), "confidant", "up",
            expect_ok=False, reason_prefix="dwell:",
        )
        # Promotion with no history establishing entry time fails closed.
        run_arm(
            "10-friendly-no-entry-ts",
            "friendly with no stage_history entry -> confidant",
            base_state("friendly", None), "confidant", "up",
            expect_ok=False, reason_prefix="dwell:",
        )

        # Success arms must have written the transition + review stamp.
        state_path.write_text(json.dumps(base_state("neutral", 4), indent=2, sort_keys=True))
        es.record_stage_transition("friendly", "up", VERIFIED_EXEMPLAR, now=BASE_TIME)
        after = json.loads(state_path.read_text())
        ok_write = (
            after["relationship_stage"] == "friendly"
            and after["stage_history"][-1]["stage"] == "friendly"
            and after["stage_history"][-1]["evidence_ref"] == VERIFIED_EXEMPLAR
            and after["last_stage_review_ts"] is not None
        )
        evidence["arms"].append(
            {
                "arm": "11-success-write",
                "description": "accepted transition appends entry, sets stage, stamps review",
                "assertions": {"transition_written_and_stamped": ok_write},
            }
        )
        if not ok_write:
            errors.append("11-success-write: assertion failed: transition_written_and_stamped")
    finally:
        state_path.write_text(old_state) if old_state else state_path.unlink(missing_ok=True)

    evidence["passed"] = len(errors) == 0
    evidence["errors"] = errors
    EVIDENCE_FILE.write_text(json.dumps(evidence, indent=2) + "\n")

    print("TRAP T8 PROMOTION-VELOCITY VALIDATION")
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
