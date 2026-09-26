# Monday-Morning Plan
What do we need so the build becomes something real?

> **Note:** this plan is written for **HalloTermin** ([[Idea A - HalloTermin (Abdul)]]). The product may change after we merge it with the teammate's idea ([[Merged Concept]]). The generic parts (auth, DPAs, EU hosting, accounts, costs) stay valid for any merged product; the telephony and pilot parts are HalloTermin-specific.
> Legal points are general information, not legal advice.

## What exists after Sunday
- **Supabase** (Frankfurt): schema, demo data, RLS in **demo mode** (anon can read all rows) — see [[Data Model]].
- **n8n Cloud**: workflow 01 (new request → Claude writes German call brief → back to DB) and workflow 02 (newcomer resources crawler). Exports in `n8n/workflows/`.
- **Voice relay** (`services/voice-relay`): browser mic ⇄ Deepgram Voice Agent in German, live text transcript and booking functions → Supabase. **No real phone line yet** (browser call only).
- **Lovable app**: the live URL from Sunday.
- Open defect: [[DEF-004 Supabase node stores jsonb payload as string]] (still open for workflow 01).
- Not built: real phone calls, user accounts, English subtitles in production, payments, other languages.

## Next 7 days
Goal of the week: **one real, consented call to one friendly practice**, on a setup that is safe for real personal data.

1. **Decide the product after the merge** (Mon). Write a decision note in `Decisions/`. If the merged product has no phone calls, skip steps 4–6.
2. **Auth + owner RLS** (Mon–Tue). Add Supabase Auth (email magic link is enough). Replace the demo policies with owner policies (`user_id = auth.uid()`) on `call_requests`, `calls`, `transcript_lines`, `events`. New migration file only. Re-run the RLS test as anon and as a second user. Remove demo data from production.
3. **DPAs and EU endpoints** (Mon–Wed). Sign / accept the data processing agreements (GDPR Art. 28) with **Supabase, Deepgram, n8n, Anthropic** (and Twilio, Lovable if they touch personal data). Switch the relay to the Deepgram EU endpoint (`wss://api.eu.deepgram.com/v1/agent/converse`). Check where n8n Cloud and the Claude calls (via n8n Gateway and via Deepgram "think") process data; write it down in a short record of processing.
4. **German +49 number** (Mon start, 2–3 business days review). Upgrade Twilio, submit the **regulatory bundle** (business registration + address proof), buy a German local number. Until then: test with a US number or a Twilio Verified Caller ID. Enable Germany in Twilio geo permissions.
5. **Phone leg for the relay** (Tue–Thu). Twilio Media Streams (8 kHz mulaw) → relay → Deepgram. Host the relay (Docker on Render/Fly or similar, see [[Relay Hosting Options]]). Keep "never store audio": no Twilio recording.
6. **Legal check of real-time transcription** (book on Mon, answer by Fri). Ask a lawyer (or a university legal clinic) one clear question: does live transcription without storing audio, with the consent line in the call, fit **§201 StGB**? Also check the AI Act Art. 50 opening line and the health-data minimisation (Art. 9). Until the answer: only structured summary, no stored transcript, on real calls.
7. **Real-practice test with consent** (Fri). Ask one practice we know (e.g. our own Hausarzt) in advance, explain the test, get a yes. One call, one booking or a clear "no". Write it up in `Runs/`.
8. **Fix DEF-004** in workflow 01 and repair old rows.
9. **Five user interviews** (any day): international students / spouses in Dresden. Do they trust an AI to call for them? What would they pay?
10. **Write to 2–3 pilot partners** (Wed–Thu, see below) with the demo video and a one-page summary.

