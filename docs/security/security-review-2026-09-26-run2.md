# Security review (run 2): full audit, 2026-09-26

**Skill:** `security-audit` (cloudflare/security-audit-skill). Full-audit method, single reviewer with delegated probing; report format per the skill (scope, method, findings with severity/likelihood/evidence/fix, verification of previous fixes, residual risks, launch checklist).
**Reviewed by:** Security auditor (Claude Code, Opus).
**Source ref:** `main` @ `0409a52` (worktree clean except `Weekender Build/.obsidian/graph.json`). Previous review: `docs/security/security-review-2026-09-26.md` (base commit `f476275`). All 6 code/DB/workflow commits since that file were audited.
**Scope:** `services/voice-relay/` (server.js, task-templates.js, Dockerfile, public page, test scripts), `supabase/migrations/*.sql` **plus the live linked project** (read-only SQL), `n8n/workflows/*.json` (01, 02, 04, 05, 06), `scripts/import_content.py` + `scripts/export_review.py`, `docs/content-kit/review/*.csv`, `docs/deploy-relay.md`, `.mcp.json`, `.gitignore`, both repos' full git history, and the **Lovable frontend** (`../hallotermin-paper`, TanStack Start SSR, read-only — added mid-audit by the coordinator; see section G).
**Method:** Static source review; **read-only** SQL against the live project (`npx supabase db query --linked`, incl. `set role anon` to measure what the browser sees); harmless WebSocket handshake probes against the **local** relay at `127.0.0.1:8787` only. No writes to the DB, no calls to production n8n webhooks, no load tests, no changes to code/config/workflows, Lovable not opened. Secrets never printed; a credential-materialisation guard blocked reading the frontend `.env` (noted in G).
**Coverage:** Backend, relay, workflows, scripts and DB covered. Frontend covered as committed source only (no `node_modules`, not built, not run). Live n8n webhook auth and the built Lovable bundle are `needs_validation` (owner checks below). Partial by design where noted.

## Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 1 |
| Medium | 4 |
| Low | 2 |
| Needs validation (no severity) | 5 |
| Privacy action for the user | 1 |

**Secrets:** none leaked. A Python regex scan (JWTs, `sb_secret_`/`sb_publishable_`, `sk-ant-`, OpenAI, GitHub, AWS, PEM, bearer/Deepgram tokens, and named assignments for `DEEPGRAM_API_KEY`/`SUPABASE_SERVICE_ROLE_KEY`/`N8N_*`/`ANTHROPIC_*`/`X-Webhook-Secret`) over both repos' full history (~350k lines) and both working trees found **0** hits (the only match is the empty `.env.example` keys). `.env` and `services/voice-relay/.env` are gitignored and untracked (`git check-ignore` confirms). n8n exports contain no `pinData` and no embedded credentials. Vault holds the four expected secret **names** only (`n8n_new_request_url`, `n8n_translate_line_url`, `n8n_call_result_url`, `n8n_webhook_secret`) — values not read.

**Note on the repo being public:** `AbdulrahmanBUW/weekender-build-2026-AA` is **public** (`gh repo view` → `PUBLIC`). No secrets are in it, but it publishes the exact n8n instance and webhook paths and the review CSVs — this raises the exploitability of M3 and P1 below.

---

## Verification of the previous audit's remediations

