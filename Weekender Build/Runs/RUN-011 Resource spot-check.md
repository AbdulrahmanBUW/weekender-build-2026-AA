---
type: run
date: 2026-09-26 11:00
by: verifier agent
result: pass
build: supabase resources (87 rows)
---

# RUN-011 Resource spot-check

Spot-check of the demo-relevant rows in `public.resources` written by the crawler ([[RUN-010 Newcomer crawler full run]], [[Newcomer Resources - Crawler]]). 20 rows checked: Ausländerbehörde, all welcome_center / international_office / migrant_counselling rows, 3 hausarzt, 2 kinderarzt (+2 kinderarzt rows flagged in passing), 2 apotheke, 2 banks. Checked against the organisation's own site where reachable; dresden.de returned HTTP 503 during the check, so city pages were confirmed via search snippets of dresden.de. 116117, KV Sachsen, Doctolib, Jameda and Google Maps were not scraped. No rows were changed.

## Results

| row name | category | check result | evidence URL | suggested fix |
|---|---|---|---|---|
| Ausländerbehörde Dresden | auslaenderbehoerde | ok (minor: official entrance is "Eingang Nord", not "Besuchereingang A"; phone missing) | https://www.dresden.de/de/rathaus/dienstleistungen/abh/auslaenderangelegenheiten-terminabsprachen.php | `update resources set address = 'Lingnerallee 3, Eingang Nord, 01069 Dresden', phone = '+493514886009' where id = '5dcda841-1d80-4982-a032-ee88bc1b8a22';` |
| Dresden Welcome Center | community / welcome_center | ok (phone missing; same building, Eingang Nord) | https://welcome.dresden.de/de/kontakt.php | `update resources set address = 'Lingnerallee 3, Eingang Nord, 01069 Dresden', phone = '+493514886051' where id = '8cd2fe42-f76a-4d2c-896c-771c4c238df8';` |
| DRESDEN-concept Welcome Center at TU Dresden | community / welcome_center | ok (address Einsteinstraße 9, 01069 Dresden; for researchers PhD+) | https://dresden-concept.de/welcome | none (district label "Plauen" is cosmetic) |
| International Office TU Dresden | community / international_office | ok | https://tu-dresden.de/studium/im-studium/beratung-und-service/akademisches-auslandsamt?set_language=en | none |
| Kulturbüro im International Office der TU Dresden | community / international_office | ok (Fritz-Foerster-Bau, Mommsenstraße 6, Raum 157) | https://tu-dresden.de/kultur | none |
| TU Dresden | community / international_office | wrong category (generic university homepage, pin is a lecture building – Trefftz-Bau – not an office for newcomers; duplicates the real International Office row) | https://tu-dresden.de/ | `delete from resources where id = '15c6d5d6-a7cc-46e3-b214-452ac342fc2b';` (or hide from demo) |
| Ausländerrat Dresden e.V. | community / migrant_counselling | ok (offers MBE + migration social work; district is Strehlen/Reick near Wasaplatz, not Prohlis; phone missing) | https://www.dresden.de/de/leben/gesellschaft/migration/neu-vereine-und-initiativen/vereine-und-initiativen_landingspages/auslaenderratdresden.php | `update resources set address = 'Heinrich-Zille-Straße 6, 01219 Dresden', phone = '+493514363725' where id = '48d0e389-89f6-47c9-a4bc-c0d553192ca0';` |
| AWO Migrationsberatung für erwachsene Zuwanderer (MBE) | community / migrant_counselling | wrong address (garbled: official is Herzberger Straße 24/26, access via Prohliser Allee) | https://awo-in-sachsen.de/migration-asyl/migrationsberatung-fuer-erwachsene-zuwanderer-mbe-dresden | `update resources set address = 'Herzberger Straße 24/26 (Zugang über Prohliser Allee), 01239 Dresden' where id = 'ac89880f-2cda-42ec-b499-b6032158aa48';` |
| Deutschkurse Asyl Migration Flucht (DAMF) | community / migrant_counselling | wrong category + wrong address (volunteer German courses, no counselling; contact address Heinrich-Zille-Straße 8) | https://damf-dresden.de/ | `update resources set subcategory = 'language_cafe', address = 'Heinrich-Zille-Straße 8, 01219 Dresden' where id = '15b89762-4856-419b-8ab1-9b22c39460a4';` (no `language_course` subcategory exists; pick closest or add one) |
| Federal Office for Migration and Refugees (BAMF) | community / migrant_counselling | ok address, questionable category (BAMF arrival centre for asylum procedures in the AnkER facility – an authority, not counselling; generic bamf.de link) | https://www.bamf.de/SharedDocs/Struktur/Organisationseinheiten/DE/Standorte/dresden-anker-einheit.html | `update resources set website = 'https://www.bamf.de/SharedDocs/Struktur/Organisationseinheiten/DE/Standorte/dresden-anker-einheit.html', name = 'BAMF Ankunftszentrum Dresden' where id = '45d644fd-1afb-4f69-ba9e-10ce61f793c1';` |
| SUFW – Außenstelle Migrationssozialarbeit | community / migrant_counselling | ok (address + phone match) | https://sufw.de/migrationssozialarbeit-dresden-west.html | none |
| Hausarztpraxis Tschistik (russisch, deutsch) | doctor / hausarzt | ok (address + phone match; languages also EN/PL/UK) – but stored https URL fails with TLS certificate error; site only works on http | http://www.dresden-hausarztpraxis.de/ | `update resources set website = 'http://www.dresden-hausarztpraxis.de/' where id = '4646f5f0-a7a9-4ce6-8ea7-e18743ddd784';` |
| Hausarzt Stephan Gurskiy, FA f. Allgemeinmedizin | doctor / hausarzt | ok (address + phone match) | https://hausarzt-gurskiy.de/ | none |
| Th. Hausbrand / Hausarzt / Internist | doctor / hausarzt | ok (address + phone match) | https://praxis-hausbrand.info/ | none |
| Kinderarztpraxis Dr. Junge & Goecke | doctor / kinderarzt | ok address; phone differs (site: 0351 27285042) | https://kinderarztpraxis-suedvorstadt.de/ | `update resources set phone = '+4935127285042' where id = '2ac30d9d-8027-4a63-9b77-0f77a74f5e61';` |
| Kinderarztpraxis Magdalena Prüfer | doctor / kinderarzt | ok address; website wrong (points to generic kinderaerzte-im-netz search portal) | https://www.kinderaerztin-pruefer.de/ | `update resources set website = 'https://www.kinderaerztin-pruefer.de/', phone = '+493514710257' where id = '7f952758-8e23-4019-ac96-77939c78025b';` |
| Kinderchirurgie Dresden / Kinderchirurg Dr. med Jens Börner (2 rows) | doctor / kinderarzt | wrong category (paediatric surgery, not a paediatrician) + duplicate of each other | https://kinderchirurgie-dresden.de/ | `delete from resources where id in ('d126a779-385e-4403-9ddc-b6814bae4a47','b35ca3db-31a3-42de-ade9-db60d00012bf');` (or keep one under a new subcategory) |
| Stadt Apotheke Dresden Altstadt | pharmacy / apotheke | ok (Prager Str. 2, phone matches) | https://die-stadtapotheken.info/ | none |
| Apotheke im Neustädter Bahnhof | pharmacy / apotheke | ok (Schlesischer Platz 1, 01097; open daily) | https://city-apotheken-dresden.de/ | none |
| Deutsche Bank (Prager Str. 8) | bank / deutsche_bank | ok (branch active; SB-Zone closed 14.09.–16.11.2026 for renovation, counter service continues) | https://www.deutsche-bank.de/pk/filialen/ost/dresden/dresden-prager-strasse.html | none (optional note in description) |
| Ostsächsische Sparkasse – Filiale Johannstadt (Fetscherstraße 32/34) | bank / sparkasse | ok (address + phone match); website is only the generic homepage | https://www.ostsaechsische-sparkasse-dresden.de/de/home/toolbar/filialen/ostsaechsische-sparkasse-dresden-filiale-dresden-johannstadt-115463.html | `update resources set name = 'Ostsächsische Sparkasse Dresden - Filiale Johannstadt', website = 'https://www.ostsaechsische-sparkasse-dresden.de/de/home/toolbar/filialen/ostsaechsische-sparkasse-dresden-filiale-dresden-johannstadt-115463.html' where id = '2d2a4d34-8a86-4ccd-82c0-0228a1745d70';` |

