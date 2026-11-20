# T7 0xC8 control test + King stance bake for Pantera — 2026-10-30

## Verdict

**The 0xC8 (format-200) path is verified end to end.** King's real Tekken 7
guard stance (`nakg_kg2kam`) was applied to Koenji's T7 mannequin through
Kiloutre's own importer and lands as a physically plausible, ground-planted,
seamlessly looping kamae. The same pose was then baked onto Pantera's rig as
a playable-format asset:

- `game/assets/anim/t7/king_on_pantera_leoman/t7_stance.json` (wh-anim/1, 30 frames @ 30 fps)
- Tools: `tools/anim/t7_c8_control_test.py`, `tools/anim/t7_c8_pantera_stance_bake.py`
- Proof renders: `docs/anim/proof/t7-c8-mannequin-stance-f58.png`,
  `docs/anim/proof/t7-pantera-stance-f58.png` (viewed by the lane before landing)

This is a **stance-only** result from the verified 0xC8 path. It is **not** a
format-100 (0x64) result; the 0x64 rotation-convention solve is a separate
lane and is untouched by this work.

## The clip

- Source: owner's Steam Tekken 7, `kinrotsm.arc` §0 (GRE
  `teardown/tekken7-steam/tkdata/mothead/mask/`), sha256
  `67c6938dcb16575acc42423c3637cc7dd86b13bd980a2eeaa301566b3ec9c992`.
- `nakg_kg2kam` = anim_id `0x4084`, MOTA table entry 132 (byte-identical
  aliases at entries 206, 210, 928, 1119, 1120 — the six motbin moves
  Story_CmnPostBtlRt_7CS, Kg_sKAM00_, sWALK_00BMv, Kg_sKAM_WAIT, Kg_Direct,
  Kg_KAM all reference this one clip).
- Format-200: 60 frames, 23 tracks, 16,660 B, clip sha256
  `1e0c6b34ca537ee459edfd2d8313d47b09910a3be3c8767b32d6e7a99bb9aeb0`.
  Header track-field sequence `(11, 11, 5, 7, 7, 7, 11, 7, 7, 7, 7, 6, 7, 7,
  7, 6, 7, 7, 6, 7, 7, 6, 7)` matches Kiloutre's expected descriptor masks
  exactly — the plugin was built against this exact clip family.
- The plugin consumes the clip little-endian (its in-memory form). The prep
  step re-serializes the proven BE MOTA fields to LE (`<2B H 24I` header +
  `<69f` frames); the plugin's own parser then reads signature byte 0xC8,
  23 vectors, 60 frames. Lossless field-for-field transform.

## Safety / inspection (why this ran here)

The helper code was **read before it ran**:

- Kiloutre/BlenderTekkenAnimationImporter (cloned 2026-10-30): pure animation
  math + `bpy` pose writes. No network, no subprocess, no eval/exec; its only
  file read is the user-supplied clip path. `Animation0xC8` parses the header
  + frames; `TekkenAnimHelper.applyRotationFromAnimdata` writes per-bone
  Euler rotations + the root offset onto the mannequin's named bones.
- Koenji's mannequin (MEGA folder linked from that repo's README):
  `TekkenMannequin_no_ik.blend` sha256
  `ce8171083d0c6da57ec2a938a1fdaf2f2b38a98e6fb31c2b6e71a4d38c1b2321`
  (ik variant `51dc22339ab2751be5759231e2f21f8f3d3e136dadc4e5b31a6c064f267ca308`).
  Opened **without autoexec**: probe found zero embedded text blocks, zero
  drivers, no pre-existing action. The mannequin itself is an untextured clay
  figure by design (its materials carry no texture maps) — the proof render
  shows it exactly as authored.

## Control-test numbers (mannequin, all 60 frames read back)

- Hip height 1.062–1.077 m in stance (rest 1.15), head top ≈ 1.77–1.79 m.
- Mesh ground contact: posed mesh min Z between **−0.024 and −0.004 m**
  across sampled frames (rest pose min Z −0.003) — feet at the ground plane,
  neither floating nor sunk. Toe-ball markers (ATH_*_Toe_Btm) at Z
  0.001–0.044; heel markers slightly raised — King stands on the balls of
  his feet, as his kamae does.
- Knees bend **forward**: knee joints sit 0.12 m (L) / 0.19 m (R) forward of
  the hip–ankle line at frame 60. No fold, no backward knee.
- Bladed guard signature: right foot +0.21 m and right hand +0.41 m forward
  of the left (facing axis), hands up at 1.41–1.43 m.
- Frame 1 ≈ frame 60 joint-for-joint (e.g. Hip (0.004, 0.007, 1.077) vs
  (0.000, 0.000, 1.073)): the clip is a seamless stance loop, with a real
  settle dip mid-loop (hip 0.920 at frame 15) and breathing-scale motion
  thereafter (avg joint motion/frame halves from 0.340 to 0.164).

## Bake method + verification (Pantera)

- Target rig: `lab/game/assets/pantera_leoman_t3real.glb`, sha256
  `cd1989165650a802e9151eba7a187d7c897d18cef6d15ec0173c06fe59ae9ecb` (the
  golden reference). All 24 GLB node rotations are identity, matching the
  wh-anim/1 convention (rest = joint positions only).
