---
type: concept
tags: [ui, a11y, review]
sources: []
---
# Accessibility and RTL Review (Frontend and UX Plan v2 + relay call test page)

**What this is:** a WCAG 2.2 AA and RTL/multilingual review of [[Frontend and UX Plan v2]] (sections C, E, F5, G, prompts P2–P11) and of the relay test page `services/voice-relay/public/index.html`. Reviewed 26 Sep 2026. Nothing has been changed in code; this note lists findings and fixes.

**Why it matters for us:** our users read in a second language, often in Arabic script, on a phone. The demo runs in Arabic (RTL). If the date shows the wrong calendar or a screen reader reads German with an Arabic voice, the "it works in your language" story breaks on stage.

**Related:** [[Frontend and UX Plan v2]] · [[Lovable Prompt Pack]] · [[Personas]] · [[Moment of Truth - First 15 Seconds]] · [[Voice Pipeline - Architecture]]

**Method:** read the plan and test page; computed contrast for every token pair actually used (Python, WCAG 2.x relative luminance); checked `Intl` output in Node for all planned locales; `ui-ux-pro-max` UX search (accessibility / screen reader / heading hierarchy); `component-reference-design` patterns (stepper, combobox, dialog, reduced motion).

---

## 1. Contrast results (all pairs in use)

Text needs 4.5:1 (normal) · UI parts, focus rings and meaningful graphics need 3:1.

| Foreground | Background | Ratio | Used for | Verdict |
|---|---|---|---|---|
| ink #1C2420 | paper / card / paper-deep | 14.45 / 15.62 / 13.13 | body text | Pass |
| ink | pine-tint / amber-tint / brick-tint | 13.44 / 14.04 / 12.92 | text in assistant rows and panels | Pass |
| ink-muted #5B635E | paper / card / paper-deep | 5.63 / 6.09 / 5.12 | helper text, subtitles | Pass |
| ink-muted | pine-tint / amber-tint / brick-tint | 5.24 / 5.48 / 5.04 | subtitle on assistant rows, muted in panels | Pass (smallest margin: brick-tint) |
| pine #1F5C4A | paper / card / paper-deep / pine-tint | 7.11 / 7.69 / 6.46 / 6.61 | links, secondary button, focus ring | Pass |
| white | pine / pine-hover | 7.81 / 10.10 | primary button | Pass |
| ink | amber #D98E04 | 5.91 | live step label | Pass |
| white | amber | 2.68 | (do not use) | **Fail** |
| amber (live dot) | paper / card / pine-tint | 2.44 / 2.64 / 2.27 | live dot, live step marker | **Fail 1.4.11** (needs 3:1) |
| amber-text #8A5A00 | amber-tint / paper / card | 5.24 / 5.39 / 5.83 | needs-your-answer, "Live updates paused" | Pass |
| brick #A63A2A | brick-tint / paper / card | 5.24 / 5.86 / 6.34 | errors | Pass |
| input #8C8577 | white / card / paper | 3.66 / 3.60 / 3.33 | input borders | Pass (3.33 is tight on paper) |
| border #D9D2C3 | paper / card / white | 1.37 / 1.48 / 1.50 | decorative borders | Only OK if decorative. **Fails** if used for chip, checkbox, segmented-control or mic-meter outlines |
| disabled button (opacity .5) | card | 2.41–2.45 | "Hang up" before call | Exempt, but see F11 |

All ratios claimed in plan G2 are correct. The only real problems are the amber dot and the risk that shadcn uses `--border` for control outlines.

---

## 2. Findings

Severity: **High** = breaks WCAG AA or the demo story · **Med** = clear barrier for some users · **Low** = polish.

