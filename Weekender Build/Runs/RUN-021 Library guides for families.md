---
type: run
date: 2026-09-26 12:35
by: claude (library guides agent, for abdul)
result: pass
build: supabase public.guides (8 rows; ref ycyrtlzympxzlfcocazh)
---
# Run: Library guides for families

## Goal
Library pillar of [[DEC-003 Merged concept]] / [[Merged Concept]]: add 4 family guides to `public.guides` from official sources only, and make sure **all 8 guides** have `i18n` objects `{title, summary, checklist}` for **de, ru, uk, ar, tr** with the same number of checklist items as English. Existing `ar/tr/uk` keys must stay untouched (merge with `jsonb ||`).

## Steps
1. Read the merge migration `20260926200000_merged_family_hub.sql` (guides `category`, `audience`, `ask_task_type` checks) and dumped the 4 existing guides as a snapshot.
2. Opened every source page myself on 26 Sep 2026 (dresden.de pages fetched with `curl` and a browser user agent: WebFetch gets HTTP 503 from dresden.de, same as in [[RUN-011 Resource spot-check]]). No 116117 / KV Sachsen / Doctolib / Jameda / Google Maps / social media scraping; 116117 is only *mentioned* as the official phone number.
3. Wrote English content + translations in Python data files, generated one UTF-8 SQL file (`INSERT … ON CONFLICT (slug) DO UPDATE`, `i18n = guides.i18n || excluded.i18n`; existing guides: `UPDATE … SET i18n = i18n || {de, ru}`), ran it with `npx supabase db query --linked -f` in one transaction.
4. Built-in checks before running: 6–10 checklist items, ≥ 2 sources, same item count per language, and every number in a translation must also appear in the English text (catches typos in phone numbers, dates, amounts).
5. Verified with SQL, a byte-exact comparison against the source data and the snapshot, an anon REST read, an anon write attempt and a link check.

