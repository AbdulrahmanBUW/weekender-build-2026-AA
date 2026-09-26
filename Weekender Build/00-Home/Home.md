# Weekender Build — Project Home

> Dresden · 25–27 Sep 2026 · **Build live under own URL by Sun 27.09 14:00**

## Status (Sat 26.09, 13:30) → full guide: `ONBOARDING.md` in the repo root
- ✅ v2 direction: **any phone task, 12 languages** → [[Frontend and UX Plan v2]] · ✅ DB v2 live · ✅ voice relay + Deepgram books in role-play · ✅ 84 Dresden places + 4 guides (AR/TR/UK) · ✅ n8n v2 (01/04/05/06) + relay v2 live · 🟡 Lovable shell only · ✅ Idea B in · 🟡 **merge proposed → [[Merged Concept]] / [[DEC-003 Merged concept]]**
- Latest handoff: [[2026-09-26 Handoff - v2 any-task multilingual, ready for Idea B]]

## Deliverables (from weekenderbuild.de)
- [ ] 1. Running build under own URL (Lovable)
- [x] 2. n8n workflow that moves data/tasks (HalloTermin 01, may change after merge)
- [x] 3. (Optional) at least one AI function — Claude writes the German call brief
- [ ] 4. Live demo (Demo Session Sun 13:00)
- [ ] 5. Monday-Morning Plan → [[Monday-Morning Plan]]

## Mandatory repos
- [ ] cloudflare/security-audit-skill → output in `docs/security/`
- [ ] tt-a1i/archify → diagrams in `docs/diagrams/`
- [ ] latent-spaces/brag → launch video in `docs/launch/`

## Pod slots
| Slot                   | When          | Bring                                   |
| ---------------------- | ------------- | --------------------------------------- |
| #01 Kick-off           | Fri 20:00     | 5-min pitch: what, for whom, hypothesis |
| #02 Build-Check        | Sat (rolling) | 7-min current build                     |
| #03 Scope/Deploy-Check | Sat 19:30     | what stays, what goes                   |
| #04 Demo-Probe         | Sun 10:00     | 3-min demo                              |

## Open decisions (decide before building!)
- [[DEC-001 Voice platform (proposed)]] — proposal: **Retell AI** (managed, no relay code); fallback ElevenLabs / browser web-call
- [[DEC-002 Backend and integration pattern (proposed)]] — proposal: **own Supabase (Frankfurt)** connected to Lovable *before first prompt*; DB insert → pg_net trigger → n8n
- ⚠ First de-risk tonight: does a trial number actually ring a German phone? → [[Telephony Constraints (Twilio Trial, Numbers)]]

## Dashboard
![[Dashboard.base]]

## Map
- Ideas: [[Idea A - HalloTermin (Abdul)]] · [[Idea B - Dies-Das-Ana-Nas]] → merged into [[Merged Concept]] ("Find it. We call for you.")
- Plan: [[Build Plan - 48h]] · [[Weekender Build - Event Format]] · [[Monday-Morning Plan]]
- Product: [[Personas]] · [[Service Blueprint - Booking a Doctor]] · [[Moment of Truth - First 15 Seconds]] · [[Glossary - German Healthcare Terms]] · [[AI Disclosure]]
- Stack: [[Stack Overview - Lovable n8n Supabase]] · [[Integration Patterns]] · [[Lovable - Practical Guide]] · [[Supabase - Practical Guide]] · [[n8n - Practical Guide]] · [[Data Model]] · [[Newcomer Resources - Crawler]] (Dresden places + guides, n8n workflow 02)
- Voice: [[Voice Pipeline - Architecture]] · [[Voice Platform Comparison]] · [[Relay Hosting Options]] · [[Telephony Constraints (Twilio Trial, Numbers)]] · [[Voice Risks and Mitigations]]
- UI: **[[Frontend and UX Plan v2]]** (any task, multilingual, Tell → Check → Call → Result) · [[Lovable Connectors - What We Use]] · [[Lovable Prompt Pack]] (v1, superseded) (visual direction "Bilingual paper", Knowledge blocks, prompts P1–P7)
- Tooling: [[Toolchain - MCP, Skills, Plugins]] · Presentation: [[Agent Space - Who Does What]] (Pixel Agents)
- Folders: `Rules/` (hard constraints) · `Concepts/` (domain + product concepts) · `Decisions/` (ADRs) · `Runs/` (test/demo runs) · `Defects/` (bugs) · `Memory/` (session handoffs, learnings)
- Create notes from `Templates/` (Obsidian core Templates plugin, folder = `Templates`).
