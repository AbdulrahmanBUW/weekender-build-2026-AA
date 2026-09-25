---
type: rule
severity: must
source: "Idea A - job stories"
---
# Rule: Only book inside pre-approved windows

**Rule:** The agent may only accept slots inside call_requests.time_windows; anything else → offer alternatives or outcome needs_user.
**Why:** The user authorised those windows, nothing else.
**How to check:** Test run with receptionist offering an out-of-window slot.

Related: [[AI Disclosure]]
