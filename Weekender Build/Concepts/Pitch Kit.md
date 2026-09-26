---
type: concept
tags: [pitch, presentation]
sources: []
---
> Superseded by [[Pitch Kit v2 (merged)]] (26.09)

# Pitch Kit

**What this is:** everything we need to talk about the project: the 5-minute pod pitch, the 30-second pitch, the 3-minute Sunday demo, jury questions and a slide outline.
**Why it matters for us:** the Sunday demo at 13:00 is 3 minutes. We want to say the same calm, true story every time.
**Related:** [[Idea A - HalloTermin (Abdul)]] · [[Merged Concept]] · [[Personas]] · [[Moment of Truth - First 15 Seconds]] · [[AI Disclosure]] · [[Weekender Build - Event Format]] · [[Agent Space - Who Does What]] · [[Monday-Morning Plan]]

> **Merge warning.** Idea B is not written yet. After the merge, parts of this note will change.
> - Text marked **[HT]** is HalloTermin-specific. Replace or cut it after the merge.
> - Text marked **[GENERIC]** is the frame that should survive any merge: *form → database → n8n + AI → result shown live*.
> - Every number here comes from [[Idea A - HalloTermin (Abdul)]] or from our own `Runs/`. Do not add numbers that are not in a source.

---

## 1. Pod #01 pitch — 5 minutes

