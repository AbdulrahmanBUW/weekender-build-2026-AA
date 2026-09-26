---
type: concept
tags: [tooling, research]
sources:
  - https://github.com/firecrawl/firecrawl
  - https://github.com/firecrawl/firecrawl-mcp-server
  - https://docs.firecrawl.dev/mcp-server
  - https://docs.firecrawl.dev/features/agent
  - https://docs.firecrawl.dev/features/alexandria
  - https://docs.firecrawl.dev/features/alpha/deep-research
  - https://docs.firecrawl.dev/rate-limits
  - https://www.firecrawl.dev/pricing
  - https://www.firecrawl.dev/alexandria
  - https://www.firecrawl.dev/blog/introducing-alexandria-series-b
  - https://www.firecrawl.dev/integrations/claude-code
  - https://www.firecrawl.dev/blog/introducing-firecrawl-skill-and-cli
---
# Firecrawl and Alexandria

Researched 2026-09-26 for the build. It follows on from [[Newcomer Resources - Crawler]] and [[Toolchain - MCP, Skills, Plugins]].

## Summary
- **Firecrawl** is a web data API. It turns a URL into clean markdown or JSON, and it can also search the web, crawl a site, map a site's URLs, and run an autonomous **agent** that finds data from a prompt and a schema. The core is open source (AGPL-3.0) and can be self-hosted. The cloud API at firecrawl.dev has extra proprietary features.
- **Alexandria is real and belongs to Firecrawl.** It was announced on **2026-09-22** with Firecrawl's $75M Series B. It is a "knowledge library for agents": one interface over official data providers (e.g. FRED, World Bank, Companies House UK), licensed publishers, Firecrawl's own indexes (**Research**, **Developer**, **Government**: laws, regulations, ordinances, tax forms, permits) and the live web. You reach it through the normal Firecrawl API, MCP and CLI (`sources: ["alexandria"]`, `firecrawl_find_tools`).
- **For us:** keep using **n8n's managed Firecrawl** (Gateway credits, no own key) for the production crawler. For ad-hoc research from Claude Code, the fastest path needs **no key at all**: the hosted Firecrawl MCP via **OAuth** or **keyless** mode. Only get a free API key (1,000 credits/month) if you want `agent`/`crawl`/Alexandria from Claude Code beyond the keyless limits.

## What Firecrawl offers (Sept 2026)

| Endpoint | What it does | Cost (cloud) |
|---|---|---|
| `scrape` | One URL → markdown / HTML / screenshot / JSON (with schema) | 1 credit/page, +4 for JSON/"question" formats |
| `batch scrape` | Many known URLs, async | 1 credit/page |
| `search` | Web search, optionally with full page content; `sources: ["web","alexandria"]` | 2 credits per 10 results |
| `map` | List all URLs of a site | 1 credit |
| `crawl` | Scrape a whole site (depth/limit) | 1 credit/page |
| `agent` (`/v2/agent`) | Autonomous: prompt (+ optional `urls`, JSON `schema`) → structured data. Model `spark-2`, `effort` low/medium/high, `maxCredits` (default 2,500). Async job, poll `GET /v2/agent/{id}`, results kept 24 h | **5 free runs/day**, then "dynamic" (usually a few hundred credits). Failed runs are free |
| `interact` | Click/type/navigate on a page after scraping | 2 credits/browser-minute |
| `parse` | PDF/documents → markdown/JSON | – |
| `monitor` | Scheduled re-checks with diffs | 1 credit/page/check |
| `extract` | Older structured-extraction endpoint; `agent` is described as its successor | – |
| `deep-research` | **Legacy/unmaintained since 30 Jun 2025.** Firecrawl says: use `search` + `agent` instead | do not use |

**Plans:** Free $0 = 1,000 credits/month, 2 concurrent browsers (no card). Hobby ~$16/mo = 5,000. Standard ~$83/mo = 100,000 (annual prices).
**Free plan rate limits (req/min):** scrape 10, search 10, map 10, crawl 2, agent 2, interact 2.

**Ways to use it**
- **Self-host:** repo `firecrawl/firecrawl` (Docker). Point clients at it with `FIRECRAWL_API_URL`. Not worth it for a 48 h event.
- **MCP server `firecrawl-mcp`:** local (`npx -y firecrawl-mcp`) or hosted at `https://mcp.firecrawl.dev/v2/mcp` (API key as bearer, or **keyless**: rate-limited scrape/search/parse) and `https://mcp.firecrawl.dev/v2/mcp-oauth` (sign in through the browser). The full profile has 26 tools, including `firecrawl_scrape`, `_search`, `_map`, `_crawl`, `_interact`, `_agent`, `_parse`, `_developer_search`, `_find_tools` (Alexandria catalogue) and `_monitor_create`.
- **CLI + skills:** `npx -y firecrawl-cli@latest init --all --browser` installs the CLI and the skills (firecrawl-scrape/-search/-crawl/-map/-agent/-interact/-parse/-monitor/-download) into every detected agent, including Claude Code. It writes results to files instead of into the context window, which saves tokens. There is a keyless free tier for search/scrape/interact.
- **Claude Code plugin:** `claude plugin install firecrawl@claude-plugins-official`, then `/firecrawl:setup` (needs an API key).
- **n8n (ours):** node `@mendable/n8n-nodes-firecrawl.firecrawl` with the managed Gateway credential (scrape, map, search, crawl, agent). Workflow 02 already uses it for scrape.

