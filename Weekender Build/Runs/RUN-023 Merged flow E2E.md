---
type: run
date: 2026-09-26 13:50
by: claude (integration agent, for abdul)
result: pass
build: cloud DB ycyrtlzympxzlfcocazh (migrations up to 20260926210000); n8n 01 peFxjt572HiUxu61, 04 OA51fhbX7NxrVEnW, 05 6ifL1eboa9a6XfeI, 06 6jDZNKyT6kScVgmU (live versions after RUN-015 verification and RUN-024); voice relay working copy on its own port :8792 (think claude-sonnet-5, listen nova-3, speak aura-2-viktoria-de)
---
# Run: Merged flow E2E ("Find it. We call for you.")

## Goal
Run the whole merged loop of [[DEC-003 Merged concept]] once on the cloud database, after all parallel build streams (RUN-015 to RUN-022, RUN-024): a **real course listing** → "Ask for me" task (`course_enquiry`, Russian parent, `resource_id`) → German brief (n8n 01) → voice call (relay role-play) → live subtitles (05) and batch subtitles (06) → answer in Russian (06) → "checked by phone" on the listing. Then clean up and count what is in the database per pillar ([[Family Hub Data]]).

## Steps
1. **Listing:** `resources` row *Musikschule Adagio Dresden* (`92edfd9e-33e8-4989-b2dd-63776725610c`, `category = course`, `audience = family`, ages 2+, languages de/en/ru/uk/ko). Before: `last_checked_at` and `last_check_outcome` null. The phone was only used as data. The relay has no dialer; nobody was called.
2. **Task** via anon REST (UTF-8 file body, `Prefer: return=minimal`, id set by the client): `task_type course_enquiry`, `user_language ru`, `patient_name` "Maria Ivanova (E2E merged)", practice name and phone from the listing, `organisation_category course`, `resource_id`, Russian `goal_user`, `allowed_facts [{child_age, "Child age", "4"}]`, `time_windows` Tue 29.09 + Thu 01.10, 15:00–18:00, consent, `status submitted` → HTTP 201.
3. Waited for `status = briefed` (n8n 01).
4. Own relay instance: `PORT=8792 node server.js` (background) → `node roleplay-course.js <id>` with `PORT=8792` → relay stopped afterwards. The relay on :8787 (if running) was not touched.
5. DB check: `calls`, `transcript_lines`, `events`, `resources`.
6. **Clean-up:** deleted the task (cascade: 1 call, 25 transcript lines, 13 events) and reset the listing's `last_checked_at` / `last_check_outcome` to null, so no fake "Checked by phone" badge is shown ([[DEF-047 Role-play calls mark real providers as checked by phone]]).
7. **Intake with prefill** (one extra call, credits are low): Russian text + `prefill` for the same listing → `POST /webhook/task-intake` (Origin `http://localhost:8787`).
8. Counts per pillar (SQL from UTF-8 files in a private scratchpad subfolder, because of [[DEF-042 Parallel agents share one scratchpad]]).