Format from [[Weekender Build - Event Format]]: *what do I build, who is the user, what is the hypothesis.* Feedback in *I like / I wish / What if*.
The same script also works for later pod check-ins (shorten section 1.4 for Pod #02 and show the build instead).

### 1.1 What we build — 0:00–1:00
**[GENERIC]** "We build a small web app. You fill in one short form in English. The form goes into a database. An n8n workflow picks it up, an AI prepares the work, and the result comes back to your screen, live."

**[HT]** "Our first use case is HalloTermin. It is an AI assistant that phones a German doctor's practice for you. It speaks German, it books a slot inside the times you already approved, and it gives you an English summary. It says in the first sentence that it is an AI."

### 1.2 Who the user is — 1:00–2:00
**[HT]** "Our main user is Priya. She is 24, from Pune, and studies Nanoelectronics at TU Dresden. Her German is A1. The practice near her only books by phone. When the receptionist speaks fast, she freezes. She has already hung up twice. She says: *'I can write a thesis in English, but I can't book a doctor.'*"

"She is a proto-persona. We built her from public data, and we still need to check her with real people this weekend."

Scale (all from [[Idea A - HalloTermin (Abdul)]]):
- About 402,000 international students in Germany, winter semester 2024/25 (DAAD).
- TU Dresden: about 29,000 students, 18.9% with a foreign nationality (TU Dresden).
- In the OECD survey, 65% of immigrants in Germany name lack of German as the biggest obstacle in everyday life.

Later users (not in the MVP): **Amina**, a family-reunion spouse who needs an Arabic or Turkish UI, and **Marco**, a Blue Card engineer whose employer might pay.

### 1.3 The hypothesis — 2:00–3:00
**[GENERIC] pattern:** "If a newcomer can hand a stressful German task to a form plus an AI, then they will get it done faster and with less stress than doing it alone."

**[HT] our version:** "If an AI assistant says honestly that it is an AI, states the purpose in under 10 seconds and already knows all the facts, then a German receptionist will stay on the line and book the appointment."

How we will test it this weekend:
- Pickup → purpose stated: target under 10 seconds.
- Pickup → booked slot: target under 90 seconds.
- Role-play calls with a German-speaking "receptionist", logged in `Runs/`.

What would prove us wrong: the receptionist hangs up after the disclosure, or the agent books a time the user did not approve.

### 1.4 What already works — 3:00–4:00
Only things with a run note:
- **Full loop, database → n8n → Claude → database:** a new request becomes a German call brief in **10 seconds or less** ([[RUN-006 Full loop DB to n8n to Claude to DB]]).
- **German voice round trip with Deepgram:** our German opening line, spoken by the German voice `aura-2-viktoria-de` and transcribed again, came back with **99.8% confidence** in 7.5 seconds. One error: the name **"Priya" was heard as "Kria"**. Our fix: give the transcriber the name as a keyword, and let the agent spell names with the German spelling alphabet ("P wie Paula") ([[RUN-008 Deepgram German round trip]]).
- **Newcomer resource crawler:** 23 checked rows (doctors, pharmacies, banks, Ausländerbehörde) and 1 sourced guide in the database ([[RUN-007 Newcomer crawler first run]]).
- **Built, not yet logged as a run:** a browser call with the German voice agent (`services/voice-relay`), which writes the transcript as text only, never audio.
- **Not done yet:** the Lovable app (empty shell, paused until the merge), a real phone line, English subtitles.

"Honest summary: the back end works. The front end is waiting for the merge."

### 1.5 Ask for feedback — 4:00–5:00
"Please give us feedback in three parts:"
- **I like** — which part should we keep, whatever we merge?
- **I wish** — what is not clear or not believable yet?
- **What if** — one idea we have not thought about.

Questions we would like answers to:
1. Would you trust an AI to call a doctor for you, if it says it is an AI?
2. Is the doctor call the right first use case, or is something else more painful?
3. Do you know a newcomer we can talk to today?

---

## 2. 30-second elevator pitch

**[HT]** (about 80 words, based on the pitch in [[Idea A - HalloTermin (Abdul)]]):

"Imagine you are sick in Dresden and you don't speak German. The practice only books by phone. Someone answers in fast German, you freeze, you hang up. That is normal life for many of the about 400,000 international students in Germany. HalloTermin makes the call for you. You type your request in English. Our AI assistant says it is an AI, speaks German, books a time you approved, and sends you an English summary. We are looking for pilot partners: universities, employers, welcome centres."

**[GENERIC] fallback, if the merged idea is different:**
"Newcomers in Germany lose hours on tasks that are easy in their own language and hard in German. We built one short English form. Behind it, n8n and an AI do the German part and show you the result live. Today we show it with [use case]. We are looking for [partner]."

---

## 3. Sunday demo run-sheet — 3 minutes (13:00)

### Roles
| Person | Role |
|---|---|
| **Presenter** (Abdul, per [[Agent Space - Who Does What]]) | talks, fills in the form, drives the laptop |
| **Receptionist** (a German speaker: teammate or a pod volunteer, briefed at Pod #04 rehearsal) | plays "Praxis Dr. Weber", speaks German into the headset or phone |
| **Backup operator** (the other teammate) | keeps the backup video and the pixel office open in tabs, watches the clock, gives a 30-second sign |

**[HT]** The receptionist uses one prepared curveball: *"Sind Sie Neupatientin? Haben Sie eine Überweisung?"* and one offer inside the approved window, for example *"Dienstag, 8:15?"*

### Timings
| Time | Beat | Who | What the audience sees |
|---|---|---|---|
| 0:00–0:20 | **Problem** | Presenter | One sentence about Priya and one number (402,000 students). No slide text to read. |
| 0:20–0:45 | **Form** [GENERIC] | Presenter | Fill in the English form in the live app (own URL): practice, reason category, insurance, 2 time windows, consent box. Submit. |
| 0:45–1:00 | **Automation** [GENERIC] | Presenter | Status changes to "briefed" within about 10 s (RUN-006). Quick cut to the n8n canvas: "this is the workflow that just ran." |
| 1:00–2:05 | **The call** [HT] | Receptionist + agent | Receptionist picks up: "Praxis Dr. Weber, guten Tag?" The agent opens with the AI disclosure, answers the curveball, accepts the slot, reads it back. The screen shows the live German transcript (English subtitles if built). Presenter says only: "Listen to the first sentence." |
| 2:05–2:25 | **Result** | Presenter | Result card: booked slot, what to bring, English summary. Say: "No audio was stored. Only text." |
| 2:25–2:50 | **Agent office** | Presenter | Pixel Agents tab (`http://127.0.0.1:3100`): "This is our team: two humans and a small crew of AI agents." Point at one character working and its label. |
| 2:50–3:00 | **Ask** | Presenter | "We are looking for pilot partners and for newcomers to test with. Thank you." |

Notes:
- If the call runs long, cut the agent-office beat, not the result card.
- Clean the test rows out of the database before the demo (see RUN-006 observations).
- Use headphones for the browser call so the agent does not hear itself.
- Do not project Pixel Agents while a session shows keys or tokens.

### Backup plan
| Problem | What we do |
|---|---|
| Venue Wi-Fi is slow or down | Switch to the phone hotspot (prepared and tested at Pod #04). |
| Voice agent fails or is silent | Say "The live voice part failed, here is a recording from this morning" and play the **backup video** of a full successful run (record it Sunday morning, before the 12:00 code freeze). |
| Phone line (Twilio) not working | Use the browser call via the voice relay. This is the default anyway, until a phone line is proven. |
| The whole app is down | Show the backup video, then the n8n canvas and the Supabase table with real rows. |
| Agent mishears a name | It is a known issue (RUN-008). Say so calmly: "It spells names with the German alphabet for this reason." |

Rule: we decide at Pod #04 (10:00) which path is live and which is backup. We do not debug on stage.

---

## 4. Likely jury questions — short answers

**1. "Does the practice know it is talking to an AI?" (EU AI Act)**
Yes. The first sentence of every call is: *"Guten Tag, hier spricht die KI-Assistentin von Frau Priya Sharma."* EU AI Act Article 50(1) applies since 2 August 2026 and asks for disclosure at the first point of contact. We made it a rule, not an option ([[AI discloses itself in first sentence]]).

**2. "Are you recording the call?" (§201 StGB)**
No. We never store audio and we do not switch on recording. We keep a text transcript, and the agent asks: *"Ist es in Ordnung, wenn ich das Gespräch für meine Nutzerin mitschreibe?"* If the answer is no, we keep only a short structured summary. Some lawyers say even live transcription is a grey area, so this is general information, not legal advice ([[Never store call audio]]).

**3. "You handle health data. How?" (GDPR)**
We collect as little as possible. The form asks for a reason *category* like "first examination", never symptoms (GDPR Art. 9). Our database is in Frankfurt. For a real product we would use EU endpoints where they exist and sign data processing agreements with each vendor ([[Data minimisation - no symptoms]]).

**4. "Why not just use Doctolib?"**
Doctolib only works where the practice has opted in. Many practices, especially family doctors and specialists, still book by phone only. We cover exactly those. Also, the 116117 service does not take language into account when it arranges appointments (KV Berlin).

**5. "Who pays?"** (business model)
Mainly organisations that already help newcomers: universities (for example an international office), employers who hire skilled workers (as a relocation benefit), welcome centres and integration-course providers. A pay-per-call option for individuals is the fallback. The Deepgram Voice Agent costs about $0.050–0.163 per minute, so one short call costs well under €1 including telephony (source: [[Idea A - HalloTermin (Abdul)]]). We have no paying customer yet; finding pilot partners is our next step.

*Spare answers if asked:*
- *"What if the practice wants to talk to the patient?"* The agent offers a callback number. A live interpreter mode is on the roadmap, not built.
- *"Can the agent book the wrong time?"* The server rejects any slot outside the approved windows, and the agent reads the slot back before it ends the call ([[Only book inside pre-approved windows]], [[Read-back before booking]]).

---

## 5. Slide outline — max 5 slides

Style: one idea per slide, few words, no hype words, real numbers with a source line at the bottom. Follow the UI skills (no purple gradients, no glass effects).

| # | Title | Content | Source line |
|---|---|---|---|
| 1 | **The problem** [HT] | "The practice only books by phone. The receptionist speaks fast German." 402,000 international students in Germany · 65% of immigrants name German as the biggest everyday obstacle. | DAAD/DZHW 2025 · OECD 2024 |
| 2 | **Who we build for** [HT] | Priya, 24, MSc student at TU Dresden, A1 German. Quote: "I can write a thesis in English, but I can't book a doctor." Small note: proto-persona. | [[Personas]] |
| 3 | **How it works** [GENERIC] | One diagram: English form → Supabase → n8n + Claude → German call → English result. Label: "no audio stored". Use the archify diagram from `docs/diagrams/`. | own build |
| 4 | **Live demo** | Only the app URL in large letters. Nothing else. | — |
| 5 | **What works and what is next** | Works: full loop ≤10 s (RUN-006) · German voice 99.8% confidence (RUN-008). Next: German phone number, English subtitles, interviews with newcomers, pilot partner. Ask: "Pilot partners and test users." | `Runs/` · [[Monday-Morning Plan]] |

Words to avoid on slides and in speech: revolutionary, game-changer, seamless, cutting-edge, disrupt, magic. Say what it does instead.
