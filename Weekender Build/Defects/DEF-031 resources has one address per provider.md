---
type: defect
date: 2026-09-26
status: open
severity: minor
found_in: "[[RUN-017 Family courses seed]]"
owner: abdul
---
# Defect: resources has one address per provider

## Observed
`resources` stores one `address`/`lat`/`lng`/`district` per row. Several real course providers teach in many places:
- KiDDs Kindersportverein: over 20 gyms across Dresden.
- Musikschule Adagio: 7 teaching locations.
- Liga der Roboter: 2 locations.
- Dresdner Bäder children's swim courses: 5 pools (Schwimmsportkomplex, Kombibad Prohlis, Klotzsche, Bühlau, Nordbad). The builder first wrote 2; the RUN-017 fact-check corrected this, and the row now lists the other pools in `notes_en`.
- Naturcamp: meets in the Dresdner Heide forest, no street address at all.

In [[RUN-017 Family courses seed]], KiDDs and Naturcamp were stored with `address`, `district`, `lat` and `lng` all null, so they have no map pin and drop out of any district filter. The other providers show only one of their locations.

A side effect: `dedupe_key` is `category|lower(name)|lower(address)`, so two rows with the same name and a null address in the same category collide.

## Expected
A parent filtering by district or on the map finds a provider that teaches in their district.

## Repro
Filter courses by any `district`. KiDDs, which uses 20+ gyms across the city, is never returned.

## Fix
For Sunday: accept the gap. The description and `notes_en` say "sessions in over 20 gyms" or "meets in the Dresdner Heide", and the UI should show rows with a null district under "All districts" or "Citywide". Later: add a `resource_locations` table (resource_id, address, district, lat, lng) or a `districts text[]` column in a new migration.
