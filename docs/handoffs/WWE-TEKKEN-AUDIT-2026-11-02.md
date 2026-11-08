# WWE + Tekken missing-material audit — 2026-11-02

Read-only audit (GitHub API + git tree reads on main). No PRs from the
audit itself, no repo files modified by it, no deploy, no Steam login,
no model fabricated. Counts below were re-verified against the main
tree (`git ls-tree -r HEAD`) on 2026-11-02, not taken from the brief.

**Update 2026-11-08 (PR #1647 fix lane):** the Tekken 5 section below
was updated to the measured state after the Devil Within decode.
Counts were re-verified against the `dw-decode` branch tree
(`git ls-tree -r HEAD` equivalent via the git trees API) and the
committed measurement artifacts were cross-checked against each
other (see §Tekken 5). All other sections are unchanged from
2026-11-02.

## WWE

### 2K19 — batch 1 landed, not a complete teardown

- PRs #1480 (1,036 files) + #1481 (607) + #1483 (34) = **1,677 files**,
  all additions, 0 deletions, all merged. Plus the pre-existing
  `README.md` = **1,678 blobs** under `teardown/wwe2k19/` on main.
- Contents: `extracted/ingame/motion/` 1,000 files (59.8% of
  extracted), `extracted/edit/` 641 (38.3%), `extracted/ch/` 32 (1.9%).
  By extension: `.bin` 1,059, `.dds` 597, `.yobj` 6, `.cnpc` 5,
  `.cnct` 5, `.onet` 1, plus manifests.
- What batch 1 is (per `teardown/wwe2k19/PULL.md`): offline extraction
  only, Steam app 817130 / depot 817131 (owner licence),
  DepotDownloader filelist `batch1.txt` (42 PACs), unpacked with
  `tools/wwe/pac_unpack.py`. Names are hash IDs only — no readable
  wrestler names imported in this batch.
- Still owed for 2K19 (stated in PULL.md itself): YOBJ → glTF
  conversion, YANM decode of the motion `.bin` blocks, more batches.
- This PR fixes the stale status line in `teardown/wwe2k19/README.md`
  ("Awaiting extraction" → batch 1 landed). Nothing else in that
  README changed, including its private-repo rule.

### 2K20 — README-only pull plan, 0% extracted

- `teardown/wwe2k20/` holds exactly **1 file: `README.md`**.
  Steam App ID 1015500, Owned: YES, Status: Awaiting extraction via
  DepotDownloader (delisted — needs Steam auth). Planned: animations,
  rigs, CAW parts unique to 2K20, showcase/story structure.
  Coordination: issue #866.

### 2K22 — README-only pull plan, 0% extracted

- `teardown/wwe2k22/` holds exactly **1 file: `README.md`**.
  Steam App ID 1255630, Owned: YES, Status: Awaiting extraction via
  DepotDownloader (delisted — needs Steam auth). Planned: full
  animation library, rigs, CAW system structure, community-creations
  format/structure. Coordination: issue #866.

### 2K24 — no directory at all

- `teardown/wwe2k24` returns 404. No directory, no README, no pull
  plan on main. **2K24 was not pulled; do not claim otherwise.**

### WWE blocker, stated plainly

A Steam pull for 2K20 / 2K22 (and any future 2K24 pull) is BLOCKED on
the owner's Steam auth. Agents never log into Steam. This was not
attempted and must not be faked. Delisted status means the owner
licence + auth path matters even more — there is no store-page
fallback to pull from.

## Tekken

WH baselines: roster `game/js/roster-full.js` = 59 fighters;
moveset library `game/data/moveset-library/index.json` (built
2026-10-22) = 9,516 total moves across 6 landed banks + 9 pending.

### Tekken 5 — Devil Within decoded 2026-11-08 (PR #1647); main-game models/movesets still 0%

- `teardown/tekken5/`: **43 blobs** (tree-verified on the `dw-decode`
  branch, 2026-11-08) — the original 11 docs/survey/manifest files
  plus 32 decode files added by PR #1647: `DW-DECODE-LOG.md`,
  `ROMD-FORMAT.md`, 10 measured-data JSONs, and 20 extraction tools
  under `tools/`.
- romD extraction (per `DW-DECODE-LOG.md` §3; extracted bytes are on
  disk only in `raw/romd_out/`, not in the repo): 1,022 files /
  108,866,592 bytes across containers; **Devil Within 236/242 files
  extracted**. The 6 with no file data in TK5DATA2 are named
  identically in the log, `dw_measurements.json`, and
  `dw-motion-bank.json`: `gym_ozhe_1ckj66a.dat`,
  `gym_ikt5_katgym_Bbr_bbblow.dat`, `gym_ikt5_katgym_Gan_mekin.dat`,
  `gym_init_obj_testchr1.dat`, `gym_init_obj_testchr2.dat`,
  `gym_init_obj_testchr3.dat`.
- Index decode: all 242 Devil Within files named and glossed in
  `dw-motion-index.json` against the 498-name romD manifest.
- Motion measurements (recomputed from `dw_measurements.json`
  per-file entries by the fix lane; group aggregates match exactly):
  **214 extracted motion clips, 16,503 frames** at 60 fps (~275 s),
  35 bones for standard motions. `dw-motion-bank.json` agrees with
  `dw_measurements.json` on frames/bones/group for all 214 clips,
  0 discrepancies. The bit-exact keyframe decode is NOT finished
  (decode log §4 says so); the romD LUT table layout is documented
  but UNVALIDATED (decode log §2).
- Audio/stage data: `dw-audio-decoded.json` covers the 18 `snd_*`
  files at 22,050 Hz; `moj-stage-geometry.json` parses 4 stages.
- Game side: PR #1647 adds the Devil Within motion bank
  `game/data/moveset-library/banks/dw.json` plus
  `game/data/heartmind-dw-teardown.json` and updates the library
  index — the DW sub-mode now has a bank; T5 main-game native
  movesets/models remain 0% (no model payloads in this decode).
- `ROSTER.md` still documents 32 fighters from public game data
  (explicitly "verify against disc file inventory"), not from
  extracted files — unchanged by PR #1647.

### Tekken 3 — the only Tekken moveset bank in the library

- `teardown/tekken3/`: **19,499 blobs** (tree-verified), dominated by
  `tim-output/` (17,116), `tools/` (1,974), `renders/` (233).
- `movesets/`: 43 files — 21 fighter/common pairs (`.csv` + `.json`)
  = 20 fighters + common. `animations/`: 21 files (20 fighters +
  common). `models/`: 15 directories. `stages/`: 15 directories.
- **Mokujin has NO moveset** (bank type 15 record size 0, no
  `divmot15` file). Consistent across movesets and animations.
- Library impact: bank `t3` = **4,648 moves from 20 source banks =
  48.8% of the library's 9,516 moves** — the single largest bank.
- Usability limit (claimed-map law, enforced by
  `game/js/moveset-library.js`): movesets may ONLY be pulled from
  unclaimed fighters. Claimed Tekken names (13) include the King,
  Demonio, Pantera, Phantom, and other roster fighters' bases. Free
  T3 names listed in the claimed map: True Ogre, Lucky Chloe,
  Hwoarang, Raven, Jun Kazama, Craig Marduk, Roger Jr. (crew
  verifying). T3's 20-fighter extraction ≠ 20 fighters freely usable.

### Tekken Tag Tournament 2 — roster documented, extraction gated

- `teardown/tekken-tag-tournament-2/`: **56 blobs** — container/format
  docs, 13 opaque small extracts (hash-named, 98,304–339,968 bytes
  each), pull manifest, tools, rigging reference, UI doc.
- `ROSTER.md` lists 60 names (59 console + Dr. Bosconovitch) from
  public game data (Tekkenpedia), NOT extracted from the archive
  (opaque Xbox 360 STFS containers, no plaintext names).
- The 13 GB `ttt2.7z` (72 files) was verified, but the inner pulls are
  9 `.bin` files whose manifest landed and whose binaries are NOT in
  the repo (by the repo's rule against copyrighted game files in a
  public repo). The blocker is the Namco container header
  (`0f f5 12 ed …`, high-entropy payload) — cracking it gates all
  TTT2 character/model data.
- Library impact: bank `ttt2` = pending, **0 moves**. Still missing:
  all TTT2-native movesets, models, animations — including the
  TTT2-only WH mappings the T7 coverage doc assigns here (True
  Ogre→Chatur, Jun Kazama→Megami, Roger Jr.→Menajerii, male
  Raven→Pond). Note: the Roger Jr. kit itself now exists as
  menajerii (see `docs/movesets/ROGER-BANK-AUDIT-2026-11-02.md`); the
  TTT2-native extraction gap is about models/animations, not the
  movelist.

### Tekken 7 — models partial, native movesets/animations 0%

- `teardown/tekken7/`: **173 blobs** — King-focused in-repo set
  (94 blobs: 1 FBX, texture sets, export scripts), tekkenmods-docs
  (59), models (9), arenas (1 file: Mishima Dojo map, 40,790,120
  bytes), tools (1: umodel_linux), UI + rigging docs.
- Per `TEKKEN7-ROSTER-COVERAGE.md` (generated 2026-10-23, doc of
  record): fighter models (T7-native, repo + releases) **25/51 =
  49%**; 5 more obtainable free; 21 with no free T7 model found.
  Fighter movesets (T7-native) **0/51 = 0%** (requires the 47 GB game
  paks). Animations **0/51 = 0%** (sole exception: an Akuma SFM
  community animset, partial). Stages **1/34 ≈ 3%**. Audio 0%.
  Customization part meshes 0/16 slot classes. UI docs only, ~5%.
- Priority-11 verdict: 3 held (Feng Wei, Hwoarang, Zafina), 4 blocked
  with no free source (Law, Lars, Marduk + Lucky Chloe
  obtainable-but-unpulled), 4 not in T7 at all (True Ogre, male Raven,
  Jun, Roger Jr. → TTT2/T5–T6 lanes).
- Missing-4 catalog: Heihachi + Yoshimitsu found via community/GTA
  sources; **Bryan Fury (T7) NOT found, Jack-7 NOT found**.
- Library impact: bank `t7` = pending, **0 moves**. T7 native
  extraction is blocked on game files (Steam paks) in the same way as
  the WWE Steam pulls — owner-side game access.

## What could go in a public PR vs what must not

**Could go in (original-derivative / public-structure data only):**
roster docs and coverage matrices, container/format analysis docs,
move-row frame-data structure (the form already in
`teardown/tekken3/movesets/` CSV/JSON), catalog/mapping docs,
rigging-reference docs, tekkenmods-docs knowledge, WH-original
wiring/catalogs that cite a source game without embedding its files,
and the T5/T7/TTT2 survey manifests (names, counts, hashes).

**Must go in NO public PR:** raw commercial files — models
(`.fbx`/`.glb` ripped from the games), textures (`.dds`/`.tim`/`.png`
texture dumps), animations/motion banks (`.bin` motion data beyond
the already-landed analysis form), audio/Wwise, ROMs/ISOs, and
Steam-pak contents. Note: several such derived files are already
present in `teardown/tekken3/` and `teardown/tekken7/king/` on public
main; this audit flags that as an owner-routing question and does
NOT propose adding more of them. The same flag applies to the raw
2K19 extracts already on public main despite the READMEs'
private-repo rule (see §WWE above) — the owner/lane confirms whether
that routing stands or needs correcting; this audit changes neither.

## Missing-material roll-up vs WH (59 fighters, 9,516-move library)

- T7-native movesets/animations: 0% — pending bank, blocked on game paks.
- TTT2-native movesets/models: 0% — pending bank, blocked on container decryption.
- T5-native (main game) movesets/models: 0% — still no main-game
  bank; the Devil Within sub-mode was decoded 2026-11-08
  (PR #1647, see §Tekken 5): 236/242 files extracted (disk),
  214 motion clips measured, `dw` motion bank in the library.
- T3-native movesets: extracted for 20 fighters + common, but
  law-gated to unclaimed/free fighters only; Mokujin missing entirely.
- T7-native models: 49% held (repo + releases) per the 2026-10-23
  coverage doc; that doc, not this audit, is the source for 25/51.
- WWE 2K19: batch 1 landed (1,677 files); YOBJ→glTF, YANM decode,
  further batches owed. 2K20/2K22: 0%. 2K24: not pulled.

## Owner blockers (exact)

1. **Steam auth** — 2K20 (App 1015500), 2K22 (App 1255630), T7 native
   extraction (47 GB paks). Agents never log into Steam.
2. **TTT2 container decryption** — Namco header gates all TTT2
   character/model data; inner-pull binaries are manifest-only in the
   public repo by design. Needs a decryption/reverse-engineering
   lane, not a re-pull.
3. **Stale-doc + routing questions** — 2K19 README status fixed by
   this PR; the public-repo raw-file routing question (2K19 extracts,
   T3/T7 derived files already on public main vs the READMEs'
   private-repo rule) needs an owner/lane confirmation, not a silent
   fix.
