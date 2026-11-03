# Job 1 + Job 3 evidence (final-three remainders lane, 2026-11-03)

## JOB 2 METHOD CORRECTION (2026-11-03, discovered mid-lane — read first)
The game boots into an ATTRACT fight (zen vs pantera) before any ?quick= fight starts;
zen's models/forms preload every session for that reason. The probe's first ready-check
(roundState==='fight' only) could latch onto the attract fight. A diagnostic session
(diag.py) proved it: ?quick=menajerii,pantera,shrine showed p1id='zen', p2id='pantera',
roundState 'fight' at 51 s, and vixen's GLB was never requested. Consequences:
- menajerii run-1 verdict (t3actions 0, all TPOSE) measured ZEN, not menajerii — RETRACTED
  (file kept as menajerii-verdict-INVALID-attract-zen.json for the audit trail).
- pond run-1 verdict stands: that session fetched tsuyu's GLB and its own console logged
  "[WH-THROW] pond vs pantera: no file pair (no T3 bank for pond (UNMAPPED))" — p1 was pond.
- ryusan/megami run-1 "never ready" was the attract fight itself stalling: the serve tree
  (everything-else build-out copy) lacked roster/zen entirely, so the attract P1's model
  404-looped. Fixed in the serve tree only (zen attire1 + oversoul/tentacle/spirit
  model-rigged.glb pulled from main, sizes exact) — no repo files touched.
- Probe fixed: ready now requires g.p1.char.id === <fighter> AND roundState==='fight';
  setup records p1id/p2id. All four fighters re-run under the fixed probe (run 2).

## JOB 1 — Menajerii Roger Jr. motion bank: GAP (does not exist in an extractable form anywhere checked)

Current in-game wiring (verified by direct reads of main, 2026-11-03):
- game/js/fighter.js FIGHTER_BANK: menajerii: 'kuma' (a 2026-10-23 design-time stand-in from the
  T3 Kuma bank; chatur: 'ogre', tobi: 'hwoarang' likewise). Her moveset game/assets/movesets/
  menajerii.json (193 moves) carries 19 anim_refs of kind ttt2:rog:row:N into
  game/assets/ttt2/movesets/rog.json (Roger Jr. TTT2 move DATA table — frame data, not clips).
- docs/anim/TTT2-ROGER-ANIM-GAP-20261023.md (in-repo, 2026-10-23) already records the target:
  game/assets/anim/ttt2/roger/ registered in t3anims.js T3_BANKS + SOURCE_TO_BANK — never built.

What was searched (2026-11-03, this lane):
- GRE (mhvnsnt/game-reverse-engineering) teardown/tekken-tag-tournament-2/ subtree, direct API
  listing: ONLY HEADER-LISTING.txt + tools/god_surgical.py + stfs_blobs.py + xdvdfs_reader.py.
  No extracted banks, no Roger files. (GRE full recursive tree grep for 'roger': 0 hits.)
- GRE tekken6/extracted/: DATA401.IDX + DINF_400.BIN only (PSP index files, no motion).
  GRE tekken5/: data = name_tables.json + roster.json; archives = catalog JSONs only.
  No roger/mota/motion hits anywhere in tekken5/tekken6 subtrees.
- Local TTT2 decodes: data001 (851,749,584 B at ~/workspace/_ttt2-work/data001.bin) contains
  669 NTXR textures, 0 MOTA. data028 (120,285,856 B) contains 0 MOTA / 0 NTXR (audio bank
  container). Per docs/teardown/ttt2/DATA001-DATA028-DECODE-20261030.md: data001 = Binaries
  (player BIN/CAS/MDL), data028 = Sound.
- The ONLY TTT2 MOTA-bearing container identified is data004.bin (the character moveset table,
  4,075,114 B compressed, sha256 d8c73be427171538…, LZX-decoded 6,522,032 B, MOTA magic x21) —
  per docs/teardown/ttt2/TTT2-STATUS.md and DATANNN-MAP-20261025.md. The decoded copy is NOT on
  local disk (the _ttt2-work archive holds extracted ntxr/nus3 only); it is reproducible from
  release ttt2-7z-v1 (27 assets, 13,529,225,673 B) via in-repo tools
  teardown/tekken-tag-tournament-2/tools/lzx-decode/ and tools/ttt2-section-decode/.
- 33 of the 42 dataNNN inner files were never pulled (disk-gated, DATANNN-MAP); per-character
  packages are expected there. Release ttt2-loose-files.tar (165,601,280 B, downloaded complete
  this lane) contains only extraction logs, tools and one pak chunk — no data004, no motion.
