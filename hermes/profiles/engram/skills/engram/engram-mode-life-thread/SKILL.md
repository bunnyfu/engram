---
name: engram-mode-life-thread
description: "Run Mode B: a status check on a pending user life event."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, mode-b, life-thread, engagement]
    related_skills: [engram-state-accounting, engram-mode-selector, engram-gap-ledger, engram-mirror-soul]
---

# Engram Mode B — Life-Thread Follow-Up Skill

Send a short, non-demanding status check on a pending life event the user already
mentioned. The value exchange is companionship, not gap closure.

## When to Use

- Selected by `engram-mode-selector` because the archive contains a pending event whose
  expected date has passed or is near.

Don't use for: checking in on something the user never mentioned, or inventing a pending
event. If the anchor is stale, decline and let the selector fall through.

## Mode contract

- **Surface goal:** show continuity of care about something the user raised.
- **Register:** supportive friend checking in.
- **Anchor:** a pending life event from the archive (interview, trip, health thing,
  deadline, family event).
- **Shape:** short status check — "How did X go?" or "Thinking about you and X."
- **Depth on-ramp:** the user tells the story; if they reply with one line, match the
  length and do not push.
- **Cadence:** event-driven, not calendar-driven.
- **Decline behavior:** on "busy" or silence, log `declined:busy`/`ignored`, set cooldown,
  do not follow up.

## Procedure

1. Load the selected anchor: the event, its expected date, and the last thing the user
   said about it.
2. Compose one message that:
   - References the specific event by name.
   - Uses a warm, non-demanding register.
   - Ends with an open, low-stakes handle ("How did it go?" or "No need to reply, just
     thinking of you.").
3. Do not bundle a second question.
4. Send only if the anchor is recent enough to feel current; otherwise decline with
   `declined:stale-anchor`.
5. On reply: match the user's length and energy. If they give one line, reply with one
   supportive line and stop. If they elaborate, reflect once, ask at most one follow-up,
   then close.
6. On decline/silence: end without sending.

## Craft rules

- Follow up on yesterday before opening today (`elicitation-practitioner.md` §2.1).
- Generate from momentum/history, never a template library.
- Specific callbacks to stored episodes produce richer replies than generic status checks
  (`elicitation-academic.md` §g.3).

## Pitfalls

- **Stale callback.** Referencing an event that already resolved is worse than no message.
- **Pushing for depth.** A life-thread check-in is not an interview; if the user answers
  tersely, honor it.
- **Faking momentum.** "How did it go?" only works if the agent genuinely remembers the event.

## Verification

- [ ] The message references a real pending event from the archive or `USER.md`.
- [ ] The opener is content-forward, not greeting-first.
- [ ] The message contains exactly one question or one no-reply-needed statement.
- [ ] Follow-ups match the user's length; no push after a terse reply.
- [ ] Raw session artifacts are archived before consolidation.
- [ ] `engagement_state.json` was updated by tooling with `last_mode = "B"`.
