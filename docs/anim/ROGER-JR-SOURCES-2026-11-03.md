# MENAJERII source kit (Roger Jr.): every game, every holding, every community source (2026-11-03)

Owner instruction (2026-11-03, verbatim): "get the roger moves from whatever game he's in and from the modding community"

This doc continues `docs/anim/TTT2-ROGER-ANIM-GAP-20261023.md` and
`docs/movesets/ROGER-BANK-AUDIT-2026-11-02.md`. Source names appear here only because the topic is
getting the data over (names law, `docs/rules/NO-SOURCE-CHARACTER-NAMES.md`). In the game she is
MENAJERII.

## Result in one paragraph

Her exact move list and frame data now sit in the repo as a data table:
`game/data/menajerii_source_frame_table.json` (wh-frame-row/1, 114 source rows, every row
`animation: "pending"`). It comes from wavu.wiki's TTT2 movelist (CC0), with three cross-checks:
RBNorway TTT2 frames (MIT, via harounb), the wavu Tekken 5/DR page, and our own TTT2 MVLT and
T6 PSP COM decodes. Her moveset file is not changed by this PR. No real motion was found in any
holding outside the TTT2 containers, which another lane is decoding (not touched here). The
nearest real motion sources are (a) Tekken 8, where she ships as DLC on 2026-11-12 (early access)
and 2026-11-17 (everyone), and (b) emulator-memory extraction with TKMovesets2. The repo can
already read that tool's animation format through `tools/anim/t7_anim64.py`.

## 1. Which games have the character

| Game | Character | Playable? | Source |
|---|---|---|---|
| Tekken 2 | Roger (the father) | yes (hidden) | https://tekken.fandom.com/wiki/Roger (infobox `game=`) |
| Tekken Tag Tournament | Roger | yes | same |
| Tekken 3 | none | no. Roger is absent from T3 (not in the fandom game list, not in our T3 roster) | same; `teardown/tekken3/` |
| Tekken 4 | none | no | https://tekken.fandom.com/wiki/Roger_Jr. |
| Tekken 5, 5: Dark Resurrection | Roger Jr. | yes (unlock) | https://tekken.fandom.com/wiki/Roger_Jr. |
| Tekken 6, 6: Bloodline Rebellion | Roger Jr. | yes | same |
| Tekken Tag Tournament 2 | Roger Jr. (+ Alex, a near-clone) | yes | same; https://wavu.wiki/t/Alex_movelist |
| Tekken 7 | none | no (cut) | same (Trivia, VG247 ref) |
| Tekken 8 | Roger Jr. | DLC, Season 3. Early access 2026-11-12, general release 2026-11-17. **Not released yet** | https://www.gematsu.com/2026/10/tekken-8-dlc-character-roger-jr-launches-november-11-for-season-3-character-pass-owners-november-16-for-all , https://www.tekken-official.jp/tekken_news/?p=3712 |

Moves come from Roger Jr. (T5 onward), not from the father's T2/TTT1 kit. TTT2 is the kit her
file is built on (`tekken_base` of her moves).

## 2. What our holdings already have, per game

| Game | Holding | Moves / frames | Motion |
|---|---|---|---|
| TTT2 | `game/assets/ttt2/movesets/rog.json` (MVLT decode of data018, 91 records) | in-game move list: names + notation, no frames | MOTA is in data004 (21 MOTA, per `teardown/tekken-tag-tournament-2/` docs). **Another lane is decoding it. Not touched here.** |
| Tekken 6 (PSP) | `teardown/tekken6/movesets/t6psp-roger-moveset{,-v2,-v3}.json` (COM container, gzip idx67 entry 723, sha256 `d79830c4…`) | 219 command records, 195 fully decoded inputs (round-15 glyph map), English + 4 languages, no frames | The COM file has only 6 empty/stub MOTA headers. Bulk motion is still encrypted (`teardown/tekken6/MOTION-UNBLOCK-2026-10-23.md`) |
| Tekken 5 (PS2) | `teardown/tekken5/` survey only. ISO deleted after survey (archived at Internet Archive) | none | `TK5DATA2.BIN` romD manifest lists 498 `gym_<code>_*.dat` motion files over 109 codes. The file-table to offset map is not reversed, and the character code is not identified |
| Tekken 2 / TTT1 | none in WH or GRE | none | none |
| GRE (`mhvnsnt/game-reverse-engineering`) | full-tree grep 'roger': 0 hits (2026-11-03, `docs/proof/2026-11-03/smutbase6-final-three/job1-job3-evidence.md`) | none | none |