## Who / partners
| Who | Why | First step |
|---|---|---|
| **TU Dresden International Office** | Thousands of international students; B2B2C channel | Email with demo video; ask for a 20-min meeting and 10–20 test users |
| **Welcome Center Dresden / city welcome service** (welcome@dresden.de) | Already helps newcomers; knows the pain points | Ask for feedback and whether they can share it with clients |
| **Employers hiring skilled workers** (e.g. Dresden semiconductor companies, via HR / relocation) | Could pay it as a relocation benefit — first B2B buyer | One HR contact, ask for a small pilot |
| Integration-course providers | Reach family-reunion spouses (later persona) | After the pilot, when other UI languages exist |
| **One friendly Arztpraxis** | Real-practice test with consent | Personal contact, ask before calling |
| **Lawyer / legal clinic** (IT + criminal law) | §201 StGB, AI Act, GDPR check | Book one consultation |
| Team | Abdul: relay, telephony, n8n. Teammate: depends on the merge (UI, partners, interviews). | Split in the Monday decision note |

## Risks & blockers
| Risk | Why it matters | What we do |
|---|---|---|
| **§201 StGB unclear** for real-time transcription | Lawyers disagree; worst case a crime | No audio ever; consent line in the call; summary-only until legal answer |
| **No German +49 number** without a registered business / address | +1 caller ID gets fewer answers; bundle review takes days | Start the bundle Monday; Verified Caller ID as interim |
| **Demo-mode RLS** still on | Anyone with the anon key can read all rows | Auth + owner RLS before the first real user (step 2) |
| **Health data (GDPR Art. 9)** | Reason for visit is health data | Reason category only, no symptoms; DPAs; EU endpoints |
| **Practices hang up on bots / insist on the patient** | Core value fails | Polite disclosure, read-back of the slot, "connect the user" fallback |
| **Names and Saxon dialect** misheard | Wrong booking | Keyterm prompting, spell names ("P wie Paula") — see [[RUN-008 Deepgram German round trip]] |
| **AI confirms a slot that was not booked** | Patient misses care | Server rejects slots outside approved windows; receptionist must confirm the read-back |
| **Product changes after the merge** | Some of this plan may be wasted | Do generic items first (auth, DPAs, accounts), telephony after the decision |
| Trial accounts expire (below) | Live URL or workflows stop | Decide keep / export before the dates |

## Cost / accounts to keep
**Per-call cost (from our research, not measured yet):**
- Deepgram Voice Agent: **$0.05–0.16 per minute** (depends on tier). New accounts get $200 free credit.
- Twilio → German mobile $0.042/min, landline $0.0283/min. German local number $1.35/month.
- Claude for the call brief: small per request — measure on the first real calls instead of guessing.
- Rough rule from the idea doc: a 3-minute booking call is well under €1 including Twilio. We will log real minutes per call in `calls` to confirm.

**Accounts and what expires:**
| Account | Status after the event | Action |
|---|---|---|
| **n8n Cloud** | Trial, **about 1 month** | Before it ends: pay, or self-host (see `n8n-self-hosting`); workflows are exported in `n8n/workflows/` |
| **Lovable** | Event credits, **about 30 days after the event** | Decide: paid plan, or keep the GitHub-synced code and host elsewhere |
| **Twilio** | Trial expires after 30 days, calls only to verified numbers | Upgrade (needed anyway for +49 number) |
| **Deepgram** | $200 free credit | Keep; watch usage; use EU endpoint |
| **Retell** (if used) | $10 free credit | Only keep if DEC-001 chooses it |
| **Supabase** (Frankfurt) | Free tier | Keep; move to paid before real users if we need backups |
| GitHub repo + board | Free | Keep |

Owner of every paid account = one person, card and invoices in a shared place; secrets stay in env vars / Vault ([[No secrets in repo]]).

## 30 / 60 / 90 days
- **30 days:** auth + owner RLS live, DPAs signed, +49 number, relay hosted, legal answer on §201, 5–10 consented real calls, 1 pilot partner agreed.
- **60 days:** pilot with 10–20 users from one partner; English subtitles; measure success rate (booked / needs user / rejected) and cost per booked appointment from real data.
- **90 days:** decide go / no-go on the numbers. If go: pricing (B2B2C via universities, employers, welcome centers, with per-call consumer fallback), second UI language for family-reunion spouses, "connect the user" interpreter mode.