## What Alexandria offers
- **Coverage (from the landing page, 2026-09-26):** about 93 providers, 640 capabilities, 20 categories. The launch press said 82 providers, 471 capabilities and 113M+ technical documents, so the catalogue is growing fast. Indexes: Research (~43M abstracts), Developer (70M+ READMEs/docs/issues/PRs), Government (laws, regulations, ordinances, permits, tax forms).
- **Use:** API `search(query, {sources: ["web","alexandria"]})`. CLI: `firecrawl search "…" --sources alexandria`, `firecrawl find-tools --providers <name>`, `firecrawl scrape <provider/capability>`. MCP: `firecrawl_find_tools`, then `firecrawl_scrape` on a capability.
- **Cost:** finding tools is free. Running a provider capability costs credits at the price in its "tool contract". Some providers need an org admin to accept their terms first (the error returns `requiresAction.url`).
- Firecrawl claims agents using it scored 21% higher on answer quality than with built-in web tools (845 tasks, their own benchmark).

**UNVERIFIED for our use case:**
- Whether the Government Index covers **German / Saxon / Dresden** sources (e.g. AufenthG, SGB V, dresden.de). Nothing on the pages mentions Germany or the EU. Test with job 5 below before relying on it.
- Whether n8n's managed Firecrawl node supports `sources: alexandria` or `find_tools`. Its operation list (scrape/map/search/crawl/agent) suggests not, so assume Alexandria needs Claude Code + MCP/CLI.
- Whether the Gateway credential lets `agent` run beyond the 5 free runs/day, and how Gateway credits map to Firecrawl credits.
- Alexandria-specific pricing is not published beyond "per tool contract".

## Recommended setup

**Rule:** production data keeps flowing through n8n workflow 02 (managed Firecrawl, logged in `events`, deny-list enforced). Claude Code Firecrawl is only for **research by a human in the loop**: it produces vault notes or candidate URLs, and those feed the n8n allow-list or `guides`.

### Option A: no key (start here)
Hosted MCP with OAuth. There is no secret in any file, and each teammate signs in through `/mcp`.
```powershell
claude mcp add --transport http --scope local firecrawl https://mcp.firecrawl.dev/v2/mcp-oauth
# in Claude Code: /mcp -> firecrawl -> Authenticate
```
Keyless alternative (rate-limited scrape/search/parse only): `claude mcp add --transport http --scope local firecrawl https://mcp.firecrawl.dev/v2/mcp`.
Use `--scope local` (just you, not committed) until the team agrees to add it to `.mcp.json`.

### Option B: own free API key (only if needed for agent/crawl/Alexandria)
1. Sign up at firecrawl.dev (free, 1,000 credits/mo). The user does this themselves.
2. Set it as a user env var, never in a file: `setx FIRECRAWL_API_KEY "fc-..."`, then open a new terminal and restart Claude Code.
3. Proposed `.mcp.json` entry (**not applied**; needs a team decision). Stdio, so the key stays in the local env:
```json
"firecrawl": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "firecrawl-mcp"],
  "env": { "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY:-}" }
}
```
Why stdio: Claude Code reads credential-looking env names as empty in *remote* url/headers (see [[Toolchain - MCP, Skills, Plugins]]). If you want the hosted HTTP server with a key, use a custom name, e.g. `"headers": {"Authorization": "Bearer ${FC_MCP_BEARER}"}`.
CLI alternative (token-efficient, writes files): `npx -y firecrawl-cli@latest init --all --browser`.

### Option C: n8n only (no Claude-side tool)
Add a Firecrawl **agent** node (managed credential) to a copy of workflow 02 for jobs 1–3 below. Set `maxCredits` low (e.g. 300) and `onError: continueRegularOutput`. This is best when the result must land in Supabase automatically.

**Allow list for Claude Code** (proposal for `.claude/settings.json`): allow `mcp__firecrawl__firecrawl_scrape`, `_search`, `_map`, `_find_tools`. Ask for `_agent`, `_crawl`, `_interact`, `_monitor_create` (these cost credits and run long).

