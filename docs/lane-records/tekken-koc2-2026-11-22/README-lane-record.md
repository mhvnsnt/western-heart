# Bannon — Tekken + KoC2 moves (Coordinator lane 3/4)

- Date: 2026-11-22/23 EST. Owner order 2026-11-22.
- Lane: Tekken (Tekken 3 / Tekken 7 / Tekken 5 Devil Within) + KoC2.
- Rules applied: pull already-decoded versions first; verify, do NOT
  re-decode; pair every Tekken clip with a receiver + restore root
  travel; wire into the moveset library; prove each move in a REAL
  match on Finn / Big Cass / Elias / Enzo with stills AND MP4s,
  eye-checked vs source; do NOT fake clips, do NOT fake live.
- Headline, stated honestly: **0 Tekken moves and 0 KoC2 moves play
  in a real match. 0 stills, 0 MP4s.** No match proof was produced
  because no clip passes the seam gates — producing stills/MP4s would
  have meant inventing a match. What this lane DID deliver: a per-clip
  pairing audit of all 383 Tekken clips (manifest-grounded, nothing
  invented), a headless seam-gate check (0/383 playable, with the exact
  failing gate per clip), a refusal wiring brick (14/14 headless tests
  pass), and new KoC2 Route A disassembly (three loader functions +
  the "KOC2"-stamped allocator finding). Show directory:
  `~/workspace/bannon-all-moves-all-games-show/tekken-koc2/`.

## 0. Scoreboard

| Game | Clips in repo / decoded | Wired to library | Plays in a real match |
|---|---|---|---|
| Tekken 3 | 230 clips, PARTIAL | 0 | 0 |
| Tekken 7 | 96 clips, PARTIAL | 0 | 0 |
| Tekken 5 Devil Within | 54 clips, PARTIAL | 0 | 0 |
| Western Heart MADE | 3 adaptations (not decoded motion) | 0 | 0 |
| **Tekken total** | **383 clips, PARTIAL, 0 FULL** | **0** | **0** |
| KoC2 | **0 decoded** (16,660 MVS, bitstream uncracked) | 0 | 0 |

## 1. Tekken — what exists (re-verified live this lane)

### 1a. Counts (fresh this lane, GitHub connector, Bannon main)

- `assets/moves/ik/tekken/manifest.json` (SHA
  `d5eca46bff5d576e0528c9aee1d2d2290207f9ac`, generated 2026-11-19,
  lane K3): **383 clips — T3 230 / T7 96 / T5DW 54 / MADE 3**.
  Coverage **full 0 / partial 383 / gap 0**. Mapped named Bannon
  library moves: **0**.
- Move classes (totals only — per-clip move_class is NOT in the
  manifest and is not asserted per clip anywhere in this lane):
  signature 4 / strike 136 / throw 27 / mixed 63 / none 151 /
  special 2.
- Throw clips named: **18** (all `T3_KING_R*`). Note: 18 named throw
  clips ≠ 27 move-class throw — 9 throw-classified moves share clips
  or are classified without a named throw-clip entry. Do not force
  the numbers to match.
- Registry moves in scope: **1,002** (916 with clip, 86 without:
  82 Tekken 8 data-only — western-heart holds T8 clip-MAPS only, no
  T8 clip data packs — + 4 western-heart originals unauthored:
  Pantera Claw Driver, Pantera's Hunt, Yukihyo Storm Shadow's
  Lesson, Yukihyo Whiteout).
- Truncated before contact: **14 clips** (end before their registry
  first active frame; no contact keyframe; full motion lives in the
  western-heart source pack row). Spike exceptions: **5**. Non-wrestling
  (beam effects): **5**.
- Batch size per `tools/tekken/README.md`: 383 clips, ~17.2 MB,
  25,239 frames. Converter gates T1–T5 all PASS 2026-11-19.
  Handedness VERIFIED with labelled ground truth (Tekken 1 = left
  punch, 2 = right punch): LP clip moves haL +0.505 m forward vs
  haR +0.055; RP moves haR +0.507 vs haL +0.147.

### 1b. Sampled IK files — the exact shape of PARTIAL (read this lane)

Three IK files fetched read-only from Bannon main and parsed:

