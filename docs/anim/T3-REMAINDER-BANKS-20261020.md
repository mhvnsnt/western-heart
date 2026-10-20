# Tekken 3 Bank Remainder — 3-Way Diff, Extraction Record, Wiring (2026-10-20)

Lane: T3 bank remainder (personality-pass recovery lane 3).
Everything below is REAL decoded Tekken 3 motion from the owner's disc
teardown — no hand-keyed, procedural, or cross-character filler motion.

## 1. Three-way diff (game banks, `game/assets/anim/t3/`)

| Bank | main | PR #382 branch (`tekken3-wiring-20261020`) | This PR |
|---|---|---|---|
| bryan, gunjack, jin, king_on_pantera_leoman, xiaoyu, yoshimitsu | yes (6) | yes (same 6) | unchanged |
| paul, lei, nina, hwoarang, eddy, julia, anna, bosconovitch | **no** | **no** (divmot sources only) | **NEW** |
| heihachi | **no** | **no** (divmot13 already on main) | **NEW** |
| armorking | **no** | **no** | **NEW** (divmot03_king on King's own rig) |
| mokujin | **no** | **no** | **BLOCKED — see §4** |

PR #382 adds NO game banks: its 47 files are divmot bins + movesets +
inventory docs in `teardown/tekken3/`. The needed set (lei, paul, eddy,
hwoarang, nina, anna, julia, mokujin, bosconovitch, armor-king,
heihachi) was missing as playable banks from BOTH main and #382.
Gap after this PR: mokujin only (evidenced blocker, §4).

## 2. Extraction pipeline (identical to the 6 existing banks)

`TEKKEN3.BNS` → divmot bank (BNS table: byte_offset = sector × 2048,
per `teardown/tekken3/docs/BNS-ORGANIZATION-PATTERN.md`; identity =
size + SHA-256 vs the n0madic original-disc index) →
`teardown/tekken3/tools/local/pose_assemble.py` + `usa_motion.py` decode →
`lab/tools/t3_motion_bake.py` bake onto the character's own
WH-Canonical-22 GLB → GLB → wh-anim/1 JSON re-encode (schema verified
field-by-field against `game/assets/anim/t3/jin/*.json`).

Extraction was executed by the personality-pass lane in its worktree
(full log: `docs/personality-pass/EXTRACTION-LOG.md` in that lane's
pending work); this lane independently re-validated every file before
shipping (see §5) and did the wiring (§3).

Divmot sources shipped in this PR (byte-identical to PR #382's copies,
so the two PRs merge cleanly in either order):

| divmot | char | BNS id | bytes | sha256 prefix |
|---|---|---:|---:|---|
| divmot00_paul.bin | Paul | 280 | 313,472 | 06f6447a |
| divmot02_lei.bin | Lei | 282 | 318,524 | bd795779 |
| divmot05_nina.bin | Nina | 285 | 333,384 | 50430e78 |
| divmot06_hwoarang.bin | Hwoarang | 286 | 312,268 | d0b5b43a |
| divmot08_eddy.bin | Eddy | 288 | 336,652 | 0383ddb2 |
| divmot10_julia.bin | Julia | 290 | 267,924 | d4c8ce91 |
| divmot17_anna.bin | Anna | 297 | 314,684 | 16886320 |
| divmot18_bosconovitch.bin | Bosconovitch | 298 | 332,372 | 130ee660 |

Heihachi's divmot13 (268,796 B) was already on main. Armor King's bank
uses divmot03_king (already on main).

Per bank: 29 wh-anim/1 clips (the 25 universal slots + light/medium/
heavy/grab picks), including all 14 files `T3_CLIP_DEFS` requires.
`t3_grab.json` is byte-identical to `t3_heavy.json` in every bank —
the same convention as the 6 existing banks. Attack picks: heihachi
rows 38/64/182 and armorking rows 35/63/230 from
`game/assets/{heihachi,king}_moves.json`; the 8 new characters use the
documented class-profile rule fitted to the 7 known banks (full picks
table in the extraction log).

Known source-data quirks (not pipeline errors): Bosconovitch's four
win slots all resolve to his single win animation (move_row 639);
his dash_fwd (10 stored frames) and crouch (19) differ from the cast
norm because his own bank's streams do; Eddy's heavy (row 139) is a
long capoeira string (173 stream frames); Nina's stance_c is 76 stored
frames (her slot-2 stream is 151 @60fps).

## 3. Wiring (this PR)

`game/js/t3anims.js`:
- `T3_BANKS` += paul, lei, nina, hwoarang, eddy, julia, anna,
  bosconovitch, heihachi, armorking.
- `SOURCE_TO_BANK`: `bosconovitch -> bosconovitch` REPLACES the
  `bosconovitch -> gunjack` fixup (docfrank's frame data was built
  from Bosconovitch's real extracted moveset; the gunjack stand-in is
  retired). `heihachi -> heihachi` REPLACES `heihachi: null` — the 9
  heihachi-source fighters (deathfang, diablo, dio, iori, koreshi,
  sf-akuma, sunra, tou, zen) now get Heihachi's own clips instead of
  no T3 actions. Direct entries added for paul/lei/nina/hwoarang/
  eddy/julia/anna (no current fighter consumers — banks ready for
  future moveset expansion) and `armorking` / `armor-king`.

`game/js/fighter.js` (`bankIdFor`): explicit `armor-king -> 'armorking'`
override. His t3_source is 'king', but the 'king' bank is King motion
retargeted onto the pantera_leoman rig for Pantera; the armorking bank
is the same divmot03 motion baked on King's own rig, matching Armor
King's proportions. All other king-source fighters (pantera, yukihyo,
zangief, kronos, hugo, kutz, marduk, ryuji-rock, sf-zangief) keep
`king_on_pantera_leoman` untouched.

