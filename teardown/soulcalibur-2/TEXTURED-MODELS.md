# Soulcalibur II (Xbox) — Textured Fighter Models (Phase 13, JOB 2)

All 22 skinned fighter GLBs from PR #406 (`models-skinned/`) now exist
in textured form in `models-textured/`, with the fighter's own VXT
textures **embedded** (owner law 2026-10-21: textures baked in — proof
= image count in the GLB + a textured render).

## Method

- Source bundles: the 22 P1 v982 bundles, range-fetched from the
  western-heart release ISO asset (asset 637640671) at
  `ISO 0x3C27D000 + 0x800 + entry offset`, sizes from the v982 entry
  table. Header-verified after fetch (the idx47 fetch is byte-identical
  to the previously verified local copy, sha256
  `03095dc7213d7cb6e857f5786b36b469ec27443c0f59421de23b9e140be08a7b`).
  The banned stale `~/workspace/scii-work/p2/v982_idx47.bin` was NOT used.
- Mapping (pointer-exact, see `VXT-FORMAT.md`): GLB mesh name
  `g{group}p{idx}` → VMX part record → part+0x0c rec80 material →
  material+0x08 primary VXT texture record. Every pointer validated by
  exact division into its array; failures would be reported, none
  occurred. Confidence: HIGH for every assigned mesh.
- Textures decoded from the VMX's own VXT section with
  `tools/vxt_decode.py` (DXT1/3/5 linear; P8 unswizzled + palette) and
  embedded as PNG at mip level 0.
- Tool: `tools/apply_textures.py`. It copies the source GLB's geometry
  and skinning through untouched and **asserts** that summed POSITION /
  index / JOINTS_0 accessor counts and the skin joint count are
  identical before and after — the assertion ran on all 22 files.
- Alpha mode: `alphaMode: MASK` (cutoff 0.5) is set ONLY when a
  texture's alpha has genuine cutout populations (≥1% fully transparent
  AND ≥5% fully opaque pixels). Texture sets whose alpha never reaches
  255 carry a specular-style mask in alpha instead of opacity
  (idx944 Spawn: all 12 used textures amax ≤ 179, RGB dark — under a
  blanket MASK his suit rendered washed-out translucent white; with
  the rule he renders opaque black, proof below). This is a rendering
  decision recorded here, not a format claim.

## Results — per fighter

| v982 entry | Fighter (source ID) | Embedded images | Meshes textured | Skin joints | Untextured meshes (reason) |
|---|---|---|---|---|---|
| 47 | Mitsurugi | 23 | 39/39 | 147 | — |
| 86 | Seong Mi-na | 32 | 55/55 | 164 | — |
| 125 | Taki | 32 | 41/41 | 155 | — |
| 164 | Maxi | 22 | 32/32 | 170 | — |
| 203 | Voldo | 18 | 34/34 | 106 | — |
| 242 | Sophitia | 29 | 33/33 | 181 | — |
| 281 | Ivy | 27 | 46/46 | 147 | — |
| 320 | Kilik | 29 | 30/30 | 165 | — |
| 359 | Xianghua | 20 | 22/22 | 161 | — |
| 398 | Yoshimitsu | 29 | 83/83 | 58 | — |
| 437 | Nightmare | 28 | 56/56 | 105 | — |
| 476 | Astaroth | 21 | 25/25 | 96 | — |
| 515 | Cervantes | 35 | 49/49 | 159 | — |
| 554 | Raphael | 36 | 39/39 | 168 | — |
| 593 | Talim | 32 | 36/36 | 168 | — |
| 632 | Cassandra | 35 | 40/40 | 187 | — |
| 671 | Necrid | 10 | 17/17 | 101 | — |
| 710 | Yun-seong | 29 | 33/33 | 157 | — |
| 827 | UNIDENTIFIED (slot 1e) | 23 | 28/28 | 107 | — |
| 866 | UNIDENTIFIED (slot 1f) | 20 | 24/24 | 87 | — |
| 905 | UNIDENTIFIED (slot 20) | 17 | 49/54 | 74 | g0p11 (material is color-only (texture ptr 0)); g0p17_r (material is color-only (texture ptr 0)); g0p19_r (material is color-only (texture ptr 0)); g0p67_r (material is color-only (texture ptr 0)); g0p69_r (material is color-only (texture ptr 0)) |
| 944 | Spawn | 12 | 75/75 | 102 | — |
Totals: 22 GLBs, 559 embedded texture images, 886/891 meshes textured.
The only untextured meshes in the whole set are idx905's five parts
above: their source materials are color-only (VXT texture pointer 0 in
the rec80 record) — that is the game's own data, so no texture was
invented for them. There is no unproven list: every mesh either has a
pointer-proven texture or a source color-only material.

## Original-comparison (owner law: body integrity, not pose)

Side-by-side renders (LEFT = PR #406 untextured original, RIGHT =
phase-13 textured), same bind pose, same framing (geometry untouched),
viewed by the lane:

- `phase13-proof/idx47-mitsurugi-textured-compare.png` — Mitsurugi:
  face/beard/topknot, lamellar armor, skin arms, white hakama with
  black flame embroidery, sandals. Silhouette identical to original.
- `phase13-proof/idx125-taki-textured-compare.png` — Taki: red
  bodysuit, black hair, shoulder armor, arm/leg guards, thigh tattoo.
- `phase13-proof/idx632-cassandra-textured-compare.png` — Cassandra:
  blonde bob, blue/white top with pink gem, brown tights, white boots
  (P8 textures render correctly in the full pipeline).
- `phase13-proof/idx944-spawn-textured-compare-v2.png` — Spawn: black
  suit, green eyes, red arm guards/pouch/boot, chains, skull pauldrons.
  (v1 of this render, under the blanket-MASK rule, showed the alpha
  defect described above; v2 is the shipped rule.)

All four comparisons show body integrity (proportions, bone placement,
weights) unchanged from the originals — only surface color was added.

**Phase-16 note (2026-10-22):** the totals above describe the
pre-fix set. After the full re-decode with the fixed reader
(phase 16, `PHASE16-STATE.md`), the base textured set is 22 GLBs,
1,081 parts, 601 embedded images; the recovered trailer-span
parts brought their own pointer-proven textures with them (the
untextured remainder is the same source color-only class —
e.g. idx905 ships 74/79 meshes textured, idx515 60/62, for the
same pointer-0 reason recorded above).
