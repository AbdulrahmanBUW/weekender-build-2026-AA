# Brag Plan: Ankommen

## What is this app?
Ankommen ("Your guide to starting in Germany") is one place for international families in Dresden: courses, events, communities, health and services and guides in six languages, and on every page a "Call for me" button: an AI assistant phones the place in German, says in its first sentence that it is an AI, and brings the answer back in the parent's language.

## The angle
The moment every new parent in Germany knows: you found the right course, and then the page says "call us", in German. The video lets that wall be heard (a rushed German phone menu under the narration), then answers it calmly with the real product: the app in six languages, the Call-for-me button being pressed, the assistant's honest first sentence, and the booked result in Russian. Confident, never hype. The product UI (live-app screenshots) is the hero of every beat.

## Hook (first 2-3 seconds)
The real courses page in Russian (filtered: age 3-6, music, Russian) in a clean browser frame, camera pushing onto "Olgas Musikstudio" while George says "She found the right music course for her daughter." Then a hard turn: a German sentence fills the frame ("Für eine Probestunde rufen Sie uns bitte an.") and a German phone menu plays under "Then the page said: call us. In German." The menu keeps talking for a second on its own ("... drücken Sie die Zwei.") and is cut off by the reveal.

## Key moments (the middle)
- The wordmark lands in silence after the phone menu is cut: "An" in ink, "kommen" in pine, tagline streaming word by word with the voice. Music starts here.
- The home page flips through all six languages on the beat (English, Deutsch, Русский, Українська, العربية with the layout mirrored, Türkçe) while the six language names hold on screen and the active one is marked.
- The provider page: the camera moves to the "We can call them for you" box, the cursor presses the real button (lifted from the screenshot and animated). The call card opens with the amber live dot, and the German first sentence types out: "Guten Tag! Hier ist die KI-Assistentin von Maria Petrova." with "KI-Assistentin" marked and the Russian line under it.
- The real result card in Russian slides up and its check draws: "Вы записаны на пробное занятие".

## Outro / punchline
End card: wordmark, the URL ankommen-dresden.lovable.app with a pine rule drawing under it, and the six language names in their own scripts. George reads the URL. Music settles out.

## User flow worth showing
Find a course (courses page, filtered) → press Call for me on the provider page → the assistant calls in German and says it is an AI → the result comes back in Russian (booked trial lesson).

## Tone
- Preset: polished
- Creative direction: a calm, honest product launch for families; confident, never hype (with warmth)
- Interpretation: few scenes, long holds, soft crossfades and slides, ease-out motion (power2/power3/expo.out), 2-3 quiet SFX, the music enters only after the problem beat so the reveal feels like relief. No hype words anywhere.

## Format: landscape — 1920x1080
## Duration: 25.9 s (brief: 20-26 s; narration alone is 24.1 s, nar_l5 sped up 1.1x to fit)

## Visual identity (from the project, design system "Bilingual paper v3")
- Background: paper #F7F4EC (card #FFFDF8, paper-deep #EFE9DC, border #D9D2C3)
- Accent: pine #1F5C4A (pressed #174A3B, tint #E6EEE9); amber #D98E04 only for the live dot (ring #8A5A00, word "Live")
- Text: ink #1C2420, ink-muted #5B635E
- Display font: Fraunces 600, "SOFT" 50 (German text Fraunces 400); Cyrillic headings Source Serif 4 600; Arabic Noto Naskh Arabic 600
- Body font: Source Sans 3
- Strongest visual element: the wordmark ("An" ink + "kommen" pine) and the pine Call-for-me button
- Bans honoured: no purple, gradients, blobs, glow, glass, blur, heavy shadows, emoji, flags, people, pill badges, uppercase eyebrows, SaaS words, fake numbers

## Share copy (draft)
Ankommen is a guide for families starting in Germany: courses, events and help in six languages, and a Call for me button that phones in German, says it is an AI, and brings the answer back in your language. Built this weekend in Dresden.