`game/js/main.js`: stale comment corrected (heihachi-source fighters
are no longer bank-less).

## 4. Mokujin — evidenced blocker (no bank fabricated)

1. BNS table entry **295 = (sector 17534, size 0)** — verified directly
   from `teardown/tekken3/bns-table.pkl` in this lane. Entry 296
   (Gun Jack) starts at the same sector 17534 with size 316,944.
2. A raw read at sector 17534 of the size the n0madic index lists for
   the original disc (127,368 B) yields header `00108701` — the start
   of Gun Jack's data, not a type-0x0f divmot.
3. No other `TEKKEN3.BNS` or `divmot15*` copy exists anywhere in the
   workspace (searched).
4. Mokujin's KMD model DOES exist locally (BNS 207, parses, 24,728 B) —
   only the motion bank is absent from this disc image. It exists on
   the original disc per the n0madic index (127,368 B, sha256
   5cead15f…): re-ripping that entry from a complete disc image
   unblocks the identical pipeline.
5. No fighter references mokujin as a t3_source (verified across all
   per-fighter moveset JSONs), so nothing in-game changes.

Per per-character isolation, no bank was fabricated from another
character's motion (Mokujin mimics the cast in-game, but shipping
another character's bank AS his would break provenance).

## 5. Heihachi — verdict: DECODED (previous blocker overcome)

The old blocker ("KMD lacks vertex data, raw divmot only") was real:
Heihachi's KMD rows for canonical parts 2 (pelvis), 9, 13 have ZERO
vertices (his mesh merges those parts into neighbours), and stock
`t3_to_gltf.py` / `t3_motion_bake.py` crash on `pivots[0] = pivots[2]`
(KeyError: 2). Fix used by the extraction lane (scratch copies of the
tools only; repo tools untouched): fill the missing pivots from the
pose chain itself — the world-matrix origins `pose_assemble.py`
computes for slot 0 frame 75. Proven equivalent on King, where both
exist: chain origin vs Kabsch pivot differ by ≤ 1.6 T3 units
(~1.6 mm) across all 17 parts. Override values (T3 units): part 2
[-82, -1118, 136], part 9 [22.842, -1458.627, 205.407], part 13
[-175.254, -1466.342, 178.552]. Result: full 29-clip bank, stance
Kabsch RMS 0.054–0.563 (Jin's existing bank: 0.019–1.056), all
validation green (§6).

## 6. Verification (this lane, independent of the extraction lane)

- All 16 banks (6 existing + 10 new): every `T3_CLIP_DEFS` file
  present (14/14 per bank), `format == 'wh-anim/1'`, bones ==
  the 22 `T3_BONES` exactly, per-bone frame counts equal and > 0,
  quaternion norms within 0.02 of unit (first/mid/last frame, all
  bones), `hand_keyed == false`, JSON key set identical to jin's.
- Loader simulation through the game's own `jsonToClip` logic (node,
  THREE stub): 14/14 clips build per new bank, 22 quaternion tracks
  per clip.
- No cross-character leakage: all 16 banks' `t3_stance.json` SHA-256
  values are pairwise distinct; common-slot frame counts match Jin's
  bank across all new banks (hit 21, hit_launch 25, block 15, ko 40,
  jumps 25, sidesteps 8, walk 10/11, crouch_hold 35).
- `node --check` passes on the edited JS (as ES modules).
