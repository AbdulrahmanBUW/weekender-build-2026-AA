---
type: concept
tags: [legal, voice]
sources: ["[[Idea A - HalloTermin (Abdul)]]"]
---
# Legal frame (Germany / EU) — AI disclosure, recording, health data

*General information, not legal advice.*

| Law | What it says | Design consequence | Rule |
|---|---|---|---|
| **EU AI Act Art. 50(1)** (applies since 2 Aug 2026) | People must be told they interact with an AI at first contact | First sentence of every call says "KI-Assistentin" | [[AI discloses itself in first sentence]] |
| **§201 StGB** (confidentiality of the spoken word) | Recording non-public speech without consent is a crime | Never store audio, no Twilio/platform recording; transcript = text only; ask consent to take notes | [[Never store call audio]] |
| **GDPR Art. 9** (health data) | Reason for visit is health data | Collect only a reason *category*, never symptoms; EU endpoints; DPAs with vendors | [[Data minimisation - no symptoms]] |
| Authorization / identity | Agent acts as messenger for a named person | "Ich rufe im Auftrag von …" — never impersonate; explicit in-app consent per call | [[Never impersonate the user]] |

Consent line for transcripts: *"Ist es in Ordnung, wenn ich das Gespräch für meine Nutzerin mitschreibe?"* → if no, keep only a structured summary.

**Pitch angle:** "compliant by design" is a differentiator vs. generic AI call apps.