## 5 ready-to-run research jobs
Every job uses only official/allowed domains, always keeps the source URL and date, and outputs facts only. Paste the prompt into Claude Code (MCP tool named) or into the n8n agent node.

**1. Health insurance registration guide (fixes our failed 4th guide)**
Tool: `firecrawl_agent`, `effort: medium`, `maxCredits: 300`, `urls`: `https://www.make-it-in-germany.com/en/living-in-germany/insurance/health-insurance`, `https://www.bundesgesundheitsministerium.de/`, `https://www.dresden.de/`, `https://www.tu-dresden.de/`, `https://www.verbraucherzentrale.de/`.
Prompt: *"How does a newcomer to Dresden (EU and non-EU; employee, student, job seeker) register for German health insurance (gesetzlich vs privat)? Give steps, deadlines, documents, who issues the insurance certificate (Versicherungsbescheinigung), and links. Use only the given official domains. Mark any conflict between sources."*
Schema:
```json
{"type":"object","properties":{
 "title_en":{"type":"string"},"summary_en":{"type":"string"},
 "steps":{"type":"array","items":{"type":"object","properties":{"step":{"type":"string"},"who":{"type":"string"},"source_url":{"type":"string"}}}},
 "checklist":{"type":"array","items":{"type":"string"}},
 "conflicts":{"type":"array","items":{"type":"string"}}},
 "required":["title_en","summary_en","checklist"]}
```
Then map the result into the `guides` row `health-insurance-registration` (same format as the other guides) or feed it to the existing Claude step.

**2. Ausländerbehörde Dresden document checklists**
Tool: `firecrawl_map` on `https://www.dresden.de` with search `auslaenderbehoerde`, then `firecrawl_scrape` (JSON format + schema) on the returned pages. This is cheaper and more controlled than `agent`.
Schema per page: `{permit_type, required_documents[], fees, appointment_how, address, source_url, last_updated_on_page}`. Check the new address (Lingnerallee 3, see [[DEF-006 Brave place results stale or misclassified]]).

**3. English-speaking doctors: verification, not discovery**
Do **not** crawl 116117/KV Sachsen/Doctolib/Jameda/Google Maps. Instead take our existing `resources` rows (category `doctor`) that have a practice website, and `firecrawl_scrape` **only the practice's own website** with the format `question`/JSON: `{"languages_mentioned":[...], "evidence_quote":"...", "source_url":"..."}`. Only set `languages` when the practice itself states it, and keep the "not verified, call ahead" note. Other allowed extra sources: official lists on `dresden.de` or TU Dresden International Office pages, if they exist.

**4. Community events for newcomers (next 4 weeks)**
Tool: `firecrawl_search`, query `"Dresden" (Sprachcafé OR "language café" OR Stammtisch OR "welcome" OR Integration) Veranstaltung Oktober 2026`, limit 10. Then scrape the organiser pages only (dresden.de, tu-dresden.de, Welcome Center, migrant counselling offices already in `resources`). Schema: `{event_name, date, time, venue, organiser, language, cost, url}`. Store as research output only. There is no `events` table for the app yet, so decide first.

**5. Alexandria probe: German legal basis (tests the unverified point)**
Tool: `firecrawl_find_tools` / `firecrawl_search` with `sources: ["alexandria"]` (CLI: `firecrawl search "Aufenthaltsgesetz Anmeldung Meldepflicht Sachsen" --sources alexandria`). Queries: "Bundesmeldegesetz 2 weeks registration", "SGB V Versicherungspflicht", "AufenthG §81 Antrag". Record in a `Runs/` note whether German law/government sources come back. If they do, cite them in the guides. If not, note that Alexandria has no DE coverage yet.

## Legal / ToS notes
- **Deny-list stays** (from [[Newcomer Resources - Crawler]]): 116117 Arztsuche, KV Sachsen Arztsuche, Doctolib, Jameda and Google Maps. Their terms forbid automated extraction or reuse of listings. The `agent` endpoint browses on its own, so **always pass an explicit `urls` allow-list** and say "use only these domains" in the prompt. Check its sources in the output. *(The exact ToS clauses were not re-read today; this is our existing project rule.)*
- Firecrawl says it respects robots.txt, but responsibility for the use stays with us. Do not use `crawl` on third-party sites, keep to single-page scrapes, and stay below the rate limits.
- Only public business/official information, no personal data (see [[Data minimisation - no symptoms]]). Doctors appear only as practice listings.
- Alexandria providers can have their own terms (`requiresAction.url`). The user must accept these, never Claude.
- Firecrawl OSS is **AGPL-3.0**. That only matters if we self-host a modified copy as a network service. We don't.
- Secrets: API keys only in env vars (see [[No secrets in repo]]). Never paste `fc-…` keys into notes, workflows or chat.
