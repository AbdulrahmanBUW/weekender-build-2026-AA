---
type: run
date: 2026-09-26 12:45
by: claude (family places seed agent, for abdul)
result: pass
build: public.resources on Supabase ycyrtlzympxzlfcocazh (merge migration 20260926200000_merged_family_hub.sql). Seed SQL generated in the scratchpad (not committed)
---
# Run: Family places seed

## Goal
Seed **real** Dresden family places into `public.resources` for "Dresden mit Kind" ([[DEC-003 Merged concept]], [[Merged Concept]], taxonomy in [[Idea B - Dies-Das-Ana-Nas]]). Scope: `kita` (the city's Kita placement office plus real Kitas, including bilingual and international ones), `school` (international and bilingual schools, plus the school enrolment office for newly arrived children), `library` (city children's libraries), `playground`, and `family_place` (family centres, a family café, parenting counselling). Target: 15–22 verified rows. Every row needs an English description, `i18n` descriptions in de/ru/uk/ar/tr, and a working `source_url` that was opened.

## Steps
1. Read the merge migration (constraints for `category`, `audience`, `activity_categories`, `price_type`, `format`, `description_en` ≤ 600, `i18n` object, and `dedupe_key` = `category|lower(name)|lower(address)`).
2. Found candidates with WebSearch, then opened each place's **own** page or an official City of Dresden page (dresden.de, jugendinfoservice.dresden.de, bibo-dresden.de). dresden.de returns HTTP 503 to WebFetch, so those pages were fetched with `curl` or Python. Nothing from 116117, KV Sachsen, Doctolib, Jameda, Google Maps, Facebook or Instagram. No personal data: leaders' and staff names on the pages were left out.
3. Rejected after checking: DETI gGmbH ("deutsch-russisch Kita") and Slowo "Skaska" both turned out to be in Berlin and Frankfurt. The city's sign-language bilingual Kita (Maxim-Gorki-Straße 4) was skipped: its only source is a 2024 press release, and the Kita site returns 403. Großer Garten playgrounds were skipped because the park's official site has no playground page.
4. Map pins come from OpenStreetMap Nominatim: 23 lookups, about one per second, with an identifying user agent. The Alaunplatz pin is the OSM playground polygon (way 25806464). Löbtauer Strand has **no pin**: house number 18 is not in OSM and the street's midpoint would be misleading.
5. Wrote one UTF-8 file, `seed_family_places.sql`: `insert … on conflict (dedupe_key) do update set` (all columns), inside `begin/commit`. Ran it with `npx supabase db query --linked -f`. Ran it **three times**: the first run inserted the rows, the second tested that the upsert is idempotent, and the third applied the Kolibri text change (step 7).
6. Every row has `source = 'web_research'`, `retrieved_at = 2026-09-26 12:30+02`, and `notes_en` starting "Details from the provider's website / the City of Dresden website (retrieved 26 Sep 2026) — please verify before visiting." The notes also list extra pages used. `last_checked_at` / `last_check_outcome` were not touched.
7. Overlap check against rows from the parallel agents: [[RUN-018 Heritage-language family offers seed]] had already added Kolibri e.V. as `community` ("Interkultureller Familientreff") and as two `course` rows. The Kolibri `family_place` row was narrowed to the parent consultation hours and parent-toddler groups, and its `notes_en` points to the other rows. See [[DEF-036 Same provider listed in several categories]].

## Result
**22 rows**: kita 5 · school 3 · library 4 · playground 4 · family_place 6. The rows were not in the table before this run, so the upsert inserted them all.

