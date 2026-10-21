# PER-CHARACTER ISOLATION — Western Heart Pose/Animation Audit

**Date:** 2026-10-20  
**Scope:** ~50 roster entries → ~30 distinct default models. Why fighters looked "bent/weird/frozen" in-game, and what this PR fixes.

## Golden State (the standard of correct)

**2026-10-14, commits `124c03c` + `9bab504`.** `tools/t3_motion_bake.py` baked REAL decoded Tekken 3 King motion ONTO Pantera (bank dir literally `king_on_pantera_leoman`). The clips carry ABSOLUTE bone quaternions keyed to the canonical 22-bone skeleton. Pantera is the standard of correct — when a fighter's pose looks right, it looks like Pantera's did on Oct 14.

## The Five Families

### Family A — Healthy: canonical rig + embedded Idle
**Models:** pantera, steve-fox, demonio (identical 49-bone rig).  
**Status:** PASS the pose gate. These animate correctly with embedded clips + T3 banks.

### Family B — Canonical rig, NO embedded clips (rest = T-pose in game)
**Models:** demonio-bloodline-ember, baek-master-white, mariposa, mariposa-monarch, dxmmii, dxmmii-patchwork.  
**Status:** PASS the pose gate (skinned, canonically complete). They need T3 bank clips for idle/stance — this PR wires idle→own-bank `stance` loop so they animate instead of holding T-pose.

### Family C — Lane-C 33-bone canonical, no clips
**Models:** michiko, star, torch.  
**Status:** PASS the pose gate. Same treatment as Family B (bank-driven idle).

### Family D — Foreign rigs (engine cannot animate without remap)
| Model | Joints | Issue |
|-------|--------|-------|
| dio | 174 | No canonical names — engine cannot animate it at all |
| vega | 364 | Foreign naming scheme — **remapped by this PR** (see below) |
| bruno | 142 | Missing Spine2/Head names |
| yukihyo | 328 | Canonical names OK |
| doc-frank / machine-shop | 178 | Missing 'Spine' name only |
| iori + deathfang | 79 | KOF rig, 61 native clips incl. Battle_Idle — game only looked for exact 'Idle' |

**Status:** FAIL the pose gate unless remapped. This PR lands:
- **Vega foreign-rig remap** (`game/js/assets.js`): renames the 21 core joint nodes to T3 canonical names on the cloned instance (skinning-safe — glTF skins reference joint indices, not names). Strict no-op unless Vega's exact scheme signature is present.
- **Embedded-idle alias** (`game/js/assets.js`): Bip001-rig models (Iori, Deathfang) ship `Battle_Idle`/`Stage_Idle` but no clip literally named `Idle` — they now register as idle instead of falling back to bind pose.

### Family E — Statues (19): UNRIGGED, cannot animate at all
**Models:** demonio-a1, demonio-human, demonio-winged, sam-ur-a1, scimitar, zangief, blanka, armor-king, kronos, kronos-attire2, koreshi, dxmmii-a2, doc-frank wowomomo/hood/frankenstein + 3 *-big forms.  
**Status:** FAIL the pose gate (0 skins). These are raw Tripo exports: 1 node, 1 mesh, 0 skins, 0 animations. In-game they are frozen statues in authored pose. **They must go through the auto-rig pipeline** (`tools/auto_rig`: decompress → prenorm → blender-heat/GameRig → `validate.py` → `pose_gate.py`) before wiring. This PR does NOT wire them.

## Root Causes (why the roster looked broken)

The contamination was never one bad model — it was **shared layers**:

