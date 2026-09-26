# voice-relay — browser call with the German AI assistant (any phone task)

Browser microphone ⇄ this relay ⇄ **Deepgram Voice Agent** (listen `nova-3` or Flux · think Claude via Deepgram · speak Aura-2 German).
The relay keeps the Deepgram key and the Supabase service key on the server, loads the task from `call_requests`, builds the agent per `task_type`, and writes the live transcript to `transcript_lines` (text only — never audio).
It also serves `/listen`: speech-to-text in the user's own language for the intake screen (nothing stored).

## Run
```bash
cd services/voice-relay
npm install
cp .env.example .env      # fill DEEPGRAM_API_KEY yourself; SUPABASE_SERVICE_ROLE_KEY optional
npm start                 # http://127.0.0.1:8787
```
Or in the Claude desktop app: preview **voice-relay** (`.claude/launch.json`). After pulling code changes, **restart the preview**.

Open http://127.0.0.1:8787, paste a task ID (or keep the demo ID), click **Start call**, and play the other side in German. Use headphones.
The page shows `task_type` + user language, and has a **Voice intake test** (pick a language, speak, see live text from `/listen`).

## Env vars (`.env`, gitignored)
| Var | Default | Notes |
|---|---|---|
| `DEEPGRAM_API_KEY` | — | required |
| `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | — | optional; without them: no-DB mode (demo patient, nothing saved) |
| `THINK_PROVIDER` / `THINK_MODEL` | `anthropic` / `claude-sonnet-5` | check with `node probe-models.js anthropic:<model>` |
| `SPEAK_MODEL` | `aura-2-viktoria-de` | `aura-2-elara-de` = calmer voice recommended in UX plan F1 (tested OK, RUN-014) |
| `LISTEN_MODEL` | `nova-3` | `flux-general-multi` = Flux (v2 listen API, `language_hints: ['de']`). Works in German (RUN-014). The relay then omits `agent.language` (Flux rejects it). |
| `PORT` | `8787` | |
| `ALLOWED_ORIGINS` | the relay's own page | comma list; add the Lovable domain when hosted. Applies to `/call` and `/listen`. |
| `MAX_CONCURRENT_CALLS` | `3` | shared by `/call` and `/listen` |
| `MAX_LISTEN_SECONDS` | `120` | hard cap per `/listen` session |
| `SILENCE_LIMIT_MS` / `HOLD_LIMIT_MS` | `30000` / `90000` | silence → `no_answer`; raised to the hold limit after "Moment bitte" |

## Task types — `task-templates.js`
One object per `task_type` (doctor_appointment, authority_appointment, landlord_request, contract_question, bank_enquiry, pharmacy_question, restaurant_booking, other_call). Each template defines: the German purpose clause for the greeting, a German fallback goal (used when n8n has not written `goal_de`), whether doctor fields are used, which functions apply, the success outcome, the `record_result` type/hint, and extra German rules (e.g. contract = information only, pharmacy = no medical advice, landlord = never rent/contract).

`buildAgent(req)` in `server.js` combines the template with the row:
- **Greeting** = UX plan F6 "warm default" (`calls.disclosure_variant = 'warm_default'`): "Guten Tag! Hier ist die KI-Assistentin von *Name*. …". Gendered words ("für sie", "ihr Deutsch") only if an `allowed_facts` entry `pronoun` (she/he) exists; "Frau/Herr *Surname*" only from a `salutation` fact; otherwise neutral with the name.
- **Prompt**: `goal_de` (else template goal), facts **only** from `allowed_facts` (+ doctor fields for doctor tasks), constraints (time windows, `party_size`, `budget_max_eur`, `deadline`, `notes_de`), the n8n `call_brief_de` (AUFGABE/FAKTEN/RAHMEN win on conflict), rules (honest "Ja, ich bin eine KI", never impersonate, never health details, read-back, only inside windows, ask when unsure, never invent names) and realism rules (≤ 2 sentences, natural acknowledgements, numbers as spoken, "Moment bitte" → wait, no bracketed stage directions).
- Text in `(…)`/`[…]`/`*…*` is stripped from lines before they are shown or saved; anything the model adds after its goodbye + `end_call` is dropped.

### Add a task type
1. Add the value to the `task_type` check constraint (new migration in `supabase/migrations/`).
2. Add one object to `TASK_TEMPLATES` in `task-templates.js` (copy the closest one).
3. Test: create a task row, then `node roleplay-test.js <id>` (appointment) or a copy of `roleplay-pharmacy.js` (information).

## Functions (what the agent can record)
| Function | For | Writes |
|---|---|---|
| `confirm_booking {date, time, bring_items?, doctor?, party_size?}` | appointment tasks with time windows | server rejects slots outside windows / bad dates / wrong party size; `calls.outcome='booked'`, `booked_slot` (Berlin → UTC), `bring_items`, `result {result_type:'booking',…}`; request `booked` |
| `record_result {result_type, details{}, summary_en}` | information tasks (pharmacy, contract, other; fallback for authority/bank/landlord) | `calls.result = {result_type, …details}`, `outcome='completed'`, `summary_en`; request `completed` |
| `needs_user {question}` | always | request `needs_user`, event |
| `end_call {outcome, summary_en}` | always | outcome ∈ booked, completed, rejected, rejected_no_new_patients, needs_user, failed |

Also: event `turn_latency` per agent turn (from Deepgram `LatencyReport.total_latency`), silence watchdog → `no_answer`.

## `/listen` — intake voice input
`ws://<relay>/listen?lang=<code>`; browser sends 16 kHz mono linear16 (same worklet as calls), optional text `{"type":"stop"}` to flush.
Relay proxies to Deepgram streaming STT (`nova-3`, `interim_results`, `smart_format`) with the server-side key and sends back `{type:'transcript', text, is_final, speech_final}`, then `{type:'closed'}`. Nothing is stored.
Languages: en, ar, tr, uk, ru, fa, hi, es, fr, pl, vi, zh (→ `zh-CN`), de — all accepted by Deepgram (`node probe-listen.js`). Dari (`prs`) is text-only. Same Origin allowlist and cap as calls; unsupported language → 400.

## Tests (relay running; set `PORT` for a second instance)
- `node selftest.js [taskId]` — greeting + events, no DB outcome.
- `node roleplay-test.js <doctorTaskId>` — synthetic receptionist: out-of-window offer, in-window offer, read-back, booking.
- `node roleplay-pharmacy.js <pharmacyTaskId>` — "Sind Sie eine KI?", "Moment bitte", stock answer → `completed` + `calls.result`.
- `node listen-test.js <lang> <file.raw | tts:Text>` — streams audio to `/listen`, also checks foreign Origin (403) and bad lang (400).
- `node probe-models.js …` / `node probe-listen.js` — which think / listen models and STT languages Deepgram accepts.

## Next
Twilio phone line (8 kHz mulaw), hosting (Docker / Render / Fly — see vault `Concepts/Relay Hosting Options.md`), signed token if exposed beyond localhost.
