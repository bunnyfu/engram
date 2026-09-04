# Cron: Engram Conversation Handler actuator

Triggered by the `conversation-handler` director when an active, non-cooling session has
an unanswered subject artifact. The director decision (mode, phase, subject artifact) is
injected above via `actuator-conversation` script stdout. Use it directly. You have no
tool access — do not call any tools.

## Steps

1. Read the director decision above.
2. Draft one reply matching the phase: `open` (normal), `nudging` (natural landing, no
   continuation invite), or `closing` (one short, warm final sentence).
3. Your final response below is the message to send. It will be delivered to the MIKOSHI
   channel (`11q5an3haffxfpo6kfradxp75y`), @mentioning the counterpart (`caleb`).
4. After the message, on a new line output exactly: `sent:<mode>:<phase>` or
   `declined:<reason>`.
5. Do NOT edit `engagement_state.json` directly; the director will apply state updates.

## Output

- The message text as your final response (this is what gets delivered).
- One outcome line starting with `sent:` or `declined:`.
