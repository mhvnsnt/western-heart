# VF5 complete teardown — Lane 1A findings (2026-11-21)

**Lane:** 1A — VF5 complete teardown (Xbox complete-teardowns job)
**Date:** 2026-11-21
**Repo:** mhvnsnt/western-heart (PUBLIC)
**Owner order (2026-11-21):** do ALL the complete work and teardowns for all six
Xbox games, or find the CLOSEST things to complete work/teardowns. Get all the
rips, whatever you can, the closest thing, so we don't start from scratch.
Finish it and make the complete ones. Put the complete ones to the side in their
own repos. AND wire them up 100% into Western Heart.
**Targets:** Kutz/Goh, Realizzt/Brad, Zen/Dural — REAL animation/moves, not
transcriptions.

## Verdict

**No complete working VF5 teardown exists anywhere searched live 2026-11-21 —
same verdict as Lane 1 (2026-11-20), re-checked live.** No pre-extracted VF5
motion dump, no VF5 motion converter, no already-extracted VF5 moveset exists
in any public source. What DOES exist, pulled whole in this lane, is the
closest thing: **MikuMikuLibrary** — the only public tool that reads VF5
motion files — vendored at `tools/anim/vf5-mikumikulibrary/` with its two
extraction CLIs (FarcPack, DatabaseConverter). That is the complete-tooling
half of the teardown. The data half (real Goh/Brad/Dural motion) still needs
an extraction run against full game files — see "The fork" below.

This confirms and re-checks (live, one day later) Lane 1's PR #1802 record
(merged 2026-11-21T11:18:20Z, merge commit
`f5e6f23543d1d18e2fd4959a922363171a098070`) and the Oct 22 gap docs
`docs/research/VF5-MOTION-GAP-2026-10-22.md`,
`docs/anim/VF5-DURAL-ANIM-GAP-20261023.md`.

## Live re-search 2026-11-21 (archive.org FIRST, actual files inspected)

1. **archive.org advancedsearch `title:(virtua fighter 5)`** — 57 hits, same
   set as 2026-11-20: G4TV/GameTrailers videos, Xbox 360 manuals (JP/NA/FR/EU),
   VF5 R.E.V.O. 4x3 patch, one XPS Vanessa model, Arcadia command books,
   Black/White Books. **No dump, no moveset, no motion extraction, no teardown.**
2. **archive.org `(virtua fighter 5) AND mediatype:software`** — 309 hits, same
   VF5 items: `vf5revo_101` (REVO 1.01 patch DLLs only, requires Steam
   ownership), `games_20250220` (full PS3 game dump `GAMES.rar`
   3,686,456,692 B — the game itself, not a teardown), `vf5revo_noEAC` /
   `Virtua5NoEAC` (No-EAC REVO builds — the game, not a teardown), redump
   discs (Europe/Japan/USA — the game), `virtua-fighter-3-recomp-windows`
   (VF3 Recomp, a different game). **No VF5 recomp exists.**
3. **archive.org `addeddate:[2026-11-20 TO 2026-11-22]` + title VF** — 0 new
   items. Nothing appeared since Lane 1's check.
4. **NEW item inspected (not in Lane 1's report): `vf5fs_dural`** (added
   2026-10-23, `vf5fs_dural.zip` 72,327,053 B, sha256
   `f76ed5e03ab883ed377750569fdade97a6defe322f8f8f0a294517996815bf6d`) —
   downloaded and listed: 70 files, 73,774,562 B uncompressed. Contents: XPS
   Dural MODEL pack only (`generic_item.mesh` + `.mesh.ascii` + textures;
   variants base/glass/gold/metal/oil/stone). **Zero motion, zero .farc,
   zero bone files.** A new Dural model source (XPS format), not motion.
   Staged to release `vf5-dural-xps-v1` (see below) so it is stored, not lost.
5. **VF5 Recomp:** still does not exist. Only VF1 Recomp (mr-finster, active
   commits Nov 2026, latest `1a5cd99b…`) and VF3 Recomp. VF5 R.E.V.O. World
   Stage v1.12 is live on Steam (purchase route — barred by NO-BUY; owner
   owns the Xbox games).
6. **RGG Modding Wiki VF5: Ultimate Showdown** (re-read live 2026-11-21):
   Dragon Engine layout, `chara` PAR = character models, `motion` PAR is a
   leftover from Yakuza: Like a Dragon. **No VF5 character-animation
   extraction exists in that ecosystem.**
