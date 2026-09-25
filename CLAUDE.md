# CLAUDE.md — Weekender Build team workspace

Two teammates (Abdul + teammate) share this repo. Event: Weekender Build, Dresden, 25–27.09.2026.
**Only success criterion: working build live under its own URL by Sun 27.09 14:00.** Scope ruthlessly.

## Sunday deliverables
1. Live build (Lovable) · 2. n8n workflow moving data/tasks · 3. optional AI function · 4. live demo · 5. Monday-Morning Plan.
Mandatory skills — installed project-level in `.claude/skills/` (pinned in `skills-lock.json`):
- `security-audit` (cloudflare/security-audit-skill) → write reports to `docs/security/`
- `archify` (tt-a1i/archify) → diagrams to `docs/diagrams/`
- `brag` / `brag-slim` (latent-spaces/brag) → launch video to `docs/launch/` (needs FFmpeg + Hyperframes; Sunday)

## Collaboration
- Task board: https://github.com/users/AbdulrahmanBUW/projects/2 (repo AbdulrahmanBUW/weekender-build-2026-AA). Milestones = pod slots. Status: Backlog → Today → In progress → Review → Done.
- `gh` CLI can read/update issues and the board. Reference issues as `AbdulrahmanBUW/weekender-build-2026-AA#N`.
- New teammate setup: see `ONBOARDING.md`.
- At session start: `git pull`. Before ending: write a `Memory/` handoff note, commit, push.

## Stack
Lovable (UI + Supabase) · n8n (orchestration, REST/webhooks – not websockets) · Supabase (data) · Claude · optional Vercel/Docker for custom services.

## Knowledge base = `Weekender Build/` (Obsidian vault)
- Read `00-Home/Home.md` and `Ideas/Merged Concept.md` first.
- Hard constraints are in `Rules/` — obey them.
- Record decisions in `Decisions/`, test/demo runs in `Runs/`, bugs in `Defects/`, session handoffs in `Memory/` — always use the matching file in `Templates/` (frontmatter matters).
- Use `[[wikilinks]]` between notes. Filenames: plain English titles.

## Conventions
- No secrets in any committed file (see `Rules/No secrets in repo.md`).
- n8n exports → `n8n/workflows/`. Diagrams → `docs/diagrams/`. Audit → `docs/security/`.
- Commit small with clear messages; pull before editing shared notes.
