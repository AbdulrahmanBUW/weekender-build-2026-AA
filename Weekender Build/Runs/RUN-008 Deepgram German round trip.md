---
type: run
date: 2026-09-26 10:07
by: claude (abdul)
result: pass
build: n8n qtvcNReBCqLLO1nW (Voice 03 – Deepgram German round-trip test)
---
# Run: Deepgram German round trip (TTS → STT)

## Goal
Prove the Deepgram key, a German voice and German transcription work before building the call agent ([[DEC-001 Voice platform (proposed)]]).

## Steps
Opening line (with AI disclosure) → Deepgram TTS `aura-2-viktoria-de` (mp3) → Deepgram STT `nova-3`, `language=de` → compare. Credential = n8n Header Auth "Header Auth account 2" (`Authorization: Token …`).

## Result ✅ (7.5 s total)
- Transcript identical except **"Priya" → "Kria"**; "KI-Assistentin" → "KI Assistentin" (hyphen only).
- Confidence **0.998**, 13.1 s audio, disclosure audible.

## Learnings
- Foreign names are the weak spot → use Nova-3 **keyterm prompting** (`&keyterm=Priya&keyterm=Sharma`) from the request, and have the agent **spell names with the German spelling alphabet** ("P wie Paula") → add to the call brief rules.
- TTS latency fine for a phone call; test streaming + 8 kHz mulaw (Twilio) next.

## Defects found
- none
