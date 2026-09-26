---
type: concept
tags: [tasks, n8n, extensibility]
---
# Task Types - How to extend

**Definition:** A *task type* is the kind of phone call HalloTermin makes (`call_requests.task_type`). Everything type-specific is data (templates and lists), so a new product direction means editing a few maps, not rebuilding workflows.

**Why it matters for us:** The merge with Idea B ([[DEC-003 Merged concept]]) added two family types in one afternoon. Adding or renaming a type should take ~15 minutes.

## The 10 types today
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
| **course_enquiry** (new, DEC-003) | appointment | a **trial lesson** (Probe-/Schnupperstunde) inside the parent's windows, after read-back → `confirm_booking` (booked). Otherwise `record_result` `course_availability` → completed. Never a binding registration, contract, membership or payment |
| **kita_enquiry** (new, DEC-003) | appointment | a **Kita visit / open day** inside the windows, after read-back → `confirm_booking` (booked). Otherwise `record_result` `kita_availability` → completed. Never registers the child or signs anything by phone (Dresden allocates places mostly via the city's online Kita portal) |

"appointment" types fall back to information mode when no time window is given.

### The two family types in detail
- **Principal = the parent** (`patient_name` = parent, e.g. "für Maria Ivanova"). The child is never the principal and only appears as allowed facts; never health details of the child.
- **Fact keys** (shared by intake 04, brief writer 01 and the relay): `child_age` (German, "5 Jahre" / "18 Monate"), `child_birth_month` ("03/2025", Kita alternative to age), `start_month` (German, "Januar 2027"; 01 and 04 also turn "2027-01" into "Januar 2027"), `preferred_days` ("dienstags ab 16 Uhr"), `language_preference` ("Russisch oder Englisch"), `child_first_name` (only if the parent gives it; intake never asks for it).
- **Opening clause** (German, after "…, weil <Name> noch nicht so gut Deutsch spricht, und"):
  - course: "wollte fragen, ob es in Ihrem Kurs für {Alter}-Jährige noch einen Platz oder eine Probestunde gibt"
  - kita: "wollte fragen, ob Sie ab {Monat} einen Betreuungsplatz für ein {Alter}-jähriges Kind haben und wie man auf die Warteliste kommt"
- **Intake essentials** (`ESSENTIALS` in 04): course = `organisation.phone`, `person.name`, `fact:child_age`, `goal_user`; kita = `organisation.phone`, `person.name`, `fact:child_age|child_birth` (either), `fact:start_month`. Windows are optional (needed only to book a trial lesson / visit).
- **Results** (relay → `calls.result`, read by 06): `course_availability` {free_spot, trial_lesson, trial_slot_text, waiting_list, schedule_text, price_text, language_of_instruction, next_steps}; `kita_availability` {places_available, from_month, waiting_list_possible, how_to_apply, visit_possible, visit_text, languages, next_steps}. A booking is `{result_type: 'booking', booking_kind: 'trial_lesson' | 'kita_visit', date, time, …details}`.

## Where the type logic lives
1. **DB:** check constraint `call_requests_task_type_check`, last changed in `supabase/migrations/20260926200000_merged_family_hub.sql` (also `guides.ask_task_type`). Doctor-only rule: `call_requests_doctor_reason`.
2. **n8n 01** (peFxjt572HiUxu61), Code node *Prepare Task Brief*: `TASK_TEMPLATES` = `{label_de, mode, needsWindows, purpose_de, may_de, ask_de, never_de}` per type, plus optional `principal_label_de` and `purpose_clause(h)` (h = child age / start month from allowed_facts; used for course/kita). Doctor extras (`REASON_DE`, the `no_reason_category` check) only apply to `doctor_appointment`.
3. **n8n 04** (OA51fhbX7NxrVEnW): enum in *Task Draft Schema*, the type list + essentials + PREFILL rules in the system prompt of *Draft Task (Claude)* (model Claude Haiku 4.5), and `ESSENTIALS` + deterministic guards in *Validate + Clean Draft* (course/kita opening built from facts, example-name guard, invented-window guard, prefill wins).
4. **n8n 06** (6jDZNKyT6kScVgmU): *Get Task Type* reads `call_requests.task_type`; *Prepare Result* turns `course_availability` / `kita_availability` (and bookings with `booking_kind`) into readable key facts, so the user reads e.g. "Trial lesson: Thursday 16:30" in their language.
5. **Voice relay**: `services/voice-relay/task-templates.js` (`TASK_TEMPLATES`, one object per type: label, mode, purposeDe, goalDe, resultType, resultHint, bookingKind, rules); `server.js` `buildAgent` picks the functions (`confirm_booking` when windows exist, `record_result` otherwise). See [[RUN-014 Relay v2 generic tasks]].
6. **Frontend:** task chips, per-type form fields and labels in the UI languages.

Workflow 05 (translate line) is type-agnostic.

## Prefill ("Ask for me" on a provider page or guide)
The app POSTs to `/webhook/task-intake` with the user's text (may be empty) and
`prefill: {task_type, organisation: {name, phone, category, resource_id}, goal_hint}`.
Intake keeps `task_type`, organisation and `resource_id` from the prefill (a valid prefill phone always wins), never asks for the organisation again, and returns `organisation.resource_id` (mirrored as top-level `resource_id`). Follow-up rounds send the draft back; `resource_id` is kept from `draft.organisation.resource_id`. The final insert into `call_requests` carries `resource_id`; when the call ends, the trigger `mark_resource_checked` sets the provider's "checked by phone" badge.
Body also accepts `ui_language` (alias of `ui_lang`), `hint_task_type` (soft hint from a chip) and answers as `{field, answer}` or `{field, value}`.

## Steps to add a type (example: `school_enquiry`)
1. New migration: drop + re-add `call_requests_task_type_check` (and `guides_ask_task_type_check`) with the new value (`npx supabase migration new add_task_type_school`), push.
2. n8n 01: add a `TASK_TEMPLATES.school_enquiry` entry (German texts, mode, optional `purpose_clause`). Publish.
3. n8n 04: add the value to the schema enum (also the enum in *Check Origin + Size* `TYPES` for prefill), one line in the prompt's TASK TYPES list, one `ESSENTIALS` entry. Publish; test with a POST to `/webhook/task-intake` (an allowed `Origin` header is required, e.g. `http://localhost:8787`; send non-ASCII bodies with `curl --data-binary @file.json`).
4. n8n 06: only if the type has its own `result_type`: add its key facts in *Prepare Result* and one line in the Claude system prompt.
5. Relay: add a `TASK_TEMPLATES.school_enquiry` entry in `services/voice-relay/task-templates.js`.
6. Frontend: chip + labels; run one E2E (insert → briefed → call → result).
7. Record it in `Decisions/` and a `Runs/` note.

To remove/rename a type, do the same in reverse; keep old values in the DB check until old rows are migrated.

**Related:** [[DEC-003 Merged concept]], [[RUN-015 Family task types in n8n]], [[Frontend and UX Plan v2]] (D2 essentials table, D5 data minimisation, F6 disclosure), [[Data Model]], [[RUN-013 n8n v2 workflows]], [[n8n - Practical Guide]]
