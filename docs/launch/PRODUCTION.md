# Ankommen: launch production brief (presentation + videos)

**What this is:** the single source for the Sunday presentation, the launch video (/brag) and the demo video.
Every script line, voice and file path below is binding for all builders. Story first, then files.
**Event:** Weekender Build, Dresden, Sun 27 Sep 2026. Demo slot 13:00, 3 minutes. Live URL: https://ankommen-dresden.lovable.app

## 1. Story in one breath
Maria (a proto-persona, not a real person) moved to Dresden. Her daughter is four. She speaks Russian.
She finds a music course, and the page says: "Call us for a trial lesson." In German. That is where parents stop.
**Ankommen** ("Your guide to starting in Germany") is one place for international families: courses, events, communities,
health and services, guides, in 6 languages (EN, DE, RU, UK, AR right-to-left, TR). On every page: **Call for me**.
Maria tells the assistant in Russian what she needs. It fills the request, shows her the German opening line, she approves.
The AI assistant phones the place **in German**, says in its first sentence that it is an AI, only agrees to times she
approved, reads the answer back, and brings the result back **in Russian**. The course page then shows "checked by phone".

Facts we may show (from the live database, 27 Sep 10:05): 162 places · 92 family providers · 44 upcoming events ·
8 guides × 6 languages · 6 UI languages · 10 call task types · 4 n8n workflows in the loop (01 brief, 04 intake,
05 translate line, 06 result). Role-play calls booked in 70–95 s (RUN-012/014). Brief written in about 10 s.
65% of immigrants in Germany name lack of German as the biggest obstacle in everyday life (OECD 2024).
**Do not claim:** real calls to real businesses (all calls are browser role-plays), "fully compliant", invented numbers,
ratings, testimonials or logos. Olgas Musikstudio is a demo listing. No real phone line yet.

## 2. Voices (all audio is made with Deepgram or ElevenLabs, nothing else)
Keys: read at runtime from `services/voice-relay/.env` (`DEEPGRAM_API_KEY`, `ELEVENLABS_API_KEY`). Never print, log,
echo or write a key anywhere. The ElevenLabs key has text-to-speech permission only (no voice listing), so use the
premade voice IDs below. Models: ElevenLabs `eleven_v3` for expressive character lines (fallback `eleven_multilingual_v2`),
Deepgram `aura-2-*` via `POST https://api.deepgram.com/v1/speak?model=<voice>&encoding=mp3`.

| Role | Provider / voice | Why |
|---|---|---|
| AI call assistant, German | Deepgram `aura-2-viktoria-de` | the exact production call voice |
| Receptionist "Herr Böhme", German, Dresden | Deepgram `aura-2-julius-de` | native German male, clear contrast to Viktoria; light Saxon phrasing in the text ("Nu", "halb fünf") |
| Automated phone menu (problem beat) | Deepgram `aura-2-aurelia-de` | native German, formal |
| App assistant, English | Deepgram `aura-2-helena-en` | the production English voice of the app |
| App assistant, RU / UK / AR / TR | ElevenLabs Sarah `EXAVITQu4vr4xnSDxMaL` | the production voice for these languages |
| Maria (parent), Russian | ElevenLabs Jessica `cgSgspJ2msm6clMCkdW9` (fallback Laura `FGY2VhQYpPwHp6x1f3ZJ`) | warm, natural Russian with eleven_v3 |
| Narrator, English | ElevenLabs George `JBFqnCBsd6RMkjVDRZzb` (fallback Alice `Xb7hH8MSUJpSbSDYk0k2`) | warm, calm storyteller |

Post-processing (ffmpeg): loudness-normalise every clip to about -16 LUFS (speech), trim leading/trailing silence to ≤ 80 ms.
Receptionist lines additionally get a **phone-line version** (`*_phone.mp3`: band-pass 300–3400 Hz, light compression) for the videos.
For every clip also write word timings (`<id>.words.json`: `[{"w","start","end"}]`), from ElevenLabs `/with-timestamps`
alignment or from Deepgram speech-to-text (`nova-3`, `language` set) run on the clip. Captions in videos and the deck sync to these.

