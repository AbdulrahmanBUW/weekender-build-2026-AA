---
type: run
date: 2026-09-26 12:45
by: claude (events seed agent, for abdul)
result: pass
build: public.family_events on Supabase ycyrtlzympxzlfcocazh (merge migration 20260926200000_merged_family_hub.sql), seed file generated from scratchpad (not committed)
---
# Run: Family events seed

## Goal
Seed 10–20 **real** family and children's events in Dresden between 27.09. and 31.10.2026 into `public.family_events` for the "Dresden mit Kind" events list ([[DEC-003 Merged concept]], [[Merged Concept]]). Every row needs a date, time and place taken from a source page we actually opened, English text plus `i18n` in de/ru/uk/ar/tr, and an upsert on `dedupe_key`.

## Sources (all opened 26.09.2026, all return HTTP 200)
- **dresden.de Interkulturelle Tage programme** (`dresden.de/apps_ext/IKT/event/<uuid>`, official city calendar, 20.09.–11.10.): 9 events. Most are multilingual or intercultural: Spanish story time, a Spanish film with German subtitles, Institut français, family festivals.
- **Städtische Bibliotheken Dresden** (`bibo-dresden.de/de/events-kids/…`, `/events/…`): 7 events (picture-book cinema, readings, puppet show, Code Week, Gruffalo show).
- **Zoo Dresden** event pages: 2 events. Prices come from `zoo-dresden.de/besuch-planen/preise/`, because the event pages list none.
- **Dresdner Philharmonie** concert pages: 2 family concerts in the Kulturpalast.
- Not used: tjg. theater junge generation (the calendar is rendered by JavaScript and has no readable dates), DHMD (no family events in the window on shop.dhmd.de), SKD (no dated family afternoons shown), BIP school open day (Dresden only offers info sessions by appointment). No banned sources (Facebook, Instagram, Google Maps and so on) were used as sources.

## Steps
1. Collected candidates. For each event, opened the detail page and read the date, time, address, age, price and registration straight from the raw HTML (`curl`). Small-model summaries were not trusted: WebFetch had made up zoo prices, see below.
2. Districts: checked each address with OSM Nominatim and stored the **Stadtbezirk** (Altstadt, Neustadt, Pieschen, Blasewitz, Leuben, Cotta, Prohlis). This matches the PRD examples in [[Idea B - Dies-Das-Ana-Nas]] ("Neustadt, Altstadt, Blasewitz, Plauen…"), the existing `resources` rows and the parallel course seed. The finer Stadtteil can still be read from the address.
3. Times: Europe/Berlin, stored with `+02:00` before 25.10. and `+01:00` from 25.10. Checked with `starts_at at time zone 'Europe/Berlin'`: all 20 rows match their source.
4. Generated one UTF-8 SQL file (`INSERT … ON CONFLICT (dedupe_key) DO UPDATE`, `source='web_research'`, `url = source_url`, `retrieved_at = 2026-09-26 12:30+02`) and ran it with `supabase db query --linked -f`.
5. Verified with SELECTs. Re-ran the same file to check the upsert is idempotent.

## Result
**20 rows** in `family_events`, 27.09.–31.10.2026:

| Date (Berlin) | Event | Place (district) | Age | Lang | Price |
|---|---|---|---|---|---|
| Sun 27.09. 11–17 | Johannstadt Kite Festival | Elbwiesen am Fährgarten Johannstadt (Altstadt) | – | de | free |
| Sun 27.09. 14–18 | Intercultural family festival | KJH Chilli, Laubegast (Leuben) | – | de | free |
| Sun 27.09. 16–18:30 | El Cuentacuentos – stories and songs in Spanish | Asociación Cultural Iberoamericana (Neustadt) | 3+ | **es** | free |
| Mon 28.09. 16:30–17 | Picture-book cinema | Bibliothek Pieschen (Pieschen) | 3+ | de | free |
| Wed 30.09. 15:30–17:30 | Familien-Nami | Familienzentrum PAULINE (Blasewitz) | – | de | free |
| Wed 30.09. 16:30–18 | Family reading with Dayeon Auh (Korean folk tale) | Bibliothek Johannstadt (Altstadt) | 4–8 | de | free |
| Thu 01.10. 15–18 | Family afternoon with Max & Moritz | Bibliothek Blasewitz (Blasewitz) | 4+ | de | free |
| Fri 02.10. 16–17:30 | Fairy-tale hour: Carnival of the Animals | Institut français, Mediathek (Altstadt) | – | de | free, register by 30.09. |
| Sat 03.10. 10–12 | My window to the Amazon (workshop) | HAUS DER BRÜCKE (Neustadt) | 8+ | de | free, 10 places |
| Sat 03.10. 10–17 | Discovery Day at Zoo Dresden | Zoo (Altstadt) | – | de | zoo ticket |
| Sat 03.10. 11–12 | Brundibár – family concert | Kulturpalast (Altstadt) | – | de | €14 / €6 |
| Sun 04.10. 15:30–17 | Spanish film afternoon: Ferdinand | Filmgalerie Dresden (Blasewitz) | – | **es, de** subtitles | free |
| Sun 04.10. 16:30–17:15 | Enna Miau: The little autumn bee | Bibliothek Neustadt (Neustadt) | 4+ | de | free, register |
| Sat 10.10. 11–18 | Code Week Highlights – Coding for Families | Zentralbibliothek (Altstadt) | 6+ | de | free |
| Sat 10.10. 11–11:40 | The Three Little Pigs (puppet show) | Bibliothek Gorbitz (Cotta) | 3+ | de | free, register |
| Sat 10.10. 15–18 | Autumn festival with lantern parade | Familienzentrum PAULINE (Blasewitz) | – | de | free |
| Mon 12.10. 16–17 | The Gruffalo Show with Axel Scheffler | Zentralbibliothek, Kinderbibliothek (Altstadt) | 3+ | de | free |
| Sun 25.10. 11:00 | phil zu entdecken … im bunten Cellokasten | Kulturpalast (Altstadt) | 5+ | de | from €14 / €6 |
| Wed 28.10. 17–17:30 | Cuddly-toy cinema | Bibliothek Leubnitz-Neuostra (Prohlis) | 3–6 | de | free |
| Sat 31.10. 10–18:30 | Halloween at Zoo Dresden | Zoo (Altstadt) | – | de | zoo ticket |

