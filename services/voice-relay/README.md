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
| `ALLOWED_ORIGINS` | the relay's own page | exact origins, comma list (e.g. a custom domain). Applies to `/call` and `/listen`. |
| `ALLOWED_ORIGIN_SUFFIXES` | `.lovable.app,.lovableproject.com` | also accept any `https://<sub><suffix>` origin (Lovable preview + published URLs). Only https, no port, a real subdomain (`evil-lovable.app`, `lovable.app.evil.com`, `http://…` are refused). **Every** Lovable-hosted app matches, so once the project URL is fixed, set `ALLOWED_ORIGIN_SUFFIXES=` (empty) and put the exact URL in `ALLOWED_ORIGINS`. Requests without an Origin header (scripts) stay allowed; UUID check + call cap unchanged. |
| `MAX_CONCURRENT_CALLS` | `3` | shared by `/call` and `/listen` |
| `MAX_LISTEN_SECONDS` | `120` | hard cap per `/listen` session |
| `SILENCE_LIMIT_MS` / `HOLD_LIMIT_MS` | `30000` / `90000` | silence → `no_answer` (or `failed` if the other side had already spoken); raised to the hold limit after "Moment bitte" |

## Task types — `task-templates.js`
One object per `task_type` (doctor_appointment, authority_appointment, landlord_request, contract_question, bank_enquiry, pharmacy_question, restaurant_booking, **course_enquiry**, **kita_enquiry**, other_call). Each template defines: the German purpose clause for the greeting, a German fallback goal (used when n8n has not written `goal_de`), whether doctor fields are used, which functions apply, the success outcome, the `record_result` type/hint, and extra German rules (e.g. contract = information only, pharmacy = no medical advice, landlord = never rent/contract). Optional: `rules` as a function `(req, h) => [...]`, placeholders `{reason}` / `{person}` (sie / er / Frau X / the name), `bookingKind` (stored as `result.booking_kind`), `bookingDetails: true` (confirm_booking also takes `details`), `keyterms` (STT hints).

