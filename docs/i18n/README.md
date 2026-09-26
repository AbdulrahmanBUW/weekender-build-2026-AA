# UI strings (i18n)

`ui-strings.json` holds every interface string for the HalloTermin Lovable app, taken from the screen specs in the vault note `Concepts/Frontend and UX Plan v2.md` (sections C, D4, E, F6, I). Lovable prompts can say: "use strings from ui-strings.json".

## Structure

```
{ "<lang>": { "<screen>": { "<key>": "text" } } }
```

- Languages: `en` (source), `ar`, `tr`, `uk`. All four have exactly the same screens and keys.
- Screens: `common`, `landing`, `intake`, `approval`, `call`, `result`, `find`, `guides`, `errors`, plus lookup tables:
  - `taskTypes`: labels for the 8 `task_type` values (keys = DB values)
  - `otherSide`: who the assistant is talking to, per `task_type` ("Practice", "Office" …)
  - `reasonCategories`: the 6 doctor `reason_category` values (keys = DB values)
  - `germanTerms`: meaning of German words shown in the serif font (key = the German word, e.g. `Versichertenkarte`, `Überweisung`). Show the German word as-is (`lang="de"`) and the value next to it.
  - `languages`: the 13 user languages in their own script (the same in every UI language; use for the picker)
  - `languageNames`: the 13 languages named in the UI language (muted second line in the picker, "You wrote in …")
- Lookup: `t("intake.title")` means `strings[lang].intake.title`.
- Placeholders use `{name}` and are identical in every language: `{language}`, `{place}`, `{duration}`, `{count}`, `{max}`, `{amount}`, `{date}`, `{source}`, `{code}`, `{list}`, `{task}`, `{items}`, `{phone}`. Replace them in code; do not translate them.
- German content that is never translated (the demo transcript lines `landing.excerpt*De`) is repeated in every language so lookups never fail.
- The Arabic strings use Arabic punctuation (`،` `؟`). German terms inside Arabic text stay in Latin letters; wrap them in `<bdi>` or `<span lang="de" dir="ltr">` if they sit at the start or end of a line.

## UI languages vs content-only languages (plan section E2)

| Kind | Languages | What the user sees |
|---|---|---|
| UI translated | en, ar (RTL), tr, uk | The whole interface from this file |
| Content only | ru, fa (RTL), prs / Dari (RTL, text only, no voice), hi, es, fr, pl, vi, zh | English interface, but intake questions, subtitles and results in their language (from n8n / Claude). `dir` still follows the language (fa, prs = rtl). |

Voice input: every language except `prs` (Dari is text only).

## Adding a language

1. Copy the `en` block to a new top-level key (ISO code, e.g. `"fa"`), translate every value, keep all keys and placeholders.
2. Keep German terms in German and add the meaning in brackets, as in the existing languages.
3. Add the code to the supported list in the app (`src/i18n/index.ts`) and, if right-to-left, to the RTL list (`ar`, `fa`, `prs`).
4. Run the check below. Missing keys fall back to English in the app, but the check should pass before a demo.
5. Ask a native speaker to read it once; keep sentences short (B1, calm, no exclamation marks, no hype words).

Check (from the repo root):

```bash
python -c "import json;d=json.load(open('docs/i18n/ui-strings.json',encoding='utf-8'));r=d['en'];print([(l,s,k) for l in d for s in r for k in r[s] if k not in d[l].get(s,{})] or 'ok')"
```

## RTL notes

- Set `<html lang="ar" dir="rtl">` for `ar`, `fa`, `prs`; `dir="ltr"` for all others.
- Use logical CSS / Tailwind only: `ms-/me-`, `ps-/pe-`, `start-/end-`, `text-start/text-end`, `border-s`, `rounded-s`. Never `ml-/mr-/pl-/pr-/left-/right-/text-left/text-right`.
- Mirror arrows, chevrons and the stepper connector (`rtl:-scale-x-100`). Do not mirror phone, check, clock, lock, shield, bot icons, numbers, times or the wordmark.
- German text: always `lang="de" dir="ltr"`. Phone numbers, postcodes, customer numbers, emails: `<bdi dir="ltr">`. User text: `dir="auto"`.
- Digits stay Latin (0-9) in all locales: `Intl.DateTimeFormat("ar-u-nu-latn", { timeZone: "Europe/Berlin", … })`.

## Lovable instruction snippet

Paste this into the P2 prompt (replaces the "fill with your best translation" part):

```text
i18n: copy docs/i18n/ui-strings.json from the repo to src/i18n/ui-strings.json (do not rewrite or re-translate it). Create src/i18n/index.tsx with a LanguageProvider (React context holding lang, saved in localStorage "ht_lang" inside try/catch) and a hook useT() that returns t(key, vars?): split key "screen.key", read strings[lang]?.[screen]?.[key], fall back to strings.en[screen][key], then to the key itself; replace {name} placeholders from vars. UI dictionaries exist only for en, ar, tr, uk; for ru, fa, prs, hi, es, fr, pl, vi, zh use the en strings but keep the chosen code as the user language. On change set document.documentElement.lang = lang and dir = "rtl" for ar, fa, prs, else "ltr". No i18n library needed.
```
