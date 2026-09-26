---
type: decision
date: 2026-09-26
status: proposed
deciders: [abdul, anastasia]
---
# Decision: Merged concept — "Find it. We call for you."

## Context
Idea A (HalloTermin: AI calls in German for newcomers, any task, 12 languages — backend v2 live) and Idea B (Dresden mit Kind: multilingual guide + directory for international parents — PRD v0.2) target the same people in the same city with the same values and stack. Build deadline: Sun 27.09, 14:00.

## Options
1. **Family-first hub with "Ask for me"** — Dresden mit Kind is the product (Discover/Understand), HalloTermin is the action button on every provider and guide (Act/Result). Doctor/pharmacy/Ausländerbehörde stay as a "Health & services" pillar.
2. **Newcomer-general assistant with a family section** — HalloTermin stays the product; B's directory becomes one section.
3. **Two products, shared backend** — build both separately; split the demo.

## Decision (proposed)
**Option 1.** It gives the clearest story ("find it, we call for you"), uses B's content and A's working backend, keeps both founders' visions, and fixes each idea's weak spot (B: parents stuck at the phone call; A: who to call). Option 3 splits a 2-person team 24 h before the demo.

## Consequences
- DB: extend `resources` for family providers (age range, categories, price type, format, description + i18n), add `events` and `suggestions`, add task types `course_enquiry` and `kita_enquiry` (see [[Task Types - How to extend]]).
- UI: [[Frontend and UX Plan v2]] stays the design base; routes add `/courses`, `/events`, `/communities`, `/p/:id` provider profile; intake gets "prefill from provider".
- Accounts, reviews, provider self-service: B's Phase 2–3, not for Sunday.
- Name/brand: to confirm with Anastasia (proposal: "Dresden mit Kind", feature "Ask for me").
