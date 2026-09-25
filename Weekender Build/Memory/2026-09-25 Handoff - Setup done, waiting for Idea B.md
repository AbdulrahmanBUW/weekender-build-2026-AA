---
type: memory
date: 2026-09-25 22:15
by: abdul + claude
---
# Handoff: Setup done, waiting for Idea B

## Done
- Collaboration: private GitHub repo + Project board #2 (milestones = pod slots), Obsidian vault with Git plugin, shared `CLAUDE.md`, full guide in `ONBOARDING.md`.
- Skills in repo (32): security-audit, archify, brag/brag-slim, Anti-AI-UI (3), n8n-skills (15 + router), hyperframes (6). rtk + FFmpeg installed on Abdul's PC.
- MCP (`.mcp.json`): n8n (official, working), n8n-mcp (needs `N8N_API_KEY`), lovable (OAuth).
- Supabase `weekender-build` (ycyrtlzympxzlfcocazh, Frankfurt): schema + seed pushed, RLS tested ([[RUN-004 Cloud Supabase push and RLS check]]), Vault secrets set, pg_net trigger → n8n.
- n8n "HalloTermin 01" (peFxjt572HiUxu61) published: request → Claude German brief → Supabase (`briefed`) + event. Full loop ≤10 s ([[RUN-006 Full loop DB to n8n to Claude to DB]]).
- Lovable project "HalloTermin Paper": P1 shell done (2.2 credits, 122 left), our Supabase connected (not Lovable Cloud). Knowledge NOT pasted yet.
- Research notes: voice (Retell proposed), stack guides, connectors, prompt pack ("Bilingual paper").

## In progress
- Waiting for Anastasia's Idea B → merge in [[Merged Concept]] → DEC-003.

## Next
1. Anastasia writes [[Idea B - (Teammate)]].
2. Merge → decide → adapt [[Lovable Prompt Pack]] (Knowledge + P2–P7) to the merged concept.
3. Lovable: paste Knowledge → P2 form → test with DB/n8n → P3 status page.
4. Invite Anastasia to n8n, Supabase org, Lovable project.
5. Clean E2E test rows from `call_requests` before the demo.

## Learnings / gotchas
- Claude 5 rejects `temperature` ([[DEF-002 Claude temperature deprecated]]).
- pg_net times out at 5 s → n8n must reply instantly and write back ([[DEF-003 pg_net 5s timeout vs Claude latency]]).
- IF node unary operators need `singleValue: true` ([[DEF-001 n8n IF unary operator type error]]).
- In the in-app browser, Lovable's menus need a wide pane.