| # | Sev | Where | Issue | Fix |
|---|---|---|---|---|
| F1 | **High** | E5 / P2 `format.ts` | `fa` and `prs` default to the **Persian solar calendar**. Node: `fa-u-nu-latn` gives "1405 مهر 7" for 29 Sep 2026. An Amina-type user in Persian would see a different date than the German practice agreed. `ar` gives 12-hour "8:30 ص" while the call said "8:30 Uhr". | Always add calendar and hour cycle: `const loc = (l) => ({prs:'fa-AF'}[l] ?? l) + '-u-ca-gregory-nu-latn';` then `new Intl.DateTimeFormat(loc(lang), {dateStyle:'full', timeStyle:'short', hourCycle:'h23', timeZone:'Europe/Berlin'})`. Verified output: "سه‌شنبه 29 سپتامبر 2026 ساعت 8:30". |
| F2 | **High** | P2 step 2, E4 CSS | P2 sets `<html lang="fa" dir="rtl">` for fa/prs, but those languages have **English UI chrome**, so English menus would render mirrored and be read with a Persian voice. Fonts are keyed on `:root[lang]`, so subtitle lines in fa/ar inside an English page get no Arabic-script font. | Split two ideas: `uiLang` (en/ar/tr/uk) drives `<html lang dir>`; `userLang` drives content blocks only. Key fonts on any element: `[lang\|="ar"], [lang\|="fa"], [lang="fa-AF"] { font-family: var(--font-arabic); line-height: 1.8; }` |
| F3 | **High** | C3 / P5 transcript | `role="log" aria-live="polite"` on the whole transcript announces speaker + German + "Translating…" for every row, then (maybe) nothing when `text_user` arrives by UPDATE (`log` defaults to `aria-relevant="additions"`). Too chatty and it announces the wrong language first. | Make the visible log quiet and add one announcer that speaks only complete, user-language lines (see snippet A). Never announce "Translating…". Queue lines, max one announcement per line. Add a checkbox "Read new lines aloud" (on by default). |
| F4 | **High** | C3 call card | Several live regions compete: stepper `aria-live`, phase line, timer, speaking bars, transcript, result. The timer ticks every second. | One `role="status"` for phase changes only ("Connected", "Call ended, 1:12"). Timer: `role="timer"` (not live) or `aria-hidden="true"` plus the phase announcement. Speaking bars: `aria-hidden="true"`. Stepper: `aria-current="step"`, **no** `aria-live`. |
| F5 | **High** | All German text (`.de`), test page `.de` | `lang` is an HTML attribute, not a CSS class. The test page has `<html lang="en">` and German lines with no `lang`, so screen readers read German with English pronunciation. Plan P2 "a .de utility" risks the same. | Build a component, not a class: `const De = ({children}) => <span className="de" lang="de" dir="ltr">{children}</span>;` Use it for text_de, opening_de, bring_items, "Bürgeramt" in chips, and German place names inside user-language sentences (`<bdi lang="de">Kinderarztpraxis Dr. Sommer</bdi>`). Test page: `li.querySelector('.de').lang = 'de'`. |
| F6 | **High** | G2 live dot | Amber dot is 2.44:1 on paper (needs 3:1 as the only graphic "live" marker next to text). | Keep the amber fill (brand), add a dark ring: `.live-dot { background: var(--amber); box-shadow: 0 0 0 2px var(--amber-text); }` (ring 5.4:1). Or a darker dot `#B06F00` (3.73 on paper, 3.39 on paper-deep). Always keep the word "Live" next to it. |
| F7 | Med | E4 / G3 subtitles | Subtitle line is 16px muted. In Arabic script 16px Noto Sans Arabic is visibly smaller than 16px Latin, and this is the line the user actually needs. "Translating…" is planned in italics; Arabic has no true italic (fake slant hurts reading). Letter-spacing breaks Arabic joining. | `.sub:is(:lang(ar),:lang(fa)) { font-size: 1.125rem; line-height: 1.8; font-style: normal; letter-spacing: 0; }` Speaker labels ≥ 16px in Arabic script (not 14). No `uppercase` / `tracking-*` on any user-language text. Consider ink colour (not muted) for the subtitle: it is the primary line for the reader. |
| F8 | Med | P3/P4/P5 `dir="auto"` | `dir="auto"` picks direction from the first strong character. Arabic subtitles often start with a Latin name ("Dr. Sommer …") and would be laid out LTR. | We know the language, so set it: `<p lang={userLang} dir={RTL.has(userLang) ? 'rtl' : 'ltr'}>`. Keep `dir="auto"` only for free text the user typed. |
| F9 | Med | C2 / C4 focus + live | Questions area is `aria-live` **and** focus moves to the first new question; result card uses focus **and** `aria-live`. Screen readers read it twice. | Pick focus only: heading/legend gets `tabIndex={-1}` and `.focus()` once. Remove `aria-live` from those containers. |
| F10 | Med | Header, sticky start column | WCAG 2.2 **2.4.11 Focus Not Obscured**: a sticky header/column can hide the focused element when tabbing. | `html { scroll-padding-top: 5rem; }` (header height + 16px); on mobile make the start column non-sticky (plan already stacks it). |
| F11 | Med | Test page Start/Hang up | Clicking "Start call" disables the focused button; focus drops to `<body>` and keyboard users lose their place. Same on cleanup for "Hang up". | After `ws.onopen`: `$('stop').focus()`. In `cleanup()`: `if (document.activeElement === $('stop') \|\| document.activeElement === document.body) $('start').focus();` |
| F12 | Med | Test page status | `#statusText` changes ("Connecting…", "Live…", "Not connected") are silent. `.dot` is not hidden. | `<span id="status" role="status">`, `<span class="dot" aria-hidden="true">`. |
| F13 | Med | Test page mic meter, P11 | `aria-label` on a plain `div` does nothing. `levelText` flips "hearing you"/"silence" many times per second; if anyone makes it live it becomes a flood. | Bar `aria-hidden="true"`; change `levelText` only on state change (hearing ↔ silence, debounce 1 s); outer row `role="group" aria-label="Microphone"`. |
| F14 | Med | Test page errors, P11 | "Could not start: " + raw `err.message` (e.g. "NotAllowedError: Permission denied"). Not understandable, no next step (3.3.3). | Map errors: `NotAllowedError` → "The microphone is blocked. Click the lock icon in the address bar, allow the microphone, then press Start call again." `NotFoundError` → "No microphone found. Plug one in or use headphones with a mic." WebSocket close before open → "Could not reach the call service. Check the request ID and try again." |
| F15 | Med | D6 / P11 voice input | "Stop after 60 s" is a time limit without warning (2.2.1). Recording state not exposed. | Show "10 seconds left" at 50 s (announce once via `role="status"`), keep the text already heard, and let the user press "Speak again" to append. Button: visible label "Speak instead" ↔ "Stop"; `aria-pressed` on the toggle; status "Listening in العربية…". |
| F16 | Med | Test page, relay | 30 s silence → `no_answer` closes the call. For the receptionist (tester) this is a hidden time limit. It is a real-time call, so WCAG exempts it, but on stage a long pause kills the demo. | Test page: show a quiet countdown after 15 s silence ("Call closes in 15 s if nobody speaks"). Plan F2 already raises the timeout to 90 s during an explicit hold; say so on the test page tip. |
| F17 | Med | P4 approval card | Consent label is one 45-word paragraph. For B1 second-language readers this is heavy, and a screen reader reads it as one blob. Native checkboxes are ~13px targets. | Short label + described list: `<input id="c" type="checkbox" aria-describedby="c-rules"><label for="c">Yes, call for me in German</label><ul id="c-rules"><li>It says it is an AI first.</li><li>It shares only the facts above.</li><li>It agrees only to times inside my limits.</li><li>No audio. A text transcript is kept.</li></ul>` Whole row clickable, `min-height: 44px`. Same for fact checkboxes. |
| F18 | Med | P4 validation | Errors must say what is wrong and how to fix it, in the user's language, tied to the field. | `<input aria-invalid="true" aria-describedby="phone-err">` + `<p id="phone-err"><CircleAlert aria-hidden/> Please enter a German phone number, for example <bdi dir="ltr">0351 1234567</bdi>.</p>`; on Continue with several errors, focus the first invalid field. |
| F19 | Med | E1 language picker | Native names in the list are not marked up, so a screen reader reads "العربية" with an English voice (3.1.2). | `<span lang="ar" dir="rtl">العربية</span> <span class="muted">Arabic</span>`; same for the header button and the info bar. Map `prs` to `lang="fa-AF"` (TTS engines rarely have a "prs" voice). |
| F20 | Med | C4 completed result, prices | "12.50 €" is hard-coded English format. | `new Intl.NumberFormat(loc(lang), {style:'currency', currency:'EUR'})` → ar "‏12.50 €", en "€12.50". Wrap amounts inside German text in `<bdi>`. |
| F21 | Med | C2 out-of-scope emergency | Urgent message must be announced immediately and actionable on a phone. | `<div role="alert">` rendered once, focus its heading; numbers as links: `<a href="tel:112"><bdi dir="ltr">112</bdi></a>`, `<a href="tel:116117">…</a>`, 44px targets. |
| F22 | Med | G5 motion | Plan covers dot + bars, but not auto-scroll, `scrollIntoView`, entrance transitions, the mic meter transition, or Radix/shadcn dialog animations. | Global guard (snippet C). Auto-scroll with `behavior: 'auto'` under reduced motion. Test page: `#level { transition: none }` under reduced motion. |
| F23 | Low | E5 icons | Mirroring list is good. Missing: the horizontal "How it works" connector and any `ChevronRight` inside `<details>`/combobox; lucide `Languages` icon must not flip; send/arrow icons must. | Use `flex` + logical insets (`inset-inline-start`) for connectors, never `left:`; flip with `[dir="rtl"] .flip-rtl { transform: scaleX(-1); }` only on arrows/chevrons. Stepper is vertical (no flip needed); put its connector at `inset-inline-start: 11px`. |
| F24 | Low | Time ranges, timer in RTL | "08:00–12:00" and "1:12" inside Arabic text are usually fine, but inside mixed German/Arabic lines neutrals can reorder. | Use `Intl.DateTimeFormat#formatRange` (locale-aware dash) and wrap any time or range that sits inside German text or next to a Latin name in `<bdi dir="ltr">`. Timer: `<span role="timer" dir="ltr" style="font-variant-numeric: tabular-nums">`. |
| F25 | Low | Touch targets | 44px stated globally; easy to miss: inline "change" link after "Writing in:", "Show English too", `<summary>` of "Behind the scenes", combobox options, language rows, "New lines below". | `summary, .chip, [role=option], .lang-row { min-height: 44px; display: flex; align-items: center; }`; turn "· change" into a real button with padding. (AA minimum is 24px, 44px is our target.) |
| F26 | Low | Test page structure | "Transcript" is `<strong>`, not a heading; request-ID help text not linked; transcript list not labelled. | `<h2 id="t-h">Transcript</h2>` + `<ol id="lines" role="log" aria-labelledby="t-h">`; `<input id="req" aria-describedby="req-help">` + `<small id="req-help">`. |
| F27 | Low | Cognitive load (all copy) | Second-language readers: German terms appear without meaning (U-Untersuchung, Überweisung, Versichertenkarte); the English third line adds noise; long step lists. | Explain each German term once in the user's language next to it (plan already does for bring items; extend to goal and limits). Show "Step 2 of 4" on `/new`. Keep English line off by default (already). One idea per sentence, ≤ 12 words (already the rule for questions; apply to all panels). |
| F28 | Low | Text spacing / reflow | Turkish and Ukrainian strings are ~30% longer; Arabic lines at 1.8 need more height. | No fixed heights on chips, buttons, stepper labels; allow wrapping; test at 320px and with 200% zoom. |

