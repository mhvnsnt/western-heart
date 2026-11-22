# VF5 teardown hunt — Lane 1 findings (2026-11-20)

**Lane:** 1 — VF5 teardown hunt + pull + wire-up
**Date:** 2026-11-20 ~19:29–20:30 EST
**Worker:** lane-1-vf5 (subagent 26dac24e)
**Coordinator workdir:** `~/workspace/_xbox-teardown-pull-20261120/`
**Owner order (Nov 20 ~19:27 EST, verbatim substance):** "Instead of buying those games, just go get like the Teardown moves. I have I own those games on Xbox. Just go get like the already tore down and decomped and already like don't start it from scratch. Go get like the mod and fan tear down and decomped and extracted stuff stuff that already has the code and stuff cracked."
**This order REPLACES the ~$30 Steam purchase for VF5. Nothing was bought.**

## Verdict

**NO complete working VF5 teardown exists anywhere found.** No pre-extracted,
complete, working VF5 moveset / animation / motion source for Goh, Brad Burns,
Dural, or any other VF5 fighter exists in any public source searched live on
2026-11-20. Nothing was pulled as a moveset because there is nothing that
meets PULL-WORKING-COMPLETE to pull. No hand-tooled rebuild was made, nothing
was bought, nothing was faked.

This CONFIRMS and RE-CHECKS (live, one month later) the prior gap assessments
`docs/research/VF5-MOTION-GAP-2026-10-22.md` and
`docs/anim/VF5-DURAL-ANIM-GAP-20261023.md`: VF5 motion was never acquired, the
format is undocumented publicly, and no motion files exist in any accessible
archive. What is NEW since Oct 22: `sp00nznet/vf5` (ps3recomp, renders loading
screens only, not under active development) and VF5 R.E.V.O. World Stage
(Oct 30, 2025 — Dural playable as DLC). Neither is a moveset/motion teardown.

## Repo inventory first (verified live via GitHub API, main branch)

`vf-*` kits in `game/assets/movesets/` — 7 files, all community-movelist
transcriptions in Tekken notation (v2 contract), NOT extracted animation:

| file | bytes | notes |
|---|---|---|
| `game/assets/movesets/vf-akira.json` | 16484 | |
| `game/assets/movesets/vf-elblaze.json` | 15102 | |
| `game/assets/movesets/vf-kage.json` | 11759 | |
| `game/assets/movesets/vf-jeffry.json` | 13320 | Bannon's canon base (25 moves per brief; file holds the kit) |
| `game/assets/movesets/vf-leifei.json` | 831233 | 812 moves, full kit on the Lei bank |
| `game/assets/movesets/vf-sarah.json` | 11886 | |
| `game/assets/movesets/vf-wolf.json` | 11252 | |
| `game/data/moveset-library/banks/vf.json` | 47423 | |
| `game/data/moveset-library/banks/vf5.json` | 115728 | |

**Missing from the repo: `vf-goh.json`, `vf-brad.json`, `vf-dural.json` — no
Goh, no Brad Burns, no Dural kit exists anywhere in the repo.** That is exactly
the Kutz / Realizzt / Zen gap this lane was sent to close, and no outside
source closes it either (see below).

Related repo docs read: `docs/research/VF5-MOTION-GAP-2026-10-22.md`,
`docs/handoffs/moveset-library-vf5-format.md`,
`docs/anim/VF5-DURAL-ANIM-GAP-20261023.md`,
`docs/research/VF5-FULL-INTEGRATION-2026-10-22.md` (listed),
`docs/decisions/2026-10-22-vf5-integration.md` (listed).

## archive.org — LIVE check 2026-11-20 (search + metadata API, files inspected)

1. `title:(virtua fighter 5)` — 57 hits. Contents: G4TV/GameTrailers
   gameplay videos and trailers, cabinet marquee/movelist art
   (`vf-5-us-lindbergh-marquee`), Xbox 360 game manuals (FR + EU),
   a VF5 R.E.V.O. 4x3 aspect-ratio patch (`virtua_fighter_5_-4x3`), one
   XPS Vanessa model (`xnalara-xps-vanessa-virtua-fighter-5-nude-by-cunihinx-dczm-5xl.-7z_202603`).
   **No game dump, no moveset, no motion extraction, no teardown.**
