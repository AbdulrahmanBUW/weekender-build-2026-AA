---
type: defect
date: 2026-09-26
status: fixed
severity: minor
found_in: "[[RUN-014 Relay v2 generic tasks]]"
owner: claude
---
# Defect: Flux rejects agent.language

## Observed
Voice Agent Settings with `listen.provider = {version: 'v2', model: 'flux-general-multi'}` plus `agent.language: 'de'` → `INVALID_SETTINGS Cannot specify agent.language when using the Deepgram V2 (Flux) listen API`.

## Fix
`server.js` (and `probe-listen.js`) omit `agent.language` when `LISTEN_MODEL` starts with `flux` and send `language_hints: ['de']` instead. Flux booking role-play passed (RUN-014).
