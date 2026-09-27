# Hyperframes Composition Brief: Ankommen

## Objective
Create a short launch video for Ankommen (Weekender Build, Dresden, demo day 27 Sep 2026).

## Output
- Composition directory: `docs/launch/video/launch/composition/`
- Rendered video: `docs/launch/video/launch/launch.mp4` (poster `launch.jpg`, baked as frame 0)
- Format: landscape — 1920x1080, 30 fps
- Duration: 25.9 s

## Source Material
- Project root: repo root; brief `docs/launch/PRODUCTION.md` (binding)
- Live-app screenshots: `docs/launch/assets/screens/` (manifest.json), copied into `composition/assets/screens/`
- Narration: `docs/launch/audio/nar_l1..nar_l6.mp3` + `.words.json` (ElevenLabs George), copied; nar_l5 time-stretched 1.1x with ffmpeg atempo (`nar_l5_110.mp3`)
- IVR: `docs/launch/audio/ivr_de.mp3` (Deepgram aurelia), trimmed by `data-media-start`
- Product name: Ankommen — tagline "Your guide to starting in Germany"
- Key UI moments: courses page (ru), home in six languages, provider page Call-for-me box and button (en), result card (ru)
- Copy that must appear verbatim:
  - "Your guide to starting in Germany"
  - "ankommen-dresden.lovable.app"
  - Language names: English, Deutsch, Русский, Українська, العربية, Türkçe
  - German call line "Guten Tag! Hier ist die KI-Assistentin von Maria Petrova." and Russian "Добрый день! Это ИИ-ассистент Марии Петровой." (PRODUCTION.md 3.3)

## Creative Direction
- Tone preset: polished
- Creative direction: a calm, honest product launch for families; confident, never hype
- Interpretation: long holds, ease-out motion, soft slides, sparse sound
- Angle / hook / outro: see `brag-plan.md`
- Avoid: generic SaaS language, abstract filler, redesigning the product, every PRODUCTION.md section 4 ban

## Visual Identity
- Background #F7F4EC, card #FFFDF8, paper-deep #EFE9DC, border #D9D2C3
- Text #1C2420 / muted #5B635E; accent pine #1F5C4A (#174A3B pressed, #E6EEE9 tint); amber #D98E04 only for the live dot
- Display: Fraunces 600 SOFT 50 (self-hosted woff2); body Source Sans 3; Cyrillic headings Source Serif 4 600; Arabic Noto Naskh Arabic 600

## Storyboard
Scene summary (contract in `brag-plan.md`):
1. Found it — 0.0-2.75 s — courses page (ru) in a browser frame, camera push onto Olgas Musikstudio
2. The German wall — 2.6-6.95 s — German course-page line, phone menu row with live bars and streaming IVR words
3. Reveal — 6.85-10.25 s — wordmark + tagline synced to voice
4. Six languages — 10.05-13.5 s — home page flips en/de/ru/uk/ar/tr on the beat, names list
5. Call for me — 13.35-22.2 s — provider page, button press, call card with the AI sentence, result card with check draw
6. End card — 22.05-25.9 s — wordmark, URL, language names

## Audio
- Audio role: narration-led; warm bed after the reveal
- Music: `assets/music/happy-beats-business-moves-vol-12-by-ende-dot-app.mp3`, starts 6.84 s with media offset 0.5 s (track beat 0.56 s lands on the wordmark at 6.90 s), fades out 24.9-25.9 s
- Music cue guidance: preset cues (109.96 BPM). Beat-locked: button press at 15.63 s (strong cue 9.29 s); beat grid: language flips at 10.16 / 10.73 / 11.25 / 11.68 / 12.34 / 12.90 s
- Ducking: voiceover carve via `hyperframes-audio/scripts/carve.mjs` (strength 0.3, voices vo-l3..vo-l6) plus a music volume lane (0.6, fade-in 0.12 s, fade-out over the last 0.86 s)
- Audio-reactive: IVR RMS drives the phone-menu bars; music RMS breathes the browser-frame shadow (precomputed per frame, embedded as data)
- SFX (bundled Kenney CC0, low HF risk): impactSoft_medium_001 at the reveal, ui/click2 at the press, interface/bong_001 at the check
- Audio files are copied into `composition/assets/`

## Hyperframes Instructions
Single standalone `index.html`, one paused GSAP timeline (local `assets/vendor/gsap.min.js`, no CDN), all timings from the narration word files, `npx hyperframes check` must pass with zero errors before render.
