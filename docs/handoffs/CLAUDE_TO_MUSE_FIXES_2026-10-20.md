# Claude → Muse: exact fixes, where the pipeline was going wrong, what to do next

Owner order 2026-10-20: "make handoff docs of everything ur doing documented to tell
Muse the exact fixes and where it was messing up as u work." This file is updated with
every commit on branch `claude/amazing-keller-p8644u`. Newest section last. Read it
before touching animation, the select screen, attires or the creation suite.

Rules this work follows (and Muse must too): AGENTS.md anti-clobber laws,
`docs/RULES_NO_GUESSING.md`, push every turn, no deletions without naming them.

---

## Fix 1 — fighters collapsing / gyro arms in every fight (ROOT CAUSE FOUND + FIXED)

### Symptom (seen in a live headless fight, frames viewed)
Pantera's whole body pitched sideways during attacks; arms gyro-displaced. The select
build log (`docs/workflows/2026-10-20-tekken-select-build.md`) already recorded "the
shipped fight path collapsing both fighters to the floor" and worked around it with a
fit gate on the select screen. The gate hid the problem. It did not fix it.

### Root cause
`game/js/t3anims.js` loaded the decoded T3 bank clips (`game/assets/anim/t3/<bank>/*.json`,
format wh-anim/1) and bound their quaternions **directly** to the game rigs' bones by name.
Those quaternions are **local rotations of the rig the bank was baked onto**:

| bank dir | baked onto (verified: every channel matches to 1e-6) | hierarchy |
|---|---|---|
| `king_on_pantera_leoman` | `lab/game/assets/pantera_leoman_t3real.glb` | WH-Canonical-22 (Root→Hips→Spine→Chest→Neck→Head) |
| `jin`, `xiaoyu`, `bryan`, `gunjack`, `yoshimitsu` | `lab/game/assets/t3_<bank>_t3real.glb` | T3 18-part import: **Chest hangs off Root, not Hips**; Head off Chest; no Spine/Neck/ToeBase |

Every joint on those rigs has an **identity rest rotation**. Game rigs do not:
`pantera.glb`/`steve-fox.glb`/`demonio.glb` have Hips rotated `(0,.707,.707,0)` under a
`Character` node, shoulders rolled 90°, etc.; Iori/DEATHFANG are 3ds Max Biped; Dio is
L_/R_ named. Playing an identity-rest local rotation on a non-identity-rest bone
rotates it to a nonsense orientation, hence the collapse. On top of that:

- the jin-family JSONs carry `Spine` and `Neck` channels that **do not exist on the
  source rig** (re-encode artefacts: `Neck` is a copy of `Chest`), and on a Mixamo
  hierarchy the source `Chest` rotation (a child of Root) gets composed under Hips *and*
  Spine, so it was applied twice;
- the canonical `Chest` channel never bound on Mixamo rigs at all (they call it `Spine2`);
- rigs with `mixamorig`-prefixed or Biped names bound nothing.

The repo **already had** the correct math: `lab/tools/t3_motion_bake.py` `retarget()`
(swing alignment from target rest bone direction to T3 stance direction, facing fix,
spine slerp). It was only ever run for Godot/canonical rigs. The browser game skipped it
(the handoff doc's item 4, "bake onto the Mixamo-49 rigs (needs rest-orientation
conversion)", was never done).

### Fix (commit on this branch)
1. `tools/anim/t3_bank_skeleton.py` (new): exports each bank's **source skeleton**
   (hierarchy and rest joint positions; foot tips from the skin where the rig has no
   ToeBase) from the source GLB, with SHA-256, to `game/assets/anim/t3/<bank>/skeleton.json`.
   `--check` proves the bank clips equal the source GLB channels.
2. `game/js/t3anims.js`: `retargetT3Clips(clips, bank, model, THREE, modelKey)` rebuilds
   every clip for the fighter's own rig using the same math as `t3_motion_bake.retarget`:
   `D(c) = F·G(c)·F⁻¹·A(c)`, `W(k) = D(driver(k))·Wrest(k)`, `local = W(parent)⁻¹·W(k)`;
   spine bones get `slerp(D Hips, D Chest, 0.5…1)`, neck bones `D Chest`; hips height
   follows `root_t` scaled by hip height. Bone names are canonicalized for Mixamo (with or
   without the prefix), 3ds Max Biped and L_/R_ rigs (`canonBoneName`).
3. `game/js/fighter.js`: `_bindT3()` binds the retargeted clips in `_build` and after a
   transform (`_doModelSwap`). Idle/walk now play the bank's stance/walk cycles; dodge
   plays T3's back-dash; jump plays T3 jump up/fwd/back. A T3-bound fighter never falls
   back to the embedded Mixamo "Idle" (a T-pose hold) mid-fight.

Proof: `docs/proof/claude-2026-10-20/retarget/` (before/after frames + state metrics).

### What Muse should do / stop doing
- **Stop** treating wh-anim/1 quaternions as rig-independent. They are only valid with
  their `skeleton.json`. Any new bank must ship `skeleton.json`; run
  `python3 tools/anim/t3_bank_skeleton.py` after adding one (add it to `BANKS` there).
- **Stop** adding fit gates that hide bad data. Fix the data path instead. The select
  screen's gate can stay as a safety net, but the stance should now pass it.
- Never re-encode a bank onto a hierarchy it wasn't baked on (the phantom Spine/Neck channels).

---

## Finding 2 — "t3_stance" is NOT the neutral stance (fix in progress)

