---
type: defect
date: 2026-09-26
status: fixed
severity: major
found_in: "[[RUN-015 Family task types in n8n]]"
owner: claude (RUN-015 verification agent)
---
# Defect: Child health terms in other languages reach the call brief

*Number assigned by the integration run ([[RUN-023 Merged flow E2E]]). The finding and the fix were made in the verification section of [[RUN-015 Family task types in n8n]], when no free defect number was left.*

## Observed
A direct anon REST insert of a Turkish `course_enquiry` with `goal_user` "Oğlumun astımı ve alerjisi var …" and a fact `child_note` = "astım, alerji" was briefed by n8n 01 with the FAKTEN line "Hinweis zum Kind: astım, alerji (nicht an Kursanbieter weitergeben)". The health word list in the safety nets knew only a few non-German words, so Turkish, Russian, Ukrainian and Arabic health terms passed. `sensitive_stripped` was not logged.

The same list also had false positives: `боль` matched больше / большой (ru "more / big"), `біль` matched більше (uk "more"), and Arabic `ألم` matched ألمانيا / الألمانية ("Germany / German"). An Arabic parent writing "we don't speak German well" had the word cut out and `sensitive_removed` set.

## Expected
No health detail about the child (or the parent, outside the pharmacy task) reaches the German brief, whatever language the parent writes in ([[Data minimisation - no symptoms]]). Everyday words must not be cut.

## Repro
Insert a `course_enquiry` via anon REST with a Turkish, Russian, Ukrainian or Arabic health word in `goal_user` or in an `allowed_facts` value, wait for `status = 'briefed'`, read `call_brief_de`.

## Fix
Done in n8n 01 *Prepare Task Brief*, 01 *Parse Brief + Re-check* and 04 *Validate + Clean Draft* (published 01 `9a55d7bf`, 04 `8a7e42d4`, exports in `n8n/workflows/`):
- Word list extended: tr astım / alerji / hastalık / otizm / diyabet / engelli; ru/uk астма / аллергия / алергія / болезнь / хвороба / аутизм / эпилепсия / діабет / инвалид / СДВГ; ar ربو / حساسية / مرض / سكري / توحد / صرع; de/en ADHS / ADHD / Autismus / Epilepsie / Neurodermitis / Behinderung / disability.
- False positives fixed with `боль(?!ш)`, `біль(?!ш)`, `ألم(?!ان)` and word boundaries on short Arabic words.
- *Parse* drops any FAKTEN line with a health term as a second safety net and logs `sensitive_stripped` (field `call_brief_de.fakten`).

Verified live in RUN-015: the Turkish adversarial task got a clean brief; a Russian "больше" goal and an Arabic "الألمانية" goal stayed unchanged. In [[RUN-023 Merged flow E2E]] the Russian course brief had FAKTEN from `allowed_facts` only.

Left over (cosmetic): when a health word is cut from `goal_user` on a direct REST insert, the sentence can read oddly ("Oğlumun ve var …"). The intake paraphrases, so the app path does not show this.
