# Weekender Build 2026 — Team Workspace

Dresden · 25–27 Sep 2026 · goal: **build live under own URL by Sun 14:00**.

**Task board:** https://github.com/users/AbdulrahmanBUW/projects/2 · milestones = pod slots

| Path | What |
|---|---|
| `Weekender Build/` | **Obsidian vault** = project KB (Home, Ideas, Rules, Concepts, Decisions, Runs, Defects, Memory) |
| `n8n/workflows/` | exported n8n workflow JSON |
| `services/` | custom code (relay servers etc.) |
| `docs/diagrams` · `docs/security` · `docs/launch` | archify · security-audit · brag outputs |
| `CLAUDE.md` | shared instructions for both teammates' Claude sessions |
| `.claude/skills/` | mandatory skills (security-audit, archify, brag, brag-slim), pinned in `skills-lock.json` |
| `ONBOARDING.md` | **START HERE: status, access, setup, how to vibecode** |

The Lovable app is the Lovable project **"HalloTermin Paper"** (connected to our Supabase), **live at https://dresden-mit-kind.lovable.app**. Its code syncs both ways with the private repo https://github.com/AbdulrahmanBUW/hallotermin-paper (TanStack Start with SSR; UI strings come from `docs/i18n/ui-strings.json` in this repo).

## Setup (each teammate)
Follow **[ONBOARDING.md](ONBOARDING.md)** — clone, open in Claude Code (skills + CLAUDE.md come with the repo), open the vault in Obsidian with the Git plugin.

## Working rules
- Pull before you start, commit small, push often. Different notes per person avoids conflicts.
- End each work block with a note from `Templates/Memory.md` in `Memory/`.
