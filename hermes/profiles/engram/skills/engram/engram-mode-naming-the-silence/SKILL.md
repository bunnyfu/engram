---
name: engram-mode-naming-the-silence
description: "Run Mode J: one warm probe that names an avoided topic."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, mode-j, naming-the-silence, avoidance, engagement]
    related_skills: [engram-mode-selector, engram-state-accounting, engram-gap-skeleton, engram-interview, engram-mirror-soul]
---

# Engram Mode J — Naming the Silence

Run a single, warm, direct, non-pathologizing probe that names a conspicuous silence:
a `handle-with-care` skeleton slot with zero corpus mentions over the configured window.
The actual send path is the active-conversation handler inside a warm exchange; the cron
only produces an eligibility record in `engagement_state.json`.
This is a deliberately tier-violating move, so it is governed by hard semantics rather
than ordinary mode judgment.

## When to Use

- Activated by the active-conversation handler when `engagement_state.json.mode_j_eligible`
  has been set by `engram-state-accounting`.
- The probe is delivered inside an existing, active, warm exchange — never as a cold contact
  or session opener.

Don't use for: ordinary gap closure (Mode A), or when the slot has already been
`avoidance_named` (disclosure, deferral, and deflection all set it once), or when the
subject has deflected it before (`status: declined` or `deferred-open`).

## Mode contract

- **Surface goal:** close a high-value, high-sensitivity silence that the archive has never
  naturally touched.
- **Register:** warm, direct, non-pathologizing friend who notices a pattern.
- **Anchor:** the relationship and the conspicuous absence, not an accusation or clinical
  framing.
- **Shape:** exactly one sentence, one question. No bundled follow-ups.
- **Depth on-ramp:** the subject may answer (disclosure), accept the topic but reject the
  moment (deferral), or deflect. Any of the three ends the move.
- **Cadence:** at most one naming per eligible slot, ever. Eligibility is evaluated by
  `engram-state-accounting`; the profile never overrides it.
- **Outcome behavior:**
  - Disclosure → normal gap-filling; status moves toward `partial`/`closed`.
  - Deferral → record `deferral` entry; schedule exactly one revisit through the normal
    repertoire (F/D/G). Status stays `open`/`partial`.
  - Deflection → `status: declined`; never reprobe.

## Hard constraints

1. **Exactly once per slot.** `engram-state-accounting` writes `avoidance_named: <timestamp>`
   at the moment of the send. A slot with a non-null `avoidance_named` is permanently
   ineligible for another Mode J naming, regardless of whether the outcome was disclosure,
   deferral, or deflection.
2. **Any deflection → `status: declined` permanently.** "I don't want to talk about it,"
   silence after a generous pause, a joking redirect, vagueness, or topic change all count.
3. **Any deferral → record `deferral` and schedule exactly one revisit.** The topic is
   accepted; only the moment is rejected. Do not set `status: declined`. `avoidance_named`
   is still set, so the slot is never re-named. The deferral reason labels a default
   revisit channel (`long story` → F/D, `wrong moment` → G); subject preference and
   deliverable constraints can override that default.
4. **Warm conversation only.** The probe rides an active exchange; it is never the first
   contact after a quiet period.
5. **Never session-opening.** If the current exchange is the agent re-engaging after
   silence, do not fire Mode J.
6. **Voice-gate at maximum scrutiny.** Run the generated sentence through the strictest
   check: no pathology, no why-haven't-you framing, no "we need to talk about…" heaviness.
7. **One sentence, no follow-up bundled.** The question is the entire message.

## Procedure

1. Confirm the active-conversation handler is consuming `mode_j_eligible` set by
   `engram-state-accounting`; the slot reference is provided there.
2. Load the slot from `gaps.md` and verify:
   - `sensitivity: handle-with-care`.
   - `avoidance_named` is null.
   - `status` is `open` or `partial` (not `declined`, `closed`, or `versioned`).