## Voiceover script
User instruction for this run: the voice comes from the pre-generated ElevenLabs clips (George), not Kokoro. Lines are PRODUCTION.md section 3.6, verbatim:
- nar_l1 "She found the right music course for her daughter." (2.32 s)
- nar_l2 "Then the page said: call us. In German." (3.11 s)
- nar_l3 "Ankommen. Your guide to starting in Germany." (3.04 s)
- nar_l4 "Courses, events and help, in six languages." (3.12 s)
- nar_l5 "And when a call in German is needed: Call for me. It says it is an AI, makes the call, and brings the answer back in your language." (9.44 s, played at 1.1x = 8.60 s)
- nar_l6 "ankommen-dresden.lovable.app" (3.04 s)
Kinetic captions stream word by word from each clip's words.json (scaled for nar_l5). No captions for nar_l3 and nar_l6: the tagline and the URL on screen are the caption, streaming with the voice.

## Audio direction
- Role: calm narration first; music is a warm bed that enters at the reveal
- Music: bundled happy-beats-business-moves-vol-12 (steady and clean, polished). ElevenLabs music/SFX were not produced (key lacks permission), so bundled assets are used.
- Music treatment: starts at the wordmark (first beat locked to the reveal), low under narration, lifts slightly in the short gaps, fades out over the last second
- Mix as rendered: voiceover carve (hyperframes-audio carve.mjs, strength 0.3; the default 0.8 left the bed at about -49 dB, inaudible) plus a volume lane at 0.6; master after the final -1.9 dB step: -16.0 LUFS integrated, true peak -3.3 dBTP (the renderer itself delivers about -14 LUFS). The German phone menu is band-limited to a phone line (320-3300 Hz) and cut on the reveal.
- Music cue guidance: preset `assets/music/cues/happy-beats-business-moves-vol-12-by-ende-dot-app.music-cues.json` (109.96 BPM). Track time 0.56 s is placed on the wordmark. Strong cue 9.29 s (0.97) lands on the Call-for-me press at "Call for me"; beat grid drives the six language flips (every beat, images not text, and the names hold as a set).
- Audio-reactive treatment: subtle. The phone-menu speaking bars in the hook follow the RMS of the German phone menu itself; the browser frame's shadow depth breathes with the music RMS. No waveform or equalizer graphics.
- SFX posture: sparse (3): soft impact at the wordmark, a quiet click on the button press, a warm bong when the result check draws
- Audio-coupled moments: IVR cut-off at the reveal; button press; check drawing
- Restraint rule: nothing may cover the narration; no whooshes, no risers, no ring tones

## Storyboard

### Scene 1 — Found it — 0.0-2.75 s
Browser frame (URL ankommen-dresden.lovable.app/courses) with the real courses page in Russian, filtered to 3-6 / music / Russian. Camera pushes from the page title down onto the "Olgas Musikstudio" listing (the "checked by phone" badge stays below the frame edge: it belongs to the end of the story). A pine outline draws around the listing on "music course".
Sequential/interaction: caption words rise in with the voice
Audio intent: voice alone, intimate
Audio-coupled idea: none
Music: none
Transition mood: hard → Scene 2

### Scene 2 — The German wall — 2.6-6.95 s
Paper frame, anchored left. Small line "Olgas Musikstudio" in muted UI type. The German sentence "Für eine Probestunde rufen Sie uns bitte an." in Fraunces 400, large; "rufen Sie uns bitte an" gets a pine underline on "call us". Below: a phone row with the demo number from the listing, live speaking bars and the German phone-menu words streaming as they are heard. Slow camera push for tension.
Sequential/interaction: IVR words stream in sync with the audio
Audio intent: tension without drama: the German phone menu under the voice, then alone for about a second
Audio-coupled idea: bars react to the IVR audio; IVR is cut on the reveal
Music: none
Transition mood: hard cut to silence → Scene 3

