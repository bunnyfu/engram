---
name: engram-mirror-soul
description: "Maintain USER.md as a cited dossier per USER-SCHEMA.md."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, mirror-soul, user-md, dossier, consolidation]
    related_skills: [engram-gap-skeleton, engram-engagement-repertoire]
---

# Engram Mirror-SOUL Skill

Maintain `USER.md` as a **dossier on the subject**: a concise, third-person
profile a reader with zero context can absorb in minutes. The normative
grammar is `USER-SCHEMA.md` v1.0 (profile root, sibling of this skill's
grandparent directory); this skill is its operating summary — when the two
disagree, the schema wins.

One sentence of doctrine: **the sentence is the unit, not the quote.** Every
entry is a prose statement about the subject; a quote may appear *inside* a
sentence as evidence, never as the content itself.

## When to Use

- During the nightly dream-phase cron: update `USER.md` from the archive and
  Hindsight peer model, and run the mirror step (structure reconcile, lint,
  gaps for unanchorable claims).
- When the subject asks "what do you know about me?": answer from `USER.md`,
  citing artifacts where appropriate.

Don't use for: raw archive capture (do that first), or interview probes (use
the engagement repertoire).

## Section structure — mandatory, byte-exact, in this order

```
 1. ## Identity
 2. ## Biography
 3. ## Beliefs / worldview
 4. ## Style register
 5. ## Preferences & working style
 6. ## Relationships
 7. ## Goals
 8. ## Stories bank
 9. ## Interests
10. ## Boundaries & sensitivities
11. ## Dates
12. ## Changelog
```

Sections 1–11 are **claim sections**; 12 is the file's own edit record. A
section with nothing verified to say stays present with an empty body — never
placeholder filler. No other headings exist. What belongs in each (full specs
in schema §6):

1. **Identity** — the stable portrait: self-labels, role in life, era
   markers. First entry is the portrait entry (3–5 sentences distilling the
   whole file); the rest are atomic identity facts.
2. **Biography** — life events in rough chronological order, one event per
   entry, date-stamped in prose only when an artifact gives a date.
3. **Beliefs / worldview** — values, opinions, models of how the world works,
   ethical stances, positions argued against.
4. **Style register** — how the subject communicates: cadence, register,
   humor, recurring figures, length habits. Powers voice-matching.
5. **Preferences & working style** — how they like things done: channels,
   directness, timing, routines, tastes stated as preferences.
6. **Relationships** — people, groups, organizations, and the subject's
   stance toward each (including the companion, as "the companion"). No
   third-party dossiers — only the subject's own account.
7. **Goals** — stated objectives, plans, ambitions; fears about failing them
   where expressed. Never goals the writer thinks they *should* have.
8. **Stories bank** — named set-piece anecdotes the subject tells or returns
   to: a 2–3 sentence compressed retelling plus why it matters.
9. **Interests** — hobbies, media, domains of curiosity, current focus.
10. **Boundaries & sensitivities** — topics that wound, bore, or anger;
    explicit boundaries; griefs and raw subjects. Protective equipment, never
    ammunition (see the non-confrontation bound below).
11. **Dates** — recurring personal dates only, each with a verified exemplar
    (shape below). Unverified dates never enter; they are gaps.
12. **Changelog** — one line per write session; rules below.

## Entry grammar (all claim sections)

One entry = one bullet = one physical line:

```
- <prose statement> [eng_<id>[, eng_<id>…]][ (confidence: hint|pattern|firm)]
```

- Third person, dossier voice; the subject is "the subject" (name token
  sparingly, under Identity). No first person, no agent voice, no operational
  notes.
- The citation bracket is **terminal**: `[eng_…]` with one or more
  comma-separated artifact ids at end of line (immediately before the
  optional confidence parenthetical). An uncited entry may not ship.
