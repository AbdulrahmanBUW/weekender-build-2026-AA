---
type: defect
date: 2026-09-26
status: open
severity: major
found_in: "[[RUN-022 UI plan v3 merged]]"
owner: n8n + relay builders (UI part done in plan v3)
---
# Defect: Non-Latin names reach the German greeting

## Observed
One POST to the live intake webhook (workflow 04) on 26 Sep with Russian text that contains the parent's name ("Здравствуйте, я Мария Иванова. Моей дочери 4 года…") returned:
- `person.name = "Мария Иванова"` and a fact `parent_name = "Мария Иванова"`;
- `opening_de = "Guten Tag! Hier ist die KI-Assistentin von Мария Иванова. Ich rufe für Мария Иванова an, …"`;
- `opening_user` (Russian) with "КИ-ассистентка": the German abbreviation "KI" copied instead of the Russian "ИИ".

The app inserts `person.name` as `call_requests.patient_name` (Plan v2 P4). The relay builds the spoken greeting from it (`services/voice-relay/server.js`: `const name = clip(req.patient_name || 'die Person', 80)`). There is no transliteration in the intake, in n8n 01 or in the relay. So the German voice gets Cyrillic (or Arabic) script in its first sentence, and the receptionist cannot write the name down. (The TTS output itself was not played in this run; the input to it is shown above.)

## Expected
The German greeting, brief and facts use the name in Latin letters as in the passport ("Maria Ivanova"). The user-language line uses the local word for AI (ru "ИИ", uk "ШІ", ar "الذكاء الاصطناعي", tr "yapay zekâ").

## Repro
POST to `https://arahmandeaxo.app.n8n.cloud/webhook/task-intake` (Origin `*.lovable.app`) with a Russian or Arabic sentence that includes a name → insert the draft as in Plan v2 P4 → start the call on the relay page → the first agent sentence contains the name in the original script. This hits the Sunday demo (Maria, Russian) and the Arabic persona Amina.

## Fix
1. **UI (in plan):** [[Frontend and UX Plan v3 (merged)]] P8 step 2: if the name has non-Latin letters, the approval card asks for "Your name in Latin letters, as in your passport" (Cyrillic prefilled by a letter map, editable). That value becomes `patient_name` and replaces the name in `opening_de` and in the facts.
2. **Intake 04 (proposed):** return `person.name_latin` (passport spelling) and use it in `opening_de`; in `opening_user`, translate "KI" into the user's language.
3. **Relay (proposed):** if `patient_name` contains non-Latin letters, greet with "meiner Auftraggeberin" instead of reading the raw script.

## Update 26 Sep 13:20 (verification, [[RUN-022 UI plan v3 merged]])
Live workflow 04 (version `de260485…`, updated 13:09 Berlin time) now covers point 2 in its own way. The prompt asks for names in Latin script ("Мария Иванова" -> "Maria Ivanova"), and a server-side replacement writes "ИИ" / "ШІ" / "AI" / "yapay zekâ" in `opening_user`. The same Russian test returned `person.name = "Maria Ivanova"` and `opening_de = "… KI-Assistentin von Maria Ivanova …"`, with "ИИ-ассистентка" in `opening_user`. The transliteration is done by the model, so it is not guaranteed; the UI guard (point 1) stays. Point 3 (relay) is still open. Status stays open until the relay fallback is in, or the team decides the two layers are enough.
