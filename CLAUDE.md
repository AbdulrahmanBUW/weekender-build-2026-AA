# CLAUDE.md — Weekender Build team workspace

Two teammates (Abdul + teammate) share this repo. Event: Weekender Build, Dresden, 25–27.09.2026.
**Only success criterion: working build live under its own URL by Sun 27.09 14:00.** Scope ruthlessly.

## Sunday deliverables
1. Live build (Lovable) · 2. n8n workflow moving data/tasks · 3. optional AI function · 4. live demo · 5. Monday-Morning Plan.
Mandatory skills — installed project-level in `.claude/skills/` (pinned in `skills-lock.json`):
- `security-audit` (cloudflare/security-audit-skill) → write reports to `docs/security/`
- `archify` (tt-a1i/archify) → diagrams to `docs/diagrams/`
- `brag` / `brag-slim` (latent-spaces/brag) → launch video to `docs/launch/` (needs FFmpeg + `hyperframes-*` skills, both set up)

Helper skills (also in `.claude/skills/`): `n8n-*` + `using-n8n-mcp-skills` (czlonkowski/n8n-skills — building/validating n8n workflows), `hyperframes-*` (heygen-com/hyperframes — used by brag).

## Database (Supabase)
- Schema = `supabase/migrations/*.sql` (source of truth), demo data = `supabase/seed.sql`. Explained in vault `Concepts/Data Model.md`.
- Local: `npx supabase start` (Docker) · `npx supabase db reset` (re-apply migrations + seed) · `npx supabase status`. Studio: http://127.0.0.1:54323
- Change schema only via a new migration file (`npx supabase migration new <name>`), never by hand in a dashboard.
- New `call_requests` rows trigger n8n via pg_net; URL + secret live in Supabase Vault (`n8n_new_request_url`, `n8n_webhook_secret`).

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
