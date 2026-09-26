---
type: run
date: 2026-09-26 19:30
by: claude (relay builder agent, for abdul)
result: pass
build: services/voice-relay v2 (task-templates.js, record_result, /listen, Flux flag) on test instances :8788 (nova-3, viktoria) and :8789 (flux-general-multi, elara)
---
# Run: Relay v2 generic tasks

## Goal
Relay works from the structured task fields of [[Frontend and UX Plan v2]] (D2, F, H): per-task agent, `record_result` for information tasks, F6 warm-default disclosure, realism rules, `/listen` intake STT in the user's language, Flux behind a flag.

## Steps
1. Two fresh tasks via anon REST insert: doctor `59688767-2dfb-4c58-b41d-6b10cbe0d7b5` (pronoun fact "she", window Tue 29.09 08–12), pharmacy `db40a58d-e83f-4ea1-b76e-52487f0e9bce` (user_language ar, fact medicine "Ibuprofen 400, 20 Tabletten", no pronoun).
2. `node probe-listen.js` (listen models + STT language codes).
3. `node roleplay-test.js <doctor>` on nova-3 and on Flux; `node roleplay-pharmacy.js <pharmacy>` (3 runs).
4. `node listen-test.js ar|tr|de …` with public Wikimedia Commons samples (Arabic spoken article, Turkish Airlines cabin announcement) and Aura TTS for German.
5. `node selftest.js <doctor>`.

## Result
| Test | Outcome | Notes |
|---|---|---|
| Doctor role-play, nova-3 / viktoria | ✅ booked, 79 s | greeting "…KI-Assistentin von Priya Sharma. Ich rufe für sie an, weil ihr Deutsch…"; refused Sat 17:00; read-back; `booked_slot` 2026-09-29 07:00 UTC (= 09:00 Berlin); `result {result_type:booking}`; `disclosure_variant = warm_default` |
| Doctor role-play, **Flux** `flux-general-multi` / **elara** | ✅ booked, 86 s and 95 s | German STT fine; turn latency 1.42–2.89 s (p50 ≈ 1.56 s) |
| Pharmacy run 1 | ✅ completed | but end_call summary overwrote the result summary → [[DEF-016 end_call summary overwrites record_result summary]] |
| Pharmacy run 2 | ⚠️ completed | STT heard "drei Euro neunundvierzig" as "Euro drei"; the read-back said "drei Euro", scripted pharmacy confirmed → price 3 (read-back did its job; the script can't correct). Agent recorded `can_reserve: true` from "Gerne, auf Wiederhören" → [[DEF-015 record_result invents answers from a goodbye]] |
| Pharmacy run 3 (after fixes) | ✅ completed, 80 s | honest "Ja, genau, ich bin eine KI."; "Moment bitte" → "Ja, gern, ich warte."; `result {result_type: stock_check, in_stock: true, price_eur: 3.49, pickup_until: "18:30"}`; request `completed`; neutral greeting (no pronoun fact); 0 bracketed lines saved; nova-3 latency 1.37–2.34 s (closing turn 5.1 s) |
| `/listen` ar | ✅ 7 final segments, first text after 1.2 s | correct Arabic text |
| `/listen` tr | ✅ 2 finals, first text 1.2 s | correct Turkish ("Sayın yolcularımız …"); the Izmir metro sample had almost no speech (0 finals) |
| `/listen` de (Aura TTS) | ✅ exact text | foreign Origin → 403, `lang=xx` → 400 |
| STT language codes | ✅ all 13 accepted | en ar tr uk ru fa hi es fr pl vi zh zh-CN de (+ multi) |
| selftest | ✅ | greeting + 10.8 s agent audio |

**Flux:** works in the Voice Agent, but only without `agent.language` (Deepgram: "Cannot specify agent.language when using the Deepgram V2 (Flux) listen API") → [[DEF-017 Flux rejects agent.language]]. Latency is similar to nova-3 in these runs; think (Claude Sonnet 5) dominates, so the F3 target (p50 ≤ 800 ms) is **not** met with either. Next lever: `THINK_MODEL=claude-haiku-4-5` (probe first, [[DEF-008 Deepgram managed model list differs from docs]]).

Other bugs fixed: [[DEF-014 Agent speaks after goodbye]], turn latency was never logged (Deepgram sends `total_latency` in `LatencyReport`, not `AgentStartedSpeaking`; now event `turn_latency`).

## Open
- Numbers: agent still sometimes says "am Dienstag, dem 29. September" (digits come from the n8n brief). TTS reads it fine.
- The n8n brief for the doctor task still says "Geburtsdatum: unbekannt" although `allowed_facts` has the DOB — prompt says FAKTEN win; brief generalisation is the n8n agent's job.
- Human A/B of viktoria vs elara still to do (UX plan F1). Restart the **voice-relay** preview to load v2.
- Test tasks are left in the DB (doctor = booked, pharmacy = completed).

## Defects found
- [[DEF-014 Agent speaks after goodbye]]
- [[DEF-015 record_result invents answers from a goodbye]]
- [[DEF-016 end_call summary overwrites record_result summary]]
- [[DEF-017 Flux rejects agent.language]]