`docs/research/formats/divmot-banks.md` in n0madic/Tekken3Remake (the RE the decoder
comes from): **move-index slots 0–2 are the round-start stance moves** (`FUN_8002D570`),
and the move row field `+0x10` "stance slot" is **3 = standing neutral, 40 = crouching
neutral**. Every bank's `t3_stance.json` is slot 0 (King's starts 0.50 m crouched and
rises; Gun Jack's and Yoshimitsu's jump around). Muse's bake labelled the round-start
intro as the idle. Fix: bake slot 3 (and 40 for crouch) per bank with the existing
`lab/tools/t3_motion_bake.py --clips t3_neutral=3,t3_crouch_neutral=40` and point the
`stance` action at it. Tracked in the next section once done.

---

## Finding 3 — 20+ roster/attire models are static meshes with NO skin

Measured with a glTF skin audit of every `MODEL_URLS` entry: these have zero skins and
**cannot animate at all** (they slide around as statues, or lie flat):
`demonio-a1` (Demonio's current roster model!), `sam-ur-a1`, `scimitar`,
`demonio-winged`, `demonio-human`, `doc-frank-wowomomo`, `doc-frank-hood`,
`doc-frank-frankenstein` (+ all their `-big` forms), `zangief`, `blanka`, `armor-king`,
`kronos`, `kronos-attire2`, `koreshi`, `phantom` (Tripo attire), `skull` (Tripo),
`saku-ra`, `purple-rain`, `waterfall`, `thor`, `thor-attire2`, `doc-frank-big`,
`dxmmii-a2`, `mariposa-slot2`, `cain-elias`, `cain-elias-attire2`, `burger` +
`burger-attire2..7`, `gyou-spirit`. Missing files: `ryuji-rock`, `deathfang-werewolf`.

Muse lanes keep wiring Tripo pulls straight into the roster unrigged. **Every model must
pass `tools/auto_rig/validate.py` (skinned, Hips, 1.5–2.2 m) before it is wired into
`roster-full.js` or `attires.js`.** Rig with `tools/auto_rig/auto_rig.py`
(`--backend knn --donor game/assets/models/pantera.glb` for dense Tripo statics, or
`gamerig`). Non-Mixamo rigs that DO have skins but unusual names (Vega SF5 naming) need
a name map in `canonBoneName` before they can take T3 motion.

---

## Fix 4 — owner: "something is permanently posing their bodies awkwardly" (3 root causes, measured)

Owner was right. Fix 1 alone was judged from wide fight frames where fighters are ~100 px tall,
which is not proof. The new **pose lab** (`game/poselab.html`) plays the bank clip RAW on the
rig it was baked onto (the true T3 pose) next to the game model playing the retargeted clip,
front and side, large, with per-bone world-direction errors. It found three more causes:

### 4a. Models face the wrong way / skeleton labels contradict the mesh
- Raw rest renders of all 52 skinned models (`docs/proof/claude-2026-10-20/model-facing/rest_sheet_*.png`):
  **8 meshes face -Z** (mariposa, mariposa-monarch, saku-ra-main, cape-jones, kiko-tanaka,
  kiko-tanaka_alt1, purple-rain-main, custom/Soldier). The game's facing math assumes +Z,
  so these fought with their backs to the opponent.
- The auto-rig template skeleton (`tools/auto_rig/backends/skeleton_template.json`, "faces -Z")
  sits inside **+Z meshes** on the whole pantera / steve-fox / demonio family: the bone named
  `LeftArm` is on the mesh's anatomical RIGHT, toe joints point behind the heel. Fix 1
  trusted the bone names, so the T3 pose was applied turned 180° (the fighter's back where
  the front should be). `before_fix_pantera_backwards.jpg` vs `pantera_rest_faces_plusZ.jpg`.
- Fix: `game/assets/models/model-facing.json` (per-model mesh facing read from the rest
  renders, proof listed in the file). `assets.js` wraps each instance so its space always
  has the mesh facing +Z. `t3anims.js analyzeRig` takes sides from mesh anatomy (+X = left)
  and swaps L/R driving when the labels are reversed. A toe joint pointing backwards keeps
  its rest relation to the shin. Unlisted models fall back to a feet-geometry cue only when
  it is confident (|score| >= 0.05; it misread no model at that threshold).
- **Muse:** check every new model's mesh facing on a raw rest render and add it to
  `model-facing.json`. Do not infer facing from bone names.

### 4b. Models authored with the origin at the hips stood waist-deep in the floor
star, torch, michiko, diablo, vega: vertices span y -1.05..+0.8. `assets.js` now grounds
every instance by its own skinned rest bounds (three r160 skinned bounding box).
`star_sunk_before_grounding.jpg` → `after_grounding_diablo_star_torch.jpg`.

### 4c. Broken skin weights (model defects, not animation)
- `steve-fox.glb` / `demonio.glb` (7 roster fighters: rin, byou, sha, jin_soul, zen, phantom,
  diablo… and demonio-body): the **shirt mesh (2,246 verts) incl. both sleeves is weighted
  100% to Spine/Spine1**. The sleeves stay in a T for any animation
  (`steve_fox_shirt_sleeves_spine1_BROKEN.jpg`). Being repaired by k-NN weight transfer from
  the same model's own arm/torso/neck meshes (see next section).
- `pantera.glb` belt2/buckles prims sit at shoulder height on Spine/Spine1 (already flagged
  in WORKLOG 2026-10-20; no source of truth for their placement, left as is).
- `deathfang` renders EMPTY at rest. `vega` has no Mixamo/Biped core bones.
- `mariposa`/`mariposa-monarch` wings tear under any pose (wing geometry on spine bones).
- **Muse:** gate every model with an arm-region skin audit (verts beyond 45% of the arm span
  must sit on arm-chain bones, wings/capes excepted) before wiring it.
