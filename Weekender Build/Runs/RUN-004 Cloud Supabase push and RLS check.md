---
type: run
date: 2026-09-25 20:10
by: claude (abdul)
result: pass
build: supabase project ycyrtlzympxzlfcocazh (weekender-build, eu-central-1)
---
# Run: Cloud Supabase push and RLS check

## Goal
Push the [[Data Model]] migrations + seed to the real project and confirm RLS behaves like local ([[RUN-001 Local DB schema and RLS check]]).

## Steps
1. `npx supabase link --project-ref ycyrtlzympxzlfcocazh` (CLI login only, no DB password needed).
2. `npx supabase db push --include-seed` → both migrations + seed applied.
3. REST checks with the **public anon key**.

## Result
| Check | Got |
|---|---|
| read demo request | `booked`, Hausarztpraxis Dr. Weber ✅ |
| transcript lines readable | 7 ✅ |
| insert without consent | 401 ✅ |
| anon write transcript | 401 ✅ |

## Open
- Vault secrets `n8n_new_request_url` + `n8n_webhook_secret` not set yet → trigger is a no-op until then (by design).
- Connect Lovable → Integrations → Supabase → this project (NOT Lovable Cloud).