7. **GitHub / web:** no VF5 motion extractor, no `mot_db` dump, no
   Goh/Brad/Dural motion pack found. YAMP / VF5FS Unlocker (play the game,
   extract nothing), sp00nznet/vf5 ps3recomp (loading screens only, not
   under active development), TeknoParrot/Lindbergh (emulator, extracts
   nothing) — all unchanged from Lane 1.

## What was pulled whole (this lane)

### MikuMikuLibrary + FarcPack + DatabaseConverter — `tools/anim/vf5-mikumikulibrary/`

The only public tool that reads VF5 motion files. Upstream
`blueskythlikesclouds/MikuMikuLibrary`, MIT, master pinned
`82380f1e40bbcf07d19c4ac8d0bdb95845be3628` (2026-04-22). Vendored subset:
206 files — core library (incl. `Motions/` motion parser and
`Databases/MotionDatabase.cs`) + the two extraction CLIs + shared items +
LICENSE/README. GUI (MikuMikuModel) and native C++ lib NOT vendored (not
needed for extraction; see `WH-NOTES.md` in that directory for the full
pin, licence, build and use notes). No binaries vendored; no game files ship.

Why this is the right tool: per the upstream wiki, VF5 uses the same engine
family as Project DIVA, and the motion pipeline needs exactly 4 files —
`obj_db.bin` + `tex_db.bin` (both already in release `vf5-ps3-v1`) +
`bone_data` (`rom`) + `mot_db` (`rom\rob`) — with motion files in `rom\rob`
inside `mot_*.farc` archives. FarcPack extracts those archives;
DatabaseConverter turns `mot_db.bin` into readable XML (the motion
inventory). That is the documented, working, already-cracked route from
game files to motion — no format guessing.

### Dural XPS model pack — release `vf5-dural-xps-v1`

`vf5fs_dural.zip` (72,327,053 B, sha256 above) — community XPS conversion of
the VF5FS Dural model, 4 material variants. Model only, NOT motion. Stored
as a release asset so the new Dural model source is kept and retrievable;
it does not close the motion gap.

## The full-PS3-dump test (vf5-500m RAR listing) — MOTION PROVEN PRESENT

The Oct 22 gap doc left open whether the 4 GB `vf5-500m` split archive
(release `vf5-ps3-v1`, reassembles to `vf5-ps3-games.rar`, the full
BLES00029 dump) contains motion files — "unverified (high-entropy, not
fully downloaded)". This lane verified it WITHOUT downloading the 4.2 GB
and WITHOUT writing a byte to disk:

- **Download attempt:** `gh release download vf5-ps3-v1` pulled 5 partial
  parts (~843 MB) then failed hard: `openat vf5-500m.part_07: disk quota
  exceeded` — disk 121G used / 29G device-free, user quota wall binding
  (see "The fork"). Partial parts deleted after use (100% on the release).
- **Read-only probe of the partial data:** `7zz l` on the truncated
  part_00 parsed the RAR5 archive (312 file headers reachable in the first
  168 MB): `GAMES/BLES00029-[Virtua Fighter 5]/PS3_GAME/USRDIR/...`,
  archive order is alphabetical filesystem traversal (`lang/*/rom/2d`
  first, then `objset/`, then `rom/`). No motion names in the first
  843 MB — expected, since `rom/` sorts after `objset/`.
- **Decisive probe — RAR5 QuickOpen record via HTTP Range (zero disk):**
  the archive carries a QuickOpen index (`Characteristics = Locator
  QuickOpen:3686312858`) in the last ~144 KB of part_07. Streaming only
  the last 1,000,000 bytes of `vf5-500m.part_07` through grep returned the
  full file list (~1,221 entries). It contains the COMPLETE motion set
  under `GAMES/BLES00029-[Virtua Fighter 5]/PS3_GAME/USRDIR/rom/rob/` —
  see the inventory doc
  `teardown/virtua-fighter-5/VF5-MOTION-INVENTORY-20261121.md` for the
  exact list. Headliners, all present:
  `mot_GOH.farc`, `mot_BRA.farc`, `mot_DUR.farc` (the three target
  fighters), `mot_db.farc`, `bone_data.bin` (`USRDIR/rom/bone_data.bin`),
  `ctrl_*.bin` ×17, `mothead_*.bin` ×19, `rob_mot_tbl.bin`, plus
  `mot_*.farc` for all 19 fighters + `mot_CMN.farc` / `mot_ENB.farc` /
  `mot_AUTH_*.farc` / `mot_TEST_*.farc`.
