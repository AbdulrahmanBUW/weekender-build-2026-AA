---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[RUN-016 Relay family task types]]"
owner: claude (relay)
---
# Defect: Silence after the read-back while the booking is written

## Observed
Course role-play run 1: after the receptionist confirmed the read-back ("Ja, richtig …") there were **11.6 s** of silence before the agent's goodbye; Kita run 1: **7.95 s**. On a real phone line the other side says "Hallo?" or hangs up.
The closing turn is: one LLM turn that writes `confirm_booking` with a large `details` object → three DB writes one after the other → a second LLM turn for the goodbye. Nothing is spoken until the second turn.

## Expected
The other side hears something within ~2–4 s, like after any other turn.

## Repro
`node roleplay-course.js <course task>` on the code before the fix; watch the `(latency …)` after the confirming line.

## Fix
- Course/Kita rules: after the confirmed read-back the agent says "Wunderbar, ich notiere das." and calls `confirm_booking` in the same turn (the text is spoken while the function runs).
- `server.js`: the independent DB writes of `confirm_booking` / `record_result` run in parallel; each function call is logged with its duration (now 150–220 ms).
Verified: course runs 2–4 and Kita runs 2–3: first audio 3.4–4.6 s after the confirmation.
Still open: the other task types (doctor, restaurant, authority …) have no filler yet — add it globally after a doctor regression run.

## Verification (RUN-016)
- Booking path holds: course runs 2–3 and Kita runs 1–2 of the independent check spoke "Wunderbar, ich notiere das." 3.2–4.4 s after the confirmation.
- Same silence on the `record_result` path (curveball runs 1–3): 6.5–6.9 s after "Ja, genau, das stimmt." before the goodbye. A filler rule in the course/Kita templates alone was ignored. Fixed for course/Kita in the `server.js` result rule ("sag dann nur "Danke, ich notiere das." und rufe im selben Zug record_result auf"); curveball run 4: filler after 4.2 s. Other task types still have no filler (see Fix above).
