---
type: concept
tags: [pitch, pod, deploy-check]
sources: ["[[RUN-023 Merged flow E2E]]", "[[RUN-024 n8n credit optimisation]]", "[[RUN-025 Data round 2 and review sheets]]", "[[Pitch Kit v2 (merged)]]", "[[Monday-Morning Plan]]", "[[Merged Concept]]"]
---
# Pod 03 Brief

**Definition:** what we say and show at **Pod #03 Scope/Deploy check, Sat 26.09, 19:30**. About 7 minutes (board card #21), then feedback as *I like / I wish / What if*.
**Why it matters for us:** this is the last check before Pod #04 (Sun 10:00, go/no-go) and the demo (Sun 13:00). We want honest scope feedback and answers to 3 open questions, not applause.
**Related:** [[Pitch Kit v2 (merged)]] · [[Merged Concept]] · [[Monday-Morning Plan]] · [[Relay Hosting Options]] · [[Competitive Landscape]] · [[Weekender Build - Event Format]]

> **Rules:** Abdul can run this alone; lines for Anastasia are marked *(if present)*. Every number comes from a Runs note. All calls so far are **role-plays**: nobody real was phoned. "Olgas Musikstudio" is a fictional demo listing. Text in **[square brackets]** gets filled in at 19:25.

---

## 1. 60-second status (read aloud)

"We are **Dresden mit Kind**: one place for international parents in Dresden. Courses, events, bilingual communities, doctors and guides, in six interface languages. On every listing there is a button, **Ask for me**: an AI phones the place in German, says it is an AI, and brings the answer back in the parent's language.

What works end to end today, on our live cloud database: a Russian-speaking parent asked about a real music course. n8n and Claude wrote the German call brief in **8 seconds**. In a role-play call with a synthetic receptionist, the assistant refused a Saturday slot she had not approved, read the Thursday slot back, and booked a trial lesson in **under 100 seconds**. The answer was there in Russian **8.5 seconds** after the booking, and the course page got its 'checked by phone' stamp.

The data is in: **162 places, 92 of them for families, 44 events, 8 guides**. What is missing is the face. The Lovable app is being built right now, and the voice relay still runs only on my laptop."

| What we claim | Evidence |
|---|---|
| Request on a real listing → German brief in 8.0 s | [[RUN-023 Merged flow E2E]] |
| Intake prefilled from a listing: answer in 8.9 s, listing id kept | [[RUN-023 Merged flow E2E]] |
| Course call booked in 99.5 s, Saturday refused, read-back before booking | [[RUN-023 Merged flow E2E]] |
| Turn latency 1.5–2.5 s (booking turn 4.8 s) | [[RUN-023 Merged flow E2E]] |
| Russian subtitles live (11/11 receptionist lines), Russian summary 8.5 s after booking, nothing invented | [[RUN-023 Merged flow E2E]] |
| About 9 cheap Claude calls per phone call (before: 17–22) | [[RUN-024 n8n credit optimisation]] |
| 162 places, 92 family rows (77 with a phone), 44 events to 29 Nov, 8 guides in 6 languages; demo listing exists | [[RUN-025 Data round 2 and review sheets]] |

Known small gaps: the last 1–2 assistant lines get no subtitle ([[DEF-049 Closing assistant lines after the outcome get no subtitle]]); test calls stamp real listings ([[DEF-047 Role-play calls mark real providers as checked by phone]]), so we only call the demo listing.

---

## 2. Status per Sunday deliverable

