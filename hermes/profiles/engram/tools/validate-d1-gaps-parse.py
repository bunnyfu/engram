#!/usr/bin/env python3
"""D1 regression — canonical gaps.md scalar grammar parses like YAML.

Defect (t2-findings.md D1, forge card t_15a4c501): both load_gaps() parsers
(engram_state.py, director_mode_j.py) split `key: value` naively, so the
canonical shipped ledger's literal `avoidance_named: null` parsed as the
truthy STRING "null" — and director_mode_j's truthiness skip then dropped
EVERY slot. Result: the Mode J eligibility predicate was dead as shipped;
`no_eligible_slot` on every scan, zero Mode J sends possible on the canonical
format. (Same defect class: `exemplar: none`, `deferral: null`.)

Arms (regression direction — the defect reproduced here must stay red):

  1. parse_scalar unit grammar — bare null/none/empty -> None (case-,
     whitespace-insensitive); quoted "null"/'none' stay strings (fail-closed);
     real scalars (timestamps, ids, quoted prose) survive verbatim.
  2. Canonical ledger fixture (verbatim t2 G-grid GAP_OPEN_HWC shape):
     avoidance_named/deferral parse to None, exemplar "none" -> None, real
     fields (tier, timestamps, quoted slot/question) survive; both consumers
     (engram_state.load_gaps, director_mode_j.load_gaps) return identical
     entries (one shared parser).
  3. Predicate E2E on the canonical fixture: a fully eligible canonical slot
     (open, tier 2, handle-with-care, avoidance_named: null) IS selected by
     the real director_mode_j subprocess — the exact case that shipped dead.
  4. Predicate discrimination intact: avoidance_named set to a timestamp
     still skips the slot.
  5. Mode A anchor path fails closed: select_mode on a ledger whose exemplar
     normalizes to None reports "anchor_none" — normalization must not open a
     no-anchor send path (fabricated-familiarity trap, T7 class).

Sandbox-only: ENGRAM_STATE_ROOT is bound to a fresh tempdir cell BEFORE the
first tools import; every module re-bind purges sys.modules so reads/writes
land in the active cell. Deterministic (frozen clock), zero LLM wakes, no
live-profile access. Standalone, stdlib-only, sibling conventions: prints
"D1 GAPS-PARSE VALIDATION PASSED" and exits 0 on success, "D1 GAPS-PARSE
VALIDATION FAILED" plus one line per failing arm, exit 1. Evidence is written
to test-evidence/d1-gaps-parse.json (gitignored).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PROFILE = TOOLS.parent
ROOT = PROFILE.parents[2]
EVIDENCE_DIR = PROFILE / "test-evidence"
EVIDENCE_FILE = EVIDENCE_DIR / "d1-gaps-parse.json"
PY = sys.executable

# Frozen clock — the director's log_line timestamps via now_utc; determinism
# here means the FILESYSTEM behavior, not the log string.
BASE_TIME = datetime(2026, 9, 5, 10, 0, 0, tzinfo=timezone.utc)

# Verbatim G-grid canonical fixture shape (t2_mechanics.py GAP_OPEN_HWC): the
# exact ledger format whose literal null killed the predicate as shipped.
CANONICAL_SLOT = """---
id: gap_d1_j1
slot: "L2.formative.family_of_origin"
question: "What was home like growing up?"
status: open
tier: 2
closability: story
feeds: both
source: skeleton
sensitivity: handle-with-care
exemplar: none
avoidance_named: null
deferral: null
last_touched: 2026-08-01T00:00:00Z
decay_after: 2026-10-01T00:00:00Z
---
"""

errors: list[str] = []
arms: list[dict] = []
_LAST: dict = {"stdout": "", "stderr": "", "rc": None}


def record(arm: str, description: str, assertions: dict) -> None:
    failed = [name for name, ok in assertions.items() if not ok]
    arms.append({"arm": arm, "description": description, "assertions": assertions, "ok": not failed})
    for name in failed:
        errors.append(f"{arm}: assertion failed: {name}")


def bind_tmp(profile_gaps: str) -> Path:
    """Fresh sandbox cell; ENGRAM_STATE_ROOT bound to it; tool modules purged
    so the next import re-binds to the cell. MUST precede any tools import."""
    cell = Path(tempfile.mkdtemp(prefix="d1-gaps-parse-"))
    os.environ["ENGRAM_STATE_ROOT"] = str(cell)
    for mod in list(sys.modules):
        if mod in ("engram_state", "director_mode_j"):
            del sys.modules[mod]
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    (cell / "gaps.md").write_text(profile_gaps)
    return cell


def _frozen_now():
    return BASE_TIME


def run_director(cell: Path) -> dict:
    """Run the real director subprocess against the bound cell."""
    r = subprocess.run(
        [PY, str(TOOLS / "director_mode_j.py")],
        capture_output=True, text=True,
        env={**os.environ, "ENGRAM_STATE_ROOT": str(cell)},
    )
    _LAST.update({"stdout": r.stdout, "stderr": r.stderr, "rc": r.returncode})
    return _LAST


def director_json() -> dict:
    try:
        return json.loads(_LAST["stdout"])
    except json.JSONDecodeError:
        return {}


def main() -> int:
    # Bind the FIRST cell before ANY tools import — everything below reads and
    # writes inside this cell until the next bind_tmp.
    cell = bind_tmp(CANONICAL_SLOT)
    import engram_state as es
    es.now_utc = _frozen_now

    # ------------------------------------------------------------------
    # Arm 1 — parse_scalar unit grammar.
    # ------------------------------------------------------------------
    ps = es.parse_scalar
    record(
        "1-parse-scalar",
        "bare null/none/empty -> None; quoted forms stay strings; real scalars survive",
        {
            "bare_null_lower": ps("null") is None,
            "bare_null_mixedcase": ps("Null") is None,
            "bare_none_lower": ps("none") is None,
            "bare_none_mixedcase": ps("NONE") is None,
            "empty_string": ps("") is None,
            "whitespace_only": ps("   ") is None,
            "quoted_double_null_stays_string": ps('"null"') == "null",
            "quoted_single_none_stays_string": ps("'none'") == "none",
            "timestamp_survives": ps("2026-09-01T00:00:00Z") == "2026-09-01T00:00:00Z",
            "id_survives": ps("gap_t2_j1") == "gap_t2_j1",
            "quoted_prose_survives": ps('"What was home like growing up?"') == "What was home like growing up?",
            "number_string_survives": ps("2") == "2",
        },
    )

    # ------------------------------------------------------------------
    # Arm 2 — canonical ledger parses with None where the ledger means null.
    # ------------------------------------------------------------------
    gaps = es.load_gaps()
    slot = gaps[0] if gaps else {}
    director_gaps = __import__("director_mode_j").load_gaps()
    record(
        "2-canonical-parse",
        "canonical fixture: none/null fields -> None, real fields survive, both consumers identical",
        {
            "one_slot_parsed": len(gaps) == 1,
            "avoidance_named_is_none": slot.get("avoidance_named") is None,
            "deferral_is_none": slot.get("deferral") is None,
            "exemplar_none_is_none": slot.get("exemplar") is None,
            "status_survives": slot.get("status") == "open",
            "tier_survives": slot.get("tier") == "2",
            "sensitivity_survives": slot.get("sensitivity") == "handle-with-care",
            "quoted_slot_survives": slot.get("slot") == "L2.formative.family_of_origin",
            "quoted_question_survives": slot.get("question") == "What was home like growing up?",
            "last_touched_survives": slot.get("last_touched") == "2026-08-01T00:00:00Z",
            "director_parser_same_result": director_gaps == gaps,
        },
    )

    # ------------------------------------------------------------------
    # Arm 3 — E2E: the exact predicate case that shipped dead now selects.
    # ------------------------------------------------------------------
    state = es.initial_state()
    state.update(
        {
            "relationship_stage": "friendly",
            "session_active": True,
            "session_opened_by": "subject",
            "mode_history": ["B"],  # no A/J gap pressure
        }
    )
    es.save_state(state)
    r3 = run_director(cell)
    out3 = director_json()
    record(
        "3-predicate-e2e",
        "canonical slot (avoidance_named: null) eligible when all other arms hold — the D1 case",
        {
            "director_exit_0": r3["rc"] == 0,
            "director_produced_json": bool(out3),
            "reason_is_eligible": out3.get("reason") == "eligible:gap_d1_j1",
            "state_slot_written": es.load_state().get("mode_j_eligible") == "gap_d1_j1",
        },
    )

    # ------------------------------------------------------------------
    # Arm 4 — discrimination intact: real avoidance value still skips.
    # ------------------------------------------------------------------
    cell4 = bind_tmp(
        CANONICAL_SLOT.replace("avoidance_named: null", "avoidance_named: 2026-09-01T00:00:00Z")
    )
    import engram_state as es4
    es4.now_utc = _frozen_now
    es4.save_state(es4.initial_state())
    r4 = run_director(cell4)
    out4 = director_json()
    record(
        "4-discrimination",
        "avoidance_named set to a timestamp still skips the slot",
        {
            "director_exit_0": r4["rc"] == 0,
            "director_produced_json": bool(out4),
            "reason_is_no_eligible_slot": out4.get("reason") == "no_eligible_slot",
            "state_slot_null": es4.load_state().get("mode_j_eligible") is None,
        },
    )

    # ------------------------------------------------------------------
    # Arm 5 — Mode A anchor path fails closed on a None-normalized exemplar.
    # ------------------------------------------------------------------
    bind_tmp(CANONICAL_SLOT)
    import engram_state as es5
    es5.now_utc = _frozen_now
    st = es5.initial_state()
    st.update(
        {
            "relationship_stage": "friendly",
            "stage_history": [
                {
                    "stage": "friendly",
                    "ts": (BASE_TIME - timedelta(days=2)).isoformat(),
                    "direction": "up",
                    "evidence_ref": "eng_x",
                }
            ],
            "mode_history": ["B"],
        }
    )
    decision = es5.select_mode(st)
    record(
        "5-anchor-fail-closed",
        "select_mode on exemplar-normalized-to-None reports anchor_none (no fail-open)",
        {
            "mode_falls_to_I": decision.get("mode") == "I",
            "reason_is_anchor_none": decision.get("reason") == "anchor_none",
            "no_send_selected": decision.get("selected_gap") is None,
        },
    )

    # ------------------------------------------------------------------
    # Campsite + evidence.
    # ------------------------------------------------------------------
    for c in (cell, cell4):
        shutil.rmtree(c, ignore_errors=True)
    os.environ.pop("ENGRAM_STATE_ROOT", None)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_FILE.write_text(json.dumps({
        "generated_at": BASE_TIME.isoformat(),
        "python": sys.version.split()[0],
        "passed": not errors,
        "arms": arms,
        "errors": errors,
    }, indent=2) + "\n")

    print("D1 GAPS-PARSE VALIDATION")
    if not errors:
        print("D1 GAPS-PARSE VALIDATION PASSED")
        print(f"Evidence: {EVIDENCE_FILE.relative_to(ROOT)}")
        return 0
    print("D1 GAPS-PARSE VALIDATION FAILED")
    for err in errors:
        print(f"  - {err}")
    print(f"Evidence: {EVIDENCE_FILE.relative_to(ROOT)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
