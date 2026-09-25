# Onboarding — Teammate Setup (≈15 min)

Welcome! This repo is our shared workspace for Weekender Build (Dresden, 25–27.09.2026).
Goal: **our build is live under its own URL by Sun 27.09 14:00.**

- Repo: https://github.com/AbdulrahmanBUW/weekender-build-2026-AA
- Task board: https://github.com/users/AbdulrahmanBUW/projects/2 (milestones = pod slots)

## 1. Install (skip what you have)
| Tool | Why | Check |
|---|---|---|
| Git | sync | `git --version` |
| Node.js 22+ | skills (archify, brag) | `node --version` |
| Claude Code (desktop app Code tab or CLI) | shared AI setup | `claude --version` |
| Obsidian | knowledge base | — |
| GitHub CLI (optional) | issues/board from terminal | `gh --version` → `gh auth login` |
| FFmpeg (only for Sunday's brag video) | launch video | `ffmpeg -version` |

## 2. Clone
```bash
git clone https://github.com/AbdulrahmanBUW/weekender-build-2026-AA.git
cd weekender-build-2026-AA
cp .env.example .env    # fill secrets locally, never commit
```

## 3. Claude — you get the same setup automatically
Open the **cloned folder** as your project in Claude Code. Everything is in the repo:
- `CLAUDE.md` — shared rules, deliverables, KB conventions (Claude reads it at start).
- `.claude/skills/` — the mandatory skills, already installed project-level:
  - `security-audit` (cloudflare/security-audit-skill) — "security audit this codebase"
  - `archify` (tt-a1i/archify) — "use archify to diagram …"
  - `brag` + `brag-slim` (latent-spaces/brag) — "/brag" launch video (Sunday)
- `skills-lock.json` — pinned skill versions. To update: `npx skills update -p`.

Quick check — ask your Claude: *"Read CLAUDE.md and 00-Home/Home.md, list the skills you have, and tell me what's on the task board for today."*

## 4. Obsidian vault (knowledge base)
1. Obsidian → **Open folder as vault** → select `Weekender Build/` **inside the clone**.
2. Settings → Community plugins → Turn on → Browse → install **Git** (by Vinzent) → Enable.
3. Git plugin settings: *Pull on startup* = on · *Auto commit-and-sync interval* = 5 · *Pull before push* = on.
4. Templates are preconfigured (folder `Templates/`): use them for Rules, Concepts, Decisions, Runs, Defects, Memory.

## 5. First task for you
Write your idea in `Weekender Build/Ideas/Idea B - (Teammate).md` (template is already there), commit & push.
We then merge both ideas in `Ideas/Merged Concept.md` before the Pod #01 kick-off (Fri 20:00).

## 6. Working agreement
- **Pull before you start, push small and often.** Prefer creating your own notes over editing the same note at the same time.
- Move your card on the board: Backlog → Today → In progress → Review → Done.
- End each work block with a handoff note in `Memory/` (template: `Templates/Memory.md`).
- **No secrets in git** — keys go in `.env`, Lovable/Supabase Secrets or n8n credentials.
