---
type: run
date: 2026-09-26 12:40
by: claude (heritage-language seed agent, for abdul)
result: pass
build: public.resources on Supabase ycyrtlzympxzlfcocazh (merge migration 20260926200000_merged_family_hub.sql); seed SQL generated in the scratchpad (not committed)
---
# Run: Heritage-language family offers seed

## Goal
Seed 12–20 **real** bilingual and heritage-language offers for families in Dresden into `public.resources` for the "Bilingual communities" pillar of "Dresden mit Kind" ([[DEC-003 Merged concept]], [[Merged Concept]], [[Idea B - Dies-Das-Ana-Nas]]). That means weekend schools and children's language classes, parent-and-child groups, and cultural associations with children's programmes. Every row needs a source page we actually opened, English text plus `i18n` in de/ru/uk/ar/tr, and an upsert on `dedupe_key`. The existing newcomer `community` rows stay untouched.

## Steps
1. Read the merge migration: `resources` checks for category, audience, activity_categories, ages, price_type, format and description length, plus the generated `dedupe_key` = `category|lower(name)|lower(address)`.
2. Starting point: the City of Dresden page **"Förderung der Herkunftssprachen für Kinder und Jugendliche"** (the official list of children's heritage-language offers, 13 entries) and the city's migrant-organisation directory (26 landing pages fetched with curl, because WebFetch got HTTP 503 from dresden.de).
3. For each candidate we opened the organisation's **own** website (course page, contact page, imprint) and took only what was stated there. Ages, prices and phones were filled only where published; everything else was left null/`unknown`. We did not scrape Facebook, Instagram, Google Maps or any doctor portal. Where an organisation has no website (IBLA, ACI, Eritrean community), the `source_url` is the city directory page.
4. Postcodes that the source page left out were checked against the venue's official address (Gymnasium Tolkewitz: 01279; Pat's Colour Box: 01309). The Ukrainian House address comes from the Plattform Dresden e.V. imprint (Töpferstraße 10, QF-Passage, 01067).
5. `gen_rows.py` (scratchpad) checks every row before writing SQL: `description_en` ≤ 400 chars, activity_categories inside the allowed set, age range 0–18 and min ≤ max, no duplicate dedupe keys. Then it writes **one** UTF-8 file `run018_seed.sql` with `INSERT … ON CONFLICT (dedupe_key) DO UPDATE SET` for every column except the key columns (it never touches `last_checked_at` or `last_check_outcome`).
6. Ran it with `npx supabase db query --linked -f run018_seed.sql`.

