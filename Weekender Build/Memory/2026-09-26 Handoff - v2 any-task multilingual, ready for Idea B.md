---
type: memory
date: 2026-09-26 13:30
by: abdul + claude
---
# Handoff: v2 (any task + multilingual) — ready for Anastasia's Idea B

## Done since yesterday
- **Product direction v2:** from "doctor appointments" to **any phone task** for newcomers, **12 input languages**, core loop Tell → Check → Call → Result → [[Frontend and UX Plan v2]] (screens, design, Lovable Knowledge + prompts P2–P10, demo storyboard).
- **Voice:** Deepgram connected ([[RUN-008 Deepgram German round trip]]); browser-call relay works ([[RUN-009 Voice relay self-test (Deepgram agent)]]); automated German receptionist role-play books correctly ([[RUN-012 Automated receptionist role-play]]). Disclosure stays (EU AI Act) but sounds natural (Plan v2 F6).
- **DB v2 live:** `call_requests` extended into generic tasks (task_type, goal_user/goal_de, constraints, allowed_facts, user_language …), subtitles + results in the user's language, status `completed`, Arabic pharmacy demo (`…0002`) → [[Data Model]].
- **Newcomer data:** 84 verified Dresden places + 4 guides (bank account, Anmeldung, Ausländerbehörde, health insurance), guides translated AR/TR/UK → [[Newcomer Resources - Crawler]], [[RUN-011 Resource spot-check]].
- **Security:** both medium findings fixed ([[docs/security]] review + remediation log).
- **Presentation kit:** [[Pitch Kit]], [[Agent Space - Who Does What]] (Pixel Agents), archify diagrams in `docs/diagrams/`, [[Competitive Landscape]], [[Monday-Morning Plan]], [[Accessibility and RTL Review]], UI strings EN/AR/TR/UK in `docs/i18n/`.

## Finished this afternoon
- n8n v2 live: 01 (all 8 task types), 04 intake `https://arahmandeaxo.app.n8n.cloud/webhook/task-intake`, 05 translate line, 06 result in user language → [[RUN-013 n8n v2 workflows]].
- Relay v2 live: task templates, `record_result`, `/listen` (13 languages) → [[RUN-014 Relay v2 generic tasks]].
- How to add a task type (important for the merge): [[Task Types - How to extend]].

## Next — Anastasia
1. `git pull`, open the vault, read [[Home]] → [[Frontend and UX Plan v2]] (section A is 1 page).
2. Write **Idea B** in [[Idea B - (Teammate)]].
3. Merge with Abdul in [[Merged Concept]] — ask Claude: *"Read Idea B, Idea A and Frontend and UX Plan v2. How does Idea B fit the any-task assistant (new task type? new user group? different channel?). Propose 2–3 merges, what changes in DB/n8n/relay/UI, and the risk for Sunday 14:00."*
4. Record the decision as `Decisions/DEC-003 Merged concept.md`; then we adapt the Lovable Knowledge + prompts and build the UI.

## Learnings / gotchas
- rtk hook mangles `grep -E` with `{n,}` → use python for regex scans.
- Deepgram's managed Claude list ≠ docs → `probe-models.js`; default `claude-sonnet-5`.
- In-app browser pane blocks the mic → test calls in normal Chrome.
