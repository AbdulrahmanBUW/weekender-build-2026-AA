---
type: run
date: 2026-09-25 19:40
by: claude (abdul)
result: partial
build: n8n workflow peFxjt572HiUxu61 (HalloTermin 01 – New request → German call brief)
---
# Run: n8n workflow 01 logic test

## Goal
Verify the first n8n workflow (built via the n8n MCP connection): Supabase webhook payload → normalize → validate consent/phone/name → Claude German call brief → JSON response.

## Steps
1. Created workflow via n8n MCP (`.mcp.json`), personal project. Claude node auto-assigned **Gateway credits** (no API key).
2. `test_workflow` with pinned webhook payload (Supabase INSERT shape) and pinned Claude output.

## Result
- Run 1: ❌ IF node — unary operators need `singleValue: true` → [[DEF-001 n8n IF unary operator type error]] fixed.
- Run 2: ✅ Normalize extracts `body.record.*` correctly; valid request routes to brief branch; response node runs.
- **Not yet tested:** the real Claude call and the live webhook (needs Header Auth credential + Publish).

## Next
1. In n8n: create credential **Supabase webhook secret** (Header Auth, name `X-Webhook-Secret`, value = long random) → attach to webhook → **Publish**.
2. Live test: `POST https://arahmandeaxo.app.n8n.cloud/webhook/new-request` with that header.
3. Add Supabase write-back (status `briefed`, `call_brief_de`, `events`) once the cloud Supabase project exists.
