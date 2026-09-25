---
type: rule
severity: must
source: "GDPR Art. 9"
---
# Rule: Data minimisation - no symptoms

**Rule:** Collect a reason *category* only (first_visit, checkup, …) — never symptoms or diagnoses. Enforced by the check constraint on call_requests.reason_category.
**Why:** Health data is special-category data; minimal data = minimal risk.
**How to check:** Form has no free-text symptom field; LLM brief never asks for symptoms.

Related: [[AI Disclosure]]
