---
type: run
date: 2026-09-26 12:40
by: claude (UI plan agent, for abdul)
result: pass
build: vault note "Frontend and UX Plan v3 (merged)"; live Supabase ycyrtlzympxzlfcocazh; live n8n workflow 04 (task-intake); services/voice-relay working copy
---
# Run: UI plan v3 merged

## Goal
Write [[Frontend and UX Plan v3 (merged)]] (Dresden mit Kind + "Ask for me") on top of [[Frontend and UX Plan v2]], and check every value in its data contract against the live database, the live intake webhook and the relay code before Lovable uses it.

## Steps
1. Skills: `anti-ai-slop-ui-ux` (5 axes, per-component bans, audit), `component-reference-design` (filter bar §8, states §10, PDP layout §21, list rows), `ui-ux-pro-max`: `search.py "family activity directory for international parents, warm calm trustworthy multilingual" --design-system -p "Dresden mit Kind"`, plus colour searches ("family kids parents warm", "childcare education community warm") and a typography search ("warm friendly editorial serif family").
2. Read: v2 plan, [[Accessibility and RTL Review]], `docs/i18n/README.md` + `ui-strings.json` structure (en/ar/tr/uk, 15 screens), [[Idea B - Dies-Das-Ana-Nas]], [[Merged Concept]], [[DEC-003 Merged concept]], all migrations (merge migration in full), workflow 04 export, relay README, `task-templates.js` (course/kita templates), relay `public/index.html` (`?request=` support), [[Pitch Kit v2 (merged)]] §3.
3. Live DB (CLI `db query --linked`, SQL from UTF-8 files): columns of 7 tables, RLS policies, grants, the `mark_resource_checked` definition, Realtime publication, data counts (twice: before and after the parallel seeding runs).
4. Browser-like REST tests with the anon key (key never printed): `family_events` select; `resources` filters (`in`, `cs`, `ov`); `suggestions` insert with `return=minimal`, with `return=representation`, with `status='accepted'`; `suggestions` select. The one test suggestion was deleted afterwards (0 rows left).
5. One POST to the live intake webhook with Russian text + a `prefill` object (course_enquiry), Origin `https://dresden-mit-kind.lovable.app`.
6. Contrast (WCAG formula in Python) for the new tokens; Google Fonts CSS checks (Fraunces SOFT URL, subsets of Fraunces, Source Sans 3, Be Vietnam Pro, Fredoka).
7. Knowledge text length counted with Python; the new strings JSON parsed and every `t("screen.key")` in the prompts checked against it.

