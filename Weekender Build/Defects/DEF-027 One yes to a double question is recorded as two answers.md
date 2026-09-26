---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[RUN-016 Relay family task types]]"
owner: claude (relay)
---
# Defect: One yes to a double question is recorded as two answers

## Observed
Pharmacy regression run 1: the agent asked "Ist dafür ein Rezept nötig, und kann ich es gleich auf den Namen … reservieren lassen?" The (scripted) pharmacy answered only "Ja, genau, richtig." The agent recorded `can_reserve: true` and the summary "a prescription is required" — the user would be told that Ibuprofen 400 needs a prescription although nobody said so.
The style rule "eine Frage pro Antwort" was not enough.

## Expected
Never two questions in one sentence. If a single "Ja" comes back anyway, the agent asks what it refers to and records nothing that was not answered on its own.

## Repro
`node roleplay-pharmacy.js <pharmacy task>` — the scripted "Ja, genau, richtig." lands on whatever the agent asked last.

## Fix
New rule in `server.js` (all task types): "Stelle nie zwei Fragen in einem Satz. Kommt trotzdem nur ein "Ja" auf zwei Fragen, frag nach, worauf es sich bezieht; notiere nichts, was nicht einzeln beantwortet wurde."
Verified: pharmacy run 2 — the agent asked "Ist dafür ein Rezept nötig, oder ist es freiverkäuflich?", got "Ja, genau, richtig." and asked back "Entschuldigung, heißt das, dass ein Rezept nötig ist?"; nothing about a prescription was recorded.

## Verification (RUN-016)
The rule is not always followed: course run 3 of the check asked "Wie sehen die Kurszeiten normalerweise aus, und was kostet der Kurs?" and curveball run 4 asked about schedule and price together. The safeguard still worked: only the price was answered, the agent asked again about the schedule (or left it out), and nothing that was not answered was recorded.
