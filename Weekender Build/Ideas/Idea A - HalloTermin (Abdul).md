# HalloTermin: An AI Voice Agent That Books German Doctor Appointments for Newcomers — Problem Validation, Concept & 48-Hour Plan

**Build an AI agent that phones a German Arztpraxis for the newcomer, speaks German, books a slot inside time windows the user has pre-approved, and sends back an English confirmation. Start with doctor appointments, not the Ausländerbehörde, and keep a "human interpreter mode" as the fallback.** The problem is well documented and the tech works for German today. Deepgram now has German speech-to-text, German Aura-2 voices and a Voice Agent API with an official Twilio outbound reference. The two things that decide success are how well you win the first 15 seconds of the call and whether you get the AI disclosure right.

## TL;DR
- **The problem is real and large.** About 402,000 international students were enrolled in Germany in winter semester 2024/25. Germany issued 128,358 family-reunion visas in 2025, and work-visa processing grew 7.7%. In the OECD's research, 65% of immigrants in Germany say lack of German is their biggest obstacle in everyday life. Meanwhile the Deutsche Stiftung Patientenschutz reports Arztpraxen are "hardly reachable by phone", and Dresden's Ausländerbehörde warns of long waits "because of many requests and little staff".
- **Best concept: a German-speaking call agent for Arzttermine, with a live English transcript and a human fallback.** Doctor calls happen often, are phone-first and low-risk, and it's obvious when one succeeded. Ausländerbehörde slots are scarce, so a bot can't create capacity there; treat it as a later vertical, handled by email.
- **Doable in 48h if you cut hard.** Use Lovable for the request form and live call view, n8n for orchestration and confirmations, and one small relay server bridging Twilio and the Deepgram Voice Agent. Skip real Praxis calls, Ausländerbehörde, accounts, payments and a multi-language UI. Demo a live call to a teammate playing a German receptionist, and disclose "KI-Assistentin" in the first sentence.

## Key Findings

### 1. Problem validation (evidence)

