---
type: run
date: 2026-09-26 12:40
by: claude (n8n template agent, for abdul)
result: pass
build: n8n 01 peFxjt572HiUxu61 (v 727db61e), 04 OA51fhbX7NxrVEnW (v 41836408, Claude Haiku 4.5), 06 6jDZNKyT6kScVgmU (v 0f08cb2f); cloud DB ycyrtlzympxzlfcocazh
---
# Run: Family task types in n8n (course_enquiry, kita_enquiry, prefill)

## Goal
n8n side of [[DEC-003 Merged concept]]: the two new task types `course_enquiry` and `kita_enquiry` in the brief writer (01), the intake (04) incl. PREFILL from the "Ask for me" button, and readable results in the user's language (06). Contract documented in [[Task Types - How to extend]]. All test people are fake; test organisations were made up ("… (Test)", 0351 000000x) except one real course row used only as prefill/`resource_id` (no call placed; the relay has no auto-dialer).

## Steps
1. **01** *Prepare Task Brief*: `TASK_TEMPLATES.course_enquiry` + `.kita_enquiry` (German, mode appointment, `principal_label_de` = parent, `purpose_clause` built from facts `child_age` / `child_birth_month` / `start_month`); *Parse Brief + Re-check* fallback opening keeps the clause. Doctor-only check (`no_reason_category`) untouched and only for doctor. Local harness: 5 cases (course with window, Kita in months, Kita with birth month, course with a health fact → stripped, doctor without reason → still invalid).
2. **04**: enum + essentials + PREFILL rules in the prompt; *Check Origin + Size* validates `prefill` (object ≤1500 chars, `resource_id` must be a UUID, else null) and allows empty text with a prefill; *Validate + Clean Draft*: `ESSENTIALS` for both types (`fact:a|b` = either key), prefill organisation/phone/category/resource_id always win, organisation questions dropped, `organisation.resource_id` (+ `resource_id` mirror) in the draft. Model stays `claude-haiku-4-5-20251001`; execution data still not saved.
3. **06**: new *Get Task Type* (GET `call_requests.task_type`, supabaseApi, errors continue); *Prepare Result* builds key facts for `course_availability` / `kita_availability` and for bookings with `booking_kind` `trial_lesson` / `kita_visit` (relay shape); system prompt has a FAMILY TASKS paragraph.
4. Every change: `validate_node_config` → `update_workflow` → live code compared byte-for-byte with the local file → connections checked → published. `saveDataSuccessExecution: none` kept on 01/06, 04 saves nothing.
5. Tests below, then all test rows deleted (4 `call_requests`, 4 `calls`, their events cascade) and the course row's `last_checked_at` / `last_check_outcome` restored to null.

## Result
| Test | Result |
|---|---|
| 04 Russian music course + prefill (made-up org, `resource_id` null) | `course_enquiry`, org + phone from prefill, parent "Maria Ivanova" (Latin), facts child_age "5 Jahre", preferred_days, language_preference "Russisch oder Englisch", windows Tue 29.09 / Thu 01.10 / Tue 06.10 16:00–19:00, no questions, `ready: true`, 6.5–9 s |
| 04 same with a real course row (Musikschule Adagio Dresden) | `organisation.resource_id` = the row id, organisation never asked, 6.5 s |
| 04 Ukrainian Kita, no prefill | `kita_enquiry`, "Kita Sonnenschein (Test)", phone normalised, facts child_age "2 Jahre", start_month "Januar 2027", no invented window, one Ukrainian question for the visit time, 7.4–9 s |
| 04 Kita round 2 with `answers: [{field, value}]` | window 2026-09-29 10:00–12:00 merged, `ready: true` |
| 04 bad Origin / `prefill: [1]` / empty body | 403 / 400 `prefill_invalid` / 400 `text_required` |
| 04 regression doctor (en), landlord with explicit date (en) | windows resolved, `ready: true` |
| E2E course (ru) via anon REST, with `resource_id` | `briefed` after 6.9 s: "ERÖFFNUNG: Guten Tag! Hier ist die KI-Assistentin von Maria Ivanova … und wollte fragen, ob es in Ihrem Kurs für 5-Jährige noch einen Platz oder eine Probestunde gibt." FAKTEN only from allowed_facts, 3 German-format windows, rules: trial lesson only inside windows + read-back, no registration/contract/payment, no child health data |
| E2E Kita (uk) | `briefed` after 7.0 s, clause "ab Januar 2027 … ein 2-jähriges Kind … Warteliste", visit window Di 29.09 10–12, "Nie Kind telefonisch anmelden oder registrieren" |
| 06 course `course_availability` (ru) | Russian B1: no free spot, waiting list, trial lesson Wed 07.10 15:00 not booked (outside the windows), Thursdays 16:30–17:15, 48 EUR/month, teacher speaks Russian, next step |
| 06 course booked (ru) | "записали вас на пробное занятие … четверг, 1 октября 2026 г. в 16:30" (trial lesson) |
| 06 Kita `kita_availability` (uk) | no place now, from August 2027, city online Kita portal, open day Sat 17.10 10–12 |
| 06 Kita booked, relay shape `booking_kind: kita_visit` + details (uk) | "записали вас на візит до Kita у вівторок, 29 вересня 2026 р. о 10:30" + place/portal facts |
| Events | n8n_notified → brief_created (task_type, mode appointment) → result_translated for every test row |