| File | Source | dur / keys | Registry moves | Receiver | Reaction | Root travel | Library move | Coverage |
|---|---|---|---|---|---|---|---|---|
| `T3_KING_R127` | tekken3 | 0.3167 s / 19 keys, 59.9 fps | 4 (damage 21, slot `grapple_front_heavy`, active frame 26) | null | null | null | null | partial |
| `T7_KING_mokg_tkr_DVD` | tekken7 | 0.9 s / 54 keys | 2 | null | null | null | null | partial |
| `T5DW_PANTERA_ikdv_36_nage_y` | tekken5_dw | 2.1167 s / 127 keys | 1 | null | null | null | null | partial |

- R127 in full: pelvis start `[0, 0.8755, 0]` → end `[0, 0.6875, 0]`
  — root x/z are exactly 0.0 throughout (the dropped travel, visible
  in the data itself). `contact_beyond_clip`: first active frame 26,
  contact at 0.4333 s, clip's last key at 0.3 s — the clip ends
  0.133 s BEFORE the hit lands. Quality flags: `upsampled` (slerp
  30→60 fps, pack is stride-2 of the 60 fps T3 stream) +
  `contact_beyond_clip`. Source row:
  western-heart `game/assets/anim/t3/king_on_pantera_leoman/rows.pack.json`
  row 127. Manifest entry bank: "Tekken 3 King (divmot03_king.bin)",
  "REAL decoded Tekken 3 motion (owner disc teardown)".
- The manifest + README state the same nulls for ALL 383; the three
  samples (one per bank) confirm the shape holds across banks. No
  clip JSON and no `.tkmvst` exists in this workspace (filename
  search clean this lane).

### 1c. Pairing audit — every clip, one verdict

`bannon-all-moves-all-games-show/tekken-koc2/pairing-audit.json`
(383 rows; built by `prep/build-pairing-audit.py` from the manifest;
assertions re-check the 230/96/54/3 split and every set size):

| Verdict | Clips | Meaning |
|---|---|---|
| `BLOCKED_NO_RECEIVER` | 361 | Solo-only attacker motion. Needs a receiver (AKI P1/P2 pair, WMXIX once identified, or authored reaction) + root restore. |
| `BLOCKED_TRUNCATED` | 14 | Ends before first active frame; no contact keyframe. Needs source-pack re-bake. (2 of the 14 are also named throw clips: R127, R148.) |
| `NOT_A_MOVE` | 5 | Beam effects, not wrestling moves. Nothing to pair. |
| `ADAPTATION` | 3 | MADE clips — adaptations of decoded T3 King motion, NOT decoded motion. Wire only labelled as adaptation. |

Pairing basis per row is the manifest set membership + the sampled
IK shape; no per-clip move_class, damage, or slot is asserted (not
in the manifest). The only receiver lead in the whole Tekken set is
attached to the T7 bank generally, not to a clip id: King `.tkmvst`
receiver move 554, found for both King throws (see §1e).

### 1d. Root-travel restore — exact spec (prep, not run)

- The travel EXISTS in the source and was dropped by converter v1:
  `tools/tekken/whanim_to_bannon.py` v1 does a direction retarget
  (source full per-bone local quaternions + root track → FK on the
  source rig → bone directions → re-FK on Bannon REST with Bannon
  bone lengths) and drops root x/z in the output. R127's own IK file
  states it: "Horizontal travel is NOT recoverable from the
  converted clip — it lives in the western-heart source pack root
  track."
- Restore job (converter v2, owed — not run here): carry the root
  track from the source pack into the Bannon clip (root x/z per key,
  same 60 fps grid), for all 383 clips. Source packs (western-heart
  public repo, fetch with `git cat-file` — the files are not in the
  sparse clones): `game/assets/anim/t3/king_on_pantera_leoman/rows.pack.json`
  + `hit_frames.json` (T3), `game/assets/anim/t7/king/moves.pack.json`
  (T7), `game/assets/anim/dw/moves.pantera.pack.json` (DW),
  `game/assets/anim/made/pantera/*.json` (MADE), movesets
  `game/assets/movesets/pantera.json` + `yukihyo.json`, T7 frame data
  `game/data/t7-frame-data/t7-king-lp-rp-lk-rk.json`. Re-run gates
  T1–T5 after the change; the 5 spike exceptions are documented in
  `tekken_manifest.json` and must still be excepted, not silently
  "fixed".