- Tooling reality: no TTT2 MOTA parser exists in WH or GRE tooling (TTT2-STATUS: "data004 MOTA
  parse: not built"); the engine has no TTT2 clip bank/loader path at all (banks are T3-format
  via game/js/t3anims.js). Jun (megami, §everything-else Step 1) is blocked by the same class.

Verdict: Roger Jr.'s motion exists only undecoded inside TTT2 containers. Producing her bank
requires (i) pulling + LZX-decoding the right dataNNN/data004, (ii) reverse-engineering the
TTT2 MOTA format into a parser, (iii) a MOTA→wh-anim/1 converter + engine bank wiring. That is
the dedicated TTT2 motion lane (research-scale), not a wiring fix. Per the brief: logged gap,
no substitute motion wired. Her file keeps the 2026-10-23 'kuma' stand-in binding and the
ttt2:rog move DATA — both pre-existing owner-era state, untouched by this lane.

## JOB 3 — Megami outfit materials: GAP (no outfit textures exist in her own data); brief's
## transmission/clearcoat hypothesis REFUTED by her material data.

Loaded file: roster/parvati/attires/attire1/model-rigged.glb (main blob b79bda9260).
Source: intake parvati-full.glb, 191,604,148 B, release megami-menajerii-smutbase-20261023
(downloaded complete this lane, sha-checked against GLB declared length; copy kept in lane
scratch megami-src/).

Findings (GLB JSON dumps + in-engine isolation renders via the visual-gate viewer):
1. Transmission/clearcoat extensions exist ONLY on the eye micro-materials (EyeMoisture-3,
   Cornea-2, EyeMoisture-4 — same in source and packed) and render correctly. The outfit
   materials carry NO extensions at all.
2. The visible "outfit" = Marvelous-Designer-style shells: 24_Material43_0.25_0_0 (7,133 tris
   over 5 meshes in the packed file; full outfit shell incl. helmet ring, shoulder pads, torso
   armor, belt+pouches, pants, knee pads, boots — proven by isolation render
   visual-gate site meshprobe output) and 25_Material40_1_0_0 (7,025 tris; headpiece/collar).
   In the packed file these prims have NEITHER TEXCOORD_0 NOR COLOR_0 (attributes: JOINTS_0,
   NORMAL, POSITION, WEIGHTS_0 only) and their materials are bare: no textures, no
   baseColorFactor → PBR defaults (white, metallic 0, roughness 1) → flat light gray is the
   only possible render.
3. The INTAKE SOURCE is the same: 24_/25_ materials are literally `"pbrMetallicRoughness": {}`
   (25_Material40 adds alphaMode BLEND), no textures, and their COLOR_0 is placeholder white
   (1,1,1) on 100% of sampled vertices (meshes 3, 5, 22). UVs exist in the source (U 0..1,
   V −2..−1, an MD tile offset) but there is no texture to sample: all 66 source images were
   inventoried; NONE belongs to the outfit materials (outfit-ish name scan: 0 hits). The rig
   rebuild's loss of the outfit UVs/COLOR_0 is therefore immaterial — there was never anything
   to show.
4. The black splotches = the Bodystocking-2 under-layer (baseColorFactor [0,0,0,1], dark
   stocking texture, UV'd) breaching between the outfit shells (same shell-breach family as
   Menajerii's decimation shards) plus unlit double-sided fabric undersides. Pre-existing in
   the source data; A/B at the visual gate already proved the pre-pack original identical.
5. What IS textured in her data renders textured: DAZ lingerie set (top-1/bottom-1/STopMain/
   garter etc., near-black lace by design, hidden UNDER the MD shells), Face-2/Legs-2/Arms-3/
   Torso-3 skin maps (tex47/52/44), DM04 gauntlets (full YF02_02 PBR set), hair cap. Torso-6
   (metallic 0.9 / roughness 0.2, no maps, no UVs) is the RenderStrandHairGeom material in the
   source (368k tris; 208k after decimation, collapsed around the neck/head) — hair, not outfit.
6. roster/parvati/PARTS.md already lists the 24_/25_ meshes as "Unresolved (verify in Blender)";
   CANON.md's "every piece of her dress is armor" matches the MD tactical set's look.

Verdict: there are no real outfit textures in Megami's own data to restore — the tactical
outfit was delivered untextured (bare MD fabric, placeholder white vertex colors) in the
original commission export. A faithful fix requires the outfit's texture set from the original
commission source, which is not in the intake. Per the rules (no invented textures, no hand
recoloring), this is a logged GAP, not a fixable wiring defect. The material definitions in
the shipped file faithfully reproduce the source; nothing was changed.
