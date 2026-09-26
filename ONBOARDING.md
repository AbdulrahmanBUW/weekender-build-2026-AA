# START HERE — Anastasia's guide (status + setup + how to vibecode)

Weekender Build, Dresden, 25–27.09.2026 · **Goal: our build is live under its own URL by Sun 27.09, 14:00.**
Last updated: Sat 26.09.2026, ~13:50 (by Abdul + Claude). **What changed: see the newest note in vault `Memory/` (now `Memory/2026-09-26 Handoff - merged build.md`).**

- Repo (private): https://github.com/AbdulrahmanBUW/weekender-build-2026-AA
- Task board: https://github.com/users/AbdulrahmanBUW/projects/2 (milestones = pod slots)
- Knowledge base: the Obsidian vault in `Weekender Build/` → open `00-Home/Home.md`

---

## 0. Where we are (TL;DR)

| Piece | Status | Where |
|---|---|---|
| **Merged product** | ✅ accepted 26.09: **Dresden mit Kind** (family hub: courses, events, bilingual communities, library + Health & services) with **"Ask for me"** (our AI phones the place in German, answer in the parent's language) | vault `Ideas/Merged Concept.md` (section "Build status"), `Decisions/DEC-003 Merged concept.md` |
| UI plan | ✅ **Plan v3 is the UI source** (routes, screens, data contract, Lovable Knowledge + prompts); v2 stays the design base | vault `Concepts/Frontend and UX Plan v3 (merged).md` |
| Database (Supabase `weekender-build`) | ✅ merge migration live: family fields on `resources`, `family_events`, `suggestions`, guide categories, `course_enquiry` + `kita_enquiry`, "checked by phone" trigger | `supabase/migrations/`, vault `Concepts/Data Model.md` |
| Family hub data | ✅ **92** family listings (incl. the demo listing *Olgas Musikstudio*), **70** service places, **44** events (to 29.11.), **8** guides, all sourced. **Review, don't research:** `docs/content-kit/review/` sheets + README section "Review and improve" (vault `Runs/RUN-025 Data round 2 and review sheets.md`) | vault `Concepts/Family Hub Data.md`; add more via `docs/content-kit/` |
| Call types | ✅ **10**: doctor, authority, landlord, contract, bank, pharmacy, restaurant, other + **course_enquiry** (free spot / trial lesson / waiting list) + **kita_enquiry** (Kita place / waiting list / visit). Full loop tested on a real course listing (RUN-023) | vault `Concepts/Task Types - How to extend.md`, `Runs/RUN-023 Merged flow E2E.md` |
| n8n | ✅ 01 brief writer · 02 Dresden crawler (don't run before the demo, credits) · 03 Deepgram test · 04 task intake with provider prefill (`/webhook/task-intake`) · 05 live subtitles (other side only) · 06 result + assistant subtitles in the user's language — all on Claude Haiku to save credits | n8n: https://arahmandeaxo.app.n8n.cloud · `n8n/workflows/` |
| Voice call (Deepgram, German) | ✅ relay: templates for all 10 types, trial lesson / Kita visit booking, `record_result`, voice input `/listen`; course, Kita, pharmacy and curveball role-plays pass. 🟡 not hosted publicly yet | `services/voice-relay/` (needs your own `.env`), `docs/deploy-relay.md` |
| Lovable app | 🟡 P1 shell only → **next: build with Plan v3 prompts** | Lovable project |
| Presentation | ✅ Pitch Kit, Pixel Agents office, archify diagrams, competitors, Monday plan, security review | vault `Concepts/`, `docs/` |

**Important:** backend and data are done and tested; what is missing for Sunday is the **Lovable UI** (Plan v3 prompts), a public host for the relay, the demo listing, and the RU/UK/AR translation review. "HalloTermin" is now only the engine name inside; the UI says **Dresden mit Kind** and **Ask for me**.

---

## 1. Access you need (Abdul sends the invites)

| Tool | How you get in | Status |
|---|---|---|
| GitHub repo | already a collaborator | ✅ |
| GitHub task board | Abdul: Project → ⋯ → Settings → Manage access | ✅ |
| n8n Cloud | Abdul: n8n → Settings → Users → Invite | ⏳ ask Abdul |
| Supabase | Abdul: Supabase → Organization → Team → Invite | ⏳ ask Abdul |
| Lovable | Abdul: project "HalloTermin Paper" → **Invite** (top right) | ⏳ ask Abdul |

---

## 2. Install (skip what you have)

| Tool | Why | Check / install |
|---|---|---|
| Git | sync | `git --version` |
| Node.js 22+ | skills, Supabase CLI | `node --version` |
| Claude Code (desktop app Code tab or CLI) | our shared AI setup | `claude --version` |
| Obsidian | knowledge base | — |
| GitHub CLI (optional) | board + issues from the terminal | `gh auth login` |
| rtk (recommended) | cuts Claude token use on shell output | `winget install -e --id rtk-ai.rtk` → `rtk init -g` → restart Claude (Mac: see github.com/rtk-ai/rtk) |
| FFmpeg (Sunday only) | brag launch video | `winget install -e --id Gyan.FFmpeg` (Mac: `brew install ffmpeg`) |
| Docker Desktop (optional) | local copy of the database | `npx supabase start` |

## 3. Clone + Claude setup

```bash
git clone https://github.com/AbdulrahmanBUW/weekender-build-2026-AA.git
cd weekender-build-2026-AA
cp .env.example .env    # local secrets only, never commit
```

Open the **cloned folder** as your project in Claude Code. You automatically get:

- **`CLAUDE.md`** — shared rules for both our Claudes (deliverables, stack, database, vault conventions). Claude reads it at start.
- **`.claude/skills/`** — 32 project skills:
  - mandatory: `security-audit` (cloudflare), `archify` (diagrams), `brag` + `brag-slim` (launch video)
  - UI quality: `anti-ai-slop-ui-ux`, `component-reference-design`, `ui-ux-pro-max` — **use for every Lovable/UI prompt**
  - n8n: 15 `n8n-*` skills + `using-n8n-mcp-skills` (czlonkowski/n8n-skills)
  - `hyperframes-*` (used by brag)
- **`.mcp.json`** — connects Claude to our tools. Approve the servers when Claude asks:
  - `n8n` (official n8n MCP: build/test/publish workflows) → needs your own token: n8n → Settings → Instance-level MCP → API key → `setx N8N_MCP_TOKEN "<token>"` (Mac: add `export N8N_MCP_TOKEN=...` to `~/.zshrc`) → restart Claude
  - `n8n-mcp` (community server the n8n skills are written for) → optional: n8n → Settings → n8n API → `setx N8N_API_KEY "<key>"`
  - `lovable` (drive Lovable from Claude) → sign in with OAuth when asked
- **Never paste tokens into chat or files.** Environment variables only.

**Check it works** — ask your Claude:
> "Read CLAUDE.md, ONBOARDING.md and Weekender Build/00-Home/Home.md. List the skills and MCP servers you have, summarise where the project stands, and tell me what's on the task board for today."

## 4. Obsidian vault (knowledge base)

1. Obsidian → **Open folder as vault** → select `Weekender Build/` **inside the clone**.
2. Settings → Community plugins → **Turn on** (once). The **Git** plugin is preinstalled: pulls on start and every 5 min, auto commit-and-sync every 10 min.
3. Open `00-Home/Home.md`: checklist, open decisions, dashboard (runs, defects, decisions, rules) and a map of all notes.
4. Use the templates in `Templates/` (Rule, Concept, Decision, Run, Defect, Memory) — frontmatter drives the dashboard.

---

## 5. How the system works (current build)

```
[Lovable app]  --insert row-->  [Supabase: call_requests]
                                      |  database trigger (pg_net), secret header
                                      v
                               [n8n webhook "new-request"]  -> replies instantly
                                      |  validate consent/phone/name
                                      v
                               [Claude via n8n Gateway credits]  -> German call brief
                                      |
                                      v
                 [Supabase: call_requests.status = 'briefed', call_brief_de, events row]
                                      |  Realtime
                                      v
                               [Lovable app shows it live]
```

- Tables: `call_requests`, `calls`, `transcript_lines`, `events` (details: vault `Concepts/Data Model.md`).
- The browser only **inserts** a request and **reads/subscribes**. All backend work is n8n (with the Supabase service key stored as an n8n credential).
- Secrets live in: Supabase Vault (n8n URL + webhook secret), n8n credentials (webhook secret, Supabase key), n8n Gateway credits for Claude (no Anthropic key needed). **None in git.**

---

## 6. Your first tasks (in order)

1. **Write your idea** in `Weekender Build/Ideas/Idea B - (Teammate).md` (template headings are there: problem, for whom, where it breaks, the one moment, feasible in 48 h). Commit + push, or let Obsidian Git sync it.
2. **Merge with Abdul** in `Ideas/Merged Concept.md` — Claude can help:
   > "Read Idea A and Idea B in the vault. Propose 2–3 ways to merge them into one MVP that fits our existing stack and database pattern (form → Supabase → n8n + Claude → live result). For each: what we reuse, what changes in the schema/n8n/Lovable, and the risk for Sunday 14:00. Then fill Ideas/Merged Concept.md with the one we pick."
3. **Record the decision** as `Decisions/DEC-003 Merged concept.md` (template `Templates/Decision.md`) and accept/adjust DEC-001 (voice) and DEC-002 (backend).
4. **Then build the UI in Lovable** with the prompt pack (see 7).
5. **Pod #01 pitch** (5 min: what, who, hypothesis) — Claude can draft it from the merged concept.

## 7. How to vibecode here (patterns that work)

**Lovable (UI)** — use `Weekender Build/Concepts/Lovable Prompt Pack.md`:
- Step 0 ✅ done (our Supabase is connected). **Never click "Enable Cloud" / Lovable Cloud.**
- Next: paste **Knowledge part A + part B** into Lovable → More → Settings → Knowledge (≈8,000 chars) — *update it first if the merged concept changes the product.*
- Then send **P2 → P7** one at a time in **Build** mode and check the preview after each. P1 is done.
- Credits: 122 left (P1 cost 2.2). Fix small things with short follow-ups, never re-send a whole prompt.
- Ask Claude to adapt prompts: *"Using the ui-ux-pro-max and anti-ai-slop-ui-ux skills, rewrite prompt P2 of the Lovable Prompt Pack for our merged concept. Keep the data contract exact."*

**Database (Supabase)** — schema changes only via migration files:
> "Create a Supabase migration that adds <X> to <table>, update seed.sql and Concepts/Data Model.md, test locally with `npx supabase db reset`, then push with `npx supabase db push` and verify RLS as anon."

**n8n** — Claude builds directly in our n8n via MCP:
> "Using the n8n skills, add a step to workflow 'HalloTermin 01' that <…>. Validate, test with pin data, publish, export to n8n/workflows/, and log a Run note."

**Every work block ends with:** a note in `Memory/` (template `Templates/Memory.md`), `git pull`, commit, push. Log tests in `Runs/`, bugs in `Defects/`.

## 8. Rules that bite (read `Weekender Build/Rules/`)

- **No secrets in git** — ever. Tokens/keys only in env vars, Supabase Vault or n8n credentials.
- **Never Lovable Cloud** — our own Supabase project is connected.
- **Schema only via `supabase/migrations/`** — never click-edit tables in the dashboard, never let Lovable create tables.
- **n8n: production webhook URLs + Publish** after every change (test URLs 404 in production).
- **Never make the database wait for AI** — n8n replies at once and writes results back (lesson from DEF-003).
- **Claude 5 models reject `temperature`** (DEF-002). **IF nodes: single-value checks need `singleValue: true`** (DEF-001).
- Health data: category only, no symptoms · AI always discloses itself · never store call audio.

## 9. Where to find things

| What | Where |
|---|---|
| Overview, checklist, dashboard | vault `00-Home/Home.md` |
| 48 h plan mapped to event slots | vault `Concepts/Build Plan - 48h.md` |
| Event rules & schedule | vault `Concepts/Weekender Build - Event Format.md` |
| Stack guides (Lovable, Supabase, n8n) | vault `Concepts/*Practical Guide.md` |
| Lovable UI prompts + design | vault `Concepts/Lovable Prompt Pack.md` |
| Lovable connectors we use / skip | vault `Concepts/Lovable Connectors - What We Use.md` |
| Tools, MCP, plugins | vault `Concepts/Toolchain - MCP, Skills, Plugins.md` |
| Test history / bugs | vault `Runs/`, `Defects/` |
| Latest handoff | vault `Memory/` (newest note) |
