---
type: run
date: 2026-09-25 21:45
by: claude (abdul)
result: pass
build: supabase ycyrtlzympxzlfcocazh + n8n peFxjt572HiUxu61 (async version, published)
---
# Run: Full loop — DB → n8n → Claude → DB

## Goal
Confirm the async fix for [[DEF-003 pg_net 5s timeout vs Claude latency]]: results land back in Supabase.

## Steps
Anon insert (Amina, Kinderarztpraxis, fake data) → poll `call_requests.status` every 5 s → read brief + events.

## Result ✅
- `submitted` → `briefed` in **≤10 s**
- `call_brief_de` filled: disclosure in sentence 1, facts, window "30.09.2026, 08:00–10:00 Uhr", all rules
- events: `system/n8n_notified` → `n8n/brief_created`

## Observations for later
- ERÖFFNUNG didn't restate the reason (Erstuntersuchung) this time → tighten prompt if needed.
- For a Kinderarzt the patient is usually the *child* — v2: add "patient is my child" field.
- Test rows (E2E 1–3) are in the DB; clean up before the demo.
