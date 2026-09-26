---
type: defect
date: 2026-09-26
status: fixed (needs Publish)
severity: major
found_in: "[[UI Feedback 01 - Guide page (Anastasia)]]"
owner: abdul
---
# Defect: Guide body stays in English in every UI language

## Observed
On https://dresden-mit-kind.lovable.app/guides/kita-place-dresden with the UI in Русский, the title, summary and checklist are Russian. After the checklist the page says "Эта памятка на английском языке." and everything from "Before you start" to "Contact" is English. The same happens for all 8 guides and all non-English UI languages. (Found by Anastasia, checked by Claude in the browser on 26 Sep.)

## Expected
The whole guide is in the parent's language, including the long text. German official terms stay as they are, with the explanation in brackets (as in the checklist today).

## Repro
Open any `/guides/<slug>` → language button → Русский (or العربية, Türkçe, Українська, Deutsch).

## Cause
By design so far: `guides.i18n` only holds `{title, summary, checklist}`; `content_md` is English only (see [[RUN-021 Library guides for families]], line "content_md is English only for all 8 guides"). The page shows `guides.inEnglish` and renders `content_md` with `lang="en"`.

## Fix
1. **Content (Claude Code, 0 Lovable credits):** add `content_md` to `guides.i18n.<lang>` for de, ru, uk, ar, tr for all 8 guides. Same method and checks as RUN-021 (every number in a translation must appear in the English text; German terms kept; merge with `i18n || …`, never overwrite other keys). Needs linked DB access.
2. **Page (Lovable, 1 small prompt):** render `i18n[uiLang].content_md` when present, with `lang=uiLang` and `dir="rtl"` for Arabic; fall back to English `content_md` + the `guides.inEnglish` notice only when it is missing. Prompt is in [[UI Feedback 01 - Guide page (Anastasia)]] (prompt F1-a).
3. Spanish, French etc. are not UI languages. If parents use the browser's own translate button, it now works on the whole page too, because the text is real HTML text.

## Done (26 Sep, Anastasia + Claude)
- Chose static files instead of the DB (no DB access needed, 0 credits): English bodies copied from the live site to `content/guides/en/`, translations in `content/guides/{de,ru,uk,tr,ar}/<slug>.md` (40 files). All pass `python3 scripts/check_guide_translations.py` (same sections, list items, links, e-mails; every number in a translation also appears in the English text). AI translations: native speakers should still read uk/ar/tr.
- Lovable repo `hallotermin-paper`: `src/routes/guides.$slug.tsx` renders `i18n.<lang>.content_md` if present, else `src/content/guides/<lang>/<slug>.md`, else English + notice. The quiet "Call for me" hint sits right after the section with the phone contacts; aside = "Useful on this topic" + "About" ([[UI Feedback 01 - Guide page (Anastasia)]] F1-a/b/c done in code, no Lovable prompts needed). Translations are copied from the team repo with `rsync -a --exclude en/ content/guides/ <hallotermin-paper>/src/content/guides/`.
- **Still to do:** Publish → Publish changes in Lovable (not built locally: no Node on Anastasia's Mac; check the Lovable build).
