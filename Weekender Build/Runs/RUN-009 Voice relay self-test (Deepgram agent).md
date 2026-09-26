---
type: run
date: 2026-09-26 10:40
by: claude (abdul)
result: pass
build: services/voice-relay (Deepgram Voice Agent: nova-3 de · claude-sonnet-5 · aura-2-viktoria-de)
---
# Run: Voice relay self-test (headless)

## Goal
Prove the browser-call relay works end to end before a human test: Deepgram accepts our settings, the German greeting with AI disclosure plays, DB rows are written, and a silent call is closed properly.

## Steps
1. `node selftest.js <E2E-3 request id>` (12 s of silence) against the relay on :8787 (Supabase connected).
2. Same with 55 s to test the silence timeout.

## Result ✅
- Attempt 0: ❌ `INVALID_SETTINGS … model not available` for `claude-sonnet-4-20250514` → probed models (`probe-models.js`): **OK** claude-sonnet-5, claude-sonnet-4-5, claude-haiku-4-5, gpt-4o-mini, gpt-4.1-mini, gpt-5-mini; **not available** claude-3-5-haiku-latest, claude-sonnet-4-20250514 → default now `claude-sonnet-5` ([[DEF-008 Deepgram managed model list differs from docs]]).
- Greeting (agent, German): "Guten Tag, hier spricht die KI-Assistentin von Amina Yilmaz (E2E 3). … Termin für eine Erstuntersuchung …" → disclosure in sentence 1 ✅, 13–14 s audio.
- DB: `calls` row (provider `deepgram-browser`), request `calling`, `transcript_lines` 1 row, events `call_started`/`call_ended` ✅
- Silence 30 s → `calls.outcome = no_answer`, summary set, `ended_at` set, request `failed` ✅ ([[DEF-007 Silent call never gets an outcome]] fixed)

## Next
Human test in the browser with [[Receptionist Test Scripts]] (headphones), measure latency, then Twilio.
