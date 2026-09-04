#!/usr/bin/env python3
"""Validate Engram SKILL.md frontmatter conventions."""
import yaml, re, pathlib, sys

SKILL_ROOT = pathlib.Path(__file__).resolve().parents[1] / "skills" / "engram"
REQUIRED_FIELDS = {"name", "description", "version", "author", "license", "platforms", "metadata"}
MARKETING_WORDS = {"powerful", "comprehensive", "seamless", "advanced", "robust"}


def main() -> int:
    errors = []
    passed = []
    for skill_file in sorted(SKILL_ROOT.glob("*/SKILL.md")):
        content = skill_file.read_text()
        rel = skill_file.relative_to(SKILL_ROOT)
        if content.startswith("\ufeff"):
            errors.append((rel, "BOM present"))
        if not content.startswith("---"):
            errors.append((rel, "does not start with ---"))
            continue
        m = re.search(r"\n---\s*\n", content[3:])
        if not m:
            errors.append((rel, "missing closing ---"))
            continue
        fm_text = content[3 : 3 + m.start()]
        body = content[3 + m.end() :]
        try:
            fm = yaml.safe_load(fm_text)
        except Exception as e:
            errors.append((rel, f"YAML parse error: {e}"))
            continue
        if not isinstance(fm, dict):
            errors.append((rel, "frontmatter not a mapping"))
            continue
        missing = REQUIRED_FIELDS - set(fm.keys())
        if missing:
            errors.append((rel, f"missing fields: {missing}"))
            continue
        desc = fm.get("description", "")
        if not isinstance(desc, str):
            errors.append((rel, "description not a string"))
        else:
            if len(desc) > 60:
                errors.append((rel, f"description too long ({len(desc)} chars): {desc[:80]}"))
            if not desc.endswith("."):
                errors.append((rel, f"description does not end with period: {desc}"))
            for w in MARKETING_WORDS:
                if w in desc.lower():
                    errors.append((rel, f"marketing word in description: {w}"))
        meta = fm.get("metadata", {})
        hermes = meta.get("hermes", {}) if isinstance(meta, dict) else {}
        if "tags" not in hermes or "related_skills" not in hermes:
            errors.append((rel, "metadata.hermes missing tags or related_skills"))
        for rs in hermes.get("related_skills", []):
            if not (SKILL_ROOT / rs / "SKILL.md").exists():
                errors.append((rel, f"related_skill missing: {rs}"))
        if not body.strip():
            errors.append((rel, "empty body"))
        else:
            passed.append(rel)

    if errors:
        print("VALIDATION FAILED")
        for rel, msg in errors:
            print(f"  {rel}: {msg}")
        return 1
    print("VALIDATION PASSED")
    for p in passed:
        print(f"  ok: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
