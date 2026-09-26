---
type: run
date: 2026-09-26 12:35
by: claude (courses seed agent, for abdul)
result: pass
build: public.resources on Supabase ycyrtlzympxzlfcocazh (merge migration 20260926200000_merged_family_hub.sql). Seed SQL generated in the scratchpad (not committed)
---
# Run: Family courses seed

## Goal
Seed 15–20 **real** Dresden providers of children's activities into `public.resources` for the Courses pillar of "Dresden mit Kind" ([[DEC-003 Merged concept]], [[Merged Concept]], taxonomy in [[Idea B - Dies-Das-Ana-Nas]]). This run uses `category = 'course'` and `audience = 'family'` and covers music, dance, sport, swimming, yoga, art, theatre/circus, STEM and nature. Language and heritage-language classes are **out of scope**, because another agent covers them. Every row needs a working `source_url` that we opened, English text, and an `i18n` description in de/ru/uk/ar/tr.

## Steps
1. Found candidates with web search. For each one we opened the provider's **own** site (or the municipal operator's page) and read the name, address, phone, ages, prices and languages from the raw HTML with `curl`. Small-model summaries were not trusted. The only page read through WebFetch was the Wix page of Naturcamp, and it was checked against its raw HTML afterwards. We did not use 116117, KV Sachsen, Doctolib, Jameda, Google Maps, Facebook or Instagram, and we stored no private individuals (no teacher names).
2. Districts: we checked every street address with OSM Nominatim. All 16 matched at house-number level. We store the **Stadtbezirk** (Neustadt, Altstadt, Blasewitz, Prohlis, Loschwitz, Leuben), which matches the existing `resources` rows and [[RUN-020 Family events seed]]. `lat`/`lng` come from the same lookup (© OpenStreetMap contributors).
3. Conventions used:
   - `languages` lists only languages the provider **states**. We assume `de` when the site is German-only.
   - `price_type`: `trial_available` if the provider states a trial lesson, else `subscription` for membership or monthly fees, `per_session` for a fixed fee per course (the swim courses), and `unknown` otherwise. The fee model is lost for providers that have both a fee and a trial, see [[DEF-030 price_type cannot express fee plus trial]].
   - Ages are filled only when the site states them.
   - `format = 'recurring_course'` for all rows.
   - `notes_en` starts with the verify notice and adds provider caveats.
4. Wrote one UTF-8 SQL file (`INSERT … ON CONFLICT (dedupe_key) DO UPDATE SET` every field, `source = 'web_research'`, `retrieved_at = 2026-09-26 12:00+02`) and ran it with `npx supabase db query --linked -f`. We ran it three times (see Verification). It is idempotent.

## Result
**18 rows**, all `category='course'`, `audience='family'`, `source='web_research'`:

| Provider | Sub | District | Ages | Languages | Price type | Source |
|---|---|---|---|---|---|---|
| Heinrich-Schütz-Konservatorium Dresden | musikschule | Neustadt | – | de | unknown | hskd.de/en/ |
| Musikschule Adagio Dresden | musikschule | Leuben | 2+ | de, en, ru, uk, ko | trial_available | musikschule-adagio.de (piano page) |
| Musikschule tune in | musikschule | Blasewitz | – | de, en, it | trial_available | musikschule-tune-in.com |
| Schwimmschule Funk – Dresden | schwimmschule | Altstadt | – | de | per_session | schwimmschule-funk.de/dresden |
| DRK Wasserwacht Dresden – Kinderschwimmkurse | schwimmkurs | Altstadt | 5–16 | de | per_session | drk-dresden.de (Kinder-Schwimmkurse) |
| Dresdner Bäder – Schwimmlernkurse Kinder (Kombibad Prohlis) | schwimmkurs | Prohlis | 5–18 | de | per_session | dresdner-baeder.de (learning courses) |
| Jugendkunstschule Dresden – JKS Schloss Albrechtsberg | jugendkunstschule | Loschwitz | 4–18 | de | trial_available | jks-dresden.de/jks-schloss |
| Jugendkunstschule Dresden – JKS Palitzschhof | jugendkunstschule | Prohlis | 4–18 | de | unknown | jks-dresden.de/jks-palitzschhof |
| elbhang.yoga – Kinderyoga | kinderyoga | Loschwitz | 6–12 | de | trial_available | elbhang.yoga/kinderyoga |
| Sport- und Tanzstudio Dresden | tanzschule | Prohlis | – | de | trial_available | sport-tanz-dresden.de |
| Kinder- und Jugendzirkus KAOS | kinderzirkus | Blasewitz | – | de | unknown | kindervereinigung-dresden.de/kaos/ |
| Liga der Roboter Dresden | robotik | Altstadt | 5–10 | de | subscription | ligaderroboter.de/dresden |
| TanzZentrum Dresden e.V. | tanzschule | Altstadt | 3+ | de | trial_available | tanzzentrum-dresden.de (Kindertanz) |
| Ballettstudio ESPIRAL | ballettschule | Neustadt | 4–15 | de | trial_available | ballettstudio-espiral.de (Stundenplan) |
| KiDDs Kindersportverein Dresden | kindersport | – (20+ gyms) | 1–14 | de | trial_available | kidds.info/sportangebot |
| Dresdner Sportclub 1898 e.V. – Allgemeines Turnen | sportverein | Altstadt | 2–18 | de | subscription | dsc1898.de (Allgemeines Turnen) |
| Wildnisschule Naturcamp Dresden – Wildnisbanden | naturgruppe | – (Dresdner Heide) | 7–14 | de | subscription | naturcamp-dresden.de/wildnisbanden |
| Pegasus-Theaterschule | theaterschule | Blasewitz | 4+ | de | subscription | pegasus-theaterschule.de |