2. `(virtua fighter) AND mediatype:software` — 309 hits. Two VF5 items:
   - `vf5revo_101` — "VF5 R.E.V.O. ver 1.01". Files inspected: 4 DLLs only
     (`media/libxess.dll` 120,278,928 B; `media/amd_fidelityfx_dx12.dll`
     6,634,192 B; `media/gpu_info.dll` 592,384 B; `media/libxell.dll`
     237,968 B). Description states it requires ownership of the game on
     Steam to run. **A version patch, not the game, not a teardown.**
   - `games_20250220` — "Virtua Fighter V PS3". Files inspected:
     `Virtua Fighter V PS3/GAMES.rar` 3,686,456,692 B + disc-cover scans
     (JPG/PDF). **A full PS3 game dump (the game itself), not an extracted
     teardown.** Even if pulled, its motion data (if present) sits in an
     undocumented format — see the Oct 22 gap doc: extracting usable motion
     from it is a days-to-weeks binary RE project, not already-cracked work.
   - Also present in the 309: `vf4evo`, `vf4tuned`, `virtua-fighter-3-recomp-windows`
     (VF3 Recomp — a different game, not VF5), `sega-universe-fix`.
     **No VF5 recomp exists** (VF1 Recomp and VF3 Recomp exist; VF5 does not).

## Fan / modding-community / public-repo search (live 2026-11-20)

| Source | What it is | Why it does NOT count |
|---|---|---|
| `CookiePLMonster/YAMP` (github.com/CookiePLMonster/YAMP) + `silentsblog.com/2021/06/01/yamp-virtua-fighter-5-final-showdown-pc/` | Launcher that runs VF5: Final Showdown standalone on PC using the Dragon Engine files from a Steam copy of Yakuza 6. No audio; 2 gamepads for versus. | A game launcher, not an extraction. Needs a Steam copy of Yakuza 6 (not owned per brief — owner owns VF5 on Xbox). Produces no moveset/animation files. |
| VF5FS Unlocker (same author, 2021) | Single-flag plugin unlocking full console VF5FS inside Yakuza 6 / Like a Dragon (Steam). | Same as YAMP: plays the game, extracts nothing. |
| `blueskythlikesclouds/MikuMikuLibrary` (Miku Miku Model) | Opens/rips/exports VF5 (same engine family as Project DIVA) models, textures, motions; `FarcPack` extracts `.farc`; needs `obj_db.bin`, `tex_db.bin`, `bone_data`, `mot_db` from the game's `rom/objset` + `rom/rob` folders. | A TOOL, not a teardown. It can read motion files only if you already have the game files (`mot_db` + `mot_*` farcs). No pre-extracted Goh/Brad/Dural motion dump ships with it or anywhere it points to. |
| `objset` (Rust lib, SEGA `_obj.bin`) via velocityra.github.io/awesome-game-file-format-reversing | Reads VF5 model object-sets. | Models only, not motion/movesets. |
| `sp00nznet/vf5` (ps3recomp static recompilation, title BLUS30020) | PS3 VF5 statically recompiled to native PC. Status per its own README: "Renders its NOW LOADING, CRIWARE and AM2 screens; zero SPURS and zero PSN imports". "Not under active development". | Not a working game, not a moveset, not motion data. Loading screens only. |
| RGG Modding Wiki — `modding.rgg-games.wiki/wiki/Virtua_Fighter_5:_Ultimate_Showdown` | Documents VF5US/REVO Dragon Engine layout: `chara` PAR = character models; `motion` PAR is a leftover from Yakuza: Like a Dragon. Tools: ParManager, yk_gmd_io, FighterCommander, HActLib, gmt_lib. | Documentation + generic Dragon Engine tools. No VF5 character-animation extraction exists in that ecosystem; VF5US motion is not a documented extractable set. |
| VFDC (virtuafighter.com) / GameFAQs Brad guide / vfdc wiki command lists | Community movelists, frame data, combo lists, video movelists (YouTube playlist incl. Brad Burns + Goh Hinogami). | Text movelists / videos. The repo's 7 existing `vf-*` kits are already built from exactly this class of source. No animation/motion data. |
| DeviantArt VF5FS mods (ogami4, glowsero) | Costume/model swaps via FarcPack on PS3 `rom/objset/*itm.farc` (`gohitm.farc`, `braitm.farc`, `kagitm.farc`...). | Model/texture swaps only. No motion. |
| Torrent/magnet listings ("Virtua Fighter 5 FS", 1.8 GB, `*itm.farc` files) | Raw PS3 VF5FS game files (`braitm.farc` 38.5 MB, `jefitm.farc` 38.3 MB, `kagitm.farc` 40.1 MB, `krtitm.farc` 50.7 MB, `vanitm.farc` 41.0 MB). | The raw game files, not a teardown. Same undocumented-motion problem as the archive.org PS3 dump. |
| TeknoParrot / Lindbergh loader (`lindbergh-loader/lindbergh-loader`, `zognic/lindbergh-install`) | Runs arcade VF5 / VF5FS (Lindbergh) on PC. | An emulator/loader. Extracts no movesets or animations. |
| VF1 Recomp / VF3 Recomp (recomplauncher.org, archive.org `virtua-fighter-3-recomp-windows`) | Static recompilations of VF1 and VF3. | Different games. No VF5 recomp exists. |
| GitHub code search `Virtua Fighter 5 decomp/recomp/extractor/moveset` | Hits are ps3recomp (above), lindbergh-install, virtuanalytics_dashboard (match-data viz), match-indexer (video timestamps). | No moveset/motion extraction repo. |