1. **One rig family for most of the roster.** Pre-#369, ALL fighters played the KING bank (`getT3Clips()` default). PR #369 added per-fighter `bankIdFor` (isolation-correct) + private IK scratch (genuine fix for the gyro arms bug).
2. **One shared Fighter class.** The gyro scratch aliasing bug (fixed #369) made arms behave identically across fighters.
3. **Mass in-place GLB rewrites.** PR #264 (2026-10-18, "Lane B auto-rig wave") rewrote 41 GLBs in place — roster-wide blast radius.
4. **Frozen-idle fallthrough.** The T3 bank `stance`/`walk` clips existed but were NEVER played for idle — idle fell through to `_stopT3()` and the near-static embedded Idle (rotation range ≤4.8°, Hips bob pinned). Headless diag: bank stance t=0 w=0 while mixer advanced embedded Idle at w=1; bone movement over 2s measured 0.0–1.0° on every bone.
5. **Constant tint wash.** `char.tintStrength ?? 0.45` lerped over every material in `createInstance` — both fighters washed in suit color (one red, one greenish-blue) for the whole fight.

## Pre-existing Defects (flagged, NOT fixed by this PR)

### Pantera Belt Defect (pre-existing since Oct 14 — DO NOT FIX here)
The belt2 + buckles meshes float detached beside Pantera's shoulders (proven by hide-test render). Present byte-identical in the golden-era file (`92fbd57` == `00e3522` == pre-#372, md5 `2bd9fc95`) — NOT a regression, shipped since Oct 14. PR #372 did not fix it. **Fix = per-file skin repair on Pantera's own GLB (pipeline work).** Flagged, not hand-fixed in this lane.

### DXMMII 4-Arm System (never landed)
DXMMII's skeleton is byte-identical to Pantera's 49-bone set — the 4-arm limb system was NEVER wired into the shipped model (no extra bones anywhere). The "jiggle" system has 0 code hits. Demonio-winged is a statue (wings cannot move). **The 4-arm/jiggle/wings features do not exist in the wired models.** Do not reference them as if they do.

## Fixes This PR Lands

1. **Tint fix** (`game/js/fighter.js`, `game/js/select-screen.js`, `game/js/assets.js`): Both `createInstance` call sites default to REAL colors. Main's `colorize` gate (`c.colorize ? (c.tintStrength ?? 0.3) : 0`) — no canon fighter sets `colorize`, so tint is 0 everywhere except the Create-a-Fighter skin tone (player's explicit choice). Tint survives ONLY as brief effects: Soul Surge aura (`_auraFlash`), impact flashes. The 57 roster `tintStrength` values are now inert (no `colorize` flag).
2. **Frozen-idle fix** (`game/js/fighter.js`): idle→own-bank `stance` loop, walk→`walkFwd`/`walkBack` (reversed when backing up), block→`block`, victory→`win`, hitstun→`hit`, knockdown→`launch`, KO→`ko`, attack→per-move T3 clip via `_moveRowAction` + `attackClipFor` fallback. The embedded layer is driven to ZERO when a T3 clip owns the state (was diluting clips ~50/50).
3. **Vega foreign-rig remap** (`game/js/assets.js`): 21 joints renamed to canonical T3 names + bind-frame conversion + Mixamo-spelling dict aliases (Spine1/Spine2). Vega now passes the pose gate.
4. **Embedded-idle alias** (`game/js/assets.js`): `Battle_Idle`/`Stage_Idle` → `Idle` for Bip001 rigs (Iori, Deathfang).
5. **T3 bind-relative retarget** (`game/js/t3anims.js`): `retargetClipToRig` converts bank clips (absolute quats for identity-rest canonical rig) via `out = targetBindLocal * clipQuat` so Mixamo-rig fighters don't fold. Chest→Spine2 rename, Root track dropped.
6. **Mesh facing + grounding** (from main, preserved in merge): `model-facing.json` + `feetFacingCue` ensures +Z facing; `groundY` puts feet on the floor.
7. **Baek→Kevin presentation** (owner 2026-10-20): the fighter IS Kevin (roster name, attires, CANON.md, RENAME-MAP.md). Model/path ids stable.

## The Pose Gate (`tools/auto_rig/pose_gate.py`)

Run BEFORE wiring any model:
```bash
python3 tools/auto_rig/pose_gate.py --in MODEL.glb
```
- Exit 0 = PASS (skinned, canonically complete, poseable; family A or B/C).
- Exit 1 = FAIL with reason:
  - 0 skins → Family E, route to auto-rig.
  - Incomplete canonical bones → Family D, remap or re-rig.
  - Statue-bound → Family E, route to auto-rig.

A model ships into `MODEL_URLS` only if it passes BOTH `validate.py` (playable gate) AND `pose_gate.py` (pose gate).
