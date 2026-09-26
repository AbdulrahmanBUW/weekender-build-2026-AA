-- DEF-047: test / role-play calls must not put a public "Checked by phone" badge on real listings.
-- Test tasks are recognisable by their patient name markers used in all test scripts: "(E2E", "Roleplay", "test",
-- or by a non-production call provider ('test', 'verify', 'mock').

create or replace function public.mark_resource_checked()
returns trigger language plpgsql security definer set search_path = public as $$
declare v_name text;
begin
  if new.outcome is null or new.outcome is not distinct from old.outcome then return new; end if;
  if new.outcome not in ('booked','completed','rejected','rejected_no_new_patients') then return new; end if;
  if coalesce(new.provider, '') in ('test','verify','mock') then return new; end if;

  select patient_name into v_name from public.call_requests where id = new.request_id;
  if v_name ilike '%(E2E%' or v_name ilike '%roleplay%' or v_name ilike '%test%' then return new; end if;

  update public.resources r
     set last_checked_at = now(), last_check_outcome = new.outcome
    from public.call_requests q
   where q.id = new.request_id and q.resource_id = r.id;
  return new;
end $$;
