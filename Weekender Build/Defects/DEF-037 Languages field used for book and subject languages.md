---
type: defect
date: 2026-09-26
status: fixed
severity: minor
found_in: "[[RUN-019 Family places seed]]"
owner: abdul
---
# Defect: Languages field used for book and subject languages

## Observed
Found during the independent fact-check of [[RUN-019 Family places seed]]. The data contract in [[Frontend and UX Plan v3 (merged)]] says `resources.languages` means languages **spoken or used for teaching**. The UI shows it as "Languages" on the provider page and uses it for the language filter. Two rows broke that rule:

- **Zentralbibliothek im Kulturpalast** had `{de,en,fr,ru,es,it,zh,tr,ar,fa,ps}`. These are the languages of the children's books held across the **whole city-library network** (bibo-dresden.de "Medienangebot"). They are not languages the staff speak, and the books are not all held at this branch. A parent who filters by Pashto or Arabic would expect staff who speak it.
- **Romain-Rolland-Gymnasium** had `{de,fr,en}`. Lessons are taught in German, and partly in French on the bilingual track. English is a foreign-language subject there, just like Spanish and Latin, which were not listed. A parent who filters by English would expect an English-taught school (that is DIS).

## Expected
`languages` = languages a parent can use with the staff, or languages lessons are taught in. Book or subject languages belong in the description.

## Repro
```sql
select name, languages from public.resources
where id in ('3f4a051a-e01d-490b-83ef-dd4e24d087f8','7347e4c0-acb0-476b-a242-d92c1650341e');
```
Before the fix: 11 codes on the library row, and `{de,fr,en}` on the school row.

## Fix
Fixed on 26 Sep 2026 (UTF-8 SQL, update by id):
- Zentralbibliothek → `{de}`. The book languages are still in `description_en` and in all 5 `i18n` descriptions, and `notes_en` now says they are held network-wide and that staff languages are not published.
- Romain-Rolland-Gymnasium → `{de,fr}`. `notes_en` explains that English, Spanish and Latin are taught as subjects.

Idea for later: if "has children's books in my language" becomes a filter, add a separate `media_languages text[]` column in a new migration rather than reusing `languages`.
