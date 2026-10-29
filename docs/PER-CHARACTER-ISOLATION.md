# PER-CHARACTER ISOLATION — the pose/animation gate

**Owner law, 2026-10-20 (verbatim core):** "The extra arms for Dxmmii, the
jiggle bones, the wings, extra wrists/hands — those are PER CHARACTER, added
onto that character's own already-working Tekken skeleton and animations…
A two-armed character should never start acting like the four-armed
character. Their stuff is separated, per character."

**Refinement (owner, 2026-10-20):** per-character work must be GATED so an
edit for one character cannot leak into another — *unless it actually
parallels*. Characters built on the same Tekken source share what truly
parallels, **through the shared source data, deliberately**. An edit made
for one character must never bleed into another character's files or state
as a side effect. Structure per-character data the way Tekken's own
developers do (per-character files in the teardown data), not by
hand-tooling shared state.

This document is the gate. Every lane that touches models, rigs, or
animation reads it first.

---

## 1. The golden architecture (2026-10-14/15 — restore target)

When Pantera was first modded in, he moved **exactly like King**: King's
real decoded Tekken 3 motion, baked onto Pantera's own skeleton
(`lab/tools/t3_motion_bake.py`, commits `124c03c` + `9bab504`, bank dir
`king_on_pantera_leoman/`). That is the pattern for every character:

- **Motion comes from the character's Tekken source**, decoded from the
  teardown — never hand-authored pose values, never another character's
  clips.
- Each fighter's animation bank lives in **its own directory**
  (`game/assets/anim/t3/<source>/`), mirroring Tekken's own per-character
  file layout in the teardown data.
- The fighter's **own model file** carries its own skeleton, skin, and
  embedded clips. Additions (extra arms, wings, jiggle, extra hands) are
  built **on that character's own skeleton**, in that character's own
  files.

## 2. The gate — where data is allowed to live

| Data | Lives in | Shared? |
|---|---|---|
| Skinned model + skeleton + skin weights | The character's own GLB (`roster/<char>/…` or `game/assets/models/<char>.glb`) | **Never.** Editing it affects that character only. |
| Tekken motion bank (stance/attacks/walk) | `game/assets/anim/t3/<moveset-source>/` | **By design, through the source.** Fighters whose moveset source is the same Tekken character share the bank *because they parallel* (e.g. every King-source fighter reads the `king` bank). |
| Moveset data (inputs, damage, frame data) | `game/assets/movesets/<char>.json`, `game/assets/<source>_moves.json` | Per character / per source. |
| Per-character additions (Dxmmii's arms, wings, jiggle, transforms) | That character's own directory + that character's own model file | **Never.** A two-armed character must never gain four-armed behavior. |
| Engine code (`fighter.js`, `assets.js`, `t3anims.js`, `main.js`) | `game/js/` | Shared **plumbing only**. A shared-code change must be *data-neutral*: it may wire/discover/route per-character data, it must never inject one character's data, pose values, or rig assumptions into another character. |

### Hard rules

1. **No mass in-place model rewrites.** A commit that rewrites many
   characters' GLBs at once (e.g. PR #264's 41-file "re-rig wave") is
   forbidden. Rig/repair work lands **one character at a time**, as a
   **new file in that character's own directory**, with the model's entry
   in `assets.js` `MODEL_URLS` repointed at it. The original file stays.
2. **Restore-from-source only.** If a stance/pose is wrong, the fix is to
   re-derive it from the character's Tekken source data (teardown banks,
   the model's own embedded clips). Hand-tweaked pose numbers are not a
   fix — if a character seems to need them, stop and report instead.
3. **Banks bind by moveset source, always.** `bankIdFor(charId, movesetId)`
   in `fighter.js` is the only routing. There is no default bank: a
   fighter whose source has no decoded bank gets **no** bank — never
   another character's (this was the pre-#369 bug: every fighter played
   the King bank).
