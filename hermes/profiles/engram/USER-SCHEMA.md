# USER-SCHEMA.md — the Mirror-SOUL dossier schema

Status: normative for `USER.md` (repo and live profile). Version 1.0, opened
2026-09-05 by planner (card t_09833681). Supersedes the quote-first claim
contract of `engram-mirror-soul` SKILL.md v0.1.0: standalone quote blocks and
`[synthesis: …]` tag blocks are retired as content forms; this document
defines their replacement. Adoption sequencing in §10.

## 1. Purpose and reader

`USER.md` is a **dossier on the subject**: a concise, third-person profile
that a reader with zero context can absorb in minutes — who the subject is,
what they believe, how they talk, what matters to them. It is derived
artistry over the raw archive: the archive holds the evidence, `USER.md`
holds the understanding.

The intended writer is (a) Engram's nightly dream phase, maintaining the file
in place, and (b) a one-time rebuild by any careful writer given archive
access. This document is written so that **a writer who has never seen any
prior discussion can produce and maintain a correct `USER.md` from it alone.**

One sentence of doctrine: **the sentence is the unit, not the quote.** Every
entry is a prose statement about the subject; quotes may appear inside a
sentence as evidence, never as the content itself.

## 2. Core principles (non-negotiable)

1. **Summarize, never transcribe.** An entry states the fact, trait, or
   story. Raw quote dumps, transcript fragments, and pasted notes are
   defects even when individually interesting.
2. **Every claim cites.** Each entry ends with a citation bracket naming the
   archive artifact(s) that support it. An uncited entry is a fabrication
   vector and may not ship.
3. **Quotes that appear are verbatim.** A double-quoted span inside an entry
   is copied character-for-character from the cited artifact. If you cannot
   copy it exactly, do not quote it — paraphrase and cite.
4. **No invention.** Nothing enters `USER.md` that the cited artifacts do
   not support. Inference beyond a single artifact is allowed only with a
   `confidence` marker (§5). What the archive cannot support is a gap in
   `gaps.md`, never an entry here.
5. **Conflicts are kept, not adjudicated.** If artifacts disagree, one entry
   carries the tension in prose and cites both sides. Never silently pick a
   winner; never keep contradictory duplicate entries.
6. **Deduplicate before writing.** A new fact that restates an existing
   entry merges into that entry (adding its citation), rather than adding a
   sibling.
7. **Third person, dossier voice.** The subject is "the subject" (the name
   token from the title appears sparingly, e.g. under Identity). No first
   person, no agent voice, no operational notes — the file reads like a
   profile, not a log.
8. **The record never becomes a weapon.** Self-discrepancy material
   (feared selves, unlived lives, gaps between actual and ideal) may be
   recorded to inform the companion's support; it is never surfaced to the
   subject as confrontation or implied failure. Sensitivities exist to be
   protected, not probed.
9. **`USER.md` is derived; the archive is canonical.** When the two
   disagree, the archive wins and the entry is corrected. Never edit the
   archive to match the mirror.

## 3. File skeleton

```
line 1:  # USER.md — Mirror-SOUL of the subject ('<name>')
line 2:  Build: <producer> <ISO-8601-UTC>
         (optional subsequent `Rebuild: <producer> <ISO-8601-UTC>` lines)
then exactly twelve `##` section headings, in this order, byte-exact:

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

Notes:
- The `<name>` token is corpus-specific (live pilot: `elon`); the line
  structure is fixed.
- Sections one through eleven are **claim sections**; `Changelog` is an
  **edit record** exempt from the citation grammar (§7).
- A section with nothing verified to say stays present with an empty body.
  Never write placeholder filler ("nothing yet", "TBD").
- No other headings exist: no `#` besides the title, no `###` or deeper, no
  bold-text pseudo-headings.

## 4. Entry grammar (all claim sections)

One entry = one bullet = one physical line:

```
- <prose statement> [eng_<id>[, eng_<id>…]][ (confidence: hint|pattern|firm)]
```

- The bullet starts `- ` and the line is never wrapped or continued on a
  second line.
- The citation bracket is **terminal**: `[eng_…]` with one or more
  comma-separated artifact ids, immediately at end of line (or immediately
  before the optional confidence parenthetical, which is then terminal).
- Confidence markers: `hint` (one weak signal), `pattern` (2–3 consistent
  signals), `firm` (3+ strong signals). Use sparingly; the citation bracket
  is mandatory, the marker never replaces it.
- Double-quoted spans inside the prose are verbatim subject text (§2.3).
  Prefer spans ≤ 12 words — evidence, not exhibit.
