# IN-FIGHT ANIMATION AUDIT — Western Heart (55 fighters)

Coordinator: PERSONALITY PASS · Owner NO-T-POSE LAW 2026-10-20 · Scope update 2026-10-20 ~07:57 CDT (extraction targets, not "blocked")
Worktree: `~/workspace/_wh-work/personality-pass`, branch `feat/personality-pass-20261020` @ origin/main `613b2943`. Audit only — no commits, no portrait changes, no merges.

> **COORDINATOR CORRECTION (2026-10-20, verified via git cat-file + GLB parse after materializing the sparse-checkout paths):** Section B's "model file missing" verdicts were WRONG for 9 of 10 fighters — this worktree's sparse checkout left `roster/…` paths unmaterialized, so present-in-git models read as missing on disk. Corrected truth: demonio / samura1 / demonio-winged / demonio-human / kronos / kronos-attire2 / koreshi models EXIST but are UNRIGGED statics (skins=0) → STATIC (rigging lane assigned); demonio-bloodline-ember EXISTS, rigged 50 joints 20/21 → ANIMATED; deathfang EXISTS, Bip001-rigged with 59 embedded clips → EMBEDDED. Only ryuji-rock is genuinely modelless (no model exists anywhere; owner Tripo link pending) and vega remains MISWIRED (foreign bone names). Corrected counts: **ANIMATED 34 / EMBEDDED 5 / PROCEDURAL-ONLY 1 / STATIC 13 / MISWIRED 2**. audit.json carries the same corrections per-row. The truth table rows for the 9 and Section B below are superseded by this correction.

## How this was verified (no guessing)

- Roster: `game/js/roster-full.js` `FULL_ROSTER` — 55 entries parsed programmatically.
- In-fight model (Attire 1): `model` field per fighter → `MODEL_URLS` in `game/js/assets.js:17` → file resolved relative to `game/` and checked on disk.
- Moveset source: `t3_source` in `game/assets/movesets/<fighter-id>.json` first (that is what `bankIdFor()` reads), else `MOVESET_MAP` in `game/js/fighter.js:42-68`.
- Bank: `bankIdFor()` (`game/js/fighter.js:81-87`) → `SOURCE_TO_BANK` (`game/js/t3anims.js:64-69`): king→king, demonio/jin/deviljin→jin, bryan→bryan, xiaoyu→xiaoyu, yoshimitsu→yoshimitsu, gunjack/bosconovitch→gunjack, **heihachi→null**.
- Live-fight gate: T3 actions are only created if clips loaded AND `this.bones.Hips && this.bones.RightArm` (`game/js/fighter.js:254`). Bones dict keys strip the `mixamorig` prefix (`game/js/assets.js:303`). Banks for the two fighters in a match are loaded in `game/js/main.js:708-709`; per-fighter movesets load at boot (`main.js:23-25`, fire-and-forget — JSON-vs-MAP source differences are all demonio↔jin / bosconovitch↔gunjack / deviljin↔jin, which resolve to the same bank either way, so the bank result is identical whether or not the JSONs have landed when `bankIdFor` runs).
- GLB inspection: small Python script parsing only the GLB JSON chunk (skins, joints, node names, animations, textures/images). No Blender, read-only.
- T3 bone set: `T3_BONES` in `game/js/t3anims.js:38-42` (22 names incl. Root; 21 core joints). `t3BoneMatch` in `audit.json` is strict: ALL 21 core bones present. **No fighter's model achieves a full 21/21 match** — see the systemic Chest note below.

## Classification counts (55)

| Class | Count | Fighters |
|---|---|---|
| ANIMATED | 34 | rin, byou, sha, kai, jin_soul, retsu, gyou, pantera, phantom, skull, sakura, zui, kinpo, waterfall, kingtyrant, burger, awapop, purplerain, nightwolf, cyborgx, michiko, star, torch, bruno, negativo, thor, yukihyo, slice, docfrank, doc-frank-machine-shop, baek-master-white, mariposa-monarch, dxmmii-patchwork, demonio-bloodline-ember |
| EMBEDDED | 5 | tou, zen, diablo, iori, deathfang |
| PROCEDURAL-ONLY | 1 | dio |
| STATIC | 13 | scimitar, doc-frank-wowomomo, doc-frank-hood, zangief, blanka, armor-king, demonio, samura1, demonio-winged, demonio-human, kronos, kronos-attire2, koreshi |
| MISWIRED | 2 | vega, ryuji-rock |