### Scene 3 — Reveal — 6.85-10.25 s
Wordmark "Ankommen" lands letter by letter from a mask; tagline "Your guide to starting in Germany" streams word by word with the voice; a pine hairline draws. Held long.
Sequential/interaction: tagline words synced to voice
Audio intent: relief; music enters on its first beat, one soft impact
Transition mood: soft slide → Scene 4

### Scene 4 — Six languages — 10.05-13.5 s
Browser frame on the right with the real home page; the six language names stacked on the left in their own scripts. On each music beat the page wipes to the next language (en, de, ru, uk, ar mirrored right-to-left, tr) and the matching name is marked. The set holds after the last flip.
Sequential/interaction: yes, 6 flips on consecutive beats; names stay readable as a set
Audio intent: warm and steady
Transition mood: continuous (the frame glides to center) → Scene 5

### Scene 5 — Call for me — 13.35-22.2 s
Same browser frame, now the real Olgas Musikstudio page (English). Camera moves to the "We can call them for you" box; the cursor presses the pine button (lifted from the screenshot), beat-locked to "Call for me". The page steps back; a call card opens: amber live dot + "Live", timer, and the German first sentence typing out, "KI-Assistentin" marked on "AI", Russian line below. On "brings the answer back" the real Russian result card slides up and its check draws.
Sequential/interaction: yes, simulated click, typed German line, check draw
Audio intent: quiet click, warm bong on the result
Transition mood: soft crossfade → Scene 6

### Scene 6 — End card — 22.05-25.9 s
Wordmark, the URL large with a pine rule drawing under it, the six language names in a row. Hold. Music fades.
Audio intent: settle, voice reads the URL
Transition mood: end on the card (no black)

**Music mood for this video:** warm, steady, restrained
**Audio summary:** the voice and a German phone menu carry the problem in silence, the music arrives with the name, stays low under the voice, and settles on the URL.

## Revision 27.09 (review fixes)
- Result card: the real card shortened below the bring-list (`assets/screens/crop-resultcard-ru-short.png`: top 836 px + the card's own bottom 52 px of `crop-resultcard-ru.png`), so the German details table and the half-cut row are gone.
- Call card: German line types at 0.09 s per word from 16.7 s (complete about 17.5 s), Russian line from 17.8 s; card opacity and slide split, page dim starts 16.3 s.
- Scene 1 starts below the app header (no wordmark before the reveal) and ends with the outline's bottom edge in view (badge still out of frame).
- IVR starts at media 6.70 s so "die" is heard whole; the on-screen menu line starts with "… die Eins."
- share-copy.txt no longer claims real calls (states the demo is role-played in the browser).
- AGENTS.md / CLAUDE.md scaffold files are git-ignored in composition/.

Rebuild (from composition/): `python ../tools/build_data.py` (if timings change), `npx hyperframes check`, `npx hyperframes render --quality delivery --output ../launch.render.mp4`, then from the launch folder:
1. poster: `ffmpeg -ss 19.6 -i launch.render.mp4 -frames:v 1 -q:v 2 launch.jpg`
2. stage copy (no poster): `ffmpeg -i launch.render.mp4 -map 0 -c:v copy -af volume=-1.9dB -c:a aac -b:a 192k -movflags +faststart launch-stage.mp4`
3. bake: `ffmpeg -i launch.render.mp4 -i launch.jpg -filter_complex "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]" -map "[v]" -map 0:a -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -c:a copy -movflags +faststart launch.poster.mp4`
4. loudness last: `ffmpeg -i launch.poster.mp4 -map 0 -c:v copy -af volume=-1.9dB -c:a aac -b:a 192k -movflags +faststart launch.mp4` (check with `-af ebur128=peak=true`: about -16 LUFS)

Files: `launch.mp4` (poster in frame 0, for posting), `launch-stage.mp4` (same, no poster frame: play this on stage), `launch-nomusic.mp4` (voice + phone menu + SFX only, with poster: use this if the ende.app music licence is not confirmed).