- **PS3 layout note (corrects the wiki's generic paths):** in BLES00029
  the model DBs live at `USRDIR/objset/` (not `rom/objset/`); the motion
  DBs live at `USRDIR/rom/rob/mot_db.farc` + `USRDIR/rom/bone_data.bin`.
  The `obj_db.bin` / `tex_db.bin` already in release `vf5-ps3-v1` are the
  same files.

So: the motion data half of the teardown EXISTS, in-repo, with exact
filenames. What is still missing is the extraction RUN (next section).

## The fork (exact, no workaround invented)

The data is proven present; the extraction run is fully specified and is
NOT done in this lane, for two environmental reasons only:

1. **Disk quota on this box.** Staging the 4.2 GB split archive fails
   with `disk quota exceeded` at ~121G used. The extraction needs the
   full reassembled RAR (or a box that can hold it).
2. **No .NET 8 on this box.** The vendored FarcPack / DatabaseConverter
   CLIs target net8.0 and could not be run here.

**Exact next lane (extraction run):** on a box with disk headroom AND
.NET 8: (1) `gh release download vf5-ps3-v1 --pattern 'vf5-500m.part_*'`,
`cat vf5-500m.part_* > vf5-ps3-games.rar`; (2) `7zz l` the full RAR and
confirm the `rom/rob` inventory against
`teardown/virtua-fighter-5/VF5-MOTION-INVENTORY-20261121.md`; (3) `7zz x`
ONLY `*/rom/rob/mot_GOH.farc mot_BRA.farc mot_DUR.farc mot_db.farc`
+ `*/rom/bone_data.bin` (small — the motion payload, not the 4.2 GB);
(4) `FarcPack` extract the mot farcs; `DatabaseConverter` convert
`mot_db.farc`→XML for the motion inventory (every motion ID/name per
fighter); (5) map mot_db names to the Goh/Brad/Dural move lists and
convert the exported motions to `wh-anim/1` via `tools/anim/`, landing at
`game/assets/anim/vf5/{goh,brad,dural}/` with `skeleton.json` +
`rows.pack.json` (per `docs/anim/VF5-DURAL-ANIM-GAP-20261023.md`); (6) wire
the banks in and open the wiring PR. The vendored toolchain in
`tools/anim/vf5-mikumikulibrary/` is the tool for every step; no format
guessing is needed — MML reads this format. (Kaggle/Colab/Oracle are the
standing compute fallbacks if no local box has headroom + .NET.)

## Still missing (exact gap)

- **Kutz — VF5 Goh:** no `vf-goh.json`, no Goh motion. Still plays King.
- **Realizzt — VF Brad Burns:** no `vf-brad.json`, no Brad motion. Still
  plays Jin.
- **Zen — Dural:** no Dural motion/animation anywhere. Zen's permanent base
  (Dural stance/idle/strikes → `game/assets/anim/vf5/dural/`, wh-anim/1)
  is still pending per `docs/anim/VF5-DURAL-ANIM-GAP-20261023.md`; the
  interim 639-move Heihachi kit stands, sources never mixed. The identity
  call (ROSTER Julia vs file Dural vs index Heihachi) is the owner's, NOT
  decided here.
- **VF5 motion converter to wh-anim/1:** still none; PR #713 open. The
  vendored MML toolchain reads/exports VF5 motion; the WH-bank converter
  step is still unbuilt.

## Sources / licence log

- MikuMikuLibrary: MIT, Copyright (c) 2023 Skyth —
  https://github.com/blueskythlikesclouds/MikuMikuLibrary
- VF5 itself: SEGA. Licence status never gated the search or the pull.
- `vf5fs_dural`: archive.org community XPS pack, author unstated in the
  item metadata — logged as found; SEGA owns the underlying model.
- Key URLs: https://archive.org/details/vf5fs_dural ·
  https://archive.org/details/games_20250220 ·
  https://modding.rgg-games.wiki/wiki/Virtua_Fighter_5:_Ultimate_Showdown ·
  https://github.com/blueskythlikesclouds/MikuMikuLibrary
