# Project Engram — Vision & Founding Charter

**Status:** Draft v1 (2026-08-27) — founded by user command, routed by nexus.
**Owner:** the founding user (L0). Router: nexus. Profile-to-be: `engram`.

## Mission

Build a local-first "digital engram": a Hermes agent whose engagements with its user
continuously produce (a) a consolidated peer-model of the user and (b) a permanent raw
corpus of the user's expressions, such that the system can serve two deliverables:

1. **Primary — the informed companion.** A coach/psychologist/trainer that knows the
   user's life, beliefs, habits, goals, and history, and uses that knowledge to help
   the user grow and overcome obstacles.
2. **Secondary — the digital likeness.** A posthumous digital copy that can mimic the
   user's voice, style, tone, thought process, preferences, and worldview for relatives.

The user is a *knowing, disciplined subject*. This is not covert profiling: the user
approaches Engram like a 21st-century diary — pouring heart and soul into an agent
harness instead of a paper journal. The machinery exists to survive the inevitable
mid-way habit drop: when the user goes quiet, the agent becomes a proactive researcher.

## Core architectural decisions

1. **The raw archive is the deliverable; everything else is derived and rebuildable.**
   A LoRA can be retrained any time from the corpus; a 2026 voice memo cannot be
   recaptured in 2030. The archive is append-only, modality-tagged (text/audio/image),
   timestamped, verbatim. Consolidated memory is never the only copy of anything —
   summaries lossy-compress exactly the idiosyncrasies the likeness layer needs.

2. **Single memory backend: Hindsight only.** Engram runs exactly one derived-memory store.
   The peer model and the world/experience knowledge are the same data here — all of
   it is *about the user* — so one store owns it. Whatever Hindsight's representation
   doesn't hold, lives in the raw archive and the exemplar-anchored `USER.md` (files),
   not in a second memory system. Hindsight is the standard memory backend across all
   Hermes profiles; persona mapping is steered through bank mission directives
   (retain/reflect prompt tuning) rather than schema differences. 

3. **Two data feeds.**
   - **User-initiated:** every engagement is a profiling opportunity. Chat text, voice
     memos (archived raw for future voice cloning + transcribed for the text corpus),
     shared photos/documents — all ingested, all archived.
   - **Agent-initiated:** the nightly dream-phase cron (relationship-stage
     re-checkpoint, gap-ledger consolidation, mirror update) plus the daily
     proactive-engagement cron (contact-window fire — see §Mechanics), which
     delivers gentle, curiosity-driven contact per the repertoire (see
     §Interview engine).

4. **Mirror-SOUL.** A living `USER.md` — a SOUL.md *of the user* — maintained by the
   consolidation loop (Letta human/persona-block pattern, generalized). Every entry is
   **exemplar-anchored**: style/belief entries carry verbatim quotes from the archive,
   not paraphrases. (Academic finding: unanchored persona descriptions collapse into
   generic behavior — "persona collapse", arXiv 2604.24698.)

5. **Mimicry is a disposable derived layer.** Periodic LoRA/QLoRA on the corpus
   (WeClone-class pipeline: 5k–50k quality pairs, 12–24GB VRAM) supplies voice/style;
   the memory system supplies facts and biography. Neither alone is sufficient —
   established independently by the academic, practitioner, and alt-tech research
   spokes. Voice cloning (XTTS v2 / F5-TTS / GPT-SoVITS) is a solved sub-problem
   needing seconds-to-minutes of raw audio — hence the voice-memo archive rule.

6. **Local-only, forever.** Project December died when OpenAI revoked API access; for a
   posthumous artifact, platform dependence is the worst failure mode. All capture,
   storage, and inference paths must run on owned hardware. (the $5–10k hardware
   estimate is conservative for everything except the largest fine-tunes.)

## Agent-initiated engagement repertoire

The agent-initiated feed is **not** one find-gap→interview loop — a single loop is
experientially thin: extractive fatigue, predictability, goal misalignment. It is a
round-robin repertoire of engagement modes that hide the probing goal inside genuine
friendly contact, each with a shallow exit and depth only if the user leans in.

**Shared hard constraints (every mode):** tooling caps are supreme — at most one
agent-initiated contact per rolling 24 hours (never calendar-"today"), none during
an active session,
`passive_mode`/`redaction_cooldown_until` honored. No templated openers — modes define
constraint contracts (tone, anchor, shape), never scripts. Voice gate applies to
every mode. Depth is user-led. Any "busy"/silence → metadata-only log, cooldown,
exponential backoff. **Silence is a first-class outcome, not a failure.**

