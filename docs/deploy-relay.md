# Deploy the voice relay publicly

The relay (`services/voice-relay/`) is a long-lived websocket server (browser ⇄ relay ⇄ Deepgram, one call = one socket for 2–5 min). Serverless functions cut that off, so it runs as a **container**. Background and option comparison: vault `Concepts/Relay Hosting Options.md`.

**Recommended for the weekend:** Render free (Frankfurt) as the public URL, the presenter laptop as a hot spare (see [Demo-day fallback](#demo-day-fallback-run-locally-on-the-presenter-laptop)).

---

## 0. Bind address (done 26.09)

**Applied on 26.09.** Before, `server.js` bound to `127.0.0.1` only:

```js
server.listen(PORT, '127.0.0.1', () => …);
```

Inside a container that makes the relay unreachable: port mapping, Render and Fly all connect from outside the container's loopback. Change the bind address to read `HOST`:

```js
server.listen(PORT, process.env.HOST || '127.0.0.1', () => …);
```

The local default stays `127.0.0.1`. The Dockerfile sets `HOST=0.0.0.0`.

Tested 26.09: the image builds. As-is, `curl http://127.0.0.1:8795/health` from the host fails (the relay only answers inside the container). With a runtime shim that does the same as the line above, it returns `200 ok`, and a websocket from a foreign Origin gets `403`.

---

## 1. Build and test the container locally

```bash
docker build -t voice-relay:test services/voice-relay
docker run --rm --name vr-test --env-file services/voice-relay/.env -e PORT=8787 -p 8795:8787 voice-relay:test
curl http://127.0.0.1:8795/health        # -> ok   (needs the HOST change above)
docker rm -f vr-test
```

- `.env` is **not** copied into the image (`.dockerignore`). Secrets are passed at runtime only.
- The image runs as the non-root `node` user and only contains `server.js`, `task-templates.js`, `public/` and the production dependencies. Test and probe scripts are excluded.
- Note: in the local test the relay's own page on `http://127.0.0.1:8795` gets `403` on `/call`, because the default allowlist is `…:8787`. Add `-e ALLOWED_ORIGINS=http://127.0.0.1:8795` if you want to click through it.

---

## 2. Env vars to set on the host

| Var | Value | Secret? |
|---|---|---|
| `DEEPGRAM_API_KEY` | from Deepgram console | **yes**, set it only in the host's secret store |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Project Settings → API | **yes**, same |
| `SUPABASE_URL` | `https://ycyrtlzympxzlfcocazh.supabase.co` | no |
| `PORT` | `8787` | no |
| `HOST` | `0.0.0.0` (already set in the Dockerfile) | no |
| `ALLOWED_ORIGINS` | see below | no |
| `MAX_CONCURRENT_CALLS` | `2`–`3` (caps Deepgram spend) | no |
| optional | `THINK_MODEL`, `SPEAK_MODEL` (`aura-2-elara-de`), `LISTEN_MODEL`, `SILENCE_LIMIT_MS`, `HOLD_LIMIT_MS`, `MAX_LISTEN_SECONDS` | no |

Never paste the two secret values into chat, commits, `fly.toml` or `render.yaml` (vault `Rules/No secrets in repo.md`).

### `ALLOWED_ORIGINS`: which pages may open `/call` and `/listen`

Comma-separated, **exact origins** (scheme + host, no trailing slash). Setting it **replaces** the localhost default, so list every page that must work:

```
ALLOWED_ORIGINS=https://<name>.lovable.app,https://<lovable-preview-origin>,https://<relay-host>
```

- `https://<name>.lovable.app` is the published Lovable app (the `/listen` mic button).
- `<lovable-preview-origin>` is the editor preview, only needed if you test the mic inside the Lovable editor. Get the exact value from DevTools console → `location.origin` in the preview. It looks like `https://id-preview--<id>.lovable.app` or `https://<id>.lovableproject.com`.
- `https://<relay-host>` is the relay's own "practice phone" page, e.g. `https://voice-relay-xxxx.onrender.com`. **Required** if the receptionist plays the other side on the hosted page.

`ALLOWED_ORIGIN_SUFFIXES` **is supported** (added 26.09; default `.lovable.app,.lovableproject.com`, leading dot required, so `evil-lovable.app` does not match). A suffix like `.lovable.app` lets **any** Lovable app use our Deepgram quota. Once the published app URL is known, set `ALLOWED_ORIGINS=<app origin>,<relay origin>` and `ALLOWED_ORIGIN_SUFFIXES=` (empty).

### Security note for a public relay

The Origin check only stops *other websites in a browser*. A script that sends no `Origin` header is still allowed (`if (origin && …)`). It can start calls with the demo ID or a known request UUID and spend Deepgram credit. For the weekend:
- keep `MAX_CONCURRENT_CALLS` low, set a spend limit / low balance on the Deepgram project, and don't post the relay URL publicly.
- **scale to zero or delete the service after Sunday.**
- The real fix is a short-lived signed token, e.g. minted by an Edge Function (README "Next"). Optional quick hardening for the `server.js` owner: reject missing `Origin` when `REQUIRE_ORIGIN=1` is set. Local test scripts run without that flag.

---

## 3a. Render (free, Frankfurt): recommended

1. <https://dashboard.render.com> → **New → Web Service** → connect GitHub repo `AbdulrahmanBUW/weekender-build-2026-AA`.
2. Settings:
   - **Language/Runtime:** Docker
   - **Region:** Frankfurt (EU Central)
   - **Branch:** `main`
   - **Root Directory:** `services/voice-relay`
   - **Dockerfile Path:** `./Dockerfile` · **Docker Build Context:** `.` (relative to the root directory. If the form asks for repo-relative paths, use `services/voice-relay/Dockerfile` and `services/voice-relay`.)
   - **Instance type:** Free
   - **Health Check Path:** `/health`
   - **Environment:** the vars from section 2. Mark the two keys as secret, and set `PORT=8787` explicitly (Render's default is 10000).
3. Deploy. The URL is `https://voice-relay-xxxx.onrender.com`, and the websocket URL is `wss://voice-relay-xxxx.onrender.com`. Websockets work on all Render web services, no extra setting.
4. Add `https://voice-relay-xxxx.onrender.com` to `ALLOWED_ORIGINS` (the practice phone page), then save. That triggers a redeploy.
5. Check: `curl https://voice-relay-xxxx.onrender.com/health` returns `ok`. Open the URL, paste a task ID, Start call.

**Render free tier caveats**
- Sleeps after **15 min without traffic**, and the first request after that takes **~1 min** (cold start). Incoming websocket messages keep it awake during a call (Render changelog, Feb 2026).
  → **Warm it 2–5 min before the demo** with `curl …/health`, or ping `/health` every 10 min during the event (n8n Schedule + HTTP Request, or any uptime pinger). One service 24/7 fits in the 750 free hours/month.
- Small CPU share (0.1 CPU, 512 MB). The relay only forwards audio bytes, so this should be fine. If `turn_latency` events look worse than local runs, switch to **Starter (~$7/month, always on, no sleep)**.
- **Turn off Auto-Deploy** (Settings → Build & Deploy) before the demo window. A push to `main` restarts the container and drops any live call.
- Ephemeral filesystem: fine, the relay stores nothing locally.

## 3b. Fly.io (paid, Frankfurt `fra`): alternative

No free tier for new accounts; a card is required. Pay per second.

1. Install `flyctl` and run `fly auth login`.
2. Create `services/voice-relay/fly.toml`. The app name must be globally unique. No secrets go in this file.

```toml
app = "weekender-voice-relay"
primary_region = "fra"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8787"
  HOST = "0.0.0.0"
  SUPABASE_URL = "https://ycyrtlzympxzlfcocazh.supabase.co"
  ALLOWED_ORIGINS = "https://<name>.lovable.app,https://weekender-voice-relay.fly.dev"
  MAX_CONCURRENT_CALLS = "3"

[http_service]
  internal_port = 8787
  force_https = true
  auto_stop_machines = "off"     # no cold start during the demo
  auto_start_machines = true
  min_machines_running = 1

  [[http_service.checks]]
    grace_period = "10s"
    interval = "30s"
    method = "GET"
    path = "/health"
    timeout = "5s"

[[vm]]
  size = "shared-cpu-1x"
  memory = "256mb"               # bump to 512mb if it OOMs
```

3. Create the app and set the secrets from `.env` without typing them. Run this in `services/voice-relay`:

```bash
fly apps create weekender-voice-relay
grep -E '^(DEEPGRAM_API_KEY|SUPABASE_SERVICE_ROLE_KEY)=' .env | fly secrets import
fly deploy --ha=false            # one machine, not two
```

PowerShell equivalent for the secrets line:

```powershell
Select-String -Path .env -Pattern '^(DEEPGRAM_API_KEY|SUPABASE_SERVICE_ROLE_KEY)=' | ForEach-Object { $_.Line } | fly secrets import
```

4. The URL is `https://weekender-voice-relay.fly.dev`, and the websocket URL is `wss://weekender-voice-relay.fly.dev`. Check with `curl …/health` and `fly logs`.
5. After the event, run `fly scale count 0` or `fly apps destroy weekender-voice-relay`.

**Cost:** about $2–3/month for one always-on `shared-cpu-1x`/256 MB machine, so cents for the weekend. Shared IPv4 is free. Don't allocate a dedicated IPv4 (about $2/month). These figures are approximate; check fly.io/pricing.

## Cost summary

| Host | Weekend cost | Cold start | Card |
|---|---|---|---|
| Render Free | $0 | ~1 min after 15 min idle → warm up | no |
| Render Starter | ~$7/month (prorated) | none | yes |
| Fly.io | cents (≈ $2–3/month if left running) | none with `auto_stop_machines="off"` | yes |

The real variable cost is **Deepgram usage** (Voice Agent per minute plus STT for `/listen`), not hosting. `MAX_CONCURRENT_CALLS` caps it.

---

## 4. Point the Lovable app at the relay

The relay URL is **public** (not a secret), so it can sit in the frontend bundle.

```
VITE_RELAY_URL=wss://voice-relay-xxxx.onrender.com      # no trailing slash, wss:// (not https://)
```

In the app:

```ts
const RELAY_URL = import.meta.env.VITE_RELAY_URL;            // e.g. wss://voice-relay-xxxx.onrender.com
new WebSocket(`${RELAY_URL}/listen?lang=${userLanguage}`);  // intake mic
// (only if the app itself ever opens calls:) new WebSocket(`${RELAY_URL}/call?request=${requestId}`)
```

- Plan v3 (merged) uses **`VITE_RELAY_URL`** everywhere; use that name in the Lovable project.
- If the Lovable editor offers no field for custom `VITE_*` variables in this project, hardcode it as a fallback constant: `import.meta.env.VITE_RELAY_URL || 'wss://voice-relay-xxxx.onrender.com'`. This is fine because the URL is not a secret. Whether Lovable exposes custom `VITE_*` vars is unverified.
- An `https://` page **must** use `wss://`. `ws://` to a remote host is blocked as mixed content.
- The Lovable app's origin must be in the relay's `ALLOWED_ORIGINS` (section 2). Otherwise the socket closes with `403`.
- Transcripts reach the Lovable app through **Supabase Realtime** (`transcript_lines`), not through the relay. The app only talks to the relay for `/listen`.

---

## Demo-day fallback: run locally on the presenter laptop

Use this when Render/Fly is down, slow or cold, or the venue blocks it. The relay writes to the **same Supabase**, so the Lovable app on the projector still shows the live transcript through Realtime. **No Lovable change or republish is needed.**

1. Before the demo, on the presenter laptop:
   ```bash
   cd services/voice-relay
   npm ci                    # or npm install; once, while Wi-Fi is good
   # .env has DEEPGRAM_API_KEY + SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY (with the service key, transcripts are saved)
   npm start                 # http://127.0.0.1:8787, log says "Supabase: connected"
   ```
   Or with Docker (after the HOST change): `docker run --rm --env-file .env -e HOST=0.0.0.0 -p 8787:8787 voice-relay:test`.
   Or the Claude desktop preview **voice-relay** (`.claude/launch.json`).
2. Practice phone: open `http://127.0.0.1:8787/?request=<task-id>` in **Chrome** on the laptop, **with headphones**. `127.0.0.1` counts as a secure context, so the mic works. A LAN IP like `http://192.168.x.x:8787` would block the mic. The default `ALLOWED_ORIGINS` already allows this page, so leave `ALLOWED_ORIGINS` empty in the local `.env`.
3. Lovable app: keep it on the projector as usual. It shows status and transcript from Supabase.
4. Intake mic (`/listen`): the published app points at the cloud relay. If that is down, **type the request** instead; the text path is the primary flow anyway.
5. If the receptionist sits at a **second device**, expose the laptop relay over HTTPS:
   ```bash
   cloudflared tunnel --url http://localhost:8787     # prints https://<random>.trycloudflare.com, no account needed
   ```
   Put `ALLOWED_ORIGINS=http://127.0.0.1:8787,http://localhost:8787,https://<random>.trycloudflare.com` in `.env` and restart the relay. The second device then opens the trycloudflare URL; its page builds `wss://` from its own host automatically. The URL changes every tunnel restart. `ngrok http --url=<static>.ngrok-free.app 8787` gives a stable one.
6. Don't start the same task on the cloud relay and the laptop at the same time.

**Rehearsal checklist (Sun morning):** cloud `/health` returns `ok` → one full test call on the hosted practice phone → the same call on the laptop relay → both show transcript lines in the Lovable app → Render Auto-Deploy off → warm-up ping 5 min before the slot.
