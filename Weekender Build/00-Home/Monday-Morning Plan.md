# Monday-Morning Plan
What do we need so the build becomes something real?

> **Product:** **Dresden mit Kind** is the family hub. Parents find courses, events, bilingual communities, doctors and guides. **"Ask for me"** is the calling feature (powered by HalloTermin): an AI phones the provider in German and gives the answer in the parent's language. Decided in [[DEC-003 Merged concept]], explained in [[Merged Concept]].
> **Founders:** Anastasia (brand, content, communities, translations, UI) and Abdul (backend, security, calls, n8n, hosting).
> Legal points are general information, not legal advice. Costs come from our research notes. Nothing here is measured with real users yet.

## What exists after Sunday
*(After the demo: tick what really shipped and remove the rest.)*
- **Lovable app** at the live URL from Sunday: home with the pillars (Courses & activities, Events, Bilingual communities, Health & services, Library), directory with filters, provider profile with **"Ask for me"**. UI in EN, DE, RU, UK, AR (right-to-left) and TR.
- **Supabase (Frankfurt):** schema in `supabase/migrations/`, including the merge migration `20260926200000_merged_family_hub.sql`: family fields on `resources`, `family_events`, `suggestions`, task types `course_enquiry` + `kita_enquiry`, and the **"checked by phone"** trigger (`last_checked_at`, `last_check_outcome`). RLS for the call tables is still in **demo mode** (see [[Data Model]]).
- **Content:** 84 checked Dresden service places (doctors, pharmacies, banks, Ausländerbehörde, community) and guides (bank account, Anmeldung, Ausländerbehörde, health insurance; Kita place and school enrolment planned for Sunday). Family providers and events are seeded for the demo. Crawled events carry a "verify" label.
- **n8n Cloud:** 01 call brief, 02 resource crawler, 04 intake, 05 translate line, 06 result in the user's language. Exports are in `n8n/workflows/`. Claude, Brave and Firecrawl run on **n8n Gateway credits**, so they depend on the n8n Cloud account.
- **Voice relay** (`services/voice-relay`): Deepgram Voice Agent speaks German, live subtitles, results go to Supabase. It runs **on a laptop only**, as a browser call. **No real phone line yet.**
- **Security:** focused review done (`docs/security/security-review-2026-09-26.md`). Both medium findings are fixed. The open items are listed under Risks.
- **Open defect:** [[DEF-011 Webhook secret visible in n8n execution data]] (mitigated, but the secret must be rotated).
- **Not built:** parent and provider accounts, provider self-service, reviews, newsletter, payments, real phone calls, public relay, Impressum and privacy pages, and 5 of Anastasia's 11 launch languages (HI, ZH, PL, VI, ES).

## Next 7 days
Goal of the week: **a site that is safe and legal to share with the first real parents**, and **one real "Ask for me" call with consent** to one friendly provider.

**Both — Monday morning**
1. **Retro and split** (Mon). Write a short decision note in `Decisions/`: what we keep from the demo, who owns what, which pillar we share first. Answer the open questions from [[Idea B - Dies-Das-Ana-Nas]]: domain (Q1), which article categories must be fully translated (Q2), who writes articles and events (Q4), what happens to the Tilda catalog (Q5). Monetisation (Q3) and "reviews with or without account" (Q6) can wait for Phase 3–4.

**Anastasia — content, trust, partners**
2. **Legal basics for a public site** (Mon–Wed). Impressum and Datenschutzerklärung (privacy policy) linked on every page. Write down which personal data we collect ("Ask for me" requests, suggestion form) and why. Use cookieless analytics only (e.g. Plausible or Umami), so we need no cookie banner.
3. **Translation review by native speakers** (Mon–Fri). Reviewers from her communities check RU, UK and AR: UI strings (`docs/i18n/ui-strings.json`), taxonomy labels, and the Kita and school guides. TR comes next. Mark each language as "reviewed by a native speaker"; unreviewed text shows a notice. No new language goes live without a review. Then plan HI, ZH, PL, VI, ES (AI draft + native review).
4. **Data freshness** (Tue–Fri). Every provider and event shows when it was last checked. The **"checked by phone"** badge comes from "Ask for me" results (the trigger already exists). Every article shows "last updated". Add a "Report outdated info" link that writes into the `suggestions` queue. Check all seeded providers and events once by hand.
5. **Partner emails** (Wed–Thu, see Who / partners) with the demo video and a one-page summary.
6. **Interviews** (any day): 8–10 international parents and 5 providers (the numbers from her PRD). Ask parents: would you let an AI call for you? Ask providers: would you update your own profile? (This tests PRD assumption A2.)