| Prev. finding | Status now | Evidence |
|---|---|---|
| **F1** relay accepts any website origin | **Fixed, verified** | `server.js:332-347` moved to a manual `server.on('upgrade')` with `originAllowed()` (`:309-316`), UUID check on `/call` (`:339`), `MAX_CONCURRENT_CALLS` gate (`:336`). Local probes: foreign origin → **403**, bad UUID → **400**, unsupported `/listen` lang → **400**. *(Residual: suffix allowlist + no-Origin bypass — see M1/M2.)* |
| **F2** anon insert can set `status`/`call_brief_de` (prompt injection) | **Fixed, verified live** | Live `pg_policies`: insert `with check (consent_ai_call AND status='submitted' AND call_brief_de IS NULL AND goal_de IS NULL)`. Migration `20260926120000` + `20260926180100`. *(Residual cost/rate-limit half — see M4.)* |
| **F3** malformed model time crashes relay | **Fixed, verified** | `berlinIso()` returns `null` on bad date/time (`:50-60`), `handleFunction` returns `{ok:false}` (`:447`), `dg.on('message')` body in `try/catch` (`:527`,`:576`), and each `handleFunction` call wrapped (`:550`). |
| **F4** unpinned `npx -y n8n-mcp` runs with the n8n API key | **Still open** | `.mcp.json:13` still `["-y","n8n-mcp"]` (unpinned). Low; see residual risks. |
| **F5** patient names in stdout logs | **Fixed** | `server.js:370` logs `req.id` + `task_type` only; patient name goes only to the operator's own practice page (`:372`), not to logs. |
| **F6** pg_net keeps the webhook secret in its queue/response tables | **Unchanged; still contained** | `net` schema is **not** exposed via PostgREST (default `public, graphql_public, storage`). Live: `net.http_request_queue` = 0 rows, `net._http_response` = 550 rows, all `200 "Workflow was started"` (no secret in bodies). See NV4 — keep `net` unexposed. |
| Accepted: anon can read **all** requests/calls/transcripts/events | **Still true, now higher exposure** | Live `set role anon`: sees all `call_requests` incl. `user_email`/`patient_dob`, all `calls`, `transcript_lines`, `events`. Now the anon key is embedded in a public frontend → see H1. |

Positives confirmed live: every `SECURITY DEFINER` function has a fixed `search_path` (`mark_resource_checked` `=public`; `notify_n8n`/`notify_n8n_new_request` `=public,extensions`; `on_call_outcome`/`on_transcript_line` `=public`). `notify_n8n(text,jsonb)` is **revoked** from `public/anon/authenticated` (live: `anon EXECUTE = false`); the other definer functions are trigger-only (not RPC-callable). `suggestions` is insert-only for anon (no SELECT — verified live), `resources`/`guides`/`family_events` read-only with writes revoked. `mark_resource_checked` correctly skips test providers (`test/verify/mock`) and test patient names (`%(E2E%`, `%roleplay%`, `%test%`) and only updates the row joined by `resource_id`.

---

## Findings

### H1 — HIGH. Demo RLS lets an anonymous browser read every request's personal data, transcripts and events

- **Where:** `supabase/migrations/20260925190000_init_schema.sql:109-112` (`demo read *` policies `using (true)` for `anon`), publication `20260925190000:115-116`. Live-confirmed.
- **Boundary crossed:** The anon (publishable) key is public — it ships in the Lovable frontend bundle and the project is a public demo. Every visitor can read **all** rows of `call_requests` (incl. `user_email`, `patient_dob`, `patient_name`, `practice_phone`, `allowed_facts`), `calls` (`result`, `summary_*`), `transcript_lines` (full call transcript) and `events`, and subscribe to them via Realtime. IDs are readable, so rows are enumerable.
- **Evidence:** `set role anon; select count(*)…` returned all rows visible (2 requests incl. 1 email + 1 DOB, 2 calls, 11 transcript lines, 15 events). Policies `demo read requests/calls/transcript/events` all `using (true)`.
- **Impact:** Full disclosure of any user's contact data and the content of their calls to anyone. This defeats the confidentiality the product needs the moment a real family submits a request during the public demo. **Today the seeded data is fictional**, and the team has consciously accepted this for the fake-data demo — that is why severity in practice is bounded — but the control that would protect real users does not exist yet.
- **Likelihood / impact:** likelihood high (trivial, one anon query), impact high if any real PII is entered; overall **high**, mitigated to informational *only while data is fictional*.
- **Smallest fix (before real users):** introduce Supabase Auth and owner scoping. Add `user_id uuid not null default auth.uid()` to `call_requests`; replace the four `demo read *` policies with `using (user_id = auth.uid())` on `call_requests` and `exists (select 1 from call_requests r where r.id = <child>.request_id and r.user_id = auth.uid())` on `calls`/`transcript_lines`; drop `events` from anon read and from the Realtime publication (or scope it the same way). For Sunday: keep data fictional and say so on stage.

