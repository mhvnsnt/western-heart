# Street Fighter X Tekken — sources

Checked live 2026-11-20. Nothing is vendored in this directory — this
is a record of what was searched and found, so the next lane does not
re-search it. Licence/source is logged honestly next to each item.

## Searched

| Source | What was found | Verdict |
|---|---|---|
| archive.org (advancedsearch, software filter) | `street-fighter-vs-tekken` — game ISO 4,689,100,800 B; `street-fighter-x-tekken_202409` — game files ZIP 1,656,249,288 B; `street-fighter-x-tekken_202508`; `PS3_BLES01252_Updates` / `PS3_BLUS30722_Updates` — update pkgs; PSVita image; RPCS3 pack | Raw game dumps only — NOT teardowns, NOT pulled |
| EventHubs / GameFAQs, Mar 2012 | ShiroiKaze Xbox 360 disc rips: full DLC cast, "fully rigged, animation files, voice files" | Complete at the time; NO surviving downloadable pack — images only |
| Models Resource | No SFxT game page exists | Nothing to pull |
| Sounds Resource (Xbox 360) | SFxT voices/sounds, ripped by Random Talking Bush | Audio only |
| TekkenMods | SFxT tutorials (EMM/EMG tools); T7 voice mods using SFxT sounds; T8 SFxT outfit remakes | Tools/mods, not a teardown |
| DeviantArt | mariokart64n SFxT Importer (3ds Max script); Mukoj-in MMD Chun-Li (redistribution prohibited) | Single-artist tools/models, not pulled |
| GitHub / Recompendium | No SFxT recomp or decomp repo; "SFxT RECOMP" is a Facebook logo image only (Oct 11, 2026, Daniel Robson) | Nothing to pull |
| MUGEN Guild | SFxT PC modding thread (costume unlocker, mesh tools, `C:\Program Files (x86)\Capcom\Street Fighter X Tekken\resource\...`) | Mods, not a teardown |

## Shared toolchain (pulled under SFIV)

The SFIV bac/bcm toolchain is pulled in `../street-fighter-4/` —
`tools/sf4tools/` (Dantarion, MIT, source commit
`e5c17132f3b6e63f66150c3a347a9e8f6e0d73a4`). SFxT uses the same
formats, so that toolchain reads SFxT files. No separate SFxT pull
was needed or made.
