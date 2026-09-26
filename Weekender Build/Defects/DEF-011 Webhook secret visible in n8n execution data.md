---
type: defect
date: 2026-09-26
status: mitigated
severity: minor
found_in: "[[RUN-013 n8n v2 workflows]]"
owner: abdul
---
# Defect: Webhook secret visible in n8n execution data

## Observed
Saved executions of the Header-Auth webhooks (01 new-request, 05 translate-line, 06 call-result) contain all request headers, including `X-Webhook-Secret` in plain text. Anyone with access to the n8n executions list (or an MCP client reading executions) can read the shared secret.

## Expected
The shared secret is only in Supabase Vault and the n8n credential.

## Repro
Open any production execution of workflow 05 → node "Translate Line Request" → headers.

## Fix
- Done: 05 no longer saves successful executions; 04 saves nothing.
- To do (user, n8n UI): enable execution data redaction for 01/05/06 (workflow settings), or set "Save successful production executions: No" on 01 and 06 after the demo tests.
- Rotate the secret after the event (new value in Vault `n8n_webhook_secret` + the "Header Auth account" credential).

## Mitigation (26.09, Orchestrator)
Workflows 01, 05, 06: `saveDataSuccessExecution = none` → new successful runs no longer store the request (incl. the `X-Webhook-Secret` header); republished. Failed runs are still saved for debugging.
**Still to do:** executions saved before this change still contain the secret → **rotate the secret after the event** (new value in Supabase Vault `n8n_webhook_secret` + n8n credential "Header Auth account"), or delete old executions in n8n.
