# WMXIX extraction — W6 lane (2026-11-19)

Source ISO: **WWE WrestleMania XIX (USA), GameCube, GW9E78**,
1,459,978,240 bytes, SHA1 `4746c3b9de58f43d1a5c803ed0c3adba628ee861`,
MD5 `c13c47a5ed24a675545c99a15e44529d`. Provenance: archive.org item
`GameCube-Redump-2024-Individual-Games-Part2`, file
`WWE WrestleMania XIX (USA).zip` (SHA1
`abd3cda81d9b15b2fbf4d5a619cdaabf65dcca1c`, verified), which contained an
RVZ converted to ISO with Dolphin 2609b `dolphin-tool convert -f iso`
(the raw-ISO hashes match the `gamecubecollectionbyblopez` metadata
exactly). FST: 4,222 files. The ISO itself is NOT in this repo (it stays
on the Oracle VM); only extracted data is committed here.

Tools: `teardown/wmxix/tools/w6_extract.py` (driver),
`w6_decode2.py` (CAW YOBJ decoder v2), `w6_arena.py` (arena facing),
`w6_hhh.py` (Triple H re-triangulation), `w6_contact.py` (face contact
sheets). Run on the Oracle VM against `/data/wmxix/wmxix-rvz.iso`.

## What was extracted

| Data | Location here | Counts |
|---|---|---|
| CAW meshes (`.ymg` → OBJ) | `caw-parts/meshes/` | 1,141 OBJs (1,128 ok + 13 pool-scan), 287,044 verts, 220,321 tris; manifest `caw-mesh-manifest.json` |
| CAW textures (`.tex` → PNG) | `caw-parts/textures/` | 5,613 PNGs from 1,469 `.tex` files, 0 errors; manifest `caw-tex-manifest.json` |
| Wrestler textures | `wrestlers/<slot>/tex/<variant>/` | 3,797 PNGs from 162 `.tex` files (77 slots), 0 errors; manifest `wrestlers/wrestler-tex-manifest.json` |
| Gameplay clips (`move.mpc` → JSON) | `animations/mpc/` | 1,900 clips decoded + 5 stubs, 0 failures, of 1,905; manifest `mpc-clips-manifest.json` |
| Arena faces | `arenas/faced/` | 35 OBJs, 2,087 faces total (PARTIAL coverage, see below) |
| Triple H re-triangulation | `wrestlers/000/triple-h-000_*.obj` | 606v / 383f each attire; see `wrestlers/000/TRIPLE-H-RETRIANGULATION.md` |
| Face contact sheets | `wrestlers/face-contact/` | 3 sheets, 77 slots (73 with faces); `slot-index.json` |

## Decoder notes (measured, not assumed)

- **CAW `.tex` TPL magic variant:** entries use `0x0120AF30` as well as
  standard `0x0020AF30`. Accept `(word & 0x00FFFFFF) == 0x0020AF30` and
  normalize before parsing. A few entries declare image data past the
  container's stated size — retry with the TPL read to end-of-file.
- **CAW YOBJ v3.0001 (754 files):** single vertex run starting just past
  the skin batch table. The wrestler batch-table heuristic does NOT fit
  CAW parts (proven on the elbow: the table points at 18 verts, the real
  run is 148). The pool-scan fallback is WRONG for CAW parts (it
  returned 160 verts of which only 18 overlapped the proven set).
- **CAW YOBJ v4:** batch-table path first, run path as fallback.
- **DUMY files are NOT all empty:** 170 of 202 DUMY files decode to real
  geometry (27,827 verts) after stripping the 0x18-byte wrapper. The
  catalog claim "202 DUMY placeholders (no geometry)" is wrong for 170
  of them; 43 are truly empty (incl. an 84-byte degenerate file).
- **59 NO-GEOMETRY files, all Gears accessories:** verified empty or
  garbage by brute-force scan (zero-filled vertex regions, or scattered
  non-mesh data with cubic bboxes) — not a decoder miss. 13 files are
  marked `pool-scan` in the manifest (fallback quality, flagged).
- **MPC clips:** file offset = `0x8240 + data_offset` (data_start
  0x8240, 870 motions, 1,905 clips per `WMXIX-MPC-INDEX.json`). YANM
  decode is a bytes-based variant of `extract_yanm.decode_yag` (29
  tracks). **Durations are NOT calibrated** — `est_seconds` in the
  manifest uses each clip's `sec_per_tick` (0.159 for `.mpc` clips vs
  0.041 for ringmotion), giving a median of ~94 s, which is not a real
  move length. Do not use `est_seconds`; use raw tick counts. The 5
  stubs (`1500_00C`–`1506_00C`) are valid YANM headers too small for the
  29-track directory (192–448 bytes).
- **Arena facing is PARTIAL (1–19% coverage):** method A (20-byte index
  records, cracked 2026-10-13) + method B (geometrically validated
  plain-u16 index runs, global and per-array). The bulk face data lives
  in a format neither method catches (likely GX display lists
  interleaved with vertex-attribute streams — `808080ff` color data,
  chained records). `ring.ymg` is DUMY-wrapped (strip 0x18 to reach
  the YOBJ). Best coverage: `f01.ymg` 19.1%. The faced OBJs ship as
  partial-but-real; a Poisson/Open3D reconstruction fallback was NOT
  applied (it would fabricate geometry).
- **Wrestler→motion assignment table: NOT found.** Static trail
  exhausted (see `WMXIX-MPC-ASSIGNMENT-DECODE-2026-10-21.md`): `wprm`
  is move-keyed, not wrestler-keyed; `menu.mpq` profile blocks are
  names + slot labels only (no motion IDs — verified 2026-11-19 by
  dumping the bytes around Rock Bottom et al.); `move.mpc` has no name
  strings. The specified crack is Dolphin runtime observation
  (breakpoints 0x800364F0 / 0x8007609C / 0x80075FB8). Dolphin 2609b
  boots and runs the game headless under Xvfb on the Oracle VM
  (verified 2026-11-19: legal screen, WWE/Yuke's logos, intro video;
  single-core `CPUThread=False`; debugger pane opens with `-d`). The
  GDB stub is compiled into the flatpak binary but does not listen by
  default, and its toggle lives in the Debug menu that Dolphin's Qt UI
  is missing (known bug #11188). Full observation needs a follow-up
  lane: a way to start the stub (or GUI breakpoint use) plus TAS input
  (`.dtm`) driving the game to a match and performing each special.
- **99 specials: names only, still.** No animation clip is identified
  for any special; identification needs the assignment table (above).

## Slot identities (texture-name evidence — Mars to confirm)

Slot 000 = Triple H (confirmed 2026-10-15, `hhh_` textures). All other
slots are UNNAMED in the repo. The extraction surfaced texture-name
hints (same kind of evidence as `hhh_`): 001 `rock`, 005 `kurt`,
006 `booker`, 007 `rvd`, 009 `edge`, 012 `jeri`, 015 `kan`,
019 `big` (**Big Show lead — needs Mars's eye**), 023 `flair`,
028 `bat`, 044 `lce` (Lance), 045 `rik`/`rikisi`, 090 `rock`
(alt?), 003 `hg`/`nwo`, 004 `teiker`. Slots 047–059, 002, 110 reuse
`hhh_` textures (CAW templates / HHH variants?). These are HINTS, not
confirmed identities — see the face contact sheets
(`wrestlers/face-contact/`) for visual confirmation.
