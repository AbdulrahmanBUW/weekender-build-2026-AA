---
type: concept
tags: [tooling]
sources:
  - https://docs.n8n.io/connect/connect-to-n8n-mcp-server
  - https://docs.n8n.io/connect/connect-to-n8n-mcp-server/mcp-client-examples
  - https://docs.n8n.io/connect/connect-to-n8n-mcp-server/mcp-server-tools-reference
  - https://github.com/czlonkowski/n8n-mcp
  - https://github.com/czlonkowski/n8n-skills
  - https://supabase.com/docs/guides/getting-started/mcp
  - https://supabase.com/docs/guides/troubleshooting/cant-access-supabase-project-lovable-cloud
  - https://supabase.com/docs/guides/local-development/cli/getting-started
  - https://docs.lovable.dev/integrations/lovable-mcp-server
  - https://docs.lovable.dev/integrations/supabase
  - https://github.com/upstash/context7
  - https://vercel.com/docs/agent-resources/vercel-mcp
  - https://github.com/microsoft/playwright-mcp
  - https://github.com/anthropics/claude-plugins-official
  - https://code.claude.com/docs/en/mcp
  - https://github.com/heygen-com/hyperframes
  - https://winstall.app/apps/Gyan.FFmpeg
  - https://github.com/Vinzent03/obsidian-git
  - https://github.com/blacksmithgu/obsidian-dataview
  - https://github.com/SilentVoid13/Templater
---

# Toolchain - MCP, Skills, Plugins

Researched 2026-09-25 for the 48h build. Principle: **few tools, each with a clear job**. Every MCP server adds tool schemas to context and a prompt-injection surface, so only add what the build actually touches.

## Key facts that drive the choices

- **n8n now ships an official instance-level MCP server** (n8n Cloud included). Settings → *Instance-level MCP* → *Enable MCP access* (owner/admin). URL: `https://<instance>.app.n8n.cloud/mcp-server/http`. Auth: OAuth (preferred, per-user) or an MCP access token as `Authorization: Bearer`.
  - Tools: `search_workflows`, `get_workflow_details`, `execute_workflow`, `test_workflow` (pinned/simulated data), `publish_workflow`/`unpublish_workflow`, version history + diff, executions search, `list_credentials`, instance activity, **workflow builder** (`search_nodes`, `get_node_types`, `get_workflow_sdk_reference`, `validate_workflow`, `validate_node_config`; create/edit workflows from n8n 2.13+), data tables CRUD, agents.
  - Gotcha: **execute** only works on workflows toggled *Available in MCP*, which must be **published and have a webhook, form, schedule or chat trigger**. Per-project/folder toggle (2.24+), "Auto-expose new workflows" (2.36+).
- **czlonkowski/n8n-mcp** (~23k stars, active): stdio via `npx n8n-mcp`, node docs + templates + validation + 21 management tools via the n8n public API (`N8N_API_URL` + `N8N_API_KEY`). Largely overlaps the official server now. Keep as fallback.
- **czlonkowski/n8n-skills** (~6k stars, MIT): Claude Code plugin, 14 skills (expression syntax, Code node JS/Python, node config, workflow patterns, validation errors, AI agents, error handling, binary data, sub-workflows). Useful whichever MCP you use. Some skills reference n8n-mcp tool names; the knowledge still transfers.
- **Lovable Cloud ≠ your Supabase.** Supabase says Lovable Cloud projects do not show in your Supabase dashboard, have no service-role/API keys, and **cannot be reached by Supabase CLI or Supabase MCP**. For DB access from Claude Code, you have two options:
  - **Lovable MCP** (`https://mcp.lovable.dev`, official, all plans, OAuth). Tools: projects (create/list/remix/deploy), chat (`send_message` to the Lovable agent), code (files, diffs, history), **`query_database`** (SQL reads/writes/DDL on Lovable Cloud DB). Credits are charged only for `create_project` and `send_message`.
  - **Connect your own Supabase project to Lovable** (Lovable → Integrations → Supabase) instead of Lovable Cloud. Then Supabase MCP + CLI + dashboard all work. **Decide this before Lovable scaffolds the backend.** Migrating off Lovable Cloud later is a documented 30+ step job.
- **Claude Code `.mcp.json`** (repo root, committed): supports `type: "http"`, `headers`, and `${VAR}` / `${VAR:-default}` expansion in `url`, `headers`, `command`, `args`, `env`. If a variable is unset, the literal `${VAR}` is sent and `claude mcp list` warns. Credential-looking names such as `ANTHROPIC_API_KEY` or `NPM_TOKEN` are read as empty in remote url/headers, so use your own names. Each teammate approves project servers on first run (`claude mcp reset-project-choices` to redo). Approvals only auto-load in a **trusted** workspace.

