-- Newcomer resources for Dresden: places (resources) + how-to guides (guides).
-- Filled by n8n workflow "Newcomer 02 – Resource crawler (Dresden)" using the service key.
-- Browser (anon/authenticated) may only read. Public business/official info only, always with source_url.

-- ---------- resources: places (offices, doctors, pharmacies, banks, community) ----------
create table public.resources (
  id             uuid primary key default gen_random_uuid(),
  category       text not null check (category in ('auslaenderbehoerde','doctor','pharmacy','bank','community','other')),
  subcategory    text,                 -- e.g. 'hausarzt','kinderarzt','frauenarzt','zahnarzt','welcome_center','language_cafe'
  name           text not null,
  address        text,
  district       text,
  city           text not null default 'Dresden',
  lat            double precision,
  lng            double precision,
  phone          text,
  website        text,
  languages      text[],
  opening_hours  text,
  notes_en       text,
  source         text not null check (source in ('brave','firecrawl','manual')),
  source_url     text not null,
  retrieved_at   timestamptz not null default now(),
  -- Dedupe key for PostgREST upsert (?on_conflict=dedupe_key)
  dedupe_key     text generated always as (category || '|' || lower(name) || '|' || coalesce(lower(address), '')) stored,
  constraint resources_dedupe_key_unique unique (dedupe_key)
);
create unique index resources_category_name_address_uidx
  on public.resources (category, lower(name), coalesce(lower(address), ''));
create index resources_category_sub_idx on public.resources (category, subcategory);

-- ---------- guides: sourced how-to guides (documents, appointments, ...) ----------
create table public.guides (
  id          uuid primary key default gen_random_uuid(),
  slug        text unique not null,     -- e.g. 'bank-account-documents'
  topic       text not null,
  city        text default 'Dresden',
  title_en    text not null,
  summary_en  text not null,
  checklist   jsonb not null default '[]'::jsonb,   -- array of strings
  content_md  text,
  sources     jsonb not null default '[]'::jsonb,   -- array of {url,title,retrieved_at}
  updated_at  timestamptz default now()
);

-- ---------- RLS: read-only for the browser; only service_role (n8n) writes ----------
alter table public.resources enable row level security;
alter table public.guides    enable row level security;

create policy "public read resources" on public.resources for select to anon, authenticated using (true);
create policy "public read guides"    on public.guides    for select to anon, authenticated using (true);

-- Defence in depth: no write grants for browser roles (service_role bypasses RLS and keeps its grants).
revoke insert, update, delete on public.resources from anon, authenticated;
revoke insert, update, delete on public.guides    from anon, authenticated;
