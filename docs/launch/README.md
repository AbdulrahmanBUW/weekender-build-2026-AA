# Ankommen: demo-day kit

Everything for the Sunday demo (27 Sep 2026, 13:00, 3 minutes). The story, script lines, voices and design rules are in
[PRODUCTION.md](PRODUCTION.md). All audio was made with Deepgram and ElevenLabs.

## Present
1. Open `docs/launch/presentation.html` in **Chrome** (it works from `file://`, offline), then press **F** for full screen.
2. **3-minute route:** slide 1 → **5 Live demo** (switch to the app) → 13 Monday-Morning Plan and the pilot ask → 14 Thank you + QR code.
3. **If the live call fails:** type `6`, press Enter, then Right 3 times. This plays the scripted 63 s call with German lines and Russian subtitles.
   Or press **V** on any slide to play the backup video (the 1:49 stage cut; `presentation.html?backup=full` plays the full 2:29).
4. Before 13:00, scan the QR code on slide 14 with a phone once.

| Key | Action |
|---|---|
| Right, Space, PageDown, click | next step (clickers work) |
| Left, PageUp | previous step (redraws the exact state) |
| Home / End, digits + Enter | first / last slide, jump to a slide |
| N | speaker notes |
| O | slide overview |
| B | black screen |
| A | replay the step's audio |
| M | mute |
| V | backup video |
| `?en=helena` | English line on slide 4 with Deepgram Helena instead of ElevenLabs Sarah |

## Files
| Path | What |
|---|---|
| `presentation.html`, `assets/deck/` | the deck (GSAP builds, word-synced captions); `assets/deck/build_data.py` rebuilds `data.js` from the manifests |
| `audio/` | 34 clips + 5 phone-line versions, word timings (`*.words.json`), `call_full.*`, `intake_full.*`, `manifest.json`. Regenerate: `python scripts/launch/make_audio.py` (keys from `services/voice-relay/.env`, never printed) |
| `assets/screens/` | 47 screenshots of the live app (6 languages, desktop/phone), `manifest.json`; script `scripts/launch/shoot_screens.mjs` |
| `assets/n8n/` | workflows 01/04/05/06 as n8n canvas images + paper-style SVGs, `manifest.json` |
| `assets/diagrams/` | architecture PNGs (light/dark) and node positions; the source is `docs/diagrams/architecture.json` (archify) |
| `video/launch/` | launch video made with /brag: `launch-nomusic.mp4` (25.9 s). `launch.mp4` has music and is **not committed**: the bundled ende.app track has no confirmed licence |
| `video/demo/` | demo walkthrough `demo.mp4` (2:29) and the stage cut `demo_stage.mp4` (1:49), poster `demo.jpg`, builder scripts |

## Honest notes
- All calls are browser role-plays. The receptionist voice in the recordings is synthetic (Deepgram Julius). Olgas Musikstudio is a demo listing.
- Slide 7 and the videos recreate the result card with the story's time (Thu 1 Oct, 16:30). The real test call (RUN-026) booked 14:00, and A3 shows the real screenshot.
- The voice intake and call screens in the demo video are recreations in the app's style. The home, provider and result screens are real screenshots.
