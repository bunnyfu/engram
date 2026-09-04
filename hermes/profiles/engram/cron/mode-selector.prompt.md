# Cron: Engram Mode Selector

## Load these skills first

- `skill_view(name='engram-engagement-repertoire')`
- `skill_view(name='engram-engagement-engine')`
- `skill_view(name='fleet-governance')`

## Stop conditions (exit silently if any is true)

1. `engagement_state.json` cannot be read or is malformed → log error.
2. `passive_mode == true`
3. `now <= redaction_cooldown_until`
4. An agent-initiated contact occurred in the past 24 hours (`last_contact_ts` within rolling window)
5. Active session detected within the configured recency threshold
6. `now <= cooling_until` (Mode I cooling lock is still active)

## Steps

1. Run pre-wake accounting (engine):
   - Query the archive/thread for subject artifacts newer than `last_user_contact_ts`.
   - If found: set `last_user_contact_ts = now`, `ignored_count = 0`, `passive_mode = false`,
     persist `engagement_state.json`.
   - The engine also updates session budget and wind-down phase fields.
2. Run the five cap checks in order.
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
9. If still no send-mode: select Mode I and log `silence:<reason>`.
10. If a send-mode is selected: execute the selected mode per the mode-execution prompt as
    a fragment (do not run it as a separate cron; Mode A keeps its dedicated tool-less
    actuator, `interview-probe`). Pass the selected anchor and `engagement_state.json`
    context. The mode execution returns an outcome.
11. Have the engine update `engagement_state.json` based on the outcome:
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
- Updated `engagement_state.json` only when a send or state transition occurred.
