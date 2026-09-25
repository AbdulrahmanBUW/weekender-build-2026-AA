---
type: decision
date: 2026-09-25
status: proposed
deciders: [abdul, teammate]
---
# Decision: Voice platform for the HalloTermin call

## Context
- We need a German-speaking AI to phone a "Praxis" (teammate's German mobile) live on stage, with a live German/English transcript in the Lovable UI, and be live under our own URL by **Sun 14:00** ([[Deadline - live by Sunday 14h]]).
- The team is not primarily developers; the event stack is Lovable + Supabase + n8n Cloud + Claude. n8n can't hold websockets, so the DIY path (Deepgram + Twilio) needs a custom relay server plus hosting ([[Relay Hosting Options]]).
- Twilio trials can't make clean international calls (sign-up country only, verified numbers, trial announcement) and German numbers need a multi-day regulatory bundle ([[Telephony Constraints (Twilio Trial, Numbers)]]).
- The idea may merge with [[Idea B - (Teammate)]], so the voice part must sit behind a small interface (trigger + tool webhooks + transcript webhook + end-of-call webhook), see [[Voice Pipeline - Architecture]].

## Options
Full table: [[Voice Platform Comparison]].
1. **Deepgram Voice Agent + Twilio + own relay (DIY)** — best EU story, most control; 150–300 lines of code, hosting, tunnel, Twilio upgrade. Highest risk for us.
2. **Retell AI (managed)** — no relay; outbound API; Retell numbers list Germany at $0.10/min (docs conflict, must test); custom functions → n8n; **`transcript_updated` webhook gives a live transcript**; $10 free credit; Claude available as LLM. No EU hosting.
3. **ElevenLabs Agents (managed)** — best German voice; no relay; needs an upgraded Twilio number (or SIP); webhook tools → n8n; post-call webhook with structured data; **no live transcript for phone calls outside Enterprise**. EU residency Enterprise-only.
4. **Vapi (managed)** — similar to Retell, live `transcript` server messages, but free numbers can't call out and there are more knobs to set.
5. **Browser-only (WebRTC) demo** — any of 2–4 via web call; no telephony risk, weaker story.

## Decision (proposed)
**Primary: Retell AI with a Retell-managed number**, triggered from n8n (`POST /v2/create-phone-call`), tools as n8n webhooks (`check_slot`, `confirm_booking`, `needs_user`), `transcript_updated` → Supabase Edge Function → `transcript_lines` (Realtime), `call_analyzed` → n8n for the English confirmation. German language, an ElevenLabs or other German voice inside Retell, Claude as LLM, fixed disclosure greeting, recording/storage off.

**Gate (Fri night, ≤ 2 h):** a Retell dashboard test call reaches the teammate's +49 mobile and sounds acceptable in German.

**Fallback A (if Retell can't dial +49 or German sounds bad):** **ElevenLabs Agents + upgraded Twilio US number** (Germany geo permission on; or a Twilio verified caller ID), same n8n tools and post-call webhook; UI shows tool-driven status steps live + full transcript after the call.

**Fallback B (if no phone path works by Sat 12:00):** same agent via **browser web call**; teammate plays the receptionist on a laptop; plus the pre-recorded backup video.

**Not this weekend:** DIY Deepgram + Twilio relay. Keep it in the pitch as the production/EU architecture (Deepgram EU endpoint, German +49 number, DPAs).

## Consequences
- ✅ Near-zero custom code: one Edge Function (transcript dedupe + optional translation) and n8n flows. Frees 10+ hours for prompt, read-back, UI and pitch.
- ✅ Swappable: n8n only knows "start call" + 3 webhooks, so switching Retell ↔ ElevenLabs ↔ Deepgram later only changes one HTTP node and webhook parsing.
- ⚠️ Data leaves the EU (Retell US; ElevenLabs non-Enterprise). Acceptable for a demo with **fake data only**; must be addressed before real users ([[Data minimisation - no symptoms]], [[AI Disclosure]]).
- ⚠️ Vendor lock-in on prompt/voice config; export the prompt text into the repo/vault.
- ⚠️ Budget: expect €20–40 total for credits/Twilio top-up; one person owns billing.
- ⚠️ Unverified until tested: Retell → Germany dialing, Retell recording-off toggle, exact German language/voice setting names.
- Risks and mitigations: [[Voice Risks and Mitigations]].
