---
type: rule
severity: must
source: https://supabase.com/docs/guides/database/postgres/row-level-security
---
# Rule: Never put service/secret keys in the frontend

**Rule:** The Lovable app may only contain the Supabase **publishable/anon** key (`VITE_SUPABASE_PUBLISHABLE_KEY`). The Supabase **secret key** (`sb_secret_…` / `service_role`), Twilio, Deepgram and Anthropic keys, and n8n webhook secrets live only in n8n credentials, the relay's env vars, or Supabase/Lovable **Secrets** (read in Edge Functions via `Deno.env.get`).
**Why:** Everything in the frontend, including all `VITE_*` variables, ships in the public JS bundle. A secret key "authorizes access through the `service_role` Postgres role, which has the `bypassrls` attribute", and Supabase says: "Never use a secret key in the browser" ([RLS docs](https://supabase.com/docs/guides/database/postgres/row-level-security)). A leaked key means anyone can read our users' names and birth dates, or burn our API credits.
**How to check:** In the published app, open DevTools → Sources and search the bundle for `sb_secret`, `service_role`, `sk-ant`, `AC` (Twilio SID) and `webhook`. Search the synced GitHub repo the same way (`git grep -nE "sb_secret|service_role|sk-ant"`). Also read the Lovable Publish security-scan findings. See also [[No secrets in repo]].
