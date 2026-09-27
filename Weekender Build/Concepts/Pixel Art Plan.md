---
type: concept
tags: [pixel-art, ui, dresden, characters, licensing]
sources: ["https://codepen.io/punkydrewster713/pen/YooJJj", "https://commons.wikimedia.org/wiki/File:FrauenkircheDresdenSilhouette.svg", "https://developer.mozilla.org/en-US/docs/Web/CSS/image-rendering", "https://developer.mozilla.org/en-US/docs/Web/CSS/offset-path", "https://github.com/ElizaWy/LPC", "https://github.com/KennethJAllen/proper-pixel-art", "https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator", "https://github.com/Orama-Interactive/Pixelorama", "https://github.com/Retro-Diffusion/retro-diffusion-mcp", "https://github.com/Siilwyn/awesome-pixel-art", "https://github.com/Tuxemon/Tuxemon", "https://github.com/adryd325/oneko.js", "https://github.com/diivi/aseprite-mcp", "https://github.com/filidorwiese/spriteling", "https://github.com/giventofly/pixelit", "https://github.com/jenissimo/unfake.js", "https://github.com/lars-rooij/webmeji", "https://github.com/mapeditor/tiled", "https://github.com/nkzw-tech/palette-swap", "https://github.com/piskelapp/piskel", "https://github.com/pixel-agents-hq/pixel-agents", "https://github.com/pixellab-code/pixellab-mcp", "https://github.com/sedthh/pyxelate", "https://github.com/silveira/openpixels", "https://github.com/straker/kontra", "https://github.com/tonybaloney/vscode-pets", "https://huggingface.co/nerijs/pixel-art-xl", "https://jik-a-4.itch.io/metrocity-free-topdown-character-pack", "https://kenney.nl/assets/roguelike-modern-city", "https://kenney.nl/assets/rpg-urban-pack", "https://kenney.nl/assets/tiny-town", "https://limezu.itch.io/modernexteriors", "https://limezu.itch.io/serenevillagerevamped", "https://lospec.com/palette-list/aap-64", "https://lospec.com/palette-list/apollo", "https://lospec.com/palette-list/resurrect-64", "https://lospec.com/pixel-art-tutorials", "https://maygetsu.itch.io/cozy-town-tileset", "https://opengameart.org/content/2d-traintramcarriege", "https://opengameart.org/content/lpc-modern-streets", "https://opengameart.org/content/tiny-16-basic", "https://opengameart.org/content/zelda-like-tilesets-and-sprites", "https://pixel-boy.itch.io/ninja-adventure-asset-pack", "https://saint11.art/blog/pixel-art-tutorials/", "https://unsplash.com/license", "https://www.derekyu.com/makegames/pixelart.html", "https://www.slynyrd.com/pixelblog-catalogue", "https://www.unicode.org/reports/tr51/", "https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html"]
---
# Pixel Art Plan

**Definition:** how we could add Pokemon-like (original, GBA-style) Dresden pixel art to Ankommen: landmarks, shops and newcomer characters walking around the site. Researched 27 Sep 2026 by a research workflow (5 search lenses, every source licence-checked).

**Why it matters for us:** it makes "arriving in Dresden" visible and warm, but it changes our design rules (drawn people, loops) and every asset needs a clean licence.

**Related:** [[Frontend and UX Plan v3 (merged)]] · [[Monday-Morning Plan]] · [[Pitch Kit v2 (merged)]]

**Decision in one line:** use the GBA scale, with 16x16 tiles and 16x32 people. The bases are CC0 or MIT. The landmarks are original art from an AI generator, fixed up by hand. We write one React component of our own and lock everything to one palette. Nothing in this stack is share-alike, and no npm package is needed.

## 1. Recommended stack

