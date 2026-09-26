---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[RUN-015 Family task types in n8n]]"
owner: claude
---
# Defect: Intake invents a time window

## Observed
Ukrainian Kita request "Can we come and see the Kita?" (no day or time given) → the draft contained `time_windows: [{date: "2026-10-03", from: "10:00", to: "12:00"}]` (a Saturday and a public holiday) **and** a question asking when the parent can come, with `ready: true`. The assistant could have agreed to a visit the parent never approved.

## Expected
No window unless the user mentioned a day/time; ask instead (field `time_windows`).

## Repro
POST the `b_uk_kita` body from [[RUN-015 Family task types in n8n]] to `/webhook/task-intake` on the version before the fix.

## Fix
- Prompt rule: turn every day/time the user mentions into windows, never add one the user did not mention; otherwise leave empty and ask.
- Guard in *Validate + Clean Draft*: if the model asks for `time_windows` in `missing`, any windows it returned are dropped (they were invented).
Verified: the same text now returns `time_windows: []` + a Ukrainian question; "Tuesdays or Thursdays after 16:00" still becomes 29.09 / 01.10 / 06.10 16:00–19:00.
