-- DEC-003 (accepted 26.09): "Find it. We call for you."
-- Dresden mit Kind (family hub: courses, events, communities, library) + "Ask for me" (HalloTermin calls).
-- Extends existing tables (resources, guides, call_requests) so the working pipeline keeps running.

-- ---------- resources: family providers & places ----------
alter table public.resources drop constraint if exists resources_category_check;
alter table public.resources add constraint resources_category_check check (category in (
  'auslaenderbehoerde','doctor','pharmacy','bank','community','other',          -- newcomer services (existing)
  'course','kita','school','library','playground','family_place'));             -- family hub (new)

alter table public.resources drop constraint if exists resources_source_check;
alter table public.resources add constraint resources_source_check check (source in
  ('brave','firecrawl','manual','web_research','suggestion'));

alter table public.resources
  add column if not exists audience text not null default 'newcomer',
  add column if not exists activity_categories text[] not null default '{}',
  add column if not exists age_min_years numeric(4,1),
  add column if not exists age_max_years numeric(4,1),
  add column if not exists price_type text not null default 'unknown',
  add column if not exists format text,
  add column if not exists description_en text,
  add column if not exists i18n jsonb not null default '{}'::jsonb,
  add column if not exists last_checked_at timestamptz,        -- set when "Ask for me" gets an answer
  add column if not exists last_check_outcome text;            -- outcome only, never personal data

alter table public.resources
  add constraint resources_audience_check check (audience in ('family','newcomer','both')),
  add constraint resources_activity_categories_check check (activity_categories <@ array[
    'music','dance','sport','yoga','art','languages','stem','swimming','theatre','nature',
    'parent_baby','parent_meetup','library','school_kita','family_cafe','playground']::text[]),
  add constraint resources_age_range_check check (
    (age_min_years is null or age_min_years between 0 and 18) and
    (age_max_years is null or age_max_years between 0 and 18) and
    (age_min_years is null or age_max_years is null or age_min_years <= age_max_years)),
  add constraint resources_price_type_check check (price_type in ('free','per_session','subscription','trial_available','unknown')),
  add constraint resources_format_check check (format is null or format in ('recurring_course','workshop','one_off','community_group','place','service')),
  add constraint resources_description_len check (description_en is null or char_length(description_en) <= 600),
  add constraint resources_i18n_obj check (jsonb_typeof(i18n) = 'object');

-- existing newcomer places stay "newcomer"; paediatricians & gynaecologists are also family-relevant
update public.resources set audience = 'both'
 where category = 'doctor' and subcategory in ('kinderarzt','frauenarzt');

create index if not exists resources_audience_idx on public.resources (audience, category);
create index if not exists resources_activity_idx on public.resources using gin (activity_categories);
create index if not exists resources_languages_idx on public.resources using gin (languages);

-- ---------- guides: library categories + "Ask for me" ----------
alter table public.guides
  add column if not exists category text,
  add column if not exists audience text not null default 'both',
  add column if not exists ask_task_type text;                 -- prefilled task for the "Ask for me" button

alter table public.guides
  add constraint guides_category_check check (category is null or category in ('documents','health','kita_school','money','everyday')),
  add constraint guides_audience_check check (audience in ('family','newcomer','both'));

update public.guides set category = case slug
    when 'anmeldung-dresden' then 'documents'
    when 'auslaenderbehoerde-dresden-appointment' then 'documents'
    when 'bank-account-documents' then 'money'
    when 'health-insurance-registration' then 'health'
  end,
  ask_task_type = case slug
    when 'anmeldung-dresden' then 'authority_appointment'
    when 'auslaenderbehoerde-dresden-appointment' then 'authority_appointment'
    when 'bank-account-documents' then 'bank_enquiry'
    when 'health-insurance-registration' then 'other_call'
  end
 where category is null;

-- ---------- call_requests: two new task types ----------
alter table public.call_requests drop constraint if exists call_requests_task_type_check;
alter table public.call_requests add constraint call_requests_task_type_check check (task_type in (
  'doctor_appointment','authority_appointment','landlord_request','contract_question',
  'bank_enquiry','pharmacy_question','restaurant_booking','other_call',
  'course_enquiry',   -- free spot / trial lesson / waiting list at a course provider
  'kita_enquiry'));   -- Kita place, waiting list, visit date