Activity coverage: music 4, dance 6, sport 4, swimming 3, art 2, theatre 3, yoga 1, stem 1, nature 1, parent_baby 2 (some rows have several categories). Useful for internationals: Adagio (teachers in en/ru/uk/ko) and tune in (en/it). Dresdner Bäder states that **children must understand German**. We put that in the description so the UI shows it honestly.

Candidates we checked and dropped:
- Yoga-Shanthi (kids yoga in de/en): the site showed a WordPress error, so we could not verify it.
- Bewegungsraum kids yoga: it is in Freital-Pesterwitz, outside Dresden.
- swimZen: its site publishes no pool location, only an office address.
- Technische Sammlungen "Ich mach' Technik!": free STEM clubs, but all of them are fully booked and the museum closes from 2 Nov 2026.
- tjg. theater junge generation: the club info is rendered by JavaScript and could not be read.
- Projekttheater kids workshop: we only found it in a March 2026 news item.
- Waldzeiten Naturschule: it offers programmes for Kitas and schools only.

Not yet checked (good next candidates): Hopsefrosch, Kinderprojekt Dresden, Sport & Jugend Dresden e.V., Zebra Musikschule, Tanzlabor, Kinder- und Jugendtanzstudio der TU Dresden.

Provider caveats (also stored in `notes_en`):
- Liga der Roboter's page names both Budapester Straße 3 and 5, and gives two different phone numbers. We store no phone.
- Naturcamp's Heidefüchse text reads "März und Dezember 204" (the year is unclear). The description tells parents to check that the group still runs.
- JKS Palitzschhof is closed on Fridays.

## Verification
- `count(*)` = 18 for `category='course' and source='web_research'` at our `retrieved_at`. All 18 are `audience='family'`, have 18 distinct `dedupe_key` values, `description_en` ≤ 400 chars and all five `i18n` keys (`i18n ?& array['de','ru','uk','ar','tr']`). 16 have `lat`/`lng`. KiDDs and Naturcamp have no single address on purpose.
- Other categories are unchanged (auslaenderbehoerde 1, bank 14, community 15, doctor 14 both + 24 newcomer, pharmacy 16).
- Browser-style REST check with the anon key: `category=eq.course&audience=eq.family&activity_categories=cs.{swimming}` returns the 3 swim rows with Arabic descriptions intact. An anon `PATCH` on a course row returns **401**, and the row stays unchanged.
- All 27 distinct `source_url`/`website` URLs return HTTP 200 (curl, 26 Sep 2026).
- Re-running the SQL file (3×) keeps 18 rows. The upsert is idempotent.
- The first run stored **no coordinates**. Another parallel agent had overwritten `geo.json` (and `geo.py`) in the shared scratchpad between our geocoding and the SQL generation. We moved everything into `<scratchpad>/run017/` with unique file names and re-ran. This is the same issue as [[DEF-042 Parallel agents share one scratchpad]].
- For a moment during verification, one course row had `last_checked_at` set. Another agent's Ask-for-me test had touched it, and a minute later it was cleaned up (0 rows). This run never writes `last_checked_at` or `last_check_outcome`.

## Defects found
- [[DEF-030 price_type cannot express fee plus trial]]
- [[DEF-031 resources has one address per provider]]
- [[DEF-042 Parallel agents share one scratchpad]] (existing, hit again)