**Who is affected (Germany-wide):**
- **International students:** about 402,000 international students and doctoral candidates were enrolled in winter semester 2024/25, up about 6%, with a record 116,600 first-year students (DAAD/DZHW, *Wissenschaft weltoffen 2025*). [DAAD](https://www.daad.de/en/press-releases/erneut-hohe-zahl-an-internationalen-studierenden-in-deutschland/) DAAD forecasts about 420,000 for 2025/26. [DAAD](https://www.daad.de/en/press-releases/zahl-internationaler-studierender-deutlich-ueber-400000/) India is the largest country of origin, with just under 59,000 students. [DAAD](https://www.daad.de/en/press-releases/erneut-hohe-zahl-an-internationalen-studierenden-in-deutschland/)
- **Dresden specifically:** TU Dresden has about 29,000 students. 18.9% of active students hold a foreign nationality, from 128 countries, and the share of Bildungsausländer:innen rose from 9.2% (2010) to 16.1% (2024). [TU Dresden](https://tu-dresden.de/internationales/profil/zahlen-und-fakten-neu?set_language=en) So thousands of potential users sit a few kilometres from this hackathon.
- **Family reunion (Familiennachzug):** the federal government reports 128,358 family-reunion visas for relatives of third-country nationals in 2025. 67,831 were for spouses and 54,882 for children, and another 43,739 were issued by the end of May 2026. [Oldenburger Onlinezeitung](https://www.oldenburger-onlinezeitung.de/nachrichten/18-570-visa-zum-familiennachzug-fuer-schutzberechtigte-erteilt-214597.html) *The sources conflict:* Mediendienst Integration cites about 110,400 for 2025, and the Foreign Office's end-of-November figure was 101,756. [Evangelisch.de](https://www.evangelisch.de/inhalte/250875/21-12-2025/bericht-mehr-als-100000-visa-zum-familiennachzug-2025-erteilt) [Mediendienst Integration](https://mediendienst-integration.de/fluechtlinge/fluechtlinge-in-deutschland/familiennachzug-nach-deutschland/) Either way it is six figures a year, and reunited spouses are often the people with the least German.
- **Skilled workers:** the Foreign Office says visa processing for employment grew 7.7% (+15,000 visas) in 2025, even though overall visa volume fell. [Federal Foreign Office](https://www.auswaertiges-amt.de/de/service/visa-und-aufenthalt/2231558-2231558)

**The language barrier (survey data):**
- OECD *State of Immigrant Integration 2024 – Germany*: 51% of immigrants now living in Germany see German as a major barrier. Those living in Germany name lack of German as the most important obstacle **for everyday life (65%)** and job search (54%). [OECD](https://www.oecd.org/content/dam/oecd/en/topics/policy-issues/migration/Sii2024--Germany%20%28ENG%29%20%E2%80%93%20v6%20%28FINAL%20with%20bookmarks%29.pdf)
- The OECD's "Your Way to Germany" survey for the Federal Ministry of Labour (BMAS), which started with about 30,000 respondents in 2022–2023, found that "participants would like more support to learn German and more help with finding a job"; 40% of those already in Germany were dissatisfied with their contact with Foreigners' offices.
- Research on healthcare access across Europe describes language as "the first barrier". In Germany, patients have a right to information in a language they understand, but who pays for interpreting is not specified. [nih](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8022480/)

**Appointment friction (authorities):**
- **Ausländerbehörde Dresden:** visits are possible only with an appointment. [Dresden](https://www.dresden.de/de/rathaus/dienstleistungen/abh/auslaenderangelegenheiten-terminabsprachen.php) There are no general opening hours; you book by hotline, (0351) 488 6009, or by email. [Dresden](https://www.dresden.de/de/rathaus/aemter-und-einrichtungen/oe/dborg/stadt_dresden_6350.php) The city's own site warns: "Wegen vieler Anfragen und wenig Personal kann es zu langen Wartezeiten bis zu Ihrem Termin kommen." ("Because of many requests and little staff, there may be long waits until your appointment.") [Dresden](https://www.dresden.de/de/rathaus/dienstleistungen/abh/auslaenderangelegenheiten-terminabsprachen.php) The office moved to Lingnerallee 3 in April–May 2026, with no regular appointments during the move. [Dresden](https://www.dresden.de/de/rathaus/aktuelles/pressemitteilungen/2026/04/pm_011.php)
- **Naturalisation in Dresden:** the backlog is about 31 months until an application is even processed, with about 3,850 applications pending in February 2026 (Ausländerrat Dresden). [Auslaenderrat](https://www.auslaenderrat.de/drei-jahre-warten-auf-einbuergerung-sind-rechtsstaatlichnicht-hinnehmbar-auslaenderrat-dresden-e-v-fordertklaren-kommunalpolitischen-kurswechsel/) A travel/local blog adds that waiting up to a year just for the application appointment is common; treat that as anecdotal. [Striezelmarkt Dresden](https://www.dresdenausflug.de/einbuergerung-dresden/)
- **Bürgeramt:** in a November 2023 netzpolitik.org data investigation, a bot searching Berlin Bürgeramt slots from 9 to 24 September 2023 found an appointment in only about one in three attempts, meaning two out of three requests failed. A whole cottage industry of appointment-sniping bots (e.g., Terminli) exists because of this. [Terminli](https://www.terminli.de/blog-artikel/termine-buergeramt-berlin-terminli)

**Appointment friction (doctors):**
- The Deutsche Stiftung Patientenschutz told APOTHEKE ADHOC that reports are piling up on its patient-protection hotline that practices are "kaum noch telefonisch erreichbar" ("hardly reachable by phone any more"): either the line is busy or you end up in an endless queue. It adds that one in five people over 65 has no access to digital services.
- BAGSO's 2022 survey of older people without internet, reported by Deutsches Ärzteblatt, found contacting the doctor was the most common difficulty: phone booking options keep shrinking, leaving sharply reduced call times, permanently busy lines or hours of waiting. One 66-year-old respondent phoned for 1.5 weeks before reaching a receptionist.
- **116117 Terminservice:** it guarantees an appointment within 4 weeks, but for most specialists it requires a referral with a Vermittlungscode. KV Berlin states explicitly that treatment in a foreign language **cannot be taken into account** when appointments are arranged. [KV Berlin](https://www.kvberlin.de/fuer-patienten/terminservice) The 116117 app can filter practices by language skills, but you still have to get through to them. [App Store](https://apps.apple.com/de/app/116117-app/id1465237675)

**What the problem really is:** it isn't just "no German". Two things stack. The system is phone-first and short on capacity (busy lines, short call windows, fast speech), and newcomers can't perform under that pressure in German. A phone call is the worst possible format for a language learner: no visual cues, no time to think, domain vocabulary (Versichertenkarte, Überweisung, Erstuntersuchung), and a receptionist who has 30 seconds.

### 2. Existing solutions and their gaps

| Solution | What it does | Gap for newcomers |
|---|---|---|
| Doctolib / online booking | Books online where the practice has opted in | Many practices, especially Hausärzte and specialists, still book by phone only |
| 116117 app/phone | Official referral-based booking; language filter | You're assigned any available practice; foreign-language treatment isn't considered; the phone line is in German |
| Bürgeramt snipers (Terminli etc.) | Poll online calendars and auto-book | Only work where an online calendar exists (e.g., Berlin); useless for phone-only services |
| AI call apps (Leximo, AI Haggler) | Consumer AI makes calls on your behalf (restaurants, hotels, appointments) [Aihaggler](https://aihaggler.com/) [apple](https://apps.apple.com/us/app/-/id6756414772) | Generic; not built for German healthcare vocabulary, insurance data or the EU AI Act; no newcomer onboarding context |
| B2B voice platforms (Telli, ElevenLabs Agents, Vapi/Retell/Bland) | Businesses automate *their own* inbound/outbound calls [ElevenLabs](https://elevenlabs.io/agents/ai-appointment-setter) [TechCrunch](https://techcrunch.com/?p=2994442) | Serve the practice or company, not the newcomer; no consumer "call on my behalf" product |
| Translation apps (Google Translate, DeepL Voice) | Translate speech face-to-face | Don't sit inside a phone call; turn-by-turn lag kills a live call |
| Relocation services / human helpers | Humans make the calls | Expensive and don't scale; students and spouses can't afford them |

**The gap:** no product combines **a consumer-side agent**, **native-quality German on the phone**, **Germany-specific domain knowledge** (insurance, Überweisung, Anmeldung) and **EU AI Act–compliant disclosure**, all for newcomers.

### 3. Tech feasibility

**Deepgram (as of September 2026):**
- **Speech-to-text:** Nova-3 has a dedicated German model for streaming and batch. [Deepgram](https://deepgram.com/learn/deepgram-expands-nova-3-with-german-dutch-swedish-and-danish-support) **Flux Multilingual** (`flux-general-multi`), generally available since April 29, 2026, covers 10 languages including German and English in one model and can switch languages mid-call. [SiliconANGLE](https://siliconangle.com/2026/04/29/deepgram-expands-flux-10-languages-mid-call-switching-voice-agents/) In the Voice Agent you pass `language_hints: ["de"]` (or `["de","en"]`). [Deepgram](https://deepgram.com/learn/introducing-flux-multilingual) [deepgram](https://developers.deepgram.com/docs/multilingual-voice-agent)
- **Text-to-speech:** Aura-2 has supported German since December 2025, with **7 German voices**. [Deepgram](https://developers.deepgram.com/changelog/2025/12/12) [deepgram](https://developers.deepgram.com/docs/tts-models) The featured ones are `aura-2-viktoria-de` (warm, friendly, female) and `aura-2-julius-de` (male). `aura-2-fabian-de` (mature, professional, polite) and `aura-2-elara-de` (calm, patient, trustworthy) also suit a Praxis call. [deepgram](https://developers.deepgram.com/docs/tts-models) **Watch out:** the newer Flux TTS voices are English-only. If you omit `agent.speak`, the agent defaults to an English Flux voice, so set the German Aura-2 voice explicitly (speak provider `version` v1). [deepgram](https://developers.deepgram.com/docs/voice-agent-tts-models) [Deepgram](https://developers.deepgram.com/docs/flux-tts/voices)
- **Voice Agent API:** one WebSocket runs STT → LLM → TTS, with barge-in, turn detection and **function calling**. A `defer_until_eot` flag holds an irreversible action, such as booking or ending the call, until the other person's turn is confirmed. [deepgram](https://developers.deepgram.com/docs/configure-voice-agent) [deepgram](https://developers.deepgram.com/docs/twilio-and-deepgram-voice-agent) `agent.language` is deprecated; set the language on the listen and speak providers instead. [Twilio +2](https://www.twilio.com/en-us/blog/partners/integrations/building-an-outbound-voice-agent-with-twilio-and-deepgram)
- **Code-switching limit:** no German Aura voice switches between English and German within one reply. [deepgram](https://developers.deepgram.com/docs/multilingual-voice-agent) The agent speaks German to the Praxis; English belongs in the app UI and the transcript, not in the call audio. This fits the product anyway.
- **Telephony:** Deepgram and Twilio publish an **outbound voice agent reference implementation**. You trigger a call through a REST API, the agent runs a scripted conversation, and a structured outcome (JSON via an `update_lead`-style function) is posted back at the end, with voicemail handling and silence monitoring. Audio is mulaw at 8 kHz, which matches Twilio natively. An EU endpoint exists. [Twilio](https://www.twilio.com/en-us/blog/partners/integrations/building-an-outbound-voice-agent-with-twilio-and-deepgram) [deepgram](https://developers.deepgram.com/docs/twilio-and-deepgram-voice-agent)
- **Cost:** the Voice Agent API costs $0.050–$0.163 per minute depending on tier, and new accounts get $200 in free credit. [Cekura](https://www.cekura.ai/blogs/deepgram-pricing) [Deepgram](https://developers.deepgram.com/docs/build-voice-agent-with-twilio-deepgram-openai) A 3-minute booking call costs well under €1 including Twilio. Hackathon cost is effectively zero.

**n8n:** use it for orchestration, not audio. The n8n community reports that n8n "doesn't work well with WebSockets" and works best with REST. [n8n](https://community.n8n.io/t/making-an-ai-powered-voice-agent-using-twilio-and-n8n/167112) So n8n should handle the pre-call steps (validate the request, generate a German call brief with an LLM, trigger the call) and the post-call steps (Google Calendar event, email/WhatsApp confirmation, database update). Webhook and Twilio nodes exist, and ready-made multilingual Twilio voice-bot templates are available. [n8n](https://n8n.io/workflows/6309-create-multilingual-voice-calling-bot-with-gpt-4o-elevenlabs-and-twilio/) [n8n](https://n8n.io/integrations/webhook/and/twilio/)

**Lovable Pro:** it builds the React frontend plus a Supabase backend. Edge Functions can act as webhooks to and from n8n, and API keys live in Secrets. [Lovable](https://lovable.dev/faq/backend/supabase/supabase-external-integrations) [Lovable](https://docs.lovable.dev/integrations/supabase) Supabase Realtime can stream the live transcript into the UI.

**Twilio in Germany:** a German (+49) local or mobile number needs a **regulatory bundle** (business registration and address proof). Review takes up to 2–3 business days, so it isn't possible this weekend. [Twilio](https://www.twilio.com/docs/phone-numbers/regulatory/api/regulations) [Twilio](https://support.twilio.com/hc/en-us/articles/8338625205147-How-to-Submit-a-Regulatory-Bundle-for-Phone-Number-Regulatory-Compliance) Use an existing trial or US number to call a teammate's phone. In production you'd need a German number, because a +1 caller ID gets fewer answers.

### 4. Legal and ethical considerations (Germany/EU)

- **EU AI Act, Article 50(1), in force since 2 August 2026:** people must be told they are interacting with an AI "at the first point of contact", and a disclosure hidden in terms and conditions is not enough. The chatbot disclosure duty got no grace period. Fines reach €15m or 3% of turnover, with the lower figure applying to SMEs and startups. [Falcon Internet +2](https://www.falconinternet.net/blog/eu-ai-act-article-50-transparency-rules-enforced-august-2026) **Design consequence:** the first sentence of every call must say it's an AI assistant. That is also good UX, because honesty buys goodwill.
- **§201 StGB (Vertraulichkeit des Wortes):** recording the non-publicly spoken word without consent is a crime punishable by up to 3 years in prison, and even an attempt is punishable. Practitioners argue that transcribing in-stream without storing audio avoids most of the problem, but lawyers flag that real-time AI transcription itself is contested. [LHR Rechtsanwälte +2](https://www.lhr-law.de/thema/heimliche-aufzeichnung-von-gespraechen/) **Design consequence:** never store audio; don't enable Twilio recording; ask for consent to a transcript ("Ist es in Ordnung, wenn ich das Gespräch für meine Nutzerin mitschreibe?", i.e. "Is it OK if I take notes of the call for my user?"); if they say no, keep only a structured summary.
- **GDPR:** the reason for a doctor visit is health data (Art. 9), so collect the minimum ("Termin für eine Erstuntersuchung", a first examination, rather than symptoms), use EU endpoints where available, and sign data processing agreements (Art. 28) with vendors. [Skill-Sprinters](https://skill-sprinters.de/blog/tools/ki-telefonassistent-voice-agent-kmu-2026/)
- **Authorization and identity:** the agent acts *as a messenger for* a named person. It must never impersonate the user ("Ich rufe im Auftrag von Frau Priya Sharma an", "I'm calling on behalf of Ms Priya Sharma"). Collect explicit in-app authorization for each call. Keep the agent away from anything needing identity proof or binding legal statements (e.g., Ausländerbehörde case questions).
- **Practical risks:** receptionists may hang up on bots; some practices will insist the patient call personally; background noise and dialect (Saxon!) hurt STT; the call may land in a phone menu ("Drücken Sie 1…"); slot negotiation can drift outside the user's constraints; and the agent may hallucinate a confirmation. Mitigations: disclosure in a polite, human framing; send phone-menu key presses (DTMF); allow only pre-approved time windows; read the booked slot back and have the receptionist confirm it before the call ends; and a "connect the user" fallback.

## Details — The Five Questions

### 1. Was ist das Problem (wenn ich…, will ich…, damit…)

**Method: Job Stories** (When… I want to… so I can…). They focus on the *situation and motivation* rather than on a persona, which fits here: the trigger (a phone-only process in German) matters more than demographics.

**Other methods you could use:**
- **Problem Statement / Point of View (POV):** "[User] needs [need] because [insight]." Example: "A newly arrived non-German speaker needs to book a doctor's appointment by phone because practices are phone-first and a live German call is the hardest format for a language learner."
- **How Might We (HMW):** "How might we let someone without German book a phone-only appointment in under 5 minutes, without speaking?"
- **Jobs-to-be-Done (JTBD):** the core job is "Get me seen by the right doctor soon, without having to perform in German under pressure."
- **5 Whys, or a Lean Canvas problem box**, for the pitch deck.

**Job stories:**
1. **When** I'm sick and the Hausarzt near me only takes appointments by phone, **I want** someone to call in fluent German and book the earliest slot that fits my lecture schedule, **so I can** see a doctor this week without panicking on the phone.
2. **When** my spouse has just arrived on a family-reunion visa and needs a first appointment (Frauenarzt, Kinderarzt), **I want to** trigger the call from my phone in English while I'm at work, **so that** she gets care without me taking time off to phone the practice in its narrow call window.
3. **When** a receptionist asks something I didn't prepare for (insurance, referral, "Sind Sie Neupatient?", i.e. "Are you a new patient?"), **I want** the answer handled or relayed to me instantly in English, **so I can** avoid a failed call and a restart from zero.

**The HMW for your slide:** *How might we turn the most stressful 3 minutes of a newcomer's week, a German phone call, into a 30-second form?*

### 2. Für wen

**Method: Proto-personas.** These are assumption-based personas built from domain knowledge and secondary data and then validated. At a hackathon, validate them by interviewing 3–5 international people at the venue on Saturday morning.

**Proto-persona A: "Priya, the international Master's student"**
- **Background:** 24, from Pune, India, Master's in Nanoelectronics at TU Dresden, second semester. India is the largest origin country, with about 59,000 students in Germany. [DAAD](https://www.daad.de/en/press-releases/erneut-hohe-zahl-an-internationalen-studierenden-in-deutschland/) She has A1 German, completed via Duolingo. Public health insurance through TK. She lives in a WG in Johannstadt.
- **Behaviours:** does everything on her phone; uses Google Translate and ChatGPT for letters; relies on WhatsApp groups ("Indians in Dresden") for tips; avoids calls and waits for friends to help.
- **Needs:** a Hausarzt and a dermatologist; also a residence-permit extension appointment at the Ausländerbehörde.
- **Pain points:** practice lines are busy during her lectures; she freezes when the receptionist speaks fast; she doesn't know words like "Überweisung" (referral) or "Versichertenkarte" (insurance card); she has already hung up on two calls; she feels like a burden asking German friends.
- **Quote:** "I can write a thesis in English, but I can't book a doctor."

**Proto-persona B: "Amina, the family-reunion spouse"**
- **Background:** 31, from Syria or Türkiye (both among the top nationalities for family-reunion visas), came to Dresden to join her husband, who works as a nurse (a skilled-worker visa). [Evangelisch.de](https://www.evangelisch.de/inhalte/250875/21-12-2025/bericht-mehr-als-100000-visa-zum-familiennachzug-2025-erteilt) She is attending an integration course at A2, has a 3-year-old child, and has little English; Arabic or Turkish is her strongest language.
- **Behaviours:** her husband currently makes all calls, during his breaks; she uses voice messages rather than text.
- **Needs:** a Kinderarzt for the U-examinations (child check-ups), a Frauenarzt, and later a Kita place.
- **Pain points:** total dependence on her husband; practices won't talk to him if the appointment is for her; she feels a loss of autonomy.
- **Product implication:** for Amina the app UI would need Arabic or Turkish plus voice input, so she is **v2, not the MVP**. Priya's English-UI persona is the MVP target; Amina is the "impact slide" in the pitch.

**(Optional C: "Marco, the Blue Card engineer"** at a Dresden semiconductor company. He has money but no time, and his employer's HR might pay for this as a relocation benefit. That makes him the first **B2B buyer** persona.)

### 3. Wo bricht's?

**Method: Service Blueprint.** It maps customer actions, frontstage (visible) interactions, backstage (invisible) processes and support systems, then marks the breakpoints (⚡).

**Current state: booking a doctor's appointment as a non-German speaker**

| Phase | Customer actions | Frontstage (touchpoint) | Backstage | Support systems | ⚡ Breakpoint |
|---|---|---|---|---|---|
| 1. Realise need | Feels ill; searches "English speaking doctor Dresden" | Google Maps, Jameda, 116117 app, WhatsApp groups | – | Practice websites (German only) | ⚡1 Can't tell which practice accepts new patients or speaks English |
| 2. Choose practice | Picks the nearest one with an online presence | Website: "Termine nur telefonisch" ("appointments by phone only") | Practice limits new patients | Doctolib (only some practices) | ⚡2 No online booking, so a phone call is forced |
| 3. Prepare | Writes a script in Google Translate | – | – | Translation app | ⚡3 Can't anticipate the receptionist's questions |
| 4. Call | Dials during the phone window (e.g., 8–10 am, clashing with lectures) | Busy tone or phone menu in German | 1–2 staff juggle phone and counter | Phone system | ⚡4 Busy line or German menu (it takes 1.5 weeks just to get through, per BAGSO) |
| 5. **Conversation** | Receptionist: "Praxis Dr. Weber, guten Tag?" ("Dr. Weber's practice, hello?") | Fast German, jargon, time pressure | Receptionist checks calendar and insurance | Practice software | ⚡5 **MOMENT OF TRUTH: the newcomer freezes; the receptionist switches to rushed English or hangs up** |
| 6. Negotiate slot | Receptionist offers "Dienstag, 8:15?" ("Tuesday, 8:15?") | Needs an instant decision | Slot held for seconds | Calendar | ⚡6 Can't check own schedule mid-call; accepts a bad slot or loses it |
| 7. Confirm details | Asked for name spelling, date of birth, insurance, referral | Spelling in German letters | Patient record created | – | ⚡7 Misspelled name; forgotten referral, so turned away on the day |
| 8. After call | Unsure what exactly was agreed | No written confirmation | – | – | ⚡8 Missed or wrong appointment; no-show fee risk |

**Future state with HalloTermin:** phases 3–8 move backstage. The user fills in one English form (practice, reason category, insurance, time windows, date of birth). The agent handles the phone menu, disclosure, conversation, slot choice within pre-approved windows, spelling (using the German spelling alphabet, e.g. "S wie Siegfried", "S as in Siegfried") and a read-back confirmation. n8n then pushes a calendar event and an English summary covering what to bring (insurance card, referral). The Ausländerbehörde journey has the same breakpoints at ⚡4–5, but the root cause there is **capacity**, not language, which is why it isn't the MVP.

### 4. Was ist der eine Moment?

**The moment of truth is the first 15 seconds after the practice picks up: "Praxis Dr. Weber, guten Tag?"** Everything before it is preparation; everything after it is logistics. In those seconds the receptionist decides whether to engage or hang up, and a newcomer either performs in German or fails. Every downstream breakpoint (⚡5–7) depends on this opening going well.

**How HalloTermin wins that moment:**
1. **Native, polite German opening with honest disclosure in one breath:** *"Guten Tag, hier spricht die KI-Assistentin von Frau Priya Sharma. Sie spricht leider noch kein Deutsch, deshalb rufe ich in ihrem Auftrag an. Ich möchte gern einen Termin für eine Erstuntersuchung vereinbaren."* ("Hello, this is Ms Priya Sharma's AI assistant. Unfortunately she doesn't speak German yet, so I'm calling on her behalf. I'd like to make an appointment for a first examination.") This satisfies AI Act Art. 50 and turns the bot into a sympathetic helper rather than a spam caller. It also states the purpose within 10 seconds.
2. **Zero hesitation:** Deepgram's turn detection plus a pre-built brief (name, date of birth, insurance, referral yes/no, new patient) means the agent never says "one moment" for things it should already know.
3. **Pre-authorized decisions:** the user approved time windows in advance, so the agent can say "Ja, Dienstag 8:15 passt" ("Yes, Tuesday 8:15 works") immediately. That wins ⚡6 as well.
4. **Graceful escape hatch:** if the receptionist insists on talking to the patient, the agent offers a callback number or, in interpreter mode, conferences in the user with live subtitles.
5. **Read-back:** "Ich wiederhole: Dienstag, 14. Oktober, 8:15 Uhr, bei Dr. Weber. Richtig?" ("Let me repeat: Tuesday, 14 October, 8:15, with Dr. Weber. Correct?") This prevents hallucinated bookings.

**Metric to show:** "Time from pickup to purpose stated: under 10 seconds. Time to booked slot: under 90 seconds."

### 5. Schaffst du das in 48h? Was ist machbar, was ist zu groß, was muss weglassen?

**Yes, if you build one call type for one persona with one happy path plus two edge cases.**

**MVP (feasible):**
- **Lovable:** landing page; a request form (practice name and phone number, reason category from a dropdown, insurance, date of birth, 2–3 time windows, authorization checkbox); a live call screen showing the German transcript with English translation line by line and a status indicator; a result card.
- **n8n:**
  - Webhook receives the request from Supabase or Lovable.
  - An LLM node builds a German call brief and system prompt.
  - An HTTP node triggers the relay server's `/call`.
  - A second webhook receives the call outcome and fans out to a Google Calendar event, an email via Gmail or SendGrid, optionally a WhatsApp message via the Twilio sandbox, and an update to the Supabase record.
- **Relay server (the one piece of real code, about 150–300 lines):** fork Deepgram's Twilio outbound reference. Configure `flux-general-multi` with `language_hints:["de"]` (or `nova-3` with `de`), an LLM for the think step, and the TTS voice `aura-2-viktoria-de`. Define functions `propose_slot`, `confirm_booking` (with `defer_until_eot`), `request_user_input` and `end_call`, and push transcript events to Supabase.
- **Edge cases to script:** "Wir nehmen keine Neupatienten" ("We're not taking new patients") → polite end and outcome = `rejected_no_new_patients`; and "Haben Sie eine Überweisung?" ("Do you have a referral?") → answered from the brief.
- **English translation of the transcript:** use an LLM call per utterance, or run it in n8n afterwards if latency hurts.

**Too big for 48h:**
- Calling real practices at scale. Do it at most once as a bonus, and with consent.
- The Ausländerbehörde vertical: capacity-limited, legally sensitive, and mostly email- or hotline-based.
- Getting a German +49 Twilio number (the regulatory bundle takes days). [Twilio](https://support.twilio.com/hc/en-us/articles/8338625205147-How-to-Submit-a-Regulatory-Bundle-for-Phone-Number-Regulatory-Compliance)
- A multi-language UI (Arabic, Turkish) and voice input for Persona B.
- Practice discovery (scraping, a "speaks English" database), 116117 Vermittlungscode flows, payments, user accounts or authentication beyond a demo login.
- Full live **interpreter mode** (bridging the user into the call with two-way translation). Show it as a mocked "next step" button, or build it only if you're ahead by Sunday morning.

**Must leave out (deliberately):**
- Storing audio recordings, because of §201 StGB. Keep text only.
- Symptom collection, because of GDPR Art. 9 data minimisation.
- Any feature that impersonates the user.
- Bürgeramt appointment sniping, which is a crowded, grey-zone market and not your differentiator.

**Demo plan:**
1. Presenter fills in the Lovable form in English on stage (20 seconds).
2. A teammate's phone rings. They play the "Praxis Dr. Weber" receptionist, in German, ideally with a small Saxon accent and one curveball ("Sind Sie Neupatientin? Haben Sie eine Überweisung?", "Are you a new patient? Do you have a referral?").
3. The audience hears the agent's disclosure and negotiation on speaker, while the screen shows the German transcript with English subtitles.
4. The slot is confirmed and read back; the presenter's phone buzzes with a WhatsApp or email confirmation and a calendar invite.
5. Backup: a pre-recorded video of a successful run, in case venue Wi-Fi or Twilio fails.

**Weekend timeline:**

| When | Goal |
|---|---|
| **Fri evening (3–4h)** | Lock scope and personas. Create Deepgram, Twilio and Supabase accounts. Run the Deepgram Twilio outbound reference end-to-end with a *German* voice calling a teammate. This is the riskiest item, so de-risk it first. |
| **Sat morning** | Write the system prompt and German opening. Implement the function calls. Interview 3–5 international attendees to validate the personas (grab quotes for the pitch). |
| **Sat afternoon** | Lovable UI: form, live transcript screen, result card. Build the n8n flows for the request → call trigger and outcome → calendar and email/WhatsApp. |
| **Sat evening** | Integrate end-to-end. Test 10+ calls with different "receptionist" behaviours (fast speech, a refusal, a phone menu, the referral question). Tune turn-taking and latency. |
| **Sun morning** | Harden the happy path. Add the English translation of the transcript. Record the backup video. Code freeze by about 12:00. |
| **Sun afternoon** | Pitch deck (5 slides: problem stats, persona, blueprint breakpoint, live demo, ask) and rehearse the 30-second pitch 5 times. |

**Team split (for 3–4 people):** (1) relay server with Deepgram and Twilio; (2) n8n flows and prompts; (3) Lovable UI and Supabase; (4) research, persona interviews, pitch and receptionist role-play.

## Recommendations

1. **Go with "HalloTermin — your German-speaking phone assistant for doctor appointments."** It's the highest-value, most demo-able slice. Doctor calls are frequent, phone-first, low-risk and have a binary outcome (booked or not).
2. **Make compliance a feature, not a footnote.** The AI disclosure in the first sentence, no audio storage and data minimisation are things jurors in Germany will ask about. Since Art. 50 has applied since August 2026, "compliant by design" is a differentiator against generic call bots.
3. **Position interpreter mode as the moat and roadmap:** agent-first, with a human in the loop when needed. It's also the answer to "what if the practice insists on the patient?"
4. **Name the business model in the ask:** B2B2C through universities (TU Dresden International Office), employers hiring skilled workers (relocation benefit), Welcome Centers and integration-course providers, with a per-call consumer fallback. The Dresden city welcome address (welcome@dresden.de) shows that the city already runs a welcome service you could approach. [Dresden](https://www.dresden.de/de/rathaus/aktuelles/pressemitteilungen/2026/04/pm_011.php)
5. **Other name options:** *Anrufa*, *SprichFürMich*, *CallBridge*, *TerminTalk*. "HalloTermin" wins because Germans and newcomers both understand it instantly.

## Caveats
- The Ausländerbehörde wait-time evidence for Dresden is qualitative (the city's own warning) plus naturalisation backlog figures. I found no official average appointment wait for residence permits. The "up to a year for an application appointment" figure comes from a secondary blog. [Striezelmarkt Dresden](https://www.dresdenausflug.de/einbuergerung-dresden/)
- The family-reunion figures conflict (110,400 vs 128,358 for 2025) depending on source and definition (visas issued vs arrivals, which third-country relatives are counted). [Oldenburger Onlinezeitung](https://www.oldenburger-onlinezeitung.de/nachrichten/18-570-visa-zum-familiennachzug-fuer-schutzberechtigte-erteilt-214597.html) [Mediendienst Integration](https://mediendienst-integration.de/fluechtlinge/fluechtlinge-in-deutschland/familiennachzug-nach-deutschland/)
- Deepgram's German performance on Saxon dialect over 8 kHz phone audio is untested. Validate it Friday night. The `auto_language_detection` voice-routing feature is mentioned in Deepgram marketing but not confirmed in the developer docs, so don't depend on it. [Deepgram](https://deepgram.com/learn/introducing-flux-multilingual)
- Legal points are general information, not legal advice. Whether real-time transcription without storage fully avoids §201 StGB is debated among German lawyers.
- Consumer AI call apps (e.g., Leximo) already exist. Your differentiation is the Germany/newcomer domain focus and compliance, not the raw capability.

## 30-Second Pitch (≈83 words)

"Imagine you're sick in Dresden and you don't speak German. The Praxis only books by phone. Someone answers in rapid German, you freeze, you hang up. That's daily life for Germany's 400,000 international students and the 128,000 people granted family-reunion visas last year. HalloTermin makes the call for you. Type your request in English; our AI agent phones the Praxis, speaks German, books the slot, and texts you the confirmation. Watch — we're calling our receptionist live. We want pilot partners: universities, employers, welcome centers."