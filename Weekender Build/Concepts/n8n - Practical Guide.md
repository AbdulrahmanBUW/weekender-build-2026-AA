---
type: concept
tags: [stack, n8n]
sources: [https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/, https://docs.n8n.io/build/understand-workflows/save-and-publish-workflows, https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.supabase/, https://docs.n8n.io/integrations/builtin/credentials/supabase/, https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatanthropic/, https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.errortrigger, https://docs.n8n.io/connect/connect-to-n8n-mcp-server, https://docs.n8n.io/connect/connect-to-n8n-mcp-server/mcp-server-tools-reference, https://docs.n8n.io/connect/connect-to-n8n-mcp-server/mcp-client-examples.md, https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger, https://github.com/n8n-io/n8n/issues/18528, https://community.n8n.io/t/lovable-app-with-n8n-ai-workflow-webhook-timeout/133975]
---
# n8n Cloud: Practical Guide (Sept 2026, n8n 2.x)

**Definition:** n8n is a visual workflow engine. A workflow starts from a trigger (Webhook, Schedule, Form, Chat…) and runs nodes (Supabase, HTTP Request, AI Agent, Gmail…). We have n8n Cloud Pro for one month.

**Why it matters for us:** it is deliverable 2 ("n8n workflow that moves data/tasks") and it hosts our AI function (deliverable 3).

## 1. n8n 2.x: Save vs **Publish** (replaces "Active")

- Edits **autosave** as a draft. Only **Publish** (top right, `Shift+P`) makes a version live. Publishing is what switches Webhook and Form triggers to their **production URLs** ([docs](https://docs.n8n.io/build/understand-workflows/save-and-publish-workflows)).
- Unpublish: via the Publish button dropdown (`Ctrl+U`).
- Tutorials from before 2026 talk about an "Active" toggle. In 2.x, that is **Publish**.
- **After each change you want live, publish again.** (A GitHub issue reported that webhook workflows picked up unpublished edits, [#23549](https://github.com/n8n-io/n8n/issues/23549). Don't rely on either behaviour; publish explicitly.)

## 2. Webhook node

([docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/))
- **Two URLs:**
  - **Test URL** `https://<inst>.app.n8n.cloud/webhook-test/<path>`: works only while you click **Listen for Test Event** / Execute in the editor, and catches one request. The data shows on the canvas.
  - **Production URL** `https://<inst>.app.n8n.cloud/webhook/<path>`: works only when the workflow is **published**. The data shows only in the **Executions** tab.
  - A `404 … webhook is not registered` error almost always means you used the test URL, or the workflow isn't published. See [[Rules/n8n - use production webhook URLs]].
- **HTTP Method:** POST. **Path:** set a readable one, e.g. `hallotermin-new-request` (otherwise it's a UUID).
- **Authentication:** Basic, **Header Auth**, JWT, None. Use Header Auth with a credential (Name `X-Webhook-Secret`, Value = long random string). Supabase sends the same header.
- **Respond:** `Immediately` · `When Last Node Finishes` · `Using 'Respond to Webhook' Node` · `Streaming response`.
  - For DB-webhook triggers: **Immediately** (Supabase doesn't care about the body, and pg_net times out after about 2–5 s).
  - For a synchronous API that the browser waits on: use `Using 'Respond to Webhook' Node` and put the **Respond to Webhook** node right after validation, *before* slow LLM steps. Long LLM chains cause browser timeouts ([community thread](https://community.n8n.io/t/lovable-app-with-n8n-ai-workflow-webhook-timeout/133975)).
- **Options:** **Allowed Origins (CORS)** (comma list or `*`), **IP(s) Allowlist**, max payload **16 MB**.
- **CORS:** on n8n Cloud you can't set `N8N_CORS_*` env vars, so the Webhook's *Allowed Origins* option is your only lever. There is a known bug where with **multiple origins only the first one is echoed back** ([#18528](https://github.com/n8n-io/n8n/issues/18528)). If you must call from the browser, set the single published origin (`https://<name>.lovable.app`) or `*` for the demo. Better: don't call n8n from the browser at all (see [[Integration Patterns]]).

## 3. Supabase node

- Operations (Row): **Create**, **Delete**, **Get**, **Get Many / Get all**, **Update** ([docs](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.supabase/)). It can also be attached as an **AI tool** to an AI Agent.
- Credential **Supabase API**: **Host** = `https://<ref>.supabase.co` (without `/rest/v1`), **Secret Key** = `sb_secret_…` from Project Settings → API Keys ([credential docs](https://docs.n8n.io/integrations/builtin/credentials/supabase/)). The secret key bypasses RLS, so updates just work.
- Update: *Select Conditions* → `id` equals `{{ $json.body.record.id }}`. Fields: `status`, `brief_de`…
- If you need upserts, RPC or complex filters, use an **HTTP Request** node to `https://<ref>.supabase.co/rest/v1/<table>` with the headers `apikey` + `Authorization: Bearer <secret>`. Better yet, put the secret in a *Header Auth* credential, not in the node.

## 4. HTTP Request node

- Calls the relay (`POST https://relay…/call`), external APIs and Edge Functions.
- Put auth in **credentials** (Header Auth / Bearer), not in plain header fields, so it isn't exported with the workflow JSON.
- Settings → **Retry On Fail** (e.g. 2 tries, 2000 ms) for flaky APIs. **On Error → Continue (using error output)** to branch to a "mark failed" path.

## 5. AI: Anthropic Claude

- For a single structured transformation (form → German brief), use **Basic LLM Chain** + sub-node **Anthropic Chat Model**, and add a **Structured Output Parser** if you want JSON. Use **AI Agent** only if the model needs to choose tools (e.g. a Supabase tool). An agent is less predictable and costs more tokens.
- **Anthropic Chat Model** options: Model (pick the current Claude Sonnet from the dropdown; the docs' model list is outdated), Maximum Number of Tokens, Sampling Temperature, Top K/P, **Prompt Caching** ([docs](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatanthropic/)).
- Credential: an **Anthropic API key**, *or* "Gateway credits on n8n Cloud" per the docs (*we haven't checked how many credits the Pro trial includes*).
- Sub-node gotcha: expressions in sub-nodes resolve to the **first item only** ([docs](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatanthropic/)).
- Example system prompt for HalloTermin: "You write a German phone brief for an AI assistant calling a German doctor's practice on behalf of {{name}}. Output JSON {opening_de, facts:{…}, allowed_windows:[…], questions_expected:[…]}. The first sentence must disclose 'KI-Assistentin'. Never invent facts."

## 6. Calendar / email nodes

- **Google Calendar** → Event → **Create**: Calendar = team calendar; Start/End from `booked_slot`; Additional Fields → **Attendees** = user email. Whether Google emails the invite depends on the node's "send updates" option. *Unverified; test it Saturday. Fallback: attach an .ics or just a link.*
- **Gmail** → Message → **Send** (OAuth2 Google credential) or **Send Email** (SMTP credential). For a hackathon, Gmail OAuth with a team Google account is quickest. On n8n Cloud, Google credentials usually offer a one-click "Sign in with Google". *Verify.*
- Keep the email in English: include the date/time, practice, what to bring (Versichertenkarte, Überweisung).

## 7. Error handling

- Create a workflow named **"Error Handler"** starting with an **Error Trigger** → Gmail/Send Email to the team (+ optional Supabase update `status='failed'`). In each production workflow: **Options → Settings → Error workflow → "Error Handler"** ([docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.errortrigger)).
- The error workflow **doesn't fire on manual test runs**, only on production executions.
- Per node: **Retry On Fail**, **On Error: Continue / Continue (using error output)**. Use a **Stop and Error** node to fail on purpose (e.g. an invalid request).

## 8. Import / export workflow JSON

- Export: workflow menu **… → Download** (JSON). Import: **… → Import from File / Import from URL**, or paste JSON onto the canvas. *Menu names from memory.*
- Credentials are **not** exported, only referenced by name/ID. After import, reselect them on each node. Hard-coded secrets in node parameters **are** exported, which is another reason to use credentials.
- Commit exported JSON to the repo (`n8n/*.json`) after checking it for secrets. This is our backup and part of the deliverable.

## 9. MCP: letting Claude Code build and edit workflows

There are two different things here:

**a) Instance-level MCP (n8n as an MCP server for Claude)**, which is what we want ([docs](https://docs.n8n.io/connect/connect-to-n8n-mcp-server)):
1. n8n: **Settings → Instance-level MCP → Enable MCP access** (owner/admin).
2. **Connect a client** → tab **OAuth (recommended)** → choose Claude Code. The Server URL ends in `/mcp-server/http`.
3. Terminal ([examples](https://docs.n8n.io/connect/connect-to-n8n-mcp-server/mcp-client-examples.md)):
   ```bash
   claude mcp add --transport http n8n https://<inst>.app.n8n.cloud/mcp-server/http
   ```
   Then run `/mcp` in Claude Code → select **n8n** → complete OAuth. (Alternative: the **API key** tab gives a personal access token plus a config JSON. Generating a new token revokes the old one.)
4. Tools include `search_workflows`, `get_workflow_details`, `search_nodes`, `get_node_types`, `get_workflow_sdk_reference`, `validate_workflow`, `validate_node_config`, `create_workflow_from_code` (and update), `test_workflow` (with pin data), `execute_workflow`, `publish_workflow` / `unpublish_workflow`, `search_workflow_executions`, `get_workflow_execution`, `list_credentials` (secrets never exposed) ([tools reference](https://docs.n8n.io/connect/connect-to-n8n-mcp-server/mcp-server-tools-reference)). Building and editing needs n8n ≥ 2.13, which Cloud should have.
5. For *executing* via MCP, a workflow must be published, have a webhook/form/schedule/chat trigger, and have **Available in MCP** switched on (workflow Settings). Most other tools work on unpublished workflows.
6. Caveats: every connected client sees every MCP-enabled workflow. `create_workflow_from_code` auto-assigns credentials **except for HTTP Request nodes**, so set those by hand. Always open the result in the editor and publish it yourself.
7. Lovable can connect to the same n8n MCP (Lovable workspace **Settings → Integrations → MCP Servers → n8n**). *Nice to have, not needed.*

**b) MCP Server Trigger node:** turns *a workflow* into an MCP server exposing tool nodes to external agents ([docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger)). This isn't needed for building. It could be a pitch extra ("HalloTermin as a tool for any AI assistant").

*(The community `czlonkowski/n8n-mcp` server also exists. It uses the n8n REST API plus an API key. The official instance MCP is simpler now.)*

## 10. HalloTermin workflows (target)

| Workflow | Trigger | Nodes |
|---|---|---|
| **WF1 New request** | Webhook POST `hallotermin-new-request`, Header Auth, Respond Immediately | IF `record.status == 'new'` → Supabase Update `status=briefing` → Basic LLM Chain + Anthropic Chat Model (+ Structured Output Parser) → Supabase Update `brief_de`, `status=calling` → HTTP Request POST relay `/call` {request_id, phone, brief} (error output → Supabase Update `status=failed`) |
| **WF2 Call outcome** | Webhook POST `hallotermin-call-outcome`, Header Auth, Respond via **Respond to Webhook** (200 `{ok:true}`) | Supabase Get request → Supabase Update `status`, `booked_slot`, `outcome` → IF booked → Google Calendar Create + Gmail Send; else Gmail "not booked, here's why" |
| **Error Handler** | Error Trigger | Gmail to team |

**Related:** [[Stack Overview - Lovable n8n Supabase]] · [[Integration Patterns]] · [[Rules/n8n - use production webhook URLs]]
