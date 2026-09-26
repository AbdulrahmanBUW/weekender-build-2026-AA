---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[RUN-009 Voice relay self-test (Deepgram agent)]]"
owner: claude
---
# Defect: Deepgram managed model list differs from docs

## Observed
Docs list `claude-sonnet-4-20250514` as managed think model; the API answers `INVALID_SETTINGS … model not available`.

## Fix
`services/voice-relay/probe-models.js` checks models live. Default `THINK_MODEL=claude-sonnet-5`; fallback for lower latency: `claude-haiku-4-5`. Always probe before switching models.
