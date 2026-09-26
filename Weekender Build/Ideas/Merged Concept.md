---
status: proposed
owners: [abdul, anastasia]
date: 2026-09-26
sources: ["[[Idea A - HalloTermin (Abdul)]]", "[[Idea B - Dies-Das-Ana-Nas]]", "[[Frontend and UX Plan v2]]"]
---
# Merged Concept — "Find it. We call for you."

> Visual overview for both of us: `docs/merged-concept.html` in the repo (open in a browser) · shared page https://claude.ai/artifact/UrzS6XF7vy5qNKtbKTXvQT (private until Abdul shares it). Decision to confirm: [[DEC-003 Merged concept (proposed)]].

## Idea A in one line (Abdul — HalloTermin)
Newcomers tell an AI assistant in their own language what they need; it **phones German offices, practices and shops for them**, honestly says it is an AI, and returns the result in their language.

## Idea B in one line (Anastasia — Dresden mit Kind)
The place expat **parents** open in their first year in Dresden: **events, courses, bilingual communities and an experience library**, in 11 languages, later with provider self-service and reviews.

## Overlap / what combines
| Common ground | A has | B has |
|---|---|---|
| Users | newcomers with little German (Priya, Amina, Marco) | international parents 0–3 years in Dresden (Maria, Ahmed) |
| City | Dresden | Dresden |
| Languages | 12 input languages, UI EN/AR/TR/UK | 11 launch languages incl. DE, RU, AR (RTL) |
| Data | 84 verified places (doctors, pharmacies, banks, Ausländerbehörde, community) + 4 guides in AR/TR/UK | providers, events, communities, places, articles (to be seeded) |
| Stack | Supabase EU + RLS, n8n, Lovable | Supabase EU + RLS, Next.js/Tailwind/shadcn |
| Values | GDPR, minimal data, honest AI, plain B1 language, mobile-first, WCAG | GDPR, no child data, plain language, mobile-first, WCAG 2.1 AA |
| The pain | German-only systems; phone-first, stressful calls | information scattered in German sites and chat groups |

**The gap each fills for the other:**
- B without A: parents *find* a Kinderarzt, a Kita or a music course… and then must **call in German** (waiting lists, trial classes, free spots). That's where they get stuck.
- A without B: the assistant can call — but **who** to call? B's curated directory and guides answer that.

## Merged problem statement
*When I'm a new international parent in Dresden, I want to find the right doctor, Kita, course or community for my child **and** have someone ask them in German for me, so that my family settles in without me fighting German websites and phone calls.*

## One solution: the loop
**Discover → Understand → Act → Result**
1. **Discover** (B): home with pillars — Courses & activities · Events · Bilingual communities · Health & services (A's doctors/pharmacies) · Library.
2. **Understand** (B + A): guides/articles in the parent's language (Kita registration, school enrolment, Anmeldung, bank account, health insurance, Ausländerbehörde).
3. **Act** (A): on every provider profile and guide: **"Ask for me"** → prefilled task (e.g. "Is there a free spot / trial class for a 4-year-old on Tuesdays?", "Put us on the Kita waiting list", "Book a U-Untersuchung at the Kinderarzt") → approval card → German call.
4. **Result** (A): answer in the parent's language, "add to calendar", saved to the provider page as "last checked by phone on …" (keeps B's listings fresh — solves B's "stale data" pain).

## MVP scope for Sunday 14:00
- **In (Must):**
  - Home with the pillars + "What do you need?" box (A's intake).
  - Directory + filters (child age, category, language of instruction, district) — `resources` extended for kids providers; ~40–60 seeded Dresden family providers/places + our 84 service places.
  - Provider profile page (description, languages, ages, contact, map link) with **"Ask for me"**.
  - Events: ~10 upcoming family events (seeded by crawler, "verify" label).
  - Library: 4 existing guides + **Kita place** + **school enrolment** guides.
  - Call flow: intake → approval → live call with subtitles → result (already built backend).
  - UI languages for the demo: EN, DE, RU, UK, AR (RTL), TR; content languages: B's 11 ∪ A's 12 (13 codes).
- **Should:** "Suggest a place" form (→ admin queue table), bilingual communities filter by language, "last checked by phone" badge.
- **Out (B's Phase 2–4, A's later):** parent/provider accounts, reviews & ratings, provider self-service/claim flow, newsletter, payments, real phone line (Twilio), hosting the relay publicly.

## Division of work
| Anastasia | Abdul (+ agents) |
|---|---|
| Name/brand decision, curation of seed providers & communities (her network), articles Kita/school, RU/UK translation review, UI in Lovable with the Designer prompts, pitch + receptionist role-play | DB migration (kids fields, events, suggestions, 2 new task types), crawler jobs for family providers/events, call templates `course_enquiry` + `kita_enquiry`, intake prefill, n8n/relay, deploy, demo backup video |

## Open questions
1. Name: "Dresden mit Kind" (her brand) with "Ask for me" powered by HalloTermin — or one new name? (Proposal: keep **Dresden mit Kind** as the product, **"Ask for me"** as the feature.)
2. Focus families only, or families first + "Newcomer services" pillar for everyone? (Proposal: families first; services pillar keeps A's doctor/pharmacy/Ausländerbehörde use cases.)
3. Which UI languages must be fully translated by Sunday (proposal: EN, DE, RU, UK, AR, TR)?
4. Who reviews RU/UK/AR translations (Anastasia's communities)?
