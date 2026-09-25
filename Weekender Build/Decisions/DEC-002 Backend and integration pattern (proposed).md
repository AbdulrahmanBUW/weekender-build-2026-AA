---
type: decision
date: 2026-09-25
status: proposed
deciders: [abdul, teammate]
---
# Decision: Backend (Lovable Cloud vs own Supabase) and integration pattern

## Context
- The build must be live by Sun 14:00 and include an n8n workflow that moves data. Team: 2 people, not primarily developers. Lovable Pro gives about 100 credits plus 5 per day.
- n8n (Supabase node) and the HalloTermin call relay both need to **write** to the database server-side, which needs a Supabase **secret/service key**.
- Lovable Cloud is on by default. It does **not** give out the service key and doesn't show the project in a Supabase dashboard ([Supabase troubleshooting](https://supabase.com/docs/guides/troubleshooting/cant-access-supabase-project-lovable-cloud)). There is **no one-click migration** between Cloud and your own Supabase, and once Cloud is enabled it can't be switched ([Lovable docs](https://docs.lovable.dev/integrations/supabase)).
- The idea may merge with the teammate's idea, so the pattern must be generic: request row → n8n → status back → live UI.

## Options

**Backend**
1. **Lovable Cloud (Europe region).** Zero setup, and it has an SQL editor in Lovable. But n8n and the relay can't use the secret key, so every external write needs an Edge Function proxy with a shared secret (more code, more credits). Usage bills against Lovable credits.
2. **Own Supabase project (Frankfurt, free tier) connected to Lovable.** About 15 min of setup. We get the full dashboard, the secret key for n8n and the relay, and both teammates can have access. It survives beyond Lovable (Monday plan). Lovable still runs migrations and generates the client code.

**Trigger pattern** (details in [[Integration Patterns]])
- (a) App → Supabase insert → Database Webhook (pg_net) → n8n
- (b) App → n8n webhook directly from the browser
- (c) App → Supabase Edge Function → n8n

**Results pattern**
- (i) n8n/relay → Supabase update/insert → Realtime → UI
- (ii) Synchronous Respond to Webhook
- (iii) Polling

## Decision (proposed)
- **Backend: option 2, own Supabase in `eu-central-1` (Frankfurt), connected to the Lovable project *before* the first backend prompt.**
- **Trigger: (a) DB Webhook on INSERT into the request table → n8n *production* webhook with Header Auth (`X-Webhook-Secret`).**
- **Results: (i).** n8n updates status fields with the Supabase node. The relay inserts transcript rows directly. The UI subscribes via Realtime `postgres_changes`.
- **RLS:** Supabase anonymous sign-ins plus owner-based policies. Fallback: anon insert plus public read with fake demo data only ([[Supabase - Practical Guide#2. RLS for a demo without real login]]).
- **Vercel:** not used, unless Lovable credits run out (fallback frontend host). The relay runs in Docker on a VM/PaaS or behind a tunnel.

## Consequences
- ✅ No secrets in the frontend, no CORS work, one source of truth (`status` column), and a live UI without polling.
- ✅ n8n workflows stay simple: the Supabase node with a secret-key credential, and no Edge Function code.
- ✅ Generic: a merged idea only has to rename the tables and swap WF1's "action" step.
- ⚠️ Setup order matters. If anyone clicks "enable Cloud" first, that Lovable project is stuck on Cloud, and we'd have to start a new Lovable project (cheap on Friday, expensive on Saturday). → [[Rules/Decide Lovable backend before first prompt]]
- ⚠️ The DB webhook is fire-and-forget: if n8n is down or unpublished, the insert succeeds but nothing happens. Mitigation: check `net._http_response`, and add a "retry" path.
- ⚠️ We must remember n8n **Publish** plus **production URLs** → [[Rules/n8n - use production webhook URLs]].
- ⚠️ Supabase free projects pause after 7 idle days. Note it in the [[Monday-Morning Plan]].
- Fallback if pattern (a) fails on Saturday evening: switch to (b) with Allowed Origins set to the single `*.lovable.app` origin, and let n8n insert the row itself.

**Related:** [[Stack Overview - Lovable n8n Supabase]] · [[Lovable - Practical Guide]] · [[n8n - Practical Guide]]
