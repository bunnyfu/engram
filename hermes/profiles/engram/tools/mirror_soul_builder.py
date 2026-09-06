#!/usr/bin/env python3
"""Scaffold the Mirror-SOUL USER.md for the Engram profile.

Deterministic bootstrap tool (spec: ~/.hermes/plans/2026-09-05-mirror-soul-usermd-builder-spec.md,
§E --mode scaffold): writes the USER.md scaffold — title, machine provenance
line carrying the `scaffold` marker, and the nine fixed section headings with
empty bodies — and ensures <root>/archive/ exists with an empty index.jsonl
(created only if absent).

Single-writer discipline: the dream-phase LLM authors all USER.md content;
this tool never writes content, and never touches gaps.md,
engagement_state.json, or archive entries. There is deliberately NO
content-refresh mode — a deterministic rewriter would collide with LLM
authorship (spec §E); an unknown --mode is rejected.

Failure modes (spec §F):
  F2  USER.md exists and is content-bearing (its `Build:` provenance line
      lacks the `scaffold` marker, or has no provenance line) → named error,
      exit 1, nothing written.
Idempotency (spec G4): re-running over an existing pure scaffold is a
no-op (exit 0, file untouched), so repeated scaffolds are byte-identical.

Root resolution (all modes), in precedence order: --root > env
ENGRAM_PROFILE_ROOT > parents[1] of this file (the profile root).
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Keep in sync with tools/validate-mirror-soul.py (standalone scripts, no imports).
TITLE = "# USER.md — Mirror-SOUL of the subject (SUBJECT_HANDLE)"
SECTIONS = [
    "Identity",
    "Biography",
    "Beliefs / worldview",
    "Style register",
    "Relationships",
    "Goals",
    "Stories bank",
    "Interests",
    "Dates",
]
SCAFFOLD_MARKER = "scaffold"
PRODUCER = "mirror_soul_builder.py"


def resolve_root(cli_root: str | None) -> Path:
    if cli_root:
        return Path(cli_root).expanduser().resolve()
    env_root = os.environ.get("ENGRAM_PROFILE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def provenance_line(ts: str) -> str:
    return f"Build: {PRODUCER} {SCAFFOLD_MARKER} {ts}"


def scaffold_text(ts: str) -> str:
    parts = [TITLE, provenance_line(ts), ""]
    for section in SECTIONS:
        parts.append(f"## {section}")
        parts.append("")
    return "\n".join(parts).rstrip("\n") + "\n"


def is_pure_scaffold(text: str) -> bool:
    """A USER.md is a pure scaffold iff its `Build:` provenance line carries
    the scaffold marker (spec §B: the marker is how the tool distinguishes a
    pure scaffold from content-bearing USER.md). Whitespace-only files are
    scaffodable (F2 covers files 'with content')."""
    if not text.strip():
        return True
    for line in text.splitlines():
        if line.startswith("Build: "):
            return SCAFFOLD_MARKER in line.split()
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold the Mirror-SOUL USER.md (no content-refresh mode by design)."
    )
    parser.add_argument(
        "--mode",
        choices=("scaffold",),
        default="scaffold",
        help="only 'scaffold' exists; content refresh is intentionally not a tool mode",
    )
    parser.add_argument("--root", default=None, help="profile root (default: ENGRAM_PROFILE_ROOT, then this file's parent)")
    args = parser.parse_args()

    root = resolve_root(args.root)
    user_md = root / "USER.md"
    archive_dir = root / "archive"
    archive_index = archive_dir / "index.jsonl"

    if user_md.exists():
        existing = user_md.read_text()
        if not is_pure_scaffold(existing):
            print("MIRROR-SOUL SCAFFOLD REFUSED")
            print("  F2: refusing overwrite of content-bearing USER.md "
                  f"(provenance line lacks '{SCAFFOLD_MARKER}' marker): {user_md}")
            return 1
        # Pure scaffold (or empty file): idempotent no-op for USER.md itself.
        print("MIRROR-SOUL SCAFFOLD NO-OP")
        print(f"  pure scaffold already present, untouched: {user_md}")
    else:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        user_md.write_text(scaffold_text(ts))
        print("MIRROR-SOUL SCAFFOLD WRITTEN")
        print(f"  {user_md} (Build: {PRODUCER} {SCAFFOLD_MARKER} {ts})")

    # Archive ensure-dir runs on every scaffold invocation (spec §E), even no-ops.
    archive_dir.mkdir(parents=True, exist_ok=True)
    if not archive_index.exists():
        archive_index.write_text("")
        print(f"  created empty archive index: {archive_index}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