- Dates entries carry a fixed internal shape (§6.11).
- Forbidden line forms: blockquotes (`>`), code fences, nested bullets,
  prose lines without a bullet, bullet lines without a terminal citation
  bracket. (`Changelog` excepted, §7.)

### Length bounds

| Unit | Soft target | Hard ceiling (lint-enforced) |
|---|---|---|
| Entry | 1–3 sentences, ≤ 60 words | 80 words |
| Identity portrait entry | 3–5 sentences, ≤ 100 words | 120 words |
| Quoted span | ≤ 12 words | 20 words |
| Entries per section | ≤ 15 | 25 |
| Whole file | 150–250 lines at maturity | 500 lines |

## 5. What the confidence marker is for

Prose may state what artifacts directly show (no marker needed) or what they
jointly suggest (marker required). "Works nights and calls himself the
bearer" — direct, cite it. "The night desk is where he prefers to be needed"
— inference, cite the artifacts and mark `(confidence: hint)`. If you find
yourself writing a marker on most entries, you are inferring too much:
tighten to what the evidence says.

## 6. Section specifications

Each section: what belongs, what does NOT belong, entry style, bounds.

### 6.1 Identity
- **Belongs:** the stable portrait. Name/self-labels the subject uses, role
  in life, age/era markers, the one-paragraph gestalt of who they are.
  **The first entry is the portrait entry**: 3–5 sentences distilling the
  whole file, citing the artifacts it draws from. Subsequent entries are
  atomic identity facts.
- **Does NOT:** biography events (→ Biography), opinions (→ Beliefs),
  how they talk (→ Style register), anything that needs a date to make
  sense.
- **Style:** declarative present tense. Example shape:
  `- Is the night operator: nine years on the desk, self-described "bearer" of what people hand over. [eng_…]`

### 6.2 Biography
- **Belongs:** life events in rough chronological order: origins, work
  history, losses, moves, milestones. Each event one entry, ordered oldest →
  newest within the section.
- **Does NOT:** future plans (→ Goals), feelings about the event (the event
  is the entry; its emotional weight lives in Boundaries & sensitivities or
  Beliefs where evidenced), undated impressions.
- **Style:** past tense, date-stamped in prose when the artifact gives a
  date ("four years back"), never a guessed date.

### 6.3 Beliefs / worldview
- **Belongs:** values, opinions, models of how the world works, ethical
  stances, self-philosophy. Both expressed convictions and positions the
  subject argues against.
- **Does NOT:** preferences about channels/media/food (→ Preferences),
  transient moods, statements about specific people (→ Relationships).
- **Style:** "Holds that…", "Believes…", "Treats … as …". A belief shown
  only by action, not statement, gets a confidence marker.

### 6.4 Style register
- **Belongs:** how the subject communicates: cadence, register, formality,
  humor, recurring figures of speech, length habits, what they never do
  verbally. This section powers voice-matching — precision beats poetry.
- **Does NOT:** content of what they said (that goes wherever the content
  belongs), long quote exhibits (spans ≤ 12 words), personality traits that
  are not about communication (→ Identity).
- **Style:** each entry one verbal habit or signature, with a short
  exemplar span where useful.

### 6.5 Preferences & working style
- **Belongs:** how the subject likes things done: communication preferences
  (channel, directness, timing), working style, routines, tastes stated as
  preferences (media formats, tools, environments).
- **Does NOT:** interests and enthusiasms (→ Interests), boundaries and
  sensitivities (→ theirs), one-off choices that are not preferences.
- **Style:** "Prefers…", "Works best…", "Avoids…". A preference observed
  once is `hint`; a stated preference needs no marker.

