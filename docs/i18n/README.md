# UI strings (i18n)

`ui-strings.json` holds every interface string of the Lovable app **Dresden mit Kind** (the family hub with the "Ask for me" call feature; "HalloTermin" is only the engine name and no longer appears in the UI). The strings come from the vault notes `Concepts/Frontend and UX Plan v3 (merged).md` (sections C, F, G.0, G.2) and, for the call flow, `Concepts/Frontend and UX Plan v2.md`. This file is the source of truth. The Lovable repo gets one file per language (see "Per-language files").

## Structure

```
{ "<lang>": { "<screen>": { "<key>": "text" } } }
```

- **6 UI languages:** `en` (source), `de`, `ru`, `uk`, `ar` (RTL), `tr`. All six have exactly the same screens and keys: 28 screens, 867 keys per language, 5,202 strings (the motion revamp of 26 Sep added the `fx*` keys in `home`, `provider`, `call`, `ask`, `events`, `guides`).
- Lookup: `t("directory.years", { min: 3, max: 6 })` means `strings[uiLang].directory.years` with the placeholders replaced. Fallback: `strings.en[screen][key]`, then `""`. Never show the raw key.

| Group | Screens |
|---|---|
| Shell | `common` (footer, 404, language picker, generic buttons), `nav` (pillar links, "Ask for me", menu, breadcrumb) |
| Discover | `home`, `filters` (filter bar, counts), `directory` (list rows, age text, badge, source line, empty/error states for `/courses`, `/communities`, `/services`), `provider` (`/p/:id`), `events`, `services` (the old `find` screen: search, district select, v2 subcategory labels), `library`, `guides` |
| Ask for me | `ask` (v3 prefill, course/Kita copy, Latin name, consent list), `intake` and `approval` (v2 intake and approval card), `call` (v2 live call + "Start the call" panel + optional in-app call), `result` (v2 results + trial lesson, Kita visit, course/Kita answer keys) |
| Community input | `suggest` (form, privacy line, honeypot label, success, error) |
| Errors | `errors` |
| Lookup tables (keys = DB values) | `taxonomy`, `subcategories`, `districts`, `taskTypes`, `otherSide`, `reasonCategories`, `germanTerms`, `languages`, `languageNames` |
| Legacy | `landing` (v2 home page; not used by the v3 routes, kept so old components do not break) |

## Lookup keys for database values

| DB value | Key | Notes |
|---|---|---|
| `resources.activity_categories[]` (16) | `taxonomy.activity_<value>` | e.g. `activity_parent_baby` |
| `resources.category` (12) | `taxonomy.cat_<category>` | `cat_kita` = "Kita" in en/de, with a local word in the others |
| `resources.price_type` (5) | `taxonomy.price_<price_type>` | `unknown` is shown on the provider page, never as a filter option |
| `resources.format` (6) | `taxonomy.format_<format>` | `null` → `directory.notListed` |
| age band ids `0-1`, `1-3`, `3-6`, `6-10`, `10+` | `taxonomy.age_<id>` | chip labels (e.g. `taxonomy.age_10+`); `home.ageLinkLabel` is the `aria-label` |
| `resources.subcategory` (the 52 values in the DB on 26 Sep, plus `demo`) | `subcategories.<subcategory>` | fallback for new values: underscores to spaces. The v2 keys `services.sub*` stay for old components |
| `resources.district` / `family_events.district` | `districts.<district>` | see "Districts" below |
| `guides.category` | `library.cat_<category>` | `null` → `library.cat_other` |
| `task_type` (10) | `taskTypes.<task_type>`, `otherSide.<task_type>`, `provider.ask_<task_type>` | `ask.title_<task_type>` exists for `course_enquiry` and `kita_enquiry`; other types use `ask.title_default`. Same for `ask.example_*`, `ask.willAsk_*`, `ask.mayAgree_*` |
| `calls.result` keys | `result.key_<key>` | missing key → the key with underscores as spaces |
| `resources.last_check_outcome` | `directory.checked_<outcome>` | `rejected_no_new_patients` uses `checked_rejected` |
| `family_events.price_type` (`free`, `paid`, `unknown`) | `events.free`, `events.paid`, `events.priceUnknown` | not the `resources` price list |
| `reason_category` (doctor) | `reasonCategories.<value>` | |

**Age text** (next to the age ruler), with `min = age_min_years`, `max = age_max_years`:

| Case | Key |
|---|---|
| both null | `directory.agesNotListed` |
| `min < 1` (and `min > 0`) | `directory.fromMonths` with `min` in months (0.5 → 6) |
| `min` null or 0, `max` set | `directory.upToYears`, or `directory.upToOneYear` when `max = 1` |
| `max` null or 18, `min` set | `directory.fromYears`, or `directory.fromOneYear` when `min = 1` |
| both set | `directory.years` |

