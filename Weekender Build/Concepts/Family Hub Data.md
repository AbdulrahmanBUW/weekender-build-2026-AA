---
type: concept
tags: [data, database, family-hub, merged]
sources: ["supabase/migrations/20260926200000_merged_family_hub.sql", "docs/content-kit/README.md", "scripts/import_content.py", "[[RUN-017 Family courses seed]]", "[[RUN-018 Heritage-language family offers seed]]", "[[RUN-019 Family places seed]]", "[[RUN-020 Family events seed]]", "[[RUN-021 Library guides for families]]", "[[RUN-023 Merged flow E2E]]"]
---
# Family Hub Data (what is in the database for "Dresden mit Kind")

**Definition:** the reference data behind the four family pillars and the Health & services pillar of [[Merged Concept]]: rows in `resources`, `family_events` and `guides` on the live Supabase project `ycyrtlzympxzlfcocazh`. Schema: [[Data Model]] (section "Merge (DEC-003)").
**Why it matters for us:** the Discover and Understand steps of the demo only work if these lists are real, sourced and translated. The "Ask for me" button needs a listing (and ideally a phone number) to prefill the call.
**Related:** [[DEC-003 Merged concept]] · [[Frontend and UX Plan v3 (merged)]] · [[Newcomer Resources - Crawler]] · [[Task Types - How to extend]]

Counts from the live DB on **Sat 26.09, ~13:45** ([[RUN-023 Merged flow E2E]]). Re-count before the demo with the queries at the end.

## Per pillar

| Pillar (UI route) | Table / filter | Rows | Translations | Notes |
|---|---|---|---|---|
| **Courses & activities** (`/courses`) | `resources` `category = course` (all `audience = family`) | **28**: 18 activity courses (dance 6 · music 4 · sport 4 · swimming 3 · theatre 3 · art 2 · parent & baby 2 · yoga 1 · STEM 1 · nature 1; a row can have several) + 10 heritage-language courses (ru, uk, ar ×2, fr, it, pl, cs, one city-wide programme with 16 languages) | description in en + de/ru/uk/ar/tr on 28/28 | 23/28 with phone, 22/28 with an age range, 25/28 with a district. Source: [[RUN-017 Family courses seed]], [[RUN-018 Heritage-language family offers seed]] |
| … places to go (same page) | `playground` 4 · `family_place` 6 | **10** | 10/10 | 4 playgrounds (incl. an adventure and a forest playground); 6 family places = 5 family/parent centres (one with a family café) + 1 family counselling centre; 7/10 with phone. [[RUN-019 Family places seed]] |
| **Events** (`/events`) | `family_events` | **20**, 27.09.–31.10.2026, all in the future; 13 in the week 27.09.–04.10., 18 in the next 30 days | title/description in en + de/ru/uk/ar/tr on 20/20 | languages de 18 · es 2 · fr 1; free 16 · paid 4; 1 linked to a listing. [[RUN-020 Family events seed]] |
| **Bilingual communities** (`/communities`) | `community` with `audience = family` 6 (+ heritage-language courses, see [[DEF-033 Communities page drops heritage-language courses]]) | **6** family groups (+15 newcomer community places from the crawler) | 6/6 | Ukrainian children's centre, Czech parent-child groups, Spanish-speaking and Eritrean associations, two intercultural family meetups (ru/uk/fa/prs; ar/fa/pl). [[RUN-018 Heritage-language family offers seed]] |
| **Kita & school** (inside `/services` or Library) | `kita` 5 · `school` 3 | **8** | 8/8 | Kitas: the city's central Kita advice office (Amt für Kindertagesbetreuung), Kleiner Globus (multilingual), Ev. Kita Lukas (de/en/ru), DIS Preschool (en), Kita SpielWerk. Schools: DIS, Romain-Rolland-Gymnasium (de/fr), LaSuB advice office (`both`). All with phone. [[RUN-019 Family places seed]] |
| **Library** (`/library`) | `guides` | **8**: Anmeldung, Ausländerbehörde appointment, bank account, health insurance (newcomer, `both`) + Kita place, school enrolment, Kinderarzt/U-Untersuchungen, Kindergeld (`family`) | title, summary, checklist in en + de/ru/uk/ar/tr on 8/8 (checklist length equal in every language); `content_md` English only | categories documents 2 · money 2 · health 2 · kita_school 2; `ask_task_type` set on all 8 (kita-place → `kita_enquiry`, kinderarzt → `doctor_appointment`). 37 source entries. [[RUN-021 Library guides for families]] |
| … libraries as places | `library` 4 (`both`) | **4** | 4/4 | Zentralbibliothek + 3 branch libraries, all free |
| **Health & services** (`/services`) | `doctor` 38 (14 paediatricians/gynaecologists are `both`) · `pharmacy` 16 · `bank` 14 · `auslaenderbehoerde` 1 · newcomer `community` 15 | **84** | none (English `notes_en`; the UI translates labels only) | crawler 02 (Brave + Firecrawl) from 26.09 morning, spot-checked in [[RUN-011 Resource spot-check]]. **Few phones:** doctors 13/38, pharmacies 1/16, banks 2/14 |
| Suggestions | `suggestions` | 0 | – | browser insert-only, read by the service role only |

**Totals:** 140 `resources` (56 seeded family rows + 84 service places), 20 `family_events`, 8 `guides`. All 56 family rows have `description_en` + five translations + a `source_url`; 45/56 have a phone; 31/56 have an age range; 12 family/`both` rows have no district.

**No demo listing yet.** Plan v3 (section H) wants a fictional "Olgas Musikstudio" with `subcategory = 'demo'` and a `+49 351 0000000`-style phone for the on-stage call. It is not in `resources` (0 rows with `subcategory = 'demo'`).

