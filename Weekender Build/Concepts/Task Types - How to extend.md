---
type: concept
tags: [tasks, n8n, extensibility]
---
# Task Types - How to extend

**Definition:** A *task type* is the kind of phone call HalloTermin makes (`call_requests.task_type`). Everything type-specific is data (templates and lists), so a new product direction (e.g. after merging Idea B) means editing a few maps, not rebuilding workflows.

**Why it matters for us:** The teammate's Idea B may change what we call about. Adding or renaming a type should take ~15 minutes.

## The 8 types today
| task_type | Mode | May agree to |
|---|---|---|
| doctor_appointment | appointment | slot inside windows, after read-back (reason category, new patient, referral, insurance) |
| authority_appointment | appointment | slot inside windows; else "how to book" info + documents |
| landlord_request | appointment | visit/repair time inside windows; never rent/contract changes |
| contract_question | information | nothing: only how/when/where to cancel. Never cancels or signs by phone |
| bank_enquiry | appointment | slot inside windows or the document list |
| pharmacy_question | information | stock/price/pick-up, reservation; medicine fact allowed (D5.6) |
| restaurant_booking | appointment | table for party_size inside windows |
| other_call | information | information only; appointment only if the user gave windows |

"appointment" types fall back to information mode when no time window is given.

## Where the type logic lives
1. **DB:** check constraint `call_requests_task_type_check` in `supabase/migrations/20260926180100_generic_tasks_multilingual.sql` (doctor-only rule: `call_requests_doctor_reason`).
2. **n8n 01** (peFxjt572HiUxu61), Code node *Prepare Task Brief*: `TASK_TEMPLATES` = `{label_de, mode, needsWindows, purpose_de, may_de, ask_de, never_de}` per type. Doctor extras (reason mapping `REASON_DE`) are in the same node.
3. **n8n 04** (OA51fhbX7NxrVEnW): enum in *Task Draft Schema* (structured output parser), the type list + essentials in the system prompt of *Draft Task (Claude)*, and `ESSENTIALS` in *Validate + Clean Draft*.
4. **Voice relay**: `services/voice-relay/task-templates.js` (`TASK_TEMPLATES`, one object per type: label, mode, purposeDe, goalDe, useDoctorFields); `server.js` `buildAgent` picks the functions (`confirm_booking` for appointment types, `record_result` for information types). See [[RUN-014 Relay v2 generic tasks]].
5. **Frontend:** task chips, per-type form fields and labels in the 12 UI languages.

Workflows 05 (translate line) and 06 (result in user language) are type-agnostic: 06 only maps `outcome` booked → request `booked`, completed → `completed`.

## Steps to add a type (example: `school_enquiry`)
1. New migration: drop + re-add `call_requests_task_type_check` with the new value (`npx supabase migration new add_task_type_school`), push.
2. n8n 01: add a `TASK_TEMPLATES.school_enquiry` entry (German texts, mode). Publish.
3. n8n 04: add the value to the schema enum, one line in the prompt's TASK TYPES list, one `ESSENTIALS` entry. Publish; test with a POST to `/webhook/task-intake` (an allowed `Origin` header is required, e.g. `http://localhost:8787`).
4. Relay: add a `TASK_TEMPLATES.school_enquiry` entry in `services/voice-relay/task-templates.js` (mode decides the functions).
5. Frontend: chip + labels; run one E2E (insert → briefed → call → result).
6. Record it in `Decisions/` and a `Runs/` note.

To remove/rename a type, do the same in reverse; keep old values in the DB check until old rows are migrated.

**Related:** [[Frontend and UX Plan v2]] (D2 essentials table, D5 data minimisation, F6 disclosure), [[Data Model]], [[RUN-013 n8n v2 workflows]], [[n8n - Practical Guide]]