- Pairing job (owed): receiver halves from AKI P1/P2 pairs (the VPW2
  Superplex pattern: P1 40f / P2 45f, frame-aligned by convention,
  offset/hold decision at wiring time — do not silently stretch),
  WMXIX clips once W7 identifies them, or authored reactions. Tekken
  alone can never supply a receiver — that is a property of the
  source, not a gap in the audit.

### 1e. King `.tkmvst` — the only real T7 fighter extraction

- Re-verified live this lane (public GitHub API): run 44858568891 has
  exactly 1 artifact, `king-tkmvst`, id 14688676730, **14,386,774 B**,
  sha256 `613826d7530a513398704a68aa1922f935e221575c908ac5a328f2ada63cc8b3`,
  created 2026-11-21, **expires 2027-02-19T02:56:50Z, expired=False**.
  It lives ONLY as that artifact — not in the repo on main, not in a
  release. Anonymous zip download re-tested this lane: **401**.
  `gh` CLI is unauthenticated in this VM (`gh auth status`: not
  logged into any GitHub hosts); the GitHub connector has no
  artifact-download tool.
- File: `T7_King.tkmvst`, 15,773,258 B, header TKM21.0, **2,787 moves**
  (matching `graph.json` exactly), CRC32 ok. **4 of 10 throw clips
  validate PASS** (common_709 40f, rotsm_534 40f, rotsm_574 130f,
  rotsm_588 226f); receiver move 554 found for both King throws.
- Western Heart PR #1803 (extraction workflow) re-verified this
  lane: **state closed, merged True, merged 2026-11-22T16:58:20Z**
  (the scramble report's "open, unmerged" line is stale — the report
  predates the merge). Workflow: Windows runner, downloads
  `tkdata.bin` from release `tekken7-gamefiles-v1` + prebuilt
  TKMovesets2 v1.1 exe, verifies `_TEKKEN7CSFILES_` magic, runs
  headless `build-disk-movesets-t7 tkdata.bin out kin` (disk-only, no
  running game). Trigger note: PR event works; `workflow_dispatch`
  returns 403.
- Blockers on the file itself: the extracted `.tkmvst` is LZ4 type 1
  and `tkmvst_to_wh.py` refuses it — re-extract with
  `--compression none` (generalise the workflow: fighter code as an
  input, not King-hardcoded; add the LZ4 re-wrap step). Then Bryan
  (expected code `bry`, unverified), Heihachi, Jin, Yoshimitsu; 16
  extractions cover every T7 group except the unified index, which
  needs all 38 fighters. No bulk unscramble from already-unscrambled
  material works for T7 motion.
- Already-decoded check (this lane): TKMovesets2 is public
  (Kiloutre/TKMovesets, Tekken 7 + 8, v1.0) but its normal mode
  extracts from a RUNNING game's memory — it is not a free bank of
  already-decoded clips, and no public `.tkmvst` bank for Bryan /
  Heihachi / Jin / Yoshimitsu exists. The older TekkenMovesetExtractor
  (Kiloutre, GPL-3.0) is the same shape (live-memory export). The
  in-place route remains PR #1803's headless disk mode + the artifact.
  TekkenDocs frame data (`~/workspace/bannon-predecoded/tekkendocs/`,
  43 CSVs, 23,739 lines) is timing/damage data only — no animation.

### 1f. Already-decoded verification — T3 + DW (do NOT re-decode)

- **Tekken 3 divmot decode: SOLVED.** Per the WH scramble report
  (§5, owner rules): "every T3 use is the already-solved divmot
  decode". R127's manifest entry confirms its bank is real decoded
  T3 motion from the owner disc teardown (`divmot03_king.bin`).
  PR #1807 (merged 2026-11-21) re-baked the T3 King pack (32 clips,
  hip height 0.9805 m → 1.06130751 m, head error 50.90° → 0.007°).
  No T3 re-decode was attempted or is owed.
- **Devil Within keyframe curves: DECODED.** Per the scramble report
  (M6): `teardown/tekken5/dw-motion-curves.json` — 220 clips, 214
  decoded, 6 missing, Euler keyframe curves; "the decode is already
  done — verification is owed, not a re-decode." Owed instead:
  watched-render verification of every mapped move + timing/damage
  fills in `dw.json` (152 pack moves still `verified: false`).
  No DW re-decode was attempted or is owed.