4. **Clip/bone names are canonical.** Banks use the canonical 22-bone
   Mixamo names. Name canonicalization (e.g. the bake's `Chest` →
   `Spine2`) happens in `t3anims.js` clip construction — once, for every
   bank equally — never by editing a character's skeleton to match a clip.
5. **Statues don't ship as fighters.** A model with no skin/skeleton
   cannot idle, stance, or fight. Unrigged Tripo/figurine exports must go
   through the auto-rig pipeline (`tools/auto_rig/`, heat backend) into
   the character's own directory **before** they are wired as a playable
   attire. Gate check: `tools/auto_rig/pose_gate.py`.
6. **Additions are additive.** Per-character systems (limb system,
   transforms, wings) attach to the character's own already-working
   skeleton and animations. They must be removable without touching any
   other character's files or behavior.

## 3. What broke (audit 2026-10-20, summary)

Full audit: `docs/POSE-AUDIT-2026-10-20.md`. Root causes, in order:

1. **The banks' stance clips were never played.** `fighter.js` `_animate`
   had no `idle` case — idle fell through to `_stopT3()`, so in-fight idle
   was the generic Mixamo mocap layer (or a raw T-pose / frozen statue),
   not the fighter's own Tekken stance. The select screen had the same
   gap (embedded `Idle` or rest pose only).
2. **Pre-#369, every fighter played the King bank** (`getT3Clips()`
   default). PR #369 (2026-10-20) fixed the routing per source — the
   isolation-correct direction — but idle still never called the stance.
3. **19 wired models were unrigged statues** (0 skins, 0 animations —
   raw Tripo/figurine exports), including Demonio's default Attire 1 and
   SAM-UR-A1. In game they stand frozen in their authored pose forever.
4. **Dead chest track on every bank clip:** the T3 bake named the chest
   bone `Chest`; every shipped skeleton names it `Spine2`. The track
   bound to nothing roster-wide, so all T3 motion lost its chest segment.
5. **Native idles ignored:** KOF-source models (Iori/Deathfang rig) carry
   their idle as `Battle_Idle`; the loader only registered exact `Idle`,
   so their base layer found nothing.
6. **Shared-code hazards** (kept fixed): the gyro-arms IK scratch-aliasing
   bug (#369, shared scratch vectors in the shared `Fighter` class) is the
   template for what rule 2/6 above forbids — per-fighter state must be
   per-fighter instances, never shared scratch.
7. **Non-defects verified:** Dxmmii's shipped model has **no** extra-arm
   bones (its skeleton is the standard 49-bone rig — the limb system was
   never wired into the shipped GLB, so it also never leaked); there is
   **no** jiggle code anywhere in the shipped game; Mariposa's wings are
   inside her own model files. Pantera's floating `belt2`/`buckles`
   meshes are a per-file skin defect present since the golden Oct-14 file
   (byte-identical blobs) — a Pantera-file repair item, not a regression
   and not shared.

## 4. The fix (this PR)

- `fighter.js`: `idle` state plays the fighter's **own bank stance**
  (loop); `walk` uses the bank's `walkFwd`/`walkBack` when the model has
  no embedded `Walk` of its own. Fighters without a bank are untouched.
- `main.js`: the select preview poses in the fighter's own bank stance
  when available; the procedural "breathing" fallback no longer applies
  on top of a posed fighter.
- `assets.js`: a model's own `Battle_Idle`/`Stage_Idle` clip registers as
  its `Idle` (per-model data only).
- `t3anims.js`: `Chest` → `Spine2` track canonicalization at clip build.
- Statues rigged one at a time via `tools/auto_rig` into each character's
  own `roster/<char>/…` directory as **new files**; `MODEL_URLS` repointed
  per character. Originals untouched.
- `tools/auto_rig/pose_gate.py`: the pre-flight gate — run it on any
  model before wiring it as playable.
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