Open branches and PRs were checked on 2026-11-03 for the other lane's TTT2 motion work. No
pushed branch or PR carries it yet (closest: `feat/ttt2-data001-data028-decode-20261030`,
`feat/ttt2-teardown-100`), so there was nothing to build on.

## 3. Community sources (URLs + terms)

### Move list + frame data (used)
| Source | URL | Terms | Used as |
|---|---|---|---|
| wavu.wiki, Roger Jr. movelist (Tag 2), revid 63304 | https://wavu.wiki/t/Roger_Jr._movelist_(Tag_2) | CC0-1.0 | **primary**: `docs/t7t8-reference/frame-data-ttt2/roger_jr.wavu.json` |
| wavu.wiki, Roger Jr. movelist (Tekken 5/DR), revid 63231 | https://wavu.wiki/t/Roger_Jr._movelist_(Tekken_5) | CC0-1.0 | lineage cross-check: `docs/t7t8-reference/frame-data-t5/roger_jr.wavu.json` |
| RBNorway TTT2 frame data, ripped by harounb (commit `070fa2ceb46712c741fb3dc1ab8df0690c9a69dd`) | https://github.com/harounb/tekken-frame-data/tree/main/ttt2 (upstream http://rbnorway.org/ttt2-frame-data/) | MIT (harounb). RBNorway asks for credit | cross-check: `docs/t7t8-reference/frame-data-ttt2/roger_jr.rbnorway.json` |

### Move list + frame data (found, not used, recorded for completeness)
- tekkendocs.com TTT2 page (same RBNorway data): https://tekkendocs.com/tag2/framedata/RogerJrTUD-converted.html
- wavu.wiki Tekken 6 page (stub, 1 move): https://wavu.wiki/t/Roger_Jr._movelist_(Tekken_6)
- wavu.wiki Alex page (only the moves that differ from Roger Jr.): https://wavu.wiki/t/Alex_movelist
- SDTekken T5DR frame data: https://sdtekken.com/t5dr/rogerjr-frame-data/ (no licence stated)
- Avoiding The Puddle TTT2 frame data (archive): https://web.archive.org/web/20191203181433/http://www.avoidingthepuddle.com/ttt2-frame-data/
- Tekken Zaibatsu TTT2 wiki (archive): https://web.archive.org/web/20201206040113/http://www.tekkenzaibatsu.com/wiki/Tekken_Tag_Tournament_2
- Tekken Wiki (Fandom) movelists, CC-BY-SA: https://tekken.fandom.com/wiki/Roger_Jr. (Moves section). This is her file's current `t3_source`.
- Wavu's list of classic resources: https://wavu.wiki/t/Classic_Tekken_Resources

### Motion (real animation), community tools and mods
| Source | URL | Terms | Status |
|---|---|---|---|
| TKMovesets2 (Kiloutre): extracts movesets **with animations** from emulator memory. TTT2 (RPCS3/CEMU), Tekken 6 (RPCS3), Tekken 5 DR (RPCS3), T7 | https://github.com/Kiloutre/TKMovesets , releases https://github.com/Kiloutre/TKMovesets/releases | GPL-3.0 (tool). Extracted data is Bandai Namco game data | **Best non-container route.** Our `tools/anim/t7_anim64.py` is already a port of its `Animations_T_x64.cpp` 0x64 decoder (and `t7_anim64_to_c8.py`). Needs the game running in an emulator (Windows tool reading process memory), so it was not run on this box |
| TekkenMovesetExtractor (predecessor, archived) | https://github.com/Kiloutre/TekkenMovesetExtractor | GPL-3.0 | superseded by TKMovesets2 |
| BlenderTekkenAnimationImporter (Kiloutre) | https://github.com/kiloutre (pinned repo) | see repo | reads the same animation format into Blender |
| TekkenMods #7292 "TTT2 Roger Jr. with Tekken 8 Mechanics" (Melonpizza, 2026-07-03): TKMovesets2 moveset, release zip 10.2 MB | https://tekkenmods.com/mod/7292/ttt2-roger-jr-with-tekken-8-mechanics | page permits modify / use assets | **Not downloaded.** The download link answers 403 (bot wall) from this box. Not verified that it bundles the animation binaries |
| Nexus Tekken 7 mod 67 "Roger Jr." (Victor Selkvotsk): moveset via the extractor on Steve | https://www.nexusmods.com/tekken7/mods/67 | Nexus terms | not downloaded |

