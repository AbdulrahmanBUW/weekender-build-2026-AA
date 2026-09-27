# Pixel Dresden: build brief (27 Sep 2026, same-day build)

**Goal:** Pokemon-like (GBA-era, top-down 3/4 view) ORIGINAL pixel art on the live Ankommen site: a Dresden skyline band on
the home page with newcomers walking along the Elbe, small scenes on the pillar pages and the 404 page. Decided by the owner
(DEC-004). Research and sources: vault `Concepts/Pixel Art Plan.md`. Never use or imitate Nintendo/Pokemon assets, logos or
the word "Pokemon" anywhere in files.

**Deadline:** art + code ready for review by **12:05**, publish decision at **12:30**. Ship what is clean; a missing scene
simply does not render. Priority: home band + walkers > services > courses > events > communities > library > 404.

## Palette (use ONLY these; you may add at most 4 extra colours, log them in your report)
ink #1C2420 · ink2 #3A3F3A · paper #F7F4EC · cream #EFE4CF · white #FFFFFF
sandstone #F1E4C6 #D9C49A #B59D73 #8C7453 #5E4C38 (Elbsandstein; the Frauenkirche has dark patina patches: mottle with the two darkest)
copper patina roofs #A9CDBB #74A590 #4E7E6B · pine #1F5C4A #174A3B
Elbe water #B7D1D6 #8DB2BD #638D9B · grass/trees #BCD08F #8FB068 #638A48 #3F6233
roof red #C9704F #93493A · street/stone grey #D3CDBF #A8A296 #77736A · tram yellow #FFD541 #D9A21B · Apotheke red #B4202A
gold #E0B04A · steel blue #6E97C9 #3F66A0
skin ramps (light, shadow): s1 #F7DCC8 #E4B9A0 · s2 #EDC29E #CF9C77 · s3 #C98E62 #A56E48 · s4 #A8703F #835530 · s5 #7F4E31 #5E3822 · s6 #573522 #3D2417
hair: black #231F1C · dark brown #4A3326 · brown #7A5234 · red #B5532E · blonde #D9B26A · grey #B3ADA3
clothes: sage #8FA888 · mustard #D9A441 · terracotta #C4674A · navy #34496B · teal #3E7F7F · denim #5C7BA6 · charcoal #4A4E52 · dusty rose #C98B8B
No purple/violet/indigo, no neon, no gradients.

## Style
Top-down 3/4 view like GBA town RPGs: building fronts visible, roofs seen slightly from above. Light from the top-left.
3–4 shades per material, selective outlines (ink for silhouettes, darker shade of the fill inside). Minimal dithering.
**No text, letters or logos inside images** (the UI has 6 languages); symbols are fine (a note for music, a red "A"-shaped
pharmacy sign is a symbol, a pretzel for the bakery, a sun for the Kita). No flags. Dresden must be recognisable:
- **Frauenkirche:** light sandstone with dark patches, square body, the huge bell-shaped stone dome ("Steinerne Glocke"),
  a lantern and a golden cross on top, four corner towers with small domes.
- **Katholische Hofkirche:** long nave with a balustrade and statues, copper-green roof, a tall slender tiered baroque tower.
- **Semperoper:** curved (semicircular) front with two rows of arches, a big central portal niche topped by a quadriga
  (four-horse chariot), copper-green roof.
- **Kunstakademie** glass dome ("lemon squeezer", ribbed, with a small golden figure on top) on the Brühl's Terrace wall.
- **Hausmannsturm** (castle tower, slim with a copper spire). **Augustusbrücke:** sandstone arch bridge over the Elbe.
- **Fernsehturm:** far away on a hill, slim concrete shaft, cabin near the top, red/white antenna tip.
- **Zwinger Kronentor:** baroque gate with an onion dome and a golden crown. **Kunsthofpassage:** blue facade with funnel
  drainpipes, yellow facade. **Tram:** yellow two-car low-floor tram (no DVB logo).

