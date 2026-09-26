# voice-relay — browser call with the German AI assistant

Browser microphone ⇄ this relay ⇄ **Deepgram Voice Agent** (listen `nova-3` German · think Claude via Deepgram · speak `aura-2-viktoria-de`).
The relay keeps the Deepgram key and the Supabase service key on the server, loads the request + German brief from `call_requests`, and writes the live transcript to `transcript_lines` (text only — never audio).

## Run
```bash
cd services/voice-relay
npm install
cp .env.example .env      # fill DEEPGRAM_API_KEY yourself; SUPABASE_SERVICE_ROLE_KEY optional
npm start                 # http://127.0.0.1:8787
```
Or in the Claude desktop app: preview **voice-relay** (`.claude/launch.json`).

Open http://127.0.0.1:8787, paste a request ID (or keep the demo ID), click **Start call**, and play the receptionist in German. Use headphones.

Headless check (relay must be running): `node selftest.js [requestId]` → prints the German greeting, events and seconds of agent audio.

## What happens in a call
1. `calls` row created (`provider = deepgram-browser`), request status → `calling`, event `call_started`.
2. Agent greets with the AI disclosure first ("Guten Tag, hier spricht die KI-Assistentin von …").
3. Every utterance → `transcript_lines` (`agent` / `practice`) → Realtime → app.
4. Functions: `confirm_booking` (server rejects slots outside the approved windows), `needs_user`, `end_call` → `calls.outcome/booked_slot/bring_items/summary_en`, request status `booked` / `needs_user` / `rejected` / `failed`, events.
5. Hang-up → `ended_at`, event `call_ended`.

Without Supabase keys the relay runs in **no-DB mode** (conversation works, nothing is saved; demo patient Priya is used).

## Next
Twilio phone line (8 kHz mulaw), English subtitles (`text_en`), hosting (Docker / Render / Fly) — see vault `Concepts/Relay Hosting Options.md`.
