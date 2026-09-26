---
type: concept
tags: [stack, n8n, database, data]
sources: ["supabase/migrations/20260926090000_newcomer_resources.sql", "n8n/workflows/02-newcomer-resource-crawler.json", "https://arahmandeaxo.app.n8n.cloud/workflow/9Dl8JmCdK418btfF"]
---
# Newcomer Resources: Crawler

**Definition:** A small, reusable data layer of practical, sourced information for newcomers in **Dresden**. It has two tables, `resources` (places) and `guides` (how-to guides). An n8n workflow fills them: **"Newcomer 02 – Resource crawler (Dresden)"**.

**Why it matters for us:** It works whatever idea we merge into ([[Merged Concept]]). HalloTermin can suggest a real practice, and an onboarding app can show "what to bring to the Ausländerbehörde". The app only reads, and every row has a source link and a date.

**Related:** [[Data Model]] · [[n8n - Practical Guide]] · [[RUN-007 Newcomer crawler first run]] · [[DEF-004 Supabase node stores jsonb payload as string]] · [[DEF-005 URL global missing in n8n Code node]] · [[DEF-006 Brave place results stale or misclassified]]

## What it collects

| Category (`resources.category`) | Subcategories | Source |
|---|---|---|
| `auslaenderbehoerde` | – | Brave place search |
| `doctor` | `hausarzt`, `kinderarzt`, `frauenarzt`, `zahnarzt` | Brave place search |
| `pharmacy` | `apotheke` | Brave place search |
| `bank` | `sparkasse`, `deutsche_bank`, `commerzbank` | Brave place search |
| `community` | `welcome_center`, `migrant_counselling`, `language_cafe`, `international_office`, `international_community` | Brave place search |

Guides (`guides.slug`): `auslaenderbehoerde-dresden-appointment`, `bank-account-documents` (incl. Basiskonto right), `anmeldung-dresden`, `health-insurance-registration`.

## How it works

```
Manual trigger
 ├─ Place Jobs (16 queries) → Brave place_search → Map Places to Rows → UPSERT resources (on_conflict=dedupe_key)
 └─ Guide Jobs (4 topics) → Brave web search → Pick Official URLs (allow-list, deny-list)
      → Loop: Firecrawl scrape (markdown) → 2 s pause → next URL
      → Group by Guide → Claude (facts only, strict JSON) → UPSERT guides (on_conflict=slug)
 → Summarize → insert events row (source 'n8n', type 'resources_crawled', payload = counts)
```

- **Places filter:** only Dresden postcodes (010xx–013xx), a name/category match per job, and dedupe inside the batch. The table also has a unique `dedupe_key` (`category|lower(name)|lower(address)`), so a re-run updates rows instead of duplicating them.
- **Errors never stop the run:** every Brave/Firecrawl/Claude/HTTP node has `onError: continueRegularOutput` plus retries. Failed jobs and pages are listed in the `events.payload` (`place_jobs_failed`, `guide_pages_failed`, `guides_failed`).
- **Claude prompt rules:** use only facts in the scraped text, B1 English, keep German document names with English in brackets, mention conflicting sources, output strict JSON `{title_en, summary_en, checklist[], content_md}`. Model `claude-sonnet-5`, **no temperature** ([[DEF-002 Claude temperature deprecated]]).
- A footer with the source links and "check before you go" is added to every guide.

## Sources: allow / deny

**Allowed**
- Brave Search API (place results and web results), via n8n Gateway credits.
- Firecrawl **scrape** (single pages, markdown) of official pages only: `dresden.de`, `tu-dresden.de`, `verbraucherzentrale.de`, `bafin.de`, `bundesbank.de`, `make-it-in-germany.com`, `bundesgesundheitsministerium.de`, official bank sites (`sparkasse.de`, `ostsaechsische-sparkasse.de`).

**Never** (their terms forbid automated extraction; a deny-list regex in *Pick Official URLs* enforces it)
- 116117 Arztsuche, KV Sachsen Arztsuche, Doctolib, Jameda, Google Maps pages.

