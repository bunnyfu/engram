# Cron: Engram Proactive Engagement

Daily agent-initiated engagement fire (absorbs the former `mode-selector` and
`mode-execution` crons, folded 2026-09-04; Mode A's former tool-less
`interview-probe` actuator is absorbed too). The scheduler fires it once a day
inside the configurable contact window (default 18:00–22:00 subject-local,
±45 min jitter) — window and jitter are scheduler parameters, never profile
judgment. The director decision may be injected above (`mode`, `phase`,
anchor / selected gap / subject artifact, `reason`); when absent or incomplete,
the steps below derive it.

`engagement_state.json` is a static checkpoint read at fire time: sessions
develop on top of it as hot context, and only the nightly dream phase
re-checkpoints it. Most fires end in Mode I silence — log the reason, touch no
state beyond tooling stamps. Mid-session reply routing is in-session behavior
owned by the SOUL plus the engine/repertoire skills — no cron for it.

## Load these skills first

- `skill_view(name='engram-engagement-engine')`
- `skill_view(name='engram-engagement-repertoire')`
- `skill_view(name='fleet-governance')`

## Stop conditions (exit silently if any is true)

1. `engagement_state.json` cannot be read or is malformed → log error.
2. `passive_mode == true`
3. `now <= redaction_cooldown_until`
4. An agent-initiated contact occurred in the past 24 hours (`last_contact_ts` within rolling window)
5. Active session detected within the configured recency threshold
6. `now <= cooling_until` (Mode I cooling lock is still active)
7. The injected decision records a cap-check or accounting failure → log
   `skipped:<reason>` and exit.

## Selection (engine ladder)

1. Run pre-wake accounting (engine):
   - Query the archive/thread for subject artifacts newer than `last_user_contact_ts`.
   - If found: set `last_user_contact_ts = now`, `ignored_count = 0`,
     `passive_mode = false`, persist `engagement_state.json`.
   - The engine also updates session budget and wind-down phase fields.
2. Run the cap checks in order (1–5 from the engine skill; a failure logs
   `skipped:<reason>` and exits). Then apply the eligibility gates 6–7 — stage
   gate (`min_stage` per mode vs `relationship_stage`; at `unknown` only the
   cold-start set I/G/D/B-on-explicit-user-mentioned-event) and anchor
   verification (gaps.md exemplar / archive-index / recorded derived-store
   recall hit). Gate failures fall through to a lower mode or Mode I — they
   never bail the fire and never authorize an unverified send.
3. If any cap check fails: log `skipped:<reason>` and exit.
4. Evaluate event-driven mode triggers (B, H, G) using the archive and `USER.md`.
   - Event-driven triggers bypass `mode_history` variety.
5. If no event-driven trigger, check `engagement_state.json.pending_revisits` for any entry
   with `revisit_after <= now` and `revisit_sent_at: null`. If one exists, treat it as the
   strongest relationship-mode candidate with its `revisit_channel` (F, D, or G).
6. If no pending revisit, evaluate relationship modes (C, F, D, E):
   - Score each by anchor strength.
   - Apply `mode_history` variety and `mode_last_sent` cadence checks to these four only.
7. Run voice-gate on the top candidate. If it fails, try the next candidate.
8. If no relationship mode passes, check for a high-priority gap for Mode A.
9. If still no send-mode: select Mode I and log `silence:<reason>` (Mode I rules
   below).

## Execution

### Send-modes A–H

1. Read the director decision above: `mode`, `phase`, and the anchor (A selected
   gap; B pending event; C artifact cue; D goal/value/theme; E interest/project;
   F recent event/topic; G project/stress pattern; H milestone + verbatim quote).
2. Follow that mode's contract in `engram-engagement-repertoire` exactly —
   register, anchor requirement, shape, follow-up bound. Mode A keeps the former
   interview-probe actuator rules: the message is a warm, anchored,
   curious-friend opener based on the selected gap — output only the message
   text, no meta-commentary, no tools beyond the send and archive. If the anchor
   is stale or weak, return `declined:<reason>`; do not update state.