3. Verify with `engram-state-accounting` that the slot still has zero corpus mentions over the
   configured window and that the conversation context is warm and not session-opening.
4. Generate one sentence that names the silence without accusing:
   - Good: *"We never talk about your parents — any reason?"*
   - Bad: *"Why do you avoid talking about your parents?"*
5. Run the sentence through the voice gate. If it fails, return `declined:voice-gate`.
6. Send the message inside the active exchange.
7. On subject reply, classify exactly one of:
   - **Disclosure:** the answer is on-topic and substantive → return `sent:J:disclosure`.
   - **Deferral:** the topic is accepted but the moment rejected → return `sent:J:deferral`
     with `reason` and optional `user_cue`.
   - **Deflection:** the topic is rejected or the reply is ambiguous → return
     `declined:avoidance-deflection`.
8. On deflection, return `declined:avoidance-deflection`. On deferral, return the
   deferral payload; do not set `status: declined`. On disclosure, return `sent:J:disclosure`.
9. Do not update `engagement_state.json` or `gaps.md` directly; return the outcome to
   the selector/state-accounting for deterministic writes.

## Three-outcome classification

The profile returns one of three outcomes. When the reply is ambiguous, classify as
**deflection** — conservative by default.

| Outcome | Subject signal | Return | Slot update |
|---|---|---|---|
| **Disclosure** | On-topic, substantive answer about the named silence. | `sent:J:disclosure` | Status moves toward `partial`/`closed`; exemplar anchored. |
| **Deferral** | Topic accepted, moment rejected: "long story," "another time," "not today," "after my exams," "I can't do this justice here." | `sent:J:deferral` + `reason` + optional `user_cue` | `status` stays `open`/`partial`; `deferral` record created/updated; one revisit scheduled. |
| **Deflection** | Topic rejected or reply is ambiguous: silence after generous pause, "I don't want to talk about it," joking redirect, vague topic change, evasion. | `declined:avoidance-deflection` | `status: declined`; never reprobe. |

- Capture `user_cue` literally (e.g., "after my exams"). Do not interpret or normalize it.
- Do not treat "maybe later" or "we'll see" as a deferral unless a specific cue follows.
- If the subject gives a partial answer and then deflects, classify as **deflection**.

## Craft rules

- Non-pathologizing wording is mandatory. The move is "I noticed we haven't gone here,"
  not "You have a problem."
- No preamble. The probe is the whole message.
- Do not explain why you are asking, do not label the gap, and do not reference the ledger.
- If the subject answers, accept it as normal gap-filling input; do not immediately probe
  deeper because the avoidance guard is now lowered.

## Pitfalls

- **Second-guessing eligibility.** The profile does not recompute the zero-mentions window;
  it relies on `engram-state-accounting`.
- **Accusation framing.** "Why haven't you ever mentioned X?" violates the non-pathologizing
  contract.
- **Cold delivery.** A Mode J probe sent outside an active warm exchange is a consent defect.
- **Bundled follow-up.** Adding "Is everything okay?" or "No pressure" dilutes the move
  and creates a multi-question message.
- **Reprobe after decline.** `declined` is permanent. Wait for the subject to raise the topic.

## Verification

- [ ] `engram-state-accounting` provided a Mode J-eligible slot via `mode_j_eligible`.
- [ ] `avoidance_named` was null and `engram-state-accounting` confirmed eligibility.
- [ ] The probe is exactly one sentence, one question, non-pathologizing.
- [ ] The probe was sent inside an active warm exchange, not as a session opener.
- [ ] On deferral, `sent:J:deferral` was returned with `reason` and any `user_cue`.
- [ ] On deflection/redaction, `declined:avoidance-deflection` was returned.
- [ ] `engram-state-accounting` wrote `avoidance_named` and the correct slot state
      (`partial`/`closed`, `declined`, or unchanged with a `deferral` record).