Definitions used, in priority order: (1) model file missing at its wired path → MISWIRED (fight load fails); (2) model present but no skin → STATIC; (3) decoded bank exists but the Hips+RightArm gate fails on bone names → MISWIRED; (4) decoded bank + gate passes → ANIMATED; (5) no bank + embedded clips → EMBEDDED; (6) no bank + no embedded clips → PROCEDURAL-ONLY.

## Systemic finding — the `Chest` track is orphaned on every ANIMATED fighter

Every decoded T3 bank clip carries a `Chest.quaternion` track (verified in all 6 bank dirs under `game/assets/anim/t3/*/t3_stance.json`: bones list = the 22 T3 names incl. `Chest`). The models the game actually loads have **no node named `Chest`**: the shared bases (steve-fox, pantera) and the 33-joint models (michiko/star/torch) and the reskins use `Spine1`/`Spine2` as the chest segment; doc-frank-machine-shop lacks both `Spine` and `Chest` (19/21); bruno lacks `Chest` and `Head` (19/21, its head bone has a different name). `jsonToClip()` in `t3anims.js` emits tracks named `<bone>.quaternion` with no Spine1/Spine2↔Chest remap, so the Chest track finds no target and is silently dropped by the AnimationMixer while the other 20 (or 19) tracks bind and animate. Net effect: ANIMATED fighters DO animate in-fight, but the chest segment of every T3 clip never drives the model — a real, fixable wiring gap (add a Chest→Spine2 (or Spine1) track rename at clip load), not a per-fighter failure. It is listed once here instead of being repeated as 33 separate MISWIRED rows.

## The 55-row truth table

