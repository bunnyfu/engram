---
name: engram-engagement-engine
description: "Own engagement state, caps, mode selection, and wind-down."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, engagement, engine, state, selector, accounting]
    related_skills: [engram-engagement-repertoire, engram-gap-skeleton, engram-mirror-soul]
---

# Engram Engagement Engine Skill

The deterministic control layer for agent-initiated engagement: the canonical
`engagement_state.json` schema, pre-wake accounting, cap checks, mode
selection, the relationship stage model with dream-phase review, the session
exchange budget (wind-down + cooling lock), session conversation routing, and
the Mode J eligibility predicate with deferral/revisit processing. Tooling
owns all of it; the profile drafts and sends per
`engram-engagement-repertoire` and never writes state.

## When to Use

- At the start of every engagement cron fire (proactive engagement or
  conversation handling) — before any cap check or mode selection.
- Mode J eligibility scans and Mode J outcome disposition.
- Session replies needing phase narrowing (`open` / `nudging` / `closing`).
- Nightly dream-phase reviews deriving a relationship-stage transition.

Don't use for: drafting, phrasing, or per-mode voice contracts
(`engram-engagement-repertoire`); gap taxonomy and slot semantics
(`engram-gap-skeleton`); `USER.md` maintenance (`engram-mirror-soul`).

## `engagement_state.json` — canonical schema (single source)

Supersedes every earlier schema (former selector, state-accounting, and
interview skill copies). Reference implementation: `tools/engram_state.py`.

```json
{
  "last_contact_ts": "2026-08-27T20:12:00Z",
  "last_mode": "A",
  "mode_history": ["B", "C", "A"],
  "mode_last_sent": {
    "A": "2026-08-27T20:12:00Z", "B": null, "C": "2026-08-25T18:00:00Z",
    "D": null, "E": null, "F": null, "G": null, "H": null, "I": null, "J": null
  },
  "mode_j_eligible": null,
  "pending_revisits": [],
  "last_probe_ts": "2026-08-27T20:12:00Z",
  "ignored_count": 0,
  "passive_mode": false,
  "redaction_cooldown_until": "2026-08-27T21:00:00Z",
  "last_user_contact_ts": "2026-08-27T19:30:00Z",
  "session_active": true,
  "session_thread_id": ["mattermost", "11q5an3haffxfpo6kfradxp75y", null],
  "session_opened_at": "2026-08-28T12:00:00Z",
  "session_opened_by": "agent",
  "session_exchange_count": 3,
  "session_agent_turn_count": 2,
  "session_last_agent_mode": "C",
  "session_wind_down_phase": "open",
  "session_close_sent_at": null,
  "session_close_mode": null,
  "wind_down_nudge_threshold": 4,
  "wind_down_close_threshold": 6,
  "cooling_window_minutes": 30,
  "cooling_until": null,
  "session_recency_threshold_seconds": 900,
  "contact_window_hours": 24,
  "relationship_stage": "friendly",
  "stage_history": [
    {
      "stage": "neutral",
      "ts": "2026-08-20T18:00:00Z",
      "direction": "up",
      "evidence_ref": "eng_20260820_002"
    }
  ],
  "last_stage_review_ts": "2026-08-29T02:00:00Z"
}
```

Field definitions:

- `last_contact_ts` / `last_mode`: most recent agent-initiated contact, and
  its mode letter.
- `mode_history`: rolling window of the last N send-mode letters (default 7);
  enforces variety among relationship modes. Mode I is never appended.
- `mode_last_sent`: mode letter → last-sent timestamp (or `null`); enforces
  per-mode cadence caps.
- `mode_j_eligible`: `null`, or the eligible slot record (slot_id, slot,
  anchor, eligible_since, window_days). Written only by the Mode J predicate;
  read by session conversation routing.
- `pending_revisits`: revisits scheduled from deferred Mode J namings; entries
  carry `slot_id`, `revisit_after`, `revisit_channel`, `revisit_sent_at`.
