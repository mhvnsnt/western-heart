# T7 0x64 joint-frame research (Claude, 2026-10-30)

**Question:** why do decoded Tekken 7 0x64 clips (every attack) crumple when applied the way 0xC8 clips are applied (BUILD-LOG 2026-10-29 18:00)?

**Why it matters:** this is the one gap between Pantera and his real King animations. It blocks every T7-based fighter for the same reason (owner order 2026-10-30: Pantera 100% from King first, then the other single-source fighters).

**Status:** the rotation encoding is SOLVED from the exe (next section); validation and the bake are next. Earlier status: partly solved. The proven facts and the rejected hypotheses are below; the full fix still needs one of the two sources in [Next](#next).

**Lane:** decode research only (claim on #866). Bake, wiring and `tools/anim/t7_*` stay in MoneyManBusch's lane.

**Tool:** `tools/anim/t7_frame_probe.py` (read-only; reads the raw files from the private GRE checkout, copies nothing in):

```
python3 tools/anim/t7_frame_probe.py channels <GRE>/teardown/tekken7-steam/tkdata/mothead/mask/kinrotsm.arc
python3 tools/anim/t7_frame_probe.py stance   <GRE>/.../json/kinmot.json <GRE>/.../mask/kinrotsm.arc
python3 tools/anim/t7_frame_probe.py hinge    <GRE>/teardown/pakchunk0/models/Character/Item/Meshes/kin/Upper/kin_bdu_1p/Meshes/SK_CH_kin_bdu_1p.glb
```

## SOLVED IN THE EXE (2026-11-01): 0x64 rotation channels are AXIS-ANGLE, not Euler

Source: `TekkenGame-Win64-Shipping.exe` from the owner's Steam library (private GRE release
`t7-shipping-exe-20261031`, 58,439,680 B, sha256 `7f2b68727023ce9f4554b47f5442dad9dfb38c8a9b778f2aa758469e2c2d60ed`).
Static disassembly only (capstone); the binary is never run and never leaves private storage.

- **The sampler** (RVA `0x73ea30`, image base `0x140000000`) is the only code in the exe that tests a clip header
  against both `0x64` and `0xC8` (three functions in 189,693 compare against both; all sit in `0x7307xx-0x73f5xx`):
  - header byte must be 0x64 or 0xC8 (else an assert write to address 0);
  - 0xC8: frame count = u32 at +4, evaluated by `0x729b10`;
  - 0x64: bone count n = u16 at +2, n u16 descriptors at +4, frame count = the u16 after them; n < 256;
  - a bone is a ROTATION bone when its descriptor is 4..7 (`(d - 4) <= 3`); others are positions;
  - `modff` splits the time; `0x7418e0` decodes one frame into 3 floats per bone (X, Y, Z);
    a fraction >= 1e-5 decodes the next frame too and blends.
- **Per rotation bone** (single-frame path `0x73ec4e-0x73ed5c`, constants read from .rdata: 1.0, sign mask, 0.5):
  ```
  axis = R_y(Y) * R_x(X) * (0, 0, 1) = (cos X * sin Y, -sin X, cos X * cos Y)
  q    = (axis * sin(Z / 2), cos(Z / 2))          # (x, y, z, w)
  ```
  X and Y are the elevation and azimuth of the rotation AXIS; Z is the ANGLE about it. Only Z is halved.
- **Position bones** are written as (x, y, z, 1.0).

This is why every Euler order failed (see Rejected) and why the four hinge bones move only in Z
(fixed axis, varying angle) with opposite signs between the formats (the axis can point either way).
**Verified by running the game's own sampler** (`tools/anim/exe_re/emulate_sampler.py`: Unicorn CPU emulation of
RVA 0x73ea30 with the CRT math imports stubbed; nothing of the game runs as a program):
- **0xC8 rotations:** `q = q_X(-X) * q_Y(-Y) * q_Z(-Z)` (Hamilton, x y z w); fits random probes to 7.4e-8.
- **0x64 formula above:** matches the sampler exactly on frames 0 and 2+. The community decoder's frame 1 differs from
  the game's (its first sub-step special case); `tools/anim/t7_anim64_to_c8.py` therefore samples with the game itself.
- **Same bone space:** King's 0xC8 stance vs the first frame of 120 of his 0x64 attacks, per bone through the game's
  sampler: forearms 2-4 deg, neck 6, feet 5, knees 4-12, all within the attacks' own start spread (wrists differ:
  the attacks start with neutral wrists, see point 7 below).
