---
name: engram-mirror-soul
description: "Maintain the subject's exemplar-anchored SOUL."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, mirror-soul, user-md, exemplar, consolidation]
    related_skills: [engram-gap-ledger, engram-interview]
---

# Engram Mirror-SOUL Skill

Maintain `USER.md` as a declared, tested, exemplar-anchored memory layer: a SOUL.md
*of the subject*. Every claim about the subject is either a verbatim quote from the raw
archive or an explicit synthesis that lists the supporting quotes and the inference drawn.

## When to Use

- During the consolidation cron: update `USER.md` from the archive and Hindsight peer model.
- During a mirror-SOUL-update cron: reconcile `USER.md` structure, lint the claim contract,
  and open gaps for unanchored claims.
- When the subject asks "what do you know about me?": answer from `USER.md`, citing
  anchors where appropriate.

Don't use for: raw archive capture (do that first), or interview probes (use the
interview skill).

## Section structure

`USER.md` follows this order. New entries go in the right section; sections may be empty
at first.

1. **Identity** — name, age, roles, self-labels the subject uses.
2. **Biography** — life events in chronological order where possible.
3. **Beliefs / worldview** — values, opinions, models of how the world works.
4. **Style register** — how the subject talks: cadence, recurring phrases, humor, formality.
5. **Relationships** — people, groups, organizations, and the subject's stance toward each.
6. **Goals** — stated objectives, plans, fears about failing them.
7. **Stories bank** — short, named anecdotes the subject tells or refers to.
8. **Interests** — hobbies, media, domains of curiosity.

Each section is a heading. Within a section, each entry is a single claim, not a
narrative paragraph.

## Claim contract

Every non-heading, non-quote block in `USER.md` must begin with one of:

1. **Verbatim quote block** — the block itself is the evidence, and ends with a source
   pointer:
   ```markdown
   > I always hated waiting in lines.
   > — [artifact: eng_20260827_001]
   ```
2. **Explicit synthesis block** — the block begins with the tag and lists the supporting
   quotes in the inference that follows:
   ```markdown
   [synthesis: eng_20260827_001, eng_20260827_003]
   Subject dislikes inefficiency and low autonomy; this generalizes from specific
   complaints about waiting and rigid scheduling.
   ```

Unquoted claims are forbidden. A generic claim with a loosely related quote is also
forbidden — either the quote supports the claim directly, or the block is a synthesis
that generalizes named quotes.

## Non-confrontation bound

Self-discrepancy records (e.g., actual/ought/ideal mismatches, feared selves, unlived
life) are captured in `USER.md` to inform the companion's model of the subject. They are
**never** surfaced back to the subject as confrontation, implied failure, or "you are not
living up to X." The companion can use the record to support the subject; the record does
not become a weapon.

## Ownership

- The Engram profile writes `USER.md` during consolidation and mirror-SOUL-update duties.
- Tooling lints the claim contract before the profile reports completion.
- No other profile edits `USER.md`.
- `USER.md` is not the raw archive; it is a derived artifact and can be rebuilt from the
  archive and Hindsight.

## Update triggers

Run a mirror-SOUL update after:

1. Every consolidation pass that touches a `USER.md` section.
2. Any redaction that removes an anchor (invalidate entries or reopen gaps).
3. A probe that provided direct answers to one or more gaps.
4. A scheduled weekly review cron that checks for drift and stale entries.

## Update procedure

1. Load `USER.md`, the archive index since the last update, and the open gaps.
2. For each new archive artifact:
   - Extract candidate claims.
   - Place each claim under the correct section.
   - Anchor it as a verbatim quote block with an artifact pointer.
3. For repeated patterns across multiple artifacts, write a synthesis block citing the
   exact artifact IDs.
4. Run claim-contract lint: every non-heading, non-quote block must begin with a
   `[synthesis: <artifact_ids>]` tag; continuation lines are covered by that tag.
5. Run anchor-verification lint: every quoted string must appear verbatim in the raw
   archive; every synthesis tag must resolve to real artifact IDs.
6. For any claim that fails lint, either fix it or open a gap.
7. Persist `USER.md`; verify by re-reading a sample of entries.

## Confidence marking

Synthesis blocks may include a confidence note:

- `confidence: hint` — one quote or weak signal.
- `confidence: pattern` — two or three consistent signals.
- `confidence: firm` — three or more strong, consistent signals.

Use confidence notes sparingly; they do not replace the synthesis tag.

## Pitfalls

- **Persona collapse.** Generic entries like "Subject is thoughtful" are useless unless
  anchored to specific words or actions.
- **Paraphrase drift.** "Subject said something like…" is not a verbatim quote. Copy the
  exact text.
- **Synthesis without quotes.** A synthesis block must name the artifacts it generalizes.
- **Editing the raw archive.** `USER.md` is derived; the archive is canonical. Never
  "correct" the archive to match `USER.md`.
- **Conflicting claims.** If two quotes contradict, keep both with their anchors and mark
  the conflict in a synthesis block; do not pick a winner silently.

## Verification

- [ ] `USER.md` has the eight sections in order; no section is missing a heading.
- [ ] Every non-heading, non-quote block begins with a `[synthesis: <artifact_ids>]` tag;
      continuation lines are covered by the block's tag.
- [ ] Every quoted string appears verbatim in the raw archive.
- [ ] Every synthesis tag resolves to real archive artifact IDs.
- [ ] No unanchored claims remain; any that cannot be fixed are gaps in `gaps.md`.
- [ ] Self-discrepancy records are present only to inform the companion's model, not to
      confront the subject.
- [ ] The file was written by the Engram profile during a declared consolidation or
      mirror-SOUL-update duty.