- `last_probe_ts`: most recent Mode A (gap-led) contact.
- `ignored_count`: agent-initiated contacts since the last user-initiated one.
- `passive_mode`: `true` after three consecutive ignored contacts.
- `redaction_cooldown_until`: earliest time the next contact may be
  considered.
- `last_user_contact_ts`: last subject artifact timestamp.
- `session_active`: a message exists within the session recency threshold.
- `session_thread_id`: `[platform, channel_id, thread_id]` (`thread_id: null`
  = top-level channel message). Thread identity, not just recency, bounds a
  session.
- `session_opened_at` / `session_opened_by`: session start and its opener
  (`"subject"` or `"agent"`).
- `session_exchange_count`: completed back-and-forth pairs; increments when
  the subject sends after the agent's last reply. Never decrements.
- `session_agent_turn_count`: agent replies in the current session.
- `session_last_agent_mode`: mode letter of the latest session reply.
- `session_wind_down_phase`: one of `open`, `nudging`, `closing`, `cooling`.
- `session_close_sent_at` / `session_close_mode`: when the closing beat was
  sent, and in which mode.
- `wind_down_nudge_threshold` / `wind_down_close_threshold`: exchange counts
  where nudging begins (default 4) and a closing beat is forced (default 6).
- `cooling_window_minutes`: cooling-lock duration after a close (default 30).
- `cooling_until`: earliest time a new agent-initiated session may begin.
- `session_recency_threshold_seconds`: session recency bound (default 900 =
  15 min).
- `contact_window_hours`: rolling agent-initiated contact cap window
  (default 24).
- `relationship_stage`: one of
  `unknown | hostile | unfriendly | neutral | friendly | confidant` (stage
  model below). Default `unknown` — a fresh subject is a cold start.
- `stage_history`: append-only log of `{stage, ts, direction, evidence_ref}`
  transitions, `direction` `up` or `down`; never rewritten or removed. Depth
  permission is **derived per stage, never stored**.
- `last_stage_review_ts`: most recent dream-phase review; `null` = never (the
  next review scans the full archive index). Advances only when the review
  runs (transition or not); written by the review tooling alone.

## Relationship stage model

Depth is tracked as a stage; every send-mode is gated on it (the `min_stage`
matrix lives in `engram-engagement-repertoire`; gates run as eligibility
checks in mode selection).

- **Enum:** `unknown | hostile | unfriendly | neutral | friendly | confidant`.
- **`unknown` = cold start, depth-permission-zero:** the eligible set is Mode
  I, G, D, and B on an explicitly user-mentioned event; no history-anchored
  modes, no past-tense phrasing, present-tense curiosity only. `unknown` is
  not sticky: the first review with any session data must assign a concrete
  warmth stage — it never survives a review that had evidence to read.
- **Derivation is the dream-phase review** (engine-owned, the nightly
  consolidation duty; out-of-session, complete before the daily contact
  window). Why out-of-session: single-writer discipline (the in-session agent
  never writes `engagement_state.json`, stage included), detachment (the warm
  in-the-moment persona must not judge demotions; the reviewer sees the whole
  arc, not the moment inside it), freshness (a ≤24h lag is acceptable).
  Scan: all sessions since `last_stage_review_ts`; a first-ever review scans
  the full archive index. Signals — up: subject-initiation reciprocity,
  reply-depth reciprocity, unprompted self-disclosure, explicit warmth
  markers; down: ignored contacts, hostility/irritation markers. At most ONE
  rung per review, either direction.
- **Evidence rules:** promotion requires cited evidence — a verbatim quote or
  artifact reference, recorded as `evidence_ref` in the appended
  `stage_history` entry. Demotion fails closed: one strong negative signal
  (hostility, irritation, sustained ignoring) suffices; no evidence quorum is
  owed to back off.