alter table public.guides add constraint guides_ask_task_type_check check (ask_task_type is null or ask_task_type in (
  'doctor_appointment','authority_appointment','landlord_request','contract_question',
  'bank_enquiry','pharmacy_question','restaurant_booking','other_call','course_enquiry','kita_enquiry'));

-- ---------- family_events: family events (seeded, read-only for the browser) ----------
-- (named family_events because public.events is the automation audit log)
create table if not exists public.family_events (
  id                  uuid primary key default gen_random_uuid(),
  title               text not null check (char_length(title) <= 160),
  description_en      text check (description_en is null or char_length(description_en) <= 600),
  i18n                jsonb not null default '{}'::jsonb check (jsonb_typeof(i18n) = 'object'),
  starts_at           timestamptz not null,
  ends_at             timestamptz,
  all_day             boolean not null default false,
  place_name          text,
  address             text,
  district            text,
  resource_id         uuid references public.resources(id) on delete set null,
  age_min_years       numeric(4,1),
  age_max_years       numeric(4,1),
  languages           text[] not null default '{de}',
  activity_categories text[] not null default '{}',
  price_type          text not null default 'unknown' check (price_type in ('free','paid','unknown')),
  price_text          text,
  url                 text,
  source              text not null default 'web_research' check (source in ('brave','firecrawl','manual','web_research','suggestion')),
  source_url          text not null,
  retrieved_at        timestamptz not null default now(),
  dedupe_key          text unique,                            -- filled by trigger: lower(title)|starts_at
  check (ends_at is null or ends_at >= starts_at)
);

create or replace function public.family_events_set_dedupe_key() returns trigger
language plpgsql as $$
begin
  new.dedupe_key := lower(trim(new.title)) || '|' || new.starts_at::text;
  return new;
end $$;

drop trigger if exists family_events_dedupe on public.family_events;
create trigger family_events_dedupe before insert or update of title, starts_at on public.family_events
  for each row execute function public.family_events_set_dedupe_key();

create index if not exists family_events_starts_idx on public.family_events (starts_at);

alter table public.family_events enable row level security;
create policy "read family events" on public.family_events for select to anon, authenticated using (true);
revoke insert, update, delete on public.family_events from anon, authenticated;

-- ---------- suggestions: "Suggest a place / event / correction" (write-only for the browser) ----------
create table if not exists public.suggestions (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  kind        text not null check (kind in ('place','event','correction','other')),
  name        text not null check (char_length(name) between 2 and 160),
  url         text check (url is null or char_length(url) <= 300),
  note        text check (note is null or char_length(note) <= 500),
  ui_lang     text not null default 'en' check (ui_lang in
                ('en','ar','tr','uk','ru','fa','prs','hi','es','fr','pl','vi','zh','de')),
  resource_id uuid references public.resources(id) on delete set null,
  status      text not null default 'new' check (status in ('new','accepted','rejected'))
);

alter table public.suggestions enable row level security;
-- browsers may only add new suggestions; nobody but the service role can read them (no personal data, no spam display)
create policy "anon can suggest" on public.suggestions
  for insert to anon, authenticated with check (status = 'new');
revoke select, update, delete on public.suggestions from anon, authenticated;

-- ---------- "checked by phone" badge: mark the resource when an Ask-for-me call ends ----------
create or replace function public.mark_resource_checked()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  if new.outcome is null or new.outcome is not distinct from old.outcome then return new; end if;
  if new.outcome not in ('booked','completed','rejected','rejected_no_new_patients') then return new; end if;
  update public.resources r
     set last_checked_at = now(), last_check_outcome = new.outcome
    from public.call_requests q
   where q.id = new.request_id and q.resource_id = r.id;
  return new;
end $$;

drop trigger if exists calls_mark_resource_checked on public.calls;
create trigger calls_mark_resource_checked after update of outcome on public.calls
  for each row execute function public.mark_resource_checked();
