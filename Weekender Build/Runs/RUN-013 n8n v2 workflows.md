---
type: run
date: 2026-09-26 11:30
by: claude (n8n builder agent)
result: pass
build: n8n 01 v2 (peFxjt572HiUxu61), 04 (OA51fhbX7NxrVEnW), 05 (6ifL1eboa9a6XfeI), 06 (6jDZNKyT6kScVgmU); cloud DB ycyrtlzympxzlfcocazh
---
# Run: n8n v2 workflows (generic tasks + multilingual)

## Goal
Build and verify the n8n side of [[Frontend and UX Plan v2]] section H: 01 generalised for all 8 task types, new 04 intake, 05 subtitle translation, 06 result in the user's language. All test data is fake.

## Steps
1. 01 updated in place (same id): Code node *Prepare Task Brief* with `TASK_TEMPLATES` (8 types), validation, D5.4 health-term strip; Claude writes `ZIEL:` + brief; *Parse Brief + Re-check* enforces "KI-Assistentin" in the opening; HTTP PATCH `call_requests` (goal_de, call_brief_de, status briefed); events as jsonb array (brief_created, sensitive_stripped).
2. 04 created: public webhook `POST /webhook/task-intake`, Origin allow-list + size checks, Basic LLM Chain + Claude Sonnet 5 + Structured Output Parser (manual JSON schema, autoFix with Haiku), server-side clean-up, JSON response. Execution data not saved.
3. 05 + 06 created (Header Auth, respond on receipt), Vault secrets `n8n_translate_line_url` and `n8n_call_result_url` created on the cloud DB.
4. End-to-end tests on the cloud DB.

## Result
| Test | Result |
|---|---|
| 01 manual: Arabic Kinderarzt (checkup, fever in goal_user) | brief in ~8.5 s, reason mapped to Vorsorgeuntersuchung, window Di 29.09 08–12, "حمى" stripped → `sensitive_stripped` event |
| 01 manual: Ukrainian contract_question | information-only brief, "Niemals am Telefon kündigen…", ~8 s |
| 04 bad Origin / 601 chars | 403 `origin_not_allowed` / 413 `text_too_long` |
| 04 Turkish pharmacy | pharmacy_question, fact medicine "Ibuprofen 400 mg, 20 Tabletten", phone normalised, ready=true, 18.8 s |
| 04 Arabic Kinderarzt | doctor_appointment, person Yusuf, parent_name fact, checkup, gkv/AOK Plus, window 2026-09-29 08–12, sensitive_removed=true, 1 question (DOB) in Arabic, 21.2 s |
| 04 English landlord heater | landlord_request, address fact, 2 windows (Thu pm, Fri am), ready=true, 7.7 s |
| E2E a: anon REST insert, Turkish pharmacy task | status `briefed` + goal_de + brief after 9 s; events n8n_notified, brief_created (jsonb object) |
| E2E b: transcript_lines insert | first try failed ([[DEF-010 Haiku alias rejected via n8n Gateway]]); after fix text_en + Turkish text_user filled in < 6 s |
| E2E c: calls.outcome = completed + result json | summary_user (Turkish, B1), bring_items_user, request status `completed`, event result_translated |
| E2E c2: outcome = booked + booked_slot on the same (completed) request | Turkish date "29 Eylül 2026 Salı, saat 08:15"; request status stayed `completed` (guard works) |
| net._http_response | all deliveries 200, none timed out |

## Notes / open
- 04 latency 8–21 s with Sonnet 5 + structured output. If too slow for the demo, switch the chain model to `claude-haiku-4-5-20251001` (quality drop in some languages to check).
- 01 brief was cut off at maxTokens 700 → raised to 1400 + "kurze Regeln" instruction.
- 04 has no per-IP rate limit yet (Plan D1); Origin check + 5 rounds cap only.
- n8n stores request headers (incl. `X-Webhook-Secret`) in saved execution data of 01/05/06 → [[DEF-011 Webhook secret visible in n8n execution data]].
- Test rows left in the cloud DB: request `df3f8726-d9bc-4198-a14e-e16f96faa43c`, call `…00e3`, transcript lines 121 (untranslated, before the fix) and 154.

## Defects found
- [[DEF-010 Haiku alias rejected via n8n Gateway]]
- [[DEF-011 Webhook secret visible in n8n execution data]]

## Update 26.09 — intake on Claude Haiku 4.5
Workflow 04 main model switched from `claude-sonnet-5` to `claude-haiku-4-5-20251001` (republished). Latency **3.9–9 s** (was 8–21 s). Quality check (Arabic children's-doctor request, UTF-8 body): task_type doctor_appointment, organisation + phone + 3 morning windows extracted, 3 follow-up questions in natural Arabic (reason, new patient, insurance), correct German opening with KI disclosure. Note: test with UTF-8 file bodies (`--data-binary @file`) — Windows command-line arguments garble Arabic.
