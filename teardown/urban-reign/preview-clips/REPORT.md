# Urban Reign Preview Clips — Lane Report (2026-11-21)

Workdir: `~/workspace/preview-clips/urban-reign/` (240 MB logical).
Converter: `ur_to_bannon.py`. Bone map + FK proof: `BONE_MAP.md`.
Move map: `ur_move_map.json` (1,151 moves + 67 moveset-coverage entries).

## What was delivered

| Stage | Count | Location |
|---|---|---|
| Motions converted (general banks) | **829** (normal 342, 30frame 373, weapon 114) | `clips/` (61 MB) |
| Exported (Blender, BANNON GLB) | **832** (827 full + 5 proof), 0 failed | `intermediates/` (84 MB) |
| Assembled previews | **832**, all contract-valid | `previews/` (84 MB) |
| Named general motions | 29 clips, 27 distinct names | see map |
| Proof moves | 5 (1 pair + 4 solos) | `jobs-proof.json`, `shots/` |

## Verification

- **FK:** euler recovery validated to 0.002° RMS (root position
  cross-check); 791/829 motions FK into a sane stance at frame 0;
  ur_m001 reads as a textbook fighting guard. H1 is the unique correct
  convention (H0/H2 both fail).
- **Exporter CALIB:** R_bt exact, R_cm max deviation 0.000001,
  q_clip vs apply() 0.0000° (proof) / 0.056° (full run, first job).
  Clip/rig ratios IDENTICAL to the proven VPW2 v1.3 mixamo clips.
- **IK clamps:** 0/516 chain-frames on the golemnage pair render.
- **Contract (all 832 previews):** 52 bones each, 0 violations; worst
  |quat norm − 1| = 0.0001; 0 Hips trajectories out of band.
  Durations 0.13–5.37 s, 19.3 min total.
- **Renders:** golemnage pair at f1/f49/f97/f129 (`shots/`) — coherent
  figures, correct proportions, feet on the floor.

## Moves covered (of 1,151)

- **5 pmot clips convertible now** (proven identical to a general-bank
  motion by root-stream match): char001 ur_m004/m005/m006
  (dwngnuke asi/atama/left_y) + char005 ur_m022/m023 (unnamed in-bank,
  = golemnage1_f/_y). Name matching alone is NOT proof — the bridge
  tested same-name pairs and most failed the root gate.
- **67 moveset entries performable from the general pool** (fighter
  performs the move using a shared motion; no pmot clip of its own).
- **1,146 pmot clips blocked**: motion data lives in the per-fighter
  `.ppk` banks, whose range-coded tracks need the ELF tables
  (SLUS_212.09 — not in any repo; the ISO release
  `urban-reign-iso-v1` holds the ISO in parts, range-fetchable, but
  release access needs approval) OR the street-reign GLBs with
  embedded clips (31 exist per the index; location unknown — the
  index lists bare filenames and the western-heart char GLBs are
  269 KB without animations).
- **5 no-bank records** (cbco_screw_r, moco_d_jumpk_f/_y1/_y2,
  moco_doubleairk_f): no source bank in the shipped disc at all —
  emulator capture only. None of the 1,151 clips carries these names.
- **41 proxy-only fighters** can only use general-pool motions.

Per-category (named, of 484): moco 241, cbco 166, momt 13, mohr 9,
cbca 6, hahr 6, itco 5, cbbx 4, haco 4, hakk 4, + 13 small prefixes;
unnamed 667. Roles: solo 1,005, P2 (_y) 130, P1 (_f) 16; only 12
_f/_y pairs have both halves in the same fighter.

## Honest gaps in the converted set

- **136/829 clips have a corrupt root decode in the staging**
  (frame-to-frame root jumps 0.5–11.6 m; the type-14 range decode
  fails for those tracks). Rotations are fine; the root is zeroed
  (motion plays in place) and the clip is flagged
  `root_corrupt: true` in `_ur`. Breakdown: normal 41, 30frame 49,
  weapon 46.
- **Root rotation is bind-only** (the packed root quat is position
  data fed through the Euler path — garbage, discarded). Pelvis
  orientation in flips/throws comes from the chain, not a root track.
- **UR has no finger bones and 2 spine joints**: ha/fi are rigid
  wrist extensions (curl ~0), chest shares MUNE2's rotation.
- **Receiver staging is an assumption**: the pair re-lift stages the
  receiver 0.65 m in front (driver fallback); the starting grapple
  distance is not in the data. `_f` = P1 / `_y` = P2 by convention;
  suffix semantics are unconfirmed in teardown docs.

## Open Mars calls (not decided here)

- **D3:** which UR moves enter the library (no UR entries yet; library
  wiring is a follow-up).
- **D5:** verbatim UR names vs Bannon-rename (names staged verbatim).
- **D10 (from WIRING-SPEC):** UR fighters as bodies needs Mars's call
  + rename/re-skin (not this lane's scope).

## Compliance note

A system security notice was attached to the western-heart sparse clone
(`wh/`, read-only): no git commands were run inside it, no code from it
was run/imported/loaded, and none of its files were copied elsewhere.
The char001 GLB was read as DATA with this lane's own scripts; all
decoder code used is the local teardown copy the task references.
Nothing in `anim-real-models/` was modified (one VPW2 clip was read
for format reference only); nothing was written to
`preview-clips/export/`, `preview-clips/previews/`, or `maps/`.
Nothing was deployed to live.