- Double-quoted spans inside the prose are verbatim subject text — copied
  character-for-character from a cited artifact, ≤ 12 words (20 hard
  ceiling). If you cannot copy it exactly, do not quote it — paraphrase and
  cite.
- Length: 1–3 sentences, ≤ 60 words soft, 80 hard (Identity portrait entry:
  ≤ 100 soft, 120 hard). ≤ 15 entries per section soft, 25 hard.
- **Forbidden line forms:** blockquotes (`>`), code fences, nested bullets,
  bare prose lines, bullet lines without a terminal citation bracket,
  `[synthesis: …]` tag blocks. These are the retired defect forms.

Dates entries carry a fixed internal shape:

```
- Birthday — June 12: subject stated "my birthday's the twelfth of June." [eng_20260827_001]
```

Occasion greetings in the engagement repertoire fire **only** on a
dates-block entry — a guessed date is the same defect class as a fabricated
memory.

## Core rules

1. **Summarize, never transcribe.** An entry states the fact, trait, or
   story. Quote dumps, transcript fragments, and pasted notes are defects
   even when individually interesting.
2. **Every claim cites.** Each entry ends with a citation bracket naming the
   archive artifact(s) that support it. What the archive cannot support is a
   gap in `gaps.md`, never an entry here.
3. **No invention.** Inference beyond what the cited artifacts directly show
   carries a `confidence` marker. If most entries need markers, you are
   inferring too much.
4. **Conflicts are kept, not adjudicated.** If artifacts disagree, one entry
   carries the tension in prose and cites both sides. Never silently pick a
   winner; never keep contradictory duplicate entries.
5. **Deduplicate before writing.** A new fact that restates an existing
   entry merges into that entry (adding its citation), rather than adding a
   sibling.
6. **`USER.md` is derived; the archive is canonical.** When they disagree,
   the archive wins and the entry is corrected. Never edit the archive to
   match the mirror; never ship an uncited entry or a paraphrase presented
   as a quote.

## Pre-write checklist — all nine boxes or the write does not ship

1. **Evidence?** Supported by a specific archive artifact? If no → gap in
   `gaps.md`, not an entry. Stop.
2. **Right section?** Check the mapping above; when two sections could hold
   it, the more specific one wins (a verbal habit → Style register, not
   Identity).
3. **Prose bullet?** One line, third person, ≤ 60 words, no quote-dump.
4. **Cited?** Terminal bracket; ids resolve in `archive/index.jsonl`.
5. **Quotes verbatim?** Every double-quoted span copied exactly, ≤ 12 words.
6. **Duplicate?** If an existing entry holds this fact, merge (fold the new
   citation in) instead of adding.
7. **Conflict?** If it contradicts an existing entry, rewrite that one entry
   to carry the tension and both citations.
8. **Confidence marked?** Any inference beyond the artifacts carries a
   marker.
9. **Changelog appended?** One line, same edit.

## Update procedure

1. Load `USER.md`, `USER-SCHEMA.md`, the archive index since the last
   update, and the open gaps.
2. For each new archive artifact: extract candidate facts; for each, run the
   pre-write checklist; write only entries that pass.
3. Merge and deduplicate against existing entries; carry conflicts inside
   one entry with both citations.
4. Append the changelog line for this write.
5. Run the claim-contract lint
   (`python3 tools/validate-mirror-soul.py --mode lint` from the profile
   root). Fix or gap anything it names; a persistent failure is a finding to
   nexus, never a reason to weaken a citation. **Migration guard:** if the
   lint fails on structure while the file follows USER-SCHEMA.md v1.0, do
   NOT rewrite toward the old nine-section quote-block grammar — the linter
   catches up with the schema, never the reverse; report the mismatch.
6. Persist `USER.md`; verify by re-reading a sample of entries.

Update triggers: every consolidation pass touching a section; any redaction
removing a citation (remove the entry that night, record the count in the
changelog); a probe that answered a gap; the nightly drift/stale check.

