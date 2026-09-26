---
type: run
date: 2026-09-26 10:28
by: claude (abdul)
result: partial
build: n8n 9Dl8JmCdK418btfF (Newcomer 02 – Resource crawler), execution 15
---
# Run: Newcomer crawler — full run

## Goal
Run all 16 place searches + 4 guide topics after [[RUN-007 Newcomer crawler first run]].

## Result (1 min 52 s)
**87 resources** in Supabase:
| Category | Subcategory | n |
|---|---|---|
| doctor | hausarzt 16 · kinderarzt 8 · frauenarzt 8 · zahnarzt 8 | 40 |
| pharmacy | apotheke | 16 |
| bank | sparkasse 6 · commerzbank 4 · deutsche_bank 4 | 14 |
| community | international_community 5 · migrant_counselling 5 · international_office 3 · welcome_center 2 · language_cafe 1 | 16 |
| auslaenderbehoerde | — | 1 |

**3 guides** (each 2 official sources): `auslaenderbehoerde-dresden-appointment` (9 steps), `bank-account-documents` incl. Basiskonto (8 steps), `anmeldung-dresden` (10 steps).

## Gaps
- 4th guide (health-insurance registration) not written — likely no trusted source passed the filter → rerun or add manually.
- Many rows have no phone (Brave place data) → the app should link to the website instead.
- Spot-check key rows before the demo ([[Newcomer Resources - Crawler]]: "verify" rule).

## Defects found
- none new ([[DEF-004 Supabase node stores jsonb payload as string]] now fixed in workflow 01 as well)
