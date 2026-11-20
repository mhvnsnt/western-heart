# Tekken 7 base extraction — per-base report (2026-11-09)

Real Tekken 7 skeletons + Namco skin weights for the 9 target bases, extracted
from the owner's own Steam copy (TEKKEN 7 app 389730, depot 389731, manifest
1653672533371481747). Extraction ran against the GRE wave Releases via the
streaming range reader (`tools/extract/t7/release_range.py` +
`tools/extract/t7/pak_index.py`); the bytes are identical to Release
`tekken7-gamefiles-v1` on this repo (same sha256 manifests). Driver:
`tools/extract/t7/extract_bases.py`; targets in `tools/extract/t7/t7_bases.json`;
full machine-readable record in `extraction-manifest.json` beside this file.

Method per part: pak entry → per-asset AES fix where needed → umodel
(`-game=tekken7 -export -gltf`) → GLB. Every GLB embeds the shared T7 skeleton
(`TekkenGame/Content/Character/Common/Skeleton/SKT_CH_base_Skeleton.uasset`);
the raw skeleton asset is committed at `_shared/raw/SKT_CH_base_Skeleton.uasset`
(407,503 B, sha256 `80ea6f9c80e05e508b2c265061b27e56dc79f3b6e68e6ac6d3250e8d08029725`)
because standalone Skeleton assets export 0 objects through umodel.

## Per-base results

| Base | Code | Source pak | Skeleton | Joints / GLB | Namco weights | Parts (GLBs) | Repo path |
|---|---|---|---|---|---|---|---|
| Julia Chang | jul | pakchunk1_P (GRE wave0) | YES | 213–271 | YES — all parts | 12 | `teardown/tekken7/julia-chang/` |
| Negan | nsa | pakchunk1_P (GRE wave0) | YES | 214–236 | YES — all parts | 9 | `teardown/tekken7/negan/` |
| Eddy Gordo | edd | pakchunk0 (GRE wave1) | YES | 207–239 | YES — all parts | 4 | `teardown/tekken7/eddy-gordo/` |
| Steve Fox | ste | pakchunk0 (GRE wave1) | YES | 207–231 | YES — all parts | 5 | `teardown/tekken7/steve-fox/` |
| Asuka Kazama | ask | pakchunk0 (GRE wave1) | YES | 207–240 | YES — all parts | 18 | `teardown/tekken7/asuka-kazama/` |
| Ling Xiaoyu | xia | pakchunk0 (GRE wave1) | YES | 207–257 | YES — all parts | 5 | `teardown/tekken7/ling-xiaoyu/` |
| Lili Rochefort | lil | pakchunk0 (GRE wave1) | YES | 207–289 | YES — all parts | 4 | `teardown/tekken7/lili-rochefort/` |
| Josie Rizal | mut | pakchunk0 (GRE wave1) | YES | 213–283 | YES — all parts | 6 | `teardown/tekken7/josie-rizal/` |
| King | kin | pakchunk0 (GRE wave1) | YES | 209–238 | YES — all parts | 7 | `teardown/tekken7/king/` |

Notes:

- **70 GLBs total, every slot rc=0, every GLB carries WEIGHTS_0.** Parts are the
  character kit slots (face / hair / upper / lower / head / extra, incl. variant
  pieces). Per-part detail (pak path, uasset sha256, pak-entry sha1, joints,
  bone names, GLB bytes) is in each base's `MANIFEST.json` and in
  `extraction-manifest.json`.
- **Julia and Negan live ONLY in `pakchunk1_P`** (GRE wave0) — not in pakchunk0
  or pakchunk0_P. The other seven are in pakchunk0 (GRE wave1). All four paks
  were indexed by `pak_index.py` (pakchunk0: 33,270 entries; pakchunk0_P:
  12,200; pakchunk1: 59,575; pakchunk1_P: 50,795).
- **King:** the fresh GLB kit lands in the same `teardown/tekken7/king/`
  directory as the pre-existing Pantera exact-King build (FBX + textures,
  untouched — no path collisions). King's WH fighter is Pantera; Xiaoyu's is
  Sakura (per `t7_bases.json`).
- **Motion:** `teardown/tekken7/motion/` holds each base's parsed moveset
  (`<code>mot.json`, from `mothead/bin` via `tools/extract/t7/t7_motbin_to_json.py`)
  and the README there documents the full tkdata → mothead → bank-bake chain
  (`tools/anim/t7_generic_bank_bake.py`). tkdata unpack: 1,087/1,087 entries,
  0 failed, mothead/bin (57) + mothead/mask (58 rotsm.arc) complete.

## What this unblocks

Per `docs/handoffs/T7-RIG-MOTION-SOURCES-2026-11-09.md`: each Tripo fighter
gets its base's real T7 skeleton (above), Namco weights transferred with Robust
Skin Weights Transfer, and the base's own T7 motion baked — Tekken 3 retired
for those fighters.

## Release copy status (tekken7-gamefiles-v1)

The cloud-to-cloud copy of the raw game files to this repo's Release
`tekken7-gamefiles-v1` is **still running** (8/54 assets landed and
digest-verified at 23:39 UTC 2026-11-09; each part is sha256-checked against
the source wave manifests as it lands). It is archive redundancy — extraction
above did not wait for it. On completion, the release gets its manifest files
(`MANIFEST-tekken7-gamefiles-v1.json`, `MANIFEST-wave1.json`,
`MANIFEST-wave3.json`) and the final all-54 digest re-read + full pull-back
re-hash of tkdata.bin and pakchunk0 part-00/part-42.
