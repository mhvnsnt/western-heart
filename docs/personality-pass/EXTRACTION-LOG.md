# Tekken 3 Bank Extraction Log — Personality Pass (2026-10-20)

Owner order: extraction IS the job. Pipeline: BNS -> divmot -> pose_assemble/usa_motion
decode -> t3_motion_bake bake onto the character's own WH-Canonical-22 GLB ->
GLB-to-wh-anim/1 re-encode -> validate through game/js/t3anims.js jsonToClip logic.

## Environment / setup

- Worktree: `~/workspace/_wh-work/personality-pass` (branch feat/personality-pass-20261020 @ 613b2943).
- This worktree has sparse-checkout active; `teardown/tekken3/` and `lab/` were tracked
  but not materialized. Fixed additively (did NOT disable sparse-checkout):
  appended `/teardown/tekken3/**` and `/lab/**` to the worktree sparse-checkout file,
  removed a stale 0-byte `index.lock` left by the interrupted first reapply, then
  `git sparse-checkout reapply`. Verified on disk: divmot13_heihachi.bin = 268,796 bytes,
  TEKKEN3.BNS = 38,150,144 bytes.
- `/tmp` is a 512MB tmpfs filled by another lane's `/tmp/rigwork` (472MB, not touched).
  All scratch (KMDs, stance OBJs, base GLBs, driver scripts) lives in
  `~/workspace/_wh-work/pp-scratch/`.
- n0madic research tools (motion.py) located at
  `~/workspace/tools/tekken3remake/tools/research` -> exported as `T3REMAKE_RESEARCH`
  for lab/tools/t3_motion_bake.py (its default `/workspace/t3anim/...` does not exist).

## Step 1 — divmot extraction from TEKKEN3.BNS

Method: `teardown/tekken3/bns-table.pkl` (303 entries: id, sector, size);
byte_offset = sector x 2048 (per teardown/tekken3/docs/BNS-ORGANIZATION-PATTERN.md).
Identity verified three ways per bank: size == n0madic original-disc index,
header byte 0x01 == divmot type, SHA-256 prefix == n0madic index SHA-256.

| type | character | BNS id | bytes | sha256 (prefix) | verified |
|---:|---|---:|---:|---|---|
| 00 | Paul | 280 | 313472 | 06f6447a | size+sha match n0madic index |
| 02 | Lei | 282 | 318524 | bd795779 | size+sha match |
| 05 | Nina | 285 | 333384 | 50430e78 | size+sha match |
| 06 | Hwoarang | 286 | 312268 | d0b5b43a | size+sha match |
| 08 | Eddy | 288 | 336652 | 0383ddb2 | size+sha match |
| 10 | Julia | 290 | 267924 | d4c8ce91 | size+sha match |
| 17 | Anna | 297 | 314684 | 16886320 | size+sha match |
| 18 | Bosconovitch | 298 | 332372 | 130ee660 | size+sha match |
| 15 | Mokujin | 295 | 0 in this disc image | — | ABSENT, see below |

Written to `teardown/tekken3/animations/divmotNN_<char>.bin`.

### Mokujin — exhausted attempts, concrete evidence
1. BNS table entry 295 = (sector 17534, size 0) — the bank is not in this disc image.
   The repo's own BNS doc records the same fact ("divmot15 is absent locally").
2. Raw read of 127,368 bytes at sector 17534 (the size n0madic lists for the original
   disc) yields sha256 prefix c3b3ffbb, header 00108701 — that is the START OF THE NEXT
   ENTRY's data (Gun Jack, id 296), not a type-15 divmot (header byte 0x01 would be 0x0f).
3. Filesystem search for any other `TEKKEN3.BNS` or `divmot15*` copy in ~/workspace:
   none found.
Conclusion: divmot15 cannot be extracted from the owner's local disc image; it exists on
the original disc per n0madic's index (127,368 bytes, sha256 5cead15f...). Mokujin's KMD
model DOES exist locally (BNS 207, parses, 24,728 bytes) — only the motion bank is absent.
No mokujin bank was fabricated from another character's motion (per-character isolation).