3. Draft one message and run the voice gate on it.
4. Send it to the counterpart `@caleb` in the MIKOSHI channel
   (`11q5an3haffxfpo6kfradxp75y`) — your outbound message must @mention the
   counterpart in this thread; an unmentioned reply reaches no one.
5. Archive the raw session verbatim.
6. Return the outcome to the engine:
   - `sent:<mode>:<phase>` + whether the subject responded, was silent, or signaled
     redaction.
   - `declined:<reason>` if the voice gate or anchor check refused the send.
   Never write `engagement_state.json` directly; the engine applies state updates.

### Mode I — silence / no-send

1. Log the silence reason:
   - `silence:no-strong-anchor`, `silence:caps-block`,
     `silence:mode-history-variety`, `silence:voice-gate-failed`,
     `silence:per-mode-cadence`, `silence:stage-gate`, `silence:gap-pacing`,
     `silence:anchor-unverified`.
   - Cooling-lock suppression (stop condition 6): `skipped:cooling-lock`.
2. No message is sent. No profile wake for contact.
3. Do not increment `ignored_count` or change `passive_mode`.
4. Do not append to `mode_history` or update `last_contact_ts`, `last_mode`, or
   `mode_last_sent` (`mode_last_sent.I` is never written).
5. Exit.

### Mode J — eligibility scanner (no send)

1. Invoke the engine's deterministic Mode J eligibility predicate
   (`tools/director_mode_j.py`):
   - A skeleton slot with `sensitivity: handle-with-care`, `status: open|partial`,
     `avoidance_named: null`, tier 1 or 2.
   - Relationship stage ≥ `friendly` (`confidant` preferred; engine stage model).
   - Zero corpus mentions of the slot topic over the configured window.
   - Slot not `declined`, `closed`, `versioned`, or `deferred-open`.
2. The engine handles all reads/writes to `engagement_state.json` and `gaps.md` for
   this predicate. This prompt does not touch those files.
3. If the engine reports no eligible slot, log `j_eligible:false` and exit.
4. If the engine reports an eligible slot, it has already written
   `mode_j_eligible` (slot_id, slot, anchor, eligible_since, window_days).
   Do not wake the Engram profile for contact. Do not send a message — the naming
   itself is delivered in-session inside an active warm exchange. Log
   `j_eligible:true slot=<slot_id>`.
5. Exit.

## State updates (engine-owned)

Have the engine update `engagement_state.json` based on the outcome:

- On send (`sent:<mode>`): `last_contact_ts = now`, `last_mode = <letter>`, append
  letter to `mode_history`, `mode_last_sent.<letter> = now`.
- On Mode A send: also `last_probe_ts = now`.
- On revisit send: have the engine set `revisit_sent_at: now` on the
  matching `pending_revisits` entry.
- On user response: `ignored_count = 0`, `last_user_contact_ts = now`.
- On no response: `ignored_count += 1`; if `>= 3`, `passive_mode = true`.
- On `declined:<reason>`: update `last_contact_ts`, `last_mode`, `mode_history`,
  `mode_last_sent.<letter> = now`, but do **not** increment `ignored_count`.
- On redaction signal: set `redaction_cooldown_until = now + configured_cooldown`.
- On Mode I: do **not** touch `last_contact_ts`, `last_mode`, `mode_history`, or
  `mode_last_sent`.
- Do **not** write `mode_j_eligible`, `pending_revisits`, slot `deferral` records, or
  session wind-down fields. Those are engine-owned.

## Output

- Zero or one messages to the subject.
- One cron run log line: timestamp, selected mode or `silence:<reason>`, outcome, and
  anchor summary.
- Updated `engagement_state.json` only when a send or state transition occurred —
  written by the engine, never this prompt.
