---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[RUN-015 Family task types in n8n]]"
owner: claude
---
# Defect: Intake opening uses the example name

## Observed
With Claude Haiku 4.5, workflow 04 copied the prompt's example into `opening_de`: "Hier ist die KI-Assistentin von **Amina Haddad**. Ich rufe für Олена Коваленко an…", "…von **Maria Haddad**…", "…von **HalloTermin**…". Names in Cyrillic ended up inside the German sentence, and the Kita opening dropped "weil … noch nicht so gut Deutsch spricht". The approval card would show the parent a wrong name.

## Expected
`opening_de` names the principal exactly (person.name), in Latin script, with the task's purpose clause.

## Repro
Intake with the Russian music-course text or the Ukrainian Kita text from [[RUN-015 Family task types in n8n]] on the version before the fix.

## Fix
- System prompt: pattern with `<Name>` placeholders instead of a real example name; "never another name, never HalloTermin"; person.name and names in facts transliterated to Latin script ("Мария Иванова" → "Maria Ivanova").
- *Validate + Clean Draft*: course/kita openings are built deterministically from the facts (same clause as workflow 01); for other types the opening is rebuilt if it lacks the person's name, and "KI-Assistentin von HalloTermin/Amina Haddad" is replaced with the person's name; the example name in `opening_user` is replaced too.
Verified in 8 intake runs after the final revision (ru/uk/en): correct names every time.

## Verification follow-up (26 Sep, fixed)
Found in the verification section of [[RUN-015 Family task types in n8n]]:
- **No name yet:** `opening_de` became "Hier ist die KI-Assistentin von meiner Auftraggeberin. Ich rufe für meiner Auftraggeberin an, weil meiner Auftraggeberin noch nicht so gut Deutsch spricht" (wrong case; Russian prefill text without a name). Fix: *Validate + Clean Draft* builds "Guten Tag! Hier ist eine KI-Assistentin. Ich rufe im Auftrag einer Person an, die noch nicht so gut Deutsch spricht, …" for every task type; the model returns `""` when `person.name` is empty. A no-name example in the prompt had primed Haiku to use the neutral form for a named landlord request, so it was removed.
- **`opening_user` not faithful:** "КИ-ассистентка от HalloTermin", "the AI assistant from HalloTermin … he wanted" under a German line that says "KI-Assistentin von <Name>". Fix: the prompt asks for a faithful translation ("AI assistant OF <Name>", local word for AI: ru ИИ, uk ШІ, ar الذكاء الاصطناعي, tr yapay zekâ); code replaces a leftover "KI" (ru/uk/en/tr). Residual: "from HalloTermin" in about 1 of 6 runs.

Workflow 04 version `8a7e42d4`. Re-tested: ru/ar/en/tr course and Kita openings, 3 landlord runs with the standard pattern.
