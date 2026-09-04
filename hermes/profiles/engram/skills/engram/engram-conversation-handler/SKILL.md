---
name: engram-conversation-handler
description: "Orchestrate active-session replies and wind-down."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, conversation, handler, wind-down, reply]
    related_skills: [engram-state-accounting, engram-mode-selector, engram-mode-silence]
---

# Engram Conversation Handler

Route every Engram reply inside an active subject session. This handler is the only
component that wakes the Engram profile to respond to a subject artifact once a session
is already open. It relies on `engram-state-accounting` for all session-budget and
`engagement_state.json` writes, and on `engram-mode-selector` for mode narrowing during
wind-down.

## When to Use

- A subject artifact has arrived in the shared thread.
- The session is active (artifact within the configured recency threshold).
- The cooling lock has not suppressed the reply.

Don't use for: opening a brand-new agent-initiated contact (that's the selector cron).
Don't use as: a direct writer of `engagement_state.json` — all writes go through
`engram-state-accounting`.

## Stop conditions

Exit silently (no reply, no wake) when:

1. `engagement_state.json` cannot be read or is malformed → log error.
2. `session_wind_down_phase == cooling` and `now <= cooling_until` → log
   `skipped:cooling-lock`.
3. The subject artifact is older than the agent's last reply in the same exchange
   (duplicate or out-of-order delivery).
4. The subject signals redaction; honor it and escalate the cooldown to state-accounting.

## Steps

1. **Run session accounting** (`engram-state-accounting`):
   - Detect session boundary and update `session_active`, `session_opened_at`,
     `session_opened_by`, `session_exchange_count`, `session_wind_down_phase`, and
     `cooling_until`.
   - If `session_wind_down_phase == cooling` and `now <= cooling_until`, stop here.
2. **Check for redaction** in the newest subject artifact. If present:
   - Do not reply.
   - Report `redaction` to state-accounting so it can set `redaction_cooldown_until`.
3. **Invoke mid-session mode narrowing** (`engram-mode-selector`):
   - Pass `session_wind_down_phase`, `session_last_agent_mode`, and the subject artifact.
   - Receive the selected mode and phase guidance (`open`, `nudging`, or `closing`).
4. **Voice-gate the drafted reply** using the standard selector voice gate.
5. **Wake the Engram profile** with the selected mode's skill loaded and the phase
   guidance appended:
   - `open` — normal reply in the current mode.
   - `nudging` — reply in the current mode, but craft it as a natural landing; do not
     invite continuation.
   - `closing` — one short, warm closing sentence; no question, no new thread to pull.
6. **Send the reply** in the shared thread with the counterpart `@mention` per the
   wake-transport contract.
7. **Report the outcome** to `engram-state-accounting`:
   - `sent:<mode>:open`
   - `sent:<mode>:nudging`
   - `sent:<mode>:closing`
   - `declined:<reason>`
8. Let state-accounting update `session_agent_turn_count`,
   `session_last_agent_mode`, `mode_last_sent.<mode>`, and — on a closing send — set
   `session_wind_down_phase = cooling` and `cooling_until`.

## Interaction with Mode I

Mode I is normally a no-send mode. In the conversation handler it appears only when:

- The cooling lock is active (`skipped:cooling-lock`), or
- The selector narrows to a closing beat that is best expressed as a silent close
  (rare; prefer a warm one-sentence close in the current mode).

When the conversation handler logs `skipped:cooling-lock`, Mode I is effectively the
active mode until `cooling_until` expires.

## Outcome format

State-accounting consumes exactly these outcomes:

- `sent:<mode>:<phase>` — a reply was sent. `<phase>` is `open`, `nudging`, or `closing`.
- `declined:<reason>` — the profile or voice gate refused to send.
- `redaction` — the subject requested redaction; no reply.
- `skipped:cooling-lock` — the cooling lock suppressed a reply.

## Pitfalls

- **Replying during cooling.** The cooling lock is set-once per close; do not override it.
- **Profile-side budget override.** The profile never sees the exchange counter; it only
  receives the narrowed mode guidance.
- **Switching modes mid-session.** The selector must not return a different mode than
  `session_last_agent_mode` during an active session.
- **Writing state directly.** The conversation handler instructs state-accounting; it does
  not edit `engagement_state.json`.

## Verification

- [ ] `engagement_state.json` was read and updated only by `engram-state-accounting`.
- [ ] The cooling lock was respected; `skipped:cooling-lock` logged when active.
- [ ] Mid-session narrowing sustained `session_last_agent_mode`.
- [ ] `nudging` guidance nudged toward a natural close without abruptness.
- [ ] `closing` guidance produced one short, warm final reply.
- [ ] Outcome was reported to state-accounting as `sent:<mode>:<phase>`.
- [ ] `mode_last_sent.<mode>` was updated for every sent reply, including closing beats.
- [ ] No direct `engagement_state.json` write occurred in the conversation handler or mode skill.
