# Cron: Engram Consolidation

## Load these skills first

- `skill_view(name='engram-gap-skeleton')`
- `skill_view(name='engram-mirror-soul')`
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
8. Set `last_consolidation_ts = now` in the consolidation state file.
9. Persist all derived files; verify by re-reading samples.

## Output

- One cron run log line with timestamp, artifact count processed, gaps opened, gaps
  closed, and lint result (`pass|N unanchored claims`).
- Updated `USER.md` and `gaps.md` only if new artifacts existed.
- A finding to nexus if the lint reports persistent unanchored claims or a redaction
  conflict.
