---
type: defect
date: 2026-09-26
status: open
severity: minor
found_in: "[[RUN-020 Family events seed]]"
owner:
---
# Defect: Event language defaults to German when the source omits it

## Observed
The verification of [[RUN-020 Family events seed]] found one event with the wrong language and age range:

| Field | Seeded (from the city calendar) | Organiser's page |
|---|---|---|
| Event | "Fairy-tale hour: The Carnival of the Animals", Fri 02.10.2026 16:00–17:30, Institut français Dresden | "Heure du conte – Der Karneval der Tiere!", same date, time and place |
| `languages` | `{de}` | "Auf Französisch!" → `{fr}` |
| age | none | "Für Kinder von 3 bis 7 Jahren" → 3–7 |

The seed's `source_url` was the dresden.de Interkulturelle Tage (IKT) calendar entry. That entry is written in German and says nothing about the language the event is held in, so the row fell back to German. The organiser's own page (`institutfrancais.de/de/dresden/event/heure-du-conte-29164`) states French and the age range.

There are two causes:
1. **Aggregator-only sourcing.** The IKT calendar republishes organisers' events in German and leaves out details such as the event language and exact ages.
2. **The schema cannot say "unknown".** `family_events.languages` is `text[] not null default '{de}'` (migration `20260926200000_merged_family_hub.sql`). "Not stated" and "German" are therefore stored the same way. For "Dresden mit Kind", events in a family's own language are a main selling point: a French-speaking parent who filters by French would not see this event, and a German-only parent would be sent to an event in French.

## Expected
- The event language and ages come from the organiser's page whenever it exists.
- When no source states the language, the row stores a value that means "unknown", not German.

## Repro
Open the old `source_url` (`https://www.dresden.de/apps_ext/IKT/event/31bdcd3a-3f83-480e-a571-6707b07854cb`): it states no language and no age. Then open the organiser page above: it says "Auf Französisch! Für Kinder von 3 bis 7 Jahren."

## Fix
- **Done (26.09.2026, RUN-020 verification):** row `17a05fce-4dab-4ac2-898c-9d89d54cd1af` corrected. `languages = {fr}`, age 3–7, `languages` added to `activity_categories`, `url`/`source_url` now point to the organiser page, and the title, `description_en` and all five `i18n` translations say "in French, ages 3–7". SQL: scratchpad `run020_verify/fix_row8_french_story_hour.sql`.
- **Open (process):** for events found through aggregators (the IKT calendar, dresden.de lists), also open the organiser's own event page before setting `languages` and the age fields. Record which page each field came from.
- **Open (schema and UI, needs a decision):** a new migration that changes the default to `'{}'` and treats an empty array as "language not stated". The UI then shows no language chip for those rows, and a language filter leaves them out. The German rows already seeded would stay as they are (their German programme text supports `de`).
- **Caution:** the builder's scratch seed file (`run020_events/seed_family_events.sql`) still has the old title and `{de}`. The title is part of `dedupe_key`, so re-running that file would **insert a second, wrong row** instead of updating this one. Do not re-run it. If a seed file is needed, regenerate it from the database.