### M1 — MEDIUM. Relay's default origin-suffix allowlist admits *any* Lovable site (Deepgram/Anthropic spend + service-role writes) when hosted publicly

- **Where:** `services/voice-relay/server.js:306-316` — `ALLOWED_ORIGIN_SUFFIXES` defaults to `.lovable.app,.lovableproject.com`; `originAllowed()` accepts any `https://<host>` whose host ends in one of those.
- **Boundary crossed:** Anyone can create a free `*.lovable.app` page. Its Origin passes the check, so it can open `ws(s)://<relay>/call?request=<uuid>` and `/listen?lang=…`. On a **publicly hosted** relay this lets a third party (a) start Deepgram Voice Agent + STT and the Anthropic "think" model on the operator's quota (capped only by `MAX_CONCURRENT_CALLS`, default 3), and (b) for any known/enumerable request UUID (anon can read them, H1) or the demo id, flip `call_requests.status` and insert `calls`/`events`/`transcript_lines` rows via the **service role** (`:364-369`, `:543`).
- **Evidence:** Local probe with `Origin: https://security-audit-probe.lovable.app` passed the 403 gate (returned 400 "bad request id" / "language not supported", i.e. it reached the per-path checks), while `https://evil.example` → 403. `docs/deploy-relay.md:71` documents that this suffix "lets **any** Lovable app use our Deepgram quota."
- **Likelihood / impact:** requires the relay to be public (unknown for Sunday — NV5) and a known relay URL; impact = attacker-driven paid API spend + state tampering. Overall **medium**.
- **Smallest fix:** once the published app origin is known, set `ALLOWED_ORIGINS=<app origin>,<relay origin>` and **`ALLOWED_ORIGIN_SUFFIXES=`** (empty) in the relay's env (deploy-relay.md §2 already prescribes this — make it a hard pre-demo step). Keep `MAX_CONCURRENT_CALLS=2` and set a Deepgram balance/spend cap.

### M2 — MEDIUM. Relay has no authentication and the Origin check is skipped when the Origin header is absent

- **Where:** `services/voice-relay/server.js:335` — `if (origin && !originAllowed(origin)) return reject(...)`. A request with **no** `Origin` header (curl, any non-browser client) skips the allowlist entirely and proceeds to `/call` or `/listen`.
- **Boundary crossed:** Origin is a browser-enforced control only. A scripted client that omits Origin can, against a public relay, spend Deepgram/Anthropic credits and (for a known request UUID or the demo id) drive service-role writes, bounded only by `MAX_CONCURRENT_CALLS` (3) and, for `/listen`, `MAX_LISTEN_SECONDS` (120).
- **Evidence:** Local probe `/call?request=not-a-uuid` **with no Origin** → 400 "bad request id" (it passed the origin gate to the UUID check); `/listen?lang=xx` no Origin → 400. `docs/deploy-relay.md:75-78` acknowledges this and proposes a `REQUIRE_ORIGIN=1` flag — **but that flag is not implemented** in `server.js` (no reference to `REQUIRE_ORIGIN` anywhere), so the documented mitigation does not exist.
- **Likelihood / impact:** requires a public relay + known URL (the repo/plan publish `wss://voice-relay-*.onrender.com` patterns); no credential needed. Overall **medium**.
- **Smallest fix (choose per exposure):** for the weekend, keep the relay off the public internet or unlisted, `MAX_CONCURRENT_CALLS` low, Deepgram spend-capped, and **delete/scale-to-zero after Sunday** (deploy-relay.md:77). Real fix: require a short-lived signed token (minted by a Supabase Edge Function) on `/call` and `/listen`, and reject a missing Origin. If you want the quick stopgap now, actually implement the `REQUIRE_ORIGIN` check the docs describe (reject when `!origin`).

### M3 — MEDIUM. The n8n `task-intake` webhook (workflow 04) is unauthenticated; its only guard is a spoofable Origin allowlist, and the URL is public