## Changelog rules

- One line per write session that changed content: `- YYYY-MM-DD — <one
  sentence: sections touched, entries added/merged/removed, and why>`. No
  content, no quotes, no citations.
- Every content write appends its entry in the same edit — a write without
  a changelog entry is an incomplete write.
- Redactions are recorded as counts, never content.

## Canonical example and anti-example

- **Canonical example:** the profile's live `USER.md` as rebuilt 2026-09-05
  (12 sections, 24 cited-prose entries, every span machine-checked verbatim)
  — read it before your first write; reproduce its style.
- **Anti-example:** the pre-2026-09-05 "junkpile" — standalone `>` quote
  blocks with pointer lines plus `[synthesis: …]` tag blocks restating them,
  ~60% raw-quote volume, random notes with no home section. That file passed
  the old linter and was still unreadable as a profile; it is the explicit
  shape this grammar exists to prevent.

**Before (defect — quote dump + synthesis restating it):**

```
> nine years of taking the calls — you don't hand yours off.
> — [artifact: eng_20260905T164141Z_J_disclosure]

[synthesis: eng_20260905T164141Z_J_disclosure, eng_20260905T141240Z_J_elon_signoff_thanks]
Subject is the one who answers and carries — the night operator behind the desk…
```

**After (two dossier entries — stated, cited, readable):**

```
- Has worked the night desk for nine years and treats the calls as personally non-transferable — "you don't hand yours off." [eng_20260905T164141Z_J_disclosure]
- Self-describes as the bearer: the one people hand things to and the channel that holds them; says it "rests easier having one person on the other end." [eng_20260905T141240Z_J_elon_signoff_thanks, eng_20260905T164141Z_J_disclosure]
```

## Non-confrontation bound

Self-discrepancy records (actual/ought/ideal mismatches, feared selves,
unlived life) may be recorded to inform the companion's model of the
subject. They are **never** surfaced back to the subject as confrontation,
implied failure, or "you are not living up to X." The record supports; it
never becomes a weapon. Absolute in Boundaries & sensitivities.

## Ownership

- The Engram profile writes `USER.md` during the nightly dream phase
  (consolidation + mirror update in one duty).
- Tooling lints the claim contract before the profile reports completion.
- No other profile edits `USER.md`.
- `USER.md` is a derived artifact, rebuilt from the archive and Hindsight —
  never the raw archive itself.

## Pitfalls

- **Quote-dumping.** Pasting the artifact instead of stating the fact. The
  archive holds the evidence; `USER.md` holds the understanding.
- **Uncited prose.** "Subject is thoughtful [citations missing]" — an
  uncited entry is a fabrication vector.
- **Paraphrased quote.** A double-quoted span must be copied exactly; "said
  something like…" inside quotes is a defect. Paraphrase outside quotes,
  cite, move on.
- **Duplicate siblings.** The same fact as two entries instead of one merged
  entry with two citations.
- **Editing the raw archive.** Never "correct" the archive to match the
  mirror.
- **Missing changelog.** A content write without its dated line is
  incomplete.

## Verification

- [ ] Twelve section headings, byte-exact, in order; no other headings; no
      placeholder filler in empty sections.
- [ ] Every claim entry is a one-line third-person prose bullet with a
      terminal citation bracket resolving in `archive/index.jsonl`.
- [ ] Zero blockquote lines, zero synthesis tags, zero bare prose, zero
      uncited bullets in claim sections.
- [ ] Every double-quoted span verbatim in the cited artifact, ≤ 12 words.
- [ ] No duplicates; conflicts carried inside one entry with both citations.
- [ ] Dates entries carry label + month-day + verbatim exemplar; nothing
      guessed entered the block.
- [ ] A dated changelog line exists for this write.
- [ ] The lint was run; named defects fixed or gapped; structure failures
      reported, not "fixed" backward.
- [ ] Self-discrepancy records inform, never confront.