- Transfer = world-orientation matching per mapped bone
  (`Q_wh = Q_mq_pose · Q_mq_rest⁻¹ · Q_wh_rest`), Root translation from the
  mannequin Hip trajectory scaled by rig height (S = 1.702/1.882 = 0.9043),
  plus per-frame grounding pinning the lower foot joint to its rest height
  (0.0925 m, held exact in all 30 stored frames).
- **Bone-map correction found by the numbers:** the mannequin's `Spine1`
  joint sits at pelvis-top (head at Hip height, 1.15) — it maps to WH
  **Spine**, not Chest. First pass mapped it to Chest and every up-chain
  joint showed a constant ≈0.35 m position offset; with the correction the
  solve is exact (below). WH Chest and ToeBases have no T7 body channel and
  stay identity.
- **Verification:** rest-pose export deviation **0.0 rad** (conversion chain
  exact); rotation solve max error **0.069°** across all 30 frames × 19
  mapped bones (evaluated WH world orientations vs the mannequin's).
  Remaining joint-position deltas vs the mannequin (RMS 0.11 m) are rest-
  geometry differences between the two skeletons (segment offsets), not
  rotation error — rotations define the pose; positions follow each rig's
  own proportions.
- WH stance signature (frame 30 stored): right foot +0.257 and right hand
  +0.336 forward of the left (mannequin: +0.213 / +0.405), hands at
  1.30–1.33 m — King's bladed kamae, on Pantera's body.
- `root_t` is the Root bone's world position in glTF meters; rest value
  [0, 0.9805, 0] matches this bank's `skeleton.json` `root_rest_y` exactly.

### Gotchas recorded for the next lane

1. The Pantera GLB ships its 42 T3 clips as **NLA tracks + an active
   action**, and Blender's glTF importer leaves a pose baked into the pose-
   bone basis values. Clear `animation_data` AND reset every pose bone
   (location/rotation/scale) before manual posing, or the NLA stack silently
   overrides the transfer (first bake attempt rendered the NLA idle blend
   instead of the stance — caught by the identity-quaternion tell).
2. This VM's Blender has no `libEGL.so.1`: EEVEE aborts; use **Cycles CPU**
   under `xvfb-run -a env -u PYTHONPATH` for proof renders.
3. Blender bone frames ≠ glTF joint frames: export local quaternions via
   `Rg = C · Rb · Rb_rest⁻¹ · C⁻¹` (C = Blender→glTF axis conversion) or the
   rest pose will not export as identity.

## Reproduction

```bash
# inputs: GRE kinrotsm.arc; Koenji mannequin (MEGA link in Kiloutre's README);
#         Kiloutre/BlenderTekkenAnimationImporter clone; Pantera GLB (WH lab/)
python3 tools/anim/t7_c8_pantera_stance_bake.py --prep --arc kinrotsm.arc --out nakg_kg2kam_0xC8.bin
T7_MANNEQUIN=TekkenMannequin_no_ik.blend T7_PLUGIN_DIR=<dir-of-package-parent> \
T7_CLIP_BIN=nakg_kg2kam_0xC8.bin T7_OUT=./out \
  xvfb-run -a env -u PYTHONPATH <blender> -b "$T7_MANNEQUIN" --python tools/anim/t7_c8_control_test.py
T7_PANTERA_GLB=pantera_leoman_t3real.glb T7_OUT=./out \
  xvfb-run -a env -u PYTHONPATH <blender> -b "$T7_MANNEQUIN" --python tools/anim/t7_c8_pantera_stance_bake.py
```

## Convergence note (two lanes, same clip, same answer)

While this lane ran, the parallel Claude Code lane landed commit `c2d5155f`
on main ("Pantera idles in King's real Tekken 7 stance"): its own baker
(`tools/anim/t7_c8_pantera_stance_bake.py`) produced
`game/assets/anim/t7/king/stance.json` — the same clip (index 132, same
arc sha256) expressed on the canonical mannequin skeleton at 60 fps with an
FK self-check of 0.0 m — and wired it into the game (`t3anims.js`
T7_STANCES). The two lanes **independently derived the same bone map**,
including the non-obvious `Spine1 -> Spine` pelvis-top correction in the bake section above.
This lane's contribution on top: (1) the independent *physical* control
test of the shared 0xC8 path (ground contact, knee direction, loop closure,
inspected-code safety record — the numbers both representations stand on),
and (2) a second representation of the pose baked **directly onto Pantera's
golden rig** in the t3-bank layout (22 joints incl. Root, 30 fps
convention, rotation-exact at ≤0.069°), kept as
`game/assets/anim/t7/king_on_pantera_leoman/t7_stance.json`.

## Status / handoff

The canonical stance is already wired into the game on main (commit
`c2d5155f`), so this work is **ready for the deployable-build lane to pick
up** with the next build. This PR adds the control-test evidence, the two
re-runnable tools, and the direct-rig representation; it deliberately
touches no moveset or fighter files and does not modify the other lane's
asset or wiring.