| category | name | district | languages | ages | price | source |
|---|---|---|---|---|---|---|
| kita | Zentrale Beratungs- und Vermittlungsstelle – Amt für Kindertagesbetreuung | Leuben | de (free community interpreters) | – | unknown | dresden.de Kita registration page |
| kita | Kita Kleiner Globus (Ausländerrat Dresden e.V.; RU/DE and EN/DE immersion groups) | Südvorstadt | de ru en ar uk es ku ce az | – | unknown | kleiner-globus-dresden.de |
| kita | Evangelische Kita Lukas Dresden-Südvorstadt | Südvorstadt | de en ru | 1–6 | subscription | diakonie-dresden.de |
| kita | Dresden International School – Preschool | Blasewitz | en | 1–5 | subscription | dresden-is.de |
| kita | Kita SpielWerk (Studentenwerk) | Südvorstadt | de | 1– | unknown | studentenwerk-dresden.de |
| school | Dresden International School | Altstadt | en | 5–18 | subscription | dresden-is.de fees page |
| school | Romain-Rolland-Gymnasium Dresden (German-French bilingual, AbiBac) | Neustadt | de fr en | – | unknown | romain-rolland-gymnasium-dresden.de |
| school | Landesamt für Schule und Bildung, Standort Dresden – Besondere Bildungsberatung (audience both) | Pieschen | de | – | unknown | dresden.de "Kinder aus dem Ausland" + lasub.smk.sachsen.de |
| library | Zentralbibliothek im Kulturpalast (children's area) | Altstadt | de en fr ru es it zh tr ar fa ps | – | free | bibo-dresden.de |
| library | Bibliothek Neustadt | Neustadt | de | – | free | bibo-dresden.de |
| library | Bibliothek Gorbitz | Gorbitz | de | – | free | bibo-dresden.de |
| library | Bibliothek Johannstadt | Johannstadt | de | – | free | bibo-dresden.de |
| playground | Spielplatz Alaunplatz (Alaunpark) | Neustadt | – | – | free | dresden.de press release 2 Dec 2024 |
| playground | Waldspielplatz Albertpark | Neustadt | – | – | free | dresden.de "Ausgewählte Spielplätze" |
| playground | Spielplatz Löbtauer Strand (toddlers) | Löbtau | – | – | free | dresden.de "Ausgewählte Spielplätze" |
| playground | Abenteuerspielplatz Johannstadt (Kinderschutzbund) | Johannstadt | de | 6–14 | free | kinderschutzbund-dresden.de |
| family_place | Familienzentrum Pauline | Gruna | de | – | unknown | jugendinfoservice.dresden.de + pauline-dresden.de |
| family_place | Familienzentrum Altstadt (Familie(n)leben e.V.) | Altstadt | de | – | unknown | familienleben-dresden.de |
| family_place | Familienzentrum Brücke (Frauenförderwerk e.V.) | Südvorstadt | de | – | unknown | jugendinfoservice.dresden.de |
| family_place | Kinder- und Elternzentrum Kolibri e.V. | Altstadt | de ru uk en | – | unknown | kolibri-dresden.de |
| family_place | Kinder-, Jugend- und Familienzentrum Tanne (family café) | Gorbitz | de | – | unknown | tanne-dresden.de |
| family_place | Beratungsstelle für Kinder, Jugendliche und Familien Mitte (Erziehungsberatung, Jugendamt) | Johannstadt | de (interpreter on request) | – | free | dresden.de |

## Judgement calls (for review)
- **Library `languages`** on the Zentralbibliothek row are the languages of the children's books held by the city libraries (bibo-dresden.de "Medienangebot"), not languages spoken by staff. The branch rows use `{de}`, and their description says foreign-language children's books can be ordered from any branch for EUR 1.20.
- **Ages** are filled only where the source gives numbers. "Krippe + Kindergarten" alone was left null, as was the gymnasium, which states grades rather than ages. DIS school 5–18 comes from "Kindergarten (age 5–6) to Grade 12".
- **price_type**: `subscription` = monthly or yearly Kita parent fees and DIS tuition. `free` = library card for under-18s, free counselling, and public municipal playgrounds. The Alaunplatz and Abenteuerspielplatz sources say "kostenfrei". The two other city playgrounds are public municipal playgrounds (Amt für Stadtgrün), so `free` was inferred. Everything else is `unknown`.
- **district** uses the common Stadtteil name taken from the OSM address, e.g. Südvorstadt, Gruna, Leuben. The Albertpark is listed as Neustadt (its Stadtbezirk) rather than Radeberger Vorstadt.
- Kita SpielWerk moves to Michelangelostraße 5 in 2027. The address stays Am Beutlerpark 6 for now, and the move is in the description and `notes_en`.
- The DIS Preschool uses the DIS main phone number. No separate preschool number is published on the pages used.

## Verification
- `select … group by category, audience`: 22 rows; all have `i18n` with de/ru/uk/ar/tr; 22/22 have `source_url`; 21/22 have a pin; max `description_en` = 400 chars.
- Re-running the SQL left 22 rows and 22 distinct `dedupe_key` values, so the upsert is idempotent.
- Comparing the database with the generator's data file (name, phone, district, price, description, source, languages, activities, lat, Arabic text) found **0 mismatches**.
- Browser-like REST read with the **anon** key (`/rest/v1/resources?category=in.(kita,school,library,playground,family_place)&source=eq.web_research`) returned 22 rows with the Arabic text intact. An anon `POST` to `resources` returned HTTP 401, so row-level security still blocks browser writes.
- All 27 distinct `source_url` / `website` URLs returned HTTP 200 on 26 Sep 2026.
- Newcomer rows (`auslaenderbehoerde`, `doctor`, `pharmacy`, `bank`, `community`, `other`) were not touched by this run.
- Side note: dresden.de returns 200 to curl, python-urllib, "n8n" and axios user agents. Only the WebFetch tool gets 503, so an n8n link checker would not be affected.

## Defects found
- [[DEF-036 Same provider listed in several categories]]

## Verification (independent fact-check, 26 Sep 2026 13:00)
A second agent re-checked **every** row with `category in ('kita','school','library','playground','family_place')`, starting from the assumption that entries could be made up. There were 22 rows, all `source = 'web_research'` and all from this run. For each row, the agent opened `source_url` and `website` again with a plain HTTP client (27/27 returned 200 on 26 Sep 2026) and checked: the place exists in Dresden; the address, phone and opening hours match the page; the category fits; the languages and ages are supported by the source. The agent also checked every number and claim in `description_en` against the pages. Extra official pages were used: bibo-dresden.de (fees, registration, holdings), the operators' own sites (kleiner-globus-dresden.de /kontakt /konzept /mehrsprachigkeit; kolibri-dresden.de /eltern-kleinkind-gruppen; pauline-dresden.de /oeffnungszeiten; frauenfoerderwerk.de), dresden.de family counselling centres, and the city playground map (stadtplan.dresden.de). All 21 existing pins were reverse-geocoded with OpenStreetMap Nominatim. The 19 pins with a street address land on the stated street and house number. The two park pins are OSM playground areas: Alaunplatz next to the Bischofsweg, and Waldspielplatz Albertpark (way 27203225).

**Result: 22 checked · 22 real and in Dresden · 0 deleted · 0 fields nulled · 4 rows corrected.**

| row | finding | action |
|---|---|---|
| Zentralbibliothek im Kulturpalast | `languages` listed 11 book languages held across the city-library network, not languages staff speak | `languages` → `{de}`, book languages kept in description, `notes_en` reworded ([[DEF-037 Languages field used for book and subject languages]]) |
| Romain-Rolland-Gymnasium | `languages` included `en`, which is a taught subject, not a language of instruction (Spanish/Latin were not listed either) | `languages` → `{de,fr}`, `notes_en` explains ([[DEF-037 Languages field used for book and subject languages]]) |
| Spielplatz Löbtauer Strand | no pin; the city playground map has an entry for exactly this site ("Reisewitzer Straße 18 - Spielplatz": Mo–So 8–22, 0–12 years, 660 m², Stadtbezirk Cotta), linked from OSM way 227642054 | added `lat/lng` 51.0431599 / 13.7006448, `opening_hours` "Daily 8:00–22:00", ages 0–12, `notes_en` cites the map entry |
| Familienzentrum Brücke | `website` pointed to the city directory page (last changed July 2025); the operator's own page is current (September 2026 programme) and confirms the address and phone | `website` → frauenfoerderwerk.de page, `notes_en` updated |

Checked and correct as stored (sample of the claims checked): the counselling centre Mitte (hours, free/anonymous, interpreter incl. sign language, the other 4 centres exist); Familienzentrum Altstadt (office Mon/Wed 9–11, offers incl. the monthly writing café); Pauline (office hours incl. "longer during events", funded by the Jugendamt); Kolibri (consultation hours in DE/RU/UK/EN, the Russian parent-toddler group for ages 1.5–2.5 on Thursdays at 16:00 in the Villa der Kulturen); Tanne (family café with free book lending, groups from 4 months, sport from 18 months); DIS Preschool (ages 1–5, Goetheallee 18, walk-in every first Thursday) and DIS school (EUR 15,065 Grade 1 example, financial aid); Kita Lukas (118 places, ages 1–6, crèche at Einsteinstraße 2, team speaks DE/EN/RU); Kleiner Globus (4 immersion groups, 27 home languages, the 9 staff languages, 6:30–17:30); SpielWerk (180 places, MINT, open to all families, move to Michelangelostraße 5 in 2027); the Kita placement office (hours, 11 months, 5 preferred Kitas, free community interpreters, leaflets in EN/RU/UK/ES/FR); the 4 libraries (hours, holdings counts, EUR 1.20 order fee, free card up to 17, registration from age 6); the Abenteuerspielplatz (ages 6–14, Tue–Fri 14–18, free); Alaunplatz (press release of 2 Dec 2024); Albertpark (first used 1889, renovated 2021); LaSuB (Tue 13–18, what to bring); Romain-Rolland (address, phone, bilingual track since 1994, AbiBac). All 110 translations have the same numbers as `description_en` (checked by script; the only differences are number formatting, e.g. "15 065", "16 Uhr"). A spot-read of de/ru/uk/tr found no added claims. No staff names appear in any text field. `last_checked_at` / `last_check_outcome` are still null on all 22 rows.

Judgement calls left as they are: `district` "Südvorstadt" for Kita SpielWerk (OSM says Zschertnitz, but Wikipedia puts the Beutlerpark in the Südvorstadt); "Blasewitz" for the DIS Preschool (OSM says Neugruna, DIS itself says Blasewitz); `price_type = free` inferred for the two municipal playgrounds; `subscription` for Kita Lukas only (the other Kitas don't state fees on their pages).

Overlap across categories: only Kolibri e.V., already covered by [[DEF-036 Same provider listed in several categories]], whose description is accurate. The DIS and "Dresden International Church" name matches are false positives.

Final state: kita 5 · school 3 · library 4 · playground 4 · family_place 6 = 22; **22/22 with a map pin**; 22/22 with de/ru/uk/ar/tr. The fix SQL is `factcheck_run019/fix_run019.sql` in the scratchpad (not in the repo), and it was checked afterwards with a SELECT by id.

### Defects found (verification)
- [[DEF-037 Languages field used for book and subject languages]] (fixed)
- [[DEF-038 District mixes Stadtteil and Stadtbezirk names]] (open: the district filter splits Südvorstadt/Plauen, Gorbitz/Cotta, Johannstadt/Altstadt)