## Result — 16 rows (10 `course`, 6 `community`, all `audience = family`, `source = web_research`)
| # | Name | Cat. | Languages | Ages | District | Source |
|---|---|---|---|---|---|---|
| 1 | Russische Schule Raduga (Brücke e.V.) | course | ru, de | 3–15 | Plauen | russische-schule-dresden.de |
| 2 | Russisch für Kinder – Kolibri e.V. | course | ru, de | 3+ | Altstadt | kolibri-dresden.de/kinder-russisch |
| 3 | Ukrainisch für Kinder – Kolibri e.V. | course | uk, de | 2.5+ | Altstadt | kolibri-dresden.de/kinder-sprachen-ukrainisch |
| 4 | Interkultureller Familientreff – Kolibri e.V. | community | de, en, ru, uk, fa, prs | all | Altstadt | kolibri-dresden.de (event page, free, Fri 15:30–18:30) |
| 5 | Le Rendez-vous e.V. – Französisch für Kinder (FLAM) | course | fr | 3–15 | Neustadt | sites.google.com/view/le-rendez-vous-e-v- |
| 6 | IBLA e.V. – Arabischunterricht für Kinder | course | ar, de | 5.5–16 | Neustadt | dresden.de directory (IBLA) |
| 7 | Friedensschule Dresden (Haus des Friedens, DIMCIB e.V.) | course | ar, de | – | Johannstadt | dimci-verein.de/die-schule |
| 8 | Schola ludus – Tschechische Schule | course | cs, de | 5+ | Blasewitz | scholaludus.de/de/page/skola |
| 9 | Schola ludus – tschechische Eltern-Kind-Gruppen Batolínek & Rákosníček | community | cs, de | 0–5 | Striesen | scholaludus.de/de/page/skola |
| 10 | Kinderclub Il Girasole (Deutsch-Italienische Gesellschaft Dresden e.V.) | course | it, de | – | Neustadt | italien-freunde-dd.de (kids' course page) |
| 11 | Akademie der polnischen Sprache in Dresden (DPG Sachsen e.V.) | course | pl, de | 5–16 | Neustadt | dpg-sachsen.eu |
| 12 | Kinderzentrum Dolon'ky (Ukrainisches Haus, Plattform Dresden e.V.) | community | uk | 0.7–14 | Altstadt | plattform-dresden.de/kinderzentrum-dolon-ky |
| 13 | Internationales Schreibcafé (Familie(n)leben e.V.) | community | de, ar, fa, pl | all | Altstadt | familienleben-dresden.de (free, childcare) |
| 14 | ACI – Asociación Cultural Iberoamericana e.V. | community | es, de, en | – | Neustadt | dresden.de directory (ACI) |
| 15 | Eritreische Gemeinschaft Dresden e.V. | community | ti, de | 6+ | Johannstadt | dresden.de heritage-language page |
| 16 | Herkunftssprachlicher Unterricht an Dresdner Schulen (LaSuB) | course | 16 languages incl. ar, tr, vi, zh, ru, uk, pl, fa | school age | – | dresden.de + 30. Grundschule 2026/27 notice |

Row 16 is the state heritage-language programme in Dresden schools for 2026/27: Arabic, Bulgarian, Chinese, Hindi, Japanese, Mongolian, Persian, Polish, Portuguese, Russian, Spanish, Czech, Turkish, Ukrainian, Hungarian and Vietnamese. Registration closes on 2 Oct 2026. It is the only row that covers **Turkish, Vietnamese and Chinese**, because we found no current community offer in those languages that we could verify.

**Left out on purpose** (not current, or not verifiable from an own source): Georgian Sunday school Ana-Bana (last announcement March 2023, possibly online only); Slovak "Slovenská školička" (2021 dates, "currently online"); Bulgarian children's dance group Veselinka (2023/24 posts); DSVB Arabic course (2021 post); Jusour Arabic school (Facebook only, which we may not scrape); "Wir sind Paten" Arabic (Facebook only); English Play Group Dresden (last post 2011); Dresden Family Friendly Meetup (events outside Dresden, 2 attendees); DRKI children's club (project page does not load); Chinesisch-Deutsches Zentrum (adult courses and school/Kita projects only, no children's Chinese class). The Russian Saturday schools "Slowo" (Frankfurt), "Perspektiva" (Nuremberg) and DRZ IBSK (Gießen) showed up in searches but are not in Dresden.

## Verification
| Check | Result |
|---|---|
| Row count after the insert | ✅ 16 rows in the new subcategories (`weekend_school`, `heritage_language_course`, `heritage_language_school`, `family_meetup`, `parent_child_group`, `kinderzentrum`, `cultural_association`, `herkunftssprachlicher_unterricht`) |
| Translations | ✅ 16/16 rows have `i18n` keys de, ru, uk, ar and tr |
| Byte-exact read-back | ✅ `cmp.py` read all 16 rows back and compared them with the generator data (description_en, notes_en, address, phone, languages, activities and the 5 translations): 0 mismatches, so no Arabic or Cyrillic text was garbled (the SQL went in through an `-f` file) |
| Constraints | ✅ all `description_en` ≤ 400 chars; `source_url` is https on every row; `last_checked_at` is null on all 16 |
| Idempotent upsert | ✅ ran the same file a second time: still 16 rows, 16 distinct `dedupe_key`s |
| Newcomer rows untouched | ✅ `community/newcomer` is still 15 rows; family community rows are counted separately (6) |
| Browser-like read | ✅ anon REST `audience=eq.family&languages=cs.{ar}&activity_categories=cs.{languages}` returns 3 rows (IBLA, Friedensschule, Herkunftssprachlicher Unterricht) with the Arabic `i18n` intact |
| Seed file integrity | ✅ regenerated the SQL and compared it with `cmp`: identical to the file that ran (relevant because of [[DEF-042 Parallel agents share one scratchpad]]) |

## Notes for the frontend
- **`/communities` in [[Frontend and UX Plan v3 (merged)]] (P5) does not show the 10 heritage-language `course` rows**, because its filter keeps only `community`/`library` rows or rows with the activities `parent_meetup`, `family_cafe` or `library`. Adding `languages` to that list fixes it → [[DEF-033 Communities page drops heritage-language courses]].
- `languages` means the language **spoken or taught**, not the UI language. Rows 4 and 13 list the languages of staff or interpreters.
- Sub-year ages: `age_min_years` is `numeric(4,1)`, so 9 months (0.75) cannot be stored exactly. Dolon'ky's baby course is stored as 0.7 so that a 9-month-old still matches an "age ≥ min" filter.
- Several rows have no phone (Schola ludus, Polish academy, Dolon'ky, ACI). The places list should show "No phone number found" rather than hide the row.
- Source error, outside our system: on the city's heritage-language page, the entry "Asociación Cultural Iberoamericana e.V. – Spanisch für Kinder" links to the **IBLA** directory page. Our ACI row uses the correct ACI page.

## Defects found
- [[DEF-033 Communities page drops heritage-language courses]] (major, frontend-only fix)
- Re-confirmed [[DEF-042 Parallel agents share one scratchpad]]. This agent's `q1.sql` was the file the guides agent ran by mistake. From then on this run used a unique subfolder (`run018_heritage/`) and checked the seed file with `cmp`.

## Verification — independent fact-check (26 Sep 2026, 12:40–12:55)
*By a second agent that did not write the seed. It assumed any row might be made up.*

**Scope:** every `resources` row with `audience in ('family','both')` and (`category = 'community'` or `'languages' = any(activity_categories)`). That is **17 rows**: the 16 from this run plus `Romain-Rolland-Gymnasium Dresden` from [[RUN-017 Family courses seed]]. Rows with `audience = 'newcomer'` were not touched.

**Method:** each `source_url` and `website` was fetched with curl (all 200) and read as text; nothing was taken from search snippets. Every name, address, phone, age, time and price in `description_en`, `notes_en` and `opening_hours` was checked against those pages, plus the city's migrant-organisation directory entry for each association. The 15 street addresses were geocoded with OpenStreetMap Nominatim (1 request per second) to check `district`. The numbers in the 5 translations were compared with the English text (only formatting differences, such as 5,5 vs 5.5 and 29.08 vs 29 Aug).

| # | Row | Pages opened | Confirmed | Action |
|---|---|---|---|---|
| 1 | Russische Schule Raduga | russische-schule-dresden.de; city directory (Brücke) | Saturdays from 9:25 at TU Seminargebäude 2, Zellescher Weg 20; ages 3–15; school year 29.08.2026–26.06.2027; phone 0351 4569834 | none |
| 2 | Kolibri – Russisch | /kinder-russisch/, /kontakt/ | Sep 2026 weekly calendar: groups from age 3 to 15+, weekday afternoons plus Saturdays 9:45–14:30, mostly in the Villa der Kulturen (Kraftwerk Mitte 2); logorhythmics from 3; Russian as a foreign language from 5; founded 2009; phone 0351 2068441 | none |
| 3 | Kolibri – Ukrainisch | /kinder-sprachen-ukrainisch/ | Groups from 5, 6 and 7; music + Ukrainian from 5; new group for 2.5–4.5; ensemble "Radist" for 4–12; 16:00–17:45 | none |
| 4 | Kolibri – Familientreff | event page, IKJEA page, city directory | Every Friday 15:30–18:30, free, no registration, Ritzenbergstraße 3, funded by the Jugendamt; office 0351 21994920 (Mon, Wed, Thu 9–14); languages de/en/ru/uk/Dari/Farsi as listed in the directory | none |
| 5 | Le Rendez-vous (FLAM) | Google site: home, inscriptions, finances; city directory | Founded Feb 2024; ages 3–15; Löwenstraße 2 (4. Grundschule) and Institut français; phone 0176 83908412 | **corrected**: fee period and alternating Mondays → [[DEF-034 Heritage-language seed overstated three details]] |
| 6 | IBLA – Arabisch | city directory (IBLA) + heritage-language page | Saturdays, grades 1–12, ages 5.5–16 on the city list; c/o Haus der Brücke, Rähnitzgasse 8; phone 0157 50146181 | none |
| 7 | Friedensschule (DIMCIB) | dimci-verein.de/die-schule/; city directory | Arabic, Islamic education, sport, competitions, outings; family discount; +49 152 299 69960 is listed on the school page; Marschnerstraße 33 | none |
| 8 | Schola ludus – Schule | /de/page/skola, /de/page/spolek; csbh.cz archive | Gymnasium Tolkewitz, Wednesdays 16:15–18:00 plus about one Saturday a month; pre-school 5–6; since 2005; the Czech Schools Without Borders membership is confirmed by csbh.cz (since 1 Nov 2011) | none |
| 9 | Schola ludus – Eltern-Kind | /de/page/skola | Batolínek every second Wednesday 9:30–11:00 (up to 2); Rákosníček Wednesdays 16:00–17:30 (up to 5) at Händelallee 23 | **corrected** `district`: Striesen → Blasewitz (DEF-034) |
| 10 | Il Girasole (DIG Dresden) | kids' course page, Kinderclub page, imprint, city directory | Founded 2010; groups of 4–6; Wednesdays from 15:30 and Thursdays from 16:15; Königsbrücker Straße 119/r; phone +49 152 313 287 85 | none |
| 11 | Polish academy (DPG Sachsen) | dpg-sachsen.eu academy page | 2025: Mondays for 5–7 and Wednesdays for 8–12 at Bautzner Str. 6, plus teen workshops and camps; 2026 courses continue, with new reading/writing and culture classes | **corrected**: the teen workshops were listed under 2026 (DEF-034) |
| 12 | Dolon'ky (Plattform Dresden) | course page, imprint, /ukrainisches-zentrum-2/ | 2026/27 course list; everything in Ukrainian and open to every child regardless of residence status; baby course 9–14 months; parent-child groups under 4 suspended; the Ukrainian House is at Töpferstraße 10 (QF-Passage, lower floor), 01067 | none |
| 13 | Internationales Schreibcafé | familienleben-dresden.de | Last Friday of the month 9:30–11:30, dates up to 27.11.2026; interpreters for de/ar/fa/pl; childcare; free; St. Petersburger Str. 12 | `notes_en` clarified: the phone is the association's main office |
| 14 | ACI | city directory (ACI) + heritage-language page | Visiting address Bischofsweg 74; languages es/de/en; activities for children and adults; "Spanisch für Kinder" is on the city list; no website or phone | none |
| 15 | Eritreische Gemeinschaft | city directory + heritage-language page | Tigrinya from age 6; phone 0176 30305722; postal address Reißiger Straße 17 | none |
| 16 | Herkunftssprachlicher Unterricht | city heritage-language page; 30. Grundschule notice of 14.08.2026 | 16 languages for 2026/27, but the notice says not every region gets every language; voluntary, 2 lessons a week, binding for the year; registration 31 Aug–2 Oct 2026; LaSuB coordination phone 0351 8439427 | `notes_en` clarified: the 16 languages are the Saxony-wide list |
| 17 | Romain-Rolland-Gymnasium *(RUN-017)* | /schulportrait/wege-zum-abitur/, /kontakt-1/ | Bilingual track since 1994; geography in French from grade 7, history from grade 10; AbiBac; no French needed to start; Weintraubenstraße 3; phone 0351 2780080 | none |

**Districts:** OSM agrees with the stored value for 14 of the 15 addresses at Stadtbezirk level, or at Stadtteil level for Johannstadt. The exception was Händelallee 23 (Neugruna, Stadtbezirk Blasewitz), which was fixed. The table as a whole mixes Stadtbezirk and Stadtteil names, which breaks an "equals" district filter → [[DEF-035 District values mix Stadtbezirk and Stadtteil]].

**How it was applied:** one UTF-8 file `fix018.sql` (scratchpad `fc018/`) ran through `supabase db query --linked -f`. It holds 5 `UPDATE … WHERE id = … AND audience IN ('family','both')` statements; `i18n` was changed with `jsonb_set` on `{lang,description}` only.

| Check after the fix | Result |
|---|---|
| Rows in scope | ✅ 17 before, 17 after (0 deleted) |
| Byte-exact read-back | ✅ every changed field equals the expected text, including the ar/ru/uk/tr/de translations; **0 unintended changes** in any other column or translation of the 17 rows |
| Browser-like read | ✅ anon REST returns the Polish academy, Le Rendez-vous and Schola ludus rows with the new English, the translations and `district` intact |
| Newcomer rows | ✅ untouched: 70 newcomer rows, 15 of them `community` |
| `last_checked_at` | ✅ still null on all 17 rows |
| Field limits | ✅ changed descriptions are ≤ 400 chars (394 and 365) |

**Counts:** 17 rows checked · **17 confirmed real, active and in Dresden** · **0 deleted** · 0 fields nulled · 3 rows corrected (Le Rendez-vous, Polish academy, Schola ludus groups) · 2 notes clarified (Herkunftssprachlicher Unterricht, Schreibcafé).

**Errors in outside sources (not our data):**
- The city's heritage-language page links "Asociación Cultural Iberoamericana e.V. – Spanisch für Kinder" to the IBLA page. Confirmed; our ACI row uses the correct ACI page.
- The city directory gives the Ukrainian House as "Neumarkt 2, 01069". Plattform Dresden gives "Töpferstraße 10 (QF-Passage, UG), 01067" or "Neumarkt 2, 01067", and we kept its own address.
- The DPG page gives "Bautzner Str. 6, 01097", while OSM puts no. 6 in 01099. We kept the source's postcode.

**Defects from this check:** [[DEF-034 Heritage-language seed overstated three details]] (minor, fixed) · [[DEF-035 District values mix Stadtbezirk and Stadtteil]] (minor, open, frontend mapping). [[DEF-033 Communities page drops heritage-language courses]] still applies: its repro still returns 11 rows.
