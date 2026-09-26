---
type: defect
date: 2026-09-26
status: fixed
severity: minor
found_in: "[[RUN-012 Automated receptionist role-play]], [[RUN-014 Relay v2 generic tasks]]"
owner: claude
---
# Defect: Agent speaks after goodbye

## Observed
After the goodbye and `end_call`, the model adds a line: "(Anruf beendet)" in RUN-012, "Termin erfolgreich vereinbart – vielen Dank!" in RUN-014. It is spoken and saved to the transcript.

## Expected
The goodbye is the last thing said. No stage directions.

## Repro
`node roleplay-test.js <doctor task>` → the last agent line comes after `relay: ending`.

## Fix
`services/voice-relay/server.js`: prompt rule "never bracketed stage directions, say nothing after the goodbye"; `(…)`, `[…]` and `*…*` are stripped before a line is shown or saved; if the last agent line was a goodbye when `end_call` arrives, later agent text is dropped and audio is muted after the goodbye audio; the `end_call` response says "Gespräch beendet. Sag nichts mehr." Verified in RUN-014 (0 bracketed lines saved).
