-- Translations for newcomer guides (UI languages ar, tr, uk; more can be added).
-- Shape: {"ar": {"title": "...", "summary": "...", "checklist": ["..."]}, "tr": {...}, "uk": {...}}
-- English stays in title_en / summary_en / checklist. RLS unchanged: guides stay read-only for anon/authenticated.
alter table public.guides
  add column if not exists i18n jsonb not null default '{}'::jsonb
  check (jsonb_typeof(i18n) = 'object');

comment on column public.guides.i18n is
  'Translations keyed by language code: {"<lang>": {"title", "summary", "checklist": [..]}}. Fallback: English columns.';
