#!/usr/bin/env python3
"""Red-when-broken harness for the Mirror-SOUL machinery (t_de77cb60).

Proves the pipeline battery actually exercises the machinery: each arm
sabotages ONE enforcement site in a working-tree copy of the tools, runs
validate-mirror-soul-battery.py (the sensor), and requires the battery to
turn RED. A battery that stays green under sabotage is not testing the
machinery.

Arms
  M1  title-zone bypass reverted (critic RED-1 regression): pre-section
      prose escapes the claim contract -> battery MUST fail.
  M2  Rebuild whitelist loosened (critic RED-2-class regression): a
      multi-token "producer" is accepted again -> prose smuggle -> battery
      MUST fail.
  M3  builder section list corrupted: the scaffold no longer emits the
      nine spec sections -> battery MUST fail.

Safety: sabotages apply only to the repo worktree copies beside this
script — NEVER to the live profile install. Each target is stashed to a
.mutbak sibling before mutation and restored in a finally block; startup
self-heals leftovers from a killed prior run; the run only passes if the
restored files are byte-identical (sha256) to the originals AND the
battery is green again (positive control).

Sibling conventions: standalone, stdlib-only; prints
"MUTATIONS PASSED (all arms)" + exit 0, or "MUTATIONS FAILED" + exit 1.
"""
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
LINTER = TOOLS / "validate-mirror-soul.py"
BUILDER = TOOLS / "mirror_soul_builder.py"
BATTERY = TOOLS / "validate-mirror-soul-battery.py"
PY = sys.executable

# Fail-closed append in check_title_zone (the RED-1 fix). Unique by message.
M1_ANCHOR = '''        errors.append((
            "F-structure",
            f"line {i}: content before the first section heading — the title "
            "zone holds only line 1 (title), line 2 (`Build:` provenance) and "
            "spec-legal `Rebuild:` provenance lines; every claim must live "
            "inside one of the nine sections",
        ))'''
M1_REPLACEMENT = '''        continue  # SABOTAGE M1: title-zone bypass reverted (pre-section prose escapes)'''

# Single-token producer grammar in the Rebuild whitelist (RED-2-class fix).
M2_ANCHOR = "if (len(parts) != 2"
M2_REPLACEMENT = "if (len(parts) < 2  # SABOTAGE M2: multi-token producer accepted again"

# Builder's nine-section list (first element; spec §B section 1).
M3_ANCHOR = 'SECTIONS = [\n    "Identity",'
M3_REPLACEMENT = 'SECTIONS = [\n    "IdentityX",  # SABOTAGE M3: section list corrupted'

failures = []


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def restore(stash: Path, target: Path) -> None:
    if stash.exists():
        shutil.copyfile(stash, target)
        stash.unlink()


def self_heal() -> None:
    """Restore any target left sabotaged by a killed prior run."""
    restore(TOOLS / ".validate-mirror-soul.py.mutbak", LINTER)
    restore(TOOLS / ".mirror_soul_builder.py.mutbak", BUILDER)


def run_battery() -> subprocess.CompletedProcess:
    return subprocess.run([PY, str(BATTERY)], capture_output=True, text=True, cwd=str(TOOLS))


def battery_red(r: subprocess.CompletedProcess) -> bool:
    return r.returncode != 0 and "BATTERY FAILED" in r.stdout


def mutate(target: Path, anchor: str, replacement: str, label: str) -> bool:
    text = target.read_text()
    n = text.count(anchor)
    if n != 1:
        print(f"[FAIL] {label}: anchor not unique in {target.name} (count={n}) — harness bug, refusing to mutate")
        failures.append(label)
        return False
    stash = TOOLS / f".{target.name}.mutbak"
    shutil.copyfile(target, stash)
    try:
        target.write_text(text.replace(anchor, replacement))
        r = run_battery()
        if battery_red(r):
            n_fail = r.stdout.count("[FAIL]")
            print(f"[PASS] {label}: battery RED ({n_fail} failing checks) — machinery is exercised")
        else:
            print(f"[FAIL] {label}: battery stayed GREEN (exit={r.returncode}) — sabotage not caught")
            failures.append(label)
    finally:
        restore(stash, target)
    return True


def main() -> int:
    self_heal()
    if not BATTERY.exists() or not LINTER.exists() or not BUILDER.exists():
        print("MUTATIONS FAILED: required tools missing beside this script")
        return 1
    orig = {LINTER: sha(LINTER), BUILDER: sha(BUILDER)}

    mutate(LINTER, M1_ANCHOR, M1_REPLACEMENT,
           "M1 linter title-zone bypass reverted")
    mutate(LINTER, M2_ANCHOR, M2_REPLACEMENT,
           "M2 linter Rebuild whitelist loosened")
    mutate(BUILDER, M3_ANCHOR, M3_REPLACEMENT,
           "M3 builder section list corrupted")

    # Positive control + byte-identical restore assertion.
    r = run_battery()
    restored_ok = all(sha(p) == s for p, s in orig.items())
    if restored_ok and r.returncode == 0 and "BATTERY PASSED" in r.stdout:
        print("[PASS] restore: linter+builder byte-identical, battery GREEN again")
    else:
        print(f"[FAIL] restore/positive control (shas_ok={restored_ok}, battery exit={r.returncode})")
        failures.append("restore/positive control")

    print()
    if failures:
        print(f"MUTATIONS FAILED: {len(failures)} arm(s) -> {failures}")
        return 1
    print("MUTATIONS PASSED (all arms)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