## Result
| Check | Result | Detail |
|---|---|---|
| Anon insert with `resource_id` | ✅ 201 | RLS accepts the new task type and the link to a listing |
| n8n 01 brief | ✅ `briefed` in 8.0 s | ERÖFFNUNG with "KI-Assistentin von Maria Ivanova" in the first sentence and the spec clause "für 4-Jährige noch einen Platz oder eine Probestunde"; FAKTEN only "Kind ist 4 Jahre alt" (from `allowed_facts`); windows "Di, 29.09.2026, 15:00–18:00 Uhr" / "Do, 01.10.2026 …"; rules: trial lesson only inside the windows + read-back, no binding registration / contract / payment, no child health data. Execution 612 |
| Greeting (relay) | ✅ | "Hier ist die KI-Assistentin von Maria Ivanova … ob es in Ihrem Kurs für Vierjährige noch einen Platz oder eine Probestunde gibt." (the test marker "(E2E merged)" was removed by the stage-direction filter and left "Maria Ivanova ." — only happens with test names) |
| Free spot not inferred ([[DEF-028 Free spot inferred from a filler or a trial offer]]) | ✅ | The receptionist answered "Ja, gern. Wie alt ist das Kind denn?"; `result` has no `free_spot` |
| Outside-window offer | ✅ | Saturday 10:00 refused, the agent offered the parent's two windows |
| Side questions | ✅ | Asked language and price before the read-back; both recorded |
| Read-back + booking | ✅ **booked**, call 99.5 s | "Die Probestunde wäre am Donnerstag, dem ersten Oktober, um sechzehn Uhr. Ist das richtig?" → `booked_slot` 2026-10-01 16:00 Berlin (inside the window), `booking_kind trial_lesson`, `bring_items` [bequeme Kleidung, Hausschuhe], `price_text` "38 Euro pro Monat", `language_of_instruction` "Deutsch, eine Lehrerin spricht auch Russisch"; `confirm_booking` 725 ms, `end_call` 120 ms, filler after the "Ja" 4.8 s |
| Request status | ✅ `booked` | |
| Turn latency | ✅ 1.5–2.5 s | 7 turns: 1.61 / 1.48 / 2.31 / 2.24 / 1.54 / 2.48 / 4.79 s (last one = booking turn) |
| Live subtitles (05, practice lines) | ✅ 11/11 Russian | (06 also picked up one practice line that was still untranslated when it ran) e.g. "Der Kurs kostet danach achtunddreißig Euro im Monat." → "Курс стоит тридцать восемь евро в месяц." |
| Batch subtitles (06, assistant lines) | ⚠️ 12/14 | 06 translated 13 lines in its single Claude call (`lines {pending 13, sent 13, translated 13, capped_at_30 false}`). The 2 assistant lines spoken **after** the outcome (filler + goodbye) stayed empty → [[DEF-049 Closing assistant lines after the outcome get no subtitle]] |
| `calls.summary_user` (06) | ✅ Russian, 8.5 s after the booking | "Пробный урок забронирован на четверг, 1 октября 2026 г. в 16:00. Группа занимается по четвергам. Стоимость 38 евро в месяц. Преподавание на немецком языке, одна учительница говорит по-русски. Принесите удобную одежду и домашние тапочки." — nothing invented; `bring_items_user` [удобная одежда, домашние тапочки] |
| Checked-by-phone trigger | ✅ fired | `resources.last_checked_at` = 11:35:45 UTC, `last_check_outcome = booked` on the listing (same second as the booking) → reset to null in clean-up |
| Events | ✅ | n8n_notified → brief_created → call_started → 7× turn_latency → booking_confirmed → call_ended → result_translated |
| Anon REST reads (browser view) | ✅ | `resources` family/both 70 rows, future `family_events` 20, `guides` 8 (all 200); `suggestions` select 401 (insert-only, as designed). `call_requests` select also works for anon (206, 13 rows): demo-mode RLS, see [[Data Model]] → Guardrails |
| Clean-up | ✅ | 0 requests / calls / lines / events left for the test id; 0 resources with `last_checked_at`; `call_requests` back to 13 rows |
| Intake + prefill (04) | ✅ 200 in 8.9 s | `course_enquiry`, `organisation` and `resource_id` (plus top-level mirror) kept from the prefill, `person.name` "Maria Ivanova" (Latin), `child_age` "4 Jahre", both windows, `opening_de` correct, `opening_user` Russian with "ИИ-ассистентка Марии Ивановой", `ready: true`. But it asked for the child's first name → [[DEF-050 Intake asks for the child's first name]] |

### Counts per pillar (26.09, ~13:45)
`select category, audience, count(*) from resources group by 1,2`: auslaenderbehoerde/newcomer 1 · bank/newcomer 14 · community/family 6 · community/newcomer 15 · course/family 28 · doctor/both 14 · doctor/newcomer 24 · family_place/family 6 · kita/family 5 · library/both 4 · pharmacy/newcomer 16 · playground/family 4 · school/both 1 · school/family 2 → **140 resources**, 56 seeded family rows (+14 paediatricians/gynaecologists as `both`).
`family_events`: 20, all in the future (27.09–31.10.2026), 18 in the next 30 days. `guides`: 8, all with title/summary/checklist in en + de/ru/uk/ar/tr (6 languages). `suggestions`: 0. Details: [[Family Hub Data]].

### Observations (no defect)
- The synthetic receptionist voice was misheard once: "Ja, richtig. Die Probestunde ist kostenlos" → STT "Ja, wichtig. Die Korbessstunde ist kostenlos", and 05 translated it faithfully as "Занятие плетением корзин бесплатное" ("the basket-weaving lesson is free"). The agent still treated "Ja" as the confirmation and the summary was right. On stage, the receptionist should speak clearly and not too fast.
- Russian subtitles declined the name wrongly twice ("ассистент ИИ Марии Иванов", "для Марии Иванов"). Cosmetic (Haiku).
- 13 older test/demo requests from 25–26.09 remain in `call_requests` (incl. the demo rows `…0001` Priya and `…0002` Amina). Not touched; decide before the demo which to keep.

## Defects found
- [[DEF-049 Closing assistant lines after the outcome get no subtitle]] (open, minor)
- [[DEF-050 Intake asks for the child's first name]] (open, minor)
- Numbered here: [[DEF-048 Child health terms in other languages reach the call brief]] (fixed in the RUN-015 verification)
- Re-confirmed: [[DEF-047 Role-play calls mark real providers as checked by phone]] (the trigger marked a real listing during this role-play; reset by hand)