- **Promotion velocity (the sigmoid):** relationships are volatile — a fight
  is a real, immediate downgrade — but two good days never buy
  neutral→friendly→confidant. Hard gates (tooling-enforced,
  `tools/engram_state.py`): dwell minimums before promotion is legal —
  →`friendly` requires ≥3 days at `neutral`; →`confidant` requires ≥14 days
  at `friendly`. The first review resolving `unknown` is dwell-exempt (no
  rung to dwell in), but `confidant` always requires the friendly dwell below
  it. Promotions advance exactly one rung. Demotions fall at most one rung
  gently — or to `unfriendly` from any non-negative stage — but `hostile` is
  reachable only from `unfriendly`: no hostile whiplash in a single night.
  `record_stage_transition` rejects illegal moves with a reason (`dwell:…`,
  `one_rung_max:…`), never clamps silently; the dream phase logs the
  rejection. Whether evidence justifies promotion within the legal dwell
  budget is the dream phase's procedural call; tooling enforces legality
  only.
- **Checkpoint semantics:** `engagement_state.json` and `gaps.md` are a
  static checkpoint read at session start; sessions develop on top as hot
  context — the in-session agent reads, never writes — and only the dream
  phase re-checkpoints them.
- **Depth permission is derived, not stored:** consumers compute it from
  `relationship_stage` + the repertoire's `min_stage` matrix; nothing else
  persists.

## Pre-wake accounting step (runs first, every fire)

1. Read `engagement_state.json`.
2. Clear an expired cooling lock: `cooling_until` past → set it `null` (and
   `session_wind_down_phase = null` when no session is active).
3. Query the raw archive / shared thread for any subject artifact newer than
   `last_user_contact_ts` (concrete query: last counterpart message or open
   `engram` session row within the recency threshold — bound once in the
   cron-tooling build, not redefined per prompt).
4. Newer subject artifact exists: set `last_user_contact_ts` to its
   timestamp, `ignored_count = 0`, `passive_mode = false`; if it carries a
   redaction signal, `redaction_cooldown_until = now + configured_cooldown`;
   then run session exchange-budget accounting (below). Persist.
5. None exists: leave the state unchanged.

**Why first:** the cap check begins with `passive_mode == false`; a subject
message that arrived between fires must clear it there, or the cron bails
incorrectly and passive mode sticks (TEST-PLAN trap T2). The profile never
decides "this probably counts as user contact."

## Cap checks (in order; 1–5 exit silently on first failure, 6–7 gate eligibility)

1. `passive_mode == false`
2. `now > redaction_cooldown_until`
3. No agent-initiated contact in the past `contact_window_hours` (rolling
   24h; `last_contact_ts` outside the window)
4. No active session (counterpart message or open session within the recency
   threshold)
5. `now > cooling_until` (no active Mode I cooling lock)
6. **Stage gate** (eligibility, not a bail): every candidate send-mode must
   satisfy its `min_stage` against `relationship_stage`; at `unknown` only
   the cold-start eligible set is available.
7. **Anchor verification** (eligibility, not a bail): every mode with an
   anchor requirement needs its anchor **verified before it is eligible** —
   a `gaps.md` `exemplar` pointing at a real archive artifact, an
   archive-index hit, or a recorded derived-store recall hit. Failure falls
   through to a lower mode or Mode I; it never suppresses the fire and never
   authorizes an unverified send.

Checks 1–5 failing exits the cron silently; 6–7 failing disqualifies the
candidate and the ladder falls through. A mode is never sent on an unverified
anchor or below its stage. **Agent-initiated contact** (proactive cron): 1–5
must all pass before a fresh opener is considered, 6–7 filter every candidate
mode. **Mid-session reply** (conversation routing): 1–5 are skipped (a reply
is already warranted and the session is not `cooling`); the stage gate still
applies to mid-session mode narrowing, and Mode J delivery additionally
requires the warm-exchange and slot predicates below.

## Mode selection priority ladder