### Family task types (Dresden mit Kind, DEC-003)
| | `course_enquiry` (kids' course: music, dance, sport, swimming, art, language …) | `kita_enquiry` (Kita / Kita office) |
|---|---|---|
| Greeting ends with | "… und wollte fragen, ob es in Ihrem Kurs für Sechsjährige noch einen Platz oder eine Probestunde gibt." | "… und wollte fragen, ob Sie ab Januar 2027 einen Betreuungsplatz für ein zweijähriges Kind haben und wie man auf die Warteliste kommt." |
| Facts used | `child_age` ("6", "6 Jahre", "2,5", "18 Monate", "sechs"), `language_preference` | `child_age` or `child_birth_month`, `start_month` ("2027-01", "Januar 2027", "02/2027"), `language_preference` |
| Booked (inside a window) | trial lesson → `confirm_booking` (`booking_kind: trial_lesson`, `bring_items`, other answers in `details`) | visit / open day → `confirm_booking` (`booking_kind: kita_visit`, other answers in `details`) |
| Otherwise | `record_result {result_type: course_availability, free_spot, trial_lesson, trial_slot_text, waiting_list, schedule_text, price_text, language_of_instruction, next_steps}` → completed | `record_result {result_type: kita_availability, places_available, from_month, waiting_list_possible, how_to_apply, visit_possible, visit_text, languages, next_steps}` → completed |
| Extra rules | one question at a time (place → trial → waiting list → times/price/language); open points before the read-back; never a binding registration, contract or payment; child facts only from FAKTEN, never health/development; a trial offer or "Ja, gern" is not a free spot (DEF-028) | order place → waiting list/allocation → languages (if a preference is given) → visit; never registers or claims a registration (Dresden: usually the city's online portal — asked, not explained); never health/Förderbedarf/Integrationsplatz; a visit is not a free place |

Age words are spelled out for TTS ("Sechsjährige", "zweieinhalbjähriges"); unclear age text is left out of the greeting (it stays in FAKTEN). Before `confirm_booking` the agent says "Wunderbar, ich notiere das." (before `record_result`: "Danke, ich notiere das.") so the other side is not left in silence while the result is written (DEF-025). Test tasks are created like any task (`task_type`, `allowed_facts` with `child_age`, `time_windows`); `resource_id` from the prefill is only stored on the row (the DB trigger sets the resource's "checked by phone" badge when the call ends).

`buildAgent(req)` in `server.js` combines the template with the row:
- **Greeting** = UX plan F6 "warm default" (`calls.disclosure_variant = 'warm_default'`): "Guten Tag! Hier ist die KI-Assistentin von *Name*. …". Gendered words ("für sie", "ihr Deutsch") only if an `allowed_facts` entry `pronoun` (she/he) exists; "Frau/Herr *Surname*" only from a `salutation` fact; otherwise neutral with the name.
- **Prompt**: `goal_de` (else template goal), facts **only** from `allowed_facts` (+ doctor fields for doctor tasks), constraints (time windows, `party_size`, `budget_max_eur`, `deadline`, `notes_de`), the n8n `call_brief_de` (AUFGABE/FAKTEN/RAHMEN win on conflict), rules (honest "Ja, ich bin eine KI", never impersonate, never health details, read-back, only inside windows, ask when unsure, never invent names) and realism rules (≤ 2 sentences, natural acknowledgements, numbers as spoken, "Moment bitte" → wait, no bracketed stage directions).
- Text in `(…)`/`[…]`/`*…*` is stripped from lines before they are shown or saved; anything the model adds after its goodbye + `end_call` is dropped.

### Add a task type
1. Add the value to the `task_type` check constraint (new migration in `supabase/migrations/`).
2. Add one object to `TASK_TEMPLATES` in `task-templates.js` (copy the closest one).
3. Test: create a task row, then `node roleplay-test.js <id>` (appointment), a copy of `roleplay-pharmacy.js` (information) or of `roleplay-course.js` / `roleplay-kita.js` (booking with extra answers + side questions).

## Functions (what the agent can record)
| Function | For | Writes |
|---|---|---|
| `confirm_booking {date, time, bring_items?, doctor?, party_size?, details?}` | appointment tasks with time windows (`details` only for course/kita) | server rejects slots outside windows / bad dates / wrong party size; `calls.outcome='booked'`, `booked_slot` (Berlin → UTC), `bring_items`, `result {result_type:'booking', booking_kind?, date, time, …details}` (earlier `record_result` answers are kept); request `booked` |
| `record_result {result_type, details{}, summary_en}` | information tasks (pharmacy, contract, other; fallback for authority/bank/landlord/course/kita) | `calls.result = {result_type, …details}`, `outcome='completed'`, `summary_en`; request `completed`. **After a booking** it only merges the extra answers into `result`; the outcome stays `booked` |
| `needs_user {question}` | always | request `needs_user`, event |
| `end_call {outcome, summary_en}` | always | outcome ∈ booked, completed, rejected, rejected_no_new_patients, needs_user, failed (`completed` after a booking stays `booked`) |

Also: event `turn_latency` per agent turn (from Deepgram `LatencyReport.total_latency`), silence watchdog → `no_answer`; a call that stops without booking/result/`end_call` (silence after a conversation, the other side closes the page, Deepgram drops) → `failed` (or `needs_user` after `needs_user`) with an honest `summary_en`, never left `calling`; one console line per function call with its duration (the DB writes run in parallel). Anything the agent says after its goodbye is dropped, also when Deepgram sends `end_call` before the goodbye text (DEF-026). Rule: never two questions in one sentence; a single "Ja" to two questions is asked back, not recorded (DEF-027).

## `/listen` — intake voice input
`ws://<relay>/listen?lang=<code>`; browser sends 16 kHz mono linear16 (same worklet as calls), optional text `{"type":"stop"}` to flush.
Relay proxies to Deepgram streaming STT (`nova-3`, `interim_results`, `smart_format`) with the server-side key and sends back `{type:'transcript', text, is_final, speech_final}`, then `{type:'closed'}`. Nothing is stored.
Languages: en, ar, tr, uk, ru, fa, hi, es, fr, pl, vi, zh (→ `zh-CN`), de — all accepted by Deepgram (`node probe-listen.js`). Dari (`prs`) is text-only. Same Origin allowlist and cap as calls; unsupported language → 400.

## Tests (relay running; set `PORT` for a second instance)
- `node selftest.js [taskId]` — greeting + events, no DB outcome.
- `node roleplay-test.js <doctorTaskId>` — synthetic receptionist: out-of-window offer, in-window offer, read-back, booking.
- `node roleplay-pharmacy.js <pharmacyTaskId>` — "Sind Sie eine KI?", "Moment bitte", stock answer → `completed` + `calls.result`.
- `node roleplay-course.js <courseTaskId>` — music school: asks the child's age, offers a trial lesson on Saturday (outside), then a Thursday slot inside a window, confirms the read-back → `booked`, `booking_kind: trial_lesson`, slot checked against the windows, then waits for the parent-language `summary_user` (n8n 06). Needs `time_windows` (a Thursday one is preferred).
- `node roleplay-kita.js <kitaTaskId>` — Kita: no place before February, waiting list via the city's online portal, visit offered inside the first window → `booked` (`booking_kind: kita_visit`, place answers kept in `result`) or `completed` with `kita_availability`; also checks the agent never claims a registration.
- `node roleplay-curveball.js <courseTaskId>` — swim school with curveballs: "Hat das Kind gesundheitliche Probleme?" (agent declines without details), "Sind Sie ein Roboter?" (agent: yes, KI), only a Saturday trial lesson outside the windows, the first waiting-list question answered with "kein Platz frei" → `completed`/`needs_user`, never `booked`, no inferred `waiting_list: false`. Needs weekday-only `time_windows`. Exit code 0 = all checks passed.
- The role-play receptionists answer the agent's clarification questions ("habe ich richtig verstanden …?") with "Ja, genau." without using up a script line, and hang up when the script is done.
  Both scripts answer side questions (language, price, waiting list, open day) once when the agent asks, so they survive a different question order.
- `node origin-test.js` — Origin allow-list incl. suffix matching (probes `/listen?lang=xx`, so no Deepgram usage: passed = 400, blocked = 403).
- `node listen-test.js <lang> <file.raw | tts:Text>` — streams audio to `/listen`, also checks foreign Origin (403) and bad lang (400).
- `node probe-models.js …` / `node probe-listen.js` — which think / listen models and STT languages Deepgram accepts.

## Next
Twilio phone line (8 kHz mulaw), hosting (Docker / Render / Fly — see vault `Concepts/Relay Hosting Options.md`), signed token if exposed beyond localhost.