**Rules we follow**
- Only public business and official information. No data about private individuals. Doctors appear only as practice listings.
- Respect robots.txt and site terms. One page at a time, 2 s pause between pages. No crawl (`crawl`) and no map, only single-page scrape.
- Always keep `source_url` and `retrieved_at`. `notes_en` says that languages, opening hours and phone are **not verified**.
- "English-speaking" in a query is only a search hint. We do **not** claim a doctor speaks English (`languages` stays empty).

## Tables (short; details in [[Data Model]])
- `public.resources`: place rows, unique `dedupe_key`, `source in ('brave','firecrawl','manual')`.
- `public.guides`: one row per `slug`, `checklist` (jsonb array of strings), `sources` (jsonb array of `{url,title,retrieved_at}`).
- RLS: `anon`/`authenticated` can only **SELECT**. Writes only with the service key (n8n credential "Supabase account"). Tested: anon insert → 401 `permission denied`.

## How to run
1. Open the workflow in n8n: https://arahmandeaxo.app.n8n.cloud/workflow/9Dl8JmCdK418btfF
2. Click **Execute workflow**. There is no schedule on purpose (credits).
3. Cheap test: set `LIMIT = 4` in *Place Jobs* and `LIMIT = 1` in *Guide Jobs*. `LIMIT = 0` runs everything.
4. Check: `select category, count(*) from resources group by 1;` and the newest `events` row with `type = 'resources_crawled'`.
5. Add a place by hand: insert with `source = 'manual'` and a `source_url` (e.g. the official page).
6. Add a query or guide: edit the `jobs` / `guides` array in the Code node (guides need an `allow` domain list).

## Reading from the app (Lovable)
```ts
supabase.from('resources').select('*').eq('category', 'doctor').eq('subcategory', 'hausarzt')
supabase.from('guides').select('*').eq('slug', 'bank-account-documents').single()
```
Always show `source_url` / `sources` and the "check before you go" note.

## Translations (i18n)
- Column `public.guides.i18n jsonb` (migration `20260926190000_guides_i18n.sql`, default `{}`, must be a JSON object). Still read-only for the browser.
- Shape: `{"ar": {"title", "summary", "checklist": [..]}, "tr": {...}, "uk": {...}}`. English stays in `title_en` / `summary_en` / `checklist`.
- Filled for all 4 guides in **ar, tr, uk** (the demo UI languages). Plain B1 language; German official terms (Anmeldung, Bürgerbüro, Ausländerbehörde, Basiskonto, Mitgliedsbescheinigung …) stay in Latin script with the local explanation in brackets. Same number of checklist items as English, no extra facts.
- App: `guide.i18n?.[lang]?.title ?? guide.title_en` (same for `summary`, `checklist`). Arabic needs `dir="rtl"`.
- Add a language: translate title, summary and checklist (same item count), then `update guides set i18n = i18n || jsonb_build_object('fa', '{"title":"…","summary":"…","checklist":["…"]}'::jsonb) where slug = '…';` with the service key or `npx supabase db query --linked -f file.sql` (UTF-8 file, double single quotes). If the crawler re-writes a guide, re-check its translations.

## Costs (approx. per full run)
- Brave: 16 place searches + 4 web searches = 20 calls.
- Firecrawl: up to 8 scrapes (2 per guide), 1 credit each.
- Claude: 4 calls, about 3–7k input tokens each (page text is cut to 12,000 characters per page).
- The test run (4 place jobs + 1 guide) used 5 Brave calls, 2 Firecrawl scrapes and 1 Claude call.

## Known limits
- Brave place data can be stale (the Ausländerbehörde moved to Lingnerallee 3 in May 2026; Brave still listed the old address). See [[DEF-006 Brave place results stale or misclassified]].
- Phone numbers are often missing in Brave place results; opening hours only for some places.
- Guides are only as good as the scraped pages. Re-run before a demo if pages change.
