---
type: concept
tags: [presentation, agents, tooling]
sources: [https://github.com/pixel-agents-hq/pixel-agents]
---
# Agent Space — who does what

For the Sunday demo we show our "agent office" live with **Pixel Agents** (MIT, pixel-agents-hq/pixel-agents): every Claude Code session and sub-agent becomes a pixel character at a desk, animated by what it's actually doing (reading, writing, running tools), with a live label.

## Run it
```bash
npx -y pixel-agents@1.4.1 --host 127.0.0.1 --port 3100
```
Open http://127.0.0.1:3100 · or in the Claude desktop app: preview `pixel-agents` (config in `.claude/launch.json`).
Settings used: **Always Show Labels** on · Sound on · Watch All Sessions off · Instant Detection (Hooks) **off** (it would modify global Claude settings — only enable on the demo laptop if wanted).
Privacy: reads Claude session transcripts from `~/.claude/projects/` locally, binds to 127.0.0.1, nothing leaves the laptop. Don't project it while a session shows secrets.

## The roster

### Humans
| Who | Role |
|---|---|
| **Abdul** | product owner (Idea A), infra (Supabase, n8n, voice), demo presenter |
| **Anastasia** | Idea B, merge partner, UI/Lovable, pitch & user interviews |

### Claude agents (visible in Pixel Agents)
| Character | Type | What it does | Output |
|---|---|---|---|
| **Orchestrator** | main Claude Code session | plans, talks to us, builds & tests, delegates, commits | repo, vault, n8n, Supabase |
| **Researcher: Voice** | sub-agent | voice-platform research (Deepgram/Retell/ElevenLabs, telephony, legal) | `Concepts/Voice *`, [[DEC-001 Voice platform (proposed)]] |
| **Researcher: Stack** | sub-agent | Lovable + Supabase + n8n integration patterns & pitfalls | stack guides, [[DEC-002 Backend and integration pattern (proposed)]], rules |
| **Researcher: Tooling** | sub-agent | MCP servers, skills, plugins | [[Toolchain - MCP, Skills, Plugins]] |
| **Designer** | sub-agent (anti-AI-slop + ui-ux-pro-max skills) | visual direction "Bilingual paper" + Lovable prompts | [[Lovable Prompt Pack]] |
| **Crawler builder** | sub-agent (n8n skills) | builds the newcomer-resources crawler + tables | `resources`, `guides`, [[Newcomer Resources - Crawler]] |
| *(Sunday)* **Security auditor** | skill `security-audit` | audits repo/app | `docs/security/` |
| *(Sunday)* **Diagrammer** | skill `archify` | architecture diagram | `docs/diagrams/` |
| *(Sunday)* **Launch-video maker** | skill `brag` | 20-s launch video | `docs/launch/` |

### Automation agents (run in n8n, not shown as characters — show the n8n canvas instead)
| Workflow | Trigger | AI / services | What it does |
|---|---|---|---|
| **HalloTermin 01 – Brief writer** | new row in `call_requests` (DB trigger) | Claude (n8n Gateway) | writes the German call brief, sets `briefed`, logs event |
| **Newcomer 02 – Resource crawler** | manual | Brave Search, Firecrawl, Claude | finds doctors, pharmacies, banks, Ausländerbehörde, community places; builds sourced guides |
| *(planned)* **Voice 03 – Deepgram** | brief ready | Deepgram TTS/STT/Voice Agent (German) | speaks German, transcribes live |

### Tools the agents use
Supabase (data + Realtime) · n8n (orchestration) · Lovable (UI) · GitHub (repo + board) · Obsidian vault (memory: Rules, Concepts, Decisions, Runs, Defects, Memory).

## Demo beat (≈30 s)
1. Show the pixel office: "This is our team — two humans and a small crew of AI agents."
2. Trigger something live (e.g. ask Claude to run the crawler or a quick audit) → a character walks to a desk and starts typing; label shows the tool.
3. Cut to the n8n canvas / app updating → "and this is what they built."
