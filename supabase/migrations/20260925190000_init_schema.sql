-- Weekender Build – core schema (worked example: HalloTermin call-booking agent)
-- Flow: app inserts call_request -> n8n picks it up -> call runs -> transcript_lines stream in
--       -> n8n writes outcome to calls + call_requests.status -> app shows result via Realtime.

create extension if not exists "pgcrypto";

-- ---------- enums ----------
create type request_status as enum (
  'submitted',   -- user sent the form
  'briefed',     -- n8n built the German call brief
  'calling',     -- call in progress
  'booked',      -- slot confirmed + read back
  'needs_user',  -- practice asked something only the user can answer
  'rejected',    -- e.g. no new patients
  'failed'       -- technical failure / no answer
);
create type speaker as enum ('agent', 'practice', 'system');

-- ---------- call_requests: what the user asked for ----------
create table public.call_requests (
  id               uuid primary key default gen_random_uuid(),
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now(),
  status           request_status not null default 'submitted',

  -- who (minimum data: no symptoms, GDPR Art. 9)
  patient_name     text not null,
  patient_dob      date,
  insurance_type   text check (insurance_type in ('gkv','pkv','other')),
  insurance_name   text,
  user_email       text not null,
  user_language    text not null default 'en',

  -- where / what
  practice_name    text not null,
  practice_phone   text not null,
  reason_category  text not null check (reason_category in
                     ('first_visit','checkup','acute','follow_up','specialist','other')),
  has_referral     boolean not null default false,
  is_new_patient   boolean not null default true,
  -- pre-approved windows, e.g. [{"date":"2026-09-29","from":"08:00","to":"12:00"}]
  time_windows     jsonb not null default '[]'::jsonb,

  -- the user's authorization (AI disclosure itself happens on the call, EU AI Act Art. 50)
  consent_ai_call  boolean not null check (consent_ai_call),
  consent_at       timestamptz not null default now(),

  -- filled by n8n
  call_brief_de    text
);

-- ---------- calls: one row per phone attempt ----------
create table public.calls (
  id               uuid primary key default gen_random_uuid(),
  request_id       uuid not null references public.call_requests(id) on delete cascade,
  created_at       timestamptz not null default now(),
  provider         text,              -- e.g. 'elevenlabs', 'deepgram-twilio', 'mock'
  provider_call_id text,
  started_at       timestamptz,
  ended_at         timestamptz,
  outcome          text check (outcome in
                     ('booked','rejected_no_new_patients','needs_user','no_answer','voicemail','failed')),
  booked_slot      timestamptz,
  bring_items      text[],            -- e.g. {'Versichertenkarte','Überweisung'}
  summary_en       text,
  error            text
);
create index on public.calls (request_id);

-- ---------- transcript_lines: live transcript (text only, never audio – §201 StGB) ----------
create table public.transcript_lines (
  id          bigint generated always as identity primary key,
  call_id     uuid not null references public.calls(id) on delete cascade,
  created_at  timestamptz not null default now(),
  speaker     speaker not null,
  text_de     text not null,
  text_en     text
);
create index on public.transcript_lines (call_id, id);

-- ---------- events: audit log of every automation step (shows n8n "moving data") ----------
create table public.events (
  id          bigint generated always as identity primary key,
  created_at  timestamptz not null default now(),
  request_id  uuid references public.call_requests(id) on delete cascade,
  source      text not null,          -- 'app' | 'n8n' | 'voice' | 'system'
  type        text not null,          -- e.g. 'brief_created', 'call_started', 'email_sent'
  payload     jsonb not null default '{}'::jsonb
);
create index on public.events (request_id, id);

-- ---------- updated_at trigger ----------
create or replace function public.touch_updated_at() returns trigger
language plpgsql as $$ begin new.updated_at := now(); return new; end $$;
create trigger call_requests_touch before update on public.call_requests
  for each row execute function public.touch_updated_at();

-- ---------- RLS (demo mode: no user accounts) ----------
-- anon (browser) may CREATE requests and READ status/transcripts.
-- Only service_role (n8n, voice webhooks) writes calls, transcripts, events and updates requests.
-- DEMO ONLY: anon can read all rows. Before real users: add auth + owner-scoped policies.
alter table public.call_requests    enable row level security;
alter table public.calls            enable row level security;
alter table public.transcript_lines enable row level security;
alter table public.events           enable row level security;

create policy "anon can submit requests" on public.call_requests
  for insert to anon, authenticated with check (consent_ai_call);
create policy "demo read requests"   on public.call_requests    for select to anon, authenticated using (true);
create policy "demo read calls"      on public.calls            for select to anon, authenticated using (true);
create policy "demo read transcript" on public.transcript_lines for select to anon, authenticated using (true);
create policy "demo read events"     on public.events           for select to anon, authenticated using (true);

-- ---------- Realtime ----------
alter publication supabase_realtime add table
  public.call_requests, public.calls, public.transcript_lines, public.events;
