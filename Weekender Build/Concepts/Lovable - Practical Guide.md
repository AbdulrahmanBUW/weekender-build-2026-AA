---
type: concept
tags: [stack, lovable]
sources: [https://docs.lovable.dev/integrations/supabase, https://docs.lovable.dev/integrations/cloud, https://supabase.com/docs/guides/troubleshooting/cant-access-supabase-project-lovable-cloud, https://docs.lovable.dev/integrations/github, https://docs.lovable.dev/introduction/credits-and-usage, https://lovable.dev/pricing, https://docs.lovable.dev/features/publish, https://docs.lovable.dev/features/collaboration, https://docs.lovable.dev/features/knowledge, https://docs.lovable.dev/tips-tricks/external-deployment-hosting, https://lovable.dev/faq/ai-agent/plan-mode]
---
# Lovable: Practical Guide (Sept 2026)

**Definition:** Lovable is an AI app builder. You describe features in chat, and it writes a React app, runs it in a preview and publishes it to a `lovable.app` URL. It has a backend layer, either **Lovable Cloud** (managed Supabase) or **your own Supabase project**.

**Why it matters for us:** It is deliverable 1 (the live URL). It is also where credits burn fastest, so we should use it deliberately.

## 1. Backend: Lovable Cloud vs own Supabase

| | Lovable Cloud (default) | Own Supabase (connected) |
|---|---|---|
| Setup | Zero; enabled by default ([docs](https://docs.lovable.dev/integrations/cloud)) | Create a project at supabase.com, then connect it in Lovable |
| Billing | Lovable Cloud credits (Pro: 20 Cloud credits/month included, per [pricing](https://lovable.dev/pricing)) | Supabase free tier (2 active projects, 500 MB DB) |
| Region | Americas / Europe / APAC; **can't be changed later** ([docs](https://docs.lovable.dev/integrations/cloud)) | Choose `eu-central-1` (Frankfurt) |
| DB access | The Cloud tab has a table editor, an **SQL editor**, logs and secrets inside Lovable ([docs](https://docs.lovable.dev/integrations/cloud)) | Full Supabase Dashboard, SQL editor, logs, connection string |
| **Service/secret key** | **Not available.** "These credentials are withheld for Cloud-managed projects"; the project isn't shown in your Supabase dashboard ([Supabase troubleshooting](https://supabase.com/docs/guides/troubleshooting/cant-access-supabase-project-lovable-cloud)) | Yes: Project Settings → API Keys → secret key (`sb_secret_…`) |
| External tools (n8n Supabase node, relay server) | No direct DB/secret access, so you need an Edge Function as a proxy | Direct: n8n Supabase credential = Host + Secret Key |
| Teammate access | Only through the Lovable project | Invite them to the Supabase org too |
| Migration | **No one-click migration** in either direction. Once Cloud is enabled "it cannot be disconnected or switched"; you have to rebuild or migrate data manually ([Lovable](https://docs.lovable.dev/integrations/supabase), [Supabase](https://supabase.com/docs/guides/troubleshooting/cant-access-supabase-project-lovable-cloud)) | You own it, so it survives beyond Lovable |

**Recommendation for us:** use your own Supabase and connect it **before the first backend prompt**. See [[DEC-002 Backend and integration pattern (proposed)]] and [[Rules/Decide Lovable backend before first prompt]].

**How to connect** ([docs](https://docs.lovable.dev/integrations/supabase)):
- Workspace admin, one time: **Connectors → Supabase → Connect Supabase** (OAuth to your Supabase org). Or, from the dashboard prompt box: **+ → Databases → Add Supabase organization**.
- In the project editor: **More → Cloud → "Already have a Supabase project? Connect it here"** → pick the project → check that the project name is shown.
- Check which backend you're on: the Cloud icon in the top bar shows either Lovable's own menu (Cloud) or the Supabase logo and project name (own) ([Supabase docs](https://supabase.com/docs/guides/troubleshooting/identify-lovable-cloud-or-supabase-backend)).
- Limits: one Lovable project ↔ one Supabase project. With your own Supabase, some Lovable-managed features (auth configuration in Lovable, branded Cloud emails) aren't available ([docs](https://docs.lovable.dev/integrations/supabase)). We don't need them.

With a connected Supabase project, Lovable still designs the schema, **shows each migration for approval** and then runs it, and deploys Edge Functions from chat ([docs](https://docs.lovable.dev/integrations/supabase)).

## 2. GitHub sync

- Official docs: when you connect, **"Lovable creates a new GitHub repository."** Importing an existing repo isn't supported ([docs](https://docs.lovable.dev/integrations/github)). Some third-party guides say you can link an existing repo. *Unverified; assume a new repo.*
- **Syncing into a subfolder or monorepo isn't documented.** Assume the Lovable repo root is the app. Keep our vault/docs repo separate, and link to the Lovable repo from it (or add it as a git submodule if you really need to).
- Two-way sync on **one branch** (default `main`). Every Lovable prompt becomes a commit, and commits pushed to `main` flow back into Lovable ([docs](https://docs.lovable.dev/integrations/github)).
- Renaming the repo is fine. Deleting it breaks the sync.
- Setup: **Settings → Connectors → GitHub** (OAuth) → install the Lovable GitHub App on your account/org → **Connect project**.
- Available on all plans for github.com ([docs](https://docs.lovable.dev/integrations/github)).
- Use: the mandatory repos (security-audit, archify, brag) can run against this repo locally. Put their output in `docs/` folders, which Lovable won't touch (*assumption: Lovable only rewrites files it generates; commit and pull often*).

## 3. Secrets and Edge Functions

- **Secrets** (Cloud tab → Secrets, or Supabase Edge Function secrets) are for server-side keys only: Twilio, Deepgram, the n8n webhook secret. They are readable only inside Edge Functions via `Deno.env.get('NAME')`.
- `VITE_*` variables (e.g. `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`) are **baked into the public JS bundle**. Only publishable/anon keys belong there ([external hosting doc](https://docs.lovable.dev/tips-tricks/external-deployment-hosting)). See [[Rules/Never put service keys in frontend]].
- Edge Functions = Supabase Edge Functions (Deno). Use them only if we need a server-side step that n8n can't do. With pattern (a) in [[Integration Patterns]], we don't.

## 4. Publishing, URL, domains

- Click **Publish** (top right) → choose the subdomain → the app goes live at `https://<name>.lovable.app` ([docs](https://docs.lovable.dev/features/publish)).
- **Publishing is a snapshot.** After later edits, click **Publish → Publish changes** again. A dot on the Publish button means there are unpublished changes. *Common demo-day mistake: the demo URL shows an old version.*
- The Publish dialog runs a quick **security scan** (DB rules, exposure). It doesn't block publishing. Read it anyway.
- Visibility on Pro: "Anyone with the link can visit" ([docs](https://docs.lovable.dev/features/publish)).
- Custom domain: the pricing page lists custom domains for paid plans, but the publish docs say Business/Enterprise. **Conflicting sources; not needed**, because `<name>.lovable.app` counts as "own URL".

## 5. Collaboration (2 people)

- **Invite to a project:** **Share** in the editor → email → role Editor. Their prompts **use the owner's workspace credits** ([docs](https://docs.lovable.dev/features/collaboration)).
- **Invite to the workspace:** **Settings → People**. Credits are shared, and admins can set per-person credit limits ([pricing](https://lovable.dev/pricing)).
- **Drafts:** each collaborator works in their own draft (own chat and preview), which merges only when someone accepts it. Agree who accepts drafts, and don't edit the same screen at the same time.

## 6. Credits: how far 100 go

- Agent (build) messages cost about **0.5–2 credits** depending on size. **Plan mode = 1 credit** per message (plus any research subagents). Chat-mode questions typically cost a fraction ([credits doc](https://docs.lovable.dev/introduction/credits-and-usage), [plan mode FAQ](https://lovable.dev/faq/ai-agent/plan-mode)).
- Pro also gives **5 daily build credits** (expire daily) and 20 Cloud credits/month ([pricing](https://lovable.dev/pricing)).
- Rough budget: 100 credits ≈ **60–120 build prompts**. Enough for the HalloTermin UI (landing, form, live call view, result card) *if* prompts are batched.
- **Saving tips:**
  1. Write one big, specific first prompt (screens, fields, table names, colours) instead of 20 small ones.
  2. Use **Plan mode** to agree on the approach, then send one build prompt.
  3. Put the schema, naming and "don't touch" rules in **Knowledge** (below) so you don't have to repeat them.
  4. For small text or CSS edits, edit the code directly (Code mode, or in GitHub/VS Code and push). It costs nothing.
  5. Don't ask Lovable to "fix" things in a loop. After two failed attempts, read the error yourself or ask Claude Code on the synced repo.
  6. Create tables with SQL in the Supabase SQL editor (free) and tell Lovable they exist.

## 7. Knowledge (project instructions)

- **Project knowledge** and **workspace knowledge**, each up to **10,000 characters**. Bullet rules work best ([docs](https://docs.lovable.dev/features/knowledge)). Lovable also reads `AGENTS.md` / `CLAUDE.md` in the repo ([docs](https://docs.lovable.dev/features/knowledge)).
- Suggested content for HalloTermin: purpose (1 line); tables and columns (`call_requests`, `call_events`); "use Supabase Realtime for status and transcript; never call n8n from the browser"; "never put secret keys in code"; the UI language is English; "don't change files under `docs/`".

## 8. Hosting elsewhere (fallback)

Export via GitHub, then deploy the Vite app on Vercel: framework preset Vite, `npm run build`, output `dist`, set `VITE_SUPABASE_*` env vars, and add an SPA rewrite to `/index.html` ([Lovable docs](https://docs.lovable.dev/tips-tricks/external-deployment-hosting)). Some newer Lovable projects may use TanStack Start instead of plain Vite. *Unverified; check `package.json`.*

**Related:** [[Stack Overview - Lovable n8n Supabase]] · [[Supabase - Practical Guide]] · [[Integration Patterns]]