| # | Fighter (id) | Model (id → path) | Exists / Shared | Source (origin) → Bank | Skinned / Joints | T3 bones matched | Embedded clips | Textures | Class |
|---|---|---|---|---|---|---|---|---|---|
| 1 | rin | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | jin (moveset-json) → jin | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 2 | byou | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | jin (moveset-json) → jin | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 3 | tou | pantera → `game/assets/models/pantera.glb` | YES / shared×10 | heihachi (moveset-json) → null | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 54 | **EMBEDDED** |
| 4 | sha | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | xiaoyu (moveset-json) → xiaoyu | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 5 | kai | pantera → `game/assets/models/pantera.glb` | YES / shared×10 | jin (moveset-json) → jin | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 54 | **ANIMATED** |
| 6 | jin_soul | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | yoshimitsu (moveset-json) → yoshimitsu | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 7 | retsu | pantera → `game/assets/models/pantera.glb` | YES / shared×10 | bryan (moveset-json) → bryan | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 54 | **ANIMATED** |
| 8 | zen | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | heihachi (moveset-json) → null | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **EMBEDDED** |
| 9 | gyou | pantera → `game/assets/models/pantera.glb` | YES / shared×10 | jin (moveset-json) → jin | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 54 | **ANIMATED** |
| 10 | pantera | pantera → `game/assets/models/pantera.glb` | YES / shared×10 | king (moveset-json) → king | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 54 | **ANIMATED** |
| 11 | demonio | demonio-a1 → `roster/demonio/attires/attire1/model.glb` | **NO — FILE MISSING** / dedicated | jin (moveset-json) → jin | no / 0 | — (no file) | 0 | 0 | **MISWIRED** |
| 12 | phantom | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | yoshimitsu (moveset-json) → yoshimitsu | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 13 | diablo | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | heihachi (moveset-json) → null | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **EMBEDDED** |
| 14 | skull | pantera → `game/assets/models/pantera.glb` | YES / shared×10 | bryan (moveset-json) → bryan | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 54 | **ANIMATED** |
| 15 | samura1 | sam-ur-a1 → `roster/sam-ur-a1/attires/attire1/model.glb` | **NO — FILE MISSING** / dedicated | gunjack (moveset-json) → gunjack | no / 0 | — (no file) | 0 | 0 | **MISWIRED** |
| 16 | sakura | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | xiaoyu (moveset-json) → xiaoyu | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 17 | zui | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | jin (moveset-json) → jin | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 18 | kinpo | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | jin (moveset-json) → jin | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 19 | waterfall | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | jin (moveset-json) → jin | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 20 | kingtyrant | pantera → `game/assets/models/pantera.glb` | YES / shared×10 | xiaoyu (moveset-json) → xiaoyu | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 54 | **ANIMATED** |
| 21 | burger | pantera → `game/assets/models/pantera.glb` | YES / shared×10 | bryan (moveset-json) → bryan | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 54 | **ANIMATED** |
| 22 | awapop | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | jin (moveset-json) → jin | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 23 | scimitar | scimitar → `game/assets/models/scimitar.glb` | YES / dedicated | jin (moveset-json) → jin | no / 0 | 0/21 (no skin) | 0 | 8 | **STATIC** |
| 24 | purplerain | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | jin (moveset-json) → jin | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 25 | nightwolf | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | xiaoyu (moveset-json) → xiaoyu | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 26 | dio | dio → `game/assets/models/dio.glb` | YES / dedicated | heihachi (moveset-json) → null | yes / 174 | 2/21 missing: Hips, Spine, Chest, LeftShoulder, LeftArm, LeftForeArm, LeftHand, RightShoulder, RightArm, RightForeArm, RightHand, LeftUpLeg, LeftLeg, LeftFoot, LeftToeBase, RightUpLeg, RightLeg, RightFoot, RightToeBase | 0 | 25 | **PROCEDURAL-ONLY** |
| 27 | cyborgx | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | gunjack (moveset-json) → gunjack | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 28 | michiko | michiko → `game/assets/models/michiko.glb` | YES / dedicated | jin (moveset-json) → jin | yes / 33 | 20/21 missing: Chest | 0 | 0 | **ANIMATED** |
| 29 | star | star → `game/assets/models/star.glb` | YES / dedicated | xiaoyu (moveset-json) → xiaoyu | yes / 33 | 20/21 missing: Chest | 0 | 0 | **ANIMATED** |
| 30 | torch | torch → `game/assets/models/torch.glb` | YES / dedicated | jin (moveset-json) → jin | yes / 33 | 20/21 missing: Chest | 0 | 0 | **ANIMATED** |
| 31 | bruno | bruno → `game/assets/models/bruno.glb` | YES / dedicated | bryan (moveset-json) → bryan | yes / 142 | 19/21 missing: Chest, Head | 0 | 18 | **ANIMATED** |
| 32 | negativo | pantera → `game/assets/models/pantera.glb` | YES / shared×10 | bryan (moveset-json) → bryan | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 54 | **ANIMATED** |
| 33 | thor | pantera → `game/assets/models/pantera.glb` | YES / shared×10 | bryan (moveset-json) → bryan | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 54 | **ANIMATED** |
| 34 | yukihyo | yukihyo → `game/assets/models/yukihyo.glb` | YES / dedicated | king (moveset-json) → king | yes / 328 | 20/21 missing: Chest | 0 | 0 | **ANIMATED** |
| 35 | slice | steve-fox → `game/assets/models/steve-fox.glb` | YES / shared×16 | bryan (moveset-json) → bryan | yes / 49 | 20/21 missing: Chest | 4 (Idle, Run, TPose, Walk) | 47 | **ANIMATED** |
| 36 | docfrank | doc-frank-machine-shop → `roster/doc-frank/attires/machine-shop/doc-frank-machine-shop-rigged.glb` | YES / shared×2 | bosconovitch (moveset-json) → gunjack | yes / 178 | 19/21 missing: Spine, Chest | 0 | 25 | **ANIMATED** |
| 37 | demonio-bloodline-ember | demonio-bloodline-ember → `roster/demonio/attires/bloodline-ember/demonio-bloodline-ember.glb` | **NO — FILE MISSING** / dedicated | jin (moveset-json) → jin | no / 0 | — (no file) | 0 | 0 | **MISWIRED** |
| 38 | demonio-winged | demonio-winged → `roster/demonio/attires/winged-devil/model.glb` | **NO — FILE MISSING** / dedicated | deviljin (moveset-json) → jin | no / 0 | — (no file) | 0 | 0 | **MISWIRED** |
| 39 | demonio-human | demonio-human → `roster/demonio/attires/human/model.glb` | **NO — FILE MISSING** / dedicated | jin (moveset-json) → jin | no / 0 | — (no file) | 0 | 0 | **MISWIRED** |
| 40 | doc-frank-wowomomo | doc-frank-wowomomo → `roster/doc-frank/attires/attire2/base/model.glb` | YES / dedicated | gunjack (moveset-json) → gunjack | no / 0 | 0/21 (no skin) | 0 | 3 | **STATIC** |
| 41 | doc-frank-hood | doc-frank-hood → `roster/doc-frank/attires/attire3/base/model.glb` | YES / dedicated | gunjack (moveset-json) → gunjack | no / 0 | 0/21 (no skin) | 0 | 3 | **STATIC** |
| 42 | doc-frank-machine-shop | doc-frank-machine-shop → `roster/doc-frank/attires/machine-shop/doc-frank-machine-shop-rigged.glb` | YES / shared×2 | gunjack (moveset-json) → gunjack | yes / 178 | 19/21 missing: Spine, Chest | 0 | 25 | **ANIMATED** |
| 43 | baek-master-white | baek-master-white → `roster/baek/attires/master-white/baek-master-white-rigged.glb` | YES / dedicated | bryan (moveset-json) → bryan | yes / 50 | 20/21 missing: Chest | 0 | 35 | **ANIMATED** |
| 44 | mariposa-monarch | mariposa-monarch → `roster/mariposa/attires/monarch/mariposa-monarch-rigged.glb` | YES / dedicated | xiaoyu (moveset-json) → xiaoyu | yes / 49 | 20/21 missing: Chest | 0 | 3 | **ANIMATED** |
| 45 | dxmmii-patchwork | dxmmii-patchwork → `roster/dxmmii/attires/patchwork-dj/dxmmii-patchwork-rigged.glb` | YES / dedicated | jin (moveset-json) → jin | yes / 49 | 20/21 missing: Chest | 0 | 21 | **ANIMATED** |
| 46 | zangief | zangief → `roster/zangief/attires/attire1/model.glb` | YES / dedicated | king (moveset-json) → king | no / 0 | 0/21 (no skin) | 0 | 3 | **STATIC** |
| 47 | blanka | blanka → `roster/blanka/attires/attire1/model.glb` | YES / dedicated | bryan (moveset-json) → bryan | no / 0 | 0/21 (no skin) | 0 | 12 | **STATIC** |
| 48 | vega | vega → `roster/vega/attires/attire1/model.glb` | YES / dedicated | xiaoyu (moveset-json) → xiaoyu | yes / 364 | 0/21 missing: Hips, Spine, Chest, Neck, Head, LeftShoulder, LeftArm, LeftForeArm, LeftHand, RightShoulder, RightArm, RightForeArm, RightHand, LeftUpLeg, LeftLeg, LeftFoot, LeftToeBase, RightUpLeg, RightLeg, RightFoot, RightToeBase | 0 | 4 | **MISWIRED** |
| 49 | iori | iori → `roster/iori/attires/attire1/model.glb` | YES / dedicated | heihachi (moveset-json) → null | yes / 79 | 0/21 missing: Hips, Spine, Chest, Neck, Head, LeftShoulder, LeftArm, LeftForeArm, LeftHand, RightShoulder, RightArm, RightForeArm, RightHand, LeftUpLeg, LeftLeg, LeftFoot, LeftToeBase, RightUpLeg, RightLeg, RightFoot, RightToeBase | 59 (Awakening, Back_Step, Back_Walk, Battle_Idle...) | 3 | **EMBEDDED** |
| 50 | armor-king | armor-king → `roster/armor-king/attires/attire1/model.glb` | YES / dedicated | king (moveset-json) → king | no / 0 | 0/21 (no skin) | 0 | 33 | **STATIC** |
| 51 | kronos | kronos → `roster/kronos/attires/attire1/model.glb` | **NO — FILE MISSING** / dedicated | king (moveset-json) → king | no / 0 | — (no file) | 0 | 0 | **MISWIRED** |
| 52 | kronos-attire2 | kronos-attire2 → `roster/kronos/attires/attire2/model.glb` | **NO — FILE MISSING** / dedicated | king (moveset-json) → king | no / 0 | — (no file) | 0 | 0 | **MISWIRED** |
| 53 | deathfang | deathfang → `roster/deathfang/attires/attire1/model.glb` | **NO — FILE MISSING** / dedicated | heihachi (moveset-json) → null | no / 0 | — (no file) | 0 | 0 | **MISWIRED** |
| 54 | ryuji-rock | ryuji-rock → `roster/ryuji-rock/attires/attire1/model.glb` | **NO — FILE MISSING** / dedicated | king (moveset-json) → king | no / 0 | — (no file) | 0 | 0 | **MISWIRED** |
| 55 | koreshi | koreshi → `roster/koreshi/attires/attire1/model.glb` | **NO — FILE MISSING** / dedicated | heihachi (moveset-json) → null | no / 0 | — (no file) | 0 | 0 | **MISWIRED** |

