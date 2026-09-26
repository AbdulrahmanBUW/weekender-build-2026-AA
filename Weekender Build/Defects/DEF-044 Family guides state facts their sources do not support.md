---
type: defect
date: 2026-09-26
status: fixed
severity: minor
found_in: "[[RUN-021 Library guides for families]]"
owner: abdul
---
# Defect: Family guides state facts their sources do not support

## Observed
A second agent checked the 4 new family guides in `public.guides` against their official sources (all opened again on 26 Sep 2026). Most statements matched. These did not:

1. `kita-place-dresden`, `content_md`: said you apply for "every kind of day care", **including the Hort**, in the Kita-Portal. dresden.de "Betreuung in Horten" says the opposite: for a city-run Hort, parents register their child **directly with the Hort management** at the school (or at the Kita with Hort places) before school starts. A parent would look for a Hort place in the portal and not find one.
2. `kinderarzt-u-untersuchungen`, `summary_en` + all 5 translations: "U1 to U9 and J1, recorded in the gelbes Heft". gesund.bund.de and the BMG say the gelbes Heft holds the **U check-ups**. The G-BA decided on 20 Aug 2026 that J1 results will be recorded there **in future**, so this is not the case yet.
3. `school-enrolment-dresden`, checklist item 6 + `content_md`: "Personalausweis **or passport**". The dresden.de FAQ and the Anmeldebogen name only the Personalausweis of the registering parent. The passport part had no source.
4. Smaller wording problems in `content_md`: Kita fee checklist said "ask for a lower fee" for families on Bürgergeld/Wohngeld/Kinderzuschlag/asylum benefits, but these families pay **no** fee. Kindergeld said "after August 2019" where the source says "since August 2019" (from the 4th month after arrival). Kinderarzt did not say the Terminservicestelle (116 117) is only for people with **statutory** insurance. School said the Besondere Bildungsberatung is for children "who do not speak German (well)", but the source means children whose first language is not German. Kita said "city offices" bring in the Gemeindedolmetscher, but the source names Kitas, childminders and the Amt für Kindertagesbetreuung.

## Expected
Every statement in a guide can be traced to one of its `sources[]`. When the sources do not answer a question, the guide tells the parent to ask (for example "ask the school which document to bring").

## Repro
`select slug, summary_en, checklist, content_md from public.guides where slug in ('kita-place-dresden','school-enrolment-dresden','kindergeld','kinderarzt-u-untersuchungen');` (values before 26 Sep 2026 ~12:50), then compare with the pages listed in `sources`.

## Fix
Fixed in the verification part of [[RUN-021 Library guides for families]] with one UTF-8 SQL transaction (optimistic lock on `updated_at`). English and all 5 translations (de, ru, uk, ar, tr) were changed together. Checklist lengths are unchanged. `https://www.dresden.de/de/leben/kinder/tagesbetreuung/betreuungsformen/horte.php` was added to `sources` of the Kita and school guides. The builder's check that every number in a translation also appears in English cannot catch this kind of error. Before any new guide goes live, a second agent should compare it with its sources, line by line.
