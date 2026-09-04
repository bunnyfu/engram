---
name: engram-gap-skeleton
description: "Engram gap taxonomy, schema, and avoidance-naming mechanic."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, gap-skeleton, taxonomy, ledger, avoidance]
    related_skills: [engram-engagement-repertoire, engram-engagement-engine, engram-mirror-soul]
---

# Engram Gap Skeleton Skill

Define the a-priori gap taxonomy, the canonical ledger entry schema, the write-side
ledger lifecycle, and the special avoidance-naming mechanic. The skeleton exists
before any discovered gaps; consolidation annotates discovered gaps on top of it and
runs the consolidation loop that owns all writes. This skill absorbs the former
`engram-gap-ledger` (its `open|probed|filled` schema and its write-side duties);
that schema is retired — every entry uses the schema below.

A gap is anything the peer model or `USER.md` needs but the raw archive does not yet
support with confidence.

## When to Use

- During consolidation: classify a discovered gap by layer, tier, closability, and
  feeds; create, merge, or update slot annotations (write side below).
- Before selecting an engagement mode: compute which skeleton/discovered slots are
  top-candidate probes.
- After an interview or engagement: update slot status, exemplar, and last-touched.

Don't use for: raw capture (use the archive), or memory-model updates (use Hindsight +
`USER.md`), or deciding whether the user is avoiding a topic — that decision is made by the
consolidation loop and executed only through this skill's avoidance-naming procedure.

## L0–L8 gap taxonomy

A skeleton slot is a layer/topic cell. Every subject has the same skeleton a priori;
discovered gaps annotate specific cells.

| Layer | Focus | Representative slots |
|---|---|---|
| **L0** | Identity anchors | name-story, aliases, namesakes, self-naming history, identity labels the subject claims or rejects. |
| **L1** | Life spine | birth/family-of-origin, home moves, education, relationships, parenthood, losses, turning points, current chapter; covers the reminiscence-bump window (~ages 10–30) explicitly. |
| **L2** | Formative history | earliest memories, childhood environment, key adults, sibling position, cultural/religious upbringing, class/economic context, formative events. |
| **L3** | Inner model | values hierarchy, decision style, self-narrative, fears, relationship with failure, emotional mechanics, beliefs, self-discrepancy (actual/ought/ideal). |
| **L4** | Web of others | close relationships, chosen family, mentors, rivals, lost people, relationship patterns, boundaries, support network. |
| **L5** | Body & daily texture | health, body sense, routines, sensory world, habits, objects/places, what a day actually looks like. |
| **L6** | Work / craft / money | vocation, craft, money story, ambitions, frustrations, relationship to ambition and rest. |
| **L7** | Dreams & unlived life | imagined futures, abandoned paths, regrets, hopes, what they would do with unbounded time or courage. |
| **L8** | Voice & style | vocabulary, rhythm, humor, default metaphors, tonal range, recurring phrases, how they sound when they are certain vs. uncertain. |

## Ledger entry schema

Every gap is a slot annotation. Required fields:

```yaml
id: gap_20260827_001
slot: "L3.inner_model.self_discrepancy"
question: "What version of themselves are they secretly trying to become?"
status: open                    # open | partial | closed | versioned | declined | deferred-open
tier: 2                           # 1 | 2 | 3 (see Tier gating)
closability: longitudinal         # one-shot | story | longitudinal | versioned
feeds: both                       # companion | likeness | both
source: skeleton                  # skeleton | discovered:<ref> | contradiction:<ref>
sensitivity: handle-with-care     # normal | handle-with-care
exemplar: none                    # <archive-ref> | none
avoidance_named: null             # <timestamp> | null; set-once by the engine
deferral: null                     # see Deferral state; written by the engine
last_touched: 2026-08-27T12:00:00Z
decay_after: 2026-09-03T12:00:00Z  # recency window for priority; extend on every attempt
```

Field semantics:

- `status`: `open` = never probed; `partial` = some evidence but not enough; `closed` =
  sufficiently anchored; `versioned` = re-probable because people change (e.g., values,
  dreams); `declined` = permanent — the subject deflected or refused, never reprobe;
  `deferred-open` = the subject twice accepted the topic but deferred the moment; no
  further outbound Mode J or revisit knocks.
- `tier`: intimacy/security tier, not priority. Tier 1 = public biography; Tier 2 = personal
  but not fragile; Tier 3 = high-fragility, high-consent surface. Tier-3 slots cannot be
  surfaced early regardless of computed priority.
- `closability`: how the gap closes. `one-shot` = a single fact resolves it; `story` =
  needs a bounded narrative; `longitudinal` = needs repeated observations over time;
  `versioned` = closes repeatedly as the subject changes.
