# Rin portrait proof — D_SUMIE b036 staging (2026-11-22)

## What changed
`game/assets/portraits/rin.png` was a stretched face image of Demonio in a
transformed version — NOT Ren. It is replaced with the real Rin bitmap from
the Eastern Mind prologue.

## Source
`teardown/eastern-mind/prologue-ending/bitmaps/D_SUMIE/D_SUMIE_b036_254x244.png`
— 9,096 bytes, 254x244, 16-color palette. Standing stick figure, arms out,
round head, downturned mouth + angled brows (perpetually frowning).

Proven Rin by three lines (full record in the bitmap-sequence lane report):
1. The narration in the SAME bitmap group names him ("One morning, Rin
   discovered the absence of a soul." / Tong-Nou devours souls / "Rin
   decides to head for Tong-Nou to regain the missing soul…").
2. The only stick figure in the entire 5,321-bitmap holdings.
3. Palette fill index 245 (238,238,238) vs background index 0 (255,255,255)
   — white chalk on black when composited.
Also proven: Rin = LIN in-game (SHARED_t007 lists the 9 lives as
Lin,Byou,Toh,Sha,Kai,Jin,Lets,Zen,Gyou). The reincarnation card Card_LIN
(SHARED_b001) and Rin's black-square portrait slot (SHARED_b053 — he has no
portrait, because he has no body) corroborate the identification.

## Treatment
- 320x320 RGBA, transparent background — the house portrait format
  (tou.png / zen.png are 320x320 RGBA). The select card's own dark purple
  radial gradient shows through, so the white chalk figure reads.
- Transparency keyed on PALETTE INDEX 0 (background), not on color value.
  The figure's own fill (index 245) and dark outline/shading indices stay
  opaque at palette color. No pixels recolored.
- Nearest-neighbor upscale to fit 304 px (304x292), centered — chalk line
  stays crisp, no smoothing.

## Proof in this folder
- `proof-card-320.png` — new portrait composited over a simulation of the
  select card's dark purple gradient. White chalk figure, arms out, frown
  visible.
- `proof-card-96.png` — same at phone card size. Still reads clearly.

## Honest limits
- NO drawn chest-hole exists in any figure frame (pixel-verified solid
  torso in standing and horizontal frames). The owner's "empty hole in his
  chest" is the story's hole — where the soul was taken — not a drawn circle
  in these bitmaps. No hole was drawn in this portrait.
- The on-black reading is a reconstruction: the source PNG carries no tRNS
  chunk; the matte index was not verified from the DXR. It follows the
  standard Director transparency reading, palette-consistent.
- The manifest entry for rin still records a demonio-a1 capture as the
  portrait source; it is now stale and should note the bitmap provenance
  (follow-up, outside this PR's portrait-only scope).
