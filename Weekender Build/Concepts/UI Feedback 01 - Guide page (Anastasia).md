---
type: concept
tags: [ui, ux, lovable, feedback, guides]
by: anastasia (written up by claude)
date: 2026-09-26
status: open
---
# UI Feedback 01: Guide page (Anastasia)

**Page:** https://dresden-mit-kind.lovable.app/guides/kita-place-dresden (applies to every guide page).
**Related:** [[Frontend and UX Plan v3 (merged)]] (C6 guide page, G.2 prompts) · [[DEF-051 Guide body stays in English]] · [[Idea B - Dies-Das-Ana-Nas]]

## What Anastasia wants

1. **The whole page is translated.** Today only title, summary and checklist are; the long text stays English. → [[DEF-051 Guide body stays in English]].
2. **"Ask for me" is a quiet, native feature, not the biggest block on the site.** On a guide page it sits right **after the contact details** (phone, email, address) as one short line and a small button:
   > Is it hard to call them yourself? Our AI assistant can call for you in German and bring the answer back in your language. [Ask the assistant to call]
3. **The right column (desktop) becomes "Useful on this topic"** instead of the big "We can call for you" box: **2–3 related links**, then a **2-sentence "About Dresden mit Kind"** text (for SEO/GEO).
   For the Kita guide, for example:
   - Find a Kita → the Kita list (`/services?group=kita_school`)
   - "Kita or Tagesmutter: what is the difference?" (**guide does not exist yet**)
   - "The Berlin settling-in model (Eingewöhnung) and how Kitas work in Germany" (**guide does not exist yet**)

## Strings (done, 0 credits)
Added to `docs/i18n/ui-strings.json` → screen `guides`, all 6 languages (804 keys each): `askHint`, `askHintText`, `askButton`, `relatedTitle`, `aboutTitle`, `aboutText`. AI translations; Anastasia to check ru, uk/ar/tr still need a native speaker. **Next step (Abdul):** run the split command from `docs/i18n/README.md` into the `hallotermin-paper` clone and push, before sending the prompts below.

## Related links: where they come from
No new table. Order of sources, max 3 links:
1. The "find" link that already exists for the guide's `ask_task_type` (Kita guide: `library.findKita` → `/services?group=kita_school`; bank guide: `guides.ctaFindBank`).
2. Other guides with the **same `category`** (newest first), excluding the current one.
3. If still fewer than 2: any other guide.
Later, when the two new Kita guides exist, they appear automatically because they share `category = kita_school`.

## Lovable prompts (send in this order, one message each, then Publish)

**F1-a: whole guide translated** (after the DB content from DEF-051 is in)
> On the guide page (/guides/$slug): render the long text from `guide.i18n[uiLang].content_md` when it exists, inside a wrapper with `lang={uiLang}` and `dir="rtl"` when uiLang is "ar". Only when it is missing, fall back to `guide.content_md` with `lang="en"` and show the existing `t("guides.inEnglish")` notice. Title, summary and checklist logic stays as it is. Do not change `src/i18n/strings/`.

**F1-b: quiet "Ask for me" after the contact details**
> On the guide page, remove the large "We can call for you" box from the aside (desktop) and from after the summary (mobile). Instead, directly after the guide's contact section (the last section of the text, "Contact"), add one quiet block: a thin 1px top border, then `t("guides.askHint")` as a short bold line, `t("guides.askHintText")` as muted body text, and one small outline button `t("guides.askButton")` that links to `/ask?type=<guide.ask_task_type>` (same target as the old box). Keep the secondary "Find a Kita" style link out of this block (it moves to the aside). Show the block only when `ask_task_type` is not null. No icon, no colour fill, no shadow; same size as normal body text. Keep it accessible (button is a real link, focus ring visible).

**F1-c: aside = "Useful on this topic" + "About"**
> In the guide page aside (sticky from 1024px, stays after the text on mobile): heading `t("guides.relatedTitle")`, then 2–3 plain text links: (1) the existing "find" link for the guide's ask_task_type if there is one (kita_enquiry → t("library.findKita") → /services?group=kita_school; bank_enquiry → t("guides.ctaFindBank")), (2) other guides with the same `category`, newest first, excluding the current guide, showing their title in the UI language, (3) if fewer than 2 links, fill with any other guide. Below, a 1px divider, heading `t("guides.aboutTitle")` and the paragraph `t("guides.aboutText")` in muted text. Remove the old "Other guides" list at the bottom if it duplicates these links. No cards, no images, no icons.

## Content to write (Claude Code, 0 credits)
- New guide: **Kita or Tagesmutter: what is the difference?** (`category = kita_school`, `ask_task_type = kita_enquiry`), official sources only (dresden.de, Familienportal).
- New guide: **Settling in at a Kita: the Berlin model (Eingewöhnung)** (`category = kita_school`), sources: official/academic (e.g. infans / Familienportal / Kita-Bildungsserver); no medical claims.
- Both with translations incl. `content_md` for de, ru, uk, ar, tr (see DEF-051).

## Same pattern elsewhere (to decide)
Provider pages (`/p/:id`) also have the big "Ask for me" aside. If the team agrees, apply the same quiet pattern there: small line + button under "Contact", aside = related places + About.