Shared-base note: `steve-fox` is the in-fight model for 16 fighters and `pantera` for 10 — those 26 fighters have no dedicated GLB; they are palette-tinted instances of a shared base. `doc-frank-machine-shop` is shared by 2 (docfrank + doc-frank-machine-shop). All other present/missing models are dedicated per fighter.

## MISWIRED — decoded bank (or a working model) exists, but it never reaches the fighter

### A. Rigged-but-unwired (1) — the model can be posed, the wiring can't reach it

- **vega** — model `../roster/vega/attires/attire1/model.glb` EXISTS, skinned, **364 joints, 0/21 T3 bones match** (joint names are `_rootJoint`, `Waist_06`, `Chest_08`, `Head_010`, …). Source xiaoyu (`game/assets/movesets/vega.json` t3_source) → bank **xiaoyu (decoded)** via `t3anims.js:64-69`. But `fighter.js:254` requires `bones.Hips && bones.RightArm`; this rig has neither name, so T3 actions are never created. Embedded clips: 0. Procedural IK (`fighter.js` `_ik`, `_animAttack`) also keys on T3 names (`RightArm`, `LeftUpLeg`, …), so it no-ops too. In-fight result: bind pose, despite a decoded bank and a fully skinned model. Fix kind: bone-name retarget/remap for this rig, or re-rig to the Mixamo/T3 naming.

