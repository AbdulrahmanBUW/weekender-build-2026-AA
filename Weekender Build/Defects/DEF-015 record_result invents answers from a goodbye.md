---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[RUN-014 Relay v2 generic tasks]]"
owner: claude
---
# Defect: record_result invents answers from a goodbye

## Observed
Agent asked "Kann das Medikament reserviert werden?", the pharmacy said only "Gerne, auf Wiederhören", and the agent saved `can_reserve: true` in `calls.result`.

## Expected
Only facts the other side said clearly. Unanswered questions are left out.

## Repro
`node roleplay-pharmacy.js <pharmacy task>` (run 2 in RUN-014).

## Fix
`record_result.details` description and the prompt now say: only facts that were said clearly; a goodbye or "gerne" is not a yes; never guess. Empty values are dropped server-side. Verified in run 3 (no `can_reserve`).
