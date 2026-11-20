# ZUI — Attire Slots (owner 2026-10-18)

Tripo 3D model = DEFAULT attire (owner law 2026-10-18).

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Zui — Drunken Monk (Tripo)** | `roster/zui/attires/attire1/model.glb` — Tripo-generated Drunken Monk (owner Drive file, 20.7MB, tripo_node), the untouched original. In game it plays as `roster/zui/attires/attire1/model-rigged.glb` (auto-rigged 2026-10-21, see below). DEFAULT. |
| 2 | **Zui — Rework v2** | `roster/zui/attires/attire2/model.glb` — rework v2 (bald, saffron/indigo, tattoo decals). |
| 3+ | **Steve Fox base + reskins** | `steve-fox` canon base + `zui_alt1` / `zui_alt2` (T7 Steve reskins) — selectable alternates via `ATTIRE_VARIANTS['zui']` (wired 2026-10-21). |

- Base: Steve Fox (canon). "Zooey" NOT in canon — flagged in TRIPO-REGISTRY.md.
- Render: Attire 1 T-pose render at `docs/tpose-refs/zui/a1_front.png` (2026-10-21, own-eyes verified) → owner generative-AI transform.
- Wiring (2026-10-21, model-key audit follow-up to PR #418): the two Tripo GLBs previously had NO MODEL_URLS keys and were unreachable in game. Now: `zui-attire1` / `zui-attire2` keys in `game/js/assets.js`, `ATTIRE_VARIANTS['zui']` in `game/js/attires.js` (Slot 1 = default), and roster `model:` = `zui-attire1` so the enemy/raw path loads the Tripo too. Steve Fox base stays a selectable alternate — not deleted, not the default.

## Stance System (2026-10-21 — owner: "stance switch from boxing to drunken fist and Steve's other stances")
Zui's moveset (`game/assets/movesets/zui.json`) carries Steve Fox's **complete T7 set** (286/287 rows; WALL BOUND skipped — mechanic row, no input) plus Lei Wulong's **drunken fist** as a distinct stance group. Data-level stances — entry moves resolve through the input buffer, gated moves by exact-notation lookup (`stances` block in zui.json; engine has no stance flag — see `docs/movesets/ZUI-STANCE-SYSTEM-2026-10-21.md`).

| Stance | Entry (touch) | Notes |
|---|---|---|
| BOX — Boxing (default) | — | all non-gated Steve moves |
| DCK — Ducking | `f+3` | 10 gated moves |
| LWV / RWV — Weaves | `3` / `4` from Ducking | 14 / 5 |
| FLK — Flicker | `b+3+4` | 23 |
| PKB — Peekaboo | via `,F` transitions (entry row preserved `f+3+4_r198`) | 42 — `f+3+4` chord fires Drunken Master Walk instead |
| SWY — Swaying | `b+3` | 3 |
| ALB — Albatross | `3+4` | 5 |
| **DRU — Drunken Fist (Drunken Master)** | **`f+3+4` (Drunken Master Walk)** | 40 Lei T7 moves verbatim; exit `DRU b`; sustain `DRU 1+2` (Tiger Sip) |

Fits the canon: Attire 1 is the Drunken Monk, title "Drunken Master", style "Boxing/Drunken".

## Rig (2026-10-21, Claude session — owner: "Unrigged static statue models need to be rigged and skinned fully the auto way")
The A1 Tripo had ZERO skinned meshes, so the fighter was invisible and the fight threw `getWorldPosition` errors.
It is now auto-rigged with the repo's open-source pipeline; the original file is unchanged.
1. `node tools/anim/gltf_codec.mjs decode model.glb` (Blender 4.0.2 cannot read meshopt).
2. `tools/auto_rig/backends/gamerig_backend.py` (GameRig/Rigify, 73 deform joints, WH names, bone heat on a voxel proxy). Bone heat: 86 of 24,022 proxy verts unweighted; 5,792 of 1,026,274 mesh verts took the nearest-bone fallback.
3. `tools/auto_rig/backends/smooth_weights.py` brought edge stretch p99.9 from 6.66 to 1.52 (gate 2.5).
4. `gltf_codec.mjs encode` produced `model-rigged.glb` (31.9MB).

Gates: `validate.py` PASS (1.80 m, all bones). `anim_check.py`: edge stretch PASS; two flags remain, both reviewed.
- Zero-length Rigify pelvis helpers: same as the Baek example.
- Hip-bound sash verts swinging rigidly in the CMU kick.

Renders were viewed at three frames from front, back and side, and in a live fight vs Pantera with 0 page errors.
Proof: `docs/proof/claude-2026-10-21/auto-rig-zui/`.
