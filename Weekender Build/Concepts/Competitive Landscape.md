---
type: concept
tags: [market, pitch]
sources:
  - https://techcrunch.com/2026/09/24/google-tests-letting-gemini-make-phone-calls-initially-for-us-pixel-owners/
  - https://blog.google/products-and-platforms/products/shopping/how-to-agentic-calling-let-google-call/
  - https://www.jobnimbus.com/blog/google-ai-calling-home-services
  - https://apps.apple.com/us/app/leximo-ai-call-agent/id6756414772
  - https://leximo.ai/en
  - https://aihaggler.com/
  - https://tech.eu/2026/07/23/telli-secures-15m-seed-to-automate-customer-facing-operations/
  - https://techcrunch.com/2026/01/15/parloa-triples-its-valuation-in-8-months-to-3b-with-350m-raise/
  - https://about.doctolib.de/news/doctolib-ubernimmt-aaron-ai-und-erweitert-sein-angebot-um-einen-ki-basierten-telefonassistenten/
  - https://www.drwait.de/telefonassistent-arztpraxis-vergleich
  - https://integreat-app.de/en/
  - https://integreat-app.de/sprachvielfalt-in-integreat/
  - https://handbookgermany.de/en/faq
  - https://welcome.dresden.de/
  - https://dresden-concept.de/welcome/?lang=en
  - https://www.macrumors.com/how-to/ios-26-translate-phone-calls-real-time/
  - https://www.irishtimes.com/technology/2025/11/05/apple-to-roll-out-live-translation-in-eu/
  - https://www.samsung.com/levant/support/mobile-devices/galaxy-ai-languages-usage-guide/
  - https://insights.samsung.com/2025/09/10/live-translate-how-to-communicate-with-anyone-anywhere-in-real-time-2/
  - https://www.androidcentral.com/phones/google-pixel/pixel-10s-voice-translate-goes-live-in-this-unexpected-market
  - https://techcrunch.com/2026/04/16/deepl-known-for-text-translation-now-wants-to-translate-your-voice/
  - https://triaphon.org/
  - https://www.telefondolmetschen-sofort.com/preise
---
# Competitive Landscape

**What this is:** who else lets a person get a phone task done across a language barrier, as of 26 Sept 2026, and where HalloTermin sits.
**Why it matters for us:** the jury will ask "doesn't X already do this?". Google launched a consumer calling feature two days before the event, so we need a calm, true answer.
**Related:** [[Idea A - HalloTermin (Abdul)]] (section 2, first version of this table) · [[Frontend and UX Plan v2]] (section A, product framing) · [[Pitch Kit]] · [[Voice Platform Comparison]] · [[AI Disclosure]]

> **Rules for this note.** Every claim has a source link. Anything we could not confirm is marked **(unverified)**. No numbers without a source. Research was done by web search on 26 Sept 2026. Product pages change quickly, so check again before quoting on stage.

**Our product, in one line (from [[Frontend and UX Plan v2]] §A):** a newcomer describes *any* phone task in their own language (12+ input languages, incl. Arabic RTL, Turkish, Ukrainian). The assistant turns it into a task, shows "Here's what I'll say" before anything happens, calls in German, says in its first sentence that it is an AI calling for a named person, stays inside approved limits, and returns the result in the user's language. It is linked to a checked Dresden directory of newcomer resources and guides.

---

## 1. Consumer AI that calls on your behalf

