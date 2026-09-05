#!/usr/bin/env python3
"""Validate the Mirror-SOUL USER.md against the claim contract.

Deterministic post-write linter for the Engram profile's USER.md (spec:
~/.hermes/plans/2026-09-05-mirror-soul-usermd-builder-spec.md, §E --mode lint).
Validates:
  (a) structure — the nine fixed sections, exact headings, exact order (§B);
  (b) claim contract at 100%, no sampling (§B.2 / mirror-soul skill):
      every non-heading, non-quote block begins with a resolvable
      [synthesis: ...] tag; every quote block's text appears verbatim in the
      raw archive; every artifact id resolves in archive/index.jsonl;
  (c) dates-block entries carry anchors (date + label + exemplar anchor);
  (d) provenance line present and well-formed (`Build: <producer> <ts>`).

Output contract (sibling validators): pass → prints
`MIRROR-SOUL VALIDATION PASSED`, exit 0; fail → `MIRROR-SOUL VALIDATION
FAILED` + one named error per defect with line numbers, exit 1. Also emits a
machine-readable JSON summary to stdout (counts + unanchored-claim list, for
the dream phase). Never writes anything.

Failure modes (spec §F): F1 USER.md missing; F3 archive index missing or
unparseable (lint cannot verify anchors); F4 quote text not found verbatim in
the archive; F5 synthesis tag id not in index; F6 section
missing/renamed/out of order.

Root resolution (all modes), in precedence order: --root > env
ENGRAM_PROFILE_ROOT > parents[1] of this file (the profile root).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Keep in sync with tools/mirror_soul_builder.py (standalone scripts, no imports).
TITLE = "# USER.md — Mirror-SOUL of the subject ('caleb')"
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

SYNTHESIS_TAG_RE = re.compile(r"^\[synthesis:\s*([^\]]+)\]$")
ARTIFACT_ID_RE = re.compile(r"eng_\d{8}_\d+")
POINTER_RE = re.compile(r"—\s*\[artifact:\s*(eng_\d{8}_\d+)\s*\]")
CONFIDENCE_RE = re.compile(r"^\s*confidence:\s*(hint|pattern|firm)\s*$")

BLOCKQUOTE_PREFIX = ">"


def resolve_root(cli_root: str | None) -> Path:
    if cli_root:
        return Path(cli_root).expanduser().resolve()
    env_root = os.environ.get("ENGRAM_PROFILE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def load_archive(root: Path) -> tuple[list[dict], list[tuple[str, str]]]:
    """Load archive/index.jsonl. Returns (artifacts, load_errors)."""
    index_path = root / "archive" / "index.jsonl"
    if not index_path.exists():
        return [], [("F3", "archive/index.jsonl missing — lint cannot verify anchors")]
    artifacts = []
    try:
        for lineno, line in enumerate(
            index_path.read_text().splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                artifacts.append(json.loads(line))
            except json.JSONDecodeError as exc:
                return [], [
                    ("F3", f"archive/index.jsonl unparseable at line {lineno}: {exc}")
                ]
    except OSError as exc:
        return [], [("F3", f"archive/index.jsonl unreadable: {exc}")]
    return artifacts, []


def check_provenance(lines: list[str]) -> list[tuple[str, str]]:
    """(d) provenance line: present at line 2, `Build: <producer> <iso-ts> [marker...]`."""
    errors = []
    if len(lines) < 2 or not lines[1].startswith("Build: "):
        errors.append(
            ("F-provenance", "line 2: missing or malformed provenance line "
             "(expected `Build: <producer> <ISO-8601-UTC>`)"))
        return errors
    body = lines[1][len("Build: "):].strip()
    parts = body.split()
    if len(parts) < 2:
        errors.append(
            ("F-provenance", "line 2: provenance lacks producer and timestamp "
             f"(got `{lines[1]}`)"))
        return errors
    ts = parts[-1]
    if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", ts):
        errors.append(
            ("F-provenance", f"line 2: provenance timestamp `{ts}` is not ISO-8601 UTC "
             "(expected ...Thh:mm:ssZ)"))
    return errors


def check_structure(lines: list[str]) -> tuple[list[tuple[str, str]], dict[str, int]]:
    """(a) nine sections, exact headings, exact order. Returns (errors, {name: heading line no})."""
    errors: list[tuple[str, str]] = []
    found: dict[str, int] = {}
    doc_order: list[str] = []
    for i, line in enumerate(lines, start=1):
        if line.startswith("## "):
            name = line[3:].strip()
            if name not in found:
                doc_order.append(name)
            found[name] = i
        elif line.startswith("#") and not line.startswith("## ") and i > 1:
            errors.append(
                ("F6", f"line {i}: unexpected heading level `{line.strip()}` "
                 "(only the title `#` and the nine `##` section headings are allowed)"))
    missing = [s for s in SECTIONS if s not in found]
    if missing:
        errors.append(("F6", f"missing section heading(s): {missing}"))
    extra = [n for n in found if n not in SECTIONS]
    if extra:
        errors.append(("F6", f"unexpected section heading(s): {extra}"))
    if doc_order != SECTIONS:
        errors.append(("F6", f"section order is {doc_order} — required order is {SECTIONS}"))
    return errors, found


def block_sections(lines: list[str], section_lines: dict[str, int]) -> list[tuple[int, str]]:
    """Map each body line to its section. Headings and blank lines are never
    claim blocks; lines before the first section heading belong to none.
    Returns [(lineno, section_name), ...]."""
    out = []
    bounds = sorted(
        (ln, name) for name, ln in section_lines.items() if name in SECTIONS
    )
    for i, line in enumerate(lines, start=1):
        if not line.strip() or line.startswith("#"):
            continue
        owning = None
        for ln, name in bounds:
            if i > ln:
                owning = name
        if owning is not None:
            out.append((i, owning))
    return out


def check_claims(
    lines: list[str],
    artifacts: list[dict],
    section_lines: dict[str, int],
) -> tuple[list[tuple[str, str]], list[dict]]:
    """(b) claim contract at 100% and (c) dates-block anchors.

    Grammar (§B.2): a block is a maximal run of consecutive non-empty body
    lines. Quote lines are blockquotes (`>`); the first body line of every
    non-quote block must be a resolvable `[synthesis: ...]` tag. Quote blocks
    end with a pointer line `— [artifact: eng_...]`; their quoted text must
    appear verbatim in the raw archive. Synthesis tags resolve against the
    archive index. Returns (errors, unanchored_claims)."""
    errors: list[tuple[str, str]] = []
    unanchored: list[dict] = []
    if not artifacts:
        return errors, unanchored

    artifact_ids = {a.get("id") for a in artifacts if isinstance(a, dict)}
    # Verbatim haystack: every text payload the archive index actually holds.
    haystacks: list[str] = []
    for a in artifacts:
        if not isinstance(a, dict):
            continue
        for key in ("text", "quote", "transcript", "content"):
            v = a.get(key)
            if isinstance(v, str):
                haystacks.append(v)

    body = block_sections(lines, section_lines)
    if not body:
        return errors, unanchored

    # Group consecutive body lines into blocks.
    blocks: list[tuple[int, int, str]] = []  # (start, end, section)
    for lineno, section in body:
        if blocks and blocks[-1][1] == lineno - 1 and blocks[-1][2] == section:
            blocks[-1] = (blocks[-1][0], lineno, section)
        else:
            blocks.append((lineno, lineno, section))

    for start, end, section in blocks:
        block_lines = [(i, lines[i - 1]) for i in range(start, end + 1)]
        first = block_lines[0][1]
        if first.lstrip().startswith(BLOCKQUOTE_PREFIX):
            # Quote block: pointer line required, text verbatim in archive.
            pointer_ids = []
            quoted = []
            for i, text in block_lines:
                content = text.lstrip()[1:].lstrip()
                m = POINTER_RE.search(content)
                if m:
                    pointer_ids.append(m.group(1))
                elif content:
                    quoted.append(content)
            quote_text = " ".join(quoted).strip()
            if not pointer_ids:
                errors.append(
                    ("F4", f"line {start}: quote block lacks a source pointer "
                     "`> — [artifact: eng_<id>]`"))
                unanchored.append({"line": start, "section": section, "kind": "quote-no-pointer"})
            for pid in pointer_ids:
                if pid not in artifact_ids:
                    errors.append(
                        ("F5", f"line {start}: artifact id `{pid}` not found in archive/index.jsonl"))
            if quote_text:
                # Dates-block entries carry an inline exemplar:
                # `> Birthday — June 12: "my birthday's the twelfth of June."`
                # — the verbatim span is the double-quoted text when present.
                qm = re.search(r'"([^"]+)"', quote_text)
                verbatim_span = qm.group(1) if qm else quote_text
                if not any(verbatim_span in h for h in haystacks):
                    errors.append(
                        ("F4", f"line {start}: quoted text not found verbatim in the raw archive "
                         f"(quote: `{verbatim_span[:80]}{'…' if len(verbatim_span) > 80 else ''}`)"))
                    unanchored.append({"line": start, "section": section, "kind": "quote-unverbatim",
                                       "quote": verbatim_span})
        else:
            m = SYNTHESIS_TAG_RE.match(first.strip())
            if m:
                ids = [t.strip() for t in m.group(1).split(",") if t.strip()]
                if not ids:
                    errors.append(
                        ("F5", f"line {start}: synthesis tag names no artifact ids"))
                for aid in ids:
                    if not ARTIFACT_ID_RE.fullmatch(aid):
                        errors.append(
                            ("F5", f"line {start}: synthesis id `{aid}` is not an artifact id "
                             "(expected eng_<yyyymmdd>_<seq>)"))
                    elif aid not in artifact_ids:
                        errors.append(
                            ("F5", f"line {start}: synthesis id `{aid}` not found in archive/index.jsonl"))
            else:
                # Skip pure scaffold state: an empty section has no blocks at
                # all; reaching here means non-empty unanchored prose.
                errors.append(
                    ("F4", f"line {start}: unanchored claim in section `{section}` — "
                     "every non-heading, non-quote block must begin with "
                     "`[synthesis: eng_<id>, ...]` or be a `>` quote block ending "
                     "in `> — [artifact: eng_<id>]`"))
                unanchored.append({"line": start, "section": section, "kind": "unanchored-claim"})

        # (c) dates-block entries carry anchors.
        if section == "Dates":
            if not first.lstrip().startswith(BLOCKQUOTE_PREFIX) and not SYNTHESIS_TAG_RE.match(first.strip()):
                errors.append(
                    ("F4", f"line {start}: dates-block entry lacks an exemplar anchor "
                     "(quote block with pointer, or synthesis tag)"))
    return errors, unanchored


def lint(root: Path) -> tuple[list[tuple[str, str]], dict]:
    errors: list[tuple[str, str]] = []
    user_md = root / "USER.md"
    if not user_md.exists():
        return [("F1", "USER.md missing")], {
            "root": str(root), "pass": False, "errors": ["USER.md missing"],
            "counts": {"sections_found": 0, "quote_blocks": 0, "synthesis_blocks": 0,
                       "unanchored_claims": 0}, "unanchored": []}

    text = user_md.read_text()
    lines = text.splitlines()

    if lines[:1] != [TITLE]:
        errors.append(("F-structure", f"line 1: title must be exactly `{TITLE}`"))
    errors += check_provenance(lines)
    struct_errors, section_lines = check_structure(lines)
    errors += struct_errors

    artifacts, load_errors = load_archive(root)
    errors += load_errors

    claim_errors, unanchored = check_claims(lines, artifacts, section_lines)
    errors += claim_errors

    counts = {
        "sections_found": len([s for s in SECTIONS if s in section_lines]),
        "quote_blocks": sum(
            1 for start, end, _ in _blocks(lines, section_lines)
            if lines[start - 1].lstrip().startswith(BLOCKQUOTE_PREFIX)),
        "synthesis_blocks": sum(
            1 for start, _, _ in _blocks(lines, section_lines)
            if SYNTHESIS_TAG_RE.match(lines[start - 1].strip())),
        "unanchored_claims": len(unanchored),
    }
    summary = {
        "tool": "validate-mirror-soul.py",
        "root": str(root),
        "pass": not errors,
        "counts": counts,
        "unanchored": unanchored,
        "errors": [f"{code}: {msg}" for code, msg in errors],
    }
    return errors, summary


def _blocks(lines: list[str], section_lines: dict[str, int]) -> list[tuple[int, int, str]]:
    body = block_sections(lines, section_lines)
    blocks: list[tuple[int, int, str]] = []
    for lineno, section in body:
        if blocks and blocks[-1][1] == lineno - 1 and blocks[-1][2] == section:
            blocks[-1] = (blocks[-1][0], lineno, section)
        else:
            blocks.append((lineno, lineno, section))
    return blocks


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lint the Mirror-SOUL USER.md (claim contract, structure, anchors)."
    )
    parser.add_argument("--mode", choices=("lint", "check"), default="lint",
                        help="lint == check (alias)")
    parser.add_argument("--root", default=None,
                        help="profile root (default: ENGRAM_PROFILE_ROOT, then this file's parent)")
    args = parser.parse_args()

    root = resolve_root(args.root)
    errors, summary = lint(root)

    print(json.dumps(summary, indent=2))
    if errors:
        print("MIRROR-SOUL VALIDATION FAILED")
        for code, msg in errors:
            print(f"  {code}: {msg}")
        return 1
    print("MIRROR-SOUL VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
