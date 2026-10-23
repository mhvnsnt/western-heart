# Pantera moves expansion + segment-flip audit — 2026-10-22

Follow-up to `docs/PANTERA-RIG-CORRECTION-2026-10-22.md` (PR #560), under the owner's
2026-10-22 ~01:23 CDT directives: Pantera's stance direction is right ("he's looking
like he's standing like king"), keep giving him more moves, and prove the moves in
two-fighter captures where the other fighter receives them correctly. His root theory
— the Tekken decode flipped body segments, the corruption creeping from character to
character — was hunted segment-by-segment in the Pantera path.

## More moves: the King row pack now covers every referenced row

Pantera's moveset (`game/assets/movesets/pantera.json`, 873 move entries) references
226 distinct Tekken 3 King rows; the shipped bank pack
(`game/assets/anim/t3/king_on_pantera_leoman/rows.pack.json`) held only 176 rows, so
**82 of his move entries (67 strikes, 10 throws, 5 specials) had no animation** and
fell back to the generic light/medium/heavy clips — the state the row baker's own
header describes ("Until now every attack played one of three generic clips").

Fix, with the repo's own pipeline (`tools/anim/t3_row_bake.py` →
`lab/tools/t3_motion_bake.py`, bit-exact disc decode):

1. **Reproducibility control first.** Inputs verified byte-identical to the shipped
   pack's recorded SHA-256 (king95.kmd, divmot03_king.bin, SLUS_004.02,
   pantera_leoman.glb). Rows 44 and 230 re-baked as controls: **max delta 0** on every
   quantized value vs the shipped pack.
2. **Baked the 79 missing referenced rows** (all 79 are Pantera-referenced):
   50, 57, 69, 99, 103, 107–111, 113–116, 119, 122, 125, 126, 129, 131–134, 137–141,
   143–146, 211, 213, 214, 223, 228, 232–234, 238, 239, 243, 249, 261, 262, 266–269,
   273–275, 290–294, 297, 298, 339, 343, 347, 351, 355, 359, 363, 367, 371, 375, 379,
   431, 564, 584, 586, 604, 606, 608, 632. **79 baked, 0 missing.**
3. **Merged additively**: the 176 shipped rows are byte-identical in the new pack
   (verified entry-by-entry); the pack grows 176 → **255 rows** (1.55 MB → 2.15 MB),
   which is every King row any WH moveset references (255 distinct globally).

Every Pantera move entry that names a `t3_row` now has its real decoded clip.

## Segment-flip audit (the owner's quarry)

Method: fit ONE global frame transform (Kabsch, rotation/reflection) between the
canonical bank skeleton's bind segment directions and each target rig's, then compare
per-segment world directions through it, source FK vs the game's retarget, across 12
real clips (neutral, strikes, throws, specials — rows 0, 35, 39, 44, 72, 83, 127,
202, 230, 279, 284, 317). Leo man (authoring rig) is the control.

| rig | global bind fit | bind outliers >20° | segment flips >90° | suspects 45–90° | worst posed residual |
|---|---|---|---|---|---|
| Leo man (control) | det +1, residual 0.0° | none | none | none | 0.0° |
| A4 Leopard King (fixed, #560) | det +1, residual max 12.8° | none | **none** | **none** | Head 26.8° (one fast frame), thighs ~17°, spine 15°, all else ≤6.7° |
| A1 in-game model (fixed, #560) | det +1, residual max 12.8° | none | **none** | **none** | same (shared template) |

Verdict: **no segment-level flip exists in the Pantera path** — not in the King bank
decode (bank rotations equal the Leo man GLB's native channels at 0.00°, and the row
bake reproduces bit-exactly), not in the template bind (one global frame difference,
a pure rotation — the template was authored turned, which the retarget's per-bone
conversion handles), and not in clip evaluation after #560 (the rejected #493 bake's
58–92° scramble is gone; every limb segment evaluates at 0.00° against the retarget).
The residuals that remain are the two models' genuine bind-shape differences, the
same class documented in the #560 correction. The flip pattern the owner mapped
tonight lives on Star's model (sibling lane; cf. PR #561) and in the discarded #493
bake — not in Pantera's shipped files or his runtime path.

**Note for the Godot slice lane** (`godot/scripts/bank_clip_loader.gd`): the shared
King decode is clean and bit-reproducible, so the solver's per-rig conversions are
compensating genuine per-rig template frame/bind differences — not an upstream
decode error. The web build's fixed files + `retargetT3Clips` remain the reference
for what the bank data itself says; per-rig conversion belongs at the rig layer in
both builds.

## Two-fighter interaction proof

Staged with the game's own runtime code (`game/js/t3anims.js` `loadT3Clips` +
`retargetT3Clips`, three.js, headless Chromium) — the fixed Leopard King model
performing three of the newly-baked moves on Diablo (house49 model), who receives
them with the T3 hit-reaction clip retargeted by the same code. Contact frames were
chosen from the clips' own data (max-reach frames), the receiver placed so the
striking limb meets his chest/head, both fighters feet-planted (attacker grounded
by his lowest foot joint; measured contact gaps: throw — hand coincides with the
receiver's chest in x/z at grapple range; uppercut — fist coincides in x/z, landing
at face height on the shorter receiver; kick — boot coincides with his head in x/z).

- `docs/tpose-refs/pantera/fight-proof-20261022.png` — the three captures, labeled:
  KING b+2 uppercut (row 99, new), KING 1+3 throw grab (row 273, new), KING row 103
  turning high kick (new). Viewed by the agent before this PR was opened.

Staging honesty note: these are contact-frame stills from the game's own animation
runtime, not live gameplay frames — they prove the clips play on Pantera, reach the
opponent, and that the opponent's reaction clip plays facing him at the contact
point. Full in-game integration (hit detection, move startup/active windows from
the moveset's frame data) is the game's existing fighter.js path, which consumes
exactly these `row:<n>` clips.
