---
type: run
date: 2026-09-25 20:00
by: claude (abdul)
result: pass
build: local supabase, migration 20260925200000_notify_n8n_on_request
---
# Run: DB trigger → n8n webhook (pattern from [[DEC-002 Backend and integration pattern (proposed)]])

## Goal
Prove "app inserts row → Postgres trigger (pg_net) → n8n production webhook with secret header" without exposing the n8n URL to the browser.

## Steps
1. Stored URL + secret in Supabase Vault (`n8n_new_request_url`, `n8n_webhook_secret`), pointing at a local fake n8n (`host.docker.internal:8765`).
2. Inserted a `call_requests` row via REST with the **anon** key (like the Lovable app will).
3. Checked what the fake receiver got, `net._http_response`, and `events`.

## Result
- insert → 201 ✅
- receiver got `path=/webhook/new-request`, `X-Webhook-Secret` correct, record with `status=submitted` ✅
- `net._http_response` → 200 ✅
- `events` row `n8n_notified` written ✅
- Without Vault secrets the trigger is a no-op (inserts never fail because of n8n) ✅ (by design, seed run)

## To do in real env
```sql
select vault.create_secret('https://<instance>.app.n8n.cloud/webhook/new-request', 'n8n_new_request_url');
select vault.create_secret('<long random>', 'n8n_webhook_secret');
```
n8n Webhook node: check header `X-Webhook-Secret` → reject otherwise. Use the **production** URL and **Publish** the workflow → [[n8n - use production webhook URLs]].

## Defects found
- none
