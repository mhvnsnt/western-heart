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