1. **Event-driven modes first (B, H, G):** B (life-thread) when a pending
   event's expected date has passed or is within the lookahead window; H
   (celebration) when a milestone occurred or a positive pattern is freshly
   detectable; G (presence) when sustained stress or a big-project pattern is
   visible and no B/H trigger exists. The strongest trigger wins; these
   bypass `mode_history` variety.
2. **Scheduled revisit** (from a deferred Mode J naming): a `pending_revisits`
   entry with `revisit_after <= now` and `revisit_sent_at: null` is the
   strongest relationship-mode candidate, on channel `revisit_channel` (F, D,
   or G). Does not bypass event-driven modes; only one revisit is ever sent
   per slot.
3. **Relationship modes (C, F, D, E) by anchor strength**, variety applied
   **only** to these four: sort candidates strong → weak; deprioritize any
   mode in `mode_history` within the variety window unless its anchor is
   clearly stronger; enforce per-mode cadence via `mode_last_sent` (e.g. D
   ≤2×/week, F ≤1×/week, E ≤1×/week, C ≤1×/3 days — exact thresholds are
   config, not profile judgment); pick the strongest candidate not recently
   used and within cadence.
4. **Mode A (curiosity callback)** only when a high-priority gap exists in
   `gaps.md` and no event-driven, relationship, or revisit option has a
   strong anchor.
5. **Mode I (silence):** default when no mode has a strong enough anchor, a
   cap would be violated, or all candidates fail the voice gate.

**Gap pacing (Mode A and Mode J):** `gap_pressure` is active when an A-or-J
contact is among the last 2 agent-initiated contacts (`mode_history[-2:]`) —
it blocks Mode A and Mode J. Mode A additionally requires a rapport-peak
signal: a recent self-disclosure event or a stage promotion in
`stage_history`. Gaps close at rapport peaks, never on consecutive touches —
gap hunger is not an anchor.

**Voice gate (before any send-mode is selected):** the drafted opener must
not be an intake form, interrogator, or listicle; must be anchored to a real
artifact or `USER.md` entry; must not be greeting-first. On failure,
downgrade to the next candidate or Mode I. Temporal framing — time-of-day /
weekday / holiday register — is a phrasing layer applied at composition per
the repertoire; it is not a mode and never changes selection or the gates.

## State writes after selection

This skill is the **sole writer** of `engagement_state.json`; directors and
prompts make decisions and report outcomes, the engine persists.

- Any send-mode: `last_contact_ts = now`; `last_mode = <letter>`; append the
  letter to `mode_history` (never Mode I); `mode_last_sent.<letter> = now`.
- Mode A send: also `last_probe_ts = now`.
- Revisit send (F/D/G from a deferred Mode J naming): also `revisit_sent_at:
  now` on the matching `pending_revisits` entry.
- User response: `ignored_count = 0`; `last_user_contact_ts = now`.
- No response to a sent contact: `ignored_count += 1`; at 3, `passive_mode =
  true`.
- `declined:<reason>`: update `last_contact_ts`, `last_mode`, `mode_history`,
  and `mode_last_sent.<letter>`, but do **not** increment `ignored_count`.
- Redaction signal: `redaction_cooldown_until = now + configured_cooldown`.
- Mode I: metadata-only log; no contact field advances. Cooling-lock skips
  log `skipped:cooling-lock` and advance nothing.
- Mid-session agent replies: update `session_agent_turn_count`,
  `session_last_agent_mode`, and `mode_last_sent.<mode>` when the send is
  reported.

## Session exchange budget and wind-down

A session is bounded by **thread identity plus recency**: same
`(platform, channel_id, thread_id)` tuple with the newest artifact within
`session_recency_threshold_seconds`; a different `thread_id` always starts a
new session regardless of recency.

**Starting a new session** (new artifact arrives, none active):

1. `cooling_until` is in the future and the artifact belongs to the previous
   session's thread → do **not** start a session, do not reply; leave the
   phase `cooling` (the lock survives same-thread resurrection — trap T6).
