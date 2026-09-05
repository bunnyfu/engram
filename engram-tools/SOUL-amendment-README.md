# SOUL.md amendment — card t_6f122dff (planner, 2026-09-05)

WHAT: retires the quote-first claim grammar from engram's SOUL.md and aligns
it with USER-SCHEMA.md v1.0 (cited dossier prose). Six sites: the mirror
ownership bullet, the derived-store bullet, consolidation duty 2(b), the
verbatim principle, the paraphrase hard boundary, and the verification
checklist line.

REGENERATED (t_902e3b12, 2026-09-05): this patch was rewritten against the
slimmed 14,995-char SOUL.md (main @ 03fdf66, card t_0b167f85) — the original
pre-slim patch no longer applied on main (RED at SOUL.md:28). Post-apply the
file is 14,972 chars, under the 15,000-char slim ceiling (net −23 chars).
The amendment text forbids the retired forms without re-naming them, so the
zero-hit grep below is literally satisfiable. Semantics are planner's
t_6f122dff v2.0.0 content in slim-card phrasing; the same content, condensed
to skill format, lives in engram-mirror-soul SKILL v2.0.0 (rebased onto the
slim bodies on wt/t_902e3b12).

WHY STAGED, NOT APPLIED: the Hermes protected-instruction-file guard
blocked the direct SOUL.md write during the headless run (approval timed
out; silence is not consent). Per constitution §5 instruction integrity,
an agent never patches instruction files it serves under — a human applies
this patch (or a worker with an approved session does).

APPLY (from the repo root or a worktree of engram on current main):

    git apply engram-tools/SOUL-amendment-t_6f122dff.patch
    # then commit and deploy to the live profile:
    cp hermes/profiles/engram/SOUL.md ~/.hermes/profiles/engram/SOUL.md

VERIFY after apply:

    grep -c "synthesis\|exemplar-anchored" hermes/profiles/engram/SOUL.md
    # must return 0 hits (grep exits 1) — the retired grammar is fully gone
    python3 hermes/profiles/engram/tools/validate-trap-t7-cold-start.py
    # static half must still pass (SOUL clauses intact) — VERIFIED PASS on
    # the amended body, t_902e3b12

ALREADY LANDED (no action needed): engram-mirror-soul SKILL v2.0.0 (rebased
onto the slimmed bodies, wt/t_902e3b12), dream-phase.prompt.md step 3,
engram-gap-skeleton lint references, TEST-PLAN.md §B.3 + DoD + v11 log entry.
