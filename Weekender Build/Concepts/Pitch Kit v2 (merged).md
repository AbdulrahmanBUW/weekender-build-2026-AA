---
type: concept
tags: [pitch, presentation, merged]
sources: []
---
# Pitch Kit v2 (merged)

**What this is:** how we talk about the merged product, **Dresden mit Kind** with the feature **"Ask for me"**. It has the 30-second pitch, the 5-minute pod pitch, the 3-minute Sunday demo, jury answers and a slide outline.
**Why it matters for us:** the demo on Sun 27.09 at 13:00 is 3 minutes. Both of us should tell the same calm, true story, every time.
**Replaces:** [[Pitch Kit]] (v1, HalloTermin only).
**Related:** [[Merged Concept]] · [[DEC-003 Merged concept]] · [[Idea B - Dies-Das-Ana-Nas]] · [[Competitive Landscape]] · [[Agent Space - Who Does What]] · [[AI Disclosure]] · [[Receptionist Test Scripts]] · [[Task Types - How to extend]] · [[Monday-Morning Plan]] · [[Weekender Build - Event Format]]

> **Rules for this note**
> - Every number comes from a vault note (see section 0). Do not add numbers on stage.
> - Plain B1 English. No hype words (revolutionary, game-changer, seamless, cutting-edge, disrupt, magic). Say what it does.
> - Maria is a proto-persona from [[Idea B - Dies-Das-Ana-Nas]]. "Olgas Musikstudio" is demo data (Olga is also a persona). Never say that we called a real provider.
> - Text in **[square brackets]** must be checked or updated on the day.

---

## 0. Fact sheet: numbers we may say

| What we say | Source |
|---|---|
| 65% of immigrants in Germany name lack of German as the biggest obstacle in everyday life | OECD 2024, via [[Idea A - HalloTermin (Abdul)]] |
| TU Dresden: about 29,000 students, 18.9% with a foreign nationality | TU Dresden, via [[Idea A - HalloTermin (Abdul)]] |
| 54,882 family-reunion visas for children in 2025. **Only say it with "sources differ"** (totals: 110,400 vs 128,358) | federal government, via [[Idea A - HalloTermin (Abdul)]] |
| 84 checked Dresden places (doctors, pharmacies, banks, Ausländerbehörde, community) and 4 guides in Arabic, Turkish, Ukrainian | [[RUN-011 Resource spot-check]], [[Merged Concept]] |
| Interface in 6 languages for Sunday (EN, DE, RU, UK, AR, TR); content in 13 language codes | [[DEC-003 Merged concept]], [[Merged Concept]] |
| Voice input: all 13 language codes accepted, first text after 1.2 s | [[RUN-014 Relay v2 generic tasks]] |
| Free-text request → task draft in 4–9 s | [[RUN-013 n8n v2 workflows]] (Haiku 4.5: 3.9–9 s) |
| n8n + Claude write the German call brief in 10 s or less | [[RUN-006 Full loop DB to n8n to Claude to DB]], [[RUN-013 n8n v2 workflows]] (9 s) |
| Role-play calls with a synthetic German receptionist: booked in 70–95 s; said no to a Saturday slot outside the approved window; read the slot back before booking | [[RUN-012 Automated receptionist role-play]] (70 s, 77 s), [[RUN-014 Relay v2 generic tasks]] (79 s, 86 s, 95 s) |
| Asked "Are you an AI?", the agent said: *"Ja, genau, ich bin eine KI."* Pharmacy role-play completed in 80 s | [[RUN-014 Relay v2 generic tasks]] |
| Turn latency 1.4–2.9 s; our target (p50 ≤ 0.8 s) is not met yet. Say it only if asked | [[RUN-014 Relay v2 generic tasks]] |
| Voice agent cost $0.050–0.163 per minute; a short call costs well under €1 including telephony | [[Idea A - HalloTermin (Abdul)]] |
| Sunday content target: about 40–60 family providers and about 10 events. **[Say the real count from the database]** | [[Merged Concept]] |

**Do not say:**
- "It works with real practices / real courses." We have role-plays only.
- "It is legal" or "fully compliant". Say: "We built it for these rules. This is general information, not legal advice."
- Any number for a course call **[until a `course_enquiry` run note exists in `Runs/`]**. The call template exists in the relay (`task-templates.js`), but it has no run note yet.

---

## 1. 30-second pitch (about 85 words)

"Maria just moved to Dresden. Her child is four. She finds a music course in Russian, and the page says: *'Call us for a trial lesson.'* In German. This is where many parents stop.

