---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[RUN-015 Family task types in n8n]]"
owner: claude
---
# Defect: Intake ignores frontend answer and language field names

## Observed
The Lovable prompts in [[Frontend and UX Plan v2]] (P3/P4) send `answers: [{field, value}]`, `ui_language` / `user_language` and `hint_task_type`. Workflow 04 *Check Origin + Size* only read `answer`, `ui_lang` and ignored the hint. Round-2 answers would reach Claude as empty strings, so the clarifying round could never fill a missing field, and the UI language fell back to `en`.

## Expected
Answers from the question round are merged into the draft; the UI language is respected.

## Repro
POST `/webhook/task-intake` with `{text: "", draft: <draft>, answers: [{field: "time_windows", value: "Tuesday 29.09, 10-12"}]}` → before the fix `answer` was `""`.

## Fix
*Check Origin + Size* accepts `answer` or `value`, `ui_lang` or `ui_language`, and passes `hint_task_type` (soft hint) and `prefill` to the prompt. Verified: Ukrainian Kita round 2 with `{field, value}` produced the visit window 2026-09-29 10:00–12:00 and `ready: true`.