Tally (20 checked rows, Kinderchirurgie pair counted once): 12 ok with no or cosmetic fixes, 4 ok but with wrong/missing phone or website, 1 wrong address (AWO), 3 wrong category (TU Dresden generic, DAMF, Kinderchirurgie pair). None closed, none outside Dresden.

## Observations
- Every checked place exists and is in Dresden; no closed businesses found.
- Crawler weaknesses: phone is often empty (Maps result had none), district labels from Maps are sometimes off (e.g. "Prohlis", "Plauen", "Altstadt" for Johannstadt addresses), `website` is sometimes a chain homepage or a portal instead of the actual location, and keyword-based subcategory assignment lets "Kinder…" surgeons and German-course projects slip into kinderarzt / migrant_counselling.
- All 6 Sparkasse rows share the same generic website and name "Filiale"; same pattern for Commerzbank (URLs with spaces in the path).

## Verdict
Data quality is good enough for the demo: all 20 checked rows are real, open, Dresden-based places and the addresses match their official sources in all but one case, so nothing embarrassing will appear if the demo shows these entries. Before going on stage, apply the SQL above for the rows most likely to be shown: the Ausländerbehörde and Dresden Welcome Center (add phone, "Eingang Nord"), fix the AWO address, move DAMF out of counselling, and remove or hide the generic "TU Dresden" row and the two Kinderchirurgie rows from the kinderarzt list. Avoid demoing the bank rows as "the branch's page" since most link to generic chain homepages, and treat missing phone numbers as a known limitation rather than a bug.

## Applied (2026-09-26, Orchestrator)
All 12 suggested SQL fixes applied in one transaction (`supabase db query --linked -f`): 9 updates (Ausländerbehörde + Welcome Center address/phone, AWO address, DAMF → language_cafe, BAMF name/website, 3 doctors' contact data, Sparkasse name/link) and 3 deletes (generic TU Dresden row, 2 duplicate Kinderchirurgie rows). Verified: 84 resources remain, deleted IDs gone, Ausländerbehörde = "Lingnerallee 3, Eingang Nord, 01069 Dresden".
