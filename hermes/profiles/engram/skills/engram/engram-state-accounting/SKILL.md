---
name: engram-state-accounting
description: "Perform deterministic engagement-state accounting."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, engagement, state, accounting, caps]
    related_skills: [engram-mode-selector, engram-interview, engram-mode-naming-the-silence, engram-gap-skeleton, engram-conversation-handler]
---

# Engram State Accounting Skill

Run the deterministic pre-wake accounting step for `engagement_state.json` and the
Mode J eligibility predicate. This step runs first in every engagement cron prompt
before cap checks, so that subject-initiated contact can clear `passive_mode` and reset
`ignored_count`. The Mode J predicate is exposed to the Mode J eligibility cron and to
the conversation handler; `engram-state-accounting` is the sole writer of `mode_j_eligible`,
`pending_revisits`, and slot `deferral` records.

## When to Use

- At the very beginning of every engagement cron prompt (selector, Mode A, Modes B–I).
- When the conversation handler updates session budget and wind-down state before an
  Engram reply.
- When the Mode J eligibility cron or conversation handler invokes the Mode J
  eligibility predicate.
- Before any cap check or mode selection.

Don't use for: consolidation or mirror-SOUL duties (they don't initiate contact).
Don't use as: a direct writer of `engagement_state.json` by any other prompt.

## Pre-wake accounting step

1. Read `engagement_state.json`.
2. Query the raw archive / shared thread for any subject artifact with a timestamp newer
   than `last_user_contact_ts`. (Concrete query: last counterpart message or open `engram`
   session row within the configured recency threshold — bind in the cron-tooling build
   spec per TEST-PLAN step 5.)
