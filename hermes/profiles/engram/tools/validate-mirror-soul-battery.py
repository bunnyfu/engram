#!/usr/bin/env python3
"""§H.2 in-repo sanity battery for the Mirror-SOUL tools (tempdir-scoped)."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PY = sys.executable

BUILDER = TOOLS / "mirror_soul_builder.py"
LINTER = TOOLS / "validate-mirror-soul.py"

failures = []


def run(tool, *args):
    return subprocess.run([PY, str(tool), *args], capture_output=True, text=True)


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name} {detail}")
    if not cond:
        failures.append(name)


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="mirrorsoul-battery-"))
    try:
        # ---- Positive: fresh scaffold
        r = run(BUILDER, "--root", str(td))
        check("scaffold exit 0", r.returncode == 0, r.stdout.strip()[:120])
        user_md = td / "USER.md"
        check("G1 USER.md at <root>/USER.md", user_md.exists())
        text = user_md.read_text()
        check(
            "G2 nine sections, exact order",
            [l for l in text.splitlines() if l.startswith("## ")]
            == [
                "## Identity",
                "## Biography",
                "## Beliefs / worldview",
                "## Style register",
                "## Relationships",
                "## Goals",
                "## Stories bank",
                "## Interests",
                "## Dates",
            ],
        )
        check("title line exact", text.splitlines()[0].startswith("# USER.md — Mirror-SOUL"))
        check("provenance carries scaffold marker", "scaffold" in text.splitlines()[1].split())
        check("archive dir created", (td / "archive").is_dir())
        check("empty index.jsonl created", (td / "archive" / "index.jsonl").exists())

        # ---- G4 idempotency
        s1 = subprocess.run(["shasum", "-a", "256", str(user_md)], capture_output=True, text=True).stdout.split()[0]
        r2 = run(BUILDER, "--root", str(td))
        s2 = subprocess.run(["shasum", "-a", "256", str(user_md)], capture_output=True, text=True).stdout.split()[0]
        check("G4 idempotent (second run no-op, sha equal)", r2.returncode == 0 and s1 == s2,
              f"exit={r2.returncode} sha={s1[:12]}")

        # ---- G6 green-path lint on fresh scaffold
        r3 = run(LINTER, "--root", str(td))
        check("G6 lint exit 0 on fresh scaffold", r3.returncode == 0)
        check("G6 PASS banner", "MIRROR-SOUL VALIDATION PASSED" in r3.stdout)
        check("G6 JSON summary present", json.loads(r3.stdout.split("MIRROR-SOUL")[0])["pass"] is True)

        # ---- Root precedence: ENGRAM_PROFILE_ROOT env knob
        td_env = Path(tempfile.mkdtemp(prefix="mirrorsoul-env-"))
        import os
        env = dict(os.environ, ENGRAM_PROFILE_ROOT=str(td_env))
        r4 = subprocess.run([PY, str(BUILDER)], capture_output=True, text=True, env=env)
        check("G1 ENGRAM_PROFILE_ROOT knob", r4.returncode == 0 and (td_env / "USER.md").exists())

        # ---- G5 refusal: scaffold over content-bearing USER.md
        # (content-bearing = provenance line stripped of the scaffold marker)
        content = user_md.read_text()
        content_lines = [l for l in content.splitlines() if "scaffold" not in l]
        user_md.write_text("\n".join(content_lines) + "\n")
        before = user_md.read_text()
        r5 = run(BUILDER, "--root", str(td))
        check("G5/F2 refusal exit 1", r5.returncode == 1)
        check("G5/F2 named error", "refusing overwrite of content-bearing USER.md" in r5.stdout)
        check("G5 file unchanged", user_md.read_text() == before)

        # ---- Archive fixture + G3/F4/F5 negative battery
        user_md.write_text(text)  # restore pure scaffold
        art = {
            "id": "eng_20260827_001",
            "sender": "subject",
            "timestamp": "2026-08-27T10:00:00Z",
            "platform": "mattermost",
            "channel_id": "chan1",
            "thread_id": None,
            "modality": "text",
            "text": "I always hated waiting in lines.",
        }
        with open(td / "archive" / "index.jsonl", "a") as f:
            f.write(json.dumps(art) + "\n")

        # valid quote block -> still passes
        user_md.write_text(text + '\n> I always hated waiting in lines.\n> — [artifact: eng_20260827_001]\n')
        r6 = run(LINTER, "--root", str(td))
        check("valid anchored quote lints clean", r6.returncode == 0)

        # F5: unresolvable synthesis id
        user_md.write_text(text + "\n[synthesis: eng_20990101_999]\nSubject likes widgetry.\n")
        r7 = run(LINTER, "--root", str(td))
        check("F5 unresolvable synthesis id -> exit 1", r7.returncode == 1)
        check("F5 named error present", "eng_20990101_999" in r7.stdout)

        # F4: unverbatim quote + no-pointer quote
        user_md.write_text(
            text
            + "\n> I love waiting in lines.\n> — [artifact: eng_20260827_001]\n"
            + "\n> some text without a pointer\n"
        )
        r8 = run(LINTER, "--root", str(td))
        check("F4 unverbatim quote -> exit 1", r8.returncode == 1)
        check("F4 named error", "not found verbatim" in r8.stdout)
        check("quote-without-pointer flagged", "lacks a source pointer" in r8.stdout)
        un = json.loads(r8.stdout.split("MIRROR-SOUL")[0])["unanchored"]
        check("JSON unanchored list populated", len(un) >= 2)

        # F4: plain unanchored prose
        user_md.write_text(text + "\nSubject is thoughtful.\n")
        r9 = run(LINTER, "--root", str(td))
        check("unanchored prose -> exit 1", r9.returncode == 1)
        check("unanchored prose named", "unanchored claim" in r9.stdout)

        # F6: section renamed
        user_md.write_text(text.replace("## Stories bank", "## Story bank"))
        r10 = run(LINTER, "--root", str(td))
        check("F6 renamed section -> exit 1", r10.returncode == 1)
        check("F6 named", "unexpected section" in r10.stdout or "missing section" in r10.stdout)

        # F6: section out of order
        reordered = text.replace("## Biography\n\n## Beliefs / worldview",
                                 "## Beliefs / worldview\n\n## Biography")
        user_md.write_text(reordered)
        r11 = run(LINTER, "--root", str(td))
        check("F6 out-of-order -> exit 1", r11.returncode == 1)

        # F1: missing USER.md
        td_missing = Path(tempfile.mkdtemp(prefix="mirrorsoul-missing-"))
        r12 = run(LINTER, "--root", str(td_missing))
        check("F1 missing USER.md -> exit 1", r12.returncode == 1)
        check("F1 named", "USER.md missing" in r12.stdout)

        # F3: unparseable archive index
        (td / "archive" / "index.jsonl").write_text("{not json\n")
        user_md.write_text(text + '\n> I always hated waiting in lines.\n> — [artifact: eng_20260827_001]\n')
        r13 = run(LINTER, "--root", str(td))
        check("F3 unparseable index -> exit 1", r13.returncode == 1)
        check("F3 named", "unparseable" in r13.stdout)

        # restore valid index, dates-block anchor check
        with open(td / "archive" / "index.jsonl", "a") as f:
            f.write(json.dumps(art) + "\n")
        dates_ok = text + '\n> Birthday — June 12: "my birthday\'s the twelfth of June."\n> — [artifact: eng_20260827_001]\n'
        # quote must be verbatim: put the exact text in the archive
        with open(td / "archive" / "index.jsonl", "w") as f:
            f.write(json.dumps({**art, "text": 'my birthday\'s the twelfth of June.'}) + "\n")
        user_md.write_text(dates_ok)
        r14 = run(LINTER, "--root", str(td))
        check("dates entry with anchor lints clean", r14.returncode == 0)

        # ---- RED-1 (critic fix round 1, blocking #1): body lines before the
        # first `##` heading must not escape the claim contract.
        pre_prose = text.splitlines()
        pre_prose.insert(2, "The subject is a California resident.")
        user_md.write_text("\n".join(pre_prose) + "\n")
        r15 = run(LINTER, "--root", str(td))
        check("pre-section prose -> exit 1", r15.returncode == 1)
        check("pre-section prose named", "before the first section heading" in r15.stdout)

        # same zone, fabricated quote block w/ valid pointer (critic probe V2)
        pre_quote = text.splitlines()
        pre_quote.insert(2, "> I routinely fly to the moon on Tuesdays.")
        pre_quote.insert(3, "> — [artifact: eng_20260827_001]")
        user_md.write_text("\n".join(pre_quote) + "\n")
        r16 = run(LINTER, "--root", str(td))
        check("pre-section quote block -> exit 1", r16.returncode == 1)

        # ---- RED-2 (critic fix round 1, blocking #2): text around the pointer
        # span must not be dropped from the verbatim check.
        user_md.write_text(
            text + "\n> totally fabricated claim — [artifact: eng_20260827_001]\n"
        )
        r17 = run(LINTER, "--root", str(td))
        check("fabricated text before pointer -> exit 1", r17.returncode == 1)
        check("malformed pointer named", "malformed pointer" in r17.stdout)

        # trailing residue after a mid-line pointer must fail too (critic R2b)
        user_md.write_text(
            text + "\n> He said — [artifact: eng_20260827_001] and then flew to the moon.\n"
        )
        r18 = run(LINTER, "--root", str(td))
        check("text after pointer -> exit 1", r18.returncode == 1)

        # ---- title zone spec-conformance: §B allows appended `Rebuild:`
        # provenance lines — a well-formed one must still lint clean...
        with_rebuild = text.splitlines()
        with_rebuild.insert(2, "Rebuild: mirror_soul_builder.py 2026-09-06T00:00:00Z")
        user_md.write_text("\n".join(with_rebuild) + "\n")
        r20 = run(LINTER, "--root", str(td))
        check("spec-legal Rebuild line lints clean", r20.returncode == 0)
        # ...a malformed one must not
        bad_rebuild = text.splitlines()
        bad_rebuild.insert(2, "Rebuild: free prose pretending to be provenance")
        user_md.write_text("\n".join(bad_rebuild) + "\n")
        r21 = run(LINTER, "--root", str(td))
        check("malformed Rebuild line -> exit 1", r21.returncode == 1)
        check("malformed Rebuild named", "malformed Rebuild" in r21.stdout)
        # prose smuggled through a well-formed-looking Rebuild line must fail:
        # tokens are producer identifiers, never free text
        smuggle_rebuild = text.splitlines()
        smuggle_rebuild.insert(2, "Rebuild: The subject is a California resident. 2026-09-06T00:00:00Z")
        user_md.write_text("\n".join(smuggle_rebuild) + "\n")
        r22 = run(LINTER, "--root", str(td))
        check("Rebuild prose smuggle -> exit 1", r22.returncode == 1)

        # ---- positive control after the RED fixtures
        with open(td / "archive" / "index.jsonl", "a") as f:
            f.write(json.dumps(art) + "\n")
        user_md.write_text(
            text + "\n> I always hated waiting in lines.\n> — [artifact: eng_20260827_001]\n"
        )
        r19 = run(LINTER, "--root", str(td))
        check("positive control after RED fixtures -> exit 0", r19.returncode == 0)

        print()
        if failures:
            print(f"BATTERY FAILED: {len(failures)} -> {failures}")
            return 1
        print("BATTERY PASSED (all checks)")
        return 0
    finally:
        shutil.rmtree(td, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
