#!/usr/bin/env python3
"""Aggregate runner for the Engram profile test pipeline (t_de77cb60).

Runs every suite entry point identified by the test-pipeline audit
(TEST-PIPELINE-AUDIT.md, t_f26f4fa4) and the Mirror-SOUL spec
(2026-09-05-mirror-soul-usermd-builder-spec.md §G), enforcing each tool's
declared success contract:

  validate-skills.py              → exit 0, "VALIDATION PASSED"
  validate-cron-prompts.py        → exit 0, "CRON PROMPT VALIDATION PASSED"
  validate-mirror-soul.py         → exit 0, "MIRROR-SOUL VALIDATION PASSED"
                                    (run against a tempdir profile produced
                                    by the real scaffold — the repo tree
                                    carries no USER.md by design, §H.8;
                                    running this linter bare in-repo is a
                                    spec-legal F1 red, not a pipeline arm)
  validate-mirror-soul-battery.py → exit 0, "BATTERY PASSED (all checks)"
  validate-mirror-soul-mutations.py → exit 0, "MUTATIONS PASSED (all arms)"
                                    (red-when-broken: sabotaged machinery
                                    must turn the battery red)
  validate-trap-*.py              → exit 0, "PASSED" (T5/T6/T7/T8)

Standalone, stdlib-only, sibling conventions: prints
"ENGRAM TEST PIPELINE PASSED" and exits 0 on success; on failure prints
"ENGRAM TEST PIPELINE FAILED" plus one line per failing arm, exit 1.
Evidence is written to test-evidence/pipeline.json (gitignored).

Usage: python3 hermes/profiles/engram/tools/run-all-validations.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PROFILE = TOOLS.parent
REPO = PROFILE.parents[2]
EVIDENCE = PROFILE / "test-evidence"
PY = sys.executable

# Explicit arm list, not a glob: the bare validate-mirror-soul.py run is
# intentionally NOT an arm (in-repo it is F1 red by design — no USER.md is
# ever committed). The mirror-soul surface is covered by the battery (which
# scaffolds a tempdir profile first), the mutation harness, and the
# scaffold→lint pipeline arm below.
STATIC_ARMS = [
    ("validate-skills.py", ("VALIDATION PASSED",)),
    ("validate-cron-prompts.py", ("CRON PROMPT VALIDATION PASSED",)),
    ("validate-mirror-soul-battery.py", ("BATTERY PASSED (all checks)",)),
    ("validate-mirror-soul-mutations.py", ("MUTATIONS PASSED (all arms)",)),
    ("validate-trap-t5.py", ("PASSED",)),
    ("validate-trap-t7-cold-start.py", ("PASSED",)),
    ("validate-trap-t8-velocity.py", ("PASSED",)),
    ("validate-trap-cooling-resurrect.py", ("PASSED",)),
]


def run_pipeline_arm() -> tuple[bool, str]:
    """Spec §G6 at pipeline level: scaffold a fresh tempdir profile with the
    real builder, then lint it with the real linter. cwd-independent."""
    td = Path(tempfile.mkdtemp(prefix="engram-pipeline-scaffold-"))
    try:
        r1 = subprocess.run(
            [PY, str(TOOLS / "mirror_soul_builder.py"), "--root", str(td)],
            capture_output=True, text=True,
        )
        if r1.returncode != 0 or not (td / "USER.md").exists():
            return False, f"scaffold exit={r1.returncode}: {r1.stdout.strip()[:200]} {r1.stderr.strip()[:200]}"
        r2 = subprocess.run(
            [PY, str(TOOLS / "validate-mirror-soul.py"), "--root", str(td)],
            capture_output=True, text=True,
        )
        if r2.returncode != 0 or "MIRROR-SOUL VALIDATION PASSED" not in r2.stdout:
            return False, f"lint exit={r2.returncode}: {r2.stdout.strip()[:200]}"
        return True, "scaffold->lint PASSED (G6, tempdir-scoped)"
    finally:
        shutil.rmtree(td, ignore_errors=True)


def main() -> int:
    started = time.time()
    results = []
    failures = []
    for name, banners in STATIC_ARMS:
        script = TOOLS / name
        r = subprocess.run([PY, str(script)], capture_output=True, text=True, cwd=str(REPO))
        tail = (r.stdout or "").strip().splitlines()[-1:] or [""]
        ok = r.returncode == 0 and any(b in r.stdout for b in banners)
        results.append({"arm": name, "ok": ok, "exit": r.returncode,
                        "banner": tail[0][:120] if tail else ""})
        if ok:
            print(f"[PASS] {name}")
        else:
            failures.append(name)
            print(f"[FAIL] {name} (exit={r.returncode})")
            print(f"       expected one of: {banners}")
            print(f"       last line: {tail[0][:160] if tail else '(no stdout)'}")
            err_tail = (r.stderr or "").strip().splitlines()[-1:]
            if err_tail:
                print(f"       stderr: {err_tail[0][:160]}")

    # Pipeline arm: real builder → real linter against a tempdir profile.
    ok, detail = run_pipeline_arm()
    results.append({"arm": "pipeline scaffold->lint (tempdir)", "ok": ok,
                    "exit": 0 if ok else 1, "banner": detail[:120]})
    if ok:
        print(f"[PASS] pipeline scaffold->lint (tempdir)")
    else:
        failures.append("pipeline scaffold->lint (tempdir)")
        print(f"[FAIL] pipeline scaffold->lint (tempdir): {detail}")

    # Evidence file (gitignored, regenerated every run — f4c8017 convention).
    try:
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        (EVIDENCE / "pipeline.json").write_text(json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "python": sys.version.split()[0],
            "passed": not failures,
            "failures": failures,
            "arms": results,
        }, indent=2) + "\n")
    except OSError:
        pass  # evidence is best-effort; it never gates the verdict

    print()
    if failures:
        print(f"ENGRAM TEST PIPELINE FAILED: {len(failures)} arm(s) -> {failures}")
        return 1
    print(f"ENGRAM TEST PIPELINE PASSED ({len(results)} arms)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
