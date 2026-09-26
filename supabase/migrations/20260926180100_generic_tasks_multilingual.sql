-- Frontend and UX Plan v2 (section H): any phone task + multilingual.
-- Strategy: EXTEND call_requests (trigger, RLS, relay, n8n and seed depend on it); UI calls it a "task".
-- Kept generic on purpose so the product can still change after merging Idea B.

-- ---------- call_requests: generic task fields ----------
alter table public.call_requests
  add column if not exists task_type text not null default 'doctor_appointment',
  add column if not exists goal_user text,
  add column if not exists goal_de text,                 -- written by n8n only (see RLS)
  add column if not exists organisation_category text,
  add column if not exists resource_id uuid references public.resources(id) on delete set null,
  add column if not exists constraints jsonb not null default '{}'::jsonb,
  add column if not exists allowed_facts jsonb not null default '[]'::jsonb;

alter table public.call_requests
  add constraint call_requests_task_type_check check (task_type in (
    'doctor_appointment','authority_appointment','landlord_request','contract_question',
    'bank_enquiry','pharmacy_question','restaurant_booking','other_call')),
  add constraint call_requests_goal_user_len check (goal_user is null or char_length(goal_user) <= 200),
  add constraint call_requests_constraints_obj check (jsonb_typeof(constraints) = 'object' and pg_column_size(constraints) < 2000),
  add constraint call_requests_allowed_facts_arr check (jsonb_typeof(allowed_facts) = 'array' and pg_column_size(allowed_facts) < 4000),
  add constraint call_requests_user_language_check check (user_language in
    ('en','ar','tr','uk','ru','fa','prs','hi','es','fr','pl','vi','zh','de'));

-- doctor-only fields become optional for other task types; email optional (result is shown on the page)
alter table public.call_requests alter column reason_category drop not null;
alter table public.call_requests alter column user_email drop not null;
alter table public.call_requests
  add constraint call_requests_doctor_reason check (task_type <> 'doctor_appointment' or reason_category is not null);

-- ---------- RLS: browser may only create fresh tasks (no injected German text) ----------
drop policy if exists "anon can submit requests" on public.call_requests;
create policy "anon can submit requests" on public.call_requests
  for insert to anon, authenticated
  with check (
    consent_ai_call
    and status = 'submitted'
    and call_brief_de is null
    and goal_de is null
  );

-- ---------- calls: structured results in the user's language ----------
alter table public.calls
  add column if not exists result jsonb,
  add column if not exists summary_user text,
  add column if not exists bring_items_user jsonb,
  add column if not exists disclosure_variant text;

alter table public.calls drop constraint if exists calls_outcome_check;
alter table public.calls add constraint calls_outcome_check check (outcome in
  ('booked','completed','rejected','rejected_no_new_patients','needs_user','no_answer','voicemail','failed'));

-- ---------- transcript_lines: subtitle in the user's language ----------
alter table public.transcript_lines add column if not exists text_user text;

-- ---------- async translation + result workflows (n8n 05 / 06), same Vault pattern as 01 ----------
-- Vault names: n8n_translate_line_url, n8n_call_result_url (+ shared n8n_webhook_secret). Missing URL = no-op.
create or replace function public.notify_n8n(p_url_secret text, p_body jsonb)
returns void
language plpgsql
security definer
set search_path = public, extensions
as $$
declare v_url text; v_secret text;
begin
  select decrypted_secret into v_url    from vault.decrypted_secrets where name = p_url_secret;
  select decrypted_secret into v_secret from vault.decrypted_secrets where name = 'n8n_webhook_secret';
  if v_url is null then return; end if;
  perform net.http_post(
    url := v_url, body := p_body,
    headers := jsonb_build_object('Content-Type','application/json','X-Webhook-Secret', coalesce(v_secret,'')),
    timeout_milliseconds := 5000);
end $$;
revoke all on function public.notify_n8n(text, jsonb) from public, anon, authenticated;

create or replace function public.on_transcript_line()
returns trigger language plpgsql security definer set search_path = public as $$
declare v_lang text;
begin
  select r.user_language into v_lang
    from public.calls c join public.call_requests r on r.id = c.request_id where c.id = new.call_id;
  perform public.notify_n8n('n8n_translate_line_url', jsonb_build_object(
    'line_id', new.id, 'call_id', new.call_id, 'speaker', new.speaker, 'text_de', new.text_de,
    'user_language', coalesce(v_lang, 'en')));
  return new;
end $$;

drop trigger if exists transcript_lines_translate on public.transcript_lines;
create trigger transcript_lines_translate after insert on public.transcript_lines
  for each row execute function public.on_transcript_line();

create or replace function public.on_call_outcome()
returns trigger language plpgsql security definer set search_path = public as $$
declare v_lang text;
begin
  if new.outcome is null or new.outcome is not distinct from old.outcome then return new; end if;
  select user_language into v_lang from public.call_requests where id = new.request_id;
  perform public.notify_n8n('n8n_call_result_url', jsonb_build_object(
    'call_id', new.id, 'request_id', new.request_id, 'outcome', new.outcome,
    'booked_slot', new.booked_slot, 'bring_items', new.bring_items, 'result', new.result,
    'summary_en', new.summary_en, 'user_language', coalesce(v_lang, 'en')));
  return new;
end $$;

drop trigger if exists calls_outcome_result on public.calls;
create trigger calls_outcome_result after update of outcome on public.calls
  for each row execute function public.on_call_outcome();
