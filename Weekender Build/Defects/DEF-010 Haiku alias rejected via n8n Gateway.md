---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[RUN-013 n8n v2 workflows]]"
owner: claude
---
# Defect: Haiku alias rejected via n8n Gateway

## Observed
Workflow 05 (translate-line) with the Anthropic node model `claude-haiku-4-5` returned "Bad request - please check your parameters" for every transcript line; the error branch left the lines untouched (subtitles missing).

## Expected
Haiku translates each line in about 1 s.

## Repro
Anthropic node (Gateway credits), Message a model, model ID `claude-haiku-4-5` → 400. Same node with `claude-sonnet-5` works.

## Fix
Use the dated model ID `claude-haiku-4-5-20251001` (05 and the 04 fixer model). Verified: line translated in 1.4 s. Rule: for Haiku via n8n Gateway use the dated ID; `claude-sonnet-5` works as alias.
