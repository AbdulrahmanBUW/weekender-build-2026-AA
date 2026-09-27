---
type: memory
date: 2026-09-27 12:30
by: claude (abdul's session)
---
# Handoff: demo-day kit and pixel art

## Done
- **The presentation** is `docs/launch/presentation.html`. Open it in Chrome and press F. It works offline.
  - It has 15 slides plus an appendix, with click-by-click animation and Deepgram/ElevenLabs audio and word-synced captions.
  - 3-minute route: 1 → 6 live demo → 14 Monday plan → 15 thank you + QR code.
  - If the live call fails, type 7, press Enter, then Right 3 times. V plays the backup video.
  - Controls and files: `docs/launch/README.md`. The story and voices: `docs/launch/PRODUCTION.md`.
- **The videos** are in `docs/launch/video/`:
  - `launch/launch-nomusic.mp4` (/brag, 25.9 s). The version with music stays local, because the licence of the bundled ende.app track is not confirmed.
  - `demo/demo_stage.mp4` (1:49) and `demo/demo.mp4` (2:29).
- **Pixel Dresden is live** ([[DEC-004 Pixel art for Dresden and newcomers]], [[Pixel Art Plan]]):
  - A skyline band under the home hero, with 12 walking newcomers and a tram.
  - Small scenes on the pillar pages and the 404 page.
  - A pause button and no motion for users who turn it off.
  - A new `/credits` page.
  - Sources: `docs/pixel/BRIEF.md` and `scripts/pixel/*.py`. The images are in `public/pixel/` in the Lovable repo.
- **The guide translations are live:** Anastasia's bodies had been synced to Lovable but never published. Every language showed English until this morning's publish.
- **The relay `/speak` now uses ElevenLabs Sarah for English**, with Deepgram Helena as the fallback. German stays Viktoria.
- **The architecture and call-sequence diagrams are updated with archify** (`docs/diagrams/`).

## Open
- The Lovable Knowledge still has no pixel-art exception. The text is ready: it adds a "PIXEL ART (DEC-004)" section and changes the bans to "…outside the pixel art". The editor only saves real keystrokes, so paste it by hand. `AGENTS.md` in the Lovable repo already has the rule.
- PRODUCTION.md's bans need a one-line exception for the pixel art.
- Confirm the music licence, or keep the no-music launch video.
- The relay still runs only on Abdul's laptop, and Render was dropped. Keep the Claude Code session open during the demo.
- Still open from before: the Impressum details, the repo privacy decision, the 14 incomplete listings, and resetting the demo badge before the demo.

## Learnings / gotchas
- **After every GitHub push to the Lovable repo, someone must click Publish → Publish changes.** Otherwise the live site stays on the old build.
- The desktop app can stop the relay preview. If you hear the robot voice or the mic fails, restart the relay and press Ctrl+Shift+R in Chrome.
