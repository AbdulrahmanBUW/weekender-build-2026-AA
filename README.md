# Weekender Build 2026 — Team Workspace

Dresden · 25–27 Sep 2026 · goal: **build live under own URL by Sun 14:00**.

| Path | What |
|---|---|
| `Weekender Build/` | **Obsidian vault** = project KB (Home, Ideas, Rules, Concepts, Decisions, Runs, Defects, Memory) |
| `n8n/workflows/` | exported n8n workflow JSON |
| `services/` | custom code (relay servers etc.) |
| `docs/diagrams` · `docs/security` · `docs/launch` | archify · security-audit · brag outputs |
| `CLAUDE.md` | shared instructions for both teammates' Claude sessions |

The Lovable app lives in its own GitHub repo (Lovable creates it via its GitHub integration); link it here once created.

## Setup (each teammate)
1. `git clone <repo-url>` 
2. Obsidian → *Open folder as vault* → select `Weekender Build/` inside the clone.
3. Settings → Community plugins → enable → Browse → install **Git** (by Vinzent) → enable.
   Set: *Auto pull on startup* = on, *Auto commit-and-sync interval* = 5 min, *Pull on commit-and-sync* = on.
4. Copy `.env.example` → `.env` for local secrets.

## Working rules
- Pull before you start, commit small, push often. Different notes per person avoids conflicts.
- End each work block with a note from `Templates/Memory.md` in `Memory/`.
