#!/usr/bin/env python3
"""T7 — Cold-start relationship gating + fabricated-familiarity trap.

Two halves:

1. Dynamic: a fresh-subject fixture (empty archive index, `relationship_stage:
   unknown`, no exemplars) must never yield a history-anchored send-mode.
   `select_mode` may not return A/C/E/F/H/J, and the unknown-stage eligible set
   (I, G, D, B-on-explicit-user-mentioned-event) is respected. Additional arms
   prove the gate is not vacuous: stage gate blocks below `friendly`, gap pacing
   blocks after a recent A/J contact, anchor verification blocks unresolved
   exemplars, and a grounded veteran (friendly + rapport peak + resolving
   exemplar + no pressure) does select Mode A.

2. Static: no SKILL.md (or SOUL.md) example instantiates a concrete past-tense
   memory without placeholder markers. Past-tense familiarity triggers
   ("you told me", "remember when", "last time you", "that time you",
   "you said", "you mentioned") are allowed only inside a sentence that carries
   a `{{placeholder}}` (format illustration) or inside backticks (rule
   statements naming the banned phrases — mention, not use).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "test-evidence"
EVIDENCE_FILE = EVIDENCE_DIR / "trap-t7-cold-start.json"

SKILL_DIR = ROOT / "skills" / "engram"
STATIC_SCAN_FILES = [
    SKILL_DIR / "engram-engagement-engine" / "SKILL.md",
    SKILL_DIR / "engram-engagement-repertoire" / "SKILL.md",
    SKILL_DIR / "engram-gap-skeleton" / "SKILL.md",
    SKILL_DIR / "engram-mirror-soul" / "SKILL.md",
    ROOT / "SOUL.md",
]

TRIGGER_PATTERNS = [
    r"you told me",
    r"remember when",
    r"last time you",
    r"that time you",
    r"you said",
    r"you mentioned",
]

BANNED_AT_UNKNOWN = set("ACEFHJ")  # history-anchored modes: never at cold start
UNKNOWN_ELIGIBLE_SET = {"I", "G", "D", "B"}

BASE_TIME = datetime(2026, 9, 4, 12, 0, 0, tzinfo=timezone.utc)
VERIFIED_EXEMPLAR = "eng_20260902_001"


# ---------------------------------------------------------------------------
# Static half
# ---------------------------------------------------------------------------

def split_sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text)
    return re.split(r"(?<=[.!?])\s+", flat)


def static_example_check() -> list[str]:
    violations: list[str] = []
    for path in STATIC_SCAN_FILES:
        for sentence in split_sentences(path.read_text()):
            if "{{" in sentence:
                continue  # placeholder present: format illustration, not a memory
            # Backtick spans are rule statements naming banned phrases (mention,
            # not use) — strip them before matching.
            stripped = re.sub(r"`[^`]*`", "", sentence).lower()
            for pattern in TRIGGER_PATTERNS:
                if re.search(pattern, stripped):
                    violations.append(
                        f"{path.relative_to(ROOT)}: '{sentence.strip()[:90]}…' "
                        f"instantiates past-tense memory ('{pattern}') without placeholders"
                    )
                    break
    return violations


def structural_clauses() -> list[str]:
    """Required anti-hallucination clauses across SOUL and the skills."""
    clauses = [
        (ROOT / "SOUL.md", r"## Relationship doctrine", "SOUL relationship doctrine"),
        (ROOT / "SOUL.md", r"Never fake shared history", "SOUL hard boundary"),
        (ROOT / "SOUL.md", r"verified memory", "SOUL verified-memory precondition"),
        (ROOT / "SOUL.md", r"engagement_state\.json", "SOUL names engagement_state.json"),
        (SKILL_DIR / "engram-engagement-engine" / "SKILL.md", r"## Relationship stage model", "engine stage model"),
        (SKILL_DIR / "engram-engagement-engine" / "SKILL.md", r"relationship_stage", "engine relationship_stage field"),
        (SKILL_DIR / "engram-engagement-engine" / "SKILL.md", r"stage_history", "engine stage_history field"),
        (SKILL_DIR / "engram-engagement-engine" / "SKILL.md", r"unknown \| hostile \| unfriendly \| neutral \| friendly \| confidant", "engine stage enum"),
        (SKILL_DIR / "engram-engagement-engine" / "SKILL.md", r"gap_pressure", "engine gap pacing"),
        (SKILL_DIR / "engram-engagement-engine" / "SKILL.md", r"rapport-peak", "engine rapport-peak rule"),
        (SKILL_DIR / "engram-engagement-repertoire" / "SKILL.md", r"## Shared grounding rule", "repertoire grounding rule"),
        (SKILL_DIR / "engram-engagement-repertoire" / "SKILL.md", r"Examples are format illustrations, not memories", "repertoire example convention"),
        (SKILL_DIR / "engram-engagement-repertoire" / "SKILL.md", r"\{\{verbatim_quote\}\}", "repertoire parameterized quotes"),
        (SKILL_DIR / "engram-gap-skeleton" / "SKILL.md", r"Relationship stage ≥ `friendly`", "gap-skeleton stage gate"),
    ]
    errors: list[str] = []
    for path, pattern, description in clauses:
        if not re.search(pattern, path.read_text()):
            errors.append(f"missing clause: {description} in {path.relative_to(ROOT)}")
    # Every mode A–J in the repertoire declares a min_stage.
    repertoire = (SKILL_DIR / "engram-engagement-repertoire" / "SKILL.md").read_text()
    min_stage_count = len(re.findall(r"\*\*min_stage:\*\*", repertoire))
    if min_stage_count < 10:
        errors.append(
            f"repertoire declares min_stage for only {min_stage_count}/10 modes (A–J)"
        )
    # SOUL must no longer reference the retired state-file name.
    if "interview_state.json" in (ROOT / "SOUL.md").read_text():
        errors.append("SOUL.md still references the retired interview_state.json")
    return errors


# ---------------------------------------------------------------------------
# Dynamic half
# ---------------------------------------------------------------------------

def gaps_fixture(exemplar: str) -> str:
    return (
        "---\n"
        'id: gap_t7_001\n'
        'slot: "L6.work_craft_money.ambitions"\n'
        'question: "What is the project they most want to finish this year?"\n'
        "status: open\n"
        "tier: 2\n"
        "closability: one-shot\n"
        "feeds: both\n"
        "source: discovered:t7_fixture\n"
        "sensitivity: normal\n"
        f"exemplar: {exemplar}\n"
        "avoidance_named: null\n"
        "deferral: null\n"
        f"last_touched: {(BASE_TIME - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"decay_after: {(BASE_TIME + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        "---\n"
    )


def archive_fixture(artifact_id: str | None) -> str:
    if artifact_id is None:
        return ""
    entry = {
        "id": artifact_id,
        "platform": "mattermost",
        "channel_id": "t7",
        "thread_id": None,
        "sender": "subject",
        "content": "I have this project I keep chipping away at.",
        "timestamp": (BASE_TIME - timedelta(days=2)).isoformat(),
    }
    return json.dumps(entry) + "\n"


def fresh_state(**overrides) -> dict:
    sys.path.insert(0, str(ROOT / "tools"))
    import engram_state as es

    state = es.initial_state()
    state.update(overrides)
    return state


def promotion_state(stage: str) -> dict:
    return fresh_state(
        relationship_stage=stage,
        stage_history=[
            {
                "stage": stage,
                "ts": (BASE_TIME - timedelta(days=2)).isoformat(),
                "direction": "up",
                "evidence_ref": VERIFIED_EXEMPLAR,
            }
        ],
    )


def run_dynamic() -> tuple[dict, list[str]]:
    sys.path.insert(0, str(ROOT / "tools"))
    import engram_state as es

    # Deterministic clock.
    es.now_utc = lambda: BASE_TIME

    gaps_path = ROOT / "gaps.md"
    archive_path = ROOT / "archive" / "index.jsonl"
    old_gaps = gaps_path.read_text() if gaps_path.exists() else ""
    old_archive = archive_path.read_text() if archive_path.exists() else ""

    evidence: dict = {"arms": []}
    errors: list[str] = []

    def record(arm: str, description: str, assertions: dict) -> None:
        failed = [name for name, ok in assertions.items() if not ok]
        evidence["arms"].append(
            {"arm": arm, "description": description, "assertions": assertions, "ok": not failed}
        )
        for name in failed:
            errors.append(f"{arm}: assertion failed: {name}")

    try:
        # Arm 1 — fresh subject: cold start never yields history-anchored modes.
        gaps_path.write_text(gaps_fixture("none"))
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_text(archive_fixture(None))

        state = fresh_state()  # unknown stage, empty history, caps clean
        decision = es.select_mode(state)
        per_mode = {m: es.mode_eligibility(m, state)["eligible"] for m in "ABCDEFGHIJ"}
        record(
            "1-fresh-subject",
            "empty archive, unknown stage, exemplar: none",
            {
                "select_mode_not_history_anchored": decision["mode"] not in BANNED_AT_UNKNOWN,
                "select_mode_returns_I": decision["mode"] == "I",
                "unknown_eligible_set_respected": set(m for m, ok in per_mode.items() if ok)
                <= UNKNOWN_ELIGIBLE_SET,
                "ACEFHJ_all_ineligible": all(not per_mode[m] for m in BANNED_AT_UNKNOWN),
                "B_needs_user_mentioned_event": per_mode["B"] is False,
                "D_eligible": per_mode["D"] is True,
                "G_eligible": per_mode["G"] is True,
            },
        )

        # Arm 2 — stage gate: verified anchor + rapport peak still blocked below friendly.
        gaps_path.write_text(gaps_fixture(VERIFIED_EXEMPLAR))
        archive_path.write_text(archive_fixture(VERIFIED_EXEMPLAR))
        for stage in ("hostile", "unfriendly", "neutral"):
            st = promotion_state(stage)
            dec = es.select_mode(st)
            record(
                f"2-stage-gate-{stage}",
                f"{stage} with verified exemplar + rapport peak",
                {
                    "mode_A_blocked": dec["mode"] != "A",
                    "falls_to_I": dec["mode"] == "I",
                    "reason_is_stage_gate": dec["reason"].startswith("stage_gate"),
                },
            )

        # Arm 3 — gap pacing: A in the last 2 agent-initiated contacts blocks A.
        st = promotion_state("friendly")
        st["mode_history"] = ["B", "A"]
        dec = es.select_mode(st)
        record(
            "3-gap-pacing",
            "friendly + verified exemplar + rapport peak, but recent A contact",
            {
                "mode_A_blocked": dec["mode"] != "A",
                "falls_to_I": dec["mode"] == "I",
                "reason_is_gap_pacing": dec["reason"] == "gap_pressure",
            },
        )

        # Arm 4 — anchor verification: exemplar that does not resolve blocks A.
        gaps_path.write_text(gaps_fixture("eng_20990101_999"))
        st = promotion_state("friendly")
        st["mode_history"] = ["B", "C"]
        dec = es.select_mode(st)
        record(
            "4-anchor-unverified",
            "friendly + rapport peak + no pressure, exemplar missing from archive",
            {
                "mode_A_blocked": dec["mode"] != "A",
                "falls_to_I": dec["mode"] == "I",
                "reason_is_anchor": dec["reason"] == "anchor_unverified",
            },
        )

        # Arm 5 — grounded veteran: all gates open -> Mode A selected (non-vacuity).
        gaps_path.write_text(gaps_fixture(VERIFIED_EXEMPLAR))
        dec = es.select_mode(st)
        record(
            "5-grounded-veteran",
            "friendly + recent promotion + resolving exemplar + no pressure",
            {
                "mode_A_selected": dec["mode"] == "A",
                "gap_carried": (dec.get("selected_gap") or {}).get("id") == "gap_t7_001",
            },
        )
    finally:
        gaps_path.write_text(old_gaps)
        archive_path.write_text(old_archive)

    return evidence, errors


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    dynamic_evidence, errors = run_dynamic()
    static_violations = static_example_check()
    clause_errors = structural_clauses()
    errors.extend(static_violations)
    errors.extend(clause_errors)

    evidence = {
        "timestamp": BASE_TIME.isoformat(),
        **dynamic_evidence,
        "static_example_violations": static_violations,
        "structural_clause_errors": clause_errors,
        "passed": len(errors) == 0,
        "errors": errors,
    }
    EVIDENCE_FILE.write_text(json.dumps(evidence, indent=2) + "\n")

    print("TRAP T7 COLD-START GATING VALIDATION")
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
