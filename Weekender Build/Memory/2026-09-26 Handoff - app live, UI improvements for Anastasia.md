---
type: memory
date: 2026-09-26 19:00
by: claude (abdul's session)
---
# Handoff: app live, UI improvements for Anastasia

## Done
- **The app is live: https://dresden-mit-kind.lovable.app** (Lovable project "HalloTermin Paper", TanStack Start with server rendering). Code: private repo https://github.com/AbdulrahmanBUW/hallotermin-paper, synced both ways with Lovable.
- All pages are built: home, courses, provider page, **Ask for me** (with a "Speak instead" dictation button), live call, result, events, communities, health & services, library, guides, suggest, Impressum, Datenschutz. 6 UI languages incl. Arabic right-to-left; SEO titles and preview image.
- **The whole loop works on the live site**: [[RUN-026 Live site E2E call]] (Russian request → German call → trial lesson booked → Russian summary).
- Plan v3 section G now holds the prompts exactly as they were sent (P1b … P16) and a build-status box at the top: [[Frontend and UX Plan v3 (merged)]].
- 183 RU/UK/AR translation fixes (AI review, not yet read by a native speaker), relay accessibility fixes, Deepgram opt-out of model training.
- Lovable settings: URL `dresden-mit-kind`, badge hidden, visitor analytics **off**, auto-fix off. Knowledge v3.1 saved. **64.8 Lovable credits left.**

## In progress
- Anastasia: **UI improvements** (board card). Abdul: Impressum details, public-repo decision, 14 incomplete service listings (SQL in chat).

## Next (Anastasia, UI improvements)
1. **Look at the live site on your phone** (375 px) in Русский and العربية. Note what feels wrong: spacing, text size, wording, the order of things.
2. **Small text changes cost nothing:** edit `docs/i18n/ui-strings.json` in the team repo (or ask Claude Code), run the split command from `docs/i18n/README.md` into the `hallotermin-paper` clone and push. Lovable picks it up; then click **Publish → Publish changes**.
3. **Layout/design changes:** in Lovable, Agent mode, one clear change per message. The rules Lovable must follow are in Knowledge and in `AGENTS.md` of the Lovable repo. Good first prompt: **P12 (polish, accessibility and RTL audit)** in Plan v3 section G, not sent yet.
4. **After every change you like: Publish → Publish changes** (free). Keep ≥ 30 credits for Sunday morning.
5. **Test a call** (needs Abdul's laptop, where the relay runs): Olgas Musikstudio → Ask for me → Call now → Start the call → speak German as the receptionist. Before the rehearsal reset the demo badge: `update resources set last_checked_at = null, last_check_outcome = null where subcategory = 'demo';`

## Never do
- Never enable **Lovable Cloud**, never click **"Try to fix"** in Lovable's security panel (it writes database changes; the one critical finding is our known demo-mode trade-off).
- Never let Lovable rewrite the files in `src/i18n/strings/` (they come from the team repo), never add Google Fonts, analytics or cookies, never add an email field.
- Never edit the Impressum placeholders with invented data: Abdul fills in the real name, address and email.

## Learnings / gotchas
- The language switch looked broken **inside the Lovable editor preview** (cross-site iframe blocks the cookie). It works on the real site; P16 made it work even with blocked cookies.
- Lovable accepts queued follow-ups ("Send follow-up…") while it works: queue several small prompts instead of waiting.
- Dictation and calls need the relay: on Abdul's laptop the local relay works; other devices need the public relay host (`docs/deploy-relay.md`).
- The security report `docs/security/security-review-2026-09-26-run2.md` is **not committed** while the team repo is public (it describes abuse paths). It is on Abdul's laptop.
