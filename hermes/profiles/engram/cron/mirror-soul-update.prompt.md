# Cron: Engram Mirror-SOUL Update

## Load these skills first

- `skill_view(name='engram-mirror-soul')`
- `skill_view(name='engram-gap-skeleton')`
- `skill_view(name='fleet-governance')`

## Stop conditions (exit silently if any is true)

1. `USER.md` is missing or unreadable.
2. Raw archive index is missing.
3. A redaction event was logged since the last update and has not been reconciled →
   halt and escalate to nexus.

## Steps

1. Load `USER.md` and validate its section structure.
2. Run the claim-contract lint:
   - Every non-heading, non-quote line must carry `[synthesis: <artifact_ids>]`.
   - Every quote must exist verbatim in the raw archive.
   - Every synthesis tag must resolve to real artifact IDs.
3. For each lint failure, decide:
   - If the claim can be re-anchored with an existing artifact → rewrite it.
   - If the original anchor was redacted → remove the claim or mark it as a gap.
   - If no anchor exists → remove the claim and open a gap.
4. Check for stale entries (claims untouched since the configured staleness threshold);
   verify their anchors are still valid. Open gaps for anchors that no longer resolve.
5. Reconcile with `gaps.md`: every removed or demoted claim must produce a slot
   annotation per the gap-skeleton schema with `source: discovered:lint`.
6. Persist `USER.md` and `gaps.md`; verify by re-reading samples.

## Output

- One cron run log line with timestamp, lint result (`pass|N failures`), entries rewritten,
  entries removed, and gaps opened.
- A finding to nexus if lint failures persist after the update or if a redaction event
  remains unreconciled.
