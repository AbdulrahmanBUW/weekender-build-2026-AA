---
type: memory
date: 2026-09-26 15:10
by: claude (abdul's session)
---
# Handoff: data round 2, review sheets for Anastasia

## Done
- **Research is done for you, Anastasia.** Agents added 10 communities / family places, 11 courses and Kitas, 24 events (5 Oct – 29 Nov), filled phones / ages / districts, and fixed the Ausländerbehörde guide. Details and numbers: [[RUN-025 Data round 2 and review sheets]].
- **Demo listing "Olgas Musikstudio"** exists (fictional, `subcategory = 'demo'`): the Discover beat of the demo can run on it.
- **Review sheets:** `docs/content-kit/review/providers-review.csv` (92 family places) and `events-review.csv` (44 events). Rows the agents were unsure about already say why in *Review note*.
- **Review mode** in the importer: rows with an ID are updated in place, only rows marked `fix` are saved, `remove` rows go to a list for the team, one column per language for translations. How-to: `docs/content-kit/README.md` → "Review and improve what is already in the app".
- [[DEF-050 Intake asks for the child's first name]] fixed in n8n 04 (live).

## In progress
- Anastasia: Lovable UI build with Plan v3 (card #22).

## Next
- **Anastasia (card #17, now much smaller):** open the two review sheets in Google Sheets. Start with the rows that have a *Review note*, then add 5–10 places from your own network at the bottom (leave ID empty). Your network is what no agent can find: the parent groups, the Saturday school without a website, the teacher parents recommend. While you're in the sheet, check the Russian and Ukrainian descriptions (part of #18).
- **Abdul:** decide on the newcomer rows listed in RUN-025 (Sprachakzente, Commerzbank Devrientstr., Zahnzentrum Dresden Zentrum, DAMF, Dresden International Church duplicate).
- **Next week:** school guide goes stale on 30 Sep (online booking for the school-entry check closes).
- If the Lovable repo already has the per-language string files: re-split `docs/i18n/ui-strings.json` (new key `subcategories.german_for_children`).

## Learnings / gotchas
- Research agents in Claude Code cost no n8n credits; crawler 02 in n8n does. Keep using agents for data until after the demo.
- The importer's default note says "Added by the Dresden mit Kind team from our own network" when *Notes* is empty. Agent rows always carry their own "Details from the provider's website (retrieved …)" note, so that text stays true.
- Never put internal flags into `notes_en`: the app may show it. Flags belong in *Review note* or in the vault.
- Commerzbank and Deutsche Bank branches mostly publish only a central hotline: never put a hotline on a branch listing.
