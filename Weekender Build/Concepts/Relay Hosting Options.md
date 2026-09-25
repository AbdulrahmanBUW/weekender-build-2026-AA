---
type: concept
tags: [voice]
sources: ["https://vercel.com/docs/functions/websockets", "https://vercel.com/changelog/websocket-support-is-now-in-public-beta", "https://supabase.com/docs/guides/functions/websockets", "https://supabase.com/docs/guides/functions/limits", "https://supabase.com/docs/guides/troubleshooting/edge-functions-worker-timeouts-and-websocket-drops", "https://render.com/changelog/free-web-services-now-remain-active-while-receiving-websocket-messages", "https://render.com/docs/free", "https://docs.railway.com/pricing/free-trial", "https://www.saaspricepulse.com/tools/flyio", "https://www.twilio.com/en-us/blog/partners/integrations/building-an-outbound-voice-agent-with-twilio-and-deepgram"]
---
# Relay Hosting Options

**Definition:** where the small websocket bridge (Twilio Media Stream ⇄ Deepgram Voice Agent) would run. **Only needed for the DIY path** — the managed platforms in [[DEC-001 Voice platform (proposed)]] need no relay.
**Why it matters for us:** a phone call keeps two websockets open for 2–5 minutes. Classic serverless kills that; the event must also be live under a public URL by Sun 14:00 ([[Deadline - live by Sunday 14h]]).
**Related:** [[Voice Pipeline - Architecture]] · [[Voice Platform Comparison]] · [[Stack Overview - Lovable n8n Supabase]]

## Requirements
- Public `wss://` URL that Twilio can reach (`<Stream url="wss://HOST/media">`).
- Holds 1 inbound websocket (Twilio) + 1 outbound websocket client (Deepgram) for ≥ 5 min.
- Stable hostname during the demo (Twilio TwiML points at it).

## Options

| Option | Holds a 5-min call? | Effort | Cost | Notes |
|---|---|---|---|---|
| **Vercel Functions (Fluid)** | **Yes, now** — websockets are in **public beta since 22 Jun 2026**; connections close at the function's max duration ([docs](https://vercel.com/docs/functions/websockets)). Default cap reported as 5 min ([Ably summary](https://ably.com/vercel/websockets-on-vercel)). | Low–medium: FastAPI or Node `ws` server exported from `api/…`. Docs page is marked "Permissions required: WebSockets (Beta)" → may need enabling on the team (unverified). | Active CPU only; team already has Vercel. | Set `maxDuration` as high as the plan allows (Pro up to 800 s — unverified for websockets). A 3-min booking call fits under 5 min, but it is beta and untested with Twilio. |
| **Docker locally + Cloudflare quick tunnel** | Yes (your laptop). | Lowest: `docker run -p 8080:8080 relay` then `cloudflared tunnel --url http://localhost:8080` → prints `https://<random>.trycloudflare.com` (no account needed). | Free | URL changes every restart → update `PUBLIC_HOSTNAME`. Laptop + venue Wi-Fi must survive the demo. Fine for Friday de-risking. |
| **Docker locally + ngrok** | Yes | Low: `ngrok http 8080` (free account gives one static domain: `ngrok http --url=<name>.ngrok-free.app 8080`). | Free tier | Static domain is nicer than cloudflared for Twilio config. Same laptop risk. |
| **Render (free web service)** | Yes while traffic flows; since 24 Feb 2026 free services stay up while receiving websocket messages; sleep after 15 min idle, **~1 min cold start** ([changelog](https://render.com/changelog/free-web-services-now-remain-active-while-receiving-websocket-messages)). | Low: connect GitHub repo, Dockerfile. | Free (750 h/month) | Warm it up with a `GET /health` 2 min before the demo (n8n can ping it). |
| **Railway** | Yes (containers) | Low | $5 one-time trial credit, 30 days ([docs](https://docs.railway.com/pricing/free-trial)) | Enough for the weekend. |
| **Fly.io** | Yes (the Deepgram outbound reference ships a Fly setup) | Low–medium | **No free tier for new accounts in 2026**; trial ~2 VM-hours/7 days (per [review](https://www.saaspricepulse.com/tools/flyio), unverified) | Needs a card; cheap pay-as-you-go. |
| **Supabase Edge Functions** | **Risky.** Websocket servers supported, but wall clock 150 s (free) / 400 s (paid) and sockets often drop at ~half the limit ([limits](https://supabase.com/docs/guides/functions/limits), [troubleshooting](https://supabase.com/docs/guides/troubleshooting/edge-functions-worker-timeouts-and-websocket-drops)). | Medium (Deno) | Included | A 3-min call can be cut off. Use Edge Functions for **webhooks** (transcript, tool calls), not for the audio relay. |
| **Cloudflare Workers + Durable Objects** | Yes (Workers can accept and open websockets) | Medium–high: rewrite the relay in JS for Workers runtime | Free tier generous | Good production choice; too much new code for this team this weekend. |

## Recommendation (only if we go DIY)
1. **Friday night:** Docker (or plain `python main.py`) locally + `cloudflared` quick tunnel → prove a German call works.
2. **Saturday:** deploy the same container to **Render** (free, Docker, stable `*.onrender.com` URL) — or to **Vercel** if the team wants everything in one place and the beta works on the first try.
3. Keep the laptop + tunnel as a hot spare during the demo.

For the recommended managed path, the only "server" code is a Supabase Edge Function for transcript webhooks (short HTTP requests — no long-lived socket) → no relay hosting needed.
