---
type: defect
date: 2026-09-26
status: open
severity: minor
found_in: "[[RUN-020 Family events seed]]"
owner:
---
# Defect: family_events dedupe_key depends on session TimeZone

## Observed
The trigger `family_events_set_dedupe_key()` (migration `20260926200000_merged_family_hub.sql`) builds the key as `lower(trim(title)) || '|' || new.starts_at::text`. When `timestamptz` is cast to text, Postgres renders it in the **session** `TimeZone`. Read-only check on the linked DB, with the session set to `Europe/Berlin`:

| stored key (seeded from a UTC session) | key the trigger builds in a Berlin session |
|---|---|
| `discovery day at zoo dresden\|2026-10-03 08:00:00+00` | `discovery day at zoo dresden\|2026-10-03 10:00:00+02` |
| `halloween at zoo dresden\|2026-10-31 09:00:00+00` | `halloween at zoo dresden\|2026-10-31 10:00:00+01` |

So a later upsert of the **same event** from a client whose session is not UTC gets a different key. `on conflict (dedupe_key)` then does not match, and the event is inserted a second time.

## Expected
The same title and the same instant always give the same key, whatever the client's session time zone.

## Repro
`select set_config('TimeZone','Europe/Berlin',true), lower(trim(title))||'|'||starts_at::text = dedupe_key from public.family_events;` returns `false` for every row. Today everything runs in UTC (`supabase db query`, PostgREST and the n8n Supabase node), so nothing has been duplicated yet. It will happen when a psql client with `PGTZ`, or an n8n Postgres node with a time zone set, runs the seed or a crawler upsert.

## Fix
Proposed, not applied (it needs a new migration and a one-time recompute):
```sql
create or replace function public.family_events_set_dedupe_key() returns trigger language plpgsql as $$
begin
  new.dedupe_key := lower(trim(new.title)) || '|' || to_char(new.starts_at at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI"Z"');
  return new;
end $$;
update public.family_events set title = title;  -- fires the trigger (update of title) to rewrite existing keys
```
Until then, run event upserts only from UTC sessions.
