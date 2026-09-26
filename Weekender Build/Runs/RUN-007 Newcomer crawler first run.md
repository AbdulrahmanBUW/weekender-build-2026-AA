---
type: run
date: 2026-09-26 10:15
by: claude (abdul)
result: pass
build: supabase ycyrtlzympxzlfcocazh (migration 20260926090000) + n8n 9Dl8JmCdK418btfF (manual trigger, not published)
---
# Run: Newcomer crawler first run

## Goal
Check that [[Newcomer Resources - Crawler]] writes real, sourced rows into `resources` and `guides`, with a small run to save credits (4 place jobs + 1 guide).

## Steps
1. Schema: `npx supabase db reset` locally, then `npx supabase db push --yes`. REST check with the anon key: `select` on both tables → 200 `[]`; anon `insert` → **401 permission denied** on both tables. Local service-role upsert twice with the same row → 1 row (dedupe works).
2. Probe workflow (temporary, archived) to learn the real output shape of Brave place search, Brave web search and Firecrawl scrape.
3. Created workflow 02, pinned-data test (execution 10/11): found [[DEF-005 URL global missing in n8n Code node]], fixed, re-test green.
4. Real run, execution **12**, `LIMIT = 4` place jobs / `1` guide. Duration 31 s.
5. Checked rows in Supabase, fixed data problems ([[DEF-004 Supabase node stores jsonb payload as string]], [[DEF-006 Brave place results stale or misclassified]]), pinned regression test (execution 14), set limits back to 0 (full run).

## Result ✅
- Upserts: resources **201**, guides **201**, events row id 12.
- **25 resource rows** landed: auslaenderbehoerde 3, doctor (hausarzt) 8, pharmacy 8, bank (Sparkasse) 6.
- After clean-up (removed 1 misclassified NGO row and 1 stale address): **23 rows** (auslaenderbehoerde 1, doctor 8, pharmacy 8, bank 6).
- **1 guide**: `auslaenderbehoerde-dresden-appointment`, 9 checklist steps, 2 dresden.de sources. Content matches the source: new address Lingnerallee 3 (since May 2026), hotline + times, emergency-appointment rules, the 5 steps on the day. Claude noted that the two pages disagree on the entrance (Nord vs A) instead of picking one.
- Credits used: 5 Brave calls, 2 Firecrawl scrapes, 1 Claude call (+ 1 probe each for Brave place, Brave web, Firecrawl).

## Observations for later
- Brave place results rarely include phone numbers (2 of 25).
- Queries with "English" do not prove English-speaking doctors. We leave `languages` empty on purpose.
- Remaining jobs (Kinderarzt, Frauenarzt, Zahnarzt, Altstadt pharmacies, Deutsche Bank, Commerzbank, community places) and 3 guides are not run yet: one full run ≈ 20 Brave calls, ≤ 8 Firecrawl scrapes, 4 Claude calls.

## Defects found
- [[DEF-004 Supabase node stores jsonb payload as string]]
- [[DEF-005 URL global missing in n8n Code node]]
- [[DEF-006 Brave place results stale or misclassified]]
