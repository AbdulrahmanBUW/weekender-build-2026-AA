---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[RUN-016 Relay family task types]]"
owner: claude (relay)
---
# Defect: Free spot inferred from a filler or a trial offer

## Observed
Course role-play run 3: the agent asked "Gibt es in Ihrem Musikkurs für Sechsjährige noch einen freien Platz?"; the receptionist said "Ja, gern. Wie alt ist das Kind denn?" (a filler before a counter-question) and later offered a trial lesson. Nobody said a place was free, but `calls.result.free_spot = true`, and n8n 06 told the parent in Russian "В курсе есть свободное место" (there is a free place).
Same class as [[DEF-015 record_result invents answers from a goodbye]], but in `confirm_booking.details`, whose description did not carry the "gerne is not a yes" warning.

## Expected
`free_spot` (course) and `places_available` (Kita) only when the other side said it explicitly; a "Ja, gern" before a counter-question, a trial lesson or a visit do not mean a free place.

## Repro
`node roleplay-course.js <course task>` where the side answer "Ja, in der Gruppe ist gerade noch ein Platz frei." is never triggered.

## Fix
- `task-templates.js`: course rule "free_spot nur, wenn ausdrücklich gesagt … eine angebotene Probestunde heißt NICHT, dass ein Platz frei ist"; Kita rule "Eine mögliche Besichtigung heißt NICHT, dass ein Platz frei ist".
- `server.js`: `confirm_booking.details` description: "'ja, gern' before a counter-question is NOT a yes; … no own conclusions".
Verified: course run 4 — after "Ja, gern. Wie alt …" the agent asked again "Gibt es denn für dieses Alter aktuell einen freien Platz?" and set `free_spot` only after the explicit answer.

## Verification (RUN-016)
Same class, different field: in curveball runs 1 and 2 the agent recorded `waiting_list: false` (and the Ukrainian `summary_user` said "no waiting list") although the waiting list was never answered. In run 1 it was taken from "unter der Woche ist leider alles voll", in run 2 from "Nein, im Moment ist leider kein Platz frei" given in reply to the waiting-list question. The scripted receptionist confirmed the summary, but a real one might not notice the error.
Fix: course rule "waiting_list nur, wenn die Frage nach der Warteliste selbst beantwortet wurde. "Kein Platz frei" … heißt NICHT "keine Warteliste" …"; Kita rule: "kein Platz frei" heißt NICHT "keine Warteliste". Verified: curveball run 4 (`roleplay-curveball.js` answers the first waiting-list question with "kein Platz frei" on purpose) — the agent asked again and recorded `waiting_list: true` only after the real answer. Also seen once: "ihre Tochter Lina" (gender guessed from the first name) — rule added, see RUN-016 Verification V2.