- **Scramble context (do not redo):** the 102 scramble files do NOT
  follow one pattern (mechanisms M1–M9); 102 = 94 T7 + 6 DW + 2
  wrestling banks. Phase 2 merged fixes PR #1804 (Cain Elias, 5
  throws) and PR #1807 (above). Full detail:
  `~/workspace/research/wh-scramble/scramble-pattern-check-report.md`.

## 2. KoC2 — 0 decoded; Route A advanced one step

### 2a. Already-decoded search — nothing exists (re-confirmed this lane)

- Fresh web searches this lane: "King of Colosseum 2 MVS motion
  decoded animation extractor" and "King of Colosseum 2 animation
  rip MVS github motion data" — only game-database pages (150+
  wrestlers / 2,800+ moves marketing copy), YouTube gameplay, the
  ResHax TIM2 thread (textures only), and a texture request thread.
  No motion decoder, no decoded clips.
- Prior lane's searches (carried, not repeated): GitHub repo search
  "King of Colosseum 2 motion MVS" 0 repos; code search "KC2FIRE"
  28 hits — only `King_of_Colosseum_2_Tool.py` (archive extractor,
  textures/models only, no motion decode) and the XeNTaXBackup forum
  mirror; Noesis/TIM2 texture viewing only. **The public KoC2 scene
  has no motion work at all.** There is nothing to pull in.
- "2,800+ moves" is marketing copy (TechPlay/IGDB/CritScore), NOT an
  extracted count. The Neoseeker move list is human-transcribed text
  names/IDs — name mapping only, not motion.

### 2b. What exists (re-verified this lane unless noted)

- Bannon main `assets/moves/ik/koc2/`: README.md + manifest.json
  only — coverage full 0 / partial 0 / gap "all". **16,660 MVS
  files, 8,205 distinct contents, 271 moveset slots with no move
  table.** (Manifest re-fetched this lane; SHA
  `2b129368b0613c1d0f368b2a7384adb0a9abad2f`.)
- Western Heart PR #1814 (KoC2 raw files) re-verified this lane:
  **state open, merged False, mergeable_state blocked, 103 commits,
  head `22bbad2c77c123bcb7d44b074ced5eb0c9cfd795`**, base main
  `e82d76bf`. 81,672 files; four ISOs, each 47 × 99 MB pieces.
  Owner direction 2026-11-22: already answered/covered, do NOT
  re-ask for a call; the visual check is what is left. Bannon
  follow-up for KoC2 motion is separate from merging #1814.
- Western Heart PR #1770 (KoC2 teardown, 49,214 files) re-verified
  this lane: **state open, merged False, mergeable blocked.**
- Bannon follow-up data (no motion): `assets/moves/koc2-moveset-slots.json`
  (271), `koc2-roster.json` (429 entries / 363 distinct wrestlers,
  per precracked lane), `koc2-systems.json`, `koc2-text-data.json`,
  `assets/moves/vpw2-koc2/move_library.json` (1,764,807 B); 5
  character GLBs on branch `muse/web-upgrade` only
  (`assets/models/koc2/` does NOT exist on main).
- Precracked lane's artifacts re-verified this lane: ELF
  `~/workspace/bannon-precracked-koc2/work/SLPM_656.02` (3,048,408 B,
  sha256 `824ef43ea1083527d681e861aef341048e8380a19dd02e7917b9c1a648ab34fe`
  — matches), 13 sample MVS files, venv Capstone 5.0.7 + pyelftools
  working, non-motion brick test re-run **ALL PASS 10/10, exit 0**.

### 2c. Route A — new disassembly this lane

Logs: `bannon-all-moves-all-games-show/tekken-koc2/prep/koc2-*.log`;
write-up: `prep/koc2-route-a-next.md`. Disassembler:
`bannon-precracked-koc2/work/disasm_region.py` (Capstone MIPS64 LE).
No decode was produced; no joint data exists.

- **0x2894c0 — chunk-name lookup** (14 instructions): loads the list
  head from `gp-0x5008`, calls **0x30cf80** with a0 = head+0xc,
  a1 = name pointer, a2 = 0xf (15 — bounded compare; "MotionBase"
  is 10 chars), clears a flag byte at head+0x1b, returns the
  0x30cf80 result. Next: disassemble **0x30cf80**.
