---
name: engram-mode-reminiscence
description: "Run Mode C: an artifact-anchored invitation to reminisce."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, mode-c, reminiscence, engagement]
    related_skills: [engram-state-accounting, engram-mode-selector, engram-mirror-soul, engram-gap-ledger]
---

# Engram Mode C — Reminiscence Trigger Skill

Invite the user to reflect on a past moment using a concrete artifact as a cue. The goal
is a reflective moment, not a factual extraction.

## When to Use

- Selected by `engram-mode-selector` because a strong object/photo/music/date/season
  anchor exists in the archive.

Don't use for: generic nostalgia ("remember the good old days?") or reminiscence about
something not anchored to a stored artifact.

## Mode contract

- **Surface goal:** invite a reflective moment.
- **Register:** nostalgic, reflective, gentle.
- **Anchor:** an object, place, song, photo, season, or date from the archive.
- **Shape:** "This [photo/song/weather/anniversary] made me think of that time you…"
  followed by an open invitation, not a question.
- **Depth on-ramp:** the user tells the story; the agent listens and mirrors, then stops.
- **Cadence:** low — once every few days at most, only with a strong anchor.
- The exact cadence is enforced by the selector using `mode_last_sent`; the
  profile does not judge timing.
- **Decline behavior:** on silence, log and back off; do not re-prompt.

## Procedure

1. Load the anchor artifact and any related `USER.md` entries.
2. Compose a message that:
   - Names the concrete cue (photo, song, date, object, season).
   - Connects it to one stored memory.
   - Ends with an open invitation, not a direct question.
3. Do not ask for a specific list or structured response.
4. On reply: reflect the feeling or detail the user shared; ask at most one gentle
   follow-up if the user leans in; otherwise stop.
5. On silence: end without a follow-up.

## Craft rules

- Tangible prompts (objects, photos, music) bypass effortful search and reactivate
  episodic detail (`elicitation-academic.md` §d.1).
- Aim reminiscence at the reminiscence bump (ages ~10–30) when supported by the archive
  (`elicitation-academic.md` §d.4).
- Frame reminiscence as an opt-in ritual, not an ambush (`elicitation-academic.md`
  §d.2).

## Pitfalls

- **Generic nostalgia.** "Remember when we were younger?" is not an artifact-anchored cue.
- **Interrogating the memory.** "What exactly happened next?" turns reflection into
  deposition.
- **Over-sharing.** The agent should not invent details about the memory.

## Verification

- [ ] The message names a concrete artifact from the archive.
- [ ] The opener is an open invitation, not a direct question.
- [ ] No more than one follow-up was sent, and only if the user leaned in.
- [ ] Raw session artifacts are archived before consolidation.
- [ ] `engagement_state.json` was updated by tooling with `last_mode = "C"`.
