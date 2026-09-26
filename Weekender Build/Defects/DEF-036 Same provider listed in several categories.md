---
type: defect
date: 2026-09-26
status: open
severity: minor
found_in: "[[RUN-019 Family places seed]]"
owner: abdul
---
# Defect: Same provider listed in several categories

## Observed
`dedupe_key` is `category|lower(name)|lower(address)`. It only catches duplicates **inside one category** with the same spelling of the name. The parallel seed agents write different categories, so one organisation can end up as several rows under different names:

- Kolibri e.V., Ritzenbergstraße 3, 01067 Dresden:
  - `community` "Interkultureller Familientreff – Kolibri e.V." ([[RUN-018 Heritage-language family offers seed]])
  - `course` "Ukrainisch für Kinder – Kolibri e.V." (same address) and `course` "Russisch für Kinder – Kolibri e.V." (Villa der Kulturen) ([[RUN-018 Heritage-language family offers seed]])
  - `family_place` "Kinder- und Elternzentrum Kolibri e.V." ([[RUN-019 Family places seed]])

Each row describes a different offer, so they are not exact copies. But a parent browsing "All" sees the same organisation 4 times, and an "Ask for me" call to any of them reaches the same office. The same could happen with Dresden International School: its preschool is `kita` and its school is `school` in RUN-019. That split is intentional, because the two campuses have different addresses.

## Expected
One organisation is recognisable as one provider. Its different offers are either grouped on one profile or clearly labelled as separate offers of the same provider.

## Repro
```sql
select address, count(*), string_agg(category || ': ' || name, ' | ')
from public.resources where address is not null
group by address having count(*) > 1;
```
Result on 26 Sep 2026: 3 rows at Ritzenbergstraße 3 (the Kolibri rows above). The query also returns 2 legitimate pairs of different organisations in one building: Ausländerbehörde + Dresden Welcome Center at Lingnerallee 3, and a pharmacy + paediatrician at Tannenstraße 17. So the address alone is not a safe provider key.

## Fix
- For Sunday: RUN-019 narrowed its Kolibri row to the parent consultation hours and parent-toddler groups, and its `notes_en` points to the course/community rows. The orchestrator can decide to keep all 4 rows or hide one.
- UI: on a provider profile, show "More from this provider" by matching `website` host or `address`.
- Later: add a `provider_id`/`org_key` column (e.g. website host) in a new migration so offers can be grouped.
