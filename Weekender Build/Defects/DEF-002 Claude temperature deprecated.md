---
type: defect
date: 2026-09-25
status: fixed
severity: major
found_in: "[[RUN-005 First end-to-end DB to n8n to Claude]]"
owner: claude
---
# Defect: Claude `temperature` deprecated

## Observed
Anthropic 400: "`temperature` is deprecated for this model." (claude-sonnet-5 via n8n Gateway credits)

## Fix
Removed `temperature` from the Anthropic node options. **Rule of thumb:** don't set temperature/top_p/top_k on Claude 5 models.