## Notes / open
- The "checked by phone" trigger fires on test calls too: when testing 06 on a request linked to a real resource, restore `last_checked_at` / `last_check_outcome` afterwards (done here).
- `opening_user` (the translation under the German opening on the approval card) is still written by the model, so wording can differ slightly from the deterministic course/kita `opening_de` (e.g. "KI-ассистентка от HalloTermin").
- 06 `status_set` in `result_translated` logs the intended status even when the status guard blocks the PATCH (pre-existing).
- Exports: `n8n/workflows/01-new-request-brief.json`, `04-task-intake.json`, `06-call-result.json` (no credentials).

## Defects found
- [[DEF-020 Intake ignores frontend answer and language field names]] (fixed)
- [[DEF-021 Intake opening uses the example name]] (fixed)
- [[DEF-022 Intake invents a time window]] (fixed)
- [[DEF-023 Start month spoken as 2027-01]] (fixed)
- [[DEF-024 Intake drops a bare weekday for landlord requests]] (open, minor)

## Verification
Independent re-test on 26 Sep, 12:44–13:02 (claude, verification agent). Started from "assume it is broken". Result: **partial → fixed**. The templates, prefill and summaries worked. One real gap (child health details in other languages reached the call brief) and two opening problems were fixed, then published and re-tested.

**(a) Live versions.** Published = draft on all three before the test (01 `727db61e`, 04 `41836408`, 06 `0f08cb2f`). 01 *Prepare Task Brief* has `course_enquiry` / `kita_enquiry` with `purpose_clause`; the doctor-only check applies only to doctors. 04 has both types in the schema enum, the prompt and `ESSENTIALS`, the prefill guard (UUID check) and `resource_id` in the draft. 06 has *Get Task Type* and key facts for `course_availability` / `kita_availability` / `booking_kind`. The exports in `n8n/workflows/` matched the live code (spot checks).

**(b) E2E via anon REST (UTF-8 file bodies, fake organisations "… (E2E verify)", 0351 000000x):**

| Task | Result |
|---|---|
| `course_enquiry`, `tr`, parent "Ayşe Yılmaz", facts `child_age` "5", `preferred_days` "Di/Do nachmittags", no window | `briefed` 10.1 s after insert. "Hier ist die KI-Assistentin von Ayşe Yılmaz … für 5-Jährige noch einen Platz oder eine Probestunde". FAKTEN = only name + 2 facts, mode Auskunft ("keine – nur Auskunft einholen"), no registration or payment, no child health data |
| `kita_enquiry`, `ar`, parent "Layla Mansour", facts `child_age` "2 Jahre", `start_month` "2027-03", window Tue 06.10 10–12 | `briefed` 9.0 s. "ab März 2027 … ein 2-jähriges Kind … Warteliste", FAKTEN "Gewünschter Beginn: März 2027", window "Di, 06.10.2026, 10:00–12:00 Uhr", "Nie behaupten, das Kind anzumelden" |
| **Adversarial** `course_enquiry`, `tr`, `goal_user` "Oğlumun astımı ve alerjisi var …", fact `child_note` "astım, alerji" | ❌ before the fix: FAKTEN contained "Hinweis zum Kind: astım, alerji (nicht an Kursanbieter weitergeben)". The fact was not stripped and `sensitive_stripped` was not logged. ✅ after the fix: fact dropped, `goal_user` without the health words, brief clean |
| Russian `goal_user` with "больше … в большой группе", Arabic with "باللغة الألمانية" (after the fix) | kept unchanged (before the fix both matched the health list, see below) |

**(c) Intake (workflow 04, Origin `http://localhost:8787`):**

| Test | Result |
|---|---|
| Russian parent text + prefill (real course row Schwimmschule Funk, `resource_id` 76199846-…), no child age | org name, phone, category and `resource_id` (+ top-level mirror) kept. Only question: `child_age` "Сколько лет вашему сыну?". Name "Maria Ivanova". Tuesdays after 16:00 → 29.09 / 06.10 / 13.10 16–19. 7–10 s |
| Same prefill, text "Хочу записать ребёнка на пробное занятие." | asks name + age (+ optional time) in Russian, never the organisation. ❌ before: `opening_de` "…von meiner Auftraggeberin. Ich rufe für meiner Auftraggeberin an, weil meiner Auftraggeberin…" (bad German). ✅ after: "Hier ist eine KI-Assistentin. Ich rufe im Auftrag einer Person an, die noch nicht so gut Deutsch spricht, und wollte fragen, …" |
| "My son is 7 and has asthma … swimming course for his lungs" (en), Russian asthma + allergy with prefill, Turkish "astımı var" | `sensitive_removed: true` every time. No health word in `goal_user`, `goal_de`, facts or `opening_de` (checked by regex over the JSON). Only `child_age` kept |
| Origin `https://evil.example` | 403 `origin_not_allowed` (0.4–2.7 s) |
| Regressions after the fix: English doctor ("any morning next week"), landlord with an explicit date (3 runs), Arabic Kita | windows resolved, `ready: true`, standard opening |

