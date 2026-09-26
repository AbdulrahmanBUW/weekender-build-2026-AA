---
type: defect
date: 2026-09-26
status: fixed
severity: minor
found_in: "[[RUN-018 Heritage-language family offers seed]]"
owner: abdul
---
# Defect: Heritage-language seed overstated three details

## Observed
The independent fact-check of [[RUN-018 Heritage-language family offers seed]] opened the source page of every row. All 17 in-scope rows are real and active, but 3 rows said slightly more than their sources do:

1. **Le Rendez-vous e.V. (French, FLAM)**: `description_en` and all 5 translations said "Annual fee €50 per child plus €25 family membership". The registration page gives €25 **per family per year** and "€50 per child" **without a period**. The association's cost breakdown (`/view/le-rendez-vous-e-v-/finances`) works the €50 out **per child per semester**, so "annual" was a guess and probably wrong. `opening_hours` also said "Mon 15:30–17:00", but the page runs Science amusante and Mouvement "un lundi sur deux", so they alternate on Mondays.
2. **Akademie der polnischen Sprache (DPG Sachsen)**: the description listed "weekend workshops for ages 12–16" in the **2026** programme. On the page they appear only in the **2025** programme. The 2026 section names the adventure and theatre courses, new reading/writing and culture classes, and winter and summer camps.
3. **Schola ludus parent-and-child groups** (Pat's Colour Box, Händelallee 23, 01309): `district = 'Striesen'`. OpenStreetMap places the address in Neugruna, Stadtbezirk Blasewitz, not Striesen.

Nothing was invented: no fake names, phones or addresses. Each error came from generalising a dated or ambiguous source.

## Expected
Descriptions state only what the source says: no period for a fee when the source gives none, and no year for a programme item that the source dates to another year. `district` matches the address.

## Repro
Compare the rows with https://sites.google.com/view/le-rendez-vous-e-v-/accueil/inscriptions, https://dpg-sachsen.eu/unsere-arbeit/akademie-der-polnischen-sprache-in-dresden/ and an OSM lookup of "Händelallee 23, 01309 Dresden" (26 Sep 2026, 12:45).

## Fix
Fixed on 26 Sep 2026 at 12:50 with one UTF-8 SQL file (`fix018.sql`, scratchpad) that updated rows by id:
- Le Rendez-vous: "Fees: €50 per child plus €25 per family per year (reduced rates available)" in `description_en` and de/ru/uk/ar/tr; `opening_hours` now notes the alternating Mondays; `notes_en` gives the reduced rates and says to ask whether the child fee is per semester.
- Polish academy: description rewritten so that the 2026 and 2025 items are kept apart (en + 5 translations, 394 chars).
- Schola ludus groups: `district = 'Blasewitz'`.

A byte-exact read-back of all 17 rows showed only the intended fields changed, and anon REST returns the new Arabic/Cyrillic text intact. For future seeds: the generator should flag words like "annual", "weekly" or a year whenever the source sentence does not contain them.
