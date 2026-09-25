---
type: concept
tags: [lovable, stack, tooling]
sources: [https://docs.lovable.dev/integrations/introduction.md, https://docs.lovable.dev/integrations/lovable-mcp-server.md, https://docs.lovable.dev/llms.txt]
---
# Lovable Connectors — what we use (and what we skip)

Lovable has **three kinds** of connectors (catalog: `lovable.dev/dashboard?connectors`):
| Kind | Who uses it | Example |
|---|---|---|
| **App + chat connector** | the *published app* at runtime (one shared account) + Lovable while building | Supabase, Twilio, ElevenLabs, Resend, Google Maps |
| **Chat connector (MCP)** | only Lovable's agent while you build (personal) | Notion, Linear, custom MCP |
| **App user connector** | each end user links their own account | Gmail, Salesforce |

Plus the reverse direction: **Lovable MCP server** (`https://mcp.lovable.dev`, OAuth, all plans) lets *our Claude* drive Lovable — list/deploy projects, send prompts to the Lovable agent, read files/diffs, manage project Knowledge. Registered in repo `.mcp.json` as `lovable`.

## Connect now (must)
| Connector | Why | Where |
|---|---|---|
| **Supabase** | our backend: project `weekender-build` (ycyrtlzympxzlfcocazh). **Not** Lovable Cloud → [[Decide Lovable backend before first prompt]] | Project → Integrations → Supabase → Connect |
| **GitHub** | code sync; Lovable creates its own repo → link it in README | Project → Integrations → GitHub |

## Connect when the matching feature is built (nice to have)
| Connector | Use in HalloTermin | Note |
|---|---|---|
| **ElevenLabs** (app) | Voice fallback A in [[DEC-001 Voice platform (proposed)]]; also TTS "hear the German opening" button on the landing page | needs ElevenLabs account |
| **Twilio** (app) | voice calls / SMS confirmation | trial limits → [[Telephony Constraints (Twilio Trial, Numbers)]] |
| **Google Maps Platform** (app) | practice search/autocomplete + map on the request form (managed connection available) | nice demo polish |
| **Built-in AI connector** | in-app translation / summaries without API keys | only if n8n isn't doing it |
| **Custom MCP chat connector → our n8n** | lets Lovable's agent see our n8n workflows while building | URL `https://arahmandeaxo.app.n8n.cloud/mcp-server/http` + own n8n token |

## Skip (n8n already does it / out of scope)
Resend, Brevo, Mailgun (email is sent by n8n) · WhatsApp/Telegram (v2) · CRM, data-warehouse, accounting connectors.

**Rule of thumb:** backend logic and side effects (email, calendar, calls) live in **n8n**; Lovable connectors only for things the UI must do directly.