2. Otherwise open: `session_active = true`, `session_thread_id` = the
   artifact's thread tuple, `session_opened_at = now`, `session_opened_by` =
   the artifact's sender, `session_exchange_count = 1`,
   `session_agent_turn_count = 0`, `session_last_agent_mode = null`,
   `session_wind_down_phase = open`, close fields `null`, expired
   `cooling_until` cleared.

**Continuing a session** (subject artifact while active): increment
`session_exchange_count` by 1 when the artifact is newer than the agent's
last reply; recompute the phase — `< nudge_threshold` → `open`;
`< close_threshold` → `nudging`; `>= close_threshold` → `closing`. Counts
never decrement.

**Agent reply accounting** (any reported agent send in the session):
increment `session_agent_turn_count`; set `session_last_agent_mode`; update
`mode_last_sent.<mode>`; on a closing send, apply the cooling lock.

The exchange budget is independent of `passive_mode`: `passive_mode` is a
long-term agent-initiated cap, the budget a per-session brake. Either
suppresses agent-initiated contact; they may overlap.

## Cooling lock (canonical spec)

When a `sent:<mode>:closing` outcome is reported:
`session_close_sent_at = now`; `session_close_mode = <mode>`;
`session_wind_down_phase = cooling`; `cooling_until = now +
cooling_window_minutes`.

Once `cooling`, the phase stays `cooling` until `cooling_until` expires — no
mid-session logic, subject message, or cron resets it early; set-once per
close. During the lock: conversation routing does not reply to same-thread
subject artifacts (log `skipped:cooling-lock`); the proactive-engagement cron
does not open a new agent-initiated contact (cap check 5); `mode_last_sent.I`
is never written (cooling is not a Mode I selection — the closing mode's
entry carries the cadence signal).

## Session conversation routing

The only component that wakes the Engram profile to respond once a session
is open; brand-new agent-initiated contact is the proactive-engagement cron's
job.

**Stop conditions** (exit silently, no reply, no wake): state
unreadable/malformed → log error; `session_wind_down_phase == cooling` and
`now <= cooling_until` → log `skipped:cooling-lock`; the subject artifact is
older than the agent's last reply (duplicate/out-of-order delivery); the
subject signals redaction → honor it, no reply, report `redaction` so the
cooldown is set.

**Steps:**

1. Run session accounting (boundary + budget + phase; stop if cooling).
2. Check the newest subject artifact for redaction.
3. Apply **mid-session mode narrowing**: never open a new mode mid-session —
   sustain `session_last_agent_mode` in all phases. `open` → normal reply in
   the current mode; `nudging` → current mode with a wind-down instruction
   (a natural landing, not a sudden cutoff); `closing` → force one short,
   warm closing sentence that does not invite continuation (Mode I only if
   the current mode has no sensible closing beat). The profile never sees
   the exchange counter and never decides to keep a session alive past its
   budget.
4. Voice-gate the drafted reply.
5. Wake the profile with the mode contract and phase guidance loaded; send
   the reply in the shared thread with the counterpart `@mention`.
6. Report the outcome for persistence. **Exact tokens:**
   `sent:<mode>:<phase>` (phase `open | nudging | closing`);
   `declined:<reason>` (profile or voice-gate refusal); `redaction`;
   `skipped:cooling-lock`. Mode J classification outcomes:
   `sent:J:disclosure`, `sent:J:deferral`, `declined:avoidance-deflection`.
   Mode J namings ride this path when `mode_j_eligible` is set — never cold,
   never session-opening.

## Mode J eligibility predicate and deferral processing

**Predicate** (deterministic, tooling-owned; the profile never overrides). A
slot is J-eligible when **all** hold:

1. A skeleton slot in `gaps.md` with `source: skeleton`,
   `sensitivity: handle-with-care`, `status` `open` or `partial`,
   `avoidance_named: null`, and `tier` 1 or 2 (tier-3 slots are hard-gated
   regardless of priority; `declined`, `closed`, `versioned`,
   `deferred-open` are all ineligible).