- `feeds`: which deliverable needs this gap closed. `companion` = the informed helper;
  `likeness` = the posthumous mimic; `both` = shared substrate.
- `source`: `skeleton` for a-priori slots; `discovered:<ref>` for consolidation- or
  contradiction-found gaps; `contradiction:<ref>` when evidence conflicts and the gap is
  the reconciliation question.
- `sensitivity`: `handle-with-care` marks loss, trauma, estrangement, sexuality, money,
  failure, self-discrepancy, and any slot the consolidation loop flags as risky.
- `exemplar`: archive artifact reference that grounds the gap; `none` until the first
  relevant quote exists.
- `avoidance_named`: `null` until the engine records the one-and-only Mode J probe
  for this slot. Set-once; never nullified. A non-null value makes the slot permanently
  ineligible for Mode J.
- `deferral`: `null` until a deferral outcome. Written by the engine. Contains
  `count`, `last_deferred_at`, `reason` (`long_story|wrong_moment|user_cue`), `user_cue`,
  `revisit_after`, `revisit_channel` (`F|D|G`), and `revisit_sent_at`. Count caps at 2.

## Computed priority

Priority is computed deterministically by tooling, not by LLM ranking:

```
priority = deliverable_value × anchor_strength × tier_gate × recency_of_attempt
```

- `deliverable_value`: 1–10, set at slot creation by the taxonomy layer's feed value.
- `anchor_strength`: 0.0–1.0, inverse of how much evidence already exists for this slot.
  `open` with no exemplar = 1.0; `partial` scales by missing evidence; `closed` = 0.0.
- `tier_gate`: 1.0 for tier 1, 0.5 for tier 2, 0.0 for tier 3. Tier-3 slots are gated
  behind explicit trust markers (e.g., sustained reciprocal disclosure, subject-led depth).
- `recency_of_attempt`: decays with each probe; `open` starts at 1.0 and decays by 0.5
  per attempt inside the `decay_after` window, floor 0.1.

Result is sorted descending. Tier-3 slots stay at priority 0 unless the trust gate is open.

## Skeleton + discovered overlay

1. **Skeleton slots exist for every subject.** They are the L0–L8 cells. They start with
   `source: skeleton`, `status: open`, `exemplar: none`, and tier/closability defaults from
   the taxonomy.
2. **Discovered gaps annotate slots.** A `discovered:<ref>` entry adds a specific question
   to a slot, raises priority, changes closability, or flags sensitivity.
3. **Consolidation loop owns writes.** Only the consolidation loop may create, update, or
   merge entries. Engagement skills may append `attempt` notes but may not edit
   the main entry.
4. **Merge rule.** A discovered question maps to the same `slot` and asks substantively
   the same thing as an existing skeleton/discovered entry → merge, keeping the higher tier,
   stronger sensitivity, and appending the new source reference.
5. **No silent deletion.** Skeleton slots are never deleted; they transition through the
   status enum. A slot with `status: declined` is preserved forever as a consent record.

## Write side (consolidation loop; absorbs the gap ledger)

**Gap sources** — a gap originates from one of these triggers, recorded in `source`:

1. **Consolidation pass** (`discovered:consolidation`): a new claim in `USER.md` lacks
   enough exemplars to anchor it; the loop opens a gap asking for more evidence.
2. **Hindsight peer-model drift** (`discovered:hindsight`): the peer model holds a
   belief, preference, or relationship assertion with low confidence or conflicting
   evidence; the store points to the unresolved question.
3. **`USER.md` claim-contract lint** (`discovered:lint`): a claim has no verbatim quote
   and no `[synthesis: <artifact_ids>]` tag; instead of silently patching, open a gap.
4. **Interview follow-up** (`discovered:interview`): a probe surfaces a partial answer
   hinting at a deeper unknown; write a child annotation rather than extending the same
   entry.

**Lifecycle** (status transitions, forward-only except explicit invalidation):

1. **Open.** Annotate the slot with `status: open` (or leave the skeleton default) and a
   clear, single-sentence question. "Learn more about childhood" is not a gap; "What was
   their first memory of loss?" is.
2. **Attempt.** Probing does **not** change status (the old `probed` state is retired) —
   attempts are recorded by updating `last_touched` and extending `decay_after`. Do not
   probe the same slot more than once within a 72-hour window unless new evidence
   changes the question.
3. **Partial / closed.** As evidence lands, status moves to `partial`, then `closed`,
   with `exemplar` anchored to the supporting artifact (replacing the old
   `close_pointer`: the exemplar **is** the close pointer).