### B. Model file missing at the wired path (10) — load fails before animation is even a question

`AssetManager.loadModels()` (`game/js/assets.js`) loads `MODEL_URLS[id]`, retries once, then rejects; `main.js` catches that as "Failed to load fighters" — a match with any of these fighters cannot start as wired.

- **demonio** — `MODEL_URLS['demonio-a1']` = `../roster/demonio/attires/attire1/model.glb` (`game/js/assets.js`) → resolved path `roster/demonio/attires/attire1/model.glb` **does not exist in the repo**. Source jin → bank jin. A working rig DOES exist unused at `game/assets/models/demonio.glb` (skinned, 49 joints, 20/21 T3 bones, embedded Idle/Run/TPose/Walk) — the `demonio:` key in assets.js points there, but roster demonio's model is `demonio-a1`, whose path is absent (there is no `roster/demonio/` directory in this checkout at all).
- **samura1** — `MODEL_URLS['sam-ur-a1']` = `../roster/sam-ur-a1/attires/attire1/model.glb` (`game/js/assets.js`) → resolved path `roster/sam-ur-a1/attires/attire1/model.glb` **does not exist in the repo**. Source gunjack → bank gunjack. Same pattern: a working rig exists unused at `game/assets/models/sam-ur-a1.glb` (skinned, 49 joints, 20/21, 0 embedded clips, 24 textures), but `sam-ur-a1` is wired to the missing `../roster/sam-ur-a1/...` path (no `roster/sam-ur-a1/` directory in this checkout).
- **demonio-bloodline-ember** — `MODEL_URLS['demonio-bloodline-ember']` = `../roster/demonio/attires/bloodline-ember/demonio-bloodline-ember.glb` (`game/js/assets.js`) → resolved path `roster/demonio/attires/bloodline-ember/demonio-bloodline-ember.glb` **does not exist in the repo**. Source jin → bank jin.
- **demonio-winged** — `MODEL_URLS['demonio-winged']` = `../roster/demonio/attires/winged-devil/model.glb` (`game/js/assets.js`) → resolved path `roster/demonio/attires/winged-devil/model.glb` **does not exist in the repo**. Source deviljin → bank jin.
- **demonio-human** — `MODEL_URLS['demonio-human']` = `../roster/demonio/attires/human/model.glb` (`game/js/assets.js`) → resolved path `roster/demonio/attires/human/model.glb` **does not exist in the repo**. Source jin → bank jin.
- **kronos** — `MODEL_URLS['kronos']` = `../roster/kronos/attires/attire1/model.glb` (`game/js/assets.js`) → resolved path `roster/kronos/attires/attire1/model.glb` **does not exist in the repo**. Source king → bank king.
- **kronos-attire2** — `MODEL_URLS['kronos-attire2']` = `../roster/kronos/attires/attire2/model.glb` (`game/js/assets.js`) → resolved path `roster/kronos/attires/attire2/model.glb` **does not exist in the repo**. Source king → bank king.
- **deathfang** — `MODEL_URLS['deathfang']` = `../roster/deathfang/attires/attire1/model.glb` (`game/js/assets.js`) → resolved path `roster/deathfang/attires/attire1/model.glb` **does not exist in the repo**. Source heihachi → bank null (heihachi). `roster/deathfang/` exists in this checkout but contains only `tools/` (df_chains.py etc.) — no `attires/attire1/model.glb`.
- **ryuji-rock** — `MODEL_URLS['ryuji-rock']` = `../roster/ryuji-rock/attires/attire1/model.glb` (`game/js/assets.js`) → resolved path `roster/ryuji-rock/attires/attire1/model.glb` **does not exist in the repo**. Source king → bank king. `game/js/assets.js:145-150` comment says it plainly in-repo: "MODEL PENDING: no Yamazaki model found anywhere… URL wired for the drop-in; model.glb lands the moment the owner sends a Tripo link" (`roster/ryuji-rock/` does not exist in this checkout).
- **koreshi** — `MODEL_URLS['koreshi']` = `../roster/koreshi/attires/attire1/model.glb` (`game/js/assets.js`) → resolved path `roster/koreshi/attires/attire1/model.glb` **does not exist in the repo**. Source heihachi → bank null (heihachi).

