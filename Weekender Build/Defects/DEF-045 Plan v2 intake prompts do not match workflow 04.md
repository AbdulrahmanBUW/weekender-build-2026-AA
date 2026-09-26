---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[RUN-022 UI plan v3 merged]]"
owner: claude
---
# Defect: Plan v2 intake prompts do not match workflow 04

## Observed
The Lovable prompts P3 and P4 in [[Frontend and UX Plan v2]] (not built yet; Lovable has only the P1 shell) describe an intake API that is different from the live n8n workflow 04 "Task intake" (`n8n/workflows/04-task-intake.json`, nodes "Check Origin + Size" and "Validate + Clean Draft"):

| Field | Plan v2 P3/P4 | Workflow 04 (live) |
|---|---|---|
| UI language | `ui_language` | `ui_lang` (anything else → `en`) |
| Answers | `[{field, value}]` | `[{field, answer}]`: `value` is read as `answer ?? ''`, so the answer arrives **empty** |
| Round | not sent | `round` (1–5); otherwise guessed |
| Questions | `missing[{field, question, options?: [{value, label}]}]` | `missing[{field, question_user, options: string[]}]` |
| Doctor fields | nested `draft.doctor.{reason_category, …}` | top level `reason_category`, `is_new_patient`, `has_referral`, `insurance_type`, `insurance_name` |
| Person | `person.{name, dob}` | `person.{name}` only |
| Extra fields | — | `essentials_missing[]`, `ready` |

## Expected
The Lovable prompts use exactly the live contract.

## Repro
Read v2 P3/P4 next to the workflow code. Built as written, P4 would:
1. send clarifying answers that the workflow reads as empty strings, so the questions never get filled;
2. read `d.doctor?.reason_category` → `null` and insert a `doctor_appointment` row without `reason_category` → Postgres `23514` (check `call_requests_doctor_reason`);
3. show `undefined` as the question (`question` instead of `question_user`) and fail on plain-string options.

## Fix
[[Frontend and UX Plan v3 (merged)]] section F.5 documents the exact request and response, and prompts P7/P8 replace v2 P3/P4 (`ui_lang`, `answers[{field, answer}]`, `round`, `question_user`, string options, top-level doctor fields, no `person.dob`). Fixed in the plan; nothing had been built from v2 P3/P4. Do not use v2 P3/P4 any more.

## Update 26 Sep 13:20 (verification, [[RUN-022 UI plan v3 merged]])
A second check of plan v3 against the live workflow 04 (version `de260485…`) found three more contract gaps in P7/P8. All three are now fixed in the plan:
1. P8 picked the age control for any field that contains "age", and `language_preference` contains "age". Now a regex matches only `child_age` / `age`.
2. The server does not copy forgotten essentials into `missing`: `missing` can be empty while `ready = false`. P8 now asks `essentials_missing` itself.
3. The live intake returned a `child_first_name` question although the prompt forbids it. P7/P8 drop it.
The live contract also gained `prefill_invalid` / `prefill_too_large` errors, a top-level `resource_id`, and `value` as a fallback answer key (plan F.5 updated). Status stays fixed.