**Counts:** use `filters.countOne` / `filters.countEventsOne` for 1, else `filters.count` / `filters.countEvents`. Russian, Ukrainian and Arabic are written as "Мест: 12", "Місць: 12", "عدد الأماكن: 12" so that one string works for every number (no plural rules needed).

## Placeholders

Identical in every language; replace them in code, never translate them: `{language}`, `{place}`, `{name}`, `{duration}`, `{count}`, `{max}`, `{min}`, `{amount}`, `{date}`, `{month}`, `{band}`, `{source}`, `{code}`, `{list}`, `{task}`, `{items}`, `{phone}`, `{age}`, `{day}`, `{n}`, `{done}`, `{total}`.

- `{language}`: pass `languageNames[uiLang][code]` (the language named in the UI language: "Russisch", "русский", "الروسية"), not the native name. The sentences are built for that.
- `{date}`: always from `src/lib/format.ts` (Gregorian calendar, Latin digits, Europe/Berlin).
- `{month}` (`ask.willAsk_kita_enquiry`): month and year, e.g. `Intl.DateTimeFormat(loc, { month: "long", year: "numeric" })`. The ru/uk strings use a colon ("начало: февраль 2027"), so the nominative form from `Intl` is correct.
- `{place}`, `{name}` with a German place name: render it through `<De>` (the `dir` attribute isolates it inside Arabic text).

## What changed from v2 (4 → 6 languages)

