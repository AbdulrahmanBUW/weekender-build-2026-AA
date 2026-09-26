---
type: run
date: 2026-09-26 15:05
by: claude (abdul's session + 8 research agents)
result: pass
build: cloud DB ycyrtlzympxzlfcocazh; n8n 04 OA51fhbX7NxrVEnW (v 04cb1fe2); scripts/import_content.py (review mode) + scripts/export_review.py
---
# Run: Data round 2 and review sheets

## Goal
Do the research and data entry ourselves, so Anastasia can **review and improve** the family data instead of building it from scratch (Abdul, 26 Sep). Also close the known gaps before the demo: phone numbers for "Ask for me", ages for the age filter, events after early October, the stale Ausländerbehörde guide, the missing demo listing, [[DEF-050 Intake asks for the child's first name]].

## Steps
1. Eight background agents (Claude Code web research, **no n8n credits**). Same sources policy as [[Family Hub Data]]: only the provider's own site or official pages, every value re-opened in a verification pass, never Facebook / Instagram / Telegram / Google Maps / Doctolib / Jameda / 116117 / KV Sachsen, no private people's numbers.
   - new communities and family places, new courses and Kitas (content-kit CSV, importer dry run first)
   - phones + districts for doctors, pharmacies and banks; phones, ages and districts for family rows (guarded `update … where <field> is null` files)
   - family events 5 Oct – 30 Nov
   - guide freshness check (all 8 guides against official sources)
   - DEF-050 fix in n8n 04 (pinned-data test, no AI credits)
2. Reviewed every agent report, then applied: CSVs with `scripts/import_content.py --apply`, SQL files in one transaction each.
3. Added the demo listing **Olgas Musikstudio** (`subcategory = 'demo'`, fictional address and phone `+49 351 0000000`, music, 3–6, ru + de, Neustadt, 6 languages) per [[Frontend and UX Plan v3 (merged)]] section H.
4. Built the review workflow: `scripts/export_review.py` + review mode in `scripts/import_content.py` (columns ID / Review / Review note / `Description (xx)` / `Title (xx)`); steps in `docs/content-kit/README.md`, section "Review and improve what is already in the app". Exported `docs/content-kit/review/providers-review.csv` (92 family rows) and `events-review.csv` (44 events) with every agent doubt pre-filled in *Review note*.

## Result
| | Before (13:20) | After (15:05) |
|---|---|---|
| resources | 140 | **162** (+10 communities / family places, +11 courses / Kitas, +1 demo listing) |
| family rows (`family` + `both`) | 70 | **92** |
| family rows with phone | 45 of 56 family-only | **77 of 92** |
| family rows with an age range | 31 of 56 | **46 of 92** |
| doctors with phone | 13 / 38 | **37 / 38** |
| pharmacies with phone | 1 / 16 | **16 / 16** |
| banks with phone | 2 / 14 | **7 / 14** (the other 7 only publish a central hotline) |
| service rows without district | 32 | **0** |
| family events | 20 (13 in demo week) | **44** (24 new, 5 Oct – 29 Nov) |
| "Checked by phone" badges | 0 | 0 |

- Guides: only the Ausländerbehörde guide was stale ("moves from May 2026" → moved; Lingnerallee 3, **Eingang Nord**; no letterbox at the new site) — fixed in en + 5 languages. The other 7 still match their official sources.
- Corrections to existing rows: Vital Apotheke → Pieschen; 4 pharmacies in 01307 → Johannstadt (address suffix "Dresden-Altstadt" removed); City Apotheke address; MVZ Doceins → "Sana Praxis für Allgemeinmedizin und Innere Medizin Dresden (formerly MVZ Doceins)"; Kinderarztpraxis Herzenssache website → www host.
- Privacy: removed a named interpreter's personal mobile from "Sprachakzente Dresden" (not a language café but a commercial interpreting agency).
- UI string `subcategories.german_for_children` added in 6 languages (`docs/i18n/ui-strings.json`, now 789 keys per language). Re-split the per-language files if they were already copied into the Lovable repo.
- Review mode tested live on the demo listing: update by ID worked, an empty `Description (tr)` cell kept the Turkish text. All 90 generated review updates passed `EXPLAIN` against the live schema.
- Left out on purpose: "Sputnik Sachsen" (only a Dec 2024 city page, no address or phone); 15 community and 11 course candidates dropped by the agents (dead sites, Facebook-only, no 2026 evidence).

**Newcomer rows for the team to decide** (not in Anastasia's family sheet): Sprachakzente Dresden (remove), Commerzbank SB-Standort Devrientstr. (ATM only, nobody to call), Zahnzentrum Dresden Zentrum (source is a scraped listing, practice may be closed), DAMF (stale, adults only), Dresden International Church (listed twice, phone/address unverified).

## Defects found
- [[DEF-050 Intake asks for the child's first name]] — fixed (n8n 04 "Validate + Clean Draft" drops child-name facts, notes and questions).
- School guide goes stale on **30 Sep 2026**: the online booking for the school-entry check closes, booking is by phone only after that. Edit next week.
- District values still mix Stadtbezirk and Stadtteil (DEF-035 / DEF-038); new rows follow the existing pattern.