## Step 2 — KMD models + stance OBJs

KMD = BNS entry 71 + (name-table index x 8), P1 (verified: entry 95 is byte-identical
to the existing models/king95/king95.kmd). Extracted to scratch, validated with
kmd_parse.py: paul 71, lei 87, nina 111, hwoarang 119, eddy 135, julia 159, anna 231,
mokujin 207. Bosconovitch is not in the 21-name table (hidden character); his model
group follows Anna's: BNS 239 parses as a valid KMD (20 rows with verts) and his
stance OBJ has 386 verts vs 487-662 for the regular cast — consistent with
Bosconovitch's small hunched model. Identification basis: group sequence + parse +
proportions; flagged here as inferred, not name-verified.

Stance OBJs: pose_assemble.py (slot 0, frame 75 — same as the existing
renders/pose-check/*_stance75.obj), with usa_tables.EXE_PATH pointed at the repo's
teardown/tekken3/disc/files/TEKKEN3/SLUS_004.02 (the tool's baked-in default path
under game-reverse-engineering/ does not exist). All 8 new chars + heihachi generated
(stream_frames 150 @60fps, julia 151 — matches the pose-check convention).

## Step 3 — movesets + attack picks (light/medium/heavy; grab = heavy)

Movesets for the 8 new characters were extracted with the repo's own
teardown/tekken3/tools/local/moveset_extract.py (extract_bank driven directly;
its __main__ hardcodes the old game-reverse-engineering path and the original 7 banks).

The 6 existing banks' attack clips match the t3_row values in the game's aggregate
frame-data files game/assets/<char>_moves.json exactly (verified for jin/bryan/king/
xiaoyu/yoshimitsu/gunjack), and in every existing bank t3_grab.json is byte-identical
to t3_heavy.json. So:
- Heihachi: rows from game/assets/heihachi_moves.json (light 38, medium 64, heavy 182).
- Armor King: rows from game/assets/king_moves.json (35, 63, 230) on divmot03_king —
  Armor King has no Tekken 3 divmot of his own (not in the T3 roster/name table);
  his WH moveset t3_source is 'king'. His bank is King's motion baked on King's own
  rig (the existing 'king' bank is King motion retargeted onto pantera_leoman).
- The 8 new characters have no aggregate *_moves.json. Their picks use a documented
  class-profile rule fitted to the 7 known banks' picks (all: strike attack_word in
  {0x0217, 0x010f, 0x0607}, active_first > 0; light dmg 10-12 / stream 31-64;
  medium dmg ~25 / stream 46-70; heavy dmg 35-43 / stream 54-100):
  light = dmg 10-12, stream closest to 45; medium = dmg closest to 25 (band 20-28),
  stream closest to 60; heavy = dmg 28-60 minimizing |dmg-38| then |stream-75|
  (widened because Paul and Nina have NO strike with dmg 35-43 and an active
  window — their 35+ dmg moves are throws, attack_word 0x0800, active 0).
  Rows -> slots by inverting the bank's move_index (each attack row has exactly
  one slot). Full picks table: see pp-scratch/picks.json (reproduced in the summary
  of the final report).

## Step 4 — base GLBs (lab pipeline's t3_to_gltf.py)

`python3 lab/tools/t3_to_gltf.py fighter <kmd> <stance75.obj> <out.glb>` per character.

### Heihachi divergence — geometry-less parts 2/9/13
Heihachi's KMD rows for canonical parts 2 (pelvis), 9, 13 have ZERO vertices (his
mesh merges those parts into neighbours, e.g. part 1 carries 56 verts). Stock
t3_to_gltf.py and t3_motion_bake.py both crash: `pivots[0] = pivots[2]` -> KeyError: 2.
Fix (scratch copies of the two tools only; repo tools untouched): fill missing
pivots from the pose chain itself — the world-matrix origins pose_assemble.py
computes for slot 0 frame 75 (part offsets from the KMD rows + pose rotations).
Proven equivalent on King, where both exist: chain origin vs Kabsch pivot differ
by <= 1.6 T3 units (~1.6 mm) across all 17 parts. Override values (T3 units):
part 2 [-82, -1118, 136], part 9 [22.842, -1458.627, 205.407],
part 13 [-175.254, -1466.342, 178.552]. Applied via env T3_PIVOT_OVERRIDE pointing
at a JSON file; inert for all other characters. Heihachi base GLB height: 1.96 m.

## Step 5 — bake (lab/tools/t3_motion_bake.py, driven via pp-scratch/bake_driver.py)

Per character: input = the character's own base GLB; BANKS patched to the scratch
t3root (models + stance OBJ) with the divmot read from the repo animations dir;
--clips = the 25 universal slots (stance 0x0/0x1/0x2, walk 0x15/0x18, dash 0x1b,
backdash 0x1e, crouch_hold 0x28, crouch 0x3b, jump 0x7f/0x81/0x83, sidestep
0x11b/0x11d/0x11f/0x121, hit 0x9a2, hit_launch 0x9fc, block 0xa85/0xa91, ko 0xd66,
win 0xd67-0xd6a — taken from the existing banks' clip provenance + GLB extras,
identical across jin/bryan/king/xiaoyu/yoshimitsu/gunjack) + light/medium/heavy/grab
from Step 3. Output: lab/game/assets/t3_<char>_t3real.glb.

PROOF (Paul, run first, 2026-10-20): 29/29 clips baked, zero MISSING. Common-bank
clips match Jin's bank frame counts exactly (hit 21, hit_launch 25, block 15,
ko 40, jumps 25, sidesteps 8, walk 10/11, stance 75) — the universal slot map
resolves identically on Paul's bank. Paul's stance has 75/75 unique LeftArm
frames and shares 0 identical frames with Jin's stance (no cross-character leakage).

## Step 6 — re-encode to wh-anim/1 (pp-scratch/reencode.py)

The audit's GLB->JSON re-encode tool is not in the repo; rewritten here to mirror
the existing banks' schema EXACTLY (verified field-by-field against
game/assets/anim/t3/jin/*.json): format wh-anim/1, provenance fields (bank path,
slot hex or null for attack clips, move_row or null when common-flagged >= 0x40000000,
stream_frames = stored rot frame count, fps 30.0, decoder/tool strings,
source_glb + its sha256, hand_keyed false), bones = the 22 T3_BONES in order,
rot_xyzw rounded to 6dp, root_t + root_t_note + stream_frames_note verbatim.
t3_grab.json is a byte copy of t3_heavy.json after re-encode (same convention as
the existing banks) — NOTE: reencode.py writes grab from its own GLB animation
(same slot as heavy), which produces identical content by construction.


## WIRING MAP (for the coordinator's t3anims.js / fighter.js integration)

Sources read: game/js/fighter.js MOVESET_MAP + bankIdFor(), game/js/t3anims.js
SOURCE_TO_BANK / T3_BANKS, and every game/assets/movesets/*.json `t3_source`
(bankIdFor prefers the per-fighter JSON's t3_source, MOVESET_MAP is the fallback).
This lane did NOT edit game/js/* — wiring changes below are recommendations with evidence.

### heihachi bank (NEW — replaces the `heihachi: null` dead end)
Fighters whose t3_source is 'heihachi' (per-fighter JSONs): deathfang, diablo, dio,
iori, koreshi, sf-akuma, sunra, tou, zen. (MOVESET_MAP lists the same set: tou, zen,
diablo, dio, iori, deathfang, koreshi.) Today SOURCE_TO_BANK['heihachi'] = null, so
all of them get NO T3 actions. Once T3_BANKS.heihachi + SOURCE_TO_BANK heihachi ->
'heihachi' are wired, they split by rig (coordinator-verified):
- Bind directly (shared Mixamo bases): tou, zen, diablo (+ sf-akuma, sunra if their
  models are the shared bases — not verified by this lane).
- Foreign Bip001-style rigs, bank will not bind by bone name (remap lane's class):
  iori, deathfang (0/21 T3 bone names, 59 embedded clips each).
- Foreign rig, no embedded clips: dio. Unrigged static model: koreshi (rigging lane).

### bosconovitch bank (NEW) — the doc-frank question
Evidence FOR replacing the `bosconovitch -> gunjack` fixup with the real bank:
- docfrank's per-fighter moveset (game/assets/movesets/doc-frank.json) has
  t3_source: 'bosconovitch' — his frame data was built from Bosconovitch's actual
  extracted moveset. t3anims.js's own header rule: "a fighter must never be animated
  with a different character's clips" / "plays ONLY their own moveset source's bank".
  The gunjack fixup was a stand-in while no bosconovitch bank existed; it now does.
- The real divmot18 bank is verified genuine (SHA-256 matches n0madic's original-disc
  index) and produced a full 29-clip bank through the identical pipeline.
Scope note: only the base 'docfrank' fighter carries the bosconovitch JSON. The
doc-frank-* variants (machine-shop, wowomomo, hood) fall back to MOVESET_MAP =
'gunjack' and keep the gunjack bank unless the coordinator re-points them too —
that is a per-fighter moveset decision, not a SOURCE_TO_BANK one.

### armorking bank (NEW) — the armor-king question
- armor-king's t3_source is 'king' in BOTH his per-fighter JSON and MOVESET_MAP, so
  today he plays the 'king' bank = King motion retargeted onto the pantera_leoman
  rig (game/assets/anim/t3/king_on_pantera_leoman/).
- The new 'armorking' bank is the SAME divmot03_king motion baked on King's OWN
  rig — same moves, King-proportioned skeleton timings, no pantera retarget swing.
- SOURCE_TO_BANK is keyed by moveset source, not by fighter, so giving armor-king
  this bank needs a fighter-level override in bankIdFor (or a distinct t3_source
  for armor-king). Evidence for doing it: his model is King-proportioned, not
  Pantera-proportioned; the pantera retarget was built for Pantera. Evidence
  against / caution: it changes a currently-working fighter's animation set, and
  per the per-character isolation law the change should be deliberate and
  owner/coordinator-approved, not a side effect of this extraction. Recommendation:
  wire it as an explicit armor-king override, leave 'king' source fighters
  (pantera, yukihyo, zangief, kronos, hugo, kutz, marduk, ryuji-rock, sf-zangief)
  on king_on_pantera_leoman untouched.

### Banks with no current consumers
lei, paul, eddy, hwoarang, nina, anna, julia: no fighter's t3_source or MOVESET_MAP
entry names them today. The banks are complete and validated, ready for future
fighters/moveset expansion. (Not a gap in this extraction — a roster fact.)
mokujin: no bank (divmot absent from the disc image, see Step 1); no fighter
references mokujin as a source either.

### Naming
Bank keys follow the task spec and the existing convention (lowercase T3 character
names, cf. jin/bryan/gunjack): lei, paul, eddy, hwoarang, nina, anna, julia,
bosconovitch, heihachi — plus 'armorking' (the fighter id in the roster is
'armor-king' with a hyphen; the bank key drops it, matching how 'gunjack' is
one word). GLBs: lab/game/assets/t3_<key>_t3real.glb for all 10 produced banks.

## Results (2026-10-20, all verified on disk)

- divmot bins: 8 NEW in teardown/tekken3/animations/ (paul, lei, nina, hwoarang,
  eddy, julia, anna, bosconovitch) — SHA-256 verified against n0madic's index.
  Mokujin: absent from this disc image (Step 1 evidence). Heihachi's divmot13
  already existed.
- GLBs: 10 NEW in lab/game/assets/ — t3_{paul,lei,nina,hwoarang,eddy,julia,anna,
  bosconovitch,heihachi,armorking}_t3real.glb. (No .import sidecars were created;
  the existing GLBs have Godot .import files — regenerate on the coordinator's
  side if that pipeline needs them.)
- Banks: 10 NEW dirs in game/assets/anim/t3/<key>/, 29 clips each, 290 clips total.
  Every bake reported 0 MISSING clips; every bank passes the validator
  (pp-scratch/validate.mjs: the game's own jsonToClip run in node with a THREE
  stub) — 29 OK / 0 FAIL per bank, 22 quaternion tracks per clip, all quaternions
  unit-norm within 0.02, bones list identical to the existing banks incl. Chest.
- t3_grab.json is byte-identical to t3_heavy.json in every new bank (md5-checked),
  matching the existing banks' convention.

### Attack picks (move rows; slots = move_index inversion)
heihachi 38/64/182 and armorking 35/63/230 from game/assets/{heihachi,king}_moves.json.
Class-profile rule: paul 128 (dmg12,s44) / 101 (25,s61) / 191 (33,s60);
lei 134 (12,44) / 178 (21,60) / 211 (35,68); nina 132 (12,44) / 100 (25,59) / 231 (30,66);
hwoarang 110 (12,44) / 86 (25,59) / 124 (40,100); eddy 119 (12,44) / 86 (25,61) / 139 (40,173);
julia 118 (12,44) / 58 (25,62) / 82 (35,100); anna 113 (12,44) / 85 (25,59) / 378 (35,65);
bosconovitch 98 (12,44) / 153 (25,60) / 137 (37,67). (s = stream_frames @60fps.)

### Quality notes / suspect items (with evidence)
- Bosconovitch win clips: slots 0xd67-0xd6a ALL resolve to move_row 639 (stream
  192) in his own bank's move_index — his four win files are identical content.
  This is what the source data contains (one win animation), not a pipeline
  error: bake report + re-encode agree, RMS is the best of all banks (<= 0.34).
- Bosconovitch dash_fwd = 10 stored frames (others 15) and crouch = 19 (others 5):
  his own bank's streams at the universal slots really are those lengths.
- Eddy heavy (row 139) is a long capoeira string: 173 stream frames (~86 stored).
  Real motion, right damage class; flagged in case the game wants a shorter heavy.
- Heihachi bake used the pivot-override path (Step 4). His stance Kabsch RMS
  0.054-0.563 T3 units — same range as Jin's existing bank (0.019-1.056). No bone
  flips observed: validator quat norms all pass and stance frame counts match the
  universal pattern (75/75/75 stance family except stance_b 30, his own stream).
- Nina stance_c = 76 stored frames (others 75): her slot-2 stream is 151 @60fps.
- Frame-count cross-check vs Jin's bank on all common-bank clips (hit 21,
  hit_launch 25, block 15/15, ko 40, jumps 25, sidesteps 8, walk 10/11,
  crouch_hold 35): identical in ALL 10 new banks — the universal slot map and the
  common-bank resolution behave identically on every character's bank.

### Reproducibility
Drivers live in ~/workspace/_wh-work/pp-scratch/ (make_stance.py, make_movesets.py,
chain_pivots.py, picks.py, bake_driver.py, reencode.py, validate.mjs, batch.sh,
bake_*.log, batch.log). Per-character bake command:
`T3REMAKE_RESEARCH=~/workspace/tools/tekken3remake/tools/research python3
pp-scratch/bake_driver.py <char>` (heihachi also needs
`T3_PIVOT_OVERRIDE=pp-scratch/heihachi_pivots.json`), then
`python3 pp-scratch/reencode.py <char> teardown/tekken3/animations/<divmot file>`,
then `node pp-scratch/validate.mjs game/assets/anim/t3/<char>`.
No game/js files were edited by this lane; nothing was committed.