---

## 3. Snippets

**A. Transcript announcer (F3, F4)**

```tsx
// Visible log: quiet, for reading and scrolling.
<ol role="log" aria-live="off" aria-labelledby="call-h">{rows}</ol>

// One announcer: only complete lines, in the user's language.
<div className="sr-only" aria-live="polite" aria-atomic="true" lang={userLang}>{announce}</div>

// When a row becomes complete (text_user arrived, or 8 s passed):
const speak = (row) => setAnnounce(
  `${label(row.speaker)}: ${row.text_user ?? t('call.subtitleMissing')}`);
// Queue: if a new line arrives within 1.5 s, replace, don't stack.
```

**B. Language and direction (F2, F5, F8, F19)**

```tsx
const RTL = new Set(['ar', 'fa', 'prs']);
const htmlLang = (l) => ({prs: 'fa-AF'}[l] ?? l);
document.documentElement.lang = htmlLang(uiLang);            // en | ar | tr | uk
document.documentElement.dir  = RTL.has(uiLang) ? 'rtl' : 'ltr';
const UserText = ({children}) =>
  <p lang={htmlLang(userLang)} dir={RTL.has(userLang) ? 'rtl' : 'ltr'} className="sub">{children}</p>;
```

**C. Reduced motion and focus (F6, F10, F22)**