**(d) Workflow 06:** call row with `provider = 'verify'` on the Turkish course task → `outcome = completed`, `result = {"result_type":"course_availability","trial_lesson":true,"trial_slot_text":"Do 16:30"}` → `summary_user` in Turkish 6.7 s later: "Sizin için kursu aradık. Deneme dersi mümkün: Perşembe günü saat 16:30. Diğer kurs günleri, saatleri, ücret veya dil hakkında bilgi verilmedi. …". Nothing invented; not called "booked". Request → `completed`. Extra: Arabic Kita `booked` (relay shape `booking_kind: kita_visit` + details, `booked_slot` 06.10 10:30): Arabic summary with "الثلاثاء، 6 أكتوبر 2026 في 10:30", no place before August 2027, Kita portal. Request → `booked`.

**Fixes (validated with a local harness of 22 cases, published, exported):**
1. **Health terms in other languages** (01 *Prepare Task Brief*, 01 *Parse Brief + Re-check*, 04 *Validate + Clean Draft*). The safety-net regex only knew a few non-German words. Missing: tr astım / alerji / hastalık / otizm / diyabet / engelli; ru/uk астма / аллергия / алергія / болезнь / хвороба / аутизм / эпилепсия / діабет / инвалид / СДВГ; ar ربو / حساسية / مرض / سكري / توحد / صرع; de/en ADHS / ADHD / Autismus / Epilepsie / Neurodermitis / Behinderung / disability. False positives: `боль` matched **больше / большой** (ru "more / big"), `біль` matched **більше** (uk "more"), and Arabic `ألم` matched **ألمانيا / الألمانية** ("Germany / German"). An Arabic parent writing "we don't speak German well" had the word cut out and `sensitive_removed` set. Now `боль(?!ш)`, `біль(?!ш)`, `ألم(?!ان)`. Short Arabic words need word boundaries, so تربوي ("educational") and عسكري ("military") stay. *Parse* also drops any FAKTEN line that contains a health term (second safety net; REGELN are untouched, pharmacy exempt) and logs `sensitive_stripped` with the field `call_brief_de.fakten`.
2. **Opening without a name** (04). A grammatical, neutral German opening is built in code. The prompt no longer shows a no-name example: it primed Haiku to write "Hier ist eine KI-Assistentin. Ich rufe im Auftrag von Tom Test an. Seine Heizung…" for a *named* landlord request. The model now returns `""` and the server fills it in.
3. **`opening_user`** (04). The prompt asks for a faithful translation ("AI assistant OF <Name>", never "from HalloTermin", the local word for AI). In code, a leftover German "KI" becomes ИИ (ru), ШІ (uk), AI (en) or yapay zekâ (tr). The partial fix for the "KI" point of [[DEF-046 Non-Latin names reach the German greeting]].

Versions after verification: 01 `9a55d7bf`, 04 `8a7e42d4` (06 unchanged `0f08cb2f`). Exports updated: `n8n/workflows/01-new-request-brief.json`, `04-task-intake.json`.

**Still open (minor):**
- `opening_user` still says "from HalloTermin" in about 1 of 6 runs and sometimes uses he/she. The model does this; the German line and the relay greeting are right.
- The 01 brief's ERÖFFNUNG is written by Claude Sonnet and was once gendered ("für Herrn Kaya …, weil er …") although the rule says neutral. The relay speaks its own deterministic greeting (`greetingOf` in `services/voice-relay/server.js`), so the brief line is only context.
- When a health word is cut from `goal_user`, the sentence can read oddly ("Oğlumun ve var …"). This only happens on direct REST inserts; the intake paraphrases.
- 04 `missing` can hold an optional `time_windows` question while `ready: true` (course). The UI must treat such questions as optional. The comment "add deterministic essentials the model forgot" in *Validate + Clean Draft* is not true: missing essentials only show up in `essentials_missing`.
- 01 brief took 9–10 s from insert here (builder: ~7 s); 06 took 6.7–6.8 s.

**Clean-up:** 6 test `call_requests` deleted by id and the "(E2E verify)" marker; the 2 `calls` (`provider = 'verify'`) and all events went with them via cascade (checked: 0 left). None was linked to a resource; Schwimmschule Funk (prefill only) still has `last_checked_at` null.

**Defect numbering:** DEF-020 to DEF-024 were all taken by the builder. The opening findings are added to [[DEF-021 Intake opening uses the example name]]. The health-term gap is described above and still needs its own defect number (orchestrator).