## 3. Audio script (clip id → voice → text). Russian lines show as subtitles under German ones.

### 3.1 Problem beat
- `ivr_de` · aurelia · "Herzlich willkommen im Musikstudio. Unsere Bürozeiten: Montag bis Donnerstag, neun bis zwölf Uhr. Für Anmeldungen drücken Sie die Eins. Für Fragen zu Kursgebühren drücken Sie die Zwei. Alle Leitungen sind zurzeit belegt." (may be sped up 1.1–1.15× so it feels rushed)

### 3.2 Voice intake (Russian, in the app, "Call for me" button)
- `intake_ru_1` · Sarah · "Здравствуйте! Я позвоню за вас в Olgas Musikstudio. Что мне у них спросить?"
- `maria_ru_1` · Maria · "Здравствуйте! Я хочу записать дочку на музыку. Ей четыре года. Лучше во вторник или в четверг, после трёх."
- `intake_ru_2` · Sarah · "Поняла. Я спрошу про свободное место или пробный урок во вторник или в четверг после 15:00. Позвонить им на немецком?"
- `maria_ru_2` · Maria · "Да, позвоните, пожалуйста."

### 3.3 The call (German, browser role-play; order = dialogue order; subtitle = Russian)
| id | voice | German | Russian subtitle |
|---|---|---|---|
| `call_01_r` | julius | "Musikstudio Olga, Böhme, guten Tag?" | «Музыкальная студия Ольги, Бёме, добрый день?» |
| `call_02_a` | viktoria | "Guten Tag! Hier ist die KI-Assistentin von Maria Petrova. Ich rufe für sie an, weil ihr Deutsch noch nicht so gut ist, und wollte fragen, ob es in Ihrem Kurs für ein vierjähriges Kind noch einen Platz oder eine Probestunde gibt." | «Добрый день! Это ИИ-ассистент Марии Петровой. Я звоню за неё, потому что она пока плохо говорит по-немецки, и хотела спросить, есть ли место или пробный урок для ребёнка четырёх лет.» |
| `call_03_r` | julius | "Nu, da haben Sie Glück. Die Früherziehung für Vier- bis Sechsjährige ist dienstags und donnerstags um halb fünf. Ich könnte Ihnen aber auch Samstag früh um zehn anbieten." | «Вам повезло. Занятия для детей 4–6 лет по вторникам и четвергам в 16:30. Могу предложить и субботу в 10 утра.» |
| `call_04_a` | viktoria | "Danke! Samstag passt leider nicht, Frau Petrova kann nur dienstags oder donnerstags ab fünfzehn Uhr. Geht eine Probestunde am Donnerstag um sechzehn Uhr dreißig?" | «Спасибо! Суббота, к сожалению, не подходит: госпожа Петрова может только во вторник или четверг после 15:00. Можно пробный урок в четверг в 16:30?» |
| `call_05_r` | julius | "Donnerstag, halb fünf, das geht. Die Probestunde ist kostenlos. Bringen Sie bitte Hausschuhe mit." | «Четверг, 16:30, подходит. Пробный урок бесплатный. Возьмите, пожалуйста, сменную обувь.» |
| `call_06_a` | viktoria | "Ich wiederhole: Probestunde am Donnerstag, dem ersten Oktober, um sechzehn Uhr dreißig, kostenlos, bitte Hausschuhe mitbringen. Ist das richtig?" | «Повторяю: пробный урок в четверг, 1 октября, в 16:30, бесплатно, взять сменную обувь. Всё верно?» |
| `call_07_r` | julius | "Ja, genau so." | «Да, именно так.» |
| `call_08_a` | viktoria | "Wunderbar, ich notiere das. Vielen Dank, Herr Böhme, und auf Wiederhören!" | «Отлично, записываю. Большое спасибо, господин Бёме, до свидания!» |
| `call_09_r` | julius | "Gerne, auf Wiederhören." | «Пожалуйста, до свидания.» |

