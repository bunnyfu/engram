---
name: engram-mode-selector
description: "Select the agent-initiated mode for this rolling-24h window."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, mode-selector, engagement, state]
    related_skills:
      [engram-state-accounting, engram-interview, engram-mode-life-thread,
       engram-mode-reminiscence, engram-mode-diary-prompt, engram-mode-gift,
       engram-mode-voice-invite, engram-mode-presence, engram-mode-celebration,
       engram-mode-naming-the-silence, engram-mode-silence, engram-conversation-handler]
---

# Engram Mode Selector Skill

Choose one engagement mode (A–J) for the next agent-initiated contact. Mode selection
and writes to `engagement_state.json` are tooling-owned, **except** for
`engram-state-accounting`-owned fields (`mode_j_eligible`, slot `deferral` records); the
profile only executes the selected mode's skill.

## When to Use

- The engagement cron fires.
- The pre-wake accounting step has already cleared any subject-contact disarm.
- All cap checks have passed.

## `engagement_state.json` schema

```json
{
  "last_contact_ts": "2026-08-27T20:12:00Z",
  "last_mode": "A",
  "mode_history": ["B", "C", "A"],
  "mode_last_sent": {
    "A": "2026-08-27T20:12:00Z",
    "B": null,
    "C": "2026-08-25T18:00:00Z",
    "D": null,
    "E": null,
    "F": null,
    "G": null,
    "H": null,
    "I": null,
    "J": null
  },
  "mode_j_eligible": null,
  "pending_revisits": [],
  "last_probe_ts": "2026-08-27T20:12:00Z",
  "ignored_count": 0,
  "passive_mode": false,
  "redaction_cooldown_until": "2026-08-27T21:00:00Z",
  "last_user_contact_ts": "2026-08-27T19:30:00Z",
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

- `last_contact_ts`: timestamp of the most recent agent-initiated contact.
- `last_mode`: mode letter of the most recent agent-initiated contact.
- `mode_history`: rolling window of the last N send-mode letters (default 7) used to
  enforce variety among relationship modes. Mode I is never appended.
- `mode_last_sent`: map from mode letter to the timestamp it was last sent (or `null`).
  Used to enforce per-mode cadence caps.
- `last_probe_ts`: timestamp of the most recent Mode A (gap-led) contact attempted.
- `mode_j_eligible`: null, or a slot reference. Written by `engram-state-accounting` during
  the Mode J eligibility cron; read by the active-conversation handler. This selector does
  **not** evaluate or write it.
- `pending_revisits`: list of scheduled revisits from deferred Mode J naming. Each entry
  carries `slot_id`, `revisit_after`, `revisit_channel`, and `revisit_sent_at`. Written by
  `engram-state-accounting`; the selector reads it to schedule the one revisit.
- `ignored_count`: contacts since the last user-initiated contact.
- `passive_mode`: true after three consecutive ignored contacts.
- `redaction_cooldown_until`: absolute time after which the next contact may be considered.
- `last_user_contact_ts`: last time the subject sent any artifact to Engram.
- `session_active`: true when a conversation has a message within the configured session
  recency threshold.
- `session_opened_at`: timestamp the current session started.
- `session_opened_by`: `"subject"` or `"agent"`; who sent the first message of this session.
- `session_exchange_count`: number of completed back-and-forth pairs in the active session.
- `session_agent_turn_count`: number of agent replies sent in the current session.
- `session_last_agent_mode`: mode letter of the agent's most recent reply in this session.
- `session_wind_down_phase`: one of `open`, `nudging`, `closing`, `cooling`.
- `session_close_sent_at`: timestamp the closing beat was sent.
- `session_close_mode`: mode letter used for the closing beat.
- `wind_down_nudge_threshold`: exchange count at which nudging begins (default 4).
- `wind_down_close_threshold`: exchange count at which a closing beat is forced (default 6).
- `cooling_window_minutes`: duration of the Mode I cooling lock after a close (default 30).
- `cooling_until`: absolute timestamp after which a new agent-initiated session may begin.

## Cap checks (tooling, after accounting)

Perform in order; exit silently on first failure:

1. `passive_mode == false`
2. `now > redaction_cooldown_until`
3. No agent-initiated contact in the past 24 hours (`last_contact_ts` outside rolling window)
4. No active session (counterpart message or open session within configured recency threshold)
5. `now > cooling_until` (no active Mode I cooling lock from a recent close)

## Invocation contexts

The selector is invoked in two distinct contexts:

1. **Agent-initiated contact (selector cron):** all five cap checks above must pass. The
   selector chooses a fresh session opener from the priority list below.
2. **Mid-session reply (conversation handler):** cap checks 1–5 are skipped; the
   conversation handler has already determined that a reply is warranted and that the
   session is not in `cooling`. The selector narrows the reply mode based on
   `session_wind_down_phase` and `session_last_agent_mode` (see "Mid-session mode
   narrowing").

## Mid-session mode narrowing

When invoked by the conversation handler, the selector must not open a new engagement
mode. It sustains or closes the current mode according to the exchange-budget phase
owned by `engram-state-accounting`:

- **`session_wind_down_phase == open`:** sustain `session_last_agent_mode`. Do not switch
  to a different mode mid-session. Run the voice gate on the drafted reply.
- **`session_wind_down_phase == nudging`:** sustain `session_last_agent_mode`, but add a
  wind-down instruction to the mode guidance: nudge Engram toward a natural closing
  beat. The reply should feel like the conversation is gently landing, not like a sudden
  cutoff. Run the voice gate.
- **`session_wind_down_phase == closing`:** force a closing beat. The mode remains
  `session_last_agent_mode` (or Mode I if the current mode has no sensible closing beat),
  but the reply must be one short, warm sentence that does not invite continuation.
  Voice-gate it for finality without abruptness.

In all three phases, **no new mode may open mid-session**. The selector returns the
selected mode and phase-specific guidance to the conversation handler; it does **not**
write `engagement_state.json`.

## Mode selection priority

1. **Event-driven modes first (B, H, G):**
   - **B (life-thread):** a pending event's expected date has passed or is within the
     configured lookahead window.
   - **H (celebration):** a milestone has occurred or a positive pattern is freshly
     detectable.
   - **G (presence):** sustained stress or big-project pattern is visible and no B/H
     trigger exists.
   - Event-driven triggers bypass `mode_history` variety; the strongest event-driven
     trigger wins.
2. **Scheduled revisit (from a deferred Mode J naming):**
   - A `pending_revisits` entry exists with `revisit_after <= now` and `revisit_sent_at: null`.
   - Treat it as the strongest relationship-mode candidate with channel `revisit_channel`
     (`F`, `D`, or `G`). It is slotted into the relationship-mode evaluation but does not
     bypass event-driven modes.
   - Only one revisit is ever sent per slot; state-accounting enforces `revisit_sent_at`.
3. **Relationship modes (C, F, D, E) by anchor strength, with `mode_history` variety
   applied ONLY to these four:**
   - Sort candidates by anchor strength (strong → weak).
   - Deprioritize any mode already in `mode_history` within the variety window unless it
     has a clearly stronger anchor than the alternatives.
   - Enforce per-mode cadence using `mode_last_sent` (e.g., D ≤2×/week, F ≤1×/week,
     E ≤1×/week, C ≤1×/3 days — exact thresholds are config, not profile judgment).
   - Pick the strongest candidate not recently used and within cadence.
4. **Mode A (curiosity callback) only when:**
   - A high-priority gap exists in `gaps.md`.
   - No event-driven, relationship, or revisit option has a strong anchor.
5. **Mode I (silence):** default when no mode above has a strong enough anchor, a cap
   would be violated, or all candidate modes fail the voice gate.

## Voice gate

Before a send-mode is selected, its drafted opener must pass the curious-friend test:

- Not an intake form, interrogator, or listicle.
- Anchored to a real artifact or `USER.md` entry.
- Not a greeting-first script.
- If it fails, downgrade to the next mode or Mode I.

## State writes after selection

`engram-state-accounting` is the **sole writer** of `engagement_state.json`. The selector
makes mode decisions and **instructs** state-accounting to persist the resulting state; it
does not write the file directly.

State-accounting writes the standard contact-state fields (`last_contact_ts`, `last_mode`,
`mode_history`, `mode_last_sent`, `last_probe_ts`, `ignored_count`, `passive_mode`,
`redaction_cooldown_until`, `last_user_contact_ts`) and the session wind-down fields
(`session_active`, `session_exchange_count`, `session_wind_down_phase`, `cooling_until`,
etc.) on behalf of the selector and the conversation handler.

`engram-state-accounting` is also the sole writer of `mode_j_eligible`, slot `deferral`
records, and `pending_revisits`. The selector never evaluates or writes Mode J eligibility.

- On any send-mode, the selector instructs state-accounting to:
  - Set `last_contact_ts = now`.
  - Set `last_mode = <letter>`.
  - Append the letter to `mode_history` (except Mode I — never append).
  - Set `mode_last_sent.<letter> = now`.
- On Mode A send: also set `last_probe_ts = now`.
- On revisit send (F/D/G, from a deferred Mode J naming): instruct `engram-state-accounting`
  to set `revisit_sent_at: now` on the corresponding `pending_revisits` entry. The revisit
  is a normal mode send and follows the same state-write rules as any send-mode.
- On user response: reset `ignored_count = 0`, update `last_user_contact_ts = now`.
- On no response to a sent contact: increment `ignored_count`; if `ignored_count >= 3`,
  set `passive_mode = true`.
- On `declined:<reason>` from the profile: update `last_contact_ts`, `last_mode`,
  `mode_history`, and `mode_last_sent.<letter>` to `now`, but do **not** increment
  `ignored_count`.
- On redaction signal: set `redaction_cooldown_until = now + configured_cooldown`.
- Mode I produces only a metadata-only log entry; it does **not** update `last_contact_ts`,
  `last_mode`, `mode_history`, or `mode_last_sent`. Mid-session cooling-lock skips are logged
  by the conversation handler and do not advance state.
- On mid-session agent replies handled by the conversation handler, the selector still
  chooses/narrows the mode but state-accounting updates `session_agent_turn_count`,
  `session_last_agent_mode`, and `mode_last_sent.<mode>` when the handler reports the send.

## Procedure

### Agent-initiated contact procedure (selector cron)

1. Run pre-wake accounting (`engram-state-accounting`): clear `passive_mode` if the
   subject has contacted Engram since `last_user_contact_ts`; state-accounting also updates
   session budget and wind-down phase fields.
2. Run the five cap checks in order.
3. If any cap check fails: log `skipped:<reason>` and exit.
4. Evaluate event-driven modes (B, H, G). If any trigger fires and passes the voice gate,
   select it and skip to step 9.
5. Check `engagement_state.json.pending_revisits` for any entry with `revisit_after <= now`
   and `revisit_sent_at: null`. If one exists, treat it as the strongest relationship-mode
   candidate with its `revisit_channel`; otherwise build the relationship-mode candidate list
   from scratch, score anchors, apply variety and cadence checks.
6. Run voice-gate on the top candidate. If it fails, try the next candidate.
7. If Mode A is reached: verify a high-priority gap exists; otherwise fall through.
8. Select Mode I if no send-mode qualifies.
9. Wake the Engram profile with the selected mode's skill loaded, or log silence.
10. After the run: archive raw artifacts, instruct `engram-state-accounting` to update
    `engagement_state.json` deterministically per the state-write rules. Do not touch
    `mode_j_eligible` or `pending_revisits`; those are state-accounting-owned.

### Mid-session reply procedure (conversation handler)

1. The conversation handler has already invoked `engram-state-accounting` to update the
   session budget and wind-down phase.
2. Skip cap checks 1–5; the active session and cooling state are already known.
3. Apply "Mid-session mode narrowing" based on `session_wind_down_phase` and
   `session_last_agent_mode`.
4. Run the voice gate on the drafted reply.
5. Return the selected mode and phase-specific guidance to the conversation handler.
6. The conversation handler wakes the Engram profile, sends the reply, and reports the
   outcome (`sent:<mode>:<phase>`) back to state-accounting for persistence.

## Pitfalls

- **Randomizing instead of prioritizing.** Event-driven modes should not lose to a
  relationship mode just because the relationship mode has a stronger anchor.
- **Mode fatigue.** Without `mode_history` variety, the selector can fall into a small
  loop.
- **Weak-anchor sends.** A send without a strong anchor is a `cadence-pressure` defect.
- **Double writes.** Per-mode cron prompts and the conversation handler must not write
  `engagement_state.json`; only `engram-state-accounting` does, on instruction from the
  selector or conversation handler.
- **Opening a new mode mid-session.** The selector must sustain `session_last_agent_mode`
  during an active session, even in `open` phase.
- **Ignoring the cooling lock.** The selector cron must treat `cooling_until` as a hard cap.
- **Profile-side wind-down override.** The selector and conversation handler provide
  narrowing guidance; the profile never decides to keep a session alive past its budget.

## Verification

- [ ] Pre-wake accounting ran and `passive_mode` was cleared if the subject re-engaged.
- [ ] All five cap checks passed before an agent-initiated contact selection.
- [ ] Selection followed the priority order (B/H/G → scheduled revisit → C/F/D/E variety+cadence → A → I).
- [ ] No Mode J eligibility evaluation happened in the selector.
- [ ] State-accounting-owned fields (`mode_j_eligible`, `pending_revisits`, session budget,
      cooling lock) were not written by the selector.
- [ ] Voice gate was applied to the selected send-mode.
- [ ] Mode I logged a reason; no profile was woken; no state advanced as a contact.
- [ ] `engagement_state.json` was updated by `engram-state-accounting`, not the profile or selector.
- [ ] Mid-session narrowing sustained `session_last_agent_mode` and never opened a new mode.
- [ ] `nudging` phase appended a wind-down nudge; `closing` phase forced a short, final reply.
- [ ] `cooling_until` was checked and respected by the selector cron.
