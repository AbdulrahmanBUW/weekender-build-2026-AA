---
type: concept
tags: [plan]
sources: ["[[Idea A - HalloTermin (Abdul)]]", "[[Weekender Build - Event Format]]"]
---
# Build Plan — 48h, mapped onto the event schedule

Provisional (HalloTermin as worked example). Re-cut after [[Merged Concept]] is decided. Board: https://github.com/users/AbdulrahmanBUW/projects/2

| When | Event slot | Our goal | Done when |
|---|---|---|---|
| **Fri 19–20:00** | before Pod #01 | Merge ideas, pick voice platform ([[DEC-001 Voice platform (proposed)]]) & backend ([[DEC-002 Backend and integration pattern (proposed)]]) | Both decisions `accepted` |
| **Fri 20:00** | Pod #01 Kick-off | 5-min pitch: what / who / hypothesis | Pod can repeat our idea back |
| **Fri 21–23:00** | commit | **De-risk:** one German voice call to a teammate's phone, end to end | Run note `pass` in `Runs/` |
| **Sat 09–12:30** | Build 1 | Lovable: form + status page on Supabase; n8n: request → brief → trigger call | Form insert shows up in DB + events |
| **Sat 10:00** | — | Interview 3–5 international attendees | Quotes in [[Personas]] |
| **Sat 13:00** | Pod #02 Build-Check | Show form → n8n → (mock) call | I like / I wish / What if captured in `Memory/` |
| **Sat 13–17:00** | — | Live transcript (Realtime), outcome webhook → n8n → email + calendar | Full happy path once |
| **Sat 17–19:30** | Build 2 | 10+ test calls with curveballs (fast speech, no new patients, referral question, phone menu, out-of-window slot) | Runs + Defects logged |
| **Sat 19:30** | Pod #03 Deploy/Scope-Check | Deployed URL works on a phone; cut scope | Scope list updated |
| **Sun 09–10:00** | brunch | Fix top defects, archify diagram, security audit | `docs/diagrams`, `docs/security` filled |
| **Sun 10:00** | Pod #04 Demo rehearsal | 3-min demo run | Timings measured |
| **Sun ~12:00** | — | **Code freeze**, record backup video, brag launch video | Video in `docs/launch/` (not in git if big) |
| **Sun 13:00** | Demo session | Live demo | 🎉 |
| **Sun 14:00** | — | Everything live, [[Monday-Morning Plan]] written | URL works |

## Demo script (3 min)
1. Fill the English form on stage (20 s).
2. Teammate's phone rings — they play "Praxis Dr. Weber" in German, one curveball.
3. Audience hears disclosure + negotiation on speaker; screen shows DE transcript + EN subtitles.
4. Read-back → booked → presenter's phone buzzes with email + calendar invite.
5. Backup: recorded video if Wi-Fi/telephony fails.

## Split (2 people)
- **Abdul:** voice pipeline + n8n flows + DB.
- **Teammate:** Lovable UI + interviews + pitch + receptionist role-play. (Adjust after merge.)
