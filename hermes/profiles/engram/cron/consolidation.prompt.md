# Cron: Engram Consolidation

## Load these skills first

- `skill_view(name='engram-gap-skeleton')`
- `skill_view(name='engram-mirror-soul')`
- `skill_view(name='engram-engagement-engine')`
- `skill_view(name='fleet-governance')`

## Stop conditions (exit silently if any is true)

1. Raw archive path is unreadable or missing → log error.
2. No new artifacts since last consolidation timestamp.
3. A redaction conflict is detected → halt and escalate to nexus.

## Steps

1. Read the archive index and list artifacts newer than `last_consolidation_ts`.
2. For each new artifact:
   - Verify the raw artifact exists and its checksum matches the index.
   - Transcribe audio if needed, but only after raw audio is already archived.
3. Update the Hindsight peer model with experience and relationship entries derived from the
   artifacts.
4. Update `USER.md`:
   - Place new claims in the correct section.
   - Anchor every claim as a verbatim quote block or a `[synthesis: <artifact_ids>]` block.
5. Run claim-contract lint on `USER.md`.
6. For each unanchored or weakly anchored claim, open or merge a slot annotation in
   `gaps.md` per the gap-skeleton schema (`source: discovered:lint`).
7. Update `gaps.md` slot statuses per the gap-skeleton lifecycle: move slots toward
   `partial`/`closed` when the archive now supports them, anchoring the `exemplar`
   field to the closing artifact.
8. Run the dream-phase relationship-stage review (engine stage model; must
   complete before the daily contact window):
   - Scan window: every session since `last_stage_review_ts` (`null` = never
     reviewed → scan the full archive index).
   - Evaluate the evidence signals across the scanned arc: subject-initiation
     reciprocity, reply-depth reciprocity, unprompted self-disclosure, explicit
     warmth markers, ignored contacts, hostility/irritation markers.
   - Promote only with citable evidence (verbatim quote / artifact ref); demote
     fail-closed on one strong negative signal; `unknown` is not sticky — the
     first review with session data assigns a concrete warmth stage.
   - Record a transition via the engine tooling (`record_stage_transition`,
     evidence cited), then stamp the review (`record_stage_review`) so
     `last_stage_review_ts` advances — the engine writes `engagement_state.json`,
     this prompt never does.
9. Set `last_consolidation_ts = now` in the consolidation state file.
10. Persist all derived files; verify by re-reading samples.

## Output

- One cron run log line with timestamp, artifact count processed, gaps opened, gaps
  closed, stage-review outcome (`no-change` or the transition + `evidence_ref`), and
  lint result (`pass|N unanchored claims`).
- Updated `USER.md` and `gaps.md` only if new artifacts existed.
- A finding to nexus if the lint reports persistent unanchored claims or a redaction
  conflict.