- **0x28b178 — chunk loader** (0x40 stack frame): calls 0x28aea0
  (chunk-table accessor), entry = table+0x1c + index*16; if a1 == 0,
  calls 0x28b0b8 then **0x289590** (allocator) to allocate the node;
  then calls **0x28b0a0** (entry fetch) and **0x28a6e8** (read/copy:
  `lhu` count at entry+0xe, 52-byte-stride table at
  0x3f0000+0x5820). This loads chunk buffers; it is NOT the MVS
  bitstream reader. Next: 0x28a6e8, 0x28aea0, 0x28b0a0, 0x28b0b8.
- **0x28b108 — range helper**: if a2 == a1, tail-jumps to 0x28b0b8;
  else returns. Bounds/equality test, no motion logic.
- **NEW finding: the allocator stamps nodes with "KOC2"**
  (magic 0x4b4f4332 — lui 0x4b4f + ori 0x4332, stored at node+0x1c;
  nodes are 0x80-aligned and linked into the gp-0x5008 list). A
  usable signature when tracing the loader's allocations.
- Prior mapping carried (not re-derived): MotionBase init **0x118970**,
  evaluator **0x2fe7d0** (per-frame evaluator/blender, NOT a
  bitstream reader), chunk loader called with IDs 0x7d6/0x7d7.
- **Corrections to stop following:** (1) `0x1189B8` is a CODE address
  (`lui $a0, 0x3b` at 0x1189B8); the real MotionBase string is at
  **0x3a8be0**, referenced from 0x118994 and 0x1189B8 (confirmed in
  `xref-scan.log`, 2 lui hits). Anyone hunting a pointer AT 0x1189B8
  searches for something that does not exist. (2) Byte 1 of an MVS
  file is probably NOT a frame count: file00000–file00003 share
  byte 1 = 218 at sizes 2,284 / 535 / 1,818 / 3,082 B. Do not build
  a decoder on it. (3) `bannon-vm-unblock-prep/koc2/koc2_motionbase.py`
  header is stale on both points (says no ELF exists in workspace;
  hunts 0x1189B8 as a data address) — file NOT edited here; treat its
  xref hunt as superseded.
- Still needed, in order: disassemble 0x30cf80, 0x28a6e8, 0x28aea0,
  0x28b0a0, 0x28b0b8; trace callees of 0x2fe7d0 to find the function
  that consumes an MVS buffer (lbu + sllv + table-driven branch);
  re-fit MVS header statistics on all 16,660 files with header
  family as a covariate; then file 01999 (WrestlerData, 2,285-byte
  records) to map slots → MVS → names. Route B (known-plaintext)
  still has no candidate plaintext. This is the longest pole.
- Full KoC2 non-motion brick (roster, slots, models, crack state):
  `~/workspace/bannon-precracked-koc2/koc2-nonmotion-brick.js`
  (10/10 tests). This lane did NOT duplicate it; the Tekken+KoC2
  brick below carries KoC2 only as a MISSING refusal + the corrected
  xref state.

## 3. Wiring brick + gate check

### 3a. Wiring brick (DRAFT, not landed)

`bannon-all-moves-all-games-show/tekken-koc2/tekken-wiring-brick.js`
(`node --check` clean). Registry of all 383 Tekken clips with
pairing verdicts + KoC2 refusal state. `lookupTekkenClip(id)` returns
the row or null; `isPlayableTekkenClip(id)` returns
`{playable: false, reasons: [...]}` for EVERY clip (G2/G3/G4/G6
always, G5 when truncated, plus not-a-move / adaptation notes);
`lookupKoC2Motion(id)` returns `{status: 'MISSING', clips: 0}` for
every id. The refusal IS the wiring until the blockers clear — do
not flip a clip to playable by editing the file; clear the blocker
and re-run the gate check. No damage/slot is filled (per-clip
move_class is not in the manifest; registry moves per clip live in
the IK files).

Headless test `tekken-wiring-brick-test.cjs`: **ALL PASS 14/14,
exit 0** (run 2026-11-23) — counts 230/96/54/3, verdicts
361/14/5/3, R127/T7/DW/MADE/beam ground-truth rows, every clip
refuses, unknown/VPW2/KoC2 ids null, KoC2 MISSING + xref correction
recorded.

### 3b. Seam-gate check (headless — no browser run, and why)

`prep/tekken-koc2-gate-check.py` → `gate-check.json`. Gates mirror
the in-page `__match` driver in
`~/workspace/bannon-all-clips-working-show/match-run.py`
(launch-spot + target-state + verified-clip checks; undecoded /
wrong-spot / not-in-hand is REFUSED, never played):