| # | Deliverable | Status | True today | Left before Sun 14:00 |
|---|---|---|---|---|
| 1 | Live build under its own URL (Lovable) | **In progress, biggest risk** | Only the P1 shell. Plan v3 prompts and string files (789 keys × 6 languages) are ready. Build **starts now** (card #22). **[At 19:25: which screens exist, is a URL published?]** | Knowledge text → prompts in order → publish. Own Supabase only, never Lovable Cloud |
| 2 | n8n workflow that moves data | **Done** | DB trigger → 01 brief, 04 intake, 05 live subtitles, 06 result in the parent's language. Live and exported to `n8n/workflows/` | Save credits. Do not run crawler 02 |
| 3 | AI function | **Done** | Claude (Haiku) turns free text in any language into a structured task, writes the German brief, translates and summarises, removes child health words | Watch the Haiku wording on stage |
| 4 | Live demo | **At risk** | Full loop proven in role-play (RUN-023). Demo listing *Olgas Musikstudio* exists. **Relay is local only** (binds `127.0.0.1`) | Host the relay or run it on the presenter laptop; go/no-go at Pod #04; backup video before 12:00 code freeze |
| 5 | Monday-Morning Plan | **Draft done** | [[Monday-Morning Plan]]: 7 days, partners, risks, accounts that expire | After the demo: tick what shipped |
| + | Mandatory skills | **In progress** | Security review and 2 archify diagrams exist, but from before the merge. Launch video not started | Refresh diagram + audit for the family tables; brag video Sun morning |

---

## 3. What we show (and the backup)

**Show (about 3 minutes):**
1. **The idea in one picture:** `docs/merged-concept.html` (the Discover → Understand → Act → Result loop). 30 s.
2. **How it is wired:** `docs/diagrams/architecture.html`. Say: "This is from before the merge; the family tables are added since." 30 s.
3. **One live call on the demo listing:** the task is prepared before the pod (see checklist). Start the scripted course role-play (`services/voice-relay/roleplay-course.js <id>`), then refresh `transcript_lines` in the Supabase table editor: German lines appear with Russian subtitles, then the result. Say: "The receptionist is synthetic. Nobody is phoned." 90 s.
   - *(if present)* Anastasia plays the receptionist live on the relay page instead, with the card in [[Pitch Kit v2 (merged)]] section 3.4. A pod member can also read the card.
4. **The app as it is right now:** Lovable preview. "This is two hours old." 30 s.

**Backup (do not debug in the pod):**
- Call fails or Wi-Fi drops → phone hotspot. Still failing → open [[RUN-023 Merged flow E2E]] in Obsidian: the result table and the Russian summary text.
- Supabase or n8n slow → show the n8n canvas (01 → 06) and the finished seeded request `…0002` (Amina, pharmacy, Arabic result) in the `call_requests` table.
- Lovable preview broken → skip it and say the status in one sentence.

**Checklist 19:00–19:25**
- `git pull`. Laptop charged, hotspot tested.
- Start the relay (`services/voice-relay`, own `.env`).
- Create one `course_enquiry` task on *Olgas Musikstudio* (Russian, Tue 29.09 + Thu 01.10, 15:00–18:00), the same way as RUN-023 step 2. Wait for `briefed`. **One call only**: each call costs about 9 Claude calls on low n8n credits.
- Tabs: merged-concept page, architecture diagram, Supabase table editor, n8n canvas, Lovable preview, RUN-023 (backup).
- After the pod: delete the test request (cascade) and reset `last_checked_at` / `last_check_outcome` on the demo listing.

---

## 4. Top 3 risks and what we do

| Risk | Why it matters | Mitigation |
|---|---|---|
| **1. No Lovable URL by 14:00** | The only success criterion | Build the demo path first: home → courses → provider page → Ask for me → result. Other pillars are simple lists from the same data. Publish a URL tonight, even if thin. Small follow-up prompts only (credits). Code freeze 12:00 |
| **2. Relay only on a laptop** | The live URL cannot start a call without it | Tonight: `HOST` bind + Render per `docs/deploy-relay.md`, warm it up before the demo. Fallback: relay and app on the presenter laptop in Chrome. Last resort: backup video. The public relay has no per-call token yet (Monday item), so we limit origins and keep it up only for the demo window |
| **3. Demo day breaks: credits or data** | Low n8n credits; test calls stamp real listings; the anon key can read test requests (demo-mode RLS) | Calls only on the demo listing. Max one rehearsal tonight and one at Pod #04. Crawler 02 stays off; kill switches in [[RUN-024 n8n credit optimisation]]. Before the demo: `last_checked_at` count must be 0 (or only the demo listing). Fake data only on the live URL |

---

## 5. Three questions for the pod

1. **Name clash.** Google uses the words "Ask for Me" for its US calling feature in Search ([[Competitive Landscape]]). Keep **Ask for me** as our button, or rename it now (for example "We call for you")? A rename is cheap tonight (3 UI keys × 6 languages) and expensive after the Lovable build.
2. **Relay hosting.** For a 3-minute demo: host the relay publicly tonight (Render free: stable URL, about 1 minute cold start), or run the call from the presenter laptop and use the public URL only for browsing? Has anyone got websockets working on Render, Railway or Vercel this weekend?
3. **Languages on stage.** We have 6 interface languages, but the Russian, Ukrainian and Arabic native-speaker review is still open. Show only Russian (Maria's story) plus one switch to Arabic for right-to-left? Or all six briefly? Does unreviewed text hurt trust with a jury?

---

## 6. Who says what (about 7 minutes)

| Time | Part | Abdul alone | *(if present)* Anastasia |
|---|---|---|---|
| 0:00–1:00 | 60-second status (section 1) | reads it | says the first paragraph (the parent's problem) |
| 1:00–2:00 | Deliverables table (section 2) | "Three of five done (Monday plan as a draft), the app in progress, the live demo at risk" | — |
| 2:00–5:00 | Show (section 3) | drives the laptop | plays the receptionist |
| 5:00–5:45 | Risks (section 4) | one sentence per risk | — |
| 5:45–7:00 | Questions (section 5) + feedback | asks, writes down | asks question 3 (languages) |

**Feedback capture** (copy into a `Memory/` note after the pod, as card #21 asks):

| I like | I wish | What if |
|---|---|---|
| | | |

Answers to the 3 questions: 1. ___ · 2. ___ · 3. ___
