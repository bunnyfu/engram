# Cron: Engram Dream Phase

Nightly consolidation duty (absorbs the former `consolidation` and
`mirror-soul-update` crons, folded 2026-09-04). Runs out of session, while the
subject sleeps, and must complete before the morning session:
`engagement_state.json` and `gaps.md` are a static checkpoint that sessions read
at start and develop on top of as hot context — this phase is the only writer
that re-checkpoints them. Single-writer unchanged: the engine tooling writes
state, this prompt never does.

## Load these skills first

- `skill_view(name='engram-engagement-engine')`
- `skill_view(name='engram-gap-skeleton')`
- `skill_view(name='engram-mirror-soul')`
- `skill_view(name='fleet-governance')`

## Stop conditions (exit silently if any is true)

1. Raw archive path is unreadable or missing → log error.
2. `USER.md` is missing or unreadable → log error.
3. A redaction conflict is detected, or a redaction event was logged since the
   last run and has not been reconciled → halt and escalate to nexus.

## Steps

1. **Relationship-stage review** (engine stage model, promotion velocity):
   - Scan window: every session since `last_stage_review_ts` (`null` = never
     reviewed → scan the full archive index).
   - Evaluate the evidence signals across the scanned arc: subject-initiation
     reciprocity, reply-depth reciprocity, unprompted self-disclosure, explicit
     warmth markers, ignored contacts, hostility/irritation markers.
   - Promote only with citable evidence (verbatim quote / artifact ref); demote
     fail-closed on one strong negative signal; `unknown` is not sticky — the
     first review with session data assigns a concrete warmth stage.
   - At most ONE transition per review, both directions: promotions advance
     exactly one rung and are dwell-gated (→`friendly` requires ≥3 days at
     `neutral`; →`confidant` requires ≥14 days at `friendly`; the first review
     resolving `unknown` is exempt from dwell — though `confidant` always
     requires the friendly dwell below it). Demotions fail closed on one
     strong negative and fall at most to `unfriendly` in a single night —
     `hostile` is reachable only from `unfriendly`, never in one night. Whether
     the evidence justifies a transition within that budget is this phase's
     judgment; `record_stage_transition` enforces legality and rejects illegal
     moves with a reason — never force or clamp past a rejection; log it.
   - Record a legal transition via the engine tooling (`record_stage_transition`,
     evidence cited), then stamp the review (`record_stage_review`) so
     `last_stage_review_ts` advances — the engine writes
     `engagement_state.json`, this prompt never does.
2. **Gap-skeleton consolidation**: read the archive index and list artifacts
   newer than `last_consolidation_ts`. For each new artifact:
   - Verify the raw artifact exists and its checksum matches the index.
   - Transcribe audio if needed, but only after raw audio is already archived.
   - Tick off gaps the session evidence closes: move slots toward
     `partial`/`closed` per the gap-skeleton lifecycle, anchoring the `exemplar`
     field to the closing artifact.
   - Update the discovered overlay: open or merge slot annotations for new
     questions and unanchored claims (`source: discovered:lint` etc.), dedupe
     per the merge rule, run the ledger lint.
3. **USER.md mirror update**:
   - Update the Hindsight peer model with experience and relationship entries
     derived from the artifacts.
   - Place new claims in the correct section; anchor every claim as a verbatim
     quote block with a source pointer or a `[synthesis: <artifact_ids>]` block
     — exemplar-anchored claims only, no unanchored or paraphrased entries.
   - When personal dates surface in the scanned sessions (birthday mentions,
     anniversaries), record them in the `USER.md` dates block with exemplar
     anchors (date + label + verbatim-quote or artifact-ref anchor); unverified
     dates never enter the block.
   - Run the claim-contract lint; for each unanchored or weakly anchored claim,
     open or merge a slot annotation in `gaps.md` per the gap-skeleton schema
     (`source: discovered:lint`).
   - Re-anchor, remove, or gap claims whose anchors were redacted or no longer
     resolve; check stale entries against the configured staleness threshold.
4. Set `last_consolidation_ts = now` in the consolidation state file.
5. Persist all derived files; verify by re-reading samples.

Steps 2–3 are no-ops when no artifacts are newer than `last_consolidation_ts`
(`USER.md` and `gaps.md` stay untouched); the stage review in step 1 still runs
and stamps `last_stage_review_ts` — a review advances the window, transition or
not.

## Output

- One cron run log line with timestamp, artifact count processed, gaps opened,
  gaps closed, stage-review outcome (`no-change`, the transition +
  `evidence_ref`, or `rejected:<reason>`), and lint result
  (`pass|N unanchored claims`).
- Updated `USER.md` and `gaps.md` only if new artifacts existed.
- A finding to nexus if the lint reports persistent unanchored claims or a
  redaction conflict.