Dresden mit Kind is one place for international parents: courses, events, communities and guides, in their own language. On every page there is a button: **Ask for me**. An AI assistant phones the place in German, says it is an AI, and brings the answer back in Russian.

We are looking for pilot partners: universities, employers, the Welcome Center."

*Who says it:* Anastasia when the room is about families; Abdul when someone asks about the tech. Same words.

---

## 2. Pod pitch: 5 minutes (Anastasia + Abdul)

For any pod slot, or anyone who has not heard the merged idea. Pod format: *what do we build, who is the user, what is the hypothesis.* Feedback: *I like / I wish / What if* ([[Weekender Build - Event Format]]).

### 2.1 The user (0:00–0:45) · Anastasia
"Hi, I'm Anastasia. I run Dresden mit Kind, a guide for international families in Dresden.
Our user is Maria. She is in her thirties, she moved here for her partner's job, and her child is four. Her German is A1 to B1.
She wants three things: activities for her child, people who speak her language, and to know the deadlines for Kita and school before she misses them.
Today this information is spread over German websites, Facebook and Telegram groups. And when she finally finds a good course, the page says: *'Call us.'* In German, during work hours. That is where she stops."

*Note:* Maria is a proto-persona. Say so if asked. We still need to talk to real parents (the PRD plans 8–10 interviews).

### 2.2 What we build (0:45–1:40) · Abdul
"I'm Abdul. I built HalloTermin, an assistant that makes phone calls in German for newcomers.
Yesterday these were two ideas. Now it is one product: **Dresden mit Kind**, with a feature called **Ask for me**.
It works in four steps: **Discover, Understand, Act, Result.**
Maria finds the course in our directory. She taps *Ask for me*. The question is already filled in: *'Is there a free spot or a trial lesson for my four-year-old on Tuesday or Thursday afternoon?'*
Before anything happens, she sees exactly what the assistant will say in German, and she approves it.
The assistant calls. In its first sentence it says it is an AI. It asks the questions, and it books a trial lesson only inside the times Maria approved.
Maria gets the answer in Russian. And the course page now shows *'checked by phone today'*, so the next parent sees fresh information."

### 2.3 What is inside (1:40–2:20) · Anastasia
"The home page has five pillars: courses and activities, events, bilingual communities, a library with guides, and Health & services: doctors, pharmacies and the Ausländerbehörde.
On Sunday the interface is in six languages: English, German, Russian, Ukrainian, Arabic and Turkish. Native speakers from my communities check the Russian, Ukrainian and Arabic texts.
I choose the first providers and communities from my own network. So the directory is not empty on day one."

### 2.4 The hypothesis (2:20–3:05) · Abdul
"Our hypothesis has two parts.
**One:** if parents can find courses and communities by child age and language in one place, they will use it to act, not only to read.
**Two:** if the assistant says honestly that it is an AI, says why it calls in under 10 seconds, and already knows the facts, then the person at the course or practice stays on the line and gives a clear answer.
This weekend we can test part two, with role-play calls. Our targets: purpose stated in under 10 seconds, answer in under 90 seconds.
What would prove us wrong: the person hangs up after *'I am an AI'*, or the assistant writes down something that nobody said."

### 2.5 What already works (3:05–4:05) · Abdul, then Anastasia
**Abdul:** "Everything here has a test note in our vault.
- A request in the user's own language becomes a task in 4 to 9 seconds.
- n8n and Claude write the German call brief in about 10 seconds.
- In role-plays with a synthetic German receptionist, the assistant booked in 70 to 95 seconds. It said no to a Saturday slot that Maria had not approved, and it read the slot back before it said yes.
- We also found real problems. Once it made up a doctor's name from a word it heard wrong. Once it took *'Auf Wiederhören'* as a yes. We fixed both and tested again.
- 84 checked Dresden places and 4 guides in Arabic, Turkish and Ukrainian are already in the database."

**Anastasia:** "What is not done yet: **[the app screens in Lovable: status on the day]**. **[No course call has been tested yet: status on the day.]** There is no real phone line. For the demo we call in the browser, and I play the course on the other end."

### 2.6 Ask for feedback (4:05–5:00) · Anastasia
"Please give us feedback in three parts:
- **I like:** what should we keep?
- **I wish:** what is not clear or not believable yet?
- **What if:** one idea we have not thought about."

