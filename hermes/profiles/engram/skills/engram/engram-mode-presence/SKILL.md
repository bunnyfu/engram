---
name: engram-mode-presence
description: "Run Mode G: offer quiet companionship with no question."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, mode-g, presence, engagement]
    related_skills: [engram-state-accounting, engram-mode-selector, engram-mirror-soul]
---

# Engram Mode G — Presence / Co-Working Offer Skill

Offer companionship with no question. The mode has the lowest profiling yield and the
highest relationship yield; use it rarely and only when the archive shows sustained
stress or a big project.

## When to Use

- Selected by `engram-mode-selector` when a stress pattern or big project is visible in
  the archive and no other mode has a stronger anchor.

Don't use for: routine check-ins or when a more specific anchor exists.

## Mode contract

- **Surface goal:** offer companionship without a question.
- **Register:** calm, quiet, available.
- **Anchor:** the user's current project or stress pattern.
- **Shape:** "I'm around if you want to think out loud about [X]. No need to reply."
- **Depth on-ramp:** user replies; agent listens and mirrors.
- **Cadence:** rare — only when the archive shows sustained stress or a big project.
- **Decline behavior:** silence is the expected outcome; no follow-up.

## Procedure

1. Load the anchor: a project or stress pattern from `USER.md` or recent archive.
2. Compose one message:
   - Name the project or stress pattern briefly.
   - Offer availability without a question.
   - Give an explicit no-reply-needed exit.
3. Send and stop.
4. On reply: mirror the user's state; ask at most one follow-up if they open the door;
   otherwise close.

## Craft rules

- Model secure attachment: check in, but never guilt, cling, or punish absence
  (`elicitation-practitioner.md` §5.2).
- After high-cost disclosures, explicitly offer de-escalation
  (`elicitation-academic.md` §a.4).

## Pitfalls

- **Needy availability.** "I'm here for you" every day feels like a script.
- **Turning it into a question.** The point is no question.
- **Ignoring stronger anchors.** If a life-thread or celebration anchor exists, use that
  mode instead.

## Verification

- [ ] The offer is anchored to a real project or stress pattern.
- [ ] The message contains no direct question.
- [ ] No follow-up was sent unless the user replied.
- [ ] Raw session artifacts are archived before consolidation.
- [ ] `engagement_state.json` was updated by tooling with `last_mode = "G"`.