## Files and sizes (logical pixels; the site scales by whole numbers with image-rendering: pixelated)
Lovable repo `C:/Users/a_rahman/Desktop/Automation/hallotermin-paper` (edit only the files you own):
| File | Owner | Spec |
|---|---|---|
| `public/pixel/home.png` | scenes-home | 960×128 (shown at 2× = 1920 px wide, full-bleed; phones crop around focusX), transparent sky (paper page colour shows through). The outer ~32 px on each side taper off in stepped pixel edges (meadow and river end softly into the paper) so ultra-wide screens look intentional. Centre ~640 px: skyline across the Elbe: Frauenkirche (largest, left-centre), Kunstakademie dome, Hausmannsturm, Hofkirche tower, Semperoper (right). Fernsehturm small and faint on a far hill at the left. River band with the Augustusbrücke arches roughly in the middle. Foreground: Neustadt bank with meadow, a paved walkway along the bottom (walkers' lane, feet at y=122), benches, lamps, a few trees, at the far right a small corner with a bakery kiosk (pretzel symbol) and a tram stop shelter. |
| `public/pixel/tram.png` | scenes-home | horizontal strip of 2 frames, each 64×20, tram facing right (left = mirrored by CSS); runs on the bridge deck |
| `public/pixel/scene-<id>.png` | scenes-pillars | 320×96 each, transparent sky, walkway at the bottom (feet at y=90). ids: `services` (Apotheke with red A-symbol sign, Bürgeramt: calm official building with a clock, Kita: low colourful building with a sun sign and a small fence/slide), `courses` (music school in a Gründerzeit house, big studio window with a piano, note sign; a small sports hall), `events` (Zwinger Kronentor, a market stall on the Elbe meadows), `communities` (Kunsthofpassage facades, café table), `library` (library building with tall windows, reading bench under trees, book kiosk), `notfound` (empty tram stop with shelter and lamp, nothing else) |
| `public/pixel/people.png` | people | 12 characters. Each character = a block of 3 rows (down, up, right) × 3 walk frames, cell 32×32 (character centred horizontally, feet on the bottom row y=31). Blocks laid out 4 per row → PNG 384×288. Props that move with the person (stroller, suitcase, wheelchair, child, cane) are drawn INSIDE the 32×32 cell for every frame. |
| `src/components/pixel/types.ts` | engineer | exactly the types below |
| `src/components/pixel/scenes.data.ts` | scenes-home writes `HOME`, scenes-pillars writes the others (engineer creates the file with stubs; scene agents replace ONLY their own export blocks, marked `// <home>` … `// </home>` etc.) |
| `src/components/pixel/people.data.ts` | people | `export const PEOPLE: PeopleDef` |
| `src/components/pixel/PixelScene.tsx`, `PixelPause.tsx`, route integration, `/credits`, strings | engineer | see engineer task |

```ts
// src/components/pixel/types.ts
export type SceneId = "home" | "services" | "courses" | "events" | "communities" | "library" | "notfound";
export type Lane = { y: number; x0: number; x1: number; stops: number[] }; // y = feet baseline (scene px); walkers walk x0..x1, pause at stops (doors, benches)
export type Tram = { src: string; frameW: number; frameH: number; frames: number; y: number; x0: number; x1: number; speed: number }; // y = top of tram on the bridge deck; speed px/s
export type SceneDef = { id: SceneId; src: string; w: number; h: number; focusX: number; lanes: Lane[]; walkers: number; tram?: Tram };
export type CharDef = { id: string; label: string; col: number; row: number }; // block position in people.png (block = 96×96)
export type PeopleDef = { src: string; cell: 32; frames: 3; rows: { down: 0; up: 1; right: 2 }; cycle: number[]; speed: number; chars: CharDef[] };
```
`focusX` = the x that must stay visible when a phone crops the scene (home: the Frauenkirche's centre).

## Source scripts (team repo, reproducible)
`scripts/pixel/make_home.py`, `make_scenes.py`, `make_people.py` (Python 3.13 + Pillow; sprites drawn as code: character grids /
shape primitives with the palette above; export 1× PNG, optimised, indexed if possible). Preview renders (6× upscales) go to
`docs/pixel/previews/`. Budget: all pixel PNGs together ≤ 120 KB.

## The 12 newcomers (people agent; base = the 6 Pixel Agents sprites, MIT, recoloured + overlays + props)
1 woman, s3 skin, sage hijab, rolling suitcase · 2 man, s6 skin, short afro, pushes a stroller · 3 grandmother, s1 skin, grey bun,
holds a small child's hand (child with a Kita bag) · 4 young man, s4 skin, curly hair, wheelchair with backpack · 5 man, s2 skin,
trimmed beard, glasses, document folder · 6 teen, s5 skin, braids, violin case · 7 woman, s1 skin, short black bob, toddler in a
sling · 8 older man, s4 skin, bald, grey beard, white cane · 9 young woman, s1 skin, long red hair, backpack + book ·
10 parent, s3 skin, dark hair, walking with a child holding hands · 11 woman, s6 skin, mustard head wrap, bag with a pretzel ·
12 man, s3 skin, ponytail, looks at a phone. Newcomer = what they carry, never ethnicity. No national costumes, no flags.
Same body proportions and face style for everyone (two-pixel eyes like the base).

## Rules for all builders
Never use the in-app Browser pane tools (use headless puppeteer-core from the scratch tools folder). Never stop the relay on
:8787 or any server. Never git commit or push (the lead does). Never touch the database. Do not add npm packages (package.json
and bun.lock must not change). Credits text for the base sprites: "Character sprites based on Pixel Agents
(https://github.com/pixel-agents-hq/pixel-agents), Copyright (c) 2026 Pablo De Lucca, MIT License. Based on MetroCity by
JIK-A-4 (CC0)." Palette credit: "Palette based on AAP-64 by Adigun A. Polack, adapted to the Ankommen colours."
