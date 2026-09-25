---
type: concept
tags: [stack, supabase]
sources: [https://supabase.com/docs/guides/database/postgres/row-level-security, https://supabase.com/docs/guides/realtime/postgres-changes, https://supabase.com/docs/guides/realtime/limits, https://supabase.com/docs/guides/database/webhooks, https://supabase.com/docs/guides/database/extensions/pg_net, https://supabase.com/docs/guides/functions/secrets, https://supabase.com/docs/guides/functions/auth, https://supabase.com/pricing, https://docs.n8n.io/integrations/builtin/credentials/supabase/]
---
# Supabase: Practical Guide (Sept 2026)

**Definition:** Supabase is hosted Postgres with an auto-generated REST API, Row Level Security (RLS), Realtime change feeds, Edge Functions (Deno) and Database Webhooks (via the `pg_net` extension).

**Why it matters for us:** it is the shared state between the Lovable UI, n8n and the call relay. Realtime gives us the live transcript and status "for free", without polling.

## 0. Project setup (10 min)

1. supabase.com → New project → **Region: Central EU (Frankfurt), `eu-central-1`**. Keeping data in the EU fits our GDPR story. Choose a strong DB password and store it in the password manager.
2. Invite the teammate: Organization → Team.
3. Keys (Project Settings → **API Keys**):
   - **Publishable key** (`sb_publishable_…`, or the legacy `anon` key): goes in the frontend; it is safe **only with RLS on**.
   - **Secret key** (`sb_secret_…`, or the legacy `service_role` key): **bypasses RLS**. Use it only in n8n, the relay server and Edge Functions. Legacy `service_role` keys are being phased out, and n8n says to migrate "before legacy keys are disabled at the end of 2026" ([n8n credential docs](https://docs.n8n.io/integrations/builtin/credentials/supabase/)).
4. Connect the project to Lovable **before** the first backend prompt (see [[Lovable - Practical Guide]]).

**Free tier** ([pricing](https://supabase.com/pricing), [realtime limits](https://supabase.com/docs/guides/realtime/limits)): 2 active projects, 500 MB DB, 1 GB file storage, 5 GB egress, 500k Edge Function invocations, Realtime **200 concurrent connections**, 100 msgs/s, 2M messages/month. Projects **pause after 1 week of inactivity**. That's irrelevant for the weekend, but matters for the Monday plan. Egress, invocations and message numbers come from secondary summaries. *Verify on the pricing page if they become relevant.*

## 1. Schema (HalloTermin example; run in SQL Editor)

```sql
create table public.call_requests (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  owner           uuid default auth.uid(),          -- null if no auth at all
  user_name       text not null check (char_length(user_name) between 2 and 80),
  user_email      text not null check (user_email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
  practice_name   text not null,
  practice_phone  text not null check (practice_phone ~ '^\+?[0-9 ]{6,20}$'),
  reason_category text not null check (reason_category in ('first_exam','checkup','vaccination','other')),
  insurance       text,
  time_windows    jsonb not null default '[]'::jsonb,
  consent         boolean not null check (consent = true),
  status          text not null default 'new'
                  check (status in ('new','briefing','calling','booked','rejected','failed')),
  brief_de        text,
  booked_slot     timestamptz,
  outcome         jsonb,
  error           text
);

create table public.call_events (          -- one row per transcript line / status event
  id          bigint generated always as identity primary key,
  request_id  uuid not null references public.call_requests(id) on delete cascade,
  created_at  timestamptz not null default now(),
  speaker     text check (speaker in ('agent','praxis','system')),
  text_de     text,
  text_en     text
);
create index on public.call_events (request_id, created_at);
```

Generic lesson: **one "request" table with a `status` column plus one "events" table** covers most orchestrated apps. The `check` constraints are our cheap input validation when anonymous users can insert.

## 2. RLS for a demo without real login

RLS is on by default for tables created in the dashboard. Without policies, **every anon request is denied, and it fails silently** (empty results, or an insert error). See [[Rules/RLS - test inserts as anon]].

### Option A (recommended): anonymous sign-ins, so each browser owns its rows
Enable **Authentication → Sign In / Providers → Allow anonymous sign-ins** (*menu path from memory; verify*). In the app, call `await supabase.auth.signInAnonymously()` on first load. Anonymous users get the `authenticated` role and a real `auth.uid()`.

```sql
alter table public.call_requests enable row level security;
alter table public.call_events   enable row level security;

create policy "insert own request" on public.call_requests
  for insert to authenticated with check (owner = (select auth.uid()));
create policy "read own requests" on public.call_requests
  for select to authenticated using (owner = (select auth.uid()));
create policy "read own events" on public.call_events
  for select to authenticated
  using (exists (select 1 from public.call_requests r
                 where r.id = request_id and r.owner = (select auth.uid())));
-- no update/delete policies: only n8n/relay (secret key, bypasses RLS) change status and events
```

### Option B (fallback, demo data only): plain anon insert + public read
```sql
create policy "anon can insert" on public.call_requests
  for insert to anon with check (consent = true and status = 'new');
create policy "anon can read" on public.call_requests
  for select to anon using (true);   -- EVERYONE can read EVERY row: use only fake names/DOBs
create policy "anon can read events" on public.call_events
  for select to anon using (true);
```
The docs warn that `to anon using (true)` should be used "only for data that is meant to be public" ([RLS docs](https://supabase.com/docs/guides/database/postgres/row-level-security)).

**Pitfalls:**
- Always name the role with `to anon` / `to authenticated` ([docs](https://supabase.com/docs/guides/database/postgres/row-level-security)).
- `supabase.from('call_requests').insert(row).select()` also needs a **SELECT** policy, or the insert "works" but returns nothing or errors. With Option A it's covered.
- Don't let the client set `status`. With Option B, the `with check (status = 'new')` enforces that.
- The secret key bypasses RLS (`service_role` has `bypassrls`), so n8n updates work without policies.

## 3. Realtime for live status and transcript

```sql
alter publication supabase_realtime add table public.call_requests, public.call_events;
```
([docs](https://supabase.com/docs/guides/realtime/postgres-changes); also possible in Dashboard → Database → Publications.)

Frontend (what Lovable should generate):
```js
const channel = supabase
  .channel(`call-${requestId}`)
  .on('postgres_changes',
      { event: 'INSERT', schema: 'public', table: 'call_events', filter: `request_id=eq.${requestId}` },
      (p) => appendLine(p.new))
  .on('postgres_changes',
      { event: 'UPDATE', schema: 'public', table: 'call_requests', filter: `id=eq.${requestId}` },
      (p) => setStatus(p.new.status))
  .subscribe();
// on unmount: supabase.removeChannel(channel)
```
- Realtime **respects RLS SELECT policies**, so if the user can't select a row, they won't get its event.
- Load the existing rows first (`select … order by created_at`), then subscribe, so a page refresh doesn't lose the transcript.
- `postgres_changes` is processed single-threaded (ordering is preserved) ([docs](https://supabase.com/docs/guides/realtime/postgres-changes)). That's fine at demo scale. For very high-frequency streams, Supabase **Broadcast** is the alternative. *Not needed here.*

## 4. Database Webhooks → n8n (pg_net)

Database Webhooks are "a convenience wrapper around triggers using the pg_net extension". They are async and don't block the insert ([docs](https://supabase.com/docs/guides/database/webhooks)). The payload is `{ type, table, schema, record, old_record }`.

**Dashboard way (easiest):** Database → **Webhooks** (Integrations) → Create → table `call_requests`, events **Insert**, type HTTP Request, method POST, URL = **n8n production webhook URL**, add header `X-Webhook-Secret: <long random>`, timeout 5000 ms.

**SQL way** (equivalent, version-controllable):
```sql
create or replace function public.notify_n8n_new_request()
returns trigger language plpgsql security definer as $$
begin
  perform net.http_post(
    url     := 'https://<your>.app.n8n.cloud/webhook/hallotermin-new-request',
    body    := jsonb_build_object('type','INSERT','table',TG_TABLE_NAME,'record',to_jsonb(NEW)),
    headers := jsonb_build_object('Content-Type','application/json',
                                  'X-Webhook-Secret',
                                  (select decrypted_secret from vault.decrypted_secrets where name = 'n8n_webhook_secret')),
    timeout_milliseconds := 5000
  );
  return NEW;
end $$;

create trigger on_call_request_insert
after insert on public.call_requests
for each row execute function public.notify_n8n_new_request();
```
- Store the secret once: `select vault.create_secret('<long random>', 'n8n_webhook_secret');`. *Vault usage is from memory; verify. For a hackathon, hard-coding the header in the dashboard webhook is acceptable.*
- Requests start **only after the transaction commits**. The default timeout is 2000 ms ([pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net)).
- **Debug:** `select id, status_code, error_msg, timed_out, created ... from net._http_response order by id desc limit 10;` (kept for 6 h). A 404 here almost always means n8n's test URL or an unpublished workflow (see [[Rules/n8n - use production webhook URLs]]).
- Don't fire on your own status updates: use **Insert** only, or guard with `when (NEW.status = 'new')`.

## 5. Edge Functions as webhook receivers (when needed)

Use them only if something external must write to the DB and can't hold the secret key. For example, if we end up on Lovable Cloud (no secret key), n8n would call an Edge Function instead of using the Supabase node.
- By default a function requires a valid JWT. For a webhook receiver, deploy with **`--no-verify-jwt`** (or set `verify_jwt = false` in `config.toml`, or use the dashboard toggle) and **check your own shared-secret header** in code ([docs](https://supabase.com/docs/guides/functions/auth)).
- Built-in env vars: `SUPABASE_URL`, `SUPABASE_DB_URL`, `SUPABASE_PUBLISHABLE_KEYS`, `SUPABASE_SECRET_KEYS`. Your own secrets can't start with `SUPABASE_` ([docs](https://supabase.com/docs/guides/functions/secrets)).

```ts
// supabase/functions/n8n-callback/index.ts  (sketch)
import { createClient } from 'npm:@supabase/supabase-js@2'
Deno.serve(async (req) => {
  if (req.headers.get('x-webhook-secret') !== Deno.env.get('N8N_SHARED_SECRET'))
    return new Response('forbidden', { status: 403 })
  const { id, status, booked_slot } = await req.json()
  const db = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SERVICE_KEY')!) // set SERVICE_KEY as a secret
  const { error } = await db.from('call_requests').update({ status, booked_slot }).eq('id', id)
  return new Response(JSON.stringify({ ok: !error, error }), { status: error ? 500 : 200 })
})
```
*(`SUPABASE_SECRET_KEYS` is a JSON map in the new key system. Setting your own `SERVICE_KEY` secret avoids having to parse it. Unverified detail.)*

**Related:** [[Stack Overview - Lovable n8n Supabase]] · [[Integration Patterns]] · [[n8n - Practical Guide]]