Three questions we want answers to:
1. As a parent: would you let an AI call a course or a Kita for you, if it says it is an AI?
2. Is a course the right first example? Or is the Kita waiting list or the Kinderarzt more painful?
3. Do you know an international parent or a course provider we can talk to today?

---

## 3. Sunday demo run-sheet: 3 minutes (13:00)

### 3.1 Roles
| Person | Role |
|---|---|
| **Abdul (presenter)** | Talks and drives the projector laptop: app, relay window, Pixel Agents, backup video. Per [[Agent Space - Who Does What]]. |
| **Anastasia (receptionist)** | Plays "Olgas Musikstudio" in German. She speaks into the **mic of the projector laptop** during the browser call (relay page, `services/voice-relay`). She uses the card in 3.4. |
| **Pod volunteer (clock)** | Holds up signs at 2:00 and 2:30. Ask for one at Pod #04. |

### 3.2 Setup and checklist (start at 12:30)
- **One laptop** on the projector, Chrome (not the in-app browser pane: it blocks the mic).
  - Window 1 tabs: (1) the Lovable app on its own URL, interface in **Русский**; (2) n8n canvas.
  - Window 2 tabs: (3) relay page **[http://127.0.0.1:8787 or the hosted relay URL]**; (4) Pixel Agents `http://127.0.0.1:3100`; (5) backup video, paused at 0:00; (6) `/r/00000000-0000-0000-0000-000000000002`.
- **Audio:** the laptop sound goes to the room speaker, so the audience hears the agent. Anastasia uses a close mic (headset or USB) on the same laptop. The relay page has echo cancellation on. **Test at Pod #04 whether the agent hears itself.** If it does, Anastasia wears headphones and the subtitles on screen carry the call.
- **Warm-up:** run one full request at 12:30 (wakes up the intake and n8n). Then set the demo provider's `last_checked_at` back to empty (data only, SQL editor), so the "checked by phone" badge **[if built]** appears fresh in the demo.
- **Pixel Agents:** `npx -y pixel-agents@1.4.1 --host 127.0.0.1 --port 3100`, labels on. At 12:55 start one small Claude task (for example a quick audit), so a character is working. No keys or tokens visible on any projected screen.
- **Hotspot** on the phone, tested.
- **Go / no-go at Pod #04 (10:00):** a live course call must pass there and be logged in `Runs/`. If not, the call beat uses the backup video (3.5) and everything else stays live.

### 3.3 Timings
| Time | Beat | Who | On screen | Presenter says (short) |
|---|---|---|---|---|
| 0:00–0:15 | **Problem** | Abdul | App home in Russian | "This is Maria. She is new in Dresden, her child is four, and she speaks Russian. She is looking for a music course." |
| 0:15–0:35 | **Discover** | Abdul | Courses: age 3–6, music, language Russian, district Neustadt → provider page "Olgas Musikstudio": ages, languages, "trial lesson on request", button **Ask for me** | "She finds the course in her language. And then the page says: call us." |
| 0:35–0:55 | **Ask for me + check** | Abdul | Tap *Ask for me* → request is prefilled (free spot or trial lesson, Tue or Thu afternoon) → approval card: German opening line with Russian below, facts (child's age only), time windows, consent → **Call now** | "Before anything happens, she sees exactly what it will say, including *KI-Assistentin*. She approves." |
| 0:55–1:05 | **Brief** | Abdul | `/r/:id` status changes to "briefed" (about 10 s). Copy the ID (Ctrl+L, Ctrl+C), switch to the relay window, paste, **Start call**, switch back | "Right now n8n and Claude write the German call brief." |
| 1:05–2:15 | **The call** | Anastasia + agent | `/r/:id`: German lines with Russian subtitles arrive live | "Listen to the first sentence." Then quiet. After the Saturday offer: "It said no. Maria did not approve Saturday." |
| 2:15–2:35 | **Result** | Abdul | Result card in Russian: trial lesson Thursday 16:30, bring indoor shoes, **Add to calendar**; provider page shows "checked by phone today" **[if built]** | "The answer is in her language. No audio was stored, only text. And the course page is now up to date for the next parent." |
| 2:35–2:50 | **Agent office** | Abdul | Pixel Agents tab | "This is our team: two humans and a small crew of AI agents. Each character is one Claude session. The label shows what it is doing right now. Every test they ran is written down in our notes." |
| 2:50–3:00 | **Ask** | Abdul (Anastasia joins) | App home | "We are looking for pilot partners (universities, employers, the Welcome Center) and for parents to test with. Thank you." |

Notes:
- If the call runs long, cut the agent-office beat, never the result card.
- Do not read slide text. The app is the demo.
- If the agent mishears something, let the read-back catch it. Say calmly: "This is why it repeats everything before it says yes."

### 3.4 Receptionist card (Anastasia)
Maria's approved windows: **Tue 29.09 and Thu 01.10, afternoon**. Wait for the agent's first sentence before you answer.

| # | Anastasia says | Meaning | The agent should… |
|---|---|---|---|
| 1 | "Olgas Musikstudio, guten Tag?" | Olga's music studio, hello? | say "KI-Assistentin von Maria Ivanova" in its first sentence and ask about a free spot or a trial lesson for a four-year-old |
| 2 | "Ja, ein Platz ist frei. Der Kurs ist auf Russisch und Deutsch. Eine Probestunde geht am Samstag um zehn Uhr." | Yes, there is a free spot. The course is in Russian and German. A trial lesson is possible on Saturday at 10. | say no to Saturday politely and ask for Tuesday or Thursday afternoon |
| 3 | "Oder Donnerstag um sechzehn Uhr dreißig?" | Or Thursday at 16:30? | read it back: "Donnerstag, 1. Oktober, 16:30 Uhr … richtig?" |
| 4 | "Ja, richtig. Bitte Hausschuhe mitbringen." | Yes, correct. Please bring indoor shoes. | confirm, note the indoor shoes |
| 5 *(only if the clock shows < 1:50)* | "Hat das Kind Allergien?" | Does the child have allergies? | not answer: "Das bespricht Maria gern selbst mit Ihnen." (no child health data) |
| 6 | "Auf Wiederhören." | Goodbye. | say goodbye and end the call |

Speak clearly, at normal speed. Say times as numbers ("sechzehn Uhr dreißig", not "halb fünf"): a price was misheard in [[RUN-014 Relay v2 generic tasks]]. More scripts: [[Receptionist Test Scripts]].

### 3.5 Backup plan
| Problem | What we do |
|---|---|
| Venue Wi-Fi slow or down | Switch to the phone hotspot. |
| The course call did not pass at Pod #04, or the agent is silent on stage | Say: *"The live voice part failed. Here is a recording from this morning."* Play the **backup video**: a full Maria run, recorded Sunday morning before the 12:00 code freeze. Then go on with the result beat. |
| We need to show a finished result without a live call | Open `/r/00000000-0000-0000-0000-000000000002`. This is a seeded, finished request from the Health & services pillar: Amina asked in Arabic whether a pharmacy has Ibuprofen 400. Result in Arabic, right to left: in stock, pickup until 18:30, about 3.49 EUR. Say: *"This is a finished request from our Health & services pillar, in Arabic."* Do not present it as Maria's course. |
| Prefill or intake is slow (more than 15 s) | Use "Fill in the details myself" and type the request. |
| The whole app is down | Backup video, then the n8n canvas and the Supabase table with real rows. |
| Anastasia loses her line | She reads the next line from the card. The agent waits. |

Rule: we decide at Pod #04 (10:00) which path is live and which is backup. We do not debug on stage.

---

## 4. Likely jury questions: short answers

**1. "Does the course know it is talking to an AI?" (EU AI Act)**
Yes. The first sentence of every call says it: *"Guten Tag! Hier ist die KI-Assistentin von Maria Ivanova."* EU AI Act Article 50(1) applies since 2 August 2026 and asks for this at the first contact. Maria sees the line on the approval card before the call. When the other side asked "Are you an AI?" in a role-play, it answered *"Ja, genau, ich bin eine KI"* ([[RUN-014 Relay v2 generic tasks]]). It calls *for* Maria; it never pretends to be her ([[AI discloses itself in first sentence]], [[Never impersonate the user]]).

**2. "Are you recording the call?" (§201 StGB)**
No. We never store audio, and we do not switch on recording in any tool. We keep a text transcript, and the agent can ask: *"Ist es in Ordnung, wenn ich das Gespräch für meine Nutzerin mitschreibe?"* If the answer is no, we keep only a short structured summary. Some lawyers see even live transcription as a grey area, so a lawyer check is in our [[Monday-Morning Plan]]. General information, not legal advice ([[Never store call audio]]).

**3. "You handle data about families and children. How?" (GDPR)**
As little as possible. From the child, the agent only says what Maria approved as a fact, usually the age. It never talks about health, allergies or development; if asked, it says *"Das bespricht Maria gern selbst mit Ihnen."* It never signs up the child, signs anything or agrees to a payment. For doctors we store a reason *category*, never symptoms, and n8n removes health words from free text (in [[RUN-013 n8n v2 workflows]] it removed "fever" from an Arabic request). The database is in the EU (Frankfurt). Honest limit: on Sunday the app runs in demo mode with fake data only; user accounts, owner-only access and data processing agreements are Monday items ([[Data minimisation - no symptoms]], [[Monday-Morning Plan]]).

**4. "Why not Google 'Call for Me' or AI Haggler?"**
Google Call for Me started on 24 Sept 2026 as a small test for US Pixel 11 owners with a paid Gemini plan. It is not in Germany. Google's calling in Search is for price checks with US local businesses. AI Haggler calls in 25 languages, including German, but it is a shopping and negotiation tool, and its own site calls it "very early stage" with about 20% of calls having significant issues. None of them helps a parent **find** the right course in Dresden first, calls from **her** language, brings the answer back in her language, and follows German rules ([[Competitive Landscape]]). The calling technology is not our moat. Our value is the local, checked directory, the trust of the parent communities, and partners who already serve these families.
*Careful:* Google also uses the words "Ask for Me" for its US calling feature in Search. If someone says so: "Yes, same words, different product. Our product is Dresden mit Kind; the button name can change."

**5. "A directory is empty on day one. How do you solve the cold start?"**
We start as a curated guide, not a review site. The PRD says it clearly: reviews and provider self-service are worth nothing without an audience, and an empty rating widget reduces trust ([[Idea B - Dies-Das-Ana-Nas]]). So: Anastasia's existing Dresden mit Kind catalog and her network, 84 checked service places, a crawler that finds family events (marked "please verify"), and a "Suggest a place" form. And every *Ask for me* answer writes "checked by phone on …" to the provider page, so each call keeps a listing fresh. Provider accounts come in phase 2, reviews in phase 3.

**6. "Who pays?" (business model)**
B2B2C first: organisations that already help international families but cannot make everyday calls for them. TU Dresden (the International Office and the DRESDEN-concept Welcome Center, which supports researchers and their families), employers who hire skilled workers (as a relocation benefit), and the Welcome Center Dresden. Later: paid provider listings (featured listings or provider subscriptions, phase 4 in the PRD), and pay per call for individuals as a fallback. One call is cheap: the voice agent costs $0.050–0.163 per minute, and our role-play calls lasted 70–95 seconds. We have no paying customer yet. Writing to 2–3 pilot partners is our next step ([[Monday-Morning Plan]]).

*Spare answers:*
- *"Was that a real call?"* A real German AI call in the browser, not a phone line. Anastasia played the course. We have not called real providers yet; the first real call will be with consent ([[Monday-Morning Plan]]).
- *"What if the course wants a firm booking or the waiting list?"* The agent says *"Danke, das macht Maria gern selbst. Wie geht das am besten?"* and brings back the next step. It only confirms a trial lesson inside Maria's approved times, after a read-back ([[Only book inside pre-approved windows]], [[Read-back before booking]]).

---

## 5. Slide outline: 5 slides

Style: one idea per slide, few words, real numbers with a source line. Follow the UI skills: warm and calm, no purple gradients, no glass effects.

| # | Title | Content | Source line |
|---|---|---|---|
| 1 | **"Call us for a trial lesson."** | The course page, with the German phone line. One number: 65% of immigrants in Germany name German as the biggest everyday obstacle. | OECD 2024 |
| 2 | **Who we build for** | Maria, 30s, new in Dresden, child aged 4, German A1–B1. Her pain: information spread over German sites and chat groups, and the phone call at the end. Small note: proto-persona. | [[Idea B - Dies-Das-Ana-Nas]] |
| 3 | **Find it. We call for you.** | The loop: Discover → Understand → Act → Result. Under it: Lovable app → Supabase (EU) → n8n + Claude → German voice agent → answer in the parent's language. Three labels: "says it is an AI" · "no audio stored" · "only the child's age". **[Update the archify diagram in `docs/diagrams/` for the merged flow.]** | own build |
| 4 | **Live demo** | Only the app URL, in large letters. | — |
| 5 | **What works, what is next** | Works: request → task in 4–9 s · German brief in ≤10 s · role-play calls booked in 70–95 s with read-back · 84 checked Dresden places · 6 interface languages. Next: real phone line (+49), first real calls with consent, lawyer check, parent interviews. **Ask: pilot partners and parents to test with.** | `Runs/` · [[Monday-Morning Plan]] |
