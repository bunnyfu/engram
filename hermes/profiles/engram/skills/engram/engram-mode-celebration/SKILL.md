---
name: engram-mode-celebration
description: "Run Mode H: recognize a milestone with a verbatim anchor."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, mode-h, celebration, engagement]
    related_skills: [engram-state-accounting, engram-mode-selector, engram-mirror-soul]
---

# Engram Mode H — Celebration / Affirmation Skill

Recognize a milestone or positive pattern with a verbatim anchor. No generic positivity.

## When to Use

- Selected by `engram-mode-selector` when a milestone the user mentioned has occurred or
  a positive pattern is visible in the archive.

Don't use for: generic "you're great" messages or celebrations not tied to a real
artifact.

## Mode contract

- **Surface goal:** recognize a milestone or pattern.
- **Register:** warm cheerleader, not performative.
- **Anchor:** a milestone the user mentioned or a positive pattern visible in the archive.
- **Shape:** "You did that thing you weren't sure about. I remember when you said [quote]."
- **Depth on-ramp:** user replies with feelings or next steps; agent matches energy and
  stops.
- **Cadence:** event-driven.
- **Decline behavior:** skip if the anchor is stale or invented.

## Procedure

1. Load the anchor: the milestone or pattern and a verbatim quote from the archive.
2. Compose one message:
   - Name the milestone or pattern.
   - Include the verbatim quote as evidence.
   - Keep it short; end with an open handle if appropriate.
3. Send and stop.
4. On reply: match the user's energy; reflect once; stop.

## Craft rules

- Anchors must be real; fabricated anchors are a `fabricated-anchor` judge defect
  (`TEST-PLAN.md` §B.6).
- Affirmation must be anchored to a real artifact; no generic positivity
  (`elicitation-practitioner.md` §5).

## Pitfalls

- **Generic positivity.** "You're amazing" with no anchor is a `template-smell`.
- **Over-celebrating.** Celebration loses meaning if frequent.
- **Wrong mode for the moment.** Celebrating on a stale anchor is `wrong-mode-for-moment`.

## Verification

- [ ] The celebration references a real milestone or pattern from the archive.
- [ ] A verbatim quote from the archive is included.
- [ ] The message is short and anchored, not generic.
- [ ] Raw session artifacts are archived before consolidation.
- [ ] `engagement_state.json` was updated by tooling with `last_mode = "H"`.