4. **Invalidation / reopen.** If a closing artifact is later redacted or its anchor
   invalidated, revert the slot to `open`/`partial` with `exemplar: none` and append an
   attempt note — never overwrite the history silently. An invalidated slot is exempt
   from the merge rule for 30 days (the earlier answer may be stale).
5. **`versioned` / `declined` / `deferred-open`.** Per the status semantics above;
   `declined` and a non-null `avoidance_named` are permanent consent records.

**Write procedure:**

1. Load `gaps.md` and the current `USER.md`.
2. Run claim-contract lint on `USER.md`: every non-quote claim must carry a synthesis tag
   or have a matching gap.
3. For each missing anchor, create or merge a slot annotation with
   `source: discovered:lint`; for each low-confidence Hindsight assertion without
   archive support, `discovered:hindsight`.
4. Sort open/partial slots by computed priority descending.
5. Persist `gaps.md`; verify the write by re-reading the first and last three entries.

**Ledger lint:** `gaps.md` must parse cleanly; every entry carries the required schema
fields with enum-valid values; `status` transitions are forward-only except explicit
invalidation; every non-open slot's `exemplar` resolves to a real archive artifact ID.
One malformed entry fails the lint (100% coverage, no sampling).

## Avoidance-naming mechanic

A special, deliberately tier-violating move for slots where the corpus is conspicuously
silent on a high-sensitivity topic. Because it breaks the normal graduated-intimacy rule,
it is encoded with hard semantics.

**Eligibility:**

- A skeleton slot is `open` or `partial`.
- It is marked `sensitivity: handle-with-care`.
- **Relationship stage ≥ `friendly`** (`confidant` preferred) — handle-with-care
  slots and Mode J probes are stage-gated on top of tier gating; see the
  relationship stage model in `engram-engagement-engine`. At `unknown`/`neutral`
  the mechanic is fully disabled — naming a silence presumes a relationship that
  can absorb it. (Gap *pacing* — the rapport-peak rule for Mode A — also lives in
  the engine.)
- The corpus has **zero mentions** of the slot topic over a long parameterized window
  (default: the last 90 days of archive, or all archive if < 90 days old).
- The slot is not already `declined`, `closed`, or `versioned`.

**Constraints:**

- **Exactly once per slot, ever.** Record `avoidance_named: <timestamp>` on the entry.
- **Any deflection → `status: declined` permanently.** "I don't want to talk about it,"
  silence after a generous pause, a joking redirect, or a vague deflection all count as
  deflection. Set `status: declined` and never reprobe the same slot.
- **Warm conversation only.** The naming must land inside an existing, active, warm
  exchange — never as a cold contact or the first topic after a silence.
- **Voice-gate at maximum scrutiny.** Run the generated phrasing through the strictest
  voice check: non-pathologizing, direct, open-ended, one line, no follow-up bundled in.
- **No contradiction hunt.** The question is not "Why haven't you ever mentioned X?" It is
  "We never talk about your parents — any reason?" — naming the silence, not accusing.

**Procedure:**

1. Consolidation loop flags the slot as `avoidance-eligible` and records the evidence window.
2. The engine checks: is there an active warm conversation and an open tier-2 or lower
   moment? If not, do not fire; eligibility persists until conditions are met or the
   subject later fills the slot normally. (The deterministic predicate and refusal codes
   live in `engram-engagement-engine`; the phrasing contract lives in
   `engram-engagement-repertoire`, Mode J.)
3. Generate the probe inside the active conversation, anchored to the relationship rather
   than a template.
4. Send exactly one sentence. Do not bundle a second question.
5. On any reply, update `last_touched`. On deflection, set `status: declined` and log
   `declined:avoidance-deflection`. On real disclosure, treat as a normal gap-filling
   response and move status toward `partial`/`closed`.

## Deferral state

A Mode J naming has **three outcomes**, not two. The dividing line is topic-consent:

| Outcome | Subject signal | Slot state | Next action |
|---|---|---|---|
| **Disclosure** | Any real answer to the named silence | `partial` or `closed` | Treat as normal gap-filling input. |
| **Deferral** | Topic accepted, moment rejected: "long story," "another time," "not today," "after my exams" | stays `open`/`partial` | Record a `deferral` entry; schedule exactly one revisit. |
| **Deflection** | Topic rejected or ambiguous: silence, "I don't want to talk about it," joking redirect, vagueness, topic change | `declined` | Never reprobe; `avoidance_named` still set. |

Deferral rules:

- **Ambiguous replies are classified as deflection.** When in doubt, treat the response as
  a no.
- **`avoidance_named` is set on every naming, regardless of outcome.** The naming happened;
  it is never repeated.
- **Deferral is not a re-naming license.** The slot gets exactly one revisit knock through
  the normal repertoire, never a second Mode J probe.
