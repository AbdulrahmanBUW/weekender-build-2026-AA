---
type: concept
tags: [product, service-design]
sources: ["[[Idea A - HalloTermin (Abdul)]]"]
---
# Service Blueprint — Booking a doctor as a non-German speaker

The event works with service-design logic, so this is our main "where does it break?" artifact.

| # | Phase | Customer action | Touchpoint | ⚡ Breakpoint |
|---|---|---|---|---|
| 1 | Realise need | Searches "English speaking doctor Dresden" | Google Maps, Jameda, 116117 app | Can't tell who accepts new patients / speaks English |
| 2 | Choose practice | Picks nearest | Website: "Termine nur telefonisch" | No online booking → call forced |
| 3 | Prepare | Writes script in Google Translate | — | Can't anticipate questions |
| 4 | Call | Dials in 8–10 am window | Busy tone / German phone menu | Line busy; days to get through |
| 5 | **Conversation** | "Praxis Dr. Weber, guten Tag?" | Fast German, jargon | **Moment of truth — freezes, receptionist hangs up** |
| 6 | Negotiate slot | "Dienstag 8:15?" | Instant decision needed | Can't check own calendar |
| 7 | Confirm details | Name spelling, DOB, insurance, referral | German spelling | Misspelled name; missing referral |
| 8 | After call | Unsure what was agreed | Nothing written | Missed/wrong appointment |

## Future state (HalloTermin)
Phases 3–8 move backstage: one English form → agent handles phone menu, [[AI Disclosure]], conversation, slot choice inside pre-approved windows, spelling alphabet ("S wie Siegfried"), read-back → n8n sends calendar event + English summary with what to bring.

Ausländerbehörde has the same breakpoints 4–5 but root cause is **capacity**, not language → not MVP.

**Related:** [[Moment of Truth - First 15 Seconds]] · [[Personas]] · [[Voice Pipeline - Architecture]]