## Recommended setup (5 items)

### 1. n8n official MCP + n8n-skills plugin
The main build surface: Claude inspects, builds, validates, tests and runs workflows on the n8n Cloud instance.

CLI (per user, OAuth):
```powershell
claude mcp add --transport http --scope project n8n https://<instance>.app.n8n.cloud/mcp-server/http
# then in Claude Code: /mcp -> n8n -> Authenticate
```
Token variant (if OAuth fails): `--header "Authorization: Bearer $env:N8N_MCP_TOKEN"` (or use the `.mcp.json` below).

Skills (inside Claude Code):
```
/plugin marketplace add czlonkowski/n8n-skills
/plugin install        (pick n8n-skills)
```

### 2. Backend DB access: pick ONE based on the backend decision
**A. Own Supabase project (recommended for control):** hosted Supabase MCP, scoped to one project. Use `read_only=true` unless you want Claude applying migrations. Prefer CLI migrations (see below) for writes.
```powershell
claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp?project_ref=<ref>&read_only=true&features=database,docs,debugging,development"
# /mcp -> supabase -> Authenticate (OAuth). PAT alternative: header Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}
```
**B. Lovable Cloud backend:** Lovable MCP (also useful in case A to drive Lovable chat, read diffs and deploy from Claude Code):
```powershell
claude mcp add --transport http --scope project lovable https://mcp.lovable.dev
```

### 3. Context7 (current library docs)
Up-to-date docs for Supabase JS, React/Vite, Tailwind, shadcn, n8n etc. Avoids stale-API hallucinations. Official Anthropic marketplace also lists it (`/plugin install context7@claude-plugins-official`).
```powershell
npx ctx7 setup        # OAuth, generates API key, configures Claude Code
```
Manual: http `https://mcp.context7.com/mcp`, header `Authorization: Bearer ${CONTEXT7_API_KEY}` (free key at context7.com/dashboard).

### 4. Hyperframes skills + CLI + FFmpeg (for /brag launch video)
Source: `heygen-com/hyperframes` (official HeyGen). Needs Node 22+ (have 24), FFmpeg, and headless Chrome (bundled/managed).
```powershell
winget install -e --id Gyan.FFmpeg        # open a new terminal afterwards so PATH refreshes
ffmpeg -version
npx skills add heygen-com/hyperframes     # interactive: tick the "Core Skills" group
#   (non-interactive: npx hyperframes skills update ; one skill: --skill hyperframes-cli)
npx hyperframes doctor                    # verify env
npx hyperframes check                     # used by brag skill to inspect a composition
```
Core skills: `hyperframes` (router), `hyperframes-core`, `-animation`, `-keyframes`, `-creative`, `-cli`, `-audio`, `-registry`, `media-use`. Other CLI commands: `init`, `preview`, `lint`, `render`, `snapshot`.

### 5. frontend-design plugin (official)
Only if Claude Code writes UI outside Lovable (for example a Vercel landing page or demo polish). Cheap, since it is a skill with no MCP server.
```
/plugin install frontend-design@claude-plugins-official
```

**Optional, only if Vercel is used:** `claude mcp add --transport http vercel https://mcp.vercel.com` then `/mcp` for OAuth (deployments, build logs, docs).

### Shared `.mcp.json` (repo root)
OAuth servers carry no secrets, so each teammate authenticates via `/mcp`. Put per-person values in user env vars (`setx SUPABASE_PROJECT_REF "abcd..."`, then open a new terminal).
```json
{
  "mcpServers": {
    "n8n": {
      "type": "http",
      "url": "${N8N_MCP_URL:-https://<instance>.app.n8n.cloud/mcp-server/http}"
    },
    "supabase": {
      "type": "http",
      "url": "https://mcp.supabase.com/mcp?project_ref=${SUPABASE_PROJECT_REF}&read_only=true"
    },
    "lovable": {
      "type": "http",
      "url": "https://mcp.lovable.dev"
    },
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": { "Authorization": "Bearer ${CONTEXT7_API_KEY}" }
    }
  }
}
```
Token-auth variant for n8n: add `"headers": { "Authorization": "Bearer ${N8N_MCP_TOKEN}" }`. Drop whichever of supabase/lovable you do not use.

