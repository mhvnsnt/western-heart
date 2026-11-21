# Street Fighter X Tekken — teardown

SFxT is the crossover: Street Fighter characters in a Tekken-style tag
system, built on the Street Fighter IV engine. It reuses SFIV's file
formats (`.bac` move scripts, `.bcm` inputs/cancels, `.emo`/`.emz`
models) — so the SFIV toolchain in `../street-fighter-4/tools/sf4tools/`
reads SFxT files too. That is why this directory holds records, not a
separate toolchain pull.

## Why this game matters most for Western Heart

Of the three games in this lane, SFxT is the most directly useful for a
Tekken-style game: its Tekken half (Kazuya, Nina, King, Law, Julia,
Hwoarang, Jin, Heihachi, Paul, Steve, Yoshimitsu, Lars, Alisa, Bob,
Lili, Asuka, Christie, Bryan, Marduk, Kuma, Lei, Raven, Ogre, Jack-X,
Xiaoyu) was re-imagined in the SFIV engine with Tekken signature moves
— the only official crossover of Tekken movesets into the SFIV format
family. A complete SFxT extraction would give Tekken-character movesets
in bac/bcm form, directly comparable to the Tekken-native data WH
already works with.

## What exists

- 2012 disc rips by ShiroiKaze (EventHubs/GameFAQs, Mar 2012): full DLC
  cast + alternates pulled from the Xbox 360 disc with SF4 tools —
  "totally complete... fully rigged, animation files, voice files, etc",
  Ryu and Elena verified with complete animation sets. NO surviving
  downloadable pack was found — only the EventHubs images remain.
- Sound rips: SFxT Xbox 360 voices/sounds on the Sounds Resource
  (ripped by Random Talking Bush; cited by TekkenMods T7 voice mods).
  Audio only.
- Single-character MMD rips (DeviantArt, e.g. Chun-Li by Mukoj-in):
  individual models, redistribution prohibited. Not pulled.
- PC modding scene (EventHubs 2012–2013, MUGEN Guild, TekkenMods):
  costume/model-swap mods for the PC version, built with the SF4 tools.
  Mods, not a teardown.
- archive.org: `street-fighter-vs-tekken` (4.69 GB game ISO),
  `street-fighter-x-tekken_202409` (1.66 GB game files),
  `street-fighter-x-tekken_202508`, PS3 update pkgs, PSVita image,
  RPCS3 pack — all raw game dumps, none a teardown.

## What does NOT exist

- No complete extracted SFxT moveset/animation/model pack.
- No SFxT decomp/recomp project. A "Street Fighter X Tekken RECOMP"
  logo image was posted to Facebook Oct 11, 2026 (Daniel Robson) with
  no repo, no release, no code — logo only, not pullable.
- No Models Resource page for SFxT at all.

## Still missing (exact gap)

Run the SFIV toolchain (`../street-fighter-4/tools/sf4tools/`) against
real SFxT game files (PC install or the owner's Xbox 360 disc) and dump
bac/bcm → JSON, then build the WH bank converter. The 2012 ShiroiKaze
rips are the only known complete extraction and they are lost as a
downloadable pack — if they resurface, that is the pull.