- **Where:** `n8n/workflows/04-task-intake.json` → webhook node `authentication: none`, `options.allowedOrigins: "*"`; guard is the `Check Origin + Size` code node matching `headers.origin` against `localhost:8787`, `127.0.0.1:8787`, `*.lovable.app`, `*.lovableproject.com`. Production URL `https://arahmandeaxo.app.n8n.cloud/webhook/task-intake` is documented in the public repo (`Frontend and UX Plan v3 (merged).md:381`).
- **Boundary crossed:** The `Origin` header is trivially set by any non-browser client (`curl -H "Origin: https://x.lovable.app"`), so the allowlist is not an authentication control against scripted abuse. Each accepted request runs Claude Haiku 4.5 (the draft chain, plus the auto-fix model on parse failure) — paid credits — up to `round ≤ 5`, `text ≤ 600` chars.
- **Evidence:** Static (per instruction, the production webhook was **not** probed). The node has no shared-secret; workflows 01/05/06 by contrast use `authentication: headerAuth` (`X-Webhook-Secret`). No DB writes and executions aren't saved, so the impact is cost, not data.
- **Likelihood / impact:** URL is public and the guard is spoofable → **medium** (operator LLM-credit drain / n8n execution quota). No SSRF or data write (the model output is validated and only returned to the caller).
- **Smallest fix:** add a lightweight anti-abuse control the browser can satisfy — a Cloudflare Turnstile/hCaptcha token verified in the workflow, or a rotating shared token minted server-side — and/or an n8n-side rate limit per IP. For the weekend at minimum: set a hard Anthropic/Gateway spend cap and keep the intake path unadvertised. Treat the Origin allowlist as CORS hygiene, not auth.

### M4 — MEDIUM. Anonymous `call_requests` insert fans out into paid n8n + Claude with no rate limit

- **Where:** insert policy (live) allows `anon` INSERT; trigger `20260925200000_notify_n8n_on_request.sql:41-43` → `pg_net` → n8n 01 → Claude brief. No CAPTCHA/rate limit on the insert path.
- **Boundary crossed:** Anyone with the (public) anon key can insert valid `call_requests` rows (consent+`submitted`+null briefs pass the check) and each one triggers an outbound webhook and a Claude Haiku call.
- **Evidence:** Live `has_table_privilege('anon','call_requests','INSERT')=true` + active trigger `call_requests_notify_n8n`; live `net._http_response` shows 550 delivered `Workflow was started` posts. The column-tampering half of the old F2 is fixed; the cost/rate-limit half is not.
- **Likelihood / impact:** trivial to script; impact = operator n8n execution + Claude spend and junk rows. **Medium.**
- **Smallest fix:** for real users, move inserts behind a Supabase Edge Function that rate-limits per IP and requires a CAPTCHA/Turnstile token; or a Postgres per-IP throttle. For Sunday: Anthropic/Gateway spend cap + don't publicise the project URL.

### L1 — LOW. CSV formula/DDE injection in `scripts/export_review.py`

- **Where:** `scripts/export_review.py:95-121` — `s()` writes DB values into review CSVs verbatim; cells beginning with `= + - @` (or tab/CR) are executed as formulas when a reviewer opens the file in Excel/Google Sheets/LibreOffice.
- **Boundary crossed:** `resources`/`family_events` text (some scraped or model-written via the service role) → CSV → the reviewer's spreadsheet application. A crafted provider name/description could run a formula (data exfiltration via `=HYPERLINK`/`WEBSERVICE`, or DDE) on the reviewer's machine.
- **Evidence:** No neutralisation in `export_review.py`; current review CSVs contain 0 formula-like cells (scanned), so nothing malicious is present today — this is a latent defect.
- **Fix:** prefix a leading `'` (or space) when a cell starts with `= + - @ \t \r`, e.g. in `s()`: `return "'"+v if v and v[0] in "=+-@\t\r" else v`. Applies to both provider and event lines.

### L2 — LOW. `allowed_facts` is not locked on anon insert → bounded prompt-injection into the relay agent's FAKTEN