### Shared `.claude/settings.json`
```json
{
  "enabledMcpjsonServers": ["n8n", "supabase", "lovable", "context7"],
  "permissions": {
    "allow": [
      "mcp__context7",
      "mcp__n8n__search_workflows",
      "mcp__n8n__get_workflow_details",
      "mcp__n8n__search_workflow_executions",
      "mcp__n8n__get_workflow_execution",
      "mcp__n8n__validate_workflow",
      "mcp__n8n__search_nodes",
      "mcp__n8n__get_node_types",
      "mcp__supabase__list_tables",
      "mcp__supabase__search_docs",
      "Bash(npx supabase status)",
      "Bash(npx supabase migration new:*)",
      "Bash(npx supabase db diff:*)",
      "Bash(npx hyperframes:*)",
      "Bash(gh pr view:*)",
      "Bash(gh pr list:*)",
      "Bash(git status)",
      "Bash(git diff:*)",
      "Bash(git log:*)"
    ],
    "ask": [
      "mcp__n8n__execute_workflow",
      "mcp__n8n__publish_workflow",
      "mcp__lovable__send_message",
      "mcp__lovable__query_database",
      "Bash(npx supabase db push:*)",
      "Bash(git push:*)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./**/.env)",
      "Bash(npx supabase db reset --linked:*)"
    ]
  }
}
```
Personal overrides go in `.claude/settings.local.json` (gitignored).

## Supabase CLI local dev (Windows, Docker)
Only for option A (own Supabase). Docker Desktop must be running. `npx` needs Node 20+ (have 24). Alternative global install: `scoop bucket add supabase https://github.com/supabase/scoop-bucket.git; scoop install supabase`.
```powershell
npx supabase init                          # creates supabase/ (config.toml, migrations/)
npx supabase start                         # local stack in Docker; prints API URL, anon/service keys, Studio at :54323
npx supabase migration new create_runs     # edit supabase/migrations/<ts>_create_runs.sql
npx supabase db reset                      # re-apply all migrations + seed.sql locally
npx supabase gen types typescript --local > src/types/supabase.ts
npx supabase login                         # browser auth once per machine
npx supabase link --project-ref <ref>
npx supabase db pull                       # if remote already has schema (e.g. Lovable-made)
npx supabase db push                       # apply local migrations to remote
npx supabase stop
```
Rule of thumb: when Lovable also edits the schema, run `db pull` before writing new migrations, so the two sides do not diverge.

## Obsidian community plugins (minimal)
Install by downloading `main.js`, `manifest.json`, `styles.css` (if present) from the latest GitHub release into `Weekender Build/.obsidian/plugins/<id>/`, then enable under Settings → Community plugins.

| Plugin id | Repo | Verdict |
|---|---|---|
| `obsidian-git` | `Vinzent03/obsidian-git` (v2.40.0) | **Install.** Pull on startup; manual or long-interval auto commit/push. |
| `templater-obsidian` | `SilentVoid13/Templater` (v2.25.1) | Optional. Only if you need prompts, dynamic filenames or auto-move to folder. Core Templates (`{{date}}`, `{{title}}`) is enough for Run/Defect/Decision notes. |
| `dataview` | `blacksmithgu/obsidian-dataview` (v0.5.68) | **Skip.** Core **Bases** covers Runs/Defects/Decisions dashboards from frontmatter (filters, sorting, table/card views) and is editable. Dataview is only needed for inline fields or DQL/JS queries. |

Obsidian Git notes: the git repo root is the parent of the vault. Git discovers the parent `.git`, but check Source Control shows files. Avoid a short auto-commit interval, because Claude Code also commits and fights over the index. Gitignore `.obsidian/workspace*.json`.

## Considered but skipped
- **czlonkowski/n8n-mcp** (stdio or hosted, 100 free calls/day): excellent, but the official n8n MCP now covers node types, validation, build, test and run with OAuth and no API key. Fallback if the official builder misbehaves:
  `claude mcp add n8n-mcp '-e MCP_MODE=stdio' '-e LOG_LEVEL=error' '-e DISABLE_CONSOLE_OUTPUT=true' '-e N8N_API_URL=https://<instance>.app.n8n.cloud' '-e N8N_API_KEY=<key>' -- npx n8n-mcp` (PowerShell quoting per their docs).
- **GitHub MCP**: `gh` CLI already authenticated. It is cheaper in tokens and Claude uses it natively.
- **Obsidian MCP (mcp-obsidian etc.)**: the vault is plain Markdown in the repo, so the filesystem tools (Read/Edit/Grep) are enough. The REST-plugin MCPs add moving parts for no gain.
- **Playwright MCP** (`claude mcp add playwright npx @playwright/mcp@latest`): the desktop app's built-in Browser pane already drives and screenshots pages, and Microsoft itself recommends the Playwright CLI + skills over the MCP for coding agents. Add it only for CLI-only headless E2E.
- **Vercel MCP**: add only if Vercel is actually used (command above).
- **Dataview, Templater**: see table above.
- **Supabase MCP against Lovable Cloud**: not possible (Lovable owns the project). Use the Lovable MCP `query_database` instead.
