# EASTERN MIND — GENERATIVE AI CANON PASS

**Date:** 2026-10-22 · **Worker:** 40 (Eastern Mind assets + generative AI canon pass)
**Owner directive (verbatim):** "Incorporate them into the game (stages, music, art, sound). THEN run a generative AI pass over the visual assets to nudge them toward our canon — slight edits, not replacements. Keep the Osamu Sato DNA, but align with Western Heart's visual identity (the art direction bible is the guide). Audio: Tong-Nou Theme goes in as-is (it's literally our god's theme); other tracks as appropriate."

## Method

- **Tool:** the project's generative image pipeline (image-edit mode), one pass per asset.
- **Guide:** `docs/VISUAL-ART-DIRECTION-BIBLE.md` §5b (per-land visual identities), §7 (palettes), §9 template B + house suffix.
- **Prompt shape (same for all six):** "Slightly edit this image — nudge it, do not replace it. Keep the original composition, forms, and the hand-crafted Osamu Sato character exactly as they are. Only shift the palette, light and atmosphere toward [per-land direction]. Luminous darkness. Visionary art style, subtle sacred geometry, intricate detail, no text, no watermark."
- **Scope:** the six in-game stage backdrops (`game/assets/stages/eastern-mind/<stage>/pano.png`) — the visual assets players actually see. The 5,321 teardown bitmaps remain untouched in `teardown/eastern-mind/`; the pass is a documented, repeatable pipeline (prompts below) the crew can run over more assets later.
- **Outputs:** `game/assets/stages/eastern-mind/<stage>/pano-wh.png` (1160px wide, in-game). Originals kept as `pano.png` beside them; stage defs in `game/js/stages.js` point at the `pano-wh.png` versions. Before/after sheets: `game/assets/stages/eastern-mind/ai-pass/compare-<stage>.png`.

## Per-stage transformations

### 1. tree-of-life (Wood / Land of Life)
- **Before:** dark psychedelic green/purple swirl with a white glow — pure Sato.
- **Nudge:** deep jungle greens `#0B3D2E`/`#145A3C`, soul-gold `#FFD76A` light blooming from the dark, blossom-pink `#FF9EBB` petal accents, branching fractal tree-forms growing out of the swirls, drifting pollen-light motes.
- **Preserved:** the swirl composition, the central light mass, the hand-painted flow.
- **Changed:** palette pulled to the Wood identity; added fractal branches + petals + motes (bible §5b: "branching fractals, humid luminosity, pollen-light motes").

### 2. plains-of-chi-u (Fire / Land of Time)
- **Before:** near-black field with orange ember swirls.
- **Nudge:** ember red `#C1272D`, scorched umber, burning gold `#FFB340`, ash-white `#E8E0D0` highlights; faint upward-triangle flame-aureole geometry in the glow; floating cinders.
- **Preserved:** the ember-swirl composition and darkness.
- **Changed:** palette to the Fire identity; subtle triangle geometry (Sri Yantra's Shiva set, bible §5b).

### 3. octagonal-shrine (Earth / the Source)
- **Before:** dark violet concentric ripples.
- **Nudge:** temple stone tones, lantern gold `#FFC85C` light, shrine vermilion `#B03A2E` accents on still-water dark; concentric gold octagon rings + a square-with-gates (bhūpura) motif settling at the center; dust motes in lantern beams.
- **Preserved:** the ripple composition, the centered vortex.
- **Changed:** palette to the Earth identity; octagon/bhūpura geometry (bible §5b: "octagons, the bhūpura square-with-gates, perfect bilateral symmetry").

### 4. helix-palace (Metal / Land of Desire)
- **Before:** golden columned architecture, flat gold.
- **Nudge:** mirror silver `#C0C8D0` and prismatic refraction gleaming off the gold, deep violet `#2A1A4A` shadows, chrome-black depths; spiral engravings on the columns; a Metatron's-Cube inlay on the wall; refracted light beams and prism-dust.
- **Preserved:** the columned architecture, the composition, the gold.
- **Changed:** palette to the Metal identity; spiral/Metatron geometry (bible §5b: "spirals, Metatron's Cube inlays, mirror symmetry").

### 5. palace-of-dreaming (Water / Land of Dreaming)
- **Before:** blue/violet stone gate over rippling water.
- **Nudge:** deep indigo `#1B2A5A` water, ripple cyan `#4FD8E8` light, dream violet `#7A5FD0` shadows, foam-white `#EAF6FF` highlights; concentric ripple-ring geometry; bioluminescent drift in the water.
- **Preserved:** the gate, the water, the composition.
- **Changed:** palette to the Water identity; ripple-ring geometry + bioluminescence (bible §5b: "concentric ripple rings, bioluminescent drift").

### 6. phantom-marketplace (liminal / the Trader's bazaar)
- **Before:** daylight market stalls with parasols.
- **Nudge:** Trader gold `#D4A017` and lantern amber glowing out of void black `#08080C`, sigil violet `#5A2A8A` shadows; night market; faint floating watchful eyes in the dark above the stalls (Malakor thread — the Eyeball Mountains watching); violet sigil circles on the ground.
- **Preserved:** the stalls, parasols, and their arrangement — the Sato composition.
- **Changed:** day → luminous-darkness night; Malakor-thread identity (bible §2/§5b: "Malakor-thread primary zone").

## What was NOT changed

- No teardown source file was modified — all 5,321 bitmaps, 229 sounds, 22 videos, and the CD audio masters are byte-identical in `teardown/eastern-mind/`.
- No composition was redrawn; every output keeps the original's layout and forms.
- No text, watermarks, or UI elements were added to any image.
- The Tong-Nou Theme was **not** AI-touched at all — it ships as-is per the directive (format conversion WAV→MP3 only, for web delivery).

## Reproducibility

To run the pass over more assets: image-edit each source with the prompt shape above, substituting the per-land direction from bible §5b. Keep outputs beside originals (`*-wh.png`), never overwrite teardown sources, and record before/after sheets the same way.