- **Where:** insert check locks `status`/`call_brief_de`/`goal_de` but **not** `allowed_facts`; `services/voice-relay/server.js:76-81` (`factsOf`) feeds them into the agent prompt's `FAKTEN` block (`buildAgent` `:123-124`, `:191-192`).
- **Boundary crossed:** An attacker inserting their own `call_requests` row can place arbitrary text in `allowed_facts` values that appears in the agent's system prompt.
- **Evidence:** Values are clipped by `clip()` to 80 chars each, control chars/newlines stripped, max 15 facts, and fenced as `- <label>: <value>`; the agent rules say "Verwende NUR die FAKTEN" / "Erfinde niemals…". So influence is bounded and the request is self-initiated (attacker's own row, attacker's own `practice_phone`). No real outbound telephony exists yet (the "call" is a browser-mic roleplay to Deepgram), so there is no arbitrary-number dialing today.
- **Fix (defence in depth / before real telephony):** also constrain `allowed_facts` shape on insert (already length-capped by check constraints), and treat all of `patient_name`/`practice_name`/`allowed_facts` strictly as fenced data in the prompt (already largely done). When real telephony is added, verify `practice_phone` against a known-good number for the target `resource_id` so the service cannot be used to call arbitrary numbers.

---

## Privacy action for the user

### P1 — Real provider contact data (personal mobiles, emails, staff names) in review CSVs committed to a PUBLIC repo

- **Where:** `docs/content-kit/review/providers-review.csv` — 13 rows with German mobile numbers (`+49 15x/16x/17x`), 4 organisation email addresses (`mosaik@auslaenderrat.de`, `vorstand@dsvb.de`, `montagscafe@staatsschauspiel-dresden.de`, `stm@frauenfoerderwerk.de`), and several "run by <name>" / "languages are those of the named staff" notes referencing individuals. The repo is public.
- **Why it matters:** The task specified "only public organisation info." Organisation switchboard numbers/emails are defensible, but personal **mobile** numbers of individuals running small Vereine, aggregated into a public repo, are personal data under GDPR and go beyond their original publication context. The same data is also world-readable in the live `resources` table via the public anon key (that is intended for the directory, but compounds the exposure).
- **What the user should do:** review the 13 mobile rows and 4 emails; keep only genuine business/organisation contacts, and remove or replace personal mobiles/named-individual data (and drop them from `resources` if they are personal). Consider making the code repo private, or at least excluding `docs/content-kit/review/` from it. This needs a human judgement call per row — flagged for you, not auto-fixable.

---

## Needs validation (facts outside source / owner-observed; do not probe production)