| Gate | Result |
|---|---|
| G1 decoded + in hand | PASS 383/383 (clip JSONs in repo) |
| G2 receiver present | FAIL 383/383 |
| G3 root travel present | FAIL 383/383 |
| G4 library mapped | FAIL 383/383 |
| G5 contact keyframe present | Known-fail 68 (14 truncated + 54 DW no-active-by-design); 315 unassessed per-clip (needs per-file `active_frames` reads — not a pass) |
| G6 renderer can play | FAIL 383/383 (position-pose JSON; renderer plays 2K26 quat clips only) |
| **Playable in a real match** | **0 / 383** |
| KoC2 G1 decoded | FAIL — 0 decoded; **0 playable** |

No browser bout was run: `match-run.py` needs Playwright/Chromium
(a live browser, which this subagent cannot operate), and every
Tekken/KoC2 clip would be refused by the gates before any frame
renders — a browser run could only reproduce the refusal, not a
match. The gate check is the honest evidence; the bout run is owed
after the unblocks in §5.

## 4. What plays in a real match now — NOTHING (prove each)

- Tekken moves played: **0**. KoC2 moves played: **0**.
- Stills produced: **0**. MP4 videos produced: **0**.
  `tekken-koc2/stills/` and `tekken-koc2/video/` hold NOT-PROOF-YET
  notes instead of files. This is deliberate: a still or MP4 would
  have to show a real match frame, and rendering a solo Tekken clip
  as a two-performer match would be inventing proof.
- Rigs: Finn / Big Cass / Elias / Enzo port zips are present in the
  workspace (`EnzoAndCassPorts.zip` 1.1 GB, `EliasPorts.zip` 167 MB,
  `FinnBalorEntrancePort.zip` 83 MB) but unopened here — they are
  2K26 `.clips` banks, not Tekken/KoC2 clips, and no Tekken/KoC2 clip
  passes the gates to play on them. The Finn-vs-Cass bout harness
  exists (`bannon-all-clips-working-show/match.html` +
  `match-run.py`, 2K26/mod moves only); the Tekken/KoC2 bout run on
  those rigs is owed after the retarget build (§5 step 4).
- Renderer limit, precisely: `match.html` plays 2K26 quaternion
  clips. Tekken clips are position-pose JSON (`{dur, keys: [{t,
  pose: {18 joints}}]}`-family). The same gate already refuses the
  VPW2 Frog Splash probe in `match-run.py` ("position-pose JSON …
  this renderer cannot play them; needs a VPW2 position->rig IK
  retarget build"). Tekken needs the identical build.
- The only move live in a Bannon match today remains the 2K26 chop
  (clip 4662, 'Reach - Chop', per prior record) — NOT a Tekken or
  KoC2 move, and not re-proven in this lane.

## 5. Blockers + exact unblock steps (in order)

1. **King artifact rescue — before 2027-02-19.** GitHub-authed
   machine downloads artifact 14688676730
   (`gh api repos/mhvnsnt/western-heart/actions/artifacts/14688676730/zip`,
   or the Actions run page in a browser) and stores it durably.
   Owner decision owed: durable home (new release vs alongside
   `tekken7-gamefiles-v1`). Binaries need a git-authed machine —
   this lane prepped the exact command and did NOT download (401
   anonymous, `gh` unauthenticated here, connector has no
   artifact-download tool).
2. **King re-extraction.** Generalise the #1803 workflow (fighter
   code as input, `--compression none`, LZ4 re-wrap, PR-event
   trigger), then Bryan, Heihachi, Jin, Yoshimitsu.
3. **Tekken pairing + root restore** (§1c–1d): receiver from AKI P2 /
   WMXIX / authored reaction; root x/z from the WH source pack root
   track (converter v2); re-bake the 14 truncated clips from their
   source rows; watched-render verification for the 152 DW pack moves
   (`verified: false`).
4. **Position-pose → rig retarget build** for the match renderer
   (Tekken + VPW2 share this need).
5. **VM/browser bout run** on Finn / Big Cass / Elias / Enzo —
   stills AND MP4s, eye-checked vs source. Append/redeploy needs
   the VM — prepped exactly here (harness + gates + rigs named),
   NOT faked live.
