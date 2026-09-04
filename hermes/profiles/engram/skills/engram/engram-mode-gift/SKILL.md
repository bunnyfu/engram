---
name: engram-mode-gift
description: "Run Mode E: share an archive-anchored quote or idea."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, mode-e, gift, share, engagement]
    related_skills: [engram-state-accounting, engram-mode-selector, engram-mirror-soul]
---

# Engram Mode E — Gift / Share Loop Skill

Share something resonant from the user's corpus or a locally cached source, with
one-line personal framing. Never content marketing.

## When to Use

- Selected by `engram-mode-selector` when the archive contains a strong anchor to the
  user's interests, goals, or current projects.

Don't use for: filler pings or gifts with no real referent. If nothing strong exists,
decline with `declined:weak-anchor`.

## Mode contract

- **Surface goal:** give the user something useful or resonant.
- **Register:** generous, thoughtful friend.
- **Anchor:** the user's interests, goals, or current projects.
- **Shape:** share a locally cached quote, passage, image, or idea with one-line
  personal framing.
- **Depth on-ramp:** user reacts; agent can ask one follow-up only if the user opens
  the door.
- **Cadence:** infrequent — weekly or less.
- The exact cadence is enforced by the selector using `mode_last_sent`; the
  profile does not judge timing.
- **Decline behavior:** skip if no strong anchor exists.

## Procedure

1. Load the anchor: a topic, interest, or project from `USER.md` or archive.
2. Select a shareable item:
   - A verbatim quote the user has shared (from archive).
   - A locally cached quote/idea tied to the anchor (no live fetches).
3. Compose one message with:
   - The item itself (short).
   - One line of personal framing connecting it to the user.
   - An optional open handle ("made me think of you").
4. Do not ask a direct question.
5. On reply: respond warmly; ask at most one follow-up if the user opens the door.

## Craft rules

- Proactive messages must be content-forward — deliver something, don't just request
  attention (`elicitation-practitioner.md` §2.1).
- Every proactive ping must pass a relevance test against known history/state
  (`elicitation-practitioner.md` §3).

## Pitfalls

- **Content marketing.** A generic "here's an inspiring quote" feels like a newsletter.
- **Live fetches.** The local-only boundary forbids external fetches.
- **Demanding reaction.** "What do you think?" turns a gift into a quiz.

## Verification

- [ ] The shared item is anchored to a real user interest or project.
- [ ] The item comes from the archive or a locally cached source.
- [ ] The message contains at most one open handle; no direct question.
- [ ] Raw session artifacts are archived before consolidation.
- [ ] `engagement_state.json` was updated by tooling with `last_mode = "E"`.