- **Round trip exact:** 0x64 clip -> `t7_anim64_to_c8.py` 0xC8 values -> the game's 0xC8 sampler gives the game's 0x64
  quaternions back to 3.6e-7 on 8 of King's clips (`--check`). Every 0x64 attack can now take the proven 0xC8 bake path.

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
- **Per-bone constant frames A·R·B fitted on many attack first frames** (2026-10-31).
  - Tried: King's 0xC8 stance (the exact local rotations Kiloutre's applier writes on Koenji's mannequin) against the first frame of every damaging King attack whose clip is 0x64. Attacks start from the stance, so this gives far more samples than the stance pair alone.
  - Search space: 6 orders × 8 sign patterns × 24 × 24 cube rotations per bone.
  - Result: the best median error per bone is 10.3°–66.9°, and 0 of 18 bones come in under 10°.
    - Worst: right thigh 66.9°, left foot 55.9°, neck 50.4°.
    - Best: right hand 10.3°, left forearm 13.4°.
  - Every bone's runner-up ties its best fit, so no candidate wins.
  - Not decisive: attack first frames are already blended away from the stance.
  - Re-run: `tools/anim/t7_bl_basis.py` (Blender side) then `tools/anim/t7_f11_fit.py`.
- **Same-motion pairs across the two formats.** Across 30 characters' clip tables, no animation name is stored once as 0xC8 and once as 0x64. There is no same-motion pair that would pin the frame exactly.

## Next

Either of the first two settles it exactly, without guessing. The third might:

1. **The game's own code.**
   - Needs `TekkenGame-Win64-Shipping.exe` from the owner's Steam install (Steam → Tekken 7 → Manage → Browse local files → `TekkenGame/Binaries/Win64/`), stored privately, e.g. as a release asset in GRE.
   - In Ghidra, locate the routine TKMovesets ported (`sub_1407316F0` / `TK__Anim_64_sub_140733340`) by its byte pattern, then follow its caller's `pos_out` into the bone-matrix build.
2. **A live capture on the owner's PC.** While King plays a 0x64 attack in practice mode, read the 23 decoded values and the bone matrices the game builds from them. TKMovesets2 / BlenderTekkenDirect already know the player-struct addresses. Two or three frames per bone pin every per-bone frame exactly.
3. **Same-motion pairs from TTT2 (untested; needs the TTT2 lane's data).** Many of King's T7 attacks reuse Tag Tournament 2 motions. If TTT2 stores any of those motions as raw 0xC8 frames, each one pairs with its T7 0x64 copy across a full attack's range of poses, not just the near-constant stance, and the per-bone frames could be fitted exactly.
   - The private research clone has only the TTT2 disc readers so far (`tekken-tag-tournament-2/tools/`), with no extracted motion data. Tekken 6 (PSP) is still encrypted.

King's moves for Pantera, checked 2026-10-31 with every move in `kinmot.json` resolved to its bank and format (`tools/anim/t7_clip_formats.py`):
- All 552 damaging moves are 0x64 (467 rotsm, 71 common, 14 inline).
- The only 0xC8 clips are the stance (rotsm 132) and the 108 round-transition cinematics (86 common, 22 inline).
- Every other clip (walks, dashes, sidesteps, throws, reactions, attacks) is 0x64, so they all wait on this fix. The stance is everything the 0xC8 path can give Pantera.

Playable now, without solving 0x64:
- King's real T7 **stance** is 0xC8, so it bakes through the 0xC8 path the crew already verified on Koenji's mannequin (BUILD-LOG 18:00 control).
- Bake `nakg_kg2kam` (kinrotsm clip 132) and Pantera stands in King's actual T7 stance in every fight.
- ~~This session could not run that path: opening the downloaded mannequin and the community helper in Blender needs the owner's explicit OK.~~ Done; see Shipped.

## Shipped: King's real T7 stance on Pantera (2026-10-30, owner: "I approve u to run the mannequin")

- **Tool:** `tools/anim/t7_c8_stance_bake.py` (with `tools/anim/t7_bl_pose.py`, the Blender side). It runs three steps:
  1. decodes kinrotsm clip 132 (`nakg_kg2kam`, 0xC8, 60 frames);
  2. poses Koenji's mannequin with Kiloutre's `applyRotationFromAnimdata` (BlenderTekkenDirect @ `bebb3d8`);
  3. converts to the game's bank format.
- **Self-check:** FK of the written skeleton reproduces every posed T7 joint, max error 0.000000 m. Re-running the tool reproduces the shipped files bit for bit.
- **Data:** `game/assets/anim/t7/king/skeleton.json` (T7 rest pose, `wh-anim-skel/1`) and `game/assets/anim/t7/king/stance.json` (`wh-anim/1`, with provenance).
- **Wiring:** `game/js/t3anims.js`
  - `T7_STANCES` = Pantera only, loaded with the King bank.
  - `applyT7Stance()` replaces the bank's T3 slot-3 `stance` in the fight (`game/js/fighter.js` `_bindT3`) and in the select preview (`game/js/select-screen.js`).
  - Every other action and every move row is unchanged.
- **In the game** (headless Chromium, `?quick=pantera,demonio,shrine`):
  - Pantera idles in `t7_pantera_stance@pantera-leoman` (weight 1 while idle), hips 0.91–0.96 m, head 1.51–1.59 m.
  - Demonio keeps `t3_jin_stance`.
  - The live build before this change showed `t3_king_stance`.
- **Test:** `test/t7-stance.test.mjs`.
  - Format and provenance.
  - Every frame is a standing guard: feet on the floor, upright, left foot forward, both hands up in front.
  - Loop seam < 3 cm.
  - Wiring is Pantera-only.

## Shipped: real T7 stances for 12 more fighters (2026-10-31)

Same tool, same path. Each fighter gets its CANON base's own T7 stance clip (the clip the base's `<code>_sKAM00_` move plays) wherever that clip is 0xC8 and the fighter has a bound bank. Every bake's FK self-check is 0.000000 m, and the stances are distinct (frame-1 joints differ by 0.17–0.43 m between characters).

