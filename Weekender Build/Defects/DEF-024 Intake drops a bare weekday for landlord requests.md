---
type: defect
date: 2026-09-26
status: open
severity: minor
found_in: "[[RUN-015 Family task types in n8n]]"
owner:
---
# Defect: Intake drops a bare weekday for landlord requests

## Observed
English landlord text "... I am home Thursday afternoon." → 6 of 6 runs on Claude Haiku 4.5 returned `time_windows: []` and no question in `missing`; only `essentials_missing: ["time_windows"]`, `ready: false`. [[RUN-013 n8n v2 workflows]] (Sonnet) got two windows for a similar text. With an explicit date ("Thursday 1 October 13:00–17:00") or "any morning next week" (doctor) the windows are resolved correctly.

## Expected
"Thursday afternoon" → next Thursday 13:00–17:00.

## Repro
POST `{"text": "Hi, my heater is broken. Please call my landlord Hausverwaltung Test GmbH at 0351 0000002. I am Tom Test, flat 3, Teststrasse 1. I am home Thursday afternoon.", "ui_lang": "en"}` to `/webhook/task-intake` with `Origin: http://localhost:8787`.

## Fix
Open. Safety net works (the UI sees `essentials_missing` and `ready: false`, so it asks for the time). Options: a few-shot example for a bare weekday in the 04 system prompt, or resolve weekday words deterministically in *Validate + Clean Draft*. Course requests ("dienstags oder donnerstags nach 16 Uhr") are not affected.