## What WOULD close the gap (not done here — owner/coordinator call)

1. **Full-game-files route (closest available):** the repo already holds
   release `vf5-ps3-v1` (89 assets: all 19 fighters' `*itm.farc` models incl.
   `gohitm.farc` 43,611,682 B, `braitm.farc` 47,006,173 B,
   `duritm.farc` 25,510,344 B, plus `obj_db.bin`, `tex_db.bin`, and the
   8-part 4 GB `vf5-500m.part_*` split archive). Per the Oct 22 gap doc the
   split archive MAY contain motion files but is unverified (high-entropy,
   never fully pulled). Even if motion files are in it, the format is
   undocumented — a dedicated multi-day binary-RE lane (header ID, bone
   tracks, keyframe decompression, converter to `wh-anim/1`), exactly as
   `docs/anim/VF5-DURAL-ANIM-GAP-20261023.md` specifies. That is new
   reverse-engineering work, NOT pulling already-torn-down work, so this
   lane did not start it silently.
2. **REVO/Dragon Engine route:** VF5 R.E.V.O. (Steam, Jan 27, 2025) or
   Yakuza 6 Steam files + ParManager/HActLib/gmt_lib tooling. Requires a
   Steam purchase the owner replaced with this order, and no public
   extracted VF5 animation set exists for it either.
3. **Community-movelist route (partial, already the repo's method):** Goh
   and Brad movelists exist as text/video (VFDC, GameFAQs, YouTube video
   movelists). A `vf-goh.json` / `vf-brad.json` could be transcribed in the
   same v2 contract as the 7 existing kits — move NAMES/inputs/frames, no
   animation. That is transcription, not a teardown pull; it does not feed
   the motion converter gap and was not done in this lane (it would be
   hand-built data, and the brief forbids silent hand-tooled rebuilds).

## Still missing (exact gap)

- **Kutz — VF5 Goh source:** no `vf-goh.json`, no Goh motion. Still plays King.
- **Realizzt — VF Brad Burns source:** no `vf-brad.json`, no Brad motion.
  Still plays Jin.
- **Zen — Dural bank:** 640 Dural moves in a file, bank lives in private
  builds only; no Dural motion/animation anywhere. Zen identity call
  (ROSTER Julia vs file Dural vs index Heihachi) NOT decided here — owner call.
- **VF5 motion converter:** still no converter; PR #713 still open. No
  public VF5 motion format documentation was found anywhere in this search.

## Sources / licence log

- All sources above are public fan/mod/community work; SEGA owns VF5.
  Licence status never gated the search (LICENCE-NOT-A-GATE); nothing was
  pulled, so nothing needs a licence line next to a pulled file.
- Key URLs (verbatim from search results):
  - https://github.com/CookiePLMonster/YAMP
  - https://silentsblog.com/2021/06/01/yamp-virtua-fighter-5-final-showdown-pc/
  - https://github.com/blueskythlikesclouds/MikuMikuLibrary
  - https://modding.rgg-games.wiki/wiki/Virtua_Fighter_5:_Ultimate_Showdown
  - https://github.com/sp00nznet/ps3recomp
  - https://velocityra.github.io/awesome-game-file-format-reversing/games/s/
  - https://archive.org/details/vf5revo_101
  - https://archive.org/details/games_20250220