Checks (SELECTs on the linked DB):
- `count(*) = 20`, `count(distinct dedupe_key) = 20`. After re-running the seed file it is still 20 rows, so the upsert is idempotent.
- 0 rows missing any of `de, ru, uk, ar, tr` in `i18n` (`i18n ?& array[…]`). The Arabic, Ukrainian and Russian titles come back intact through `db query`, with no encoding damage.
- 0 rows with `description_en` over 300 characters (the longest is 277). 0 rows without `source_url`.
- `curl` on all 20 `source_url`s returns HTTP 200. The IKT deep links work without a session cookie.
- `resource_id`: 1 of 20 linked. El Cuentacuentos now points to the resource "ACI – Asociación Cultural Iberoamericana e.V." (same address, Bischofsweg 74), which the parallel community seed added. The upsert does not touch `resource_id`, so re-running the seed keeps the link. The other 19 stay null: when this ran, `resources` had no library, zoo, Kulturpalast or family-centre rows. See the follow-up below.
- Not run: browser-style anon REST read and write-refusal tests on `family_events`. The auto-mode permission guard blocked REST calls with the anon key against the production project. The RLS setup comes from the migration: `select` for anon, writes revoked.

Data notes:
- The Dayeon Auh reading is listed as 16:30–17:30 on dresden.de/IKT and in the city press release, but as 16:30–18:00 on the library's own page. We store the organiser's page (18:00).
- WebFetch's summary of the zoo pages said "included with regular ticket (€19/€10)", but the raw event pages contain no price. The price text now cites the zoo's price page (summer day ticket: adults €19, children 3–16 €10) and says the event page lists no extra fee.
- The `family_events` table has no `notes_en` column, so the "please verify before visiting" hint cannot be stored per row. The UI should show `retrieved_at` ("checked 26 Sep") next to the source link.
- Parallel agents overwrote each other's scratch SQL files ([[DEF-042 Parallel agents share one scratchpad]]). This run used its own subfolder `scratchpad/run020_events/`.

Follow-up: when library, zoo or family-centre resources exist, link them with a name-based update, for example `update family_events e set resource_id = r.id from resources r where e.resource_id is null and r.category = 'library' and e.place_name = r.name;`. Check the matches before running it.

## Defects found
- [[DEF-039 family_events dedupe_key depends on session TimeZone]]

## Verification
Independent fact-check on 26.09.2026 (about 12:45) by claude (verification agent, for abdul). The starting assumption was that any row might be invented or have a wrong date.

**Result: 20 rows checked. 19 confirmed unchanged, 1 corrected, 0 deleted. No invented events.**

> **Correction to the results table above:** the 02.10. row is now "Heure du conte (French story hour): The Carnival of the Animals". It is held **in French** for **ages 3–7** (not `de`, not "–"). Details below and in [[DEF-040 Event language defaults to German when the source omits it]].

Method:
1. Read all 20 rows from the linked DB, including `starts_at` in UTC and in Europe/Berlin time.
2. Downloaded every `source_url` with `curl` without cookies (all 20 HTTP 200) and turned the raw HTML into text. Nothing came from small-model summaries.
3. A script parsed each page's own date and time format (IKT "Termine", bibo "DD.MM.YYYY, HH:MM - HH:MM", zoo, Philharmonie) and compared it with the DB. Each page was also read by eye for place, age, price, registration and the claims in the description.
4. Checked the UTC offsets separately with Python `zoneinfo`.
5. Opened extra pages where the event page lacked a field:
   - zoo address: `zoo-dresden.de/service/kontakt/`
   - zoo summer/winter price season: `zoo-dresden.de/besuch-planen/preise/`
   - "phil zu entdecken" age: `dresdnerphilharmonie.de/de/familie-schule/familienkonzerte/`
   - organiser sites for the IKT events: institutfrancais.de, johannstadtquartier.de, laubegast-ist-bunt.de
