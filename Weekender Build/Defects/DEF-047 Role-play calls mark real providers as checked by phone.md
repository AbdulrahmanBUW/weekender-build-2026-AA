---
type: defect
date: 2026-09-26
status: open
severity: major
found_in: "[[RUN-022 UI plan v3 merged]]"
owner: orchestrator (migration)
---
# Defect: Role-play calls mark real providers as checked by phone

## Observed
The live trigger function `public.mark_resource_checked()` (read with `pg_get_functiondef` on 26 Sep) sets `resources.last_checked_at = now()` and `last_check_outcome` whenever `calls.outcome` changes to `booked`, `completed`, `rejected` or `rejected_no_new_patients` and the request has a `resource_id`. It never looks at `calls.provider`.

Today every call is a browser role-play: the relay always inserts `provider = 'deepgram-browser'` (`services/voice-relay/server.js`), and the SQL test scripts use `'mock'`. Plan v3 sends `resource_id` from the provider page with every "Ask for me" request, and the provider page shows "Checked by phone on {date}" from these two columns.

## Expected
A real Dresden business shows "Checked by phone on …" only after a real phone call to that business. Test and demo calls (a teammate playing the receptionist, invented answers) must not change a real listing.

## Repro
Static, from the live function and the relay code (not executed, to avoid n8n side effects on a real listing): create an "Ask for me" request for a real course → open the relay page → a teammate answers and a trial lesson is booked → the trigger marks the real course "Checked by phone today: A slot was booked", although nobody called that course.

## Fix
Proposed migration (orchestrator):

```sql
create or replace function public.mark_resource_checked()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  if new.outcome is null or new.outcome is not distinct from old.outcome then return new; end if;
  if new.outcome not in ('booked','completed','rejected','rejected_no_new_patients') then return new; end if;
  -- browser role-plays and SQL mocks only count for demo listings
  if coalesce(new.provider, '') in ('deepgram-browser','mock') and not exists (
       select 1 from public.call_requests q join public.resources r on r.id = q.resource_id
        where q.id = new.request_id and r.subcategory = 'demo') then
    return new;
  end if;
  update public.resources r
     set last_checked_at = now(), last_check_outcome = new.outcome
    from public.call_requests q
   where q.id = new.request_id and q.resource_id = r.id;
  return new;
end $$;
```

Until then: after each test call on a real listing, reset it (`update resources set last_checked_at = null, last_check_outcome = null where id = '<id>'`, test clean-up only), and on stage call only the demo listing ([[Frontend and UX Plan v3 (merged)]] H, demo listing rule).

## Update 26 Sep 13:20 (verification, [[RUN-022 UI plan v3 merged]])
Still open: the live `mark_resource_checked()` is unchanged (no `provider` check). No harm so far: 0 resources have `last_checked_at` and 0 requests carry a `resource_id`. The risk grows as soon as the app sends `resource_id` from provider pages. The live intake now keeps `resource_id` from the prefill, so every "Ask for me" test on a real listing will trigger it.
