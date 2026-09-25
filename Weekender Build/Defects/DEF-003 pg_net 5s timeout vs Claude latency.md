---
type: defect
date: 2026-09-25
status: fixed
severity: major
found_in: "[[RUN-005 First end-to-end DB to n8n to Claude]]"
owner: claude
---
# Defect: pg_net 5 s timeout vs Claude latency

## Observed
n8n finished (brief generated, ~6 s) but the DB trigger's HTTP call timed out after 5 s, so the result never reached the database.

## Expected
Result lands in `call_requests` regardless of how long the AI takes.

## Fix
Async: webhook responds on receipt (`responseMode: onReceived`); n8n writes results back with the Supabase node (service key credential). Draft saved; waiting for credential "Supabase weekender-build" → then publish + re-run.
Applies to every AI step: **never make the DB wait for an LLM.**
