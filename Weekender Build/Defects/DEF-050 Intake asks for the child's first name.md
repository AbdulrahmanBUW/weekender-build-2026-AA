---
type: defect
date: 2026-09-26
status: fixed
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

### Applied (26 Sep ~14:40, n8n 04 version `04cb1fe2`, published)
Only the Code node *Validate + Clean Draft* changed. No prompt, model, credential, setting or other node changed. Four additions:
1. `const CHILD_NAME = /child.*name/i;` plus a list of the child-name values the model put into `allowed_facts`.
2. `missing[]`: every item whose `field` matches `CHILD_NAME` is dropped (before the max-3 cut), e.g. `child_first_name`, `child_name`, `childName`.
3. `allowed_facts`: every fact whose key matches `CHILD_NAME` is dropped, even when the parent volunteered the name. We never keep a child's name.
4. `constraints.notes_de` is dropped when it repeats one of those name values.

`ready` logic is unchanged: `essentials_missing` is empty and there is no `refuse_reason`. A child's name is never an essential, so the dropped question can never keep `ready` false. In the case above (all essentials present) the response is now `missing: []` and `ready: true`. If an essential is missing as well (e.g. no `child_age`), `ready` stays `false` and the app asks the `essentials_missing` items itself (Plan v3 P8 step 1). Forcing `ready: true` there would let through a draft without a phone number or with `refuse_reason: "emergency"`, so it is deliberately not done.

Not filtered: `child_dob` / `child_birth_month`. A Kita enquiry legitimately asks for the birth month as an alternative to the age.

### How tested (no AI credits, production webhook not called)
- **Local:** old and new node code ran side by side in Node with 5 drafts (this defect, name volunteered, missing essential, no child name, refusal). The draft without a child name gave byte-identical output.
- **Official n8n MCP:** `validate_workflow` (SDK code with the new node) gave valid. The version diff `de260485` → `04cb1fe2` shows only `Validate + Clean Draft.jsCode` changed and no connection changed.
- **`test_workflow` with pinned data:** the trigger and the **`Draft Task (Claude)` output were pinned**, so no Claude node ran (the executions hold no run data for either Haiku node). Fictional provider and test UUID, no DB writes.
  - Exec 627 (copy of this defect: `missing: [child_first_name]`, fact `child_first_name: "Anna"`, `notes_de: "Die Tochter heißt Anna, …"`) gave `missing: []`, `essentials_missing: []`, `ready: true`, `allowed_facts: [child_age]`, `constraints: {}`. "Anna" appears nowhere in the draft.
  - Exec 628 (`missing: [childName, language_preference]`, `notes_de: "Am liebsten nachmittags."`) kept only the `language_preference` question and kept `notes_de`. `ready: true`.
  - To inspect these two runs, `saveManualExecutions` was set to `true` for about one minute and then set back to `false`. Settings are now identical to before.
- Workflow is still active. The published version is `04cb1fe2` and the trigger and production URL are unchanged. Export `n8n/workflows/04-task-intake.json` updated (node code + a `_notes` line). A python scan found no keys or tokens.

### Open (small)
- The 04 prompt still lists `child_first_name` as an optional fact. The server drops it now; remove it from the prompt at the next prompt change (a prompt change costs no extra credits).
- [[Task Types - How to extend]] still lists `child_first_name` as a shared fact key. It should say "dropped by 04 (DEF-050)".
- Doctor appointments for a child still use `person.name` = the child (by design: the practice needs the patient's name). That is outside this defect.
- The frontend guard (questions optional while `ready: true`) can stay as a second safety net.