6. Checked 6 addresses against OSM Nominatim (Laubegast, zoo, Gruna, Leubnitz-Neuostra, Gorbitz, Johannstadt).
7. Scanned every page for abgesagt / ausverkauft / entfällt / verschoben / Restkarten.
8. Compared the numbers (times, ages, dates) in each `i18n` description with `description_en`.

| Check | Result |
|---|---|
| Event exists on its source page | 20/20 |
| Date, start and end in Berlin time match the source | 20/20. Brundibár's end (12:00) comes from "Dauer ca. 1 Std."; Cellokasten gives no end, so it stays null. |
| UTC offset | 17 rows at +02:00 (27.09.–12.10.), 3 rows at +01:00 (25.10., 28.10., 31.10.). All correct. |
| Place and address | 20/20. Kulturpalast "Schloßstraße 2 (Eingang Altmarkt)" is as printed on the Philharmonie page. Zoo "Tiergartenstraße 1, 01219" is from the zoo's contact page. |
| District (Stadtbezirk) | 6/6 spot checks match Nominatim `city_district` (the zoo is in Altstadt, suburb Johannstadt). |
| Age | 19/20. **Row 02.10. was wrong** (the organiser says 3–7). "Ab 5 Jahren" for Cellokasten is confirmed on the series page. |
| Price | 20/20. The zoo summer season runs 01.03.–31.10., so the €19 / €10 price also applies to Halloween (31.10.). Brundibár "Restkarten" is confirmed. |
| Language | 19/20. **Row 02.10. was wrong** (`de`; the organiser says "Auf Französisch!"). |
| `i18n` | Complete for de/ru/uk/ar/tr, nothing garbled, numbers consistent. The ru/uk "2nd floor" for the German "1. OG" is correct localisation. |
| Cancelled or sold out | None. |
| Window 27.09.–31.10.2026 | 20/20 inside. |
| `dedupe_key` format | 20/20 end in `+00`: every write so far came from a UTC session (the `db query` session is UTC). This confirms the mechanism behind DEF-039, but no duplicate exists. |

Correction applied (UTF-8 file `scratchpad/run020_verify/fix_row8_french_story_hour.sql`, not in the repo), row `17a05fce-4dab-4ac2-898c-9d89d54cd1af`:
- title "Fairy-tale hour: The Carnival of the Animals" → "Heure du conte (French story hour): The Carnival of the Animals". The trigger rebuilt `dedupe_key` in UTC.
- `languages` `{de}` → `{fr}`; `age_min_years`/`age_max_years` null → 3 / 7; `activity_categories` now also include `languages`.
- `url` and `source_url` → `https://www.institutfrancais.de/de/dresden/event/heure-du-conte-29164` (organiser page, opened 26.09.). The IKT page is still correct for date, time and the registration deadline of 30.09.
- `description_en` (278 characters) and all 5 `i18n` titles and descriptions now say "in French, ages 3–7". `price_text` now reads "registration requested (by 30 Sep per the city's calendar)". `retrieved_at` = now.
- Date, time and place are unchanged; both sources agree.

State after verification: 20 rows, 20 distinct keys, first 27.09. 11:00, last 31.10. 10:00 (Berlin). 16 free, 4 paid. Languages: `de` 17, `es` 1, `es+de` 1, `fr` 1. 0 rows with incomplete `i18n`, 0 rows with `ends_at < starts_at`, 0 rows without `source_url`.

Verification notes:
- **Do not re-run the builder's scratch seed** (`run020_events/seed_family_events.sql`). It still has the old title, and the title is part of `dedupe_key`, so it would insert a second, wrong row. If a seed file is needed, regenerate it from the DB.
- **DST trap in the Dresdner Philharmonie's structured data:** the JSON-LD on the 25.10. concert page gives `startDate` `2026-10-25T11:00:00+02:00`. DST ends at 03:00 that morning, so 11:00 is +01:00 (10:00 UTC). The DB row is correct because it was taken from the visible "11.00 Uhr". Any crawler (for example an n8n workflow) must build timestamps from the local time plus Europe/Berlin rules and not trust JSON-LD offsets near 25.10.
- Dayeon Auh ends at 17:30 on the IKT page and at 18:00 on the library page. The builder's choice (the organiser's library page, 18:00) is kept.
- `de` on the other 17 rows is stated or clearly implied by the German programme text. The one exception is "My window to the Amazon" (BluoVerda, 03.10.): the organiser's site is JavaScript-only, so `de` there is only the city calendar's implied language and is not verified.
- The builder's report said "14 free". The DB has 16 free and 4 paid; the two free events with registration and a place limit are counted as free.
- Not run: the anon REST read and write-refusal test, for the same permission-guard reason as above.

### Defects found (verification)
- [[DEF-040 Event language defaults to German when the source omits it]]
