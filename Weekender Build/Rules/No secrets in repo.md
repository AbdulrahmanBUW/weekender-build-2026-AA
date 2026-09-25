---
type: rule
severity: must
---
# Rule: No secrets in the repo

**Rule:** API keys, tokens, phone numbers live in `.env` (gitignored), Lovable/Supabase Secrets or n8n credentials — never in notes or commits.
**Why:** Repo is shared; a leaked key can burn credits or data.
**How to check:** `git diff --cached` before each commit.
