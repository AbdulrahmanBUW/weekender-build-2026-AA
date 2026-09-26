---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[RUN-007 Newcomer crawler first run]]"
owner: claude
---
# Defect: Brave place results stale or misclassified

## Observed
The place search "Ausländerbehörde Dresden" returned 3 rows that we saved as `category = 'auslaenderbehoerde'`:
1. "Ausländerbehörde Dresden", Lingnerallee 3: correct.
2. "Abteilung Staatsangehörigkeits- und Ausländerangelegenheiten", **Theaterstraße 11**: stale. dresden.de says the office moved to Lingnerallee 3 in May 2026.
3. "Ausländerrat Dresden e.V.": an NGO (migrant counselling), not the authority. The name filter `ausländer` matched it.

District values also contained ", Germany" / "Dresden-" (e.g. "Dresden-Altstadt, Germany").

## Expected
Only the real, current office is listed as Ausländerbehörde. NGOs appear under `community`.

## Fix
- *Place Jobs*: the ABH job now matches `ausländerbehörde|ausländerangelegenheiten|foreigners` and excludes `e.V.|verein|theaterstra`. The `exclude` regex is now also tested on the address.
- *Map Places to Rows*: district cleaned (strip ", Germany" and "Dresden-"; plain "Dresden" → null).
- DB: deleted the 2 wrong rows and cleaned districts with SQL. Pinned regression test (execution 14) keeps only Lingnerallee 3.
- Lesson: place data from search engines can lag behind official pages. Keep the "not verified" note in the app, prefer the guide (from dresden.de) for official addresses, and re-check key rows by hand before the demo.
