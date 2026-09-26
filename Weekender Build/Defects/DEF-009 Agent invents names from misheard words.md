---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[RUN-012 Automated receptionist role-play]]"
owner: claude
---
# Defect: Agent invents names from misheard words

## Observed
STT turned "geht das?" into "Peters"; the agent read back "bei Frau/Herr Peters" and saved `doctor: "Peters"`.

## Fix
Prompt rules 9–10 in `services/voice-relay/server.js`: name a doctor only if clearly and fully said, never invent names/dates/times, ask back when unsure; `confirm_booking.doctor` description = "only if clearly said". Verified in run 2.
