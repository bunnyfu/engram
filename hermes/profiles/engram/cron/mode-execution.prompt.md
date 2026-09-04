# Cron: Engram Mode Execution (parameterized)

Replaces the former per-mode prompts (Mode B–H stubs, Mode I silence, Mode J
eligibility scanner). The director decision is injected above (`mode`, `phase`,
anchor / selected gap / subject artifact, `reason`). Branch on the injected `mode`.
Mode A is served by its dedicated tool-less actuator (`interview-probe.prompt.md`);
this prompt covers B–H, I, and J.

## Load these skills first

- `skill_view(name='engram-engagement-repertoire')`
- `skill_view(name='engram-engagement-engine')`
- `skill_view(name='fleet-governance')`

## Stop conditions (exit silently if any is true)

1. `engagement_state.json` cannot be read or is malformed → log error.
2. The injected decision is missing or carries no `mode`.
3. The decision records a cap-check or accounting failure → log `skipped:<reason>`
   and exit.

## Branch: send-modes B–H

1. Read the director decision above: `mode`, `phase`, and the anchor (B pending
   event; C artifact cue; D goal/value/theme; E interest/project; F recent
   event/topic; G project/stress pattern; H milestone + verbatim quote).
2. Follow that mode's contract in `engram-engagement-repertoire` exactly —
   register, anchor requirement, shape, follow-up bound. If the anchor is stale or
   weak, return `declined:<reason>`; do not update state.
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

## Branch: Mode I — silence / no-send

1. Log the silence reason:
   - Selector-cron reasons: `silence:no-strong-anchor`, `silence:caps-block`,
     `silence:mode-history-variety`, `silence:voice-gate-failed`,
     `silence:per-mode-cadence`.
   - Conversation-handler cooling-lock suppression: `skipped:cooling-lock`.
2. No message is sent. No profile wake for contact.
3. Do not increment `ignored_count` or change `passive_mode`.
4. Do not append to `mode_history` or update `last_contact_ts`, `last_mode`, or
   `mode_last_sent`.
5. Exit.

## Branch: Mode J — eligibility scanner (no send)

1. Invoke the engine's deterministic Mode J eligibility predicate:
   - A skeleton slot with `sensitivity: handle-with-care`, `status: open|partial`,
     `avoidance_named: null`, tier 1 or 2.
   - Zero corpus mentions of the slot topic over the configured window.
   - Slot not `declined`, `closed`, `versioned`, or `deferred-open`.
2. The engine handles all reads/writes to `engagement_state.json` and `gaps.md` for
   this predicate. This prompt does not touch those files.
3. If the engine reports no eligible slot, log `j_eligible:false` and exit.
4. If the engine reports an eligible slot, it has already written
   `mode_j_eligible` (slot_id, slot, anchor, eligible_since, window_days).
   Do not wake the Engram profile for contact. Do not send a message — the naming
   itself is delivered by the conversation-handler path inside an active warm
   exchange. Log `j_eligible:true slot=<slot_id>`.
5. Exit.

## Output

- Zero or one messages to the subject (send-modes only).
- One cron run log line: timestamp, mode/branch, outcome, and anchor summary.
- `engagement_state.json` updated only by the engine.
