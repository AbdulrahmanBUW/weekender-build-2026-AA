---
type: rule
severity: must
source: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/
---
# Rule: n8n - use production webhook URLs and publish

**Rule:** Anything outside the n8n editor (the Supabase DB webhook, the relay server, the Lovable app) calls the **production** URL `https://<inst>.app.n8n.cloud/webhook/<path>`, never `/webhook-test/<path>`. After every change you want live, click **Publish** (n8n 2.x replaced the "Active" toggle with Publish).
**Why:** The test URL only listens while someone clicks "Listen for Test Event" in the editor, and it catches one request. Production URLs exist only for published workflows, and otherwise return `404 webhook is not registered` ([docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/), [publish docs](https://docs.n8n.io/build/understand-workflows/save-and-publish-workflows)). This is the most common "it worked yesterday" demo failure.
**How to check:** `curl -X POST https://<inst>.app.n8n.cloud/webhook/<path> -H "X-Webhook-Secret: …" -d '{}'` with the editor closed → a new entry appears in the **Executions** tab. In Supabase: `select status_code from net._http_response order by id desc limit 5;` should show 200s, not 404s.
