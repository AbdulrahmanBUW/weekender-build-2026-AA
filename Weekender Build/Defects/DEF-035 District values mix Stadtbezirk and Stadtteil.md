---
type: defect
date: 2026-09-26
status: open
severity: minor
found_in: "[[RUN-018 Heritage-language family offers seed]]"
owner: abdul
---
# Defect: District values mix Stadtbezirk and Stadtteil

## Observed
`resources.district` holds names from two levels of Dresden's geography. Most rows use a **Stadtbezirk** (Altstadt 27, Neustadt 27, Blasewitz 9, Plauen 4, Prohlis 4, Leuben 2, Loschwitz 2, Pieschen 2, Cotta 1). Some use a **Stadtteil** that lies inside one of those Stadtbezirke:

| Value in the table | Rows | Lies inside Stadtbezirk |
|---|---|---|
| Johannstadt | 5 | Altstadt |
| Südvorstadt | 4 | Plauen |
| Gorbitz | 2 | Cotta |
| Gruna | 1 | Blasewitz |
| Löbtau | 1 | Cotta |
| Weißer Hirsch | 1 | Loschwitz |

(Counts from 26 Sep 2026, 12:52, all audiences. A "Striesen" row was corrected to Blasewitz in [[DEF-034 Heritage-language seed overstated three details]].)

[[Frontend and UX Plan v3 (merged)]] builds the district filter from the distinct `district` values and matches with **equals**. A parent in Johannstadt who picks "Altstadt" therefore misses the Friedensschule (Arabic) and the Eritrean community (Tigrinya), because both rows say Johannstadt. A parent who picks "Plauen" misses the 4 Südvorstadt rows. The dropdown also shows parts and wholes side by side ("Altstadt" and "Johannstadt"), which is confusing for someone new to the city.

The PRD ([[Idea B - Dies-Das-Ana-Nas]]) allows "Stadtbezirke/Stadtteile", and the seed tasks said "district = Dresden Stadtteil". So each seed was right by its own rule, but the rules together do not give one filterable level.

## Expected
The district filter returns every place inside the chosen area, and the dropdown lists one level only.

## Repro
```sql
select district, count(*) from public.resources where district is not null group by 1 order by 1;
```
→ the list above. Then open `/courses?district=Altstadt` or `/communities?district=Altstadt`: the rows with `district = 'Johannstadt'` are missing.

## Fix
For Sunday (frontend only, no DB change): in the filter, map Stadtteil to Stadtbezirk before comparing, i.e. Johannstadt→Altstadt, Südvorstadt→Plauen, Gorbitz→Cotta, Löbtau→Cotta, Gruna→Blasewitz, Striesen→Blasewitz, Weißer Hirsch→Loschwitz. Then build the dropdown from the 10 Stadtbezirke (Altstadt, Neustadt, Pieschen, Klotzsche, Loschwitz, Blasewitz, Leuben, Prohlis, Plauen, Cotta) and keep showing the stored Stadtteil on the card. Later: add a `stadtbezirk` column filled by a migration and require it in seed scripts.
