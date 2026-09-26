---
type: defect
date: 2026-09-26
status: fixed
severity: minor
found_in: "[[RUN-015 Family task types in n8n]]"
owner: claude
---
# Defect: Start month spoken as 2027-01

## Observed
The Kita brief listed `- Gewünschter Startzeitpunkt: 2027-01` (the intake stored the fact as `YYYY-MM`). The voice agent would read "zweitausendsiebenundzwanzig minus null eins", and the approval card showed the raw value.

## Expected
"Januar 2027".

## Fix
- 04 prompt asks for the German month name ("Januar 2027"); *Validate + Clean Draft* converts any `YYYY-MM` `start_month` fact to the German month name.
- 01 *Prepare Task Brief* also converts `start_month` / `from_month` facts when writing FAKTEN (old rows).
Verified: a new Kita task with the old `2027-01` fact was briefed with "Gewünschter Startzeitpunkt: Januar 2027" (7.9 s); a fresh intake returns "Januar 2027".
