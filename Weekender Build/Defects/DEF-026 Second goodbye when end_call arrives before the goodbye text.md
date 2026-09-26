---
type: defect
date: 2026-09-26
status: fixed
severity: minor
found_in: "[[RUN-016 Relay family task types]]"
owner: claude (relay)
---
# Defect: Second goodbye when end_call arrives before the goodbye text

## Observed
Kita role-play run 2: the agent said "Vielen Dank für die Informationen und den Termin, auf Wiederhören!" and then, four seconds later, "Auf Wiederhören!" again. Both lines were saved (transcript lines 275, 276) and spoken.
Timestamps show why: the event `booking_confirmed` (10:30:51.336) was written before the filler line of the same model turn (10:30:51.391). Deepgram sends the `FunctionCallRequest` **before** the `ConversationText` of the same response. The [[DEF-014 Agent speaks after goodbye]] fix only muted when the goodbye text had already arrived when `end_call` came in.

## Expected
Nothing is spoken or saved after the goodbye.

## Repro
Kita or course role-play; happens when the model writes the goodbye and `end_call` in one response (intermittent: 1 of 3 Kita runs).

## Fix
`server.js`: when an agent line with a goodbye arrives **after** `end_call` was requested, that line is the last one (`muteAfterEnd = true`); later lines are dropped and later audio is muted after `AgentAudioDone`.
Verified: Kita run 3, relay log "dropped post-goodbye line", only one goodbye in the transcript.

## Verification (RUN-016)
Independent check: one goodbye in all 8 voice runs; the relay log showed "dropped post-goodbye line" in course run 2 and Kita run 1.