## 4. What got wired (this PR)

- `game/data/menajerii_source_frame_table.json` is built by
  `tools/frame-data/build_menajerii_source_table.py` from the files above.
  - 114 source rows. Each carries the wh-frame-row/1 fields that parse exactly (command, hit_level,
    damage, startup, on_block, on_hit, on_ch, tags, transitions), the verbatim wavu values in
    `source_values`, the cross-checks, and the join to her file. Every row has `animation: "pending"`.
  - Join to `game/assets/movesets/menajerii.json`: **90 same move, 12 input conflicts, 12 absent**.
    78 rows have a sourced startup and 109 have a sourced on-block value.
  - **All 12 input conflicts are Kuma-sourced moves (`tekken_base: "Kuma (Tekken 7)"`) sitting on her
    source kit's inputs:** `3`, `4`, `1+2` (Double Spin), `f+1+2`, `df+1`, `db+1` (alt of d+1), `d+1+2`,
    `b+2`, `uf+3` (Helicopter Kick), `ws1`, `ws2`, `f+1+3` (Head Stomp). Her file has 65 Kuma-sourced
    moves in total (the other 53 match no source row, e.g. the HBS stance). This is the move-data side of the
    'kuma' stand-in. The table reports it. It changes nothing.
  - The 12 absent rows include the 2026-11-02 audit gaps, now with sourced frames: `FC.df+2` i16 31,
    `FC.df+4` i21 27, the `f,n,d,df` crouch dash. The audit's unresolved `f+2+4` is settled: wavu lists
    it as the forward Tasmanian Doormat (i15~17, 35). Also absent: the AKS intermediate rows, the BOB charged versions and `WR.4,4`.
  - RBNorway disagrees with wavu on a few values: `2` dmg 16 (wavu) / 18 (RBN basic list),
    `b+2,3,3+4` last hit 22 / 27, `b+4` 27 / 26. wavu (the newer, CC0 source) is primary. Both values are in the table.
- `docs/t7t8-reference/frame-data-ttt2/roger_jr.wavu.json`, `…/roger_jr.rbnorway.json`,
  `docs/t7t8-reference/frame-data-t5/roger_jr.wavu.json`: the source data, pinned (revid / commit).
- `tools/frame-data/wavu_movelist_wikitext.py`: fetches and parses any wavu movelist page from its
  wikitext. wavu's Cargo API, used by `tools/fetch_wavu_framedata.py`, only covers Tekken 8.
- `test/menajerii-source-frame-table.test.mjs`: 6 checks. Rows validate against
  `game/js/frame-data-schema.js`, no clip is bound, the values are spot-checked exactly, and the join stays consistent with her file.

Not done, on purpose:
- Her moveset file is unchanged. Moving these numbers into it needs the damage-source decision the
  2026-11-02 audit left open (her file follows Fandom, while this table follows wavu), plus a call on the 12 Kuma
  moves that hold her source inputs. Both calls belong to the owner. This PR also carries only new files.
- `FIGHTER_BANK menajerii: 'kuma'` is unchanged. Nothing replaces it, because no real Roger Jr. motion exists in an
  extractable form outside the other lane's TTT2 container.

## 5. Still missing, and the shortest path to each

1. **Real motion bank** (`game/assets/anim/ttt2/roger/` target, per the 2026-10-23 GAP doc). Routes, best first:
   - (a) The other lane's TTT2 data004 MOTA decode, once it pushes.
   - (b) Tekken 8 DLC after 2026-11-17. The repo already has a T8 frame-data path (wavu Cargo,
     `tools/fetch_wavu_framedata.py`, add "Roger Jr." to `ALL_T8` once wavu has the page) and T8 clip maps for
     other fighters (`game/assets/anim/t8/clip-maps/`). This needs the owner's T8 install plus the DLC. No Steam login was used here.
   - (c) TKMovesets2 export from an emulator (RPCS3: TTT2 BLES01702, T6 BLES00635, T5DR NPEA00019). It outputs the
     animation format that `tools/anim/t7_anim64.py` already decodes. This has to run on a Windows machine with the
     emulator and the owner's disc image.
   - (d) TekkenMods #7292 release zip. It needs a browser download, and its files must be checked for animation binaries.
2. Frame data for the T6 version (wavu's T6 page is a stub). The T5/DR page is in the repo, and TTT2 is primary.
3. The father's T2/TTT1 kit: not pursued, because no holding exists and her kit is Roger Jr.'s.