2. **Zero mentions** of the slot topic over the configured window (default:
   last 90 days of archive, or all archive if younger) — a deterministic
   archive query (text/embedding/Hindsight, bound in the tooling build),
   including aliases bound in slot metadata. Never an LLM impression.
3. An active, warm exchange in progress: the subject has sent at least one
   artifact in the current exchange, and the exchange is not a session opener
   (the agent did not just re-engage after silence).

Slot eligibility is necessary, not sufficient: delivery additionally passes
the stage gate (cap check 6 — Mode J's `min_stage` is `friendly`, confidant
preferred, per the repertoire matrix) and gap pacing (`gap_pressure` blocks J
like A).

Multiple eligible slots → highest priority per the `engram-gap-skeleton`
formula, tie-break earliest `last_touched`. On a hit, write `mode_j_eligible`
(slot_id, slot, anchor, eligible_since, window_days); the eligibility cron
itself sends nothing. A Mode J send appends `"J"` to `mode_history` and sets
`mode_last_sent.J` like any send-mode; `last_probe_ts` is unaffected.

**Exactly-once enforcement:** verify `avoidance_named` is `null` before any
send; at the verified send moment, write `avoidance_named: now` atomically
with the slot update; a `declined` outcome also sets it. Non-null → refuse.

**Refusal codes (hard stops, never reinterpreted):**
`refused:avoidance-already-named` (non-null `avoidance_named`);
`refused:deferred-open` (`status: deferred-open`);
`refused:revisit-already-sent` (non-null `revisit_sent_at`).

**Deferral processing** (on `sent:J:deferral`): set `avoidance_named: now`
if unset; leave status `open`/`partial`; write the `deferral` record —
`count` (1 or 2, never higher), `last_deferred_at`, `reason`
(`long_story|wrong_moment|user_cue`), literal `user_cue` (or null),
`revisit_after`, `revisit_channel` (`F|D|G`), `revisit_sent_at: null`.
Channel: `long_story` → F first, D if F cadence is exhausted; `wrong_moment`
→ G; `user_cue` → F/D if date-bound, else G. Timing: the parsed cue time if
parseable, else `last_deferred_at + 14 days`. Add the entry to
`pending_revisits`.

**`deferred-open` and the one-knock cap:** a second deferral sets
`deferral.count = 2` and `status: deferred-open` — behaviorally `declined`
for outbound (further knocks hit `refused:deferred-open`) but semantically
distinct: a later user-initiated disclosure is received as normal
gap-filling. Exactly one revisit per slot: the engine checks
`revisit_sent_at == null` before allowing the send, sets it once, and never
schedules a second. Revisit outcomes: disclosure → `partial`/`closed`;
deferral → `deferred-open`; deflection → `declined`.

## Single-writer boundary

Only this skill's tooling writes `engagement_state.json` (all fields; stage
fields only via the dream-phase review tooling) and the slot-level `deferral`
/ `avoidance_named` fields in `gaps.md`. Mode prompts, actuators, and the
profile **invoke or report**; they never read or write state directly. The
proactive-engagement cron reads scheduling state but does not evaluate Mode J
eligibility.

## Prose vs. tooling (`tools/engram_state.py`) divergences

The reference implementation binds this spec; known differences, do not
"fix" silently:

1. `session_thread_id` and the two threshold fields
   (`session_recency_threshold_seconds`, `contact_window_hours`) are
   canonical here; the former prose schemas lacked them.
2. Redaction cooldown: prose `now + configured_cooldown`; code fixes +1h
   (`record_outcome`).
3. Mode J warmth: the code additionally requires
   `session_opened_by == "subject"` (stricter — agent-opened warm sessions
   are never eligible).
4. Priority formula: prose computes
   `deliverable_value × anchor_strength × tier_gate × recency_of_attempt`;
   the code's Mode A path takes the first `open`/`partial` gap whose exemplar
   passes verification (stage gate + gap pacing + rapport peak applied) —
   the formula is still unimplemented in tooling.
