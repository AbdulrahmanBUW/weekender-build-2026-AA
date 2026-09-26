---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[Receptionist Test Scripts]] (script 10, found by QA agent)"
owner: claude
---
# Defect: Silent call never gets an outcome

## Observed
If the receptionist stays silent or hangs up, the relay kept the call open; request stayed `calling`, `calls.outcome` empty.

## Fix
Silence watchdog in `services/voice-relay/server.js`: after the agent finishes speaking, 30 s (`SILENCE_LIMIT_MS`) without practice speech → `calls.outcome = no_answer`, request `failed`, call closed. Verified in [[RUN-009 Voice relay self-test (Deepgram agent)]].