## Result
| Check | Outcome | Notes |
|---|---|---|
| Design-system search | ✅ ran | Marketplace/Directory pattern kept; Dark OLED, cyan #0891B2 (white 3.68:1) and Be Vietnam Pro (latin/vietnamese only) rejected; childcare pink #F472B6 (white 2.65:1) and Fredoka (no Cyrillic) rejected; bakery brown/cream supports the sand surface |
| Columns and allowed values | ✅ match the merge migration | `resources.languages` is nullable; `family_events.price_type` is `free\|paid\|unknown`; `call_requests.practice_phone` NOT NULL |
| RLS and grants | ✅ as planned | anon: SELECT resources / family_events / guides; INSERT-only suggestions (check `status = 'new'`); call_requests insert needs consent, `status = 'submitted'`, `call_brief_de` and `goal_de` null |
| Realtime publication | ✅ | call_requests, calls, transcript_lines, events (resources and family_events not needed) |
| `family_events` select (anon) | ✅ 200 | |
| `resources?category=eq.course&activity_categories=cs.{music}&languages=ov.{ru}` | ✅ 200 | after seeding: 1 real row (a music school, ages 2+, de/en/ru/uk/ko) |
| Age-band rule on live `/courses` rows (38 rows, 21 with ages) | ✅ | 0–1: 0 · 1–3: 4 · 3–6: 18 · 6–10: 21 · 10+: 21. Rows without ages go to a closed group (plan C2) |
| `suggestions` insert, `Prefer: return=minimal` | ✅ 201 | |
| `suggestions` insert, `return=representation` | ✅ 401 `42501` (expected) | proves "never `.select()` after this insert" |
| `suggestions` insert with `status='accepted'` | ✅ 401 RLS (expected) | |
| `suggestions` select | ✅ 401 `42501` (expected) | |
| Intake webhook with `prefill` | ⚠️ 200 in 11 s, prefill ignored | `task_type: other_call`, organisation empty, asks again for organisation name and phone. Plan v3 P7 re-applies the prefill in the client, so the UI works either way. Name and `opening_de` in Cyrillic → [[DEF-046 Non-Latin names reach the German greeting]]; "КИ-ассистентка" in `opening_user` |
| v2 P3/P4 vs workflow 04 fields | ❌ mismatch | → [[DEF-045 Plan v2 intake prompts do not match workflow 04]], fixed in plan v3 (F.5, P7/P8) |
| "Checked by phone" trigger | ❌ design gap | no `calls.provider` filter; relay always writes `deepgram-browser` → [[DEF-047 Role-play calls mark real providers as checked by phone]] |
| New tokens | ✅ | sand #F2E6D3: ink 12.88, ink-muted 5.02, pine 6.34; input border on sand 2.97 → no controls on sand; age ruler fill vs track 5.19 |
| Fraunces SOFT URL | ✅ 200 | variable woff2, weight 400–600; subsets latin, latin-ext, vietnamese (no Cyrillic → Source Serif 4 for ru/uk headings) |
| Knowledge v3 | ✅ 9,337 characters | budget 9,500 |
| Strings spec | ✅ | 12 screens, 275 new EN keys, valid JSON; all `t("…")` keys used in P1b–P13 exist |
| Data, 2nd check (after RUN-018/020/021) | info | 56 family places (28 courses, 5 Kitas, 3 schools, 4 libraries, 6 communities, 4 playgrounds, 6 family places), all with `i18n.ru`, 28 without an age range, 45 with a phone; 84 newcomer places, 23 with a phone; 20 family events 27.09–31.10 (languages de/es; `i18n` title+description in ar/de/ru/tr/uk); 8 guides with `i18n` in ar/de/ru/tr/uk; 0 resources with `last_checked_at`; no demo listing ("Olgas Musikstudio") yet |

## Defects found
- [[DEF-045 Plan v2 intake prompts do not match workflow 04]] (fixed in the plan)
- [[DEF-046 Non-Latin names reach the German greeting]]
- [[DEF-047 Role-play calls mark real providers as checked by phone]]

## Observations (not filed)
- `anon` and `authenticated` still hold TRUNCATE, REFERENCES and TRIGGER on `resources`, `family_events`, `guides` and `suggestions` (the migrations revoke only insert/update/delete). PostgREST cannot run TRUNCATE, so this is not reachable through the API today; worth one line in the next security audit (`docs/security/`).
- `docs/i18n/ui-strings.json` has en, ar, tr, uk only. RU and DE UI strings and all v3 screens still have to be written (plan G.0). The README's RTL note ("`<html dir="rtl">` for fa, prs") conflicts with the review's F2; plan v3 follows F2.
- The relay page is served by the relay itself, so "Start the call" in a new tab needs no origin change; only the optional in-app WebSocket (P13) needs the Lovable origin in `ALLOWED_ORIGINS`.
- Pitch Kit v2 plans a fictional "Olgas Musikstudio". Plan v3 H defines the rule if it is seeded: `subcategory = 'demo'`, fictional phone, visible "Demo listing, not a real business" tag.

## Verification

**2026-09-26 13:07 · by: claude (i18n agent, for abdul) · result: pass.** Goal: turn the plan's strings spec (G.0 step 2) into the real `docs/i18n/ui-strings.json` with all 6 UI languages, so the risk "Russian/German UI strings don't exist yet" (plan H) is closed before P1b.