## Verification (independent fact-check)
*26 Sep 2026, by a separate fact-check agent. The builder's rows were treated as possibly wrong or stale.*

**Scope:** every `resources` row with `category='course'` and no `languages` activity. That is the same 18 rows as above.

**Method**
- Opened every `source_url` and `website` again (27 URLs, all HTTP 200) and followed each provider's own sub-pages where needed: ESPIRAL course terms, the Dresdner Bäder pool page, the HSKD "Who we are" page, the JKS contact page, the KiDDs imprint, the Liga price list, the Naturcamp imprint and donations page, the TanzZentrum contact page and Adagio's dance page.
- Read the facts from the raw HTML with `curl`, not from a model summary. The KAOS weekly timetable exists only as an image on its page, and it was read directly.
- Checked that each organisation exists, is in Dresden, has the stored address and phone, and really runs children's activities. Also checked ages, languages, `price_type`, categories and every number in `description_en`.
- Geocoded all 16 street addresses again with OSM Nominatim. Every stored Stadtbezirk and coordinate matches (HSKD and DRK are within about 50 m).
- Checked that the numbers in all five `i18n` descriptions match the English text. They match; where a translation writes a number as a word, that is correct.
- All files were kept in a private folder (`<scratchpad>/verify017_fc/`) so that [[DEF-042 Parallel agents share one scratchpad]] could not happen again.

**Counts:** 18 checked · 12 correct as seeded · 6 fixed · 0 deleted. Every provider is real, is in Dresden (Naturcamp's forest, the Dresdner Heide, is inside the city) and offers children's activities.

**Fixes** (one UTF-8 SQL file of `UPDATE … WHERE id=…`, run with `npx supabase db query --linked -f`):

| Row | What was wrong | Fix |
|---|---|---|
| Dresdner Bäder – Schwimmlernkurse Kinder | The description named only 2 pools. The page lists children's beginner courses at **5** pools (Schwimmsportkomplex, Kombibad Prohlis, Klotzsche, Bühlau, Nordbad). It also left out the water-confidence course for ages 3–5 on the same page. | Rewrote `description_en` and all 5 `i18n` texts, changed `age_min_years` from 5 to **3**, and listed the other pools in `notes_en` |
| Dresdner SC 1898 – Allgemeines Turnen | "Groups up to age 18" read like an open group. The page says the 6–18 group is **competitive gymnastics for girls**: competitions are mandatory and it costs EUR 30 a month. | Rewrote `description_en` and all 5 `i18n` texts |
| Heinrich-Schütz-Konservatorium | No ages were stored, but the HSKD "Who we are" page says its early-years classes run from age 0 (baby courses). | Set `age_min_years = 0` and added the source to `notes_en` |
| Kinder- und Jugendzirkus KAOS | No ages were stored, but the timetable on the page shows Minizirkus 3–6, Kinderzirkus 6–11, Jugendzirkus 11+ and a show group 8+. | Set `age_min_years = 3` and put the groups in `notes_en` |
| JKS Palitzschhof | The Friday closure is real, but it is stated only on the JKS **contact** page. The location page still shows a Friday 10–11 viewing slot. | `notes_en` now names the source, notes the conflict and says "call ahead" |
| Schwimmschule Funk – Dresden | The stored phone number belongs to the head office in **Darmstadt**, and the note did not say so. | `notes_en` now says so |

**Checked and left unchanged**
- The DRK `source_url` redirects to a different site (drk-kurs.de). Browsers follow the redirect, but WebFetch does not follow redirects to another host.
- Adagio has a dance page, but it says the school is still looking for a dance trainer, so `dance` was **not** added.
- Liga der Roboter's Dresden page lists only LEGO robotics, for ages 5–10. The Roblox (9–12) and Minecraft (8–10) ages appear only on the network-wide price page, so `age_max_years` stays at 10.
- HSKD is a registered association (e.V.) that calls itself the Saxon capital's music college, so "municipal" was kept.
- Pegasus's news section stops at 2020/21, but a teacher biography says "since 2025" and there are uploads from 2026, so the school is still running.
- After the fixes, a new query shows: 18 rows, all with the five `i18n` keys, the longest `description_en` at 397 characters, and `last_checked_at` empty on every row. An anon REST read of the Bäder row returns the new age and the Arabic text intact.

**Corrections to this note's table above:** the Dresdner Bäder ages are now **3–18**, KAOS is **3+** and HSKD is **0+**. [[DEF-031 resources has one address per provider]] said Dresdner Bäder has 2 pools; it has 5, and the defect note is corrected. No new defect was found, so DEF-032 was not used.
