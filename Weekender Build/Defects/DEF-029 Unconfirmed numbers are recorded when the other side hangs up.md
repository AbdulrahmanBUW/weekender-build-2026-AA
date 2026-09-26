---
type: defect
date: 2026-09-26
status: open
severity: minor
found_in: "[[RUN-016 Relay family task types]]"
owner: relay builder
---
# Defect: Unconfirmed numbers are recorded when the other side hangs up

## Observed
Pharmacy regression run 2: the pharmacy said "drei Euro neunundvierzig … abholen bis halb sieben". Speech-to-text heard "Euro drei Komma neun … bis halt sieben". The agent's read-back question was answered only with "Gerne, auf Wiederhören", and `record_result` still saved `price_eur: 3.9` and `pickup_until: "19:00"` (true: 3.49 / 18:30); the user summary says "until 7 PM". Run 1 also saved 3.9. The STT slip on prices is known from [[RUN-014 Relay v2 generic tasks]]; the new part is that numbers are stored as facts although the read-back was never confirmed.

## Expected
When the summary/read-back was not confirmed, uncertain numbers are either left out or the result is marked as unconfirmed, and the user sees "please double-check".

## Repro
`node roleplay-pharmacy.js <pharmacy task>` (the script ends the call on the agent's read-back).

## Fix
Proposed, not built: add `confirmed: boolean` to `record_result` (true only after an explicit "Ja/Richtig" to the summary), store it in `calls.result`, and let n8n 06 / the result card add "not confirmed on the phone — please check" when it is false. Optionally add German number/time keyterms ("halb", "Euro") for nova-3.