- New UI languages `de` and `ru` for every key (no English fallback needed any more).
- `common.appName` and `common.docTitleSuffix` = "Dresden mit Kind"; "HalloTermin" replaced in every value (consent and calendar text: "the Dresden mit Kind AI assistant").
- Screen `find` renamed to `services`.
- `taskTypes` and `otherSide` + `course_enquiry`, `kita_enquiry`; `germanTerms` + `Hausschuhe`, `Sportsachen`, `Probestunde`, `Warteliste`, `Betreuungsplatz`, `Kita-Portal`; `languages` and `languageNames` + `de`.
- `intake.loadingSlow` now says 20 seconds (the app's intake timeout in plan v3).
- New screens: `nav`, `home`, `filters`, `directory`, `provider`, `events`, `library`, `ask`, `suggest`, `taxonomy`, `subcategories`, `districts`. New keys in `common` (footer), `call` (Start the call panel, "Read new lines aloud", optional in-app call) and `result` (course and Kita results).
- All 275 keys of the plan v3 strings spec (G.0) are included with the same English text, plus the strings that the plan's prompts write out in English (fallback texts, counts, age edge cases, footer, P13 errors).

## UI languages vs content languages

| Kind | Languages | What the user sees |
|---|---|---|
| UI translated | en, de, ru, uk, ar (RTL), tr | The whole interface from this file |
| Content only | fa (RTL), prs / Dari (RTL, text only, no voice), hi, es, fr, pl, vi, zh | English interface; intake questions, subtitles and results in their language (from n8n / Claude) |

`uiLang` (one of the 6) sets `<html lang dir>`. `userLang` (the language of a request, 14 codes) only sets `lang` and `dir` on the content blocks. Voice input: every language except `prs`.

## Word choices (for reviewers)

- **Product name** "Dresden mit Kind" stays German in every language (`lang="de"`).
- **"Ask for me"**: de "Für mich anfragen", ru "Спросите за меня", uk "Запитайте за мене", ar "اسألوا نيابةً عني", tr "Benim için sor" (from plan v3 A; native speakers to confirm, see RUN-022).
- **Kita**: en/de "Kita"; ru "детский сад (Kita)", uk "садочок (Kita)", ar "روضة (Kita)", tr "Kita (kreş ve anaokulu)" in labels; the short local word in running text.
- **The assistant**: German uses "die KI-Assistentin / sie" (it matches the German call opening "Hier ist die KI-Assistentin …"); ru/uk "ассистент / асистент, он / він", ar masculine, tr neutral. "AI": ru ИИ, uk ШІ, ar الذكاء الاصطناعي, tr yapay zekâ, de KI.
- **Library pillar**: en "Library" (plan name); de "Ratgeber", ru "Справочник", uk "Довідник", ar "مكتبة الأدلة", tr "Rehberler", so it is not mixed up with real libraries (`activity_library`, `cat_library`).
- German terms stay German with the meaning in brackets (`Ausländerbehörde (ведомство по делам иностранцев)`). `germanTerms` gives the meaning for `bring_items` and chips; in the `de` block it is a plain-German explanation.
- Tone: B1, short sentences, formal address (Sie, вы, ви, siz; Arabic masculine singular imperative as in v2), no exclamation marks, no hype words. The German demo transcript lines (`landing.excerpt*De`) are content and keep their "Guten Tag!".

## Districts

`districts.<value>` covers the 16 districts in the database on 26 Sep 2026 plus Klotzsche (all 10 Stadtbezirke). The value is the German name in en, de and tr, and the name in the reader's script in ru, uk and ar (Нойштадт, نويشتات). Show the German name as the label (`<De>`, as street signs and trams use it). In ru, uk and ar, add the script version muted after it when it differs: `Neustadt · Нойштадт`. Unknown district → show the DB value as it is.

## RTL notes (plan v3 section E)

- `<html lang dir>` follows the UI language only: `dir="rtl"` only for `ar`. Content blocks in `ar`, `fa`, `prs` get their own `dir="rtl"` (`<UserText>`), inside any UI language.
- Logical CSS / Tailwind only: `ms-/me-`, `ps-/pe-`, `start-/end-`, `text-start/text-end`, `border-s`, `rounded-s`. Never `ml-/mr-/pl-/pr-/left-/right-/text-left/text-right`.
- Mirror arrows, chevrons, the stepper connector, the "How it works" connector and the age-ruler fill (`rtl:-scale-x-100` or logical insets). Do not mirror phone, check, clock, lock, shield icons, numbers, times or the wordmark.
- German text: always `<De>` (`lang="de" dir="ltr"`). Phone numbers, postcodes, URLs, emails: `<bdi dir="ltr">`. User text: `dir="auto"`.
- Digits stay Latin (0-9) in all locales: `${ui}-u-ca-gregory-nu-latn`, `hourCycle: "h23"`, `timeZone: "Europe/Berlin"`.
- Number ranges in Arabic: an en dash between digits ("3–6") is shown reversed ("6–3") in right-to-left text. The Arabic strings therefore use words ("الأعمار من {min} إلى {max}") or an ASCII hyphen in the age chips ("3-6"). Keep it that way when editing.
- `ar.suggest.urlError` contains invisible left-to-right marks (U+200E) around `https://` so that the `://` does not jump to the other side. Do not remove them.

## Per-language files (for the Lovable repo)

Plan v3 G.0 step 2: the Lovable app reads `src/i18n/strings/<lang>.json` with the shape `{ "<screen>": { "<key>": "text" } }`. From the repo root, write them into the Lovable checkout (`<lovable-repo>` = its path):

```bash
python -c "import json,os,sys;d=json.load(open('docs/i18n/ui-strings.json',encoding='utf-8'));o=os.path.join(sys.argv[1],'src','i18n','strings');os.makedirs(o,exist_ok=True);[json.dump(d[l],open(os.path.join(o,l+'.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=2) for l in d];print(list(d))" <lovable-repo>
```

## Check

Run before every push (valid JSON, same keys in all 6 languages, same placeholders as English, no empty values):

```bash
python -c "import json,re;d=json.load(open('docs/i18n/ui-strings.json',encoding='utf-8'));e=d['en'];P=lambda v:sorted(set(re.findall(r'\{[a-zA-Z_]+\}',v)));bad=[(l,s,k) for l in d for s in e for k in e[s] if k not in d[l].get(s,{}) or not d[l][s][k].strip() or P(e[s][k])!=P(d[l][s][k])]+[(l,s) for l in d for s in d[l] if s not in e];print(list(d),sum(len(v) for v in e.values()),'keys per language');print(bad or 'ok')"
```

## Adding a language

1. Copy the `en` block to a new top-level key (ISO code, e.g. `"fa"`), translate every value, keep all keys and placeholders.
2. Keep German terms in German and add the meaning in brackets, as in the existing languages. Keep German place and district names.
3. Add the code to the UI language list in the app (`src/i18n/index.tsx`) and, if right-to-left, to the RTL list.
4. Run the check above, then write the per-language files.
5. Ask a native speaker to read it once; keep sentences short (B1, calm, no exclamation marks, no hype words).

## Lovable instruction snippet

Replaces the v2 snippet. P1b of plan v3 builds this; paste it only if the strings files are pushed before P1b:

```text
i18n: the strings are in src/i18n/strings/{en,de,ru,uk,ar,tr}.json (pushed from GitHub; do not rewrite or re-translate them). Create src/i18n/index.tsx with a LanguageProvider (uiLang, setUiLang; saved in localStorage "dmk_ui_lang" inside try/catch; first visit: first match of navigator.languages among the 6, else en) and a hook useT() that returns t(key, vars?): split "screen.key" at the first dot, read strings[uiLang]?.[screen]?.[key] ?? en[screen]?.[key] ?? "", replace {name} placeholders from vars. Import en.json statically, load the others with dynamic import(). On change set document.documentElement.lang = uiLang and dir = "rtl" only for ar. Keep uiLang separate from the request language (userLang), which only sets lang/dir on content blocks. No i18n library needed.
```

## Review status

All de, ru, uk, ar and tr strings added on 26 Sep 2026 are drafts written by Claude and checked by script (keys, placeholders, script, Russian vs Ukrainian letters). Native speakers from Anastasia's communities review ru, uk and ar before the demo (vault note `Decisions/DEC-003 Merged concept.md`). Open questions for them are listed in `Weekender Build/Runs/RUN-022 UI plan v3 merged.md` → "Verification".