**Abdul — safety, calls, infrastructure**
7. **Rotate the webhook secret** (Mon, DEF-011). New value in Supabase Vault `n8n_webhook_secret` and in the n8n credential "Header Auth account". Delete old executions. Send one POST without the header and expect 403 (security review, "needs validation" #1). Also pin the `n8n-mcp` version in `.mcp.json` (finding F4).
8. **Auth and owner RLS instead of demo RLS** (Mon–Tue). Supabase Auth with email magic link. New migration only: `user_id` on `call_requests`, owner policies on `call_requests`, `calls`, `transcript_lines`, `events`; no anon read; remove `events` from Realtime. Test as anon and as a second user ([[RLS - test inserts as anon]]). Delete demo rows in production. Plan the PRD roles now (`parent`, `provider`, `editor`, `admin`), so Phase 2 needs no rewrite.
9. **Stop abuse and extra cost** (Tue–Wed). Every "Ask for me" request costs n8n and Claude work. Add a rate limit (and CAPTCHA) in front of inserts into `call_requests` and `suggestions`, for example with an Edge Function. Add length limits on text fields. Render guides with a sanitising markdown renderer (no raw HTML, only `https:` links). Remove names from relay logs (F5). Set a retention rule for `transcript_lines` and `events`.
10. **DPAs and EU endpoints** (Mon–Wed). Accept the data processing agreements (GDPR Art. 28) with **Supabase, n8n, Deepgram and Anthropic** (plus Lovable and Twilio if they touch personal data). Switch the relay to the Deepgram EU endpoint. Decide: Claude through n8n Gateway credits, or our own Anthropic key (the contract is different). Write a short record of processing.
11. **German +49 number and regulatory bundle** (start Mon; Twilio reviews in 2–3 business days). Upgrade Twilio, submit business registration + address proof, buy a German local number, enable Germany in the geo permissions. Until then: Verified Caller ID ([[Telephony Constraints (Twilio Trial, Numbers)]]).
12. **Public relay hosting** (Wed–Thu). Docker on Render or similar ([[Relay Hosting Options]]), Twilio Media Streams → relay → Deepgram. Before the relay leaves the laptop: a short-lived signed token per call (F1), calls only to verified provider numbers, and user fields fenced as data in the agent prompt (security must-fix #6). No recording ([[Never store call audio]]).
13. **Legal check of real-time transcription** (book Mon, answer by Fri). One lawyer or university legal clinic, one clear question: live transcription with a consent line and no stored audio — does it fit **§201 StGB**? Also ask about AI Act Art. 50 (the AI says it is an AI, see [[AI discloses itself in first sentence]]) and GDPR Art. 9 (a Kinderarzt call is health data about a child). Until the answer: only a structured summary on real calls, no stored transcript.
14. **One real call with consent** (Fri, if steps 11–12 work). One course provider or Kita from Anastasia's network agrees in advance. One call, one clear answer, and the provider page shows "checked by phone". Write it up in `Runs/`.

**Friday, both:** handoff note in `Memory/`, update the board, commit.

## Who / partners
| Who | Why | First step | Owner |
|---|---|---|---|
| **TU Dresden International Office** | Many international students and staff, some with families; B2B2C channel | Email with the demo video; ask for a 20-min meeting and 10–20 test families | Abdul |
| **Welcome Center Dresden** (city welcome service, welcome@dresden.de) | Already helps newcomers; knows the questions families ask | Ask for feedback and whether they can point clients to the site | Anastasia |
| **Kita-Eigenbetrieb** (city-run Kitas) | Kita places are a big pain for parents; our Kita guide and `kita_enquiry` calls must match the real process | Ask them to check the Kita guide; ask if AI calls for parents are OK for them or if they prefer another channel | Anastasia |
| **Bilingual communities** (Anastasia's network) | Content, trust, first users, and the native-speaker reviewers | Ask for one reviewer per language and 2–3 providers each | Anastasia |
| **Impact Hub "Business, Baby!"** | Mentoring for founders with children (PRD Q7) | Ask whether it fits our timeline and business-model questions | Anastasia |
| **Providers** (teachers, studios, language schools) | Phase 2 only works if providers update their own profiles | 5 interviews; ask 2–3 to test the claim flow first | Anastasia |
| **Employers hiring skilled workers** (e.g. semiconductor companies, via HR / relocation) | Could pay for it as a relocation benefit | One HR contact after the first pilot | Abdul |
| **One friendly provider or Kinderarzt** | Real call test with consent | Personal contact; ask before calling | Both |
| **Lawyer / legal clinic** (IT, criminal and consumer law) | §201 StGB, AI Act, GDPR, DSA, review rules | Book one consultation; send the questions in writing first | Abdul |

## Risks & blockers
| Risk | Why it matters | What we do |
|---|---|---|
| **Demo RLS still on** | Anyone with the anon key can read call requests (names, emails, phone numbers) | Step 8 before the first real user; no real data before that |
| **Abuse and cost** | Anonymous inserts start paid Claude work; the suggestion form can get spam | Step 9: rate limit, CAPTCHA, length limits |
| **Webhook secret in old n8n executions** (DEF-011) | Anyone with n8n access can read it and call our webhooks | Rotate on Monday (step 7) |
| **§201 StGB unclear** for real-time transcription | Lawyers disagree; worst case it is a crime | No audio ever; consent line in the call; summary only until the legal answer |
| **No German +49 number** without a registered business and address | A +1 caller ID gets fewer answers; the review takes days | Start the bundle on Monday; Verified Caller ID until then |
| **Public relay without auth** | Anyone could start calls on our Deepgram quota or call any number | Signed token per call, verified numbers only, concurrency cap (already in the code) |
| **Child data vs. "Ask for me"** | The PRD says "no data about children", but a Kita or Kinderarzt call needs the child's age and sometimes name and birth date (health data = GDPR Art. 9) | Ask only what the call needs; age instead of birth date where possible; delete personal fields after the result ([[Data minimisation - no symptoms]]) |
| **Platform legal duties** | Missing Impressum or unclear rules can bring warnings (Abmahnung) and fines | Impressum + privacy policy before we share the link. Before any user content (Phase 2–3): DSA notice-and-action (report button, statement of reasons when we remove something). Phase 2: providers confirm they have consent for photos of children. Phase 3: explain how reviews are checked (EU review rules). Phase 4: newsletter only with double opt-in |
| **Bad or unreviewed translations** | Wrong Kita deadlines or office info hurts families and trust | Native-speaker review; notice on unreviewed text; official German names kept with an explanation |
| **Stale data** | Parents ask about closed courses; trust drops | "Checked by phone" badge, "last updated" dates, report link, "verify" label on crawled events, re-check listings not updated in 90 days (PRD metric) |
| **Cold start** | Empty reviews and empty provider pages reduce trust (PRD) | Keep Anastasia's order: curated guide first, self-service in Phase 2, reviews in Phase 3 |
| **Providers or Kitas refuse AI calls or hang up** | Core value of "Ask for me" fails | Polite disclosure, read-back of the answer, "connect the parent" fallback; ask the Kita-Eigenbetrieb early |
| **Misheard names, Saxon dialect** | Wrong result | Keyterm prompting, spelling ("P wie Paula"), never invent names ([[DEF-009 Agent invents names from misheard words]], [[RUN-008 Deepgram German round trip]]) |
| **Trial accounts expire** (below) | Live URL, workflows and AI calls stop | Decide keep / pay / move before the dates |
| **Two founders, many tracks** | Nothing gets finished | One goal per week, board status, Friday handoff |

## Cost / accounts to keep
**Per-call cost for "Ask for me" (from our research, not measured yet):**
- Deepgram Voice Agent: **$0.05–0.16 per minute** (depends on tier). New accounts get $200 free credit.
- Twilio → German mobile $0.042/min, landline $0.0283/min. German local number $1.35/month.
- Claude for brief, intake and translation: small per request. We measure it on the first real calls instead of guessing.
- Rough rule from [[Idea A - HalloTermin (Abdul)]]: a 3-minute call is well under €1 including Twilio. We log real minutes per call in `calls` to confirm.
- Platform plans (Lovable, n8n, Supabase paid): check the price pages before the deadlines below. We do not guess numbers here.

**Accounts and what expires:**
| Account | Status after the event | Action |
|---|---|---|
| **n8n Cloud** | Trial, **about 1 month** from sign-up (check the exact date on the billing page) | **Claude, Brave and Firecrawl run on its Gateway credits, so they stop too.** Before the end: pay, or self-host (`n8n-self-hosting` skill) with our own API keys. Workflows are exported in `n8n/workflows/` |
| **Lovable** | Event credits, **about 30 days after the event** | Decide: paid plan, or keep the GitHub-synced code and host it elsewhere (the PRD prefers an EU host) |
| **Twilio** | Trial ends after 30 days; calls only to verified numbers | Upgrade (needed anyway for the +49 number) |
| **Deepgram** | $200 free credit | Keep; watch usage; use the EU endpoint |
| **Anthropic** | Today only through n8n Gateway and Deepgram "think" | Own API key + DPA if we leave the Gateway |
| **Supabase** (Frankfurt) | Free tier | Keep; move to paid before real users if we need backups |
| **Retell** | $10 free credit, not used by the build | Let it expire unless [[DEC-001 Voice platform (proposed)]] changes |
| **Domain + Tilda site** (Anastasia) | Exists outside this repo | Decide if the domain points to the new app (PRD Q1, Q5) |
| **GitHub repo + board** | Free | Keep |

Set a reminder one week before each end date. One person owns each paid account; card and invoices in a shared place. Secrets stay in env vars and Vault ([[No secrets in repo]]).

## 30 / 60 / 90 days
- **30 days — Phase 1 done: curated guide, live and safe.** Impressum + privacy policy, auth + owner RLS, DPAs signed, secret rotated, rate limits on. RU, UK, AR and TR reviewed by native speakers. First "checked by phone" badges. +49 number, relay hosted, legal answer on §201. 5–10 consented real calls. One pilot partner agreed. Decision on n8n and Lovable made before they expire. Content towards Anastasia's Phase 1 target (about 60–100 providers/places, 10–15 articles, events for the next 4 weeks — her assumption in the PRD).
- **60 days — Phase 2: provider self-service.** Claim flow with verification and admin approval; providers edit only their own profile (enforced with RLS); providers publish classes and events; iCal export; parent accounts and favourites. Consent checkbox for photos of children. DSA notice-and-action ready before any user content goes live. Pilot with 10–20 families from one partner. Measure: returning visitors, contact clicks, "Ask for me" results (answered / needs parent / refused) and cost per answered call. Next languages (HI, ZH, PL, VI, ES) only after native review.
- **90 days — Phase 3: reviews with moderation, and the money question.** Reviews only from logged-in parents, one per parent per provider, one public provider reply, report button, moderation queue, clear note on how reviews are checked, no children named. Decide monetisation (PRD Q3, start of Phase 4): free, freemium or featured listings / provider subscriptions for providers; B2B2C for "Ask for me" through TU Dresden, employers and the Welcome Center, with a per-call option for parents. Newsletter with double opt-in. Go / no-go on the real numbers.
