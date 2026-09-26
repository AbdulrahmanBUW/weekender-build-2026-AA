---
type: defect
date: 2026-09-26
status: open
severity: minor
found_in: "[[RUN-007 Newcomer crawler first run]]"
owner: claude
---
# Defect: Supabase node stores jsonb payload as string

## Observed
`events.payload` rows written by the n8n **Supabase node** (field value `{{ JSON.stringify(...) }}`) are stored as a JSON **string**, not an object: `jsonb_typeof(payload) = 'string'`. Seen on event 12 (workflow 02) and event 11 `brief_created` (workflow 01). Rows from the DB trigger are fine (`object`).

## Expected
`payload` is a JSON object, so the app and SQL can read `payload->>'resources_rows'`.

## Repro
Supabase node → Row → Create → table `events`, field `payload` = `={{ JSON.stringify({a:1}) }}` → `select jsonb_typeof(payload) from events order by id desc limit 1;` → `string`.

## Fix
- Workflow 02: fixed. The event is now written with an **HTTP Request** node (predefined credential `supabaseApi`) POSTing `{source, type, request_id, payload}` as a real JSON body to `/rest/v1/events`. Verified: `jsonb_typeof = object`. Event 12 was repaired with `update events set payload = (payload #>> '{}')::jsonb where id = 12;`.
- **Still open for workflow 01** ("Log Event: brief_created"): switch it to the same HTTP pattern, then repair old rows with `update events set payload = (payload #>> '{}')::jsonb where jsonb_typeof(payload) = 'string';`.
