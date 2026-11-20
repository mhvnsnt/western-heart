# Where real Tekken 7 rigs and motion are (and are not): checked 2026-11-09, corrected 2026-11-09

Owner (verbatim): "do the skin wait and get the rig and stuff the skeleton in the model and the skin and the weights and
all perfect and then put it on the f****** more upgraded Tekken 7 are taking five f****** bases". Standing law
(2026-10-23): T7 is first-class, T3 is fallback only.

> **Correction (2026-11-09, later the same day):** the first version of this doc concluded that the real T7 game
> files were missing and had to come from the owner's install. That was wrong about where they were held. The
> owner's Steam copy had already been pulled (depot 389731, 2026-10-31..11-02) and was sitting in split-part
> Releases on `mhvnsnt/game-reverse-engineering` the whole time. Those files are being copied to western-heart as
> Release `tekken7-gamefiles-v1` (copy still in progress at this writing — see Verification). The "What unblocks
> it" ask below is therefore RESOLVED — see "The game files (now on western-heart)". The negative findings
> (model-site rips are rig-stripped statics; `tekken7-full-v1` has no motion; the T5 release is stage geometry)
> were re-checked and still stand.
>
> **Second correction (2026-11-09, wire-up lane):** an earlier draft of this correction assumed all 9 target
> bases sit in `pakchunk0-WindowsNoEditor.pak` (+ its `_P` pak). They do not: **Julia and Negan exist only in
> `pakchunk1-WindowsNoEditor_P.pak`** (GRE wave0). The extraction below read them from there. Also, the
> extraction and motion results are no longer pending — they are committed in this repo (see "Extraction —
> done 2026-11-09").

## The plan this serves

1. Give each fighter's Tripo model its base character's own T7 skeleton.
2. Transfer that character's professional (Namco) skin weights onto it with Robust Skin Weights Transfer (Abdrashitov et
   al., SIGGRAPH Asia 2023, the industry method).
3. Animate it with the character's own T7 motion on that skeleton.

## Inventory

| Source | What it really holds |
|---|---|
| `teardown/tekken7/king/`, `king-variants/rigmodels/` | King only: Pantera's exact-King T7 build. |
| Release `tekken7-full-v1` (3.3 GB, 7 parts, 1,266 files, listed by streaming) | Fan and model-site downloads: King variants plus `models/<char>/` zips for Julia, Negan, Eddy, Steve Fox, Asuka, Xiaoyu, Lili, Josie (12-34 MB), small (~1 MB) fan models for Ganryu, Yoshimitsu, Bryan, Lee, Lei, Nina, Baek, Mokujin, Gun Jack, Zafina (T6 XNALara) and Bosconovitch (TTT2 XPS). |
| The eight large FBX rips, imported in Blender 4.0.2 | **Static meshes: no armature, zero vertex groups.** Model-site exports drop the rig. One zip also carries an `Animate3D.exe` (never run; the extracted files were deleted). |
| Release `tekken7-full-v1`, any motion | **None:** no `.arc`, `.anm`, `motbin` or pak files. |
| Release `tekken5-ctype5-glbs-v1` | Stage and effect geometry (beams, rings), not characters. |
| `game/assets/anim/t7/<base>/` | The 17 bases' T7 stances and move packs. Baked from `GRE teardown/tekken7-steam/tkdata/mothead/mask/<code>rotsm.arc` (`tools/anim/t7_c8_stance_bake.py`): a T7 Steam teardown on another lane's machine, not in the repo or Releases. |
| GRE Releases `t7-depot389731-wave1-20261031` / `t7-depot389731-wave3-20261031` | **The real game files** (see next section). Present since 2026-10-31..11-02; missed by the first inventory because it only searched this repo and its Releases. |
| archive.org (checked live 2026-11-09, search + metadata API, files inspected) | **No usable Steam-build T7:** `takken-7` is an empty item (metadata only, no payload files); `tekken-7-iso-file` is a 250.6 MB stub zip with no metadata file list; remaining hits are arcade VHDs, tools, OST and video. |

## The game files (now on western-heart)

Provenance: Steam TEKKEN 7 (app 389730), depot 389731, manifest 1653672533371481747, pulled 2026-10-31..2026-11-02
from the owner's (Vil3m) Steam library via DepotDownloader. Held as split-part Releases on
`mhvnsnt/game-reverse-engineering`; copied cloud-to-cloud (release → release, no local staging) to western-heart
on 2026-11-09.

**Release `tekken7-gamefiles-v1` (mhvnsnt/western-heart)** — 54 payload assets + `MANIFEST-tekken7-gamefiles-v1.json`
(+ the source `MANIFEST-wave1.json` / `MANIFEST-wave3.json`). Reassemble each file by concatenating its `.part-NN`
assets in numeric order, then check the whole-file sha256 in the manifest.

