# T7 0x64 joint-frame research (Claude, 2026-10-30)

**Question:** why do decoded Tekken 7 0x64 clips (every attack) crumple when applied the way 0xC8 clips are applied (BUILD-LOG 2026-10-29 18:00)?

**Why it matters:** this is the one gap between Pantera and his real King animations. It blocks every T7-based fighter for the same reason (owner order 2026-10-30: Pantera 100% from King first, then the other single-source fighters).

**Status:** partly solved. The proven facts and the rejected hypotheses are below; the full fix still needs one of the two sources in [Next](#next).

**Lane:** decode research only (claim on #866). Bake, wiring and `tools/anim/t7_*` stay in MoneyManBusch's lane.

**Tool:** `tools/anim/t7_frame_probe.py` (read-only; reads the raw files from the private GRE checkout, copies nothing in):

```
python3 tools/anim/t7_frame_probe.py channels <GRE>/teardown/tekken7-steam/tkdata/mothead/mask/kinrotsm.arc
python3 tools/anim/t7_frame_probe.py stance   <GRE>/.../json/kinmot.json <GRE>/.../mask/kinrotsm.arc
python3 tools/anim/t7_frame_probe.py hinge    <GRE>/teardown/pakchunk0/models/Character/Item/Meshes/kin/Upper/kin_bdu_1p/Meshes/SK_CH_kin_bdu_1p.glb
```

## Proven

1. **The decoder is faithful.** `tools/anim/t7_anim64.py` was checked line by line against TKMovesets2 `Utils/Animations_T_x64.cpp`:
   - base pose;
   - the shared bit-reader state, which persists across axes;
   - the double integration of sub-keyframes;
   - short vs float bone output.

   It matches. The crumple is not a decode bug; it is how the decoded values are interpreted.
2. **Nobody in the community has a 0x64 → pose path.**
   - TKMovesets2 declares `ParseAnimation0x64` but never calls it, and its extractor copies animation bytes raw.
   - Kiloutre's Blender importer and the old TekkenMovesetExtractor animation editor are 0xC8 only. Their README says "rare are the animations that are compatible".
   - BlenderTekkenDirect reads only the 0x64 base pose, behind debug prints.
3. **Where 0xC8 is used** (King's move table joined with `tools/anim/t7_clipmap.py`):
   - **King's standing stance.** `Kg_sKAM00_`, `Kg_KAM` and `Kg_sKAM_WAIT` all play `nakg_kg2kam`, rotsm clip 132, which is 0xC8 (60 frames).
   - **86 round-transition cinematics** in the common bank (`vlc_round2co_*`, 1P and 2P per opponent). Every other fighter checked (jin hei bry law pau xia nin asa bob mig yos edd) also resolves these to the common bank, so they never pair with a 0x64 copy.
   - **Every attack is 0x64:** 422 of King's 23-bone attack clips.
4. **King's own T7 skeleton is in GRE.**
   - Source: pakchunk0 `SK_CH_kin_bdu_1p.glb`, 238 joints with bind pose, head 1.87 m, ankles 0.14 m.
   - King faces +Z. Every bone points along its bind-local +X.
   - The bone names equal the applier's (`BASE`, `Spine1`, `Hip`, `R_ForeArm`, …), so the slot → bone map is Kiloutre's `applyRotationFromAnimdata`.
   - The community FBX rips in GRE `tekken7/models/*` are static meshes with no armature.
5. **Hinges are solved.** On the four hinge bones (both forearms, both shins), the only moving channel is z (descriptor 6) in both formats.
   - Anatomically (hand forward, foot back), that channel is a rotation about the **bind-local Y** axis.
   - The angle is **−z in 0x64** and **+z in 0xC8**.
   - In the stance pair (point 6) the two formats are negations of each other. Right knee: 0xC8 +1.102 vs 0x64 −1.103. Elbows: −1.79 / −1.67 vs +1.57 / +1.63.
6. **The only same-pose pair in the files:** King's 0xC8 stance frame 1 vs the median first frame of his 422 0x64 attacks.
   - Most channels have tight spreads, so attacks start from a consistent stance.
   - Printed by `stance`.
7. **Structural differences between the formats, beyond the hinges:**

   | Item | 0xC8 | 0x64 |
   |---|---|---|
   | Root | World position (`posX`/`posZ` up to ±1000–2100 mm) plus a −π/2 yaw in slot 3 | Local: forward motion in channel 2, slot 3 = 0 |
   | Slot 6 float vector | Constant (−130, 400, 0) in the round clips, (−400, 0, 0) in the stance | (−400, 0, 0), or (−270, 0, 0) in the shared `kopl_kamae` |
   | Wrists at attack start | Posed | Exactly (0, π/2, −π/2) |

## Rejected (measured, so nobody re-runs them)

- **One channel → axis mapping for all bones, on King's skeleton.**
  - Tried: 6 permutations × 8 sign patterns × 6 Euler orders × {bind·R, R·bind, R replaces bind}.
  - Best: 15% of stance frames physically plausible for 0x64, 35% for 0xC8.
  - With the hinge-derived mapping, limbs bend right, but the torso folds upside down: the 0x64 spine z ≈ −2.09 and hip z ≈ +1.83 are large constants.
- **Tekken 3 lineage.** T3's `PoseBuildMatrices` solves limbs by IK from target channels, so it is a different format. One shared idea is T3's fixed "limb basis" matrices, the same kind of per-bone constant frame that 0x64 seems to need.
- **"Native chain" model.** Offsets along each bone's X and rotation replacing the bind, with all 48 order/sign variants: none renders a plausible stance.
- **Per-bone constant frames A·R·B** (24 × 24 cube rotations × 6 orders) fitted on the stance pair.
  - Only `Spine1` gives a distinct fit: 4.4°, next best 15.7°, order XYZ.
  - The other bones land at 7°–24° with no consensus. The pair is too noisy: T7 blends into attacks, and the stance is a breathing loop.

## Next

Either of these settles it exactly, without guessing:

1. **The game's own code.**
   - Needs `TekkenGame-Win64-Shipping.exe` from the owner's Steam install (Steam → Tekken 7 → Manage → Browse local files → `TekkenGame/Binaries/Win64/`), stored privately, e.g. as a release asset in GRE.
   - In Ghidra, locate the routine TKMovesets ported (`sub_1407316F0` / `TK__Anim_64_sub_140733340`) by its byte pattern, then follow its caller's `pos_out` into the bone-matrix build.
2. **A live capture on the owner's PC.** While King plays a 0x64 attack in practice mode, read the 23 decoded values and the bone matrices the game builds from them. TKMovesets2 / BlenderTekkenDirect already know the player-struct addresses. Two or three frames per bone pin every per-bone frame exactly.

Playable now, without solving 0x64:
- King's real T7 **stance** is 0xC8, so it bakes through the 0xC8 path the crew already verified on Koenji's mannequin (BUILD-LOG 18:00 control).
- Bake `nakg_kg2kam` (kinrotsm clip 132) and Pantera stands in King's actual T7 stance in every fight.
- This session could not run that path: opening the downloaded mannequin and the community helper in Blender needs the owner's explicit OK.