Also export `call_full.mp3` (all nine lines in order, 0.35–0.6 s gaps, receptionist in the phone-line version) and
`call_full.timeline.json` (`[{id, speaker, start, end, de, ru}]` in seconds on that combined track).
Key moments to highlight on screen: line 02 "KI-Assistentin" (says it is an AI in the first sentence);
line 04 "Samstag passt leider nicht" (declines a time Maria did not approve); line 06 (reads back before booking).

### 3.4 Result (Russian, app read-back)
- `result_ru` · Sarah · "Готово! Пробный урок в Olgas Musikstudio: четверг, 1 октября, в 16:30. Урок бесплатный. Возьмите с собой сменную обувь."

### 3.5 "Call for me" in six languages (deck language beat; the app assistant voice per language)
- `lang_en` · helena · "I'll call them in German for you, and tell you the answer in English."
- `lang_de` · viktoria · "Ich rufe für Sie an und sage Ihnen gleich, was sie gesagt haben."
- `lang_ru` · Sarah · "Я позвоню за вас на немецком и расскажу ответ по-русски."
- `lang_uk` · Sarah · "Я зателефоную замість вас німецькою і розповім відповідь українською."
- `lang_ar` · Sarah · "سأتصل بهم بالألمانية نيابةً عنك، وأخبرك بالجواب بالعربية."
- `lang_tr` · Sarah · "Sizin yerinize Almanca arayacağım ve cevabı size Türkçe söyleyeceğim."

### 3.6 Launch video narration (English, George; ≈ 22 s total, one clip per line)
- `nar_l1` "She found the right music course for her daughter."
- `nar_l2` "Then the page said: call us. In German."
- `nar_l3` "Ankommen. Your guide to starting in Germany."
- `nar_l4` "Courses, events and help, in six languages."
- `nar_l5` "And when a call in German is needed: Call for me. It says it is an AI, makes the call, and brings the answer back in your language."
- `nar_l6` "ankommen-dresden.lovable.app"

### 3.7 Demo video narration (English, George; bridges only, the dialogue carries the video)
- `nar_d1` "This is Maria. She is new in Dresden, and she speaks Russian."
- `nar_d2` "Ankommen shows her courses, events and help in her own language."
- `nar_d3` "She taps Call for me, and just says what she needs."
- `nar_d4` "Before anything happens, she sees what the assistant will say in German. She approves."
- `nar_d5` "Now the assistant calls. Listen to the first sentence."
- `nar_d6` "The answer comes back in Russian. No audio is stored, only text. And the course page now shows: checked by phone."
- `nar_d7` "Ankommen. Built this weekend in Dresden with Lovable, n8n, Supabase, Deepgram, ElevenLabs and Claude."

## 4. Visual language (the app's design system "Bilingual paper v3")
Colours: paper `#F7F4EC` (background) · card `#FFFDF8` · paper-deep `#EFE9DC` · sand `#F2E6D3` (sparingly) · ink `#1C2420` ·
ink-muted `#5B635E` · pine `#1F5C4A` (primary, hover `#174A3B`) · pine-tint `#E6EEE9` · amber `#D98E04` **only** for the
live dot (with ring `#8A5A00` and the word "Live") · amber-text `#8A5A00` on amber-tint `#FBF0D9` · border `#D9D2C3`.
Type: headings and wordmark **Fraunces** 600 (font-variation "SOFT" 50), German text Fraunces 400, body/UI **Source Sans 3**,
Cyrillic headings **Source Serif 4** 600, Arabic **Noto Naskh Arabic** 600 / **Noto Sans Arabic** 400, right-to-left.
Wordmark: "An" in ink + "kommen" in pine. Tagline "Your guide to starting in Germany".
Font files (self-hosted, copy them, never Google Fonts): `../hallotermin-paper/node_modules/@fontsource-variable/fraunces/files/`,
`@fontsource-variable/source-sans-3/files/`, `@fontsource/source-serif-4/files/`, `@fontsource/noto-naskh-arabic/files/`,
`@fontsource/noto-sans-arabic/files/` (all under `C:/Users/a_rahman/Desktop/Automation/hallotermin-paper/node_modules`).
Motion: purposeful, ease-out (power2/power3/expo.out), 250–900 ms for UI builds, text that must be read holds long enough.
Loops only for live things (live dot, speaking bars, audio waveform). Subtitles stream in word by word, synced to word timings.
**Bans:** purple/violet/indigo, gradients, blobs, glow, glassmorphism, blur, heavy shadows, neon, emoji, flags, stock photos,
drawn or AI-generated children or people, mascots, pill badges, uppercase eyebrows, rainbow category colours, generic SaaS words
(seamless, unlock, effortless, revolutionary, game-changer, streamline), fake numbers, ratings, logos or testimonials.
Real product UI (screenshots of the live app) is the hero of every beat. Real brand marks only where a tool is named in text.