## New guides
| slug | category | audience | ask_task_type | items | sources | main official sources |
|---|---|---|---|---|---|---|
| `kita-place-dresden` | kita_school | family | kita_enquiry | 10 | 5 | dresden.de Anmeldeverfahren, Kitaportal, Elternbeiträge, city leaflet for immigrant parents (EN PDF); familienportal.de (Rechtsanspruch from age 1) |
| `school-enrolment-dresden` | kita_school | family | other_call | 9 | 4 | dresden.de Einschulung FAQ (general + kommunale Grundschulen), Schulaufnahmeuntersuchung, Kinder aus dem Ausland |
| `kindergeld` | money | family | other_call | 10 | 5 | arbeitsagentur.de (Anspruch/Höhe, Ausland, Nachweise), familienportal.de (foreign parents), BZSt FAQ (Steuer-ID) |
| `kinderarzt-u-untersuchungen` | health | family | doctor_appointment | 9 | 6 | gesund.bund.de (U/J check-ups, Kinderärztliche Versorgung, Arztwahl/Terminsuche), BMG, G-BA press release 20 Aug 2026, dresden.de (doctor's certificate before Kita) |

All `sources[].retrieved_at = '2026-09-26'`, `city = 'Dresden'`. Each `content_md` ends with the "check the source before you act" footer and the source list.

**Numbers quoted (all with source + date):** Kita fees from 1 Sep 2026 — 9-hour Krippe 280.19 EUR, 9-hour Kindergarten 231.40 EUR per month (first child, married/couple; dresden.de Elternbeiträge); Kindergeld 2026 259 EUR per child per month (arbeitsagentur.de). No other amounts.

**Content decisions**
- Dresden's official pages describe no Kita-Gutschein / Bedarfsbescheinigung step, so the Kita guide does not mention one.
- School guide is written for school year **2027/28**: registration days were 10 + 15 Sep 2026 (online 1 Aug–15 Sep 2026), school-entry exam booking portal open until 30 Sep 2026. The guide tells parents who missed it to contact a Grundschule now.
- Kinderarzt guide: J1 age written as "about 12–14 years" because gesund.bund.de says 12–13 and the G-BA (20 Aug 2026) says 13–14. The new G-BA "U10" for 9–10-year-olds is mentioned as decided but not yet available.
- Only official phone numbers/e-mails of public offices are in the texts (Amt für Kindertagesbetreuung, Beitragsstelle, Familienkasse 0800 4 555530, 116 117, 112). No private individuals.

## Result
| Check | Outcome |
|---|---|
| `jsonb_object_keys(i18n)` per guide | ✅ all 8 guides have exactly `ar, de, ru, tr, uk` (40 rows) |
| checklist length per language = English | ✅ 40/40 (10/9/8/10 existing; 10/9/10/9 new) |
| keys per language object | ✅ `{checklist, summary, title}` everywhere |
| existing ar/tr/uk + English columns of the 4 old guides | ✅ byte-identical to the snapshot taken before the run |
| stored text vs source data (Arabic/Cyrillic round trip) | ✅ byte-identical, 0 mismatches |
| anon REST `GET /guides?select=slug,i18n->de->>title,…` | ✅ 200, 8 rows, correct de + ar titles |
| anon REST `PATCH /guides` | ✅ refused (401, `42501 permission denied`) |
| link check of all 35 source URLs in the 8 guides | ✅ 35 × HTTP 200 |

## Follow-ups (not done here)
- `content_md` is English only for all 8 guides (the `i18n` shape has no body). The guide page must keep the "This guide is in English" notice for the body ([[Frontend and UX Plan v2]] C6).
- Time-bound facts will go stale: school registration dates (next cycle: summer 2027), Kita fee table (next change usually 1 Sep), Kindergeld amount (per calendar year). Re-check before any demo after September 2026.
- The guide list in the UI is still hard-wired to `bank-account-documents` in parts of the plan; with 8 guides and `category`, the library page should group by category.

## Defects found
- [[DEF-042 Parallel agents share one scratchpad]]
- [[DEF-043 Guide sources mix two retrieved_at formats]]

## Verification
*Independent fact-check, 2026-09-26 ~12:40–12:55, by claude (verification agent). Work files in `<scratchpad>/verify_guides_run021/`.*

**Method:** I dumped all 8 guides from the linked DB. I opened all 19 source URLs of the 4 new guides myself (curl with a browser user agent, all HTTP 200; the dresden.de PDF was read with pdftotext). Where the text raised a question, I also opened two linked official pages: the dresden.de Hort page and the Anmeldebogen PDF. I then checked every checklist item, every number and every factual line of `content_md` against the source text. For all 8 guides I checked the i18n structure and the translation language: script heuristics plus a manual read of every de/ru/uk/ar/tr item of the new guides, and de/ru/uk (plus an ar/tr skim) of the old guides.

**Confirmed correct against the sources:**
- Kita: apply from birth, about 11 months ahead, up to 5 Wunscheinrichtungen, 14-day steps, "zweite Zwischeninformation" = waiting list, about 4 months before start, address and phone details, opening hours.
- Kita fees from 1 Sep 2026: 280,19 € (9 h Krippe) and 231,40 € (9 h Kindergarten).
- Kita: 3rd child free, no fee with social benefits, apply at the earliest 6 weeks ahead, doctor's certificate not older than 14 days, measles proof, leaflet languages, Rechtsanspruch since Aug 2013.
- School: birth window 1 Jul 2020–30 Jun 2021, registration days 10/15 Sep 2026 14–18 h, online 1 Aug–15 Sep 2026 with BundID, only one municipal school, Aufnahmebescheid at end of May/start of June.
- School check: exam free and compulsory, Aug–Jan, 40 min, booking portal until 30 Sep 2026, 12-hour confirmation link, LiSe-DaZ, handout languages.
- Kindergeld: 259 € per child per month, 6-month back payment, 6 weeks then 0800 4 555530 / +49 911 12031010, KG1 / Anlage Kind / KG 51, copies only, list of 8 countries, list of residence permits, exclusions, Steuer-ID after 3 months, Einspruch within 1 month.
- Kinderarzt: all U1–U9 time windows, 11 check-ups paid by statutory and private insurance, U10/U11/J2 as optional insurer extras, Terminservicestelle has 1 week to find an appointment within 4 weeks, 116 117 / 112 signs, Teilnahmekarte since 2017, dental checks from 6 months, G-BA U10 (20 Aug 2026) not yet available.
- J1 "about 12–14 years" is a fair summary: gesund.bund.de says 12–13, BMG says "13.–14. Lebensjahr", G-BA says "13 to 14".

**Fixed (details in [[DEF-044 Family guides state facts their sources do not support]]):**
| Guide | Field(s) | Change |
|---|---|---|
| `kita-place-dresden` | `content_md`, `sources` | The Hort is **not** booked in the Kita-Portal: city-run Hort = register directly with the Hort management. The interpreter wording now names Kitas, childminders and the Amt für Kindertagesbetreuung. Added source "Betreuung in Horten" (dresden.de). |
| `kita-place-dresden` | checklist[9] + de/ru/uk/ar/tr | "lower fee **or no fee**": benefit recipients pay nothing. |
| `school-enrolment-dresden` | checklist[5] + 5 languages, `content_md` | Removed the unsourced "or passport". Parents without a German ID are told to ask the school. |
| `school-enrolment-dresden` | checklist[8] + 5 languages, `content_md`, `sources` | Hort: register separately, **directly at the Hort**, before school starts. Besondere Bildungsberatung = children whose first language is not German (plus the LaSuB address and phone from the source). Added the Hort source. |
| `kindergeld` | `content_md` | "in or after August 2019 … from the fourth month after arrival" (source wording). |
| `kinderarzt-u-untersuchungen` | `summary_en` + 5 language summaries, `content_md` | The gelbes Heft holds the **U** check-ups; J1 goes in only in future (G-BA decision). Terminservicestelle is for people with **statutory** insurance. |

SQL: one UTF-8 file, `begin … commit`, 4 `UPDATE`s guarded by `updated_at = '2026-09-26 10:30:05.528077+00'`, run with `npx supabase db query --linked -f`. No schema change. The 4 old guides were not touched.

**Result after the fix:**
| Check | Outcome |
|---|---|
| Stored values vs. expected values (all 11 content columns, 8 guides) | ✅ byte-identical; 4 new guides updated, 4 old guides unchanged |
| i18n keys `de, ru, uk, ar, tr` with `{title, summary, checklist}` in all 8 guides | ✅ |
| Checklist length per language = English | ✅ 40/40 (10/9/8/10 old; 10/9/10/9 new) |
| Right language | ✅ uk has no Russian-only letters (ы э ъ ё) and ru has no Ukrainian-only letters (і ї є ґ); Arabic is Arabic script and reads naturally right to left (German terms appear as Latin inserts); tr and de read naturally |
| German official terms kept in translations (Kita-Portal, Geburtsurkunde, Familienkasse, Steuer-ID, gelbes Heft, Terminservicestelle, Beitragsstelle, …) | ✅ |
| `category` / `audience` / `ask_task_type` set and allowed by the check constraints | ✅ all 8 |
| Numbers in translations also appear in English | ✅ (only `26.09` from the date 26.09.2026) |
| New source URL (dresden.de Hort page) | ✅ HTTP 200 |

**Left open (not changed here):**
- `auslaenderbehoerde-dresden-appointment` (old guide, all languages): the summary still says "From May 2026 it moves to a new address". In September 2026 the move has already happened. Suggested wording: "Since May 2026 it is at Lingnerallee 3". The English column of the old guides was out of scope for this run.
- `kinderarzt-u-untersuchungen` checklist[1] still does not say that the Terminservicestelle is only for people with statutory insurance. The summary and `content_md` now say it.
- The J1 age differs between official sources (12–13 / 13–14). The guide keeps "about 12–14 years".
