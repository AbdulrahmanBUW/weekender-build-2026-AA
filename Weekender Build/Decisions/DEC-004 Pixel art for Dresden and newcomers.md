---
type: decision
date: 2026-09-27
status: accepted
deciders: [abdul]
---
# Decision: Pixel art for Dresden and the newcomers

## Context
On Sunday morning Abdul asked for Pokemon-like pixel art on the site: Dresden landmarks (Frauenkirche and others), shops and places, and pixel characters from different migration backgrounds who walk around the website as newcomers to Dresden. Our design rules said the opposite. [[Frontend and UX Plan v3 (merged)]] section D4 and the Lovable Knowledge ban drawn people and mascots, cap animations at 300 ms, and allow only the live dot to loop.
Research with verified licences is in [[Pixel Art Plan]]. No openly licensed Dresden pixel art exists. The best free base for people is the Pixel Agents sprites (MIT, based on MetroCity, which is CC0).

## Options
1. **Full version on Monday.** Update the rules first, then build with PixelLab and Retro Diffusion. This was the research recommendation.
2. **A static skyline band today.** No people, no motion.
3. **The full version today.** A skyline band with a tram, pillar scenes, and 12 walking newcomers made from the Pixel Agents base sprites. All art is drawn in code, with no new accounts or downloads.

## Decision (accepted 27.09 by Abdul)
**Option 3, built today.** Abdul chose it in chat ("Full version but do it now today").
Guard rails:
- Build and test locally first, with no new npm packages.
- Show it only in bands, never behind text.
- Add a visible pause toggle, stop all motion under reduced motion, and switch the band to left-to-right in Arabic.
- Put no words in the images and use no Nintendo or Pokemon assets.
- Credits go on a `/credits` page.
- Publish only if it is clean by 12:30. Otherwise it waits without going live.

## Consequences
- The design rules change for pixel art only:
  - Walkers and the tram may loop inside the pixel band.
  - Everything else keeps the old motion rules.
  - Plan v3 D4, the Lovable Knowledge and `AGENTS.md` in the Lovable repo now carry an exception pointing to this decision.
- The characters must stay respectful:
  - Everyone gets the same body and face style.
  - Diversity comes from skin tone, hair, headwear, age and mobility aids.
  - Being new is shown by what people carry.
  - No costumes and no flags.
  - Show the cast to 2–3 people from the target communities before a wider launch. This is on the [[Monday-Morning Plan]].
- Licences:
  - The Pixel Agents MIT notice goes on `/credits`.
  - The Dresden scenes are our own art.
  - The palette is based on AAP-64.
- The build brief is `docs/pixel/BRIEF.md`. The generator scripts are `scripts/pixel/*.py` in the team repo, and the images go in `public/pixel/` in the Lovable repo.