## 5. Files (all under `docs/launch/`, relative paths so everything works from `file://` and offline)
```
docs/launch/
  PRODUCTION.md                 this brief
  README.md                     how to present, keys, how to regenerate (written last)
  presentation.html             the click-through deck (open in Chrome, full screen)
  assets/fonts/                 woff2 files
  assets/vendor/                gsap.min.js (+ plugins) copied from the scratch tools folder, qr code svg
  assets/screens/               live-app screenshots (desktop-*.png 1440x900 @2x, mobile-*.png 390x844 @2x, full-*.png full page)
  assets/screens/manifest.json  what each screenshot shows, language, route, size
  assets/n8n/                   workflow images 01/04/05/06 (PNG @2x) + manifest.json
  assets/diagrams/              architecture.png (+ copy of the updated docs/diagrams/architecture.html for the deck)
  audio/                        <id>.mp3, <id>_phone.mp3, <id>.words.json, call_full.mp3, call_full.timeline.json, manifest.json
  video/launch/                 brag launch video: composition/, brag-plan.md, launch.mp4, launch.jpg, share-copy.txt
  video/demo/                   demo walkthrough (stage backup): composition/, demo.mp4, demo.jpg
scripts/launch/                 make_audio.py, shoot_screens.mjs, render_n8n.mjs (reproducible generators)
```
Headless browser for screenshots: `puppeteer-core` with the installed Chrome (`C:/Program Files/Google/Chrome/Application/chrome.exe`),
already installed in the scratch tools folder `C:/Users/a_rahman/AppData/Local/Temp/claude/C--Users-a-rahman-Desktop-Automation-Weekender-Build/bc0649a2-1b68-40fd-bce5-cd66ad9c3d51/scratchpad/tools`
(also `gsap` there). UI language is chosen by the cookie `dmk_ui_lang` (`en|de|ru|uk|ar|tr`) on `ankommen-dresden.lovable.app`.
Key routes: `/` · `/courses` · `/events` · `/communities` · `/services` · `/library` · `/guides/kita-place-dresden` ·
`/p/ae0ae23b-0dd7-4f82-adf8-6fd78aa3456d` (Olgas Musikstudio, demo listing) · `/ask?resource=ae0ae23b-0dd7-4f82-adf8-6fd78aa3456d&type=course_enquiry` ·
`/r/fb99c45e-660b-4882-affa-1a71505f8f02` (the real end-to-end test call from RUN-026: booked, Russian summary).

## 6. House rules for builders
- Never use the in-app Browser pane tools (the user is using it); use headless puppeteer-core.
- Never stop the local relay on port 8787 or any preview server. Do not start dev servers of the Lovable repo.
- Never edit the Lovable repo (`hallotermin-paper`) or the database. Read only.
- No secrets in any file. The team repo is public.
- Plain B1 English on screen. Russian/Ukrainian/Arabic/Turkish text exactly as in this brief or as captured from the live app.
- The deck and videos must play offline (no CDN at show time).
