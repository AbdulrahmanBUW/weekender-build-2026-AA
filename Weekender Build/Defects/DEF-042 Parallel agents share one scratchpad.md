---
type: defect
date: 2026-09-26
status: open
severity: major
found_in: "[[RUN-021 Library guides for families]]"
owner: abdul
---
# Defect: Parallel agents share one scratchpad

## Observed
During the parallel build, several agents use the **same** scratchpad directory. The guides agent wrote `q1.sql` (a `SELECT` on `information_schema.columns`) and ran it with `npx supabase db query --linked -f <scratchpad>/q1.sql`. The query that actually ran was another agent's file with the same name (`select category, audience, source, count(*) from public.resources …`). It was a harmless read, but the same race with a write statement would run another agent's SQL against the **production** database.

## Expected
Each agent runs only the SQL it wrote.

## Repro
Two agents in the same workflow run write `<scratchpad>/q1.sql` a few seconds apart, then each runs `db query --linked -f <scratchpad>/q1.sql`.

## Fix
- Short term: every agent uses its own subfolder (e.g. `<scratchpad>/<task-name>/`) and unique file names; `cat` the file right before running it. The guides agent switched to `<scratchpad>/guides_run021/`.
- Orchestrator: give each parallel agent a separate scratchpad path in its task text.