| Product | What it does | Target user | Languages | Pricing (public) | Gap vs us |
|---|---|---|---|---|---|
| **Google "Call for Me" (Gemini)** | Gemini places real calls to businesses: check stock, reserve a table, reschedule an appointment, put an item on hold. User sees a live transcript and can take over. Launched 24 Sept 2026 as a small-scale experiment. [TechCrunch](https://techcrunch.com/2026/09/24/google-tests-letting-gemini-make-phone-calls-initially-for-us-pixel-owners/) | US Pixel 11 owners with a paid Gemini subscription, beta Phone app [TechCrunch](https://techcrunch.com/2026/09/24/google-tests-letting-gemini-make-phone-calls-initially-for-us-pixel-owners/) | Not stated in the launch coverage (unverified; assume English-first) | Needs paid Gemini plan; price not given in article | US only, one device line, not in Germany. No sign of multilingual input → German call, no newcomer context, no public statement on EU AI Act disclosure (unverified). |
| **Google "Ask for Me" / agentic calling (Search)** | From Search, Google's AI calls several local businesses to ask price and availability, then sends a comparison. Started with nail salons and auto repair, expanded to home repair, beauty and pet care (announced I/O, 20 May 2026). [Google blog](https://blog.google/products-and-platforms/products/shopping/how-to-agentic-calling-let-google-call/) [JobNimbus](https://www.jobnimbus.com/blog/google-ai-calling-home-services) | US consumers shopping for local services | English (US) (unverified beyond US rollout) | Free inside Search | Price-shopping only, US only. Does not book doctors, talk to landlords, or handle authorities. |
| **Leximo Calls** (Leximo LTD, Cyprus) | App: "tell it what you need", AI agent calls restaurants, salons, doctors, makes inquiry calls, returns summary, transcript **and recording**. Also has an MCP server for Claude. [App Store](https://apps.apple.com/us/app/leximo-ai-call-agent/id6756414772) [leximo.ai](https://leximo.ai/en) | General consumers | Store listing names Spanish, English, Polish, Portuguese, Ukrainian, "5+" [App Store](https://apps.apple.com/us/app/leximo-ai-call-agent/id6756414772); German not confirmed (unverified) | 2 free calls; paid price not public [leximo.ai](https://leximo.ai/en) | Generic concierge. Stores recordings (a §201 StGB problem when calling in Germany, see [[Idea A - HalloTermin (Abdul)]] §4). No Germany-specific domain knowledge, no approval step shown, AI disclosure policy not stated on site. |
| **AI Haggler** | Calls many businesses to gather prices/availability, negotiates hotel rates, books appointments; covers healthcare, pet care, home maintenance, hospitality. [aihaggler.com](https://aihaggler.com/) | Price-conscious consumers, travellers | 25 languages incl. German [aihaggler.com](https://aihaggler.com/) | $5 = 10 credits, $20 = 50 credits, 1 credit per call [aihaggler.com](https://aihaggler.com/) | Closest in price and language range. But it is a shopping/negotiation tool; the site itself says the tech is "very early stage" and roughly 20% of calls have significant issues [aihaggler.com](https://aihaggler.com/). No newcomer flow, no local directory, no preview-before-call, no user-language result stated. |

## 2. German/EU voice-agent companies (who they serve)

All of these sit on the **business** side of the call. They are potential *counterparts* (the voice that answers our call) or infrastructure, not consumer competitors.

| Company | What it does | Who pays | Notes | Gap vs us |
|---|---|---|---|---|
| **telli** (Berlin, YC) | AI agents for B2C customer operations across voice, chat, SMS, WhatsApp, email: answering calls, qualifying leads, resolving requests. $15M seed (July 2026), >$18.5M total. Customers include Sky, Enpal, Vaillant. [Tech.eu](https://tech.eu/2026/07/23/telli-secures-15m-seed-to-automate-customer-facing-operations/) | Companies | Pricing not public | Serves the company, not the caller. |
| **Parloa** (Berlin) | Enterprise AI agent platform for customer service (phone, chat, messaging). $350M Series D at $3B valuation (Jan 2026), >$50M ARR, customers incl. Allianz, Booking.com, SAP, Swiss Life. [TechCrunch](https://techcrunch.com/2026/01/15/parloa-triples-its-valuation-in-8-months-to-3b-with-350m-raise/) | Enterprises | Pricing not public | Serves large enterprises' inbound service. |
| **Aaron (Doctolib)** | AI phone assistant for practices: answers patient calls, collects info, books into Doctolib. Acquired by Doctolib May 2024; >3M calls/month for ~16,000 doctors and health professionals in Germany. [Doctolib](https://about.doctolib.de/news/doctolib-ubernimmt-aaron-ai-und-erweitert-sein-angebot-um-einen-ki-basierten-telefonassistenten/) | Practices | Many rivals in the practice-phone market; comparison sites list 12+ vendors [Dr.wait](https://www.drwait.de/telefonassistent-arztpraxis-vergleich) | Practice-side. **Important for us:** our agent will increasingly be talking to *another* AI at the practice. Its patient-facing languages are not confirmed (unverified). |
| **Platforms** (ElevenLabs Agents, Vapi, Retell, Bland, Deepgram Voice Agent) | Toolkits to build voice agents. See [[Voice Platform Comparison]] and [[Idea A - HalloTermin (Abdul)]] §2. | Developers | Usage-priced | Infrastructure; we build on one (Deepgram). |

## 3. Newcomer and integration services in Germany

| Service | What it does | Target user | Languages | Pricing | Gap vs us |
|---|---|---|---|---|---|
| **Integreat** (Tür an Tür) | Open-source, offline-capable app with local information (health, family, admin, learning), content maintained by each municipality. 100+ municipalities, >3M accesses/year. [Integreat](https://integreat-app.de/en/) | Refugees and migrants | 21 languages across the platform; each city picks its own set (e.g. Düsseldorf offers 12) [Integreat](https://integreat-app.de/sprachvielfalt-in-integreat/) | Free for users; paid by municipalities | **Tells** you whom to call, does not call. Whether Dresden runs an Integreat instance: **unverified** (we could not confirm). |
| **Handbook Germany** | Information portal with 160+ topic pages, videos and forum on visas, family, work, language. Neue deutsche Medienmacher, funded by the Federal Integration Commissioner. [Handbook Germany](https://handbookgermany.de/en/faq) | Refugees, newcomers | 9: DE, EN, AR, FA/Dari, Pashto, TR, FR, UK, RU [Handbook Germany](https://handbookgermany.de/en/faq) | Free | Information only, national (not local directory), no action. |
| **Dresden Welcome Center** (city) | Free advice on skilled-worker immigration for employers and newcomers. [welcome.dresden.de](https://welcome.dresden.de/) | Skilled workers, employers | Not checked (unverified) | Free | Human advice with office hours; does not make everyday calls for you. A natural **pilot partner**. |
| **DRESDEN-concept Welcome Center at TU Dresden** | Non-academic support for international researchers and families (visa, housing, Welcome Guide); Mon–Fri 10–15. [DRESDEN-concept](https://dresden-concept.de/welcome/?lang=en) | International researchers | Not checked (unverified) | Free for researchers | Limited hours and audience; another pilot partner. |
| **Relocation services** | Humans do registration, housing, calls. | Employer-paid expats | Varies | Not researched; typically employer-paid (unverified) | Expensive and does not scale to students and spouses. See [[Idea A - HalloTermin (Abdul)]] §2. |

## 4. Translation and interpreting for phone calls

| Service | What it does | Target user | Languages | Pricing | Gap vs us |
|---|---|---|---|---|---|
| **Apple Live Translation (Phone app)** | Spoken two-way translation inside a normal call, on device. Needs iPhone 15 Pro or later, iOS 26. [MacRumors](https://www.macrumors.com/how-to/ios-26-translate-phone-calls-real-time/) EU rollout was delayed by DMA work; Apple said Dec 2025 [Irish Times](https://www.irishtimes.com/technology/2025/11/05/apple-to-roll-out-live-translation-in-eu/) | iPhone owners | 10 incl. German; **no Arabic, Turkish, Ukrainian, Farsi** [MacRumors](https://www.macrumors.com/how-to/ios-26-translate-phone-calls-real-time/) | Free with device | The user still has to lead the call live, at the practice's call hours, with turn-by-turn lag. Key newcomer languages missing. Needs a recent, expensive phone. |
| **Samsung Galaxy AI Live Translate** | Real-time call translation, audible + on screen, on device; also in WhatsApp, Signal, Telegram etc. [Samsung](https://insights.samsung.com/2025/09/10/live-translate-how-to-communicate-with-anyone-anywhere-in-real-time-2/) | Recent Galaxy owners (S25, Z Fold7/Flip7) | 20 incl. German, Arabic, Turkish, Russian; **no Ukrainian or Farsi** in the list [Samsung](https://www.samsung.com/levant/support/mobile-devices/galaxy-ai-languages-usage-guide/) | Free with device | Same: user must be on the call and perform. No task prep, no Germany knowledge, device-locked. |
| **Pixel Voice Translate** | Translates your voice in your own voice timbre during calls, on device (Pixel 10+). German listed, but German rollout was reported as pending [Android Central](https://www.androidcentral.com/phones/google-pixel/pixel-10s-voice-translate-goes-live-in-this-unexpected-market) — current status in Germany **unverified** | Pixel owners | ~11 listed incl. German | Free with device | Same as above; Google-device-only. |
| **DeepL Voice** | Real-time voice-to-voice translation for meetings, mobile conversations; API for call centres (April 2026). [TechCrunch](https://techcrunch.com/2026/04/16/deepl-known-for-text-translation-now-wants-to-translate-your-voice/) | Businesses, teams | 40+ (per coverage, unverified exact list) | Business pricing, not checked | Enterprise meeting tool; does not place a call to a German practice for a consumer (unverified that no consumer calling exists). |
| **Triaphon** (non-profit) | 24/7 medical phone-interpreting hotline; human interpreter in a 3-way call with doctor/nurse and patient. 60,000+ calls since 2017. [Triaphon](https://triaphon.org/) | Medical staff (they call it) | AR, BG, Dari/Farsi, PL, RO, RU, TR, UK, VI (per Wikipedia summary, unverified list) | For institutions, not checked | Used once you are *in* care; the practice initiates. Does not get you the appointment. |
| **Commercial phone interpreters** (e.g. TelefonDolmetschen-sofort) | Human interpreter on the phone, on demand. | Anyone | Many | €1.99/min from landline, up to €2.99/min mobile [TelefonDolmetschen-sofort](https://www.telefondolmetschen-sofort.com/preise) | Works, but the user still sits through a 3-way call and pays per minute. |

---

## 5. Positioning

### The gap in one sentence
Everyone either **tells** newcomers what to do (Integreat, Handbook Germany, welcome centres), **translates while they struggle through the call themselves** (Apple, Samsung, Pixel, interpreters), **serves the business on the other end** (telli, Parloa, Aaron), or **calls for them in English in the US** (Google Call for Me, Ask for Me). Nobody **does the German call for a newcomer, in Germany, from their own language, honestly**.

### Our unique angle
1. **Delegation, not translation.** The user does not need to be on the call, at the practice's call hours, or on a new phone. They tell, check, approve — then do something else.
2. **Newcomer languages that the big players skip.** Our input covers Arabic (RTL), Turkish and Ukrainian ([[Frontend and UX Plan v2]] §A); Apple's in-call translation covers none of these, Samsung lacks Ukrainian and Farsi (sources in §4).
3. **Honesty as a feature, built for German law.** First sentence says it is an AI calling for a named person (EU AI Act Art. 50), no audio stored (§201 StGB), "Here's what I'll say" preview before any data is stored. Leximo, by contrast, advertises recordings (§1).
4. **Local, checked context.** A Dresden directory of doctors, pharmacies, banks, Ausländerbehörde, linked guides ([[Frontend and UX Plan v2]] §B). Generic callers know nothing about Überweisung, Versichertenkarte or Neupatient questions.
5. **Distribution through institutions that already exist.** Universities, welcome centres and employers already serve these users but cannot make everyday calls for them.

### 3 honest weaknesses
1. **The giants are moving now.** Google shipped Call for Me on 24 Sept 2026 ([TechCrunch](https://techcrunch.com/2026/09/24/google-tests-letting-gemini-make-phone-calls-initially-for-us-pixel-owners/)); AI Haggler already calls in German for $0.40–0.50 per call ([aihaggler.com](https://aihaggler.com/)). The core calling tech is not a moat.
2. **Unproven on real German receptionists.** Our evidence is role-play and a round-trip test ([[Pitch Kit]] §1.4), not real practice calls. AI Haggler reports ~20% of its calls have significant issues; we have no reason to assume we are better yet. Practices may refuse to deal with a bot, and more and more will answer with their own AI (Aaron handles >3M calls/month, [Doctolib](https://about.doctolib.de/news/doctolib-ubernimmt-aaron-ai-und-erweitert-sein-angebot-um-einen-ki-basierten-telefonassistenten/)).
3. **No German phone number and no business model yet.** A +49 number needs a Twilio regulatory bundle ([[Telephony Constraints (Twilio Trial, Numbers)]]); who pays (user, university, employer, city) is untested. Newcomers are price-sensitive and the free device translators set a price anchor of zero.

### "Why won't Google just do this?"
**Google builds for the average user in big markets; a German-law-compliant agent that takes a Ukrainian or Arabic request and phones a Dresden Hausarzt is a niche it has no reason to serve soon — and if it does, our value moves to the local data, trust and institutional channels, not the voice.**