### C. STATIC even though a bank exists (6) — kept separate from MISWIRED: these cannot be posed at all until rigged

Each model's GLB has `skins: []` (jointCount 0, no embedded clips). The bank exists, the gate is moot — there is no skeleton for any clip, embedded or T3, or for procedural IK, to drive. `assets.js:createInstance` also logs `ZERO skinned meshes` for this shape of model. Fix kind: rigging (auto-rig/re-rig), NOT wiring.

- **scimitar** — model `game/assets/models/scimitar.glb` exists, **unrigged** (textures 8), source jin → bank **jin (decoded)** unreachable for lack of a rig.
- **doc-frank-wowomomo** — model `roster/doc-frank/attires/attire2/base/model.glb` exists, **unrigged** (textures 3), source gunjack → bank **gunjack (decoded)** unreachable for lack of a rig.
- **doc-frank-hood** — model `roster/doc-frank/attires/attire3/base/model.glb` exists, **unrigged** (textures 3), source gunjack → bank **gunjack (decoded)** unreachable for lack of a rig.
- **zangief** — model `roster/zangief/attires/attire1/model.glb` exists, **unrigged** (textures 3), source king → bank **king (decoded)** unreachable for lack of a rig.
- **blanka** — model `roster/blanka/attires/attire1/model.glb` exists, **unrigged** (textures 12), source bryan → bank **bryan (decoded)** unreachable for lack of a rig.
- **armor-king** — model `roster/armor-king/attires/attire1/model.glb` exists, **unrigged** (textures 33), source king → bank **king (decoded)** unreachable for lack of a rig.

