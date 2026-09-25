---
type: run
date: 2026-09-25 19:40
by: claude (abdul)
result: pass
build: local supabase (docker), migration 20260925190000_init_schema
---
# Run: Local DB schema and RLS check

## Goal
Verify the [[Data Model]] migration applies, seed loads, Realtime publication is set, and RLS behaves as designed for the browser (anon key).

## Steps
1. `npx supabase start` → migration + `seed.sql` applied (1 booked request, 7 transcript lines, 5 events).
2. REST calls with the local anon key against `/rest/v1/...`.

## Result
| # | Action (anon) | Expected | Got |
|---|---|---|---|
| 1 | insert request with consent | allowed | 201 ✅ |
| 2 | insert request without consent | blocked | 401 ✅ |
| 3 | insert with non-category reason ("headache") | blocked by check | 400 ✅ |
| 4 | update request status | 0 rows (RLS filters silently) | 204, 0 rows ✅ |
| 5 | insert transcript line | blocked | 401 ✅ |
| 6 | read transcript | allowed (demo mode) | 200 ✅ |

Realtime publication contains: call_requests, calls, transcript_lines, events ✅

## Defects found
- none. Known limitation (by design): demo-mode read-all policy → Monday-morning item.