```css
:root { --live-ring: #8A5A00; }
.live-dot { background: var(--amber); box-shadow: 0 0 0 2px var(--live-ring); border-radius: 9999px; }
html { scroll-padding-top: 5rem; }
:focus-visible { outline: 3px solid var(--ring); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important;
    transition-duration: .01ms !important; scroll-behavior: auto !important; }
}
/* Controls that carry meaning use the input border, not the decorative one */
.chip, [role="checkbox"], [role="radio"], .segmented button { border-color: var(--input); }
```

---

## 4. Must fix before demo (max 7)

1. **F1** Gregorian calendar + 24h in `format.ts` (`-u-ca-gregory-nu-latn`, `hourCycle:'h23'`, `prs → fa-AF`).
2. **F2** Separate UI language (`<html lang dir>`) from user language (content blocks); fonts on `[lang|=…]`, not `:root`.
3. **F3 + F4** One quiet log + one announcer for complete user-language lines; timer and bars not live; stepper uses `aria-current`.
4. **F5** `<De>` component with `lang="de" dir="ltr"` for every German string (and fix the test page `.de`).
5. **F6** Live dot ring (`box-shadow: 0 0 0 2px #8A5A00`) and control outlines on `--input`, never `--border`.
6. **F7 + F8** Arabic-script subtitles 18px / 1.8, no italics or tracking; explicit `dir` from the language, not `dir="auto"`.
7. **F11 + F12 + F14** Test page (used live by the receptionist on stage): focus to "Hang up" / back to "Start call", `role="status"` on status, friendly mic and connection errors.

## 5. Nice to have

- F9 remove double announcements (focus vs live) on questions and result.
- F10 `scroll-padding-top` for the sticky header.
- F13 debounced mic meter text; F15 60 s warning for voice input; F16 silence countdown on the test page.
- F17 short consent label with described rules list; F18 field-level error pattern; F21 `role="alert"` emergency panel with `tel:` links.
- F19 `lang` on native language names; F20 `Intl.NumberFormat` for prices; F24 `formatRange` + `<bdi>` for times.
- F25–F28 targets on small controls, headings on the test page, German term explanations, reflow at 320px / 200% zoom.
- After P10: run Lighthouse and one NVDA (Windows) pass in English and Arabic on `/r/<demo id>`, and one TalkBack pass on a phone; log as a Run.