3. If a newer subject artifact exists:
   - Set `last_user_contact_ts = now`.
   - Set `ignored_count = 0`.
   - Set `passive_mode = false`.
   - If the artifact contains a redaction signal, set
     `redaction_cooldown_until = now + configured_cooldown`.
   - Run session exchange-budget accounting (see "Session exchange budget and wind-down
     lock" below): detect session boundary, update `session_exchange_count` and
     `session_wind_down_phase`, and respect the cooling lock.
   - Persist `engagement_state.json`.
4. If no newer subject artifact exists: leave `engagement_state.json` unchanged.
5. Now proceed to cap checks.

## Why this comes first

The cap check begins with `passive_mode == false`. If a subject message arrived between
fires, it must reset `passive_mode` before that check, or the cron will incorrectly bail
out and leave passive mode stuck. This is the disarm half of TEST-PLAN trap T2.

## Mode J eligibility predicate

The Mode J eligibility cron and conversation handler ask state-accounting for
`j_eligible`, `j_slot_id`, and `j_opener_anchor`.
The predicate is deterministic and tooling-owned; the profile never overrides it.

Eligibility requires **all** of the following:

1. A skeleton slot exists in `gaps.md` with:
   - `source: skeleton`
   - `sensitivity: handle-with-care`
   - `status` is `open` or `partial` (not `declined`, `closed`, `versioned`, or `deferred-open`)
   - `avoidance_named` is `null`
   - `tier` is 1 or 2 (tier-3 slots are hard-gated regardless of priority)
2. The corpus has **zero mentions** of the slot topic over the configured window.
   - Default window: the last 90 days of archive, or all archive if < 90 days old.
   - The check is a deterministic archive query (text/embedding/hindsight, bound in the
     tooling build spec), not an LLM judgment.
3. An active, warm exchange is in progress.
   - The subject has sent at least one artifact in the current exchange.
   - The exchange is not a session opener (i.e., the agent did not just re-engage after
     a period of silence).
4. The slot is not already `declined`, `closed`, `versioned`, or `deferred-open`.

If multiple slots are eligible, pick the highest-priority skeleton slot using the
`engram-gap-skeleton` priority formula, tie-breaking by earliest `last_touched`.

## Zero-mentions check

- Query the archive index and `USER.md` for any artifact matching the slot topic within the
  configured window.
- A match is a direct mention, a named reference, or a strong synonym/handle bound in the
  slot metadata (e.g., `aliases: ["mom","mother"]` for a parents slot).
- Zero matches → predicate passes. Any match → the slot is not J-eligible until the window
  rolls forward.

## `avoidance_named` exactly-once enforcement

- `avoidance_named` is a set-once field on the gap entry. Only `engram-state-accounting`
  may write it.
- Before any Mode J send, state-accounting verifies `avoidance_named` is `null`. If it is
  non-null, the tooling refuses the send and reports `refused:avoidance-already-named`.
- If the slot status is `deferred-open`, the tooling refuses and reports
  `refused:deferred-open`.
- At the moment of a verified Mode J send, state-accounting writes `avoidance_named: now`
  atomically with the slot update.
- A `declined` outcome also sets `avoidance_named: now` so the slot is never reprobed.

## Refusal codes

State-accounting returns these refusals instead of allowing the caller (Mode J eligibility
cron, selector, or conversation handler) to override:

- `refused:avoidance-already-named` — `avoidance_named` is non-null.
- `refused:deferred-open` — slot `status: deferred-open`.
- `refused:revisit-already-sent` — `revisit_sent_at` is non-null for this slot.

The profile or another skill never reinterprets a refusal; it is a hard stop.

## Mode J entries in `mode_history`

When the conversation handler reports a Mode J send, state-accounting appends `"J"` to
`mode_history` and sets `mode_last_sent.J = now` exactly as for any other send-mode.
Mode J is a send-mode for history and cadence purposes; it does not affect
`last_probe_ts`.

## Session exchange budget and wind-down lock

State-accounting owns the per-session exchange budget, the forced de-escalation ladder
state, and the Mode I cooling lock. These fields live in `engagement_state.json` and are
written **only** by `engram-state-accounting`.

### New `engagement_state.json` fields

```json
{
  "session_active": true,
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
  "cooling_until": null
}
```

- `session_active`: true when a conversation has a message within the configured session
  recency threshold.
- `session_opened_at`: timestamp the current session started.
- `session_opened_by`: `"subject"` or `"agent"`; who sent the first message of this session.
- `session_exchange_count`: number of completed back-and-forth pairs in the active session.
  Increments when the subject sends after the agent's last reply.
- `session_agent_turn_count`: number of agent replies sent in the current session.
- `session_last_agent_mode`: mode letter of the agent's most recent reply in this session.
- `session_wind_down_phase`: one of `open`, `nudging`, `closing`, `cooling`.
- `session_close_sent_at`: timestamp the closing beat was sent; null until then.
- `session_close_mode`: mode letter used for the closing beat.
- `wind_down_nudge_threshold`: exchange count at which the selector begins nudging toward a
  close (default 4).
- `wind_down_close_threshold`: exchange count at which a closing beat is forced (default 6).
- `cooling_window_minutes`: duration of the Mode I cooling lock after a close (default 30).
- `cooling_until`: absolute timestamp after which a new agent-initiated session may begin.

### Session boundary detection

A session is active if the shared thread has any artifact newer than the configured
recency threshold (e.g., 15 minutes). If no artifact exists within that window, the session
is inactive.

### Starting a new session

When a new artifact arrives and `session_active` is false:

1. If `cooling_until` is in the future and the artifact belongs to the previous session
   thread, **do not** start a new session. Leave `session_wind_down_phase` as `cooling` and
   do not reply. This preserves the Mode I cooling lock.
2. Otherwise, start a new session:
   - `session_active = true`
   - `session_opened_at = now`
   - `session_opened_by = subject|agent` based on the newest artifact's sender
   - `session_exchange_count = 1`
   - `session_agent_turn_count = 0`
   - `session_last_agent_mode = null`
   - `session_wind_down_phase = open`
   - `session_close_sent_at = null`
   - `session_close_mode = null`
   - Clear any expired `cooling_until` (`null` if `now > cooling_until`).

### Continuing a session

When a new subject artifact arrives and `session_active` is true:

1. If the subject artifact is newer than the agent's last reply, increment
   `session_exchange_count` by 1.
2. Recompute `session_wind_down_phase`:
   - `session_exchange_count < wind_down_nudge_threshold` → `open`
   - `wind_down_nudge_threshold <= session_exchange_count < wind_down_close_threshold` →
     `nudging`
   - `session_exchange_count >= wind_down_close_threshold` → `closing`
3. Do not decrement counts; the budget only burns down.

### Cooling lock (set-once per close)

When the conversation handler reports `sent:<mode>:closing`:

1. Set `session_close_sent_at = now`.
2. Set `session_close_mode = <mode>`.
3. Set `session_wind_down_phase = cooling`.
4. Set `cooling_until = now + cooling_window_minutes`.

Once `session_wind_down_phase` becomes `cooling`, it stays `cooling` until `cooling_until`
expires. No mid-session logic, subject message, or cron may reset it early. This is the
Mode I cooling lock; its set-once semantics mirror `avoidance_named` in the gap ledger.

### Agent reply accounting

When the conversation handler reports any agent send in the active session:

1. Increment `session_agent_turn_count` by 1.
2. Set `session_last_agent_mode = <mode>`.
3. Update `mode_last_sent.<mode> = now`.
4. If the send was a closing beat (`sent:<mode>:closing`), apply the cooling lock above.

### Interaction with `passive_mode`

The cooling lock is independent of `passive_mode`. `passive_mode` is a long-term
agent-initiated cap; the cooling lock is a short-term per-session brake. They may
overlap; either one suppresses agent-initiated contact.

## Deferral processing

When a Mode J naming returns `sent:J:deferral`, state-accounting owns the deterministic
write to the slot:

1. Set `avoidance_named: now` (if not already set).
2. Leave `status` unchanged (`open` or `partial`).
3. Write or update the `deferral` record:
   ```yaml
   deferral:
     count: 1                       # 1 or 2; never higher
     last_deferred_at: 2026-08-27T21:00:00Z
     reason: long_story             # long_story | wrong_moment | user_cue
     user_cue: "after my exams"     # literal cue, or null
     revisit_after: 2026-09-10T21:00:00Z
     revisit_channel: F             # F | D | G
     revisit_sent_at: null
   ```
4. Choose `revisit_channel` deterministically:
   - `long_story` → `F` (voice memo) as first choice; fall back to `D` if voice-memo cadence
     is exhausted.
   - `wrong_moment` → `G`.
   - `user_cue` → `F` or `D` if the cue is date-bound; otherwise `G`.
5. Choose `revisit_after`:
   - If `user_cue` is parseable to a date/time, use that.
   - Otherwise, `last_deferred_at + 14 days`.
6. Add the revisit to the `pending_revisits` list in `engagement_state.json`.

## `deferred-open` enforcement

- If a revisit is also deferred, state-accounting increments `deferral.count` to 2 and
  sets `status: deferred-open`. No further outbound Mode J or revisit knocks are allowed.
- `deferred-open` is behaviorally equivalent to `declined` for outbound selection but
  semantically distinct: a later user-initiated disclosure is accepted as normal gap-filling.

## Revisit one-knock cap

- A slot with `deferral.count: 1` and `revisit_sent_at: null` is a pending revisit.
- State-accounting exposes `pending_revisits` to the selector.
- The selector may request one revisit per slot. State-accounting checks
  `revisit_sent_at == null` before allowing the send. If it is non-null, state-accounting
  refuses with `refused:revisit-already-sent`.
- When the send is allowed, state-accounting sets `revisit_sent_at: now`.
- If `revisit_sent_at` is non-null, the slot is removed from `pending_revisits` and no
  second revisit is ever scheduled.
- If the revisit outcome is:
  - **disclosure** → status moves to `partial`/`closed`.
  - **deferral** → `deferral.count = 2`, `status: deferred-open`.
  - **deflection** → `status: declined`.

## Revisit channel matching

- `long_story` → Mode F (voice-memo invitation) or Mode D (diary co-pilot); subject signaled
  the topic needs bandwidth or a longer form.
- `wrong_moment` → Mode G (presence/co-working offer); subject wants a calm, spacious
  context.
- `user_cue` → parse the cue; date-bound cues map to F/D, open-ended or stress-bound cues
  map to G.

## Single-writer boundary

- `engram-state-accounting` is the **only** writer of:
  - `engagement_state.json.mode_j_eligible`
  - `engagement_state.json.pending_revisits`
  - Slot-level `deferral` records in `gaps.md`
  - Slot-level `avoidance_named` fields
  - `mode_history` and `mode_last_sent` entries for Mode J sends
- The Mode J eligibility cron and the active-conversation handler **invoke**
  `engram-state-accounting`; they never read or write `engagement_state.json` or
  `gaps.md` directly.
- The selector cron reads `engagement_state.json` for its own scheduling state
  (`last_contact_ts`, `mode_history`, caps, etc.) but does **not** evaluate or write
  Mode J eligibility.

## Ownership

- Only `engram-state-accounting` performs the pre-wake accounting step and the J
  eligibility predicate.
- The profile never reads the archive to decide whether to clear `passive_mode` or whether
  a slot is J-eligible.
- The profile reports signals; `engram-state-accounting` applies them.

## Pitfalls

- **Skipping the step.** Every engagement cron prompt must include it; missing one mode
  creates a hole in passive-mode disarm.
- **Profile-side reset.** Never let the profile decide "this probably counts as user
  contact."
- **Query drift.** The exact active-session/new-message query must be bound in the
  cron-tooling spec, not redefined per prompt.
- **LLM-based zero-mentions check.** Zero-mentions must be a deterministic archive query,
  not a model's impression of whether the topic came up.
- **Reprobe after `declined`.** A slot with `status: declined` or non-null `avoidance_named`
  must never be J-eligible again.

## Verification

- [ ] `engagement_state.json` was read.
- [ ] The archive/thread was queried for subject artifacts newer than `last_user_contact_ts`.
- [ ] If a newer artifact was found, `ignored_count` was reset to 0 and `passive_mode` to false.
- [ ] The file was persisted before cap checks ran.
- [ ] Mode J eligibility used the deterministic predicate and respected `avoidance_named`.
- [ ] A non-null `avoidance_named` caused an immediate `refused:avoidance-already-named`.
- [ ] `deferred-open` slots caused an immediate `refused:deferred-open`.
- [ ] Deferral records were written by tooling with `count`, `last_deferred_at`, `reason`,
      `user_cue`, `revisit_after`, and `revisit_channel`.
- [ ] A second deferral set `status: deferred-open` and blocked further outbound knocks.
- [ ] Revisit one-knock cap was enforced: `revisit_sent_at` set once and never reset;
      non-null `revisit_sent_at` returned `refused:revisit-already-sent`.
- [ ] Session budget fields (`session_active`, `session_exchange_count`,
      `session_wind_down_phase`, `cooling_until`) were read and written only by
      state-accounting.
- [ ] Session boundary detection used the configured recency threshold and started a
      new session only when the previous session was inactive.
- [ ] The cooling lock preserved an active `cooling_until` when a subject artifact arrived
      in the same thread; it was never reset early.
- [ ] `session_exchange_count` incremented only on subject replies after an agent turn; it
      never decremented.
- [ ] `mode_last_sent.<mode>` was updated for every agent reply, including closing beats.
- [ ] The profile did not perform this accounting.
