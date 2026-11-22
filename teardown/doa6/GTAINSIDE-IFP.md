# DOA6 animations via GTAinside GTAV06 .ifp packs — inventory, conversion, assessment

Lane 1D, 2026-11-22. This is the closest complete DOA6 animation material that
exists publicly: 32 per-character packs by GTAinside user GTAV06, converting
Dead or Alive 6 animations into GTA: San Andreas `.ifp` format.

## Source (licence / provenance — logged honestly, licence never gates)

- Author: GTAV06 (Bojan Vasiljevic, Philippines), https://www.gtainside.com/user/GTAV06
  — 208 mods, 646,177 downloads. Last activity ~2026-11-22.
- The 32 packs: https://www.gtainside.com/en/sanandreas/mods/ — mod IDs 213177
  (Common) + 213188 … 213749 (31 fighters). Full ID list in the lane workdir
  `gtainside/mods.txt`.
- Content: DOA6 (Team Ninja, 2019) character animations, extracted by the author
  from DOA6 and exported to GTA:SA `.ifp` (Kam's MaxScript ANP3 format) so they
  play on GTA:SA ped models. This is fan/modder extraction of commercial game
  animation data. No licence is stated on the packs. Logged here as-is.
- The 12 newest packs (Diego, Honoka, Kula, Mai, Momiji, NiCO, Nyotengu,
  Phase-4, Rachel, Raidou, Tamaki + Common) carry no bundled sound files; the
  other 20 also bundle CLEO `sound/doa6/*.wav` voice clips (DOA6 battle voices).
  The voice wavs are NOT converted into the bank (animation only).
- 32 zips, 258 MB total, sha256 per file in `gtainside/SHA256SUMS.txt` (lane
  workdir). The zips themselves are stored on the release
  `doa6-gtainside-ifp-20261122` (see INDEX.json), NOT in the git tree.

## Roster coverage — complete (32/32)

31 fighters = the complete DOA6 roster (24 base + 7 DLC: Nyotengu, Phase 4,
Momiji, Rachel, Tamaki, Mai Shiranui, Kula Diamond) + 1 Common pack
(shared/common animations, 924 clips). No DOA6 fighter is missing.

## What the bank contains

- Format: `wh-anim/1` JSON, one file per pack:
  `game/assets/anim/doa6/<Fighter>.json` (release assets; see INDEX.json).
  FINAL VALIDATED TOTAL: 12,816 clips across 32 bank files (1.1 GB),
  0 failed files, 0 validation problems (quat norms sampled, root_t ==
  Normal translation, per-bone frame counts preserved). Per-bank counts,
  bytes and sha256 in `INDEX.json`.
  Shape follows `game/assets/anim/t7/*/graph-clips/clips.NN.json` and
  `game/assets/anim/t3/*/*.json`: `format`, `fps`, `anim_set: FIGHT`,
  `bones`, `bone_ids`, `rot_xyzw` (per-bone per-frame xyzw quats),
  `trans_xyz` (per-bone per-frame translations, only for type-4 bones),
  `root_t` (the `Normal` root bone's translation, for WH-reader compat),
  `loop` (true for `(loop)`-named files), `source` (game, pack, zip, zip
  sha256, ifp file, ifp sha256, parser, skeleton note, trailing-bytes flag).
- Skeleton: the 29-bone GTA:SA ped skeleton as exported (bone IDs read from
  the files). See `game/assets/anim/doa6/skeleton.json`. Variants preserved
  as exported: 37-bone extended set in 24 clips (+ Belly 201, R/L breast
  301/302, 5 Nub end-bones 303–307, all type-4 with translations);
  25-bone set in 381 clips (the grounded `face_down_*` / down-state anims
  from the `[IFP]` packages — the 4 finger bones R Finger / R Finger01 /
  L Finger / L Finger01 are not animated in those).
- fps is detected per clip from the raw_time step: 60 (step 1, 11,368
  clips), 30 (step 2, 1,465 clips), plus two slow outliers — both
  `CMN05130_CMN (Car Bailout)` in Common (15 fps and 10 fps mirrored,
  203 frames each; a long cutscene-style anim, preserved as exported).
- Root translation Z in the loop/idle clips runs about -0.36..0.01 (negative):
  the DOA6 root sits below the GTA origin in the export. Preserved as-is;
  the retarget step owns the offset, not this conversion.
- Clip keys are the zip-relative .ifp path without extension
  (e.g. `KAS/Normal/KAS00111_KAS`, `KAS/Custom/KAS00111_KAS (mirrored)`,
  `[IFP]/face_down_0`). Normal/ vs Custom/ variants share basenames and are
  kept as separate clips (mirrored / face-forward / GTA-edit / old variants
  of the same numbered clip).
- `[IFP]/<char>.ifp` files (20 packs) are multi-animation packages (143–304
  anims each, 3,684 entries total). Their entries are converted too, keyed
  `[IFP]/<animname>`. 1,496 of those entries are anims with no split .ifp
  in the same pack (grounded `face_down_*`, CMN common anims,
  cross-character anims). The 19 split-pass `[IFP]/<char>.ifp` clips (each
  holding only anims[0]) were removed as duplicates of the multi-pass
  `[IFP]/<animname>` clips.

## Conversion

- Parser: `rwfury` (PyPI 0.6.1), ANP3 bit-exact parser — the converter uses
  it directly, no hand-rolled parser. Converter:
  `tools/anim/doa6-ifp-convert.py` (+ `tools/anim/doa6-ifp-multi.py` for the
  `[IFP]` packages). Vendored rwfury lives in the lane workdir (`.deps/`);
  the converter imports it from there.
- Verified: every clip re-parsed from the emitted JSON; quat norms sampled
  (tolerance 0.02, worst observed ~0.9996); `root_t` == `Normal` translation;
  per-bone frame counts preserved as exported (some bones legitimately have
  fewer frames than their siblings, e.g. KAS00144's L clavicle 61 vs 64).
- Stance/idle mapping (the only move mapping claimed): 19 `(loop)` clips
  verified as seamless loops (first/last frame quat dot >= 0.9993 on Normal
  + Pelvis, small root_z sway) and mapped as stances for 18 fighters in
  `moves.pack.json` (Phase 4 has two loop clips; its own PHF00000 is the
  stance, Kasumi's KAS00000 is also banked). 14 fighters have no `(loop)`
  clip and stay UNMAPPED for stance. No fight move is mapped to any clip.
- Known source quirks, all preserved and flagged in each clip's `source`:
  - KAS00246_KAS: 19,528 trailing bytes after the first 29 objects (18 extra
    type-4 objects: duplicated finger/leg bones + Belly + 5 Nub bones);
    declared frame-data size 2x the first animation's. Converted from the
    first animation only; trailing bytes recorded, not converted.
  - CRI00127_CRI (inside `[IFP]/christie.ifp`): same trailing-objects
    pattern; handled by the per-anim split.
  - HYT05300_HYT / HYT05301_CMN / HYT05311_CMN / HON04401_CMN: complete
    files whose declared frame-data size is wrong (exporter bug); converted
    by patching the declared size in the in-memory copy only.
  - KAS00144 (old): per-bone frame counts differ (61/60 vs 64).
  - Two clips per pack on average are 30 fps (raw_time step 2), the rest 60.

## Honest assessment — what converts and what does NOT

CONVERTS (done here):
- The complete DOA6 animation set as GTAV06 exported it: every numbered clip
  for every fighter + the Common pool + the multi-package extras. Real
  extracted keyframe data (quaternions + root translation), not transcribed
  frame tables. This is the closest thing to a complete DOA6 moveset/animation
  dump that exists publicly — no complete native DOA6 (G1A/G2A) animation dump
  exists anywhere (see EXTRACTION-ROUTE.md).

DOES NOT CONVERT (not faked, not papered over):
- These are GTA:SA-format animations on the 29/37-bone GTA ped skeleton.
  They are NOT DOA6-native skeletons and NOT WH fighter rigs. Retargeting
  onto WH rigs is a separate job — no retarget is performed or implied here.
- Clip names are numbers (`KAS00111_KAS`), NOT DOA move names (P, 6P, 3P…).
  No source maps numbers to DOA moves. The bank therefore does NOT claim
  any clip is a specific DOA move. `moves.pack.json` maps only what is
  verifiable (the `(loop)` idle/stance per fighter, where present) and lists
  everything else UNMAPPED with the reason. Do not guess mappings.
- The 6 repo DOA kits (`doa-kasumi`, `doa-bass`, `doa-hayabusa`,
  `doa-jannlee`, `doa-ayane`, `doa-tina`) keep their existing `anim_ref`s
  (`doa:<fighter>/<move>`), which are community-movelist refs, NOT bank
  keys. Wiring kits to numbered clips needs a number→move mapping source
  that does not exist yet.
- No DOA6 models, textures, or skeletons are in this bank (animation only).
  Models/textures need the G1M/RDB route (see EXTRACTION-ROUTE.md).

## Files

- Bank JSONs (release `doa6-gtainside-ifp-20261122`): 32 files, one per pack.
- `game/assets/anim/doa6/INDEX.json` — per-fighter counts, hashes, status.
- `game/assets/anim/doa6/skeleton.json` — GTA:SA ped skeleton + bone IDs.
- `game/assets/anim/doa6/moves.pack.json` — verified mappings only.
- `tools/anim/doa6-ifp-convert.py`, `tools/anim/doa6-ifp-multi.py` — converters.
