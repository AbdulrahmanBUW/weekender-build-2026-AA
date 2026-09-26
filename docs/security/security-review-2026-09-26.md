# Security review: focused pass, 2026-09-26

**Skill:** `security-audit` (cloudflare/security-audit-skill), used in guidance mode for a focused review. This was not the full six-phase audit.
**Reviewed by:** Security auditor agent (Claude Code)
**Source ref:** `main` @ `0f21e2d`. The worktree was dirty: `services/voice-relay/server.js` and `public/index.html` were modified, and `roleplay-test.js` was untracked. The uncommitted state was reviewed.
**Scope:** `services/voice-relay/` (server.js, public/*), `supabase/migrations/*.sql`, `n8n/workflows/*.json`, `.mcp.json`, `.gitignore`, and git history (all 19 commits, all branches) checked for leaked secrets.
**Method:** Source reading only. No code was run, and no deployed endpoint, n8n instance or Supabase project was probed.
**Coverage:** This is partial coverage. The Lovable frontend is not in the repo and was not reviewed. There is no earlier security ledger.

## Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 2 |
| Low | 2 |
| Informational | 2 |
| Needs validation (no severity) | 3 |

**Secrets:** Nothing leaked. A Python regex scan over `git log -p --all` (328k lines) and the current uncommitted diff plus untracked files found 0 hits. It looked for Supabase JWTs, `sb_secret_`, `sk-ant-`, OpenAI `sk-`, GitHub tokens, AWS keys, PEM private keys, bearer tokens, and named assignments to `DEEPGRAM_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `N8N_*`, `ANTHROPIC_*` and `X-Webhook-Secret`. `.env` files never appear in history. `.gitignore` covers both `.env` and `services/voice-relay/.env`, which `git check-ignore` confirms.

---

## Findings (ranked)

### F1: MEDIUM. The voice relay accepts WebSocket connections from any website (no Origin check, no auth)

- **Where:** `services/voice-relay/server.js:158` (`new WebSocketServer({ server, path: '/call' })` has no `verifyClient`), `:160-175`, `:299`
- **Boundary crossed:** A web page from any origin that the operator opens while the relay runs can drive a relay that holds the Deepgram key and the Supabase **service-role** key. Binding to `127.0.0.1` stops remote hosts. It does not stop the operator's own browser: browsers do not apply CORS to WebSockets, and `ws` checks no Origin by default.
- **Impact:** Someone else's page can open `ws://127.0.0.1:8787/call?request=<uuid>` and:
  - start Deepgram Voice Agent and Anthropic sessions on your quota, with no limit on concurrent sessions;
  - use the service role to set any request's `status` to `calling`/`failed`/`booked`/`needs_user` and insert `calls`/`events` rows (`:168-173`, `:189-190`, `:234-248`);
  - receive the patient name and practice name (`:175`) plus the transcript and agent audio for that request.

  Request IDs are readable by anon under demo RLS, so an attacker can enumerate them.
- **Mitigating factors:** It only works while the relay is running on the operator's machine. Newer Chromium Local Network Access prompts may block it; this needs checking per browser. Firefox and Safari do not have the same control.
- **Fix (smallest):**
  - Add `verifyClient: ({ origin }) => [`http://127.0.0.1:${PORT}`, `http://localhost:${PORT}`].includes(origin)` to the `WebSocketServer` options.
  - Reject a `request` param that is not a UUID.
  - Cap concurrent calls at 1–2.
  - If the relay is ever exposed beyond localhost (tunnel or Vercel), also require a short-lived signed token.

### F2: MEDIUM. The anon insert policy lets the browser set server-owned columns, and every insert fans out into paid n8n and Claude work

- **Where:** `supabase/migrations/20260925190000_init_schema.sql:107-108` (`with check (consent_ai_call)` only; Supabase's default table grants give anon every column). Trigger: `20260925200000_notify_n8n_on_request.sql:41-43`. Consumer: `services/voice-relay/server.js:67`.
- **Boundary crossed:** An anonymous client can write `status`, `call_brief_de`, `id`, `created_at` and `consent_at`. Only n8n and the relay are supposed to own these.
- **Impact:**
  - **Faked state:** A client can insert rows already set to `booked`, `briefed` and so on.
  - **Prompt injection into the call agent:** An attacker can pre-fill `call_brief_de`. It survives whenever workflow 01 takes the "Mark Request Failed" branch, which only updates `status` (for example with an empty `practice_phone`). The relay then puts it verbatim into the agent's system prompt under "VORBEREITETES BRIEFING".
  - **Cost amplification:** Each anonymous insert triggers `pg_net`, then n8n, then one Claude call, with no rate limit.
- **Fix:**
  - Add a `BEFORE INSERT` trigger that forces `status := 'submitted'`, `call_brief_de := null`, `consent_at := now()` and `created_at := now()`. Alternatively, `revoke insert on call_requests from anon` and then `grant insert (patient_name, patient_dob, insurance_type, insurance_name, user_email, user_language, practice_name, practice_phone, reason_category, has_referral, is_new_patient, time_windows, consent_ai_call) on call_requests to anon`.
  - Add length checks on the text columns.
  - For production, put an Edge Function with rate limiting and CAPTCHA in front of inserts.

### F3: LOW. Unvalidated LLM function-call arguments can crash the relay mid-call

- **Where:** `services/voice-relay/server.js:115-117`, `:229-233`, `:212` (async handler, no try/catch)
- **Boundary:** The practice side of the call is untrusted speech, and it steers the model's `confirm_booking` args. `inWindows` compares strings, so a value like `time: "10:30 Uhr"` passes (`>= "08:00"` and `<= "12:00"`). `new Date(...)` is then invalid and `.toISOString()` throws `RangeError` inside an async `ws` listener. That is an unhandled rejection, which terminates the Node process on Node ≥15 and drops every active call.
- **Fix:**
  - Validate with `/^\d{4}-\d{2}-\d{2}$/` and `/^\d{2}:\d{2}$/` before `inWindows`, and send back `{ok:false}` on a mismatch.
  - Wrap the `dg.on('message')` body in try/catch.
  - Optionally add `process.on('unhandledRejection', console.error)` for the demo.

### F4: LOW. An unpinned `npx -y n8n-mcp` runs with the n8n API key

- **Where:** `.mcp.json:10-19`
- **Impact:** Every Claude Code session fetches whatever `n8n-mcp` version is latest on npm and runs it with `N8N_API_KEY`, which has full n8n instance API access. A compromised or typosquatted release would get that key.
- **Fix:** Pin an exact version (`"n8n-mcp@<x.y.z>"`), or install it as a pinned devDependency.

### F5: INFO. Patient names are written to stdout logs

- **Where:** `services/voice-relay/server.js:174` (uncommitted change)
- **Fix:** Log `req.id` only. This matters once real users exist (GDPR data minimisation).

### F6: INFO. `pg_net` keeps the webhook secret in its queue and response tables

- **Where:** `20260925200000_notify_n8n_on_request.sql:27-33`
- **Note:** The `X-Webhook-Secret` header sits in `net.http_request_queue` until it is sent, and responses stay in `net._http_response`. The `net` schema is not exposed through PostgREST by default, so there is no finding today. Keep it that way: do not add `net` to the exposed schemas.

---

## Needs validation (facts not in the repo)

1. **n8n webhook header auth is bound to the right credential.** `01-new-request-brief.json` sets `authentication: headerAuth`, but the exported node has no credential attached (credentials are stripped on export). In the n8n UI, confirm that the Header Auth credential uses the name `X-Webhook-Secret` and the same value as Vault `n8n_webhook_secret`. Then send one POST to the production URL with no header and expect 403. If the Vault secret is missing, the trigger sends an empty header (`coalesce(v_secret,'')`), so calls should fail closed. Check that as well.
2. **The Lovable frontend's rendering of `guides.content_md`.** This markdown is written by Claude from scraped third-party web pages (workflow 02). If the frontend renders it with raw HTML enabled (`dangerouslySetInnerHTML`, `rehype-raw`), stored XSS is possible. It must use a sanitising markdown renderer with HTML disabled. The same applies to `summary_en`/`checklist` and to `resources.website` (only allow `https?:` links, never `javascript:`).
3. **Whether browser Local Network Access (Chromium) blocks F1** in the browser you will demo with. Don't rely on it: F1's fix is two lines.

## Accepted risks for the demo (fake data only)

| Risk | Where | Why accepted | Fix before production |
|---|---|---|---|
| Anon can read **all** rows in `call_requests` (incl. `user_email`, `patient_dob`, `practice_phone`), `calls`, `transcript_lines`, `events` | `init_schema.sql:109-112` | Demo has no accounts; seed data is fictional | Supabase Auth; add `user_id uuid default auth.uid()` to `call_requests`; policies `using (user_id = auth.uid())`; child tables via `exists (select 1 from call_requests r where r.id = request_id and r.user_id = auth.uid())`; no anon read on `events` |
| Realtime broadcasts the same tables to any subscriber | `init_schema.sql:115-116` | Same as above | Realtime honours RLS, so owner-scoped policies fix it. Drop `events` from the publication. |
| Public read of `resources`/`guides` | `newcomer_resources.sql:50-51` | Intended: public business/official info with `source_url` | None needed. Writes are already revoked (`:54-55`). |
| Relay has no user auth | `server.js` | Localhost-only operator tool | See F1. Needs real auth if it ever leaves localhost. |

## Must-fix before real users

1. Owner-scoped RLS and auth, replacing all the "demo read" policies (table above).
2. F2: lock the anon-writable columns and rate-limit request creation (every insert costs Claude and n8n spend).
3. F1: Origin allowlist, UUID validation and a concurrency cap on the relay, plus a signed token if it is exposed beyond localhost.
4. Needs-validation #2: sanitised markdown rendering in the frontend.
5. F3: input validation on function-call args (a crash means a dropped live phone call).
6. Prompt-injection guard for the real phone flow. Treat `patient_name`, `practice_name` and `call_brief_de` as untrusted data in the agent prompt: length limits, strip newlines, and fence them as data. Allow `practice_phone` only for verified practice numbers, so the service cannot be used to place AI calls to arbitrary numbers.
7. F5: remove PII from logs, and set a retention policy for `transcript_lines`/`events`.

## What is already done well

- The Deepgram and service-role keys stay server-side in the relay. The browser gets only audio and text (`server.js:2`, `:27-29`, `:177`).
- The transcript UI uses `textContent` for untrusted text (`public/index.html:76-77`), so there is no XSS there.
- The `security definer` trigger function has a fixed `search_path`, can only run as a trigger (not callable over RPC), reads the URL and secret from Vault, and is a no-op when they are absent.
- The n8n exports contain no `pinData` and no embedded credentials. The Supabase project URL in them is not a secret.
- The crawler (workflow 02) uses domain allow- and deny-lists and caps the scraped text size before it goes to Claude.
- No secrets anywhere in git history.