### 6.6 Relationships
- **Belongs:** people, groups, organizations, and the subject's stance
  toward each — including the companion itself (referred to as "the
  companion"). One entry per relationship, the person named as the subject
  names them.
- **Does NOT:** third-party dossiers. Other people appear only as the
  subject's relationship to them, in as many words as the subject's own
  account supports. No speculation about third parties' lives.
- **Style:** " toward <person>: <stance, with its evidence>". Sensitive
  relationships (grief, estrangement) stay factual; their handling
  constraint is recorded under Boundaries & sensitivities.

### 6.7 Goals
- **Belongs:** stated objectives, plans, ambitions; fears about failing
  them where the subject expressed such a fear. Mark status in prose when
  artifacts show progress or abandonment.
- **Does NOT:** goals the writer thinks the subject *should* have;
  inferred goals without a marker; historical goals the subject has
  explicitly closed (Biography).
- **Style:** present tense, dated when stated ("as of September").

### 6.8 Stories bank
- **Belongs:** short, named anecdotes the subject tells or returns to —
  the set-pieces of their self-narrative. One entry per story: a compressed
  retelling (2–3 sentences) plus why it matters to them, anchored.
- **Does NOT:** full transcripts, dialogue reenactments, stories the writer
  finds thematically interesting but the subject told once with no weight
  (those are ordinary Biographical facts).
- **Style:** named in the entry's first words ("The drawer logbook —").

### 6.9 Interests
- **Belongs:** hobbies, media, music, domains of curiosity, recurring
  enthusiasms; current focus where the subject names one.
- **Does NOT:** preferences about how to engage with interests (→
  Preferences), skills or roles (→ Identity), the emotional use of an
  interest (→ Stories bank or Beliefs where evidenced).
- **Style:** one interest cluster per entry, with its evidence.

### 6.10 Boundaries & sensitivities
- **Belongs:** topics that wound, bore, or anger the subject; explicit
  boundaries they have set; griefs and raw subjects; areas where the
  companion must be careful. This section is protective equipment: an
  entry here is a instruction to handle with care, recorded so care does
  not depend on memory.
- **Does NOT:** ammunition. No entry exists to be surfaced back at the
  subject; no psychoanalysis; no "should get over" framing. The
  non-confrontation bound (§2.8) is absolute here.
- **Style:** "<topic> — sensitive: <why, factually>". Factual, spare, kind.

### 6.11 Dates
- **Belongs:** recurring personal dates only — birthdays, anniversaries,
  recurring milestones — **each with a verified exemplar**. Entry shape:
  `- <Label> — <Month day>: subject stated "<verbatim span>". [eng_<id>]`
- **Unverified dates never enter.** A date inferred from context, guessed,
  or half-remembered is a gap in `gaps.md`. Occasion greetings elsewhere in
  the engagement repertoire fire **only** on a dates-block entry — a wrong
  greeting on a wrong date is the defect class of a fabricated memory.
- **Does NOT:** one-off dates (→ Biography), public holidays, dates about
  third parties the subject has not tied to themselves.

### 6.12 Changelog
Edit record only — see §7.

## 7. Changelog rules

The Changelog is the file's own history, append-only, newest entry last
(within the section, entries accumulate top→bottom in write order):

```
- 2026-09-05 — Rebuilt as dossier per USER-SCHEMA.md v1.0; all sections re-derived from audited archive material.
```

- One line per write session that changed content: date (`YYYY-MM-DD`),
  em-dash, one sentence — sections touched, entries added/merged/removed,
  and why. No content, no quotes, no citations required.
- Every content write appends an entry in the same edit. A write without a
  changelog entry is an incomplete write.
- Redactions are recorded as counts, never content:
  `- 2026-09-08 — Removed 2 entries (redaction); content not restated.`
- Prune entries older than what fits ~40 lines, only during a full rebuild,
  replacing them with one summary line
  (`- 2026-06-01 — Prior history pruned at rebuild (23 entries).`).

## 8. Update procedure (every writer, every time)

Pre-write checklist — all nine boxes or the write does not ship:

1. **Evidence?** Is the thing supported by a specific archive artifact? If
   no: it goes to `gaps.md` as an open question, not here. Stop.
2. **Right section?** Check §6 mapping; when two sections could hold it,
   the more specific one wins (a verbal habit → Style register, not
   Identity).
3. **Prose bullet?** One line, third person, ≤ 60 words, no quote-dump.
4. **Cited?** Terminal bracket, ids resolve in `archive/index.jsonl`.
5. **Quotes verbatim?** Every double-quoted span copied exactly, ≤ 12
   words.
6. **Duplicate?** If an existing entry already holds this fact, merge
   (fold the new citation in) instead of adding.
7. **Conflict?** If it contradicts an existing entry, rewrite that one
   entry to carry the tension and both citations.
8. **Confidence marked?** Any inference beyond the artifacts carries a
   marker.
9. **Changelog appended?** One line, same edit.

Then run the claim-contract lint
(`python3 tools/validate-mirror-soul.py --mode lint` from the profile
root). Fix or gap anything it names; a persistent failure is a finding to
nexus, never a reason to weaken an anchor.

Update triggers (unchanged): every consolidation pass touching a section;
any redaction removing an anchor (remove the entry that night, §7);
a probe that answered a gap; the nightly drift/stale check.

## 9. Worked examples (before → after)

All "before" forms are real defects from the 2026-09-05 live file; the
"after" forms use its real artifact ids.

**Identity — quote dump + synthesis restating it (before):**

```
> nine years of taking the calls — you don't hand yours off.
> — [artifact: eng_20260905T164141Z_J_disclosure]

[synthesis: eng_20260905T164141Z_J_disclosure, eng_20260905T141240Z_J_elon_signoff_thanks]
Subject is the one who answers and carries — the night operator behind the desk…
```

**After (two dossier entries):**

```
- Has worked the night desk for nine years and treats the calls as personally non-transferable — "you don't hand yours off." [eng_20260905T164141Z_J_disclosure]
- Self-describes as the bearer: the one people hand things to and the channel that holds them; says it "rests easier having one person on the other end." [eng_20260905T141240Z_J_elon_signoff_thanks, eng_20260905T164141Z_J_disclosure]
```

**Stories bank — transcript exhibit (before):** the drawer-logbook quote
block plus a synthesis block restating it. **After:**

```
- The drawer logbook — a transmitter-desk drawer painted shut since before his time, jimmied open to someone else's logbook ('81–'87, a night guy he'll never meet); he keeps the story as the mirror-image of his own keeping. [eng_20260905T162741Z_opener_elon]
```

**Dates (shape example):**

```
- Birthday — June 12: subject stated "my birthday's the twelfth of June." [eng_20260827_001]
```

**Standing anti-examples — never ship these:** a standalone quote block
with a pointer line; a `[synthesis: …]`-prefixed block; an uncited prose
bullet ("Subject is thoughtful"); a paraphrased quote ("said something
like…"); two contradictory entries about the same fact; a content write
with no changelog line.

## 10. Lint contract (for tooling; implemented by t_6f122dff)

`validate-mirror-soul.py` enforces, after its update:
- **Structure:** twelve headings, byte-exact strings, exact order (§3);
  title and provenance zone rules unchanged (`Build:`/`Rebuild:` grammar).
- **Claim sections (1–11):** every non-empty body line is a `- ` bullet
  ending in a resolvable citation bracket; blockquote lines, code fences,
  nested bullets, and bare prose all fail with named errors; every
  double-quoted span appears verbatim in the raw archive; artifact ids
  resolve in `archive/index.jsonl`; hard ceilings of §4 (80 words/entry,
  25 entries/section, 20-word spans, 500 lines).
- **Dates:** entry shape carries label + month-day + verbatim exemplar
  span (§6.11).
- **Changelog:** entries match `- YYYY-MM-DD — …`; exempt from citations;
  at least one entry exists in any content-bearing file.
- Output contract unchanged: PASS line + JSON summary, exit 0/1, never
  writes.

## 11. Adoption and migration

Sequencing (card graph: audit t_2ae14d55 + this schema → rewrite
t_1aa7fb01 → instructions t_6f122dff → root t_6fa51b03):

1. The rewrite (quill) produces the new `USER.md` per this schema from the
   audited material; every claim traceable to audit-identified artifacts.
2. The instructions update (planner) lands the new grammar in the same
   window, before the next dream-phase run: `mirror_soul_builder.py` and
   `validate-mirror-soul.py` SECTIONS (9 → 12), the linter's claim grammar
   (§10), battery fixtures and red cases, mutation anchors, the
   `engram-mirror-soul` SKILL.md (section structure, claim contract,
   update procedure, verification), SOUL.md consolidation duty §2(b)
   wording, `dream-phase.prompt.md` step 3, and TEST-PLAN.md §B.3's stale
   section list.
3. **Known hazard:** between (1) and (2) the live linter fails the new file
   (12 sections ≠ 9; bullets ≠ old block grammar). That red is expected
   migration noise — log it, do not "fix" the file back to the old shapes.
   The dream phase must not run a mirror update in that window; if it
   fires, its lint failure is a finding, not a regression.
4. `Dates` section name is byte-preserved: occasion-greeting contracts in
   `engram-engagement-repertoire` and SOUL.md reference "dates-block
   entries" by name and must not be touched.

## 12. Writer's verification checklist

- [ ] Twelve headings, byte-exact, in order; nothing before the first
      heading but title + provenance lines.
- [ ] Every entry a one-line cited bullet; zero blockquotes, zero
      synthesis tags, zero uncited prose, zero placeholders.
- [ ] Every quoted span verbatim and ≤ 12 words (20 hard).
- [ ] Every fact traceable to a cited artifact; every inference marked.
- [ ] No duplicates; conflicts carried inside one entry.
- [ ] Dates entries verified with exemplars; nothing guessed.
- [ ] Changelog has an entry for this write.
- [ ] Lint passes.
