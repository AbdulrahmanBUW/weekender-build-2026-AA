---
type: run
date: 2026-09-26 18:47
by: claude (abdul's session)
result: pass
build: https://dresden-mit-kind.lovable.app (Lovable, TanStack Start SSR, repo AbdulrahmanBUW/hallotermin-paper); n8n 04/01/05/06; local relay :8787 (mip_opt_out)
---
# Run: Live site E2E call

## Goal
Answer Abdul's question "Does the live call actually work?" on the **published** site, not the preview: Ask for me → intake → approval → insert → brief → call → live subtitles → result in the parent's language.

## Steps
1. `https://dresden-mit-kind.lovable.app/ask?resource=<Olgas Musikstudio>&type=course_enquiry`, typed the Russian demo sentence (Maria Ivanova, son 4, Tue/Thu afternoon, Russian or German), Continue.
2. Approval card → consent → Call now → `/r/fb99c45e-660b-4882-affa-1a71505f8f02`.
3. The call was driven by `services/voice-relay/roleplay-course.js` (synthetic German receptionist via Deepgram TTS) against the local relay, i.e. exactly what the relay tab does after "Start the call". The live page was watched in a normal Chrome tab.

## Result
- **Intake (n8n 04, Haiku):** approval card in ~15 s. German opening "KI-Assistentin von Maria Ivanova", Russian "ИИ-ассистентка"; windows Tue 29.09 / Thu 01.10 / Tue 06.10 13:00–17:00; facts: child age 4, preferred days, language; no question about the child's name.
- **Brief (n8n 01):** status `briefed` within ~12 s.
- **Call (101 s):** AI said it is an AI first; answered "Wie alt ist das Kind?" with the approved fact ("Das Kind ist vier Jahre alt"); **declined the Saturday offer** (outside the windows) and asked for Tue/Thu from 13:00; asked the language and the price on its own; read back "Donnerstag, erster Oktober, vierzehn Uhr … richtig?" before agreeing.
- **Live page:** stepper, timer, "The assistant said it is an AI", the other side's lines with Russian subtitles within seconds.
- **Result:** `booked`, Thu 1 Oct 14:00 Berlin (inside the window), result card "Trial lesson booked" with price 38 €/month, free trial lesson, "Deutsch, eine Lehrerin spricht auch Russisch", bring items with Russian meanings (удобная одежда, тапочки), Russian summary (`summary_user`) after the call, calendar button.
- 28 transcript lines, 1 without subtitle (last line; known [[DEF-049 Last agent lines without subtitle]] pattern).
- The "Checked by phone" badge is now set on the demo listing (intended only for the demo listing). **Reset it before the stage demo** so the badge beat appears live: `update resources set last_checked_at = null, last_check_outcome = null where subcategory = 'demo';`

## Defects found
- STT mishears synthetic TTS words ("Die alt", "Kucke", "Ungerichtet"); the agent still understood. Real voices are clearer.
- Dictation and the call need the relay: on the presenter laptop the local relay works; other devices need the public relay host (docs/deploy-relay.md).