| Fighter(s) | T7 base | Clip | Frames |
|---|---|---|---:|
| Diablo | Heihachi | `nahe_he2kam` heirotsm 126 | 90 |
| Skull, Retsu | Bryan | `nabx_bx2kam` bryrotsm 126 | 80 |
| Burger | Bob | `ikfa_kamae` bobrotsm 128 | 386 |
| Saku Ra, Sha | Xiaoyu | `kmfu_kamae` xiarotsm 126 | 110 |
| Phantom | Yoshimitsu | `mbym_kamae` yosrotsm 117 | 111 |
| Gyou, Tobi | Hwoarang | `kmhw_kamae_L` hworotsm 126 | 50 |
| Gashadokuro | Kuma | `nakm_kam` kumrotsm 201 | 120 |
| Aotsuki | Panda | `nakm_kam` panrotsm 201 | 120 |
| Nightwolf | Julia | `najl_jl2kam` julmot.bin inline 119 | 80 |
| Purple Rain | Lee | `kole_kamae` leerotsm 126 | 53 |
| Chordz | Lars | `amla_kamae` larrotsm 123 | 100 |
| Negativo | Negan | `nass_kamae` nsamot.bin inline 131 | 1100 |

Not given a stance:
- **Owner decisions:** Zen is NOT Heihachi; Cyborg X and Zui keep their stances; `jin_soul` is on the decision list.
- **Only borrow the bank:** Menajerii (Roger Jr., on the kuma bank) and Silvertongue (Lili, on the xiaoyu bank).

Still waiting:
- **0x64 stances** need the joint frame: Jin (Rin, Demonio), Law (Buffalo Bill), Paul, Nina (Awa Pop), Alisa, Miguel (Bruno), Eddy (Kai, King Tyrant), Asuka (Kinpo), Katarina (Michiko), Akuma (Dio), Jack-7 (Sam-UR-A1), Raven (Pond), Anna (Torch), Lei (Rave), Lili, Zafina (Mariposa), Lucky Chloe (Ryusan).
- ~~**No bank:** Purple Rain (Lee), Chordz (Lars) and Negativo (Negan)~~. Corrected 2026-10-31: they do have a bound bank. Their moveset `t3_source` binds a proxy bank (jin / jin / bryan), so they shared Demonio's / Skull's stance. Their own bases' stances are 0xC8 and now ship in the table above. Negan's FK self-check is 0.000001 m over 1,100 frames, so the test tolerance is 10 µm.