| Need | Choice | Licence | Attribution text (for /credits) | Why |
|---|---|---|---|---|
| Characters (base) | Pixel Agents sprites, `webview-ui/public/assets/characters/char_0..5.png` (https://github.com/pixel-agents-hq/pixel-agents), built on MetroCity by JIK-A-4 (https://jik-a-4.itch.io/metrocity-free-topdown-character-pack) | The repo is MIT. MetroCity is CC0, but we only have that from search results because the itch page blocked us, so re-check it in a browser | "Character sprites from Pixel Agents (https://github.com/pixel-agents-hq/pixel-agents), Copyright (c) 2026 Pablo De Lucca, MIT License. Based on MetroCity by JIK-A-4, CC0." Add the full MIT notice. | These are true 16x32 walkers in modern clothes, with the cleanest licence, and we can use them today. Limits: only 6 people, 3 walk frames per direction (down, up, side; left is the side row mirrored), 2 with darker skin, and no props. |
| Characters (newcomer variants) | PixelLab MCP (https://github.com/pixellab-code/pixellab-mcp), cleaned up in Piskel (https://github.com/piskelapp/piskel) | We own the outputs and can use them commercially (ToS 3.3, 2025-11-23). We may not train other models on them. | None required. Optional: "Some sprites created with PixelLab (pixellab.ai), edited by the Ankommen team." | No open pack has a suitcase, a stroller or a child holding a hand at 16x32. PixelLab is the only tool that makes 4-direction walk cycles from a text prompt. You need to set up the account and token yourself. |
| Town, shops, tram | Kenney RPG Urban Pack (https://kenney.nl/assets/rpg-urban-pack), plus Kenney Tiny Town (https://kenney.nl/assets/tiny-town) for ground and trees | CC0 | Optional: "RPG Urban Pack and Tiny Town by Kenney (www.kenney.nl), CC0" | It is the only free modern town at 16x16. We change the shop signs: a pretzel for the bakery, the red A for the Apotheke, then Kita, Bürgeramt and music school. We make a yellow tram from one of the buses, with no DVB logo. Its own walkers are smaller, so don't use them as adults. |
| Landmarks | Original art from Retro Diffusion MCP (https://github.com/Retro-Diffusion/retro-diffusion-mcp). Fix the pixel grid with RD `fix_pixel_art` or proper-pixel-art (MIT), lock the colours with unfake.js (MIT), then do a hand pass in Piskel. | We own the outputs and can use them commercially (T&C section 7, 19 Aug 2025). | None required. Optional: "Pixel art generated with Retro Diffusion (retrodiffusion.ai), edited by the Ankommen team." | No openly licensed Dresden pixel art exists anywhere. RD can lock our palette (`input_palette`) and match a style from reference images or `create_user_style`, so all 10 landmarks look like one set. About $0.18 per image, so roughly $5-6 in total. References: the CC0 Frauenkirche silhouette, Unsplash photos and our own photos. If you want only one account, PixelLab `create_map_object` can make the landmarks too. |
| Animation runtime | Our own component of about 150-250 lines. CSS `steps()` switches the frames and one requestAnimationFrame loop inside `useEffect` moves the walkers. The loop follows the pattern of Pixel Agents `gameLoop.ts` and `tileMap.ts`. Colour variants are made offline with palette-swap (https://github.com/nkzw-tech/palette-swap). | MIT | In the ported file header: "Walker loop adapted from Pixel Agents, Copyright (c) 2026 Pablo De Lucca, MIT License" | No npm packages. The ready-made libraries we checked (Kontra, Spriteling, webmeji) each leak listeners, pull in npm packages or break server rendering. |
| Palette | A subset of about 24 colours from AAP-64 (https://lospec.com/palette-list/aap-64). Replace 24523b with #1F5C4A and 122020 with #1C2420, and add #F7F4EC. | No formal licence. A list of colours is generally not protected. | "Palette based on AAP-64 by Adigun A. Polack, adapted to the Ankommen brand colours." | It was the closest match to our colours when measured (pine dE 6.1, ink dE 4.3). It has a sandstone ramp, two skin ramps, a tram yellow (ffd541) and an Apotheke red (b4202a). Backup: Resurrect 64, whose author gave written permission for commercial use. |

**Fallback without AI:** the hosted Universal LPC Spritesheet Character Generator (ULPC) with its licence filter set to CC0 + CC-BY + OGA-BY. It gives a CC0 hijab, an OGA-BY wheelchair, children, older people and glasses. The costs: a larger 64px SNES look that doesn't mix with 16x32 sprites, and a full credits list.

## 2. All verified sources

| Name | Link | What | Art licence | Commercial use | Fit | Verdict |
|---|---|---|---|---|---|---|
| Pixel Agents | https://github.com/pixel-agents-hq/pixel-agents | 6 walkers at 16x32, plus a rAF loop and BFS paths | MIT repo; based on MetroCity (CC0) | Yes (MIT notice) | 8 | Use |
| MetroCity (JIK-A-4) | https://jik-a-4.itch.io/metrocity-free-topdown-character-pack | Layered 16x32 city people | CC0 (search text only) | Yes | 7 | Use; re-check the page |
| PixelLab MCP | https://github.com/pixellab-code/pixellab-mcp | AI characters with 4- or 8-direction walk, map objects | Outputs are ours | Yes | 8 | Use for variants |
| Universal LPC Generator | https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator | 64px layered sprites: hijab, wheelchair, child, elderly | Per item (CC0, CC-BY, OGA-BY, CC-BY-SA, GPL); has a filter | Yes, with credits | 7 | Fallback |
| LPC Revised (ElizaWy) | https://github.com/ElizaWy/LPC | 32px people, 9 skin tones, many hair styles | OGA-BY 3.0 | Yes, with credits | 5 | Maybe (use it through ULPC) |
| OpenPixels | https://github.com/silveira/openpixels | 32x48 chibis, turban, afro | CC-BY-SA 4.0; some layers copy others' IP | Share-alike | 4 | Avoid |
| Tuxemon | https://github.com/Tuxemon/Tuxemon | Open-source Pokemon-like game | Mixed; many sprites unlabelled, some NC | Unclear | 3 | Style reference only |
| LimeZu Modern Interiors/Exteriors | https://limezu.itch.io/modernexteriors | Paid modern 16px city plus a character generator | Custom licence: no redistribution, credit required | Yes (paid) | 6 | Not now |
| Kenney RPG Urban Pack | https://kenney.nl/assets/rpg-urban-pack | 480 modern 16px tiles and vehicles | CC0 | Yes | 8 | Use |
| Kenney Tiny Town | https://kenney.nl/assets/tiny-town | 16px ground, paths, trees | CC0 | Yes | 7 | Use (recolour) |
| Kenney Roguelike Modern City | https://kenney.nl/assets/roguelike-modern-city | 16px city blocks, flatter view | CC0 | Yes | 6 | Secondary |
| LPC Modern Streets / [LPC] Streets | https://opengameart.org/content/lpc-modern-streets | 32px streets; German signs in [LPC] Streets | CC0 / CC-BY-SA+GPL | Yes / share-alike | 6 | Fallback route only |
| Ninja Adventure | https://pixel-boy.itch.io/ninja-adventure-asset-pack | GBA-like pack with a ninja theme | CC0 | Yes | 6 | Maybe (nature, water) |
| ArMM1998 Zelda-like | https://opengameart.org/content/zelda-like-tilesets-and-sprites | Bridge, fountain, market stall | CC0 | Yes | 5 | Maybe (skip the trees) |
| LimeZu Serene Village | https://limezu.itch.io/serenevillagerevamped | Free 16px village | CC-BY 4.0 (search text only) | Yes, with credit | 5 | Maybe |
| Tiny 16: Basic | https://opengameart.org/content/tiny-16-basic | 16-colour town | CC-BY / OGA-BY | Yes, with credit | 5 | Maybe |
| Cozy Town (Maygetsu) | https://maygetsu.itch.io/cozy-town-tileset | Pastel 16px town | Unverified, conflicting | Unclear | 4 | Check the page first |
| Retro Diffusion MCP | https://github.com/Retro-Diffusion/retro-diffusion-mcp | AI top-down assets with a palette lock | Outputs are ours | Yes | 9 | Use for landmarks |
| proper-pixel-art | https://github.com/KennethJAllen/proper-pixel-art | Fixes the pixel grid of AI images | Tool (MIT) | Yes | 8 | Use |
| unfake.js | https://github.com/jenissimo/unfake.js | Locks images to a fixed palette | Tool (MIT) | Yes | 8 | Use |
| Piskel | https://github.com/piskelapp/piskel | Web sprite editor | Tool (Apache-2.0) | Yes | 8 | Use |
| Pixelorama | https://github.com/Orama-Interactive/Pixelorama | Editor with layers and tilemaps | Tool (MIT) | Yes | 7 | Alternative |
| aseprite-mcp | https://github.com/diivi/aseprite-mcp | Lets Claude drive Aseprite | MIT; Aseprite is paid | Yes | 4 | Skip |
| Pixel It | https://github.com/giventofly/pixelit | Pixelates an image | Tool (MIT) | Yes | 4 | Silhouette tests only |
| Pyxelate | https://github.com/sedthh/pyxelate | Photo to 8-bit | Tool (MIT) | Yes | 3 | Skip |
| pixel-art-xl LoRA | https://huggingface.co/nerijs/pixel-art-xl | Self-hosted image model | OpenRAIL-M | Yes | 2 | Avoid (needs a GPU) |
| Frauenkirche silhouette | https://commons.wikimedia.org/wiki/File:FrauenkircheDresdenSilhouette.svg | Accurate front view | CC0 | Yes | 6 | Reference |
| Unsplash + German §59 UrhG | https://unsplash.com/license | Reference photos; freedom of panorama | Unsplash licence | Yes | 7 | Reference |
| OGA 2D tram | https://opengameart.org/content/2d-traintramcarriege | Side-view vector tram | CC0 | Yes | 2 | Avoid (wrong view) |
| palette-swap | https://github.com/nkzw-tech/palette-swap | Makes colour variants from one sheet | MIT (don't use the Yoshi examples) | Yes | 7 | Use offline |
| oneko.js | https://github.com/adryd325/oneko.js | One sprite walking on a website | Code MIT; the cat sprite is not usable | Code only | 4 | Pattern only |
| vscode-pets | https://github.com/tonybaloney/vscode-pets | A small behaviour graph per pet | Code MIT; art mixed | Code only | 6 | Pattern only |
| Kontra | https://github.com/straker/kontra | Small game library | MIT | Yes | 5 | Skip (leaks listeners) |
| Spriteling | https://github.com/filidorwiese/spriteling | DOM sprite animation | ISC; demo art NC-ND | Yes | 3 | Avoid (needs npm packages) |
| webmeji | https://github.com/lars-rooij/webmeji | Mascot that walks the page | Code Unlicense; skins are fan art | Code only | 3 | Avoid |
| CodePen walking sprites | https://codepen.io/punkydrewster713/pen/YooJJj | CSS `steps()` walk demo | Code MIT; sprite unclear | Code only | 5 | Pattern only |
| Tiled | https://github.com/mapeditor/tiled | Map editor | Tool (GPL/BSD) | Yes | 5 | Monday, if we build a full town |
| MDN offset-path | https://developer.mozilla.org/en-US/docs/Web/CSS/offset-path | CSS movement along a path | n/a | Yes | 7 | Use for fixed lanes |
| MDN image-rendering | https://developer.mozilla.org/en-US/docs/Web/CSS/image-rendering | Keeps pixels sharp when scaled | n/a | Yes | 8 | Use |
| WCAG 2.2 SC 2.2.2 | https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html | Moving content needs a pause | n/a | n/a | 8 | Requirement |
| AAP-64 | https://lospec.com/palette-list/aap-64 | Closest palette to our brand | No formal licence | Yes (credit) | 9 | Master palette |
| Resurrect 64 | https://lospec.com/palette-list/resurrect-64 | Muted palette | Author allows commercial use | Yes (credit) | 8 | Backup palette |
| Apollo | https://lospec.com/palette-list/apollo | Low-chroma palette with warm ramps | No formal licence | Yes (credit) | 7 | Skin ramps |
| SLYNYRD Pixelblog | https://www.slynyrd.com/pixelblog-catalogue | Top-down sprite and tile rules | All rights reserved | Learning only | 9 | Use as our spec |
| Lospec tutorials | https://lospec.com/pixel-art-tutorials | Outline and shading rules | Per author | Learning only | 7 | Use |
| saint11.art | https://saint11.art/blog/pixel-art-tutorials/ | Silhouette, walk and modular tutorials | No licence | Learning only | 7 | Use |
| Derek Yu basics | https://www.derekyu.com/makegames/pixelart.html | Checklist for reviewing sprites | All rights reserved | Learning only | 7 | Use |
| Unicode UTS #51 §2.4 | https://www.unicode.org/reports/tr51/ | How to show diverse people in tiny figures | n/a | n/a | 6 | Guidance |
| awesome-pixel-art | https://github.com/Siilwyn/awesome-pixel-art | Curated list of links | CC0 | Yes | 5 | Index only |

## 3. How we build it

- **Files:** `public/pixel/landmarks.png`, `public/pixel/people.png` and `public/pixel/shops.png`, all at 1x as indexed PNGs. The sprite positions live in a small TS map (`src/components/pixel/sprites.ts`). PNGs go into the Lovable repo through the GitHub sync, following that repo's `AGENTS.md`. The code goes in through one Lovable prompt.
- **Grid:** 16px tiles. Each person is a 16x32 cell, with rows for down, up and side; left is `scaleX(-1)`. A 3-frame walk is exported as 4 frames (1-2-3-2). Scale only by whole numbers (2x on phones, 3x on desktop), use `image-rendering: pixelated`, and snap positions to whole pixels.
- **Component `<PixelScene variant>`:**
  - Landmarks and shops are static `div`s with `background-position`. That is safe to render on the server.
  - Reserve the band's height with `aspect-ratio` so nothing shifts when it loads.
  - The band gets `aria-hidden="true"`, `pointer-events: none` and `dir="ltr"`, so the Arabic UI doesn't mirror Dresden.
  - No words inside the images, only symbols, because the UI has 6 languages.
  - Walkers start only inside `useEffect`. One loop runs at about 10-12 fps and moves them between 16px grid waypoints (tram stop → bakery → Kita) with idle pauses. The effect cleanup cancels the loop and removes all listeners.
- **Motion stops when:**
  - `prefers-reduced-motion` is on. Watch it with a change listener and show static idle frames instead.
  - The user presses a visible "Pause animation" toggle. WCAG 2.2.2 requires one. Store the state in `localStorage` inside try/catch.
  - The tab is hidden (`visibilitychange`).
  - The band is off screen (IntersectionObserver).
  - `saveData` is on.
- **Where it appears:**
  - Home hero: a band below the text with the Elbe, the Augustusbrücke with a tram, the Frauenkirche, Hofkirche and Semperoper, and 3-5 walkers. Never behind text.
  - One small scene per pillar: Courses gets the music school, Events the Zwinger and the Elbe meadows, Communities the Kunsthofpassage, Library a reading bench under trees, and Health & services the pharmacy, Bürgeramt and Kita.
  - Empty states: a walker with a map at a signpost.
  - 404: a newcomer with a suitcase at an empty tram stop.
- **Performance budget:** all pixel PNGs together at most 80 KB. At most 6 walkers on desktop and 3 on phones. One loop for the whole page. Layout shift (CLS) stays at 0. Pillar scenes load lazily.
- **Credits:** a `/credits` route linked from the footer. It holds the Pixel Agents MIT notice, the optional CC0 credits (Kenney, MetroCity), the palette credit and the generator lines, all from one credits list in the repo.

## 4. Respectful characters

**Rules:**
- Every character uses the same base body and the same face (two eye pixels).
- Diversity comes from 5-6 skin ramps, hair, head coverings, age and mobility aids.
- "Newcomer" is shown by what people carry, never by ethnicity.
- No national costumes and no flags.
- Nobody is shown as helpless.
- Mix up which traits go together.
- Show the cast to 2-3 people from the target communities before launch.

| # | Look | Accessory | Carries / does |
|---|---|---|---|
| 1 | Woman, medium-brown skin, sage-green hijab | Rolling suitcase | Steps off the tram and checks a paper map |
| 2 | Man, dark skin, short afro | Stroller | Stops at the bakery |
| 3 | Grandmother, light skin, grey bun | Holds a child's hand; the child carries a Kita bag | Walks to the Kita |
| 4 | Young man, tan skin, curly hair | Wheelchair, backpack | Rolls to the Bürgeramt at walking pace |
| 5 | Man, olive skin, trimmed beard, glasses | Document folder | Waits at the Bürgeramt |
| 6 | Teen, deep-brown skin, braids | Violin case | Goes into the music school |
| 7 | Woman, light skin, short black bob | Toddler in a sling | Leaves the pharmacy with a small bag |
| 8 | Older man, warm-brown skin, bald, grey beard | White cane | Waits at the tram stop |
| 9 | Young woman, light skin, long red hair | Backpack, course book | Reads on a bench by the Elbe |
| 10 | Two parents with different skin tones | Child walking between them | Walk along the riverside |
| 11 | Woman, dark skin, everyday yellow head wrap | Bag with a pretzel | Walks home from the bakery |
| 12 | Man, medium skin, ponytail | Phone | Looks at the phone and a check mark appears (the "Call for me" answer arriving) |

## 5. Scopes, time and risks

**Demo-day mini (60-90 minutes, lowest risk to the live site):**
- Home hero band only: Frauenkirche, Hofkirche, Semperoper, Fernsehturm and an Elbe strip. **No people yet.** No newcomer sprites exist, and the rules below ban drawn children and mascots.
- Draw the landmarks in code: each sprite is an array of strings of palette keys, rendered as `<svg shape-rendering="crispEdges">`. That means no PNG, no account, no licence and no browser code. The result will look like clean flat silhouettes in 4 colours, not detailed art.
- Leave the band still. A moving tram breaks the rule that only the live dot may loop.
- Time: 30-40 minutes drawing, 15 minutes for the component and the prompt, 15-20 minutes checking (phone, desktop, Arabic RTL, reduced motion, the SSR console), and 10 minutes spare.
- Stop at 12:30. If it isn't clean by then, don't publish. The working build is the only Sunday criterion.

**Full version (Monday, about 1.5-2 person-days):**
- First, update the design rules.
- 10 landmarks with RD, including cleanup: 4-6 hours.
- 6 shops and the tram from Kenney: 2 hours.
- 12 newcomers with PixelLab and Piskel: 5-6 hours.
- The component with walkers, the pause toggle, pillar scenes, empty states and the 404 page: 3-4 hours.
- Credits page, QA and community review: 3 hours.
- Cost: about $5-6 for RD, plus a PixelLab plan (price not confirmed).

**Risks:**
- **Design rules:** Plan v3 section D4 and the Lovable Knowledge ban "drawn or AI children, mascots", animations over 300 ms and any loop except the live dot. Walkers break all three. Record a Decision note and update D4 and the Knowledge before any people ship. If we don't, the Lovable agent will work against them.
- **Licence:** the recommended stack has no share-alike. Share-alike comes in only with the ULPC backpack or basic beard, OpenPixels, [LPC] Streets or Tuxemon files. We could not read MetroCity's or any other itch.io terms ourselves, so check them in a browser. Never put "Pokemon" in a prompt, and avoid red-roofed "centre" buildings, DVB logos and Semperoper logos.
- **Readability:** motion stays in the band, with few walkers and muted colours. The site must still read as a serious service guide, not a game.
- **Live site:** touching `window` at module level causes hydration errors. Test in the Lovable preview and keep a revert ready.