### D. Secondary wiring notes (not counted as separate MISWIRED rows)

- **iori (EMBEDDED, rigged-but-different-skeleton):** 59 embedded clips on a `Bip001 …` skeleton (79 joints, 0/21 T3 names). `createInstance` (`game/js/assets.js:309`) only auto-plays clips literally named `Idle`/`Walk`/`Run` — iori has `Walk` and `Run` but **no `Idle`** (it has `Battle_Idle`, `Stage_Idle`), so in-fight it animates when moving and falls back to bind pose when standing still. Its T3 source is heihachi→null, so no bank is involved.
- **dio (PROCEDURAL-ONLY, crippled fallback):** skinned (174 joints, names like `MODEL_00`, `L_Arm`, `Spine1`/`Spine2` — only Neck/Head of the T3 names), 0 embedded clips, source heihachi→null. Even the procedural fallback is largely inert: `_ik` chains and `_weaponBone`/hurtbox lookups key on `Hips`/`RightArm`/`RightHand`/`Spine1`-style Mixamo names this rig mostly doesn't carry (it does have `Spine1`). Class stays PROCEDURAL-ONLY by definition (no bank should apply), but in practice it is close to static in-fight.
- **docfrank (ANIMATED, bosconovitch fixup):** JSON source is `bosconovitch`; `SOURCE_TO_BANK` maps it to the decoded gunjack bank, and its model is the rigged doc-frank-machine-shop GLB (178 joints, Hips+RightArm present) — it animates today. See Extraction Targets for its true-source bank.

## EXTRACTION TARGETS — banks not yet baked/decoded (owner order 2026-10-20: extraction is the job; these are work items, not blockers)

Source material verified for this checkout: `git ls-files` tracks `teardown/tekken3/disc/files/TEKKEN3/TEKKEN3.BNS` and the already-extracted divmot bins `teardown/tekken3/animations/divmot03_king.bin`, `divmot04_yoshimitsu.bin`, `divmot07_xiaoyu.bin`, `divmot09_jin.bin`, `divmot12_bryan.bin`, **`divmot13_heihachi.bin`**, `divmot16_gunjack.bin`, `divmot99_common.bin` (these teardown paths are tracked in git but not materialised in this worktree's checkout, so they were verified via the git index, not a directory listing). The 6 banks in `game/assets/anim/t3/` (king, jin, xiaoyu, bryan, gunjack, yoshimitsu) were baked from exactly this pipeline. **Heihachi is the closest target: his divmot bin is already extracted — his bank was simply never baked** (`t3anims.js:58`: "heihachi: no decoded bank exists (raw divmot only) — intentionally absent").

| Fighter | Extract this T3 character's bank | Why (effective source and/or roster base) | What covers them today |
|---|---|---|---|
| byou | **Lei** | roster base = Lei Wulong | proxy bank jin (from source jin) — animates, but with another character's motion |
| tou | **Heihachi** | effective t3_source = heihachi | nothing — bank null (embedded/procedural only, or less) |
| tou | **Paul** | roster base = Paul Phoenix | proxy bank None (from source heihachi) — animates, but with another character's motion |
| kai | **Eddy** | roster base = Eddy Gordo | proxy bank jin (from source jin) — animates, but with another character's motion |
| zen | **Heihachi** | effective t3_source = heihachi; roster base = Heihachi | nothing — bank null (embedded/procedural only, or less) |
| gyou | **Hwoarang** | roster base = Hwoarang | proxy bank jin (from source jin) — animates, but with another character's motion |
| diablo | **Heihachi** | effective t3_source = heihachi; roster base = Heihachi | nothing — bank null (embedded/procedural only, or less) |
| kingtyrant | **Eddy** | roster base = Eddy Gordo | proxy bank xiaoyu (from source xiaoyu) — animates, but with another character's motion |
| awapop | **Nina** | roster base = Nina | proxy bank jin (from source jin) — animates, but with another character's motion |
| nightwolf | **Julia** | roster base = Julia | proxy bank xiaoyu (from source xiaoyu) — animates, but with another character's motion |
| dio | **Heihachi** | effective t3_source = heihachi | nothing — bank null (embedded/procedural only, or less) |
| torch | **Anna** | roster base = Anna | proxy bank jin (from source jin) — animates, but with another character's motion |
| yukihyo | **Armor King** | roster base = Armor King | proxy bank king (from source king) — animates, but with another character's motion |
| docfrank | **Bosconovitch** | effective t3_source = bosconovitch; roster base = Bosconovitch | gunjack bank via SOURCE_TO_BANK fixup |
| doc-frank-wowomomo | **Bosconovitch** | roster base = Bosconovitch | gunjack bank via SOURCE_TO_BANK fixup |
| doc-frank-hood | **Bosconovitch** | roster base = Bosconovitch | gunjack bank via SOURCE_TO_BANK fixup |
| doc-frank-machine-shop | **Bosconovitch** | roster base = Bosconovitch | gunjack bank via SOURCE_TO_BANK fixup |
| dxmmii-patchwork | **Mokujin** | roster base = Mokujin | proxy bank jin (from source jin) — animates, but with another character's motion |
| iori | **Heihachi** | effective t3_source = heihachi | nothing — bank null (embedded/procedural only, or less) |
| armor-king | **Armor King** | roster base = Armor King | proxy bank king (from source king) — animates, but with another character's motion |
| deathfang | **Heihachi** | effective t3_source = heihachi | nothing — bank null (embedded/procedural only, or less) |
| koreshi | **Heihachi** | effective t3_source = heihachi | nothing — bank null (embedded/procedural only, or less) |

Distinct extraction targets: **Anna, Armor King, Bosconovitch, Eddy, Heihachi, Hwoarang, Julia, Lei, Mokujin, Nina, Paul** (11 characters). Fighters listed: 21 (a fighter appears once per target; tou appears for both Paul — its roster base — and Heihachi — its effective moveset source).
Fighters whose roster base is one of the target characters but who are NOT listed because a decoded proxy already covers them and neither their base nor source is in the target set: none — every such fighter is listed above; the table distinguishes "covered by proxy today" from "covered by nothing today" in the last column. Bosconovitch fighters are covered today by the gunjack fixup and are listed only because Bosconovitch's own bank is an extraction target, not because they are unanimated.

## Per-class in-fight reality

- **ANIMATED (34):** Real decoded T3 clips play in-fight (stance/light/medium/heavy/grab/block/hit/launch/ko/win per `T3_CLIP_DEFS`, `t3anims.js`). Caveat for all 33: the `Chest` track is orphaned (above), and for the 26 on shared steve-fox/pantera bases the motion is their source character's, on a shared body — personality comes from the bank, not a dedicated model.
- **EMBEDDED (5):** tou/zen/diablo ride the shared bases' embedded Idle/Walk/Run (combat is procedural IK on top); iori rides its own 59-clip set, minus a wired Idle (above).
- **PROCEDURAL-ONLY (1):** dio — see note D.
- **STATIC (13):** bind pose in-fight; root position still moves (game drives `root.position`), limbs never do. Rigging lane assigned to all 13 (docs/personality-pass/RIGGING-LOG.md).
- **MISWIRED (2):** vega (rigged, bank exists, bone names break the gate — remap lane assigned) + ryuji-rock (no model file exists anywhere — owner Tripo link pending). [The original '10 missing model files' claim is retracted in the coordinator correction at the top.]

Machine-readable rows: `docs/personality-pass/audit.json`.
