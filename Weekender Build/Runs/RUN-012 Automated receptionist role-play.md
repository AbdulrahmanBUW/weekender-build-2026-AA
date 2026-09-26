---
type: run
date: 2026-09-26 11:10
by: claude (abdul)
result: pass
build: services/voice-relay + roleplay-test.js (receptionist voice aura-2-julius-de)
---
# Run: Automated receptionist role-play (no microphone)

## Goal
End-to-end booking through the real Deepgram agent with a synthetic German receptionist: questions, out-of-window slot, in-window slot, read-back, confirmation.

## Result
| Run | Outcome | Notes |
|---|---|---|
| 1 | booked ✅ 77 s | STT heard "…geht das?" as "Peters" → agent **invented doctor "Peters"** and saved it → [[DEF-009 Agent invents names from misheard words]] |
| 2 (after fix) | booked ✅ 70 s | refused Sat 17:00 (outside window), read back "Dienstag, 06.10.2026, um 10:00 Uhr", booked only after "Ja, richtig"; no invented doctor; `booked_slot` 10:00 Berlin, `bring_items` [Versichertenkarte], English summary |

Also: Chrome mic test by Abdul — mic-level bar moves (earlier failure = in-app pane mic). Full human test still to do with [[Receptionist Test Scripts]].

## Open
- Agent still adds a line like "(Anruf beendet)" after goodbye → cosmetic.
- Latency not yet measured per turn (Deepgram sends `LatencyReport`; add to page).
