---
name: engram-mode-silence
description: "Run Mode I: send nothing when no anchor is strong."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, mode-i, silence, engagement]
    related_skills: [engram-state-accounting, engram-mode-selector, engram-conversation-handler]
---

# Engram Mode I — Silence / No-Send Skill

The default mode: do not initiate contact. Silence preserves relationship capital and
prevents the user from feeling pinged.

## When to Use

- Selected by `engram-mode-selector` when no mode (A–H) has a strong enough anchor, or
  when caps would be violated, or when `mode_history` variety cannot be satisfied.

Don't use for: avoiding contact because crafting a message is hard. If a strong anchor
exists, the selector should pick a real mode.

## Mode contract

- **Surface goal:** preserve relationship capital.
- **Register:** none.
- **Anchor:** none.
- **Shape:** no message is sent.
- **Depth on-ramp:** n/a.
- **Cadence:** any time the tooling decides conditions are not right.
- **Decline behavior:** n/a — silence is the outcome.

## Procedure

1. The selector decides Mode I.
2. The cron logs the reason (e.g., `silence:no-strong-anchor`, `silence:caps-block`,
   `silence:mode-history-variety`).
3. No profile is woken.
4. No `ignored_count` or `passive_mode` change occurs.
5. The selector logs the silence reason and touches no state.

## Cooling lock

When the conversation handler reports `sent:<mode>:closing`, state-accounting enters the
Mode I cooling lock: `session_wind_down_phase = cooling` and
`cooling_until = now + cooling_window_minutes`. During the lock:

- The conversation handler does **not** reply to subject artifacts in the same thread.
- The selector cron does **not** open a new agent-initiated contact until
  `now > cooling_until`.
- Mode I is effectively the active mode; log `skipped:cooling-lock` when the handler
  suppresses a reply because of it.
- No `mode_last_sent.I` update occurs; the closing mode's `mode_last_sent` carries the
  wind-down cadence signal.

The cooling lock is set-once per close and mirrors the `avoidance_named` set-once pattern:
once entered, it persists until its configured expiry.

## Craft rules

- "Nothing to say" beats quota (`elicitation-practitioner.md` §3).
- A send without a strong anchor is itself a `cadence-pressure` judge defect
  (`TEST-PLAN.md` §B.6).

## Pitfalls

- **Treating silence as failure.** It is a first-class outcome.
- **Logging nothing.** Mode I must still leave a tooling record for the judge.
- **Touching state.** Mode I must not update `last_contact_ts`, `last_mode`,
  `mode_history`, or `mode_last_sent`.
- **Using silence to avoid effort.** The selector must honestly evaluate anchors.

## Verification

- [ ] The reason for silence is logged.
- [ ] No profile was woken for a selector-cron Mode I decision.
- [ ] `engagement_state.json` was not advanced as if a contact occurred.
- [ ] `ignored_count` and `passive_mode` were unchanged.
- [ ] Cooling-lock skips were logged as `skipped:cooling-lock` and did not wake the profile.
- [ ] `mode_last_sent.I` was not updated during a cooling lock.
