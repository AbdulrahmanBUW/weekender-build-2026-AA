---
type: defect
date: 2026-09-26
status: open
severity: minor
found_in: "[[RUN-019 Family places seed]]"
owner: abdul
---
# Defect: District mixes Stadtteil and Stadtbezirk names

## Observed
Found during the independent fact-check of [[RUN-019 Family places seed]]. Pins were reverse-geocoded with OpenStreetMap, which returns both the Stadtteil and the Stadtbezirk. `resources.district` mixes two levels of Dresden geography:

- **Stadtbezirk** (the 10 city boroughs): Altstadt, Neustadt, Plauen, Prohlis, Cotta, Loschwitz, Leuben, Pieschen, Blasewitz.
- **Stadtteil** (the smaller quarters inside a borough): Johannstadt, Südvorstadt, Gorbitz, Gruna, Löbtau, Striesen, Weißer Hirsch.

On 26 Sep 2026 the table had these values: Altstadt 27 · Neustadt 27 · Blasewitz 8 · Johannstadt 5 · Südvorstadt 4 · Plauen 4 · Prohlis 4 · Gorbitz 2 · Leuben 2 · Loschwitz 2 · Pieschen 2 · Löbtau 1 · Striesen 1 · Gruna 1 · Weißer Hirsch 1 · Cotta 1 · null 48.

The rows from RUN-019 alone use both levels: "Altstadt" for Seevorstadt and Wilsdruffer Vorstadt addresses, next to "Johannstadt", which is itself a Stadtteil of Altstadt.

In [[Frontend and UX Plan v3 (merged)]], the district filter is an **equals** match on the distinct `district` values. So choosing "Plauen" hides Kita Kleiner Globus, Kita Lukas, Kita SpielWerk and Familienzentrum Brücke (all tagged "Südvorstadt", which is part of Plauen). Choosing "Cotta" hides Gorbitz and Löbtau. Choosing "Altstadt" hides Johannstadt.

The individual values are not wrong. Each one is a real, correct area name for its address.

## Expected
Every `district` value uses the same level, so the filter groups places the way parents expect. Stadtbezirk is the safer choice: there are only 10 of them, plus the Ortschaften.

## Repro
```sql
select district, count(*) from public.resources group by district order by 2 desc;
select district, count(*) from public.family_events group by district order by 2 desc;
```

## Fix
Not applied, because the fix changes rows written by several agents and the frontend filter. The orchestrator should decide.
- **Sunday (no schema change):** in the frontend, map Stadtteil → Stadtbezirk before building the district filter:
  Johannstadt → Altstadt · Seevorstadt → Altstadt · Wilsdruffer Vorstadt → Altstadt · Südvorstadt → Plauen · Zschertnitz → Plauen · Gorbitz → Cotta · Löbtau → Cotta · Gruna → Blasewitz · Striesen → Blasewitz · Neugruna → Blasewitz · Weißer Hirsch → Loschwitz · Radeberger Vorstadt → Neustadt. The mappings were checked against the OSM `city_district` of the pins, and Löbtau against the city playground map ("Stadtbezirk Cotta").
- **Or:** run one UTF-8 `update … set district = …` over `resources` and `family_events` that uses the same mapping, and change the plan text from "Dresden Stadtteil" to "Dresden Stadtbezirk".
- **Later:** keep both levels with a new migration that adds `stadtbezirk text`, filled from the pin.
