---
type: defect
date: 2026-09-26
status: open
severity: minor
found_in: "[[RUN-023 Merged flow E2E]]"
owner: abdul (n8n 04)
---
# Defect: Intake asks for the child's first name

## Observed
Live intake (workflow 04, `POST /webhook/task-intake`, 26 Sep ~13:45) with a Russian parent text and a prefill for a real course row (Musikschule Adagio Dresden): the draft was correct (`course_enquiry`, organisation and `resource_id` kept from the prefill, `child_age` "4 Jahre", both windows, `ready: true`). But `missing` held one question: `{"field": "child_first_name", "question_user": "Какое имя у вашей дочки?"}` ("What is your daughter's name?").

The 04 prompt says: "the child's first name only if the user gives it (fact child_first_name; **never ask for it**)". Haiku asked anyway, and *Validate + Clean Draft* does not filter it. Seen in 1 of 1 runs (only one run, to save credits).

## Expected
Intake never asks for the child's name. A trial-lesson or Kita enquiry does not need it, and the spec shares it only if the parent volunteers it ([[Data minimisation - no symptoms]], shared task spec in [[Task Types - How to extend]]).

## Repro
POST to `/webhook/task-intake` with Origin `http://localhost:8787`, `ui_language: "ru"`, text "Меня зовут Мария Иванова. Моей дочке 4 года, хочу узнать, есть ли место или пробное занятие. Нам удобно во вторник 29.09 и в четверг 01.10 с 15 до 18 часов." and `prefill: {task_type: "course_enquiry", organisation: {name, phone, category: "course", resource_id}}`.

## Fix
Proposed (not applied; integration run, n8n owner decides):
- **04 *Validate + Clean Draft*:** drop every `missing` entry whose `field` is `child_first_name` (also `child_name`, `child_dob`) before responding. Deterministic, no extra Claude call.
- **Frontend until then:** while `ready: true`, the intake screen must treat every `missing` question as optional (same rule as the optional `time_windows` question in [[RUN-015 Family task types in n8n]]) and show a visible "Skip" for this one.
