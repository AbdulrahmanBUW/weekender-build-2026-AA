---
type: rule
severity: must
source: "Idea A - moment of truth"
---
# Rule: Read-back before booking

**Rule:** Before a booking counts as done, the agent repeats day, date, time and doctor and gets an explicit 'Richtig/Ja' from the practice. Only then set outcome=booked.
**Why:** Prevents hallucinated confirmations — the worst possible failure.
**How to check:** Transcript of every 'booked' run contains a read-back line followed by a confirmation from the practice.

Related: [[AI Disclosure]]
