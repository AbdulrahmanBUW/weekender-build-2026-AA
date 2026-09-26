---
type: defect
date: 2026-09-26
status: fixed
severity: minor
found_in: "[[RUN-007 Newcomer crawler first run]]"
owner: claude
---
# Defect: URL global missing in n8n Code node

## Observed
In the pinned test, *Pick Official URLs* returned only the "skip" item, so no page was scraped and no guide was written. The execution still showed **success**.

## Expected
dresden.de links from the Brave web results are picked.

## Repro
Code node (JavaScript, n8n Cloud task runner): `try { host = new URL(r.url).hostname } catch (e) { continue; }` → every URL is skipped. The same code works in local Node.js. `URL` seems not to be available in the Code node sandbox, and the `try/catch` hid the error.

## Fix
Parse the host with a regex instead: `String(r.url).match(/^https?:\/\/([^\/?#:]+)/i)`. Rule of thumb: in n8n Code nodes, avoid browser/Node globals like `URL`, and never wrap them in a silent `catch`.
