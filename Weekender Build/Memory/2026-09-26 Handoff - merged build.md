---
type: memory
date: 2026-09-26 13:50
by: abdul + claude (integration agent)
---
# Handoff: merged build — backend and data done, Lovable next

## Done (Sat 26.09, 11:00–13:50, parallel agent streams + integration)
- **Decision:** [[DEC-003 Merged concept]] accepted — **Dresden mit Kind** + **"Ask for me"**; families first + Health & services; UI in en, de, ru, uk, ar, tr. Status table: [[Merged Concept]] → "Build status (26.09 evening)".
- **DB:** merge migration `20260926200000_merged_family_hub.sql` live (family fields on `resources`, `family_events`, `suggestions`, guide categories + `ask_task_type`, task types `course_enquiry` / `kita_enquiry`, "checked by phone" trigger) + credit migration `20260926210000_credits_translate_practice_only.sql` → [[Data Model]] section "Merge (DEC-003)".
- **Data (real and sourced; family listings, events and new guides fact-checked by a second agent and translated de/ru/uk/ar/tr):** 28 courses, 6 family communities, 5 Kitas, 3 schools, 4 libraries, 4 playgrounds, 6 family places (56) + 84 service places from the crawler (English, spot-checked in [[RUN-011 Resource spot-check]]); 20 events (27.09.–31.10.); 8 guides incl. Kita place, school enrolment, Kinderarzt, Kindergeld → [[Family Hub Data]] ([[RUN-017 Family courses seed]] … [[RUN-021 Library guides for families]]). Spreadsheet import for more: `docs/content-kit/README.md` + `scripts/import_content.py`.
- **n8n:** 01/04/06 know both new types; intake keeps the provider prefill (`resource_id`); child health words in any language are stripped ([[RUN-015 Family task types in n8n]], [[DEF-048 Child health terms in other languages reach the call brief]]). All Claude calls on Haiku, assistant subtitles batched at call end ([[RUN-024 n8n credit optimisation]]).
- **Relay:** course + Kita templates, trial lesson / Kita visit booking inside the windows only, Lovable origins accepted, hang-up handling ([[RUN-016 Relay family task types]]). Container + deploy guide: `services/voice-relay/Dockerfile`, `docs/deploy-relay.md`.
- **UI plan:** [[Frontend and UX Plan v3 (merged)]] = the UI source (routes `/courses`, `/events`, `/communities`, `/services`, `/library`, `/p/:id`, `/ask`, `/suggest`; Knowledge + prompts). `docs/i18n/ui-strings.json` has 788 keys in all 6 languages ([[RUN-022 UI plan v3 merged]]). Pitch: [[Pitch Kit v2 (merged)]].
- **Integration test:** [[RUN-023 Merged flow E2E]] — real course listing → Russian "Ask for me" task → German brief in 8 s → role-play call books a trial lesson inside the window → Russian subtitles and summary 8.5 s after the booking → listing marked "checked by phone" (then reset). Intake with prefill: 200 in 8.9 s, `resource_id` kept.

## Open
- **Lovable UI: not built** (P1 shell only). This is the only big piece missing for the Sunday URL.
- **Relay not hosted publicly:** `server.js` still binds `127.0.0.1` (the `HOST` change in `docs/deploy-relay.md` §0 is not made); set `ALLOWED_ORIGINS` to the real app + relay origins and `ALLOWED_ORIGIN_SUFFIXES=` once the Lovable URL is known. Fallback: presenter laptop.
- **Demo listing "Olgas Musikstudio"** (`subcategory = 'demo'`, fictional `+49 351 0000000`-style phone, `i18n.ru`) is not in `resources` yet. Needed because role-plays must never run on a real provider on stage ([[DEF-047 Role-play calls mark real providers as checked by phone]], trigger fix proposed there, not applied).
- **Translation review** of UI strings and content in RU, UK, AR by native speakers (Anastasia's communities). Guide long texts (`content_md`) are English only.
- Open defects that touch the demo: [[DEF-049 Closing assistant lines after the outcome get no subtitle]] · [[DEF-050 Intake asks for the child's first name]] · [[DEF-046 Non-Latin names reach the German greeting]] · [[DEF-033 Communities page drops heritage-language courses]] (frontend rule) · [[DEF-035 District values mix Stadtbezirk and Stadtteil]] / [[DEF-038 District mixes Stadtteil and Stadtbezirk names]] (frontend mapping) · [[DEF-024 Intake drops a bare weekday for landlord requests]] · [[DEF-029 Unconfirmed numbers are recorded when the other side hangs up]] · [[DEF-042 Parallel agents share one scratchpad]].
- Content: the Ausländerbehörde guide still says it "moves from May 2026" (it has moved; [[RUN-021 Library guides for families]]). 13 events fall in the demo week, so the list thins out after 04.10.
- 13 old test/demo rows in `call_requests` (25–26.09, incl. demo `…0001` Priya and `…0002` Amina). Decide which to keep before the demo.
- Mandatory deliverables still to produce on Sunday: brag launch video (`docs/launch/` is empty); archify diagrams and the security review in `docs/` are from before the merge (no family tables, no `suggestions`, no prefill).

## Next
1. **Lovable build with Plan v3** (Anastasia + Abdul): Knowledge text, then the prompts in the plan's order; check each preview; use the six strings files; never Lovable Cloud.
2. **Translation review** (Anastasia): RU, UK, AR in `docs/i18n/ui-strings.json` and the "Ask for me" labels; flag wrong content translations as corrections.
3. **Events refresh** (Sunday morning): add upcoming October/November family events via the content kit (see [[Family Hub Data]] → How to refresh); re-count before Pod #04.
4. Abdul: host the relay (HOST bind + Render/Fly per `docs/deploy-relay.md`), add the demo listing, decide the DEF-047 trigger fix and the cheap DEF-049 fix (Wait node in 06), then rehearse the demo on the demo listing only.
5. Before the demo: `select count(*) from resources where last_checked_at is not null;` must be 0 (or only the demo listing).

## Learnings / gotchas
- **Test calls on a real listing** fire the "checked by phone" trigger (the relay writes `provider = 'deepgram-browser'`). Always reset `last_checked_at` / `last_check_outcome` after a test.
- Run your own relay on a spare port (`PORT=8792 node server.js`; `roleplay-*.js` read the same `PORT`), so you never disturb a teammate's relay on :8787.
- Anon test inserts: set the `id` in the body so clean-up can delete exactly that row. Note: in demo-mode RLS the anon key can still **read all** `call_requests` (names, phones, windows) — fine for fake demo data, but a real parent using the live URL would be exposed. Owner policies/auth are a Monday-morning item ([[Data Model]] → Guardrails).
- Keep SQL and scratch files in your own subfolder; parallel agents overwrote each other's files ([[DEF-042 Parallel agents share one scratchpad]]). Non-ASCII SQL only from UTF-8 files.
- The synthetic receptionist voice gets misheard sometimes ("Probestunde" → "Korbessstunde"), and the subtitle translates the mishearing. On stage, speak clearly.
