#!/usr/bin/env python3
"""Validate Engram cron prompt references point at existing skills."""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "engram"
CRON_DIR = ROOT / "cron"

# The folded cron set (2026-09-04): exactly two prompts.
EXPECTED_PROMPTS = {"dream-phase.prompt.md", "proactive-engagement.prompt.md"}


def main() -> int:
    skill_names = {p.parent.name for p in SKILL_ROOT.glob("*/SKILL.md")}
    # Cross-repo fleet skills that may be referenced from cron prompts.
    skill_names |= {"fleet-governance", "fleet-collaboration"}
    errors = []
    passed = []
    found = {p.name for p in CRON_DIR.glob("*.prompt.md")}
    missing = EXPECTED_PROMPTS - found
    extra = found - EXPECTED_PROMPTS
    if missing:
        errors.append((", ".join(sorted(missing)), "expected prompt missing from cron/ (folded set: dream-phase + proactive-engagement)"))
    if extra:
        errors.append((", ".join(sorted(extra)), "unexpected prompt in cron/ (folded set is exactly two prompts)"))
    for prompt_file in sorted(CRON_DIR.glob("*.prompt.md")):
        content = prompt_file.read_text()
        if not content.strip():
            errors.append((prompt_file.name, "empty file"))
            continue
        if not content.lstrip().startswith("# Cron:"):
            errors.append((prompt_file.name, "missing '# Cron:' header"))
        refs = set(re.findall(r"skill_view\(name='([^']+)'\)", content))
        missing = refs - skill_names
        if missing:
            errors.append((prompt_file.name, f"missing referenced skills: {sorted(missing)}"))
        else:
            passed.append(prompt_file.name)
    if errors:
        print("CRON PROMPT VALIDATION FAILED")
        for name, msg in errors:
            print(f"  {name}: {msg}")
        return 1
    print("CRON PROMPT VALIDATION PASSED")
    for p in passed:
        print(f"  ok: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
