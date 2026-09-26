---
type: defect
date: 2026-09-26
status: open
severity: major
found_in: "[[RUN-018 Heritage-language family offers seed]]"
owner: abdul
---
# Defect: Communities page drops heritage-language courses

## Observed
The seed task (and [[Idea B - Dies-Das-Ana-Nas]], pillar 3 "Bilingual communities": "heritage-language classes … filter by language") says children's language classes are stored as `category = 'course'` with `'languages'` in `activity_categories`. [[RUN-018 Heritage-language family offers seed]] stored 10 such rows this way: Raduga, Kolibri Russian, Kolibri Ukrainian, Le Rendez-vous (French), IBLA and Friedensschule (Arabic), Schola ludus (Czech), Il Girasole (Italian), the Polish academy, and the state Herkunftssprachlicher Unterricht (16 languages including Turkish and Vietnamese).

[[Frontend and UX Plan v3 (merged)]], prompt **P5 `/communities`**, keeps only rows with `audience in (family, both)` **and** (`category in (community, library)` **or** `activity_categories` overlapping `parent_meetup`, `family_cafe`, `library`). `languages` is not in that list, so all 10 heritage-language courses are dropped from the page grouped by language. A Russian or Arabic parent opening "Bilingual communities" sees only the 6 community rows. The Saturday schools show up only on `/courses`, and only if the parent sets the Activity filter to "Languages".

## Expected
`/communities` lists every family row that offers a language other than German. In particular, rows with `'languages'` in `activity_categories` appear in the section for each of their `languages`.

## Repro
```sql
select name, category, activity_categories from public.resources
 where audience in ('family','both')
   and not (category in ('community','library') or activity_categories && array['parent_meetup','family_cafe','library'])
   and activity_categories @> array['languages'];
```
→ 11 rows that P5 would hide (26 Sep 2026, 12:50): the 10 from RUN-018 plus `Romain-Rolland-Gymnasium Dresden` (`school`, `{school_kita,languages}`) from another seed.

## Fix
Frontend only, in P5 (and the pillar table in section A of the v3 plan): add `languages` to the overlap list, i.e. keep rows where `category in (community, library)` or `activity_categories` overlaps `parent_meetup, family_cafe, library, languages`. The breadcrumb on `/p/:id` can stay category-based (course → `/courses`). No DB change needed.