| File (game path) | Size | Whole-file sha256 | Parts |
|---|---|---|---|
| `TekkenGame/Content/Paks/pakchunk0-WindowsNoEditor.pak` | 20,108,006,385 B | `d30cb0b6ad54bb9f0180672f65abe8856cb48e5c5f9012b5e866530c1297ade4` | 43 × 471,859,200 B |
| `TekkenGame/Content/Paks/pakchunk0-WindowsNoEditor_P.pak` | 4,543,870,420 B | `c5cbd1e44b55cf47895463bb9e4fb7bacd2cf14fa323eff1cea324a8bd29a787` | 10 |
| `TekkenGame/Content/Binary/tkdata.bin` | 304,756,784 B | `f1523deaa8a17ad4fbd599d23ab9c4bd1e9bed7904277e15244bd5bc183daf3c` | 1 |

Verification (2026-11-09, interim): the copy is **still running** — 8 of 54 payload assets had landed by
23:39 UTC, each one's sha256 checked by GitHub's upload digest during the copy against the original depot-pull
hashes in the source manifests (all 8 matched). When the copy completes, all 54 asset digests are re-read from
the new release and matched, `tkdata.bin` and the first/last pakchunk0 parts (part-00, part-42) are pulled back
in full and re-hashed locally, and the three manifest files are uploaded to the release. The extraction below
did **not** wait for this copy: it read the identical bytes from the GRE wave Releases through a streaming
range reader (every extraction output manifest records both provenances).

What the rig/motion lane can now consume, per base (Julia, Negan, Eddy, Steve Fox, Asuka, Xiaoyu, Lili, Josie, King):

- **Skeletons + Namco skin weights:** the skeletal meshes inside the paks — pakchunk0 for Eddy, Steve Fox,
  Asuka, Xiaoyu, Lili, Josie and King; **pakchunk1_P for Julia and Negan (they are nowhere else)**. Already
  extracted to GLB — see "Extraction — done 2026-11-09".
- **Motion:** `tkdata.bin` — the complete tkdata payload; the mothead/motion data the in-game T7 stances and
  attacks were baked from lives inside this binary. Bake each base's own walk / block / hit / KO through
  `tools/anim/t7_generic_bank_bake.py`.

Not copied (not needed for the WH release copy): wave0 `pakchunk1-WindowsNoEditor_P.pak` (18.2 GB), wave2
`pakchunk1-WindowsNoEditor.pak` (15.9 GB), wave4 movies, wave5 tail. They remain on the GRE releases above if a
later lane needs them — note the wire-up lane already consumed wave0/wave2 **from GRE** for the pak indexes and
the Julia/Negan extraction. Extracted banks already on GRE: `t7-fighter-banks-v1`, `t7-bank0-clips-v1`,
`t7-rotsm-clips-v1`.

## Extraction — done 2026-11-09

All 9 bases extracted from the real paks (index reader `tools/extract/t7/pak_index.py` parses all four paks;
driver `tools/extract/t7/extract_bases.py`; range reader `tools/extract/t7/release_range.py`):

- **70 GLBs** under `teardown/tekken7/<base>/` — every part carries the shared T7 skeleton
  (`SKT_CH_base_Skeleton`, raw asset at `teardown/tekken7/_shared/raw/`) and Namco `WEIGHTS_0`;
  207–289 joints per GLB depending on the part; every slot rc=0. Per-base table:
  `teardown/tekken7/T7-BASES-REPORT-2026-11-09.md`; machine record:
  `teardown/tekken7/extraction-manifest.json` + per-base `MANIFEST.json`.
- **Motion:** `tkdata.bin` (local pull hash-verified against the wave3 manifest) unpacked with
  `tools/extract/t7/tkdata_unpack_tolerant.py`: 1,087/1,087 entries, 0 failed — `mothead/bin` (57 movesets)
  and `mothead/mask` (58 rotsm.arc) complete. Each base's parsed moveset is committed at
  `teardown/tekken7/motion/<code>mot.json`; the chain into `tools/anim/t7_generic_bank_bake.py` is documented
  in `teardown/tekken7/motion/README.md`.

## What unblocks it — RESOLVED 2026-11-09

The first version asked for the T7 game files from the owner's install, uploaded as a Release, following
`tools/depot-pull/T7-USER-STEPS.md`. No owner action is needed: the files were already held (above) and are now
Release `tekken7-gamefiles-v1` on this repo. The plan at the top of this doc can proceed: T7 skeleton in, Namco
weights transferred with Robust Skin Weights Transfer, the base's own T7 motion baked.

## Why the rig-only route is not enough (Thor, 2026-11-09)

Re-rigging Thor with `tools/auto_rig/refit_rig.py` changed his weights and joints. The owner judged the in-fight change
at about 5%, and against his base model he is still squashed.

He plays the Tekken 3 Bryan stance. The retarget leaves his torso 12.6 deg and his arms 11-12 deg off that source, and
it stacks three correction layers on the old data: head 77 deg, spine -12.9 deg and arm rolls of 48-76 deg. Switching
them off (`globalThis.__WH_RETARGET_LAYERS` in poselab) exposes the raw T3 head twisted about 77 deg.

Proof: `docs/proof/2026-11-09/refit-thor/`.
