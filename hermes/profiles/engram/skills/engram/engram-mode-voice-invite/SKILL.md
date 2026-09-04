---
name: engram-mode-voice-invite
description: "Run Mode F: invite the user to send a voice memo."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [engram, mode-f, voice, engagement]
    related_skills: [engram-state-accounting, engram-mode-selector, engram-mirror-soul]
---

# Engram Mode F — Voice-Memo Invitation Skill

Invite the user to talk rather than type. Voice memos are high-fidelity raw material,
but the invitation must never feel surveilled.

## When to Use

- Selected by `engram-mode-selector` on a weekly-max cadence when a recent event or a
  broad open topic gives the user something light to talk about.

Don't use for: daily invitations, or framing the memo as "record for the archive."

## Mode contract

- **Surface goal:** invite the user to talk rather than type.
- **Register:** intimate, low-effort.
- **Anchor:** a recent event or a broad open topic the user cares about.
- **Shape:** Event-anchored invitation: "The [topic] you mentioned yesterday made me
  want to hear your take — send a note if you feel like it, no pressure."
- **Depth on-ramp:** user sends a voice memo; agent transcribes and archives verbatim,
  then may send a short acknowledgment.
- **Cadence:** weekly at most.
- The exact cadence is enforced by the selector using `mode_last_sent`; the
  profile does not judge timing.
- **Decline behavior:** silence is fine; no reminder.

## Procedure

1. Load the anchor: a recent event or a light topic from the archive.
2. Compose one message that:
   - Anchors the invitation to a specific recent event or topic from the archive.
   - Suggests one specific, light topic they can riff on.
   - Explicitly permits "or anything" so it is not a quiz.
   - Never uses affection stock phrases like "I miss hearing your voice."
3. Send and stop. Do not ask for a reply.
4. On voice memo: archive raw audio first, transcribe after, send a short acknowledgment
   (not a summary), then stop.

## Craft rules

- Voice warmth lives in the words, not the TTS (`elicitation-practitioner.md` §1.1).
- Bound the vulnerability: explicit exit, no pressure (`elicitation-academic.md` §b.3).

## Pitfalls

- **Affection stock phrases.** "I miss hearing your voice" is prohibited; anchor to a real event.
- **Surveillance framing.** "Record a memo for the archive" is prohibited.
- **Pressure.** "I'd love to hear your voice" can feel needy if overused.
- **Ignoring the archive.** The topic must come from real user history.

## Verification

- [ ] The invitation is anchored to a specific, light topic or recent event.
- [ ] The message does not frame the memo as archival capture.
- [ ] No reply was demanded.
- [ ] Raw voice memo was archived before transcription.
- [ ] `engagement_state.json` was updated by tooling with `last_mode = "F"`.