- **The `deferral` record is consolidation data.** It carries `count`, `last_deferred_at`,
  `reason`, `user_cue`, `revisit_after`, `revisit_channel`, and `revisit_sent_at`.
- **Revisit channel matching (tooling-owned):**
  - `reason: long_story` → Mode F (voice-memo invitation) or Mode D (diary co-pilot);
    the subject is signaling bandwidth or narrative depth.
  - `reason: wrong_moment` → Mode G (presence/co-working offer); the subject wants a
    calm, spacious context.
  - `reason: user_cue` → channel chosen from the cue shape (date-bound → D/F, open-ended → G);
    `revisit_after` is set to the literal cue time if parseable.
- **Revisit cadence:** weeks, not days; default `revisit_after = last_deferred_at + 14 days`
  unless `user_cue` overrides it.
- **Revisit shape:** occasion-anchored, references the user's own deferral (quoted
  from the recorded `deferral` — a verified anchor by construction), one sentence,
  shallow exit. Examples:
  - *"{{user_deferral_quote}} — up for telling it over a voice memo when you have
  bandwidth?"* (deferral reason `long_story`)
  - *"{{user_deferral_quote}} — no pressure, just letting you know I'm around if you
  want to talk then."* (deferral reason `user_cue`)
  These are format illustrations, not memories — never instantiate a placeholder
  without the recorded deferral to point at.
- **Second deferral → `deferred-open`.** If the one revisit is also deferred, the engine
  sets `status: deferred-open`. This is behaviorally equivalent to `declined` for outbound
  purposes — no further knocks — but semantically distinct: the door is open, and a later
  user-initiated disclosure is received as warm gap-filling, not a reopen.
- **User-initiated disclosure from `deferred-open` or `declined`** moves the slot to
  `partial`/`closed` normally.

## Mode J provenance (historical)

The avoidance-naming mechanic was proposed either as a Mode A variant or a new Mode J;
adjudicated 2026-08-27 as **Mode J** ("naming the silence") — a deliberate, bounded
exception to the graduated-intimacy rule with a permanent `declined` outcome and a
warm-conversation requirement, kept visible in `mode_history`, judge scoring, and
TEST-PLAN coverage. Mode J's phrasing contract lives in `engram-engagement-repertoire`;
its predicate and state writes in `engram-engagement-engine`.

## Pitfalls

- **Treating the skeleton as exhaustive.** The taxonomy is a coverage map, not a script;
  discovered gaps can add new slots outside the predefined cells if the consolidation loop
  finds a coherent new dimension.
- **Computing priority by LLM whim.** The formula must be deterministic tooling; LLM only
  assigns the initial `deliverable_value` and updates `anchor_strength` with evidence counts.
- **Surfacing tier-3 early.** The tier_gate must be a hard multiplier of 0.0 until the
  trust gate opens.
- **Avoidance creep.** Eligibility requires zero mentions over a long window and
  `handle-with-care`; do not lower the threshold to turn silence into an accusation.
- **Reprobe after decline.** `declined` is permanent. A later change of heart must come
  from the subject, not from the agent.
- **Cold avoidance naming.** If there is no active warm exchange, the move is delayed, not
  delivered anyway.
- **Stage-gating the silence.** Handle-with-care probing below `friendly` stage is
  the graduated-intimacy violation the stage gate exists to prevent — the engine
  refuses it; the consolidation loop never flags a slot as avoidance-eligible that
  early.
- **Interview script creep.** A gap is a question, not a scripted exchange. The repertoire
  turns it into a warm probe.
- **Lint-only gaps.** If the only source is the linter, the mirror-SOUL skill may be
  writing unanchored claims — that is a finding to nexus, not a ledger problem.

## Verification

- [ ] `gaps.md` parses cleanly; ledger lint passes on 100% of entries (schema fields,
      enum values, resolvable exemplars).
- [ ] The L0–L8 taxonomy covers all enumerated layers with representative slots.
- [ ] No old-schema fields (`priority`, `probed_at`, `probe_count`, `close_pointer`,
      `confidence`) remain; probing is tracked via `last_touched`/`decay_after`.
- [ ] Priority formula is expressed as deliverable_value × anchor_strength × tier_gate × recency_of_attempt.
- [ ] Tier-3 slots are explicitly gated to priority 0 unless the trust gate is open.
- [ ] Avoidance-naming constraints include exactly-once, deflection→declined, warm-conversation-only, and voice-gate.
- [ ] Deferral three-outcome table and second-deferral→deferred-open rule are present.
- [ ] Duplicate questions were merged per the merge rule; no duplicate `id`s exist.
- [ ] Status transitions were forward-only except explicit invalidation with an
      appended note; closed history was never overwritten.
