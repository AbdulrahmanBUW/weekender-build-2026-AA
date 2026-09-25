---
type: run
date: 2026-09-25 20:00
by: claude (abdul)
result: partial
build: supabase ycyrtlzympxzlfcocazh + n8n peFxjt572HiUxu61 (published)
---
# Run: First end-to-end — DB insert → pg_net → n8n → Claude

## Goal
Insert a request like the app will (anon key) and see the German brief come out of Claude via n8n.

## Result
| Step | Result |
|---|---|
| anon insert into `call_requests` | 201 ✅ |
| pg_net trigger → n8n production webhook, `X-Webhook-Secret` accepted | ✅ |
| Normalize + validate | ✅ |
| Claude (Gateway credits, `claude-sonnet-5`) attempt 1 | ❌ [[DEF-002 Claude temperature deprecated]] → fixed |
| Claude attempt 2 | ✅ 5.6 s, 590 in / 472 out tokens — German brief with disclosure in sentence 1, facts, windows with weekdays, rules |
| Response back to the DB | ❌ pg_net 5 s timeout → [[DEF-003 pg_net 5s timeout vs Claude latency]] |

## Sample brief (fake data)
> ERÖFFNUNG: Guten Tag, ich bin eine KI-Assistentin und rufe im Auftrag von Test Person (E2E 2) an, die noch kein Deutsch spricht, um einen Termin zur Vorsorgeuntersuchung in der Praxis Dr. Test zu vereinbaren. … ERLAUBTE ZEITFENSTER: Donnerstag, 01.10.2026, 09:00–11:00 Uhr …

## Next
Async pattern (draft saved): ack immediately → Claude → Supabase update (`status=briefed`, `call_brief_de`) + `events` row. Needs n8n credential **Supabase weekender-build**.