## Sources policy (all rows)
- Only **real, public** information about organisations and public events in Dresden. Every row has a `source_url` that an agent actually opened (curl, raw HTML; no small-model summaries), and `notes_en` says "Details from the provider's website (retrieved 26 Sep 2026) — please verify before visiting."
- Never scraped: 116117, KV Sachsen Arztsuche, Doctolib, Jameda, Google Maps, Facebook, Instagram. No private individuals (no teacher names).
- Unknown stays unknown: null ages, `price_type = unknown`, no invented phone. `languages` = languages spoken / of instruction that the provider **states** (`de` assumed only for German-only sites) — not book or subject languages ([[DEF-037 Languages field used for book and subject languages]]).
- Districts were geocoded with OpenStreetMap Nominatim (© OpenStreetMap contributors); `lat`/`lng` from the same lookup.
- `last_checked_at` / `last_check_outcome` are written **only** by the trigger when an Ask-for-me call ends. Test calls on a real listing must be reset afterwards ([[DEF-047 Role-play calls mark real providers as checked by phone]]).

## Who verified what
| Data | Built by | Independent check | Outcome |
|---|---|---|---|
| 18 activity courses | courses seed agent ([[RUN-017 Family courses seed]]) | fact-check agent re-opened all 27 URLs and sub-pages, re-geocoded 16 addresses, compared numbers in all 5 translations | 18 real · 12 correct · 6 fixed · 0 deleted |
| 10 heritage-language courses + 6 communities (+1 school) | heritage seed agent ([[RUN-018 Heritage-language family offers seed]]) | fact-check agent, all pages + the city's migrant-organisation directory | 17 real and active · 3 corrected · 2 notes clarified · 0 deleted ([[DEF-034 Heritage-language seed overstated three details]], fixed) |
| 22 Kitas, schools, libraries, playgrounds, family places | family places agent ([[RUN-019 Family places seed]]) | fact-check agent, 27/27 URLs, reverse-geocoded all pins | 22 real · 4 corrected · 0 deleted |
| 20 events | events seed agent ([[RUN-020 Family events seed]]) | fact-check agent parsed each page's own date format, checked UTC offsets, scanned for "abgesagt/ausverkauft" | 19 unchanged · 1 corrected (French story hour: language fr, ages 3–7, [[DEF-040 Event language defaults to German when the source omits it]]) · 0 invented |
| 8 guides (4 new, 4 translated to de/ru) | guides agent ([[RUN-021 Library guides for families]]) | verification agent read all 19 new source URLs and every checklist item | fixes applied ([[DEF-044 Family guides state facts their sources do not support]], fixed); open: the Ausländerbehörde guide still says it "moves to a new address from May 2026" (it has moved) |
| UI strings for the data (districts, subcategories, 6 languages) | i18n agent ([[RUN-022 UI plan v3 merged]]) | schema review agent | pass after fixes |
| Whole loop on a real listing | integration agent ([[RUN-023 Merged flow E2E]]) | – | pass; badge reset afterwards |

**Translation review by native speakers (RU, UK, AR) is still open** — Anastasia's communities ([[DEC-003 Merged concept]] detail 4).

## Known data gaps (open defects)
- District values mix Stadtbezirk and Stadtteil → map in the frontend filter: [[DEF-035 District values mix Stadtbezirk and Stadtteil]], [[DEF-038 District mixes Stadtteil and Stadtbezirk names]].
- One address per provider (multi-site schools): [[DEF-031 resources has one address per provider]]. Same provider in several categories: [[DEF-036 Same provider listed in several categories]].
- `price_type` cannot say "fee + free trial": [[DEF-030 price_type cannot express fee plus trial]].
- `family_events.dedupe_key` depends on the session time zone: [[DEF-039 family_events dedupe_key depends on session TimeZone]] (always import with the script below).
- Guide `sources.retrieved_at` has two formats: [[DEF-043 Guide sources mix two retrieved_at formats]].

## How to refresh
1. **Spreadsheet → DB (preferred, no SQL):** `docs/content-kit/README.md`. Fill the Google Sheet from `providers-template.csv` / `events-template.csv` (columns include *Translations (JSON)* and *Source link*), download as CSV, then
   `python scripts/import_content.py "<file>.csv"` (dry run + report) → `… --apply` (asks `yes`, upserts on `dedupe_key` in one transaction). Needs `npx supabase login` + `link --project-ref ycyrtlzympxzlfcocazh`.
2. **Events go stale fastest:** 13 of 20 events are in the week of the demo. After 04.10. the list thins out; add October/November events from the same sources (IKT Dresden calendar, bibo-dresden.de, zoo, Philharmonie family concerts). Build timestamps from the visible local time with Europe/Berlin rules, not from JSON-LD offsets (DST ends 25.10.).
3. **SQL by hand:** only from a UTF-8 `.sql` file via `npx -y supabase db query --linked -f <file>` (never inline non-ASCII), upsert `on conflict (dedupe_key) do update`. Use a private scratchpad folder ([[DEF-042 Parallel agents share one scratchpad]]).
4. **Do not run crawler 02 before the demo** — it spends Brave + Firecrawl + Claude credits for every resource ([[RUN-024 n8n credit optimisation]]).
5. **Suggestions:** rows from the "Suggest a place" form land in `suggestions` (`status = new`); review them with the service role and import accepted ones through step 1.

## Count queries
```sql
select category, audience, count(*) from resources group by 1,2 order by 1,2;
select count(*) from family_events where coalesce(ends_at, starts_at) >= now();
select count(*) from guides where i18n ?& array['de','ru','uk','ar','tr'];
select count(*) from resources where last_checked_at is not null;   -- must be 0 before the demo (except the demo listing)
```