### Steps
1. Read [[Frontend and UX Plan v3 (merged)]] sections A–C, E, F, G.0–G.2, H, plus `docs/i18n/README.md` and the v2 `ui-strings.json` (en, ar, tr, uk; 15 screens, 394 keys).
2. Live DB (CLI `db query --linked`, SQL from UTF-8 files, read-only): distinct `district` values in `resources` + `family_events` (16), distinct `subcategory` values (52; the lookup adds `demo` for the planned demo listing), distinct `languages` codes (27). Used for the `districts` and `subcategories` lookups.
3. Wrote de and ru for all 394 v2 keys, and 394 new keys in all 6 languages: the 275 keys of the plan spec (same English text) plus every string the prompts P1b–P13 write out in English or need for DB values (footer lines, `ask.sensitiveRemoved`, `ask.yourTimes`, `ask.neverTimes`, years/months units, event counts, age edge cases, `provider.ask_*` for all 10 task types, age-band chips, 53 subcategories, 17 districts, P13 microphone errors). Merged by a script from the v2 file, so no v2 key was lost.
4. v3 changes applied to the v2 values: "HalloTermin" → "Dresden mit Kind" (32 values; consent and calendar text "the Dresden mit Kind AI assistant"), screen `find` → `services`, `intake.loadingSlow` 15 → 20 seconds (the plan's 20 s intake timeout).
5. Validation script (Python), then the README check command and the per-language split command were run on the result, and the check was mutation-tested (a wrong placeholder, a deleted key and an empty value were all caught).

### Result
| Check | Outcome | Notes |
|---|---|---|
| Valid JSON, top-level languages | ✅ | `en, de, ru, uk, ar, tr`, 282 KB |
| Same screens and keys in every language | ✅ | 27 screens, 788 keys per language, 4,728 strings, no empty value |
| Placeholders identical to English | ✅ | 45 keys with placeholders, 0 mismatches |
| Plan G.0 spec | ✅ 275 / 275 | English text identical to the plan |
| `t("screen.key")` references in the plan | ✅ 131 / 131 | |
| Dynamic lookups | ✅ | 10 task types (`taskTypes`, `otherSide`, `provider.ask_*`), 16 activities, 12 categories, 5 price types, 6 formats, 5 age bands, 6 library categories, 15 result keys, 3 badge outcomes, 6 UI languages in `languages` / `languageNames` |
| Ukrainian ≠ Russian | ✅ | no і/ї/є/ґ in ru, no ы/э/ъ/ё in uk; 36 identical values are shared words (Меню, Банк, Аптека, Район …) |
| Content rules | ✅ | no "HalloTermin" left; no exclamation mark outside the German demo transcript; no hype words; Latin digits only in Arabic; no en dash between digits in Arabic |
| README commands | ✅ | check prints `ok`; split writes `en/de/ru/uk/ar/tr.json` (37–54 KB each) |

### Problems in the plan's strings spec, handled in the file
1. **"from 1 years" / "up to 1 years":** the spec has only `fromYears` / `upToYears`. Added `directory.fromOneYear` and `directory.upToOneYear`; the README says when to use them. Russian and Ukrainian have the same issue ("от 1 лет").
2. **Plurals:** `filters.count` / `countOne` cannot express Russian/Ukrainian (3 forms) or Arabic (6 forms). ru/uk/ar use a count label instead ("Мест: 12", "Місць: 12", "عدد الأماكن: 12"), which is correct for every number.
3. **Arabic ranges:** "3–6" with an en dash is shown as "6–3" in right-to-left text. Arabic uses words ("الأعمار من {min} إلى {max}") and ASCII hyphens in the age chips ("3-6"). `ar.suggest.urlError` has U+200E marks around `https://`.
4. **`{month}` in Russian/Ukrainian:** "место с {month}" would need the genitive, but `Intl` gives the nominative. The ru/uk strings use a colon ("место, начало: февраль 2027").
5. **`{language}`:** the plan's example "Events in Русский" passes the native name. The sentences are written for `languageNames[uiLang][code]` ("Veranstaltungen auf Russisch", "فعاليات باللغة الروسية"); the README says so.
6. **Old README RTL rule** (`<html dir="rtl">` for fa, prs) contradicted review F2; the README now follows plan v3 E (html `dir` from the UI language only).

No new defect notes: the only allowed numbers (DEF-045 to DEF-047) are already used by this run's builder for other bugs, and the six problems above are fixed in the strings file itself.

### For the native-speaker check (ru, uk, ar) before the demo
- Feature name: ru "Спросите за меня" and uk "Запитайте за мене" come from plan v3 A. "Спросить за кого-то" is colloquial Russian; alternatives are "Спросите вместо меня" / "Запитайте замість мене". Decide once and change `nav.ask` and `directory.askForMe` together.
- Kita: ru "детский сад (Kita)", uk "садочок (Kita)", ar "روضة (Kita)", tr "Kita (kreş ve anaokulu)".
- Library pillar: de "Ratgeber", ru "Справочник", uk "Довідник", ar "مكتبة الأدلة", tr "Rehberler" (not "library", to avoid confusion with real libraries).
- District names in Cyrillic and Arabic script (`districts`), e.g. ru "Йоханнштадт", uk "Йоганнштадт", ar "نويشتات".
- Arabic uses "فبراير" for February (Levantine readers may prefer "شباط").
- German uses "die KI-Assistentin / sie" to match the German call opening; ru/uk/ar use the masculine "ассистент / асистент / المساعد".

## Verification (schema and consistency review)

**2026-09-26 13:30 · by: claude (review agent, for abdul) · result: pass after fixes.** Goal: check [[Frontend and UX Plan v3 (merged)]] against the live system: schema, Knowledge length, string keys, the accessibility must-fix items and the call integration. Fix the note wherever it was wrong.

### Steps
1. Live DB (CLI `db query --linked`, SQL from UTF-8 files, read-only): `information_schema.columns` for `resources`, `family_events`, `suggestions`, `guides`, `call_requests`, `calls`, `transcript_lines`, `events`; all `pg_constraint` definitions; enum values (`request_status`, `speaker`); RLS policies; anon/authenticated grants; the Realtime publication; triggers and `pg_get_functiondef` of `mark_resource_checked`, `on_call_outcome`, `on_transcript_line`, `notify_n8n_new_request`; `i18n` shapes of guides, resources and family events; data counts; the demo requests `…0001` / `…0002` and their calls.
2. Anon REST GETs with the exact `select` lists of P2, P3, P4, P5, P6, P7, P10, P11 and P9 (key never printed; no writes). `suggestions` select → 401 `42501` as expected.
3. Knowledge text counted with Python. Every `t("screen.key")` in the note (165 static keys after the fixes) and every dynamic prefix (`provider.ask_`, `result.key_`, `taxonomy.age_`, `subcategories.`, `districts.`, …) checked against all 6 languages of `docs/i18n/ui-strings.json`.
4. [[Accessibility and RTL Review]] §4 must-fix list compared with section E and the prompts; the relay page `services/voice-relay/public/index.html` read for F5/F11/F12/F14.
5. Call integration: live workflow 04 read with the n8n MCP (`get_workflow_details`, version `de260485…`, updated 11:09 UTC = 13:09 Berlin) and the repo export; relay `server.js` (origin check, `?request=` page, `calls` insert, result shapes), `task-templates.js` (fact keys, `booking_kind`, result keys), `docs/deploy-relay.md`; migration `20260926210000_credits_translate_practice_only.sql` (untracked but live).
6. One POST to the live intake (`https://arahmandeaxo.app.n8n.cloud/webhook/task-intake`, Origin `https://dresden-mit-kind.lovable.app`) with Maria's Russian sentence and a `prefill` for the real course "Musikschule Adagio Dresden" (course_enquiry). Nothing is stored by workflow 04.

### Result
| Check | Outcome | Notes |
|---|---|---|
| Tables, columns, allowed values (resources, family_events, guides, suggestions, call_requests, calls, transcript_lines, events) | ✅ match the note | `family_events` (not `events`), 16 `activity_categories`, `resources.price_type` 5 values vs `family_events.price_type` `free\|paid\|unknown`, `format` nullable, `languages` nullable, `request_status` 8 values, `speaker` `agent\|practice\|system`, `calls.outcome` 8 values, `user_language` / `ui_lang` 14 codes |
| RLS, grants, Realtime | ✅ | suggestions INSERT-only (`status = 'new'`), call_requests insert check (consent, `submitted`, no brief/goal_de), publication = call_requests, calls, transcript_lines, events |
| `guides.i18n` shape | ✅ | `{"ar"\|"de"\|"ru"\|"tr"\|"uk": {title, summary, checklist[]}}` on all 8 guides; `sources[0]` = `{url, title, retrieved_at}`; `resources.i18n[lang].description`; `family_events.i18n[lang].{title, description}` |
| Anon REST with the prompt queries | ✅ all 200 | a non-UUID `id` gives 400 `22P02` → P7 now validates `?resource=` |
| Knowledge length | ✅ 9,476 characters after the fixes (9,337 before) | budget 9,500 |
| String keys | ✅ 165 / 165 static keys in all 6 languages; all dynamic prefixes present | |
| A11y must-fix 1–6 | ✅ in P1b, P9, P12 | F1 `prs → fa-AF` was missing in P1b's `loc()` → fixed |
| A11y must-fix 7 (F11 + F12 + F14, relay call page) | ❌ not covered | section E had re-labelled item 7 as app focus management. The relay page still has none of these fixes (no `role="status"`, raw `err.message`, `aria-live` log, no `lang="de"`) → new G.0 step 5 |
| Intake with prefill (live, 13:20) | ✅ 200 in 7 s | `task_type` course_enquiry, organisation + `resource_id` kept (also top-level `resource_id`), `person.name = "Maria Ivanova"` (transliterated), `opening_user` "ИИ-ассистентка", windows Tue 29.09 + Thu 01.10 13:00–17:00, facts `child_age`, `preferred_days`, `language_preference`, `ready = true` |
| Intake asks for the child's name | ❌ | `missing = [{field: "child_first_name", question_user: "Как зовут вашу дочь?"}]` although `ready = true` and the prompt says never ask → client guard added (P7/P8) |
| `essentials_missing` vs `missing` | ⚠️ | the server does not copy forgotten essentials into `missing` (the code comment says it does) → P8 now asks `essentials_missing` when `missing` is empty and `ready` is false |
| Relay integration | ⚠️ | `VITE_RELAY_URL` is `wss://…` in `docs/deploy-relay.md` but the page origin in the plan → P1b normalises and derives `RELAY_WS_URL`; the hosted relay page needs its own https origin in `ALLOWED_ORIGINS` (default localhost only); `server.js` accepts `*.lovable.app` / `*.lovableproject.com` by default, while `docs/deploy-relay.md` still says suffixes are unsupported |
| Live subtitles | ⚠️ | since migration `20260926210000` only `practice` lines are translated live; the plan showed "Translating…" / "Subtitle not available" under every agent row → P9 fixed |
| `/demo` request `…0001` | ❌ data | `status = calling`, 2 calls: the seeded booked mock call (08:15) and an aborted `deepgram-browser` call `b5c7dc08…` (26 Sep 08:38 UTC, `ended_at` set, no outcome). P9 "latest call" would show a dead call on `/demo` → P9 pick rule changed; reset SQL written into plan H (not run: data outside this task) |
| `mark_resource_checked` | ⚠️ unchanged | still no `provider` filter ([[DEF-047 Role-play calls mark real providers as checked by phone]] open); 0 resources with `last_checked_at`, 0 requests with `resource_id` |
| Data counts (13:20) | info | 56 family places (25 without ages, 45 with a phone, all with `i18n` in 5 languages); 84 newcomer places (23 with a phone); `/courses` 38 rows (24 with ages); 20 events 27.09–31.10, languages de 17 · es 1 · fr 1 · es+de 1, free 16 / paid 4; 8 guides |

### Fixes made in [[Frontend and UX Plan v3 (merged)]]
1. C5 and P6: the guide box label for `doctor_appointment` ("Ask for an appointment", guide `kinderarzt-u-untersuchungen`) was missing.
2. C6.3, C6.5, F.5, P7, P8, H: prefill and Latin names are now handled by the live intake (since 13:09). The note says so, and the client guards stay.
3. C6.4, F.5, P7 step 7, P8: never ask for the child's name (drop `child_first_name` / `child_name` questions).
4. F.5: the error list now includes `prefill_invalid` and `prefill_too_large`; limits added (draft 5,000, prefill 1,500, answers 10 × 200, round ≤ 5; `text` may be empty only with a prefill); `value` is accepted as a fallback key; timing 7 s.
5. F.5 TaskDraft: `organisation.resource_id: string | null`, top-level `resource_id`, `essentials_missing` values, `ready` rule; the gap between `essentials_missing` and `missing` is documented. P8 step 1 asks the essentials with existing string keys (`intake.*`, `ask.childAge`, `ask.startMonth`).
6. P8 step 1: the age control matched every field that contains "age", which includes `language_preference`. It now uses the regex `(^|[._:])(child_)?age($|[_|])`. `child_birth_month` gets a month input; units come from `ask.unitYears` / `ask.unitMonths`.
7. P8 step 2: `latinName` is defined (the field if shown, else `person.name`); the check text is updated.
8. P7 step 1: `?resource=` must be a UUID (otherwise PostgREST answers 400).
9. F.6: the intake normalises `start_month` to "Februar 2027"; `preferred_days` and `child_first_name` documented; `allowed_facts` < 4,000 bytes and `constraints` < 2,000 (check constraints).
10. F.7 + Knowledge + P9 step 4: agent lines have no live subtitle. They get no placeholder and are not announced; only practice rows show "Translating…" / "Subtitle not available".
11. F.7 + Knowledge: `events` columns and live event types; `transcript_lines.created_at`; `calls.created_at` (P9 sorts by it).
12. F.7 + P9 + P10: a request can have several calls. The pick rule is: the newest call that is running or has an outcome, and aborted calls are skipped. The stepper shows "Result" when the picked call has an outcome. The P10 check of `/r/…0001` explains the aborted call.
13. P9 step 5: timeline labels use the existing `call.ev*` keys; `turn_latency` is hidden.
14. P1b step 8: `loc()` maps `prs` → `fa-AF` (review F1).
15. P1b step 9, G.0 step 3, C7, F.7, P13, H: `VITE_RELAY_URL` is the relay's https origin. A `wss://` value is converted, and `RELAY_WS_URL` is derived from it (the separate `VITE_RELAY_WS_URL` is gone). The relay host must list its own origin in `ALLOWED_ORIGINS`. Lovable origins are already accepted through `ALLOWED_ORIGIN_SUFFIXES`.
16. Section E: the intro and rows 4 and 7 now map must-fix 7 (F11 + F12 + F14) and the test-page half of item 4 (F5) to a new **G.0 step 5**, a relay page fix in Claude Code. App focus management moved to a "+" row.
17. P2: string keys for the edge cases: `taxonomy.age_<band>` chips (hyphen in Arabic), `directory.fromOneYear` / `upToOneYear`, `directory.agesMissing`, `filters.triggerCount`, `filters.countOne`, `districts.*` next to the German district name. P4: `filters.countEvents(One)`. P5: `subcategories.*` instead of a hard-coded English list.
18. P5: `/services` drops `community` rows with `audience = 'family'` (they belong to `/communities`). The check text now says 92 rows.
19. G.0 step 2 is marked done (6 languages, 788 keys), and the strings spec is marked as implemented. G.0 step 4 has the counts from 13:20 (25 without ages, events de/es/fr).
20. G.1: the Knowledge count is updated to 9,476. RELAY_URL is described as the https origin.
21. H storyboard: windows are 13:00–17:00 (the intake maps "после обеда" / afternoon that way). Fact labels are not promised word for word. Only the receptionist's lines get live Russian subtitles.
22. H risks: strings done; prefill fixed and verified; the Latin name and "КИ" are now low risk; new rows for the child-name question, the stuck `/demo` request (with reset SQL), the relay origin and `VITE_RELAY_URL` scheme, and agent lines without live subtitles; "28" changed to "25" family places without ages.
23. Frontmatter sources + migration `20260926210000` and `docs/deploy-relay.md`.

### Defects found (not filed: DEF-045 to DEF-047 are the only allowed numbers and are already used)
- **Intake asks for the child's first name** (workflow 04). For the n8n owner: in "Validate + Clean Draft", drop `missing` items whose field matches `child_first_name|child_name`. The client guard is in the plan.
- **Intake never surfaces forgotten essentials in `missing`** (workflow 04; the code comment promises it). For the n8n owner: append a question per `essentials_missing` item when `missing` is empty. The client handling is in the plan.
- **`/demo` request `…0001` stuck at `calling` with an aborted second call.** The relay page and `server.js` default to this ID. For the orchestrator: run the reset SQL in plan H before the rehearsal. Relay owner: consider defaulting the page's ID field to empty.
- **Relay call page lacks accessibility must-fix 7** (F11, F12, F14) and F5 → plan G.0 step 5.
- **`docs/deploy-relay.md` drift:** it says `VITE_RELAY_URL=wss://…` (the plan uses the https page origin; the app now accepts both) and "`ALLOWED_ORIGIN_SUFFIXES` is not supported" (the current `server.js` supports it with a Lovable default).

Changes are limited to the plan note, this Run note, and short updates on [[DEF-045 Plan v2 intake prompts do not match workflow 04]], [[DEF-046 Non-Latin names reach the German greeting]] and [[DEF-047 Role-play calls mark real providers as checked by phone]]. No database rows were changed. In the builder's first result table two pipes inside a code span were escaped (`free\|paid\|unknown`), so the row renders as one cell. Nothing else in the earlier sections was changed.
