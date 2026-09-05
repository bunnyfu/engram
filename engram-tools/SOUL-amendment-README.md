# SOUL.md amendment — card t_6f122dff (planner, 2026-09-05)

WHAT: retires the quote-first claim grammar from engram's SOUL.md and aligns
it with USER-SCHEMA.md v1.0 (cited dossier prose). Six sites: the mirror
ownership bullet, the derived-store bullet, consolidation duty 2(b), the
verbatim principle, the paraphrase hard boundary, and the verification
checklist line.

WHY STAGED, NOT APPLIED: the Hermes protected-instruction-file guard
blocked the direct SOUL.md write during this headless run (approval timed
out; silence is not consent). Per constitution §5 instruction integrity,
an agent never patches instruction files it serves under — a human applies
this patch (or a worker with an approved session does).

APPLY (from the repo root or a worktree of engram that has the
t_6f122dff changes merged):

    git apply engram-tools/SOUL-amendment-t_6f122dff.patch
    # then commit and deploy to the live profile:
    cp hermes/profiles/engram/SOUL.md ~/.hermes/profiles/engram/SOUL.md

VERIFY after apply:

    grep -n "synthesis\|exemplar-anchored" hermes/profiles/engram/SOUL.md
    # must return ZERO hits (the retired grammar is fully gone)
    python3 hermes/profiles/engram/tools/validate-trap-t7-cold-start.py
    # static half must still pass (SOUL clauses intact)

ALREADY LANDED in this branch (no action needed): engram-mirror-soul
SKILL.md v2.0.0, dream-phase.prompt.md step 3, engram-gap-skeleton lint
references, TEST-PLAN.md §B.3 + DoD + v11 log entry.
