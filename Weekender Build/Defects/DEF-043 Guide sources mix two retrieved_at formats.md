---
type: defect
date: 2026-09-26
status: open
severity: minor
found_in: "[[RUN-021 Library guides for families]]"
owner: abdul
---
# Defect: Guide sources mix two retrieved_at formats

## Observed
`public.guides.sources[].retrieved_at` has two formats:
- `anmeldung-dresden`, `auslaenderbehoerde-dresden-appointment`, `bank-account-documents` (written by the crawler, workflow 02): full ISO timestamps, e.g. `2026-09-26T08:27:06.060Z`.
- `health-insurance-registration` and the 4 new family guides: date only, `2026-09-26`.

## Expected
One format, so the guide page can show "retrieved 26 Sep 2026" for every source ([[Frontend and UX Plan v2]] P8: "each sources[] item as a link with its retrieved_at date").

## Repro
`select slug, s->>'retrieved_at' from public.guides, jsonb_array_elements(sources) s order by 1;`

## Fix
Either format the value in the UI (`new Date(v).toLocaleDateString(lang, {dateStyle: 'medium'})` works for both) or normalise the data: `update public.guides set sources = (select jsonb_agg(jsonb_set(s, '{retrieved_at}', to_jsonb(left(s->>'retrieved_at', 10)))) from jsonb_array_elements(sources) s);` Not changed in RUN-021, because that task only covered new guides and translations.
