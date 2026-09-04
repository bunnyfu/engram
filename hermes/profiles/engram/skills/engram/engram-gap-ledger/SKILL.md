---
name: engram-gap-ledger
description: "Maintain the Engram gap ledger of open subject questions."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, gap-ledger, memory, consolidation, interview]
    related_skills: [engram-interview, engram-mirror-soul]
---

# Engram Gap Ledger Skill

Maintain the machine-readable `gaps.md` ledger of open questions about the subject.
A gap is anything the peer model or `USER.md` needs but the raw archive does not yet
support with confidence.

## When to Use

- During or after a consolidation pass: write newly discovered gaps.
- Before an interview cron fire: read the ledger to select the highest-value probe target.
- After an interview or engagement: update gap status based on what was learned.

Don't use for: capturing raw artifacts (use the archive), or for memory-model updates
(use Hindsight + `USER.md`).

## Gap sources

A gap originates from one of these triggers:

1. **Consolidation pass.** A new claim in `USER.md` lacks enough exemplars to anchor it;
   the consolidation loop opens a gap asking for more evidence.
2. **Hindsight peer-model drift.** The peer model contains a belief, preference, or
   relationship assertion with low confidence or conflicting evidence; the store points to
   the unresolved question.
3. **USER.md claim-contract lint.** A claim has no verbatim quote and no
   `[synthesis: <artifact_ids>]` tag; instead of silently patching, open a gap.
4. **Interview follow-up.** A probe surfaces a partial answer that hints at a deeper
   unknown; write a child gap rather than extending the same entry.

## Gap schema

Each entry is a YAML front-matter block or a JSON object; the rest of the file is
append-only history. Required fields:

```yaml
id: gap_20260827_001           # stable, sortable, never reused after close
question: "What first made them distrust authority?"
priority: high                 # high | medium | low
created_at: 2026-08-27T12:00:00Z
status: open                   # open | probed | filled
probed_at: null                # ISO timestamp; set each time a probe is sent
probe_count: 0                 # increments every time a probe is issued for this gap
source_pointer:                # why this gap exists
  type: consolidation          # consolidation | hindsight | lint | interview
  artifact_ids: [eng_001, eng_002]
  note: "USER.md claims distrust of authority but only one weak exemplar"
close_pointer: null            # artifact_id that filled the gap; null until status=filled
closed_at: null
confidence: tentative          # tentative | likely | confirmed; set on close
```

## Lifecycle

1. **Open.** Write the entry with `status: open` and a clear, single-sentence question.
2. **Probed.** When the interview cron selects this gap, set `status: probed`, update
   `probed_at`, and increment `probe_count`. Do not probe the same gap more than once
   within a 72-hour window unless new evidence changes the question.
3. **Filled.** When the archive holds a direct answer, set `status: filled`, record the
   `close_pointer` (artifact ID), set `closed_at`, and update `confidence`.
4. **Reopen.** If the closing artifact is later redacted or the anchor is invalidated,
   reopen the gap with a new `id`; never overwrite a closed entry's history.

## Dedupe rule

Two gaps are duplicates if they ask substantively the same question about the same
aspect of the subject. Before adding a new gap:

1. Compare the question string and the `source_pointer` to every open or probed entry.
2. If a duplicate exists, merge: keep the higher priority, append the new source pointers
   and artifact IDs, and do not create a new `id`.
3. A filled gap that is reopened is exempt from the duplicate check for 30 days; the
   earlier answer may be stale.

## Procedure

1. Load `gaps.md` and the current `USER.md`.
2. Run claim-contract lint on `USER.md`: every non-quote claim must carry a synthesis tag
   or have a matching gap.
3. For each missing anchor, create or merge a gap with `type: lint`.
4. For each low-confidence Hindsight assertion without archive support, create or merge a
   gap with `type: hindsight`.
5. Sort open/probed gaps by `priority` descending, then `probe_count` ascending, then
   `created_at` ascending.
6. Persist `gaps.md`; verify the write by re-reading the first and last three entries.

## Pitfalls

- **Vague questions.** "Learn more about childhood" is not a gap. "What was their first
  memory of loss?" is.
- **Interview script creep.** A gap is a question, not a scripted exchange. The interview
  skill turns it into a warm probe.
- **Overwriting history.** Never delete or edit a closed gap; append a reopen note with a
  new `id`.
- **Lint-only gaps.** If the only source is the linter, the mirror-SOUL skill may be
  writing unanchored claims — that is a finding to nexus, not a ledger problem.

## Verification

- [ ] `gaps.md` parses cleanly as YAML/JSON.
- [ ] Every open/probed gap has non-empty `id`, `question`, `priority`, `created_at`, and
      `source_pointer`.
- [ ] No duplicate `id`s exist; duplicate questions were merged.
- [ ] `status` transitions are forward-only (`open` → `probed` → `filled`) except via an
      explicit reopen note with a new `id`.
- [ ] Every closed gap has a `close_pointer` resolving to a real archive artifact ID.