- **NV1 — Frontend service-role key exposure (coordinator's question).** `src/integrations/supabase/client.server.ts:32-56` builds an **admin** client (bypasses RLS) from `process.env.SUPABASE_SERVICE_ROLE_KEY`. **Today it is safe:** no route/loader/server-function imports `supabaseAdmin` (grep: the only reference is the file itself), and because it reads `process.env` (not `import.meta.env.VITE_*`), Vite does not inline the value into the client bundle — a mistaken client import would get `undefined`, not the key. **The real risks to confirm:** (a) whether Lovable's hosting/"Lovable Cloud" injects `SUPABASE_SERVICE_ROLE_KEY` into the server env — `AGENTS.md:12` says never enable Lovable Cloud, and the plan says browser uses the anon key only, so the service key should **not** be set for this frontend at all; (b) that no future SSR route/server-fn starts importing `supabaseAdmin` and returns data without auth. **Owner check:** in the frontend's hosting env, confirm `SUPABASE_SERVICE_ROLE_KEY` is unset; keep Lovable Cloud disabled; after each build, grep the client bundle for `sb_secret_`, a service-role JWT (`"role":"service_role"`), and `SUPABASE_SERVICE_ROLE_KEY` (expect none).
- **NV2 — Frontend rendering of DB text.** The routes are currently static shells (no data fetch, no `dangerouslySetInnerHTML`), so nothing is exploitable yet. The build plan says `content_md` is rendered with react-markdown and "no raw HTML" (`Frontend and UX Plan v3 (merged).md:684`). **When built, verify:** react-markdown is used **without** `rehype-raw`/`allowDangerousHtml`; `guides.summary_en`/`i18n` and `resources.description_en`/`notes_en` are never injected as HTML; `resources.website`/`source_url` and `guides.sources[].url` are constrained to `http(s):` before use as `href` (block `javascript:`), with `rel="noopener noreferrer"` on external links.
- **NV3 — n8n webhook auth (workflows 01/05/06).** Exports show `authentication: headerAuth` but credentials are stripped on export. **Owner check (in the n8n UI, not by probing prod):** the Header Auth credential uses header name `X-Webhook-Secret` with the same value as Vault `n8n_webhook_secret`; the DB trigger sends `coalesce(v_secret,'')`, so a missing Vault secret makes it fail closed. Confirm each of 01/05/06 is bound to that credential.
- **NV4 — Do not expose the `net` (or `vault`) schema via PostgREST.** The `anon` role holds `USAGE` on schema `net` and `SELECT`/`EXECUTE` on `net._http_response` (550 rows) and `net.http_request_queue` — these are unreachable **only** because PostgREST's exposed-schema list is the default (`public, graphql_public, storage`). If `net` is ever added to the API schemas, anon could read outbound request/response history (and, transiently, queued rows carrying the `X-Webhook-Secret` header). **Owner check:** confirm the API "Exposed schemas" stays `public, graphql_public, storage`; optionally `revoke usage on schema net from anon, authenticated` as defence in depth.
- **NV5 — Is the relay hosted publicly for the demo, and is Deepgram spend-capped?** Governs the real-world exploitability of M1/M2/M3. **Owner check:** if hosted, set the exact-origin allowlist (M1 fix), a Deepgram balance/spend cap, `MAX_CONCURRENT_CALLS=2`, Auto-Deploy off, and scale-to-zero/delete after Sunday (deploy-relay.md).

---

## Other checks that came back clean (hardening notes, not findings)

- **SSRF:** no n8n node fetches a user-supplied URL. Workflows 01/04/05/06 HTTP nodes all target the hardcoded Supabase REST base; the crawler (02) is manual-trigger and fetches URLs from Brave results + trusted-source lists with allow/deny filtering; the pg_net trigger posts to a Vault URL. No user text reaches a fetch target.
- **SQL injection in `scripts/import_content.py`:** quoting is correct for `standard_conforming_strings = on` (Supabase default). `q()` doubles `'` and strips NUL; `q_arr`/`q_num`/`q_ts` are safe; `id` is validated against `UUID_RE` before interpolation (`:398-405`); ages via `float()`; JSON via `json.dumps(...)::jsonb`; SQL comments collapse whitespace incl. newlines so labels can't break out. One statement, one transaction. *Hardening:* it relies on `standard_conforming_strings=on` (backslashes are not escaped) — fine on Supabase, but note it if ever run elsewhere.
- **Frontend hygiene:** CSRF middleware is re-enabled for server functions (`src/start.ts:23-25`); `previewAuthStorage.ts` brokers the auth session to the Lovable editor over `postMessage` with strict origin/`targetOrigin` validation and a project-id taken only from non-user-controlled host positions (`:12-16`, `:46-55`) — carefully scoped, preview-only. `lovable-error-reporting.ts` sends `error.message`/`stack`/`location.pathname` to `window.__lovableEvents`/`__lovableReportRuntimeError` (present only in the editor preview) — keep secrets/PII out of thrown errors. `supabase/config.toml` holds only `project_id`.
- **Container:** `Dockerfile` runs as non-root `node`, bakes no secrets (`.dockerignore` excludes `.env`, `.env.*`, and all test/probe scripts), and `HOST` defaults to `127.0.0.1` locally / `0.0.0.0` in the image.

---

## Rules the upcoming Lovable prompts must follow (frontend)

1. **No service key in the frontend, ever.** Do not set `SUPABASE_SERVICE_ROLE_KEY` in the Lovable/hosting env; do not enable Lovable Cloud or Lovable's managed Supabase (it can inject the service key). Leave `src/integrations/supabase/client.server.ts` **unused** — no route, loader, or server function may `import` `supabaseAdmin`. The browser uses only the publishable/anon key via `@/integrations/supabase/client`.
2. **Render all DB text safely.** `guides.content_md` via react-markdown with raw HTML **disabled** (no `rehype-raw`, no `dangerouslySetInnerHTML`). Escape `summary_en`/`i18n`/`notes`/`description_en` as text. Allow only `http(s):` in `resources.website`/`source_url`/`guides.sources[].url` used as `href`; keep `rel="noopener noreferrer"`.
3. **Keep the anon surface minimal (matches the plan's HARD RULES).** Browser only reads `resources`/`family_events`/`guides`, inserts `suggestions` (no `.select()`), POSTs to the intake, inserts one `call_requests` row (never `status`/`goal_de`/`call_brief_de`), reads/Realtime on `call_requests`/`calls`/`transcript_lines`/`events`. Never store the parent's free text beyond React state; never put personal data in URLs.
4. **Do not add features that write more PII** to `call_requests`/`events` while the demo RLS is world-readable (H1).
5. **Before publishing:** run Lovable's built-in security scan; grep the built client bundle for `sb_secret_`, a `service_role` JWT, and `SUPABASE_SERVICE_ROLE_KEY` (expect none); set CSP/security headers where the host allows.

---

## Coverage summary

- **Covered:** relay (server.js, task-templates.js, public page, Dockerfile, test scripts), all 5 migrations since base + live DB state (RLS, grants, policies, definer functions, triggers, pg_net/vault, anon-visible rows), workflows 01/02/04/05/06 (webhook auth, prompt-injection surfaces, SSRF, secrets), `import_content.py` + `export_review.py`, review CSVs, `.mcp.json`/`.gitignore`, both repos' full history, and the frontend as committed source.
- **Candidate/needs-validation:** NV1–NV5 (env facts, live webhook auth, built bundle, PostgREST schema exposure, public hosting) — owner-observed checks provided; no production probing performed.
- **Deferred / out of scope:** the built Lovable bundle and `node_modules` (not present); live n8n webhook responses (must not spend credits); the crawler's live behaviour; load/availability testing (excluded by policy).
- No prior coverage ledger existed; this run does not claim exhaustive coverage.

---

## Launch checklist (before Sunday 14:00)

**Must do (highest value first):**
1. **M1 fix:** set the relay's `ALLOWED_ORIGINS` to the exact app + relay origins and **`ALLOWED_ORIGIN_SUFFIXES=`** (empty). `services/voice-relay/server.js:306` / deploy-relay.md §2. Set a **Deepgram spend cap** and `MAX_CONCURRENT_CALLS=2`.
2. **M3/M4 cost caps:** set an Anthropic/Gateway spend cap; keep the project + intake URL unadvertised. (Real fix later: Turnstile + rate limit on the intake and on `call_requests` inserts.)
3. **NV5:** if the relay is public, Auto-Deploy off during the demo, and **scale-to-zero/delete after Sunday**.
4. **H1:** keep all demo data fictional and say so on stage; owner-scoped RLS is a Monday item (exact policies above).
5. **NV1:** confirm `SUPABASE_SERVICE_ROLE_KEY` is **not** set in the frontend host and Lovable Cloud is off; grep the built bundle for it.
6. **NV3:** confirm 01/05/06 are bound to the `X-Webhook-Secret` Header Auth credential (send one no-header POST → expect 401/403, owner-side).
7. **NV4:** confirm PostgREST exposed schemas stay `public, graphql_public, storage`.

**Needs the user (cannot be auto-fixed):**
- **P1:** review/remove personal mobile numbers, emails and named-staff data in `docs/content-kit/review/providers-review.csv`; consider making the code repo private.
- **Secret rotation:** none required — no secret leaked. (If the repo is made private *after* the fact, still consider rotating the n8n API key and webhook secret only if you suspect the public window exposed them via any non-repo channel; nothing in this audit indicates exposure.)

**Nice to have (low, post-weekend):**
- **F4:** pin `n8n-mcp` to an exact version in `.mcp.json:13`.
- **L1:** neutralise leading `= + - @` in `export_review.py` CSV output.
- **L2:** verify `practice_phone` against the target `resource_id` before adding real outbound telephony.
