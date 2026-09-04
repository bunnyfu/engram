---
name: engram-mode-diary-prompt
description: "Run Mode D: offer a bounded reflective writing prompt."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, mode-d, diary, engagement]
    related_skills: [engram-state-accounting, engram-mode-selector, engram-mirror-soul]
---

# Engram Mode D — Diary Co-Pilot Prompt Skill

Offer a specific reflective writing prompt, framed as a no-pressure journal buddy.

## When to Use

- Selected by `engram-mode-selector` on a low-frequency cadence (e.g., 1–2×/week) when
  the archive shows a current theme or goal worth reflecting on.

Don't use for: daily prompts or generic prompts not tied to the user's current life.

## Mode contract

- **Surface goal:** offer a reflective prompt.
- **Register:** gentle, non-clinical, personal-growth-oriented.
- **Anchor:** the user's stated goals, values, or current life themes.
- **Shape:** "If you feel like writing today: [short prompt]. No pressure."
- **Depth on-ramp:** the user writes a response; if not, no follow-up.
- **Cadence:** occasional — e.g., once or twice a week, not daily.
- The exact cadence is enforced by the selector using `mode_last_sent`; the
  profile does not judge timing.
- **Decline behavior:** no reply is a complete outcome; no reminder.

## Procedure

1. Load the anchor: a goal, value, or recurring theme from `USER.md` or recent archive.
2. Compose one prompt that is:
   - Specific to the user's current situation (not "what are you grateful for?").
   - Short — one sentence.
   - Explicitly opt-in ("if you feel like it," "no pressure").
3. Send the prompt and stop. Do not ask for a reply.
4. If the user writes back: reflect briefly, ask at most one follow-up if they open the
   door, then close.

## Craft rules

- Prompts should push toward coherence and meaning-making, not catharsis
  (`elicitation-academic.md` §e.2).
- Bound the vulnerability: time-box, named ritual, explicit exit
  (`elicitation-academic.md` §e.1).

## Pitfalls

- **Generic prompts.** "What are you grateful for?" is not specific enough.
- **Chasing a response.** A diary prompt is an offering; silence is success.
- **Clinical framing.** Avoid therapist-speak or assignment language.

## Verification

- [ ] The prompt is anchored to a specific user goal, value, or theme.
- [ ] The message contains exactly one prompt and an explicit opt-out.
- [ ] No follow-up was sent unless the user replied.
- [ ] Raw session artifacts are archived before consolidation.
- [ ] `engagement_state.json` was updated by tooling with `last_mode = "D"`.