6. **KoC2 Route A** (§2c): 0x30cf80, 0x28a6e8, 0x28aea0, 0x28b0a0,
   0x28b0b8; find the MVS bitstream reader; re-fit header stats;
   then file 01999. Do NOT schedule KoC2 clips before the MVS decode
   lands.

## 6. Landing

- Text-only landing for this lane (branch → PR → merge, no force):
  branch `lane/tekken-koc2-2026-11-22` (from main `158a088f`),
  commit `91d84366`, **Bannon PR #426**
  (created 2026-11-23; mergeable_state `unstable` at creation —
  checks pending, not a conflict). Merge status: see final report.
- Landed set (text only, no binaries): the lane record (this file),
  `tekken-koc2/` show-directory contents (README, pairing-audit.json,
  gate-check.json, tekken-wiring-brick.js + test, prep scripts +
  KoC2 logs + route-a note, stills/video NOT-PROOF-YET notes).
- NOT landed and NOT attempted here: the King artifact (needs
  git-authed download + owner decision on home), any `.tkmvst` or
  clip binary, any engine append, any deploy/redeploy (needs VM).

## 7. What was NOT re-done (audit trail)

- T3 divmot decode NOT re-derived; DW curves NOT re-decoded; King
  `.tkmvst` NOT re-downloaded (401) or re-extracted.
- KoC2 MVS files NOT decoded; no decode attempted; the precracked
  lane's ELF/brick work was re-verified (sha + test re-run), not
  redone, except the three new disassemblies in §2c.
- Nothing bought, no paywall bypassed, no leaked SDK used.
  TKMovesets2 / TekkenMovesetExtractor are public tools that extract
  from the owner's own game files or a running game — noted as
  routes, not used to pull a free decoded bank (none exists).
- The `wh-clone` under `~/workspace/research/wh-scramble/` is empty
  on disk (staged deletions, HEAD `b2a52a7`) — not used for any
  claim in this lane; all repo facts came from the GitHub connector.

## Sources (exact paths)

- Bannon main (GitHub connector, read-only, 2026-11-22/23):
  `assets/moves/ik/tekken/manifest.json`,
  `assets/moves/ik/tekken/README.md`,
  `assets/moves/ik/tekken/T3_KING_R127.json`,
  `assets/moves/ik/tekken/T7_KING_mokg_tkr_DVD.json`,
  `assets/moves/ik/tekken/T5DW_PANTERA_ikdv_36_nage_y.json`,
  `assets/moves/ik/koc2/manifest.json`, `tools/tekken/README.md`
- Western Heart PRs (connector, 2026-11-22/23): #1803 merged
  2026-11-22T16:58:20Z; #1814 open/blocked, 103 commits, head
  22bbad2c77c1; #1770 open/blocked
- King artifact (public GitHub API, 2026-11-22/23): run 44858568891,
  artifact 14688676730, 14,386,774 B, sha256 613826d7…,
  expires 2027-02-19T02:56:50Z; anonymous zip download 401
- Workspace: `~/workspace/bannon-all-moves-all-games-show/tekken-koc2/`
  (README, pairing-audit.json, gate-check.json,
  tekken-wiring-brick.js + test, prep/); `~/workspace/bannon-all-clips-100/other-banks.md`
  §3–§4; `~/workspace/bannon-all-games-tekken-vpw2-koc2.md` §2–§3;
  `~/workspace/research/wh-scramble/scramble-pattern-check-report.md`
  (M6, §4–§5); `~/workspace/bannon-precracked-koc2/` (record, brick,
  work/SLPM_656.02 + logs + scripts); `~/workspace/bannon-vm-unblock-prep/koc2/`
  (koc2_motionbase.py — stale header, see §2c);
  `~/workspace/bannon-all-clips-working-show/match-run.py` (seam gates,
  VPW2 refusal probe); `~/workspace/bannon-predecoded/tekkendocs/`
  (frame data only); `~/workspace/bannon-predecoded/koc2-000-001-spec-notes.md`
- Public web (2026-11-22/23): TekkenMovesetExtractor (Kiloutre,
  GPL-3.0, live-memory export); TKMovesets2 (Kiloutre/TKMovesets,
  T7+T8 v1.0); ResHax "King of Colosseum 2 TIM2 Compression"
  (skstylez, Oct 2025 — textures only); XentaxWiki KoC2 000/001 spec