5. The director imports `engram_state` and writes directly; prose says the
   selector "instructs" — same single-writer boundary, different mechanics.
6. `record_send` would write `mode_last_sent.I` if called with `"I"`; by
   construction it never is (Mode I is a no-send).
7. Stage derivation: the code ships the deterministic gates
   (`MODE_MIN_STAGE`, gap pressure, rapport-peak-from-`stage_history`), the
   `record_stage_transition` write helper (`DWELL_MIN_DAYS` dwell minimums +
   the one-rung cap; rejections returned with a reason, never clamped), and
   `last_stage_review_ts` bookkeeping (`stage_review_due`,
   `record_stage_review`); the signal scoring is procedural in the dream
   phase.
8. Anchor verification: the code verifies the deterministic part only —
   `gaps.md` exemplar / archive-index existence on disk; derived-store
   recall hits are trusted from dream-phase `evidence_ref` records.
9. The unknown-stage B exception ("explicitly user-mentioned event") is
   approximated in code by "a subject artifact exists in the archive index"
   — no event-matching machinery exists yet (B/H/G triggers remain
   unimplemented).
10. Rapport peak: a stage promotion in `stage_history` (configured window,
    default 7 days) is checked deterministically; "recent self-disclosure
    event" is procedural — not yet recorded in state.

## Pitfalls

- **Randomizing instead of prioritizing.** Event-driven modes must not lose
  to a relationship mode with a stronger anchor.
- **Mode fatigue.** Without `mode_history` variety the selector loops.
- **Weak-anchor sends.** A send without a strong anchor is
  `cadence-pressure`.
- **Fabricated familiarity.** Past-tense phrasing below `friendly` — or
  anywhere without a verified anchor — is the exact defect the stage gate
  and anchor verification exist to prevent. A fresh subject is a cold start,
  never a reunion.
- **Double writes.** Directors/prompts must not write state; only the
  engine.
- **Opening a new mode mid-session.** Sustain `session_last_agent_mode`
  always.
- **Ignoring or resetting the cooling lock.** `cooling_until` is a hard cap;
  set-once per close, never cleared early.
- **Skipping the pre-wake step.** Every engagement cron includes it; one
  missing mode punches a hole in passive-mode disarm.
- **LLM-based zero-mentions.** The check is a deterministic archive query.
- **Reprobe after decline / after `avoidance_named`.** Permanent, hard stop.

## Verification

- [ ] Pre-wake accounting ran first; `passive_mode` cleared on subject
      contact.
- [ ] Cap checks 1–5 passed, in order, before any agent-initiated selection;
      the stage gate and anchor verification (6–7) filtered every candidate
      mode.
- [ ] Selection followed B/H/G → revisit → C/F/D/E variety+cadence → A → I,
      with gap pacing (`gap_pressure`, rapport peak) applied to A and J.
- [ ] Voice gate applied to the selected send-mode.
- [ ] Mode I logged a reason; no profile wake; no state advanced.
- [ ] Session boundary used thread identity + recency; exchange counts only
      rose.
- [ ] Closing send set the cooling lock; both selector and routing respected
      it until expiry; `skipped:cooling-lock` logged when active.
- [ ] Mid-session routing sustained `session_last_agent_mode`; `nudging`
      appended a landing instruction; `closing` forced one short final
      reply.
- [ ] Mode J: predicate deterministic; `avoidance_named` exactly-once;
      refusals returned verbatim; deferral record complete; one-knock cap
      enforced.
- [ ] Any relationship-stage transition came out of the dream-phase review,
      appended to `stage_history` with a cited `evidence_ref`; promotion
      without evidence did not happen; dwell and one-rung legality held (or
      the rejection was logged, never forced); `last_stage_review_ts`
      advanced.
- [ ] Every outcome was persisted by the engine, not by a prompt or the
      profile.