**Relationship stage model (the inverted RPG).** The engine continuously assesses
where the relationship actually stands — an inverted RPG where the system tracks
its own progress with the subject instead of the player's. Ladder: `unknown →
hostile | unfriendly | neutral | friendly | confidant`; `unknown` = cold start
(no verified subject data, depth permission zero). Depth is a derived permission,
not an assumption: mode eligibility is stage-gated (at `unknown`, no
history-anchored mode is eligible — the agent starts cold, small talk is the
runway), and past-tense familiarity is banned without a verified anchor: never
fake shared history. Stage transitions are decided by the **dream phase** — the
nightly `dream-phase` cron, an out-of-session review scanning sessions since the
last review, promoting only with citable evidence, demoting fail-closed; the
in-session agent never writes engagement state (single-writer). Gaps close at
rapport peaks: Mode A/J are additionally paced by gap-pressure and rapport-peak
signals, never forced on first contact or every opportunity.
**Promotion velocity is sigmoidal:** promotions are dwell-gated — days at the
rung below, weeks at the higher rungs (→`friendly` ≥3 days at `neutral`,
→`confidant` ≥14 days at `friendly`, tooling-enforced) — while demotions
fail-closed on one strong negative but move at most one rung per night (never
to `hostile` in a single night): volatile-but-realistic, never whiplash.

**Modes:**
- **A. Curiosity callback** — the original interview engine, demoted to *fallback*:
  one warm, archive-anchored question on a high-priority gap; ≤2 follow-ups.
- **B. Life-thread follow-up** — event-driven check-in on a pending life event the
  user mentioned ("How did X go?"); match reply length, never push.
- **C. Reminiscence trigger** — object/photo/music/date-anchored invitation to reflect
  ("This made me think of that time you…"), open invitation, not a question.
- **D. Diary co-pilot** — a specific reflective writing prompt, offered with
  "no pressure"; 1–2×/week max.
- **E. Gift/share loop** — share an archive-anchored quote/idea/passage with one-line
  personal framing; skip entirely if nothing strong exists. Never content marketing.
- **F. Voice-memo invitation** — invite talking over typing; weekly max; never framed
  as "record for the archive."
- **G. Presence/co-working offer** — companionship with no question ("I'm around if
  you want to think out loud about X"); rare, stress-pattern-triggered.
- **H. Celebration/affirmation** — milestone recognition anchored to a real artifact
  and a verbatim quote; no generic positivity.
- **I. Silence/no-send** — the default when no mode has a strong anchor. A send
  without a strong anchor is itself a judge defect (`cadence-pressure`).

**Mode-selection priority (tooling, not LLM whim):** event-driven modes first (B, H,
G) → low-frequency relationship modes (C, F, D, E) by anchor strength with
`mode_history` variety enforced → Mode A only when a high-priority gap exists →
Mode I otherwise.

**Evidence-derived craft rules** (catalogs):
- Open content-forward with a specific callback; never a greeting script.
- Inside conversations: ~2:1 reflections-to-questions (motivational interviewing).
- Breadth-before-depth, graduated intimacy across sessions (mechanized by the
  stage model); never deep on first touch.
- Keep each initiated interaction short — length hurts more than frequency (ESM).
- Aim reminiscence at the reminiscence bump (ages ~10–30) when the archive supports it.
- Banned: stock phrases, greeting resets, duplicate greetings, always-first-and-last
  asymmetry, and the documented engagement-farming dark patterns
  (`elicitation-practitioner.md` §5).
- Evidence quality (scout audit): the catalogs rest on WEIRD-biased studies,
  self-selected community reports, and working papers; no direct RCTs of LLM-companion
  elicitation exist. Treat craft rules as strong priors to be re-derived from Engram's
  own judge/response data, not as settled science.

**Components:**
- **Gap ledger** (`gaps.md`, machine-maintained): open questions about the user. The
  ledger is now a **skeleton + discovered overlay**: a-priori L0–L8 slots exist for every
  subject (see `skills/engram-gap-skeleton/SKILL.md`), and discovered gaps annotate on
  top. Each entry carries `status` (`open|partial|closed|versioned|declined`), `tier`
  (1|2|3), `closability` (`one-shot|story|longitudinal|versioned`), `feeds`
  (`companion|likeness|both`), `source` (`skeleton|discovered:<ref>|contradiction:<ref>`),
  `sensitivity` (`normal|handle-with-care`), `exemplar` (`<archive-ref>|none`),
  `last-touched`, and `decay-after`. Priority is computed deterministically as
  `deliverable-value × anchor-strength × tier-gate × recency-of-attempt`; tier-3 slots
  are hard-gated regardless of raw priority. Skeleton slots are never deleted; `declined`
  is a permanent consent state. The ledger also encodes a special **avoidance-naming**
  mechanic for `handle-with-care` slots with zero corpus mentions over a long window:
  exactly one warm, direct, non-pathologizing probe inside an active conversation; any
  deflection → `status: declined`, permanently. See `skills/engram-gap-skeleton/SKILL.md`
  for taxonomy, schema, formula, and mode routing question (Mode A variant vs. new Mode J).
- **Engagement state** `engagement_state.json` (supersedes `interview_state.json`):
  `last_contact_ts`, `last_mode`, `mode_history` (rolling window, variety enforced),
  the interview fields `last_probe_ts`, `ignored_count`, `passive_mode`,
  `redaction_cooldown_until`, `last_user_contact_ts`, and the relationship-stage
  fields `relationship_stage`, `stage_history` (append-only), and
  `last_stage_review_ts`.
- **Mechanics (unchanged, generalized to all contacts):** caps enforced by cron
  tooling, never profile prose. The engram side runs exactly **two crons**, both
  git-tracked under `hermes/profiles/engram/cron/`:
  - **`dream-phase.prompt.md`** — the nightly dream phase: relationship-stage
    re-checkpoint + gap tick-offs + `USER.md` mirror update in one duty. Runs
    out of session while the subject sleeps and must complete before morning;
    the morning session starts from the new checkpoint
    (`engagement_state.json` + `gaps.md` are otherwise a static checkpoint —
    only the dream phase re-checkpoints them).
  - **`proactive-engagement.prompt.md`** — the daily proactive engagement fire:
    jittered contact window, the full pre-wake gate ladder (caps → passive /
    redaction cooldown → 24h rolling contact window → active session → cooling
    lock → stage gate → anchor verification), mostly resolving to Mode I
    silence (log the reason, touch no state beyond tooling stamps).
  Active-session detection is a deterministic lookup.
  Contacts land in a configured window (e.g. 18:00–22:00 subject-local) with bounded
  jitter (±45 min) applied by the scheduler. Check order: tooling verifies
  `!passive_mode`, `now > redaction_cooldown_until`, no agent-initiated contact in the past
  24 hours (rolling), no active session, `now > cooling_until` (no active Mode I
  cooling lock) — *before* waking the profile. The profile may decline
  (`declined:<reason>`, no `ignored_count` increment); the tooling may not be bypassed.
  Mid-session reply routing is in-session behavior owned by the SOUL + the
  engine/repertoire skills — no cron for it.
- **Stop conditions:** explicit "not now" → respect + cooldown; three consecutive
  ignored contacts → passive mode until next user-initiated contact.

## Operating doctrine (founding directives)

1. **Autonomous testing.** The test phase runs without hand-holding: nexus routes,
   gates fire per TEST-PLAN, the owner receives on-signal digests only. README.md is the
   alignment reference for every tuning decision.
2. **Voice is a tested quality.** Probe voice is curious-friend, never inquisitor or
   police officer. Blunt, gap-closing interrogation is a defect class; testing
   includes a voice criterion and a tuning loop.
3. **Mechanics live in skills, not prose.** Gap-finding, interview-running, and the
   mirror-SOUL are durable Hermes skills (forge-authored) with explicit mechanics:
   schemas, file ownership, lifecycle (how gaps are identified, where tracked, how
   ticked off). Crons inject skills explicitly; cron prompts are tunable artifacts —
   drafted, saved to disk, git-tracked under `hermes/profiles/engram/cron/`.
4. **USER.md is a first-class tested layer.** Its structure, ownership, and update
   mechanics are declared in a dedicated Hermes skill referenced from the Engram
   SOUL; tests cover it at parity with the Hindsight backend.

## Consent & ethics boundary

Self-engram: the user knows and consents intrinsically; the pipeline need not be
surfaced in conversation. But the architecture generalizes to capturing *others*
(building an engram of a parent, the relatives-chat use case). Consent, closure-bounded
sessions, and exportability (lessons from the griefbot market: HereAfter, StoryFile,
Seance AI) are design requirements now, not retrofits.

## Test strategy (draft — Planner to refine)

- **Phase 0 (recon):** RESOLVED (Scout — `scout-session-durability.md`).
  Hermes sessions are durable-with-config (no auto-prune by default, compression
  soft-archives rather than deletes) but deletable — so `state.db` is a convenience
  copy, never the archive. **Export-at-capture stands as the rule.**
- **Phase 1 (synthetic smoke test):** Engram profile + Hindsight on Mattermost; a
  dedicated throwaway test-subject profile engages on a cron. (Elon-as-subject
  rejected: board seats stay read-only per constitution §11, and a
  synthetic subject provides ground truth Elon can't.) The test subject is seeded
  from a **SillyTavern-style character card** pulled from the web — description,
  personality, backstory, speech-style examples, example dialogues. The card IS the
  ground truth: profiling accuracy is scored against it, and its example dialogues
  double as exemplar-anchoring targets for the mirror-SOUL check. Cache the card
  locally with source URL + license recorded (critic YELLOW-3); keep a hand-authored
  offline fallback card in case of takedown or licensing problems.
- **Phase 2 (tuning):** iterate on profiling quality against the growing artifact
  corpus; measure what the mirror-SOUL actually captures.
- **Phase 3 (real user):** move to a private machine; the founding user as subject.

## Research base (five-spoke recon)

Full reports in `research/`: `digital-engram-memory-backends.md`,
`digital-afterlife-landscape.md`, `engram-research.md`, `digital-engram-research.md`,
`digital-likeness-directions.md`. Key bound: Stanford 1,000-person study (arXiv
2411.10109) — a 2-hour structured interview yields ~82–86% of the subject's own
test-retest reliability. That is the realistic fidelity ceiling, and structured
interview data is the highest-value data per minute — the empirical basis for the
interview engine.
