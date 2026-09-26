---
type: defect
date: 2026-09-26
status: fixed
severity: minor
found_in: "[[RUN-014 Relay v2 generic tasks]]"
owner: claude
---
# Defect: end_call summary overwrites record_result summary

## Observed
`calls.summary_en` ended up as "Confirmed availability, price, pickup time … then said goodbye." instead of the summary from `record_result` that gives the actual answer.

## Expected
The user sees the answer ("Ibuprofen 400 is in stock at 3.49 EUR, pickup until 18:30").

## Fix
`server.js`: `end_call` only writes `summary_en` if `record_result` didn't already set one. Verified in run 3.
