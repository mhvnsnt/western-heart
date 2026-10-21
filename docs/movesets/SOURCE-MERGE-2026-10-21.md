# Moveset source merge — 2026-10-21 (T8 + T7 + fixed T3 + donors, additions only)

Owner: "We need move string, combos, different moves and move inputs, everything Tekken and the teardown files have, but Tekken as the base" · "If ur just using stuff from t3 not the other then u will be limiting us" · "why would you decrease fighter moves?"

Tool: `tools/moveset-merge/merge_sources.py` (+ `notation.py`, `bases.json`). Runs on top of PR #407's history union (main already = union of all 548 historical versions). Raw per-fighter numbers: `docs/movesets/SOURCE-MERGE-2026-10-21.json`.

## Guarantees (enforced by the tool's guard; any failure writes nothing)

- every existing move key kept with a byte-identical payload; strings/specials only appended (verified again against HEAD: 0 files with a lost or changed move)
- every new move carries `merge_source` resolving to a record in a vendored dataset (T8 wavu id, T7 t7chicken id, T3 bank row) or a donor file
- every input that fired a move before still fires one (`slots`), except the owner-directed Doc Frank exclusion (Gun Jack proxy moves never take a Doc Frank slot): listed below
- files keep their own JSON formatting (detected by byte-exact round-trip), so the diff is additions: 740,734 lines added, 34 changed (trailing commas / `[]` that gained entries)

## What a fighter gets

Sources per fighter come from `bases.json` (owner overrides, cited) or the file's `tekken_base` (anchored match): T8 = all 41 wavu characters, T7 = 47 t7chicken characters, T3 = the 20 decoded banks via the fixed generator (strings + EXE common-table throws). `slots` maps every notation to the move that fires by default: WH signature > T8 base > T7 base > T3 base > curated/donor > proxy bank. Every other move stays assignable in the moveset editor.

| Fighter | Built on | Moves before → after | Default inputs (slots) | was playable | Added |
|---|---|---:|---:|---:|---|
| armor-king | t8:armor_king, t7:armorking | 125 → 500 | 247 | 9 | t8 +173, t7 +202 |
| awapop | t8:nina, t7:nina, t3:nina | 340 → 909 | 402 | 106 | t8 +6, t7 +354, t3 +209 |
| baek-master-white | donors:baek | 113 → 122 | 36 | 33 | donor +9 |
| bob | t8:bob, t7:bob | 115 → 557 | 238 | 10 | t8 +161, t7 +281 |
| bruno | t7:miguel | 315 → 328 | 170 | 70 | t7 +13 |
| burger | t8:bob, t7:bob | 264 → 552 | 240 | 85 | t8 +7, t7 +281 |
| burger-demon | t8:bob, t7:bob | 24 → 466 | 237 | 0 | t8 +161, t7 +281 |
| burger-speed-demon | t8:bob, t7:bob | 12 → 454 | 233 | 0 | t8 +161, t7 +281 |
| burger-the-mouth | t8:bob, t7:bob | 12 → 454 | 230 | 0 | t8 +161, t7 +281 |
| byou | t7:lei, t3:lei | 157 → 947 | 444 | 59 | t7 +524, t3 +266 |
| chordz | t8:lars, t7:lars | 145 → 452 | 203 | 48 | t8 +121, t7 +186 |
| cyborgx | t8:alisa, t7:alisa | 334 → 624 | 302 | 92 | t8 +6, t7 +284 |
| demonio | t8:jin, t7:jin, t3:jin | 270 → 658 | 299 | 83 | t8 +7, t7 +198, t3 +183 |
| demonio-bloodline-ember | t8:jin, t7:jin, t3:jin, donors:demonio | 147 → 662 | 299 | 49 | t8 +128, t7 +198, t3 +183, donor +6 |
| demonio-human | donors:demonio | 102 → 271 | 157 | 10 | donor +169 |
| demonio-winged | t8:devil_jin/jin, t7:deviljin/jin, t3:jin, donors:demonio | 175 → 1039 | 394 | 87 | t8 +148, t7 +416, t3 +199, donor +101 |
| diablo | t8:heihachi, t7:heihachi, t3:heihachi | 288 → 642 | 297 | 73 | t8 +7, t7 +183, t3 +164 |
| dio | t7:akuma | 265 → 275 | 134 | 59 | t7 +10 |
| doc-frank-hood | t3:bosconovitch, donors:docfrank | 101 → 476 | 176 | 13 | t3 +266, donor +109 |
| doc-frank-machine-shop | t3:bosconovitch, donors:docfrank | 147 → 517 | 176 | 50 | t3 +266, donor +104 |
| doc-frank-wowomomo | t3:bosconovitch, donors:docfrank | 101 → 476 | 176 | 13 | t3 +266, donor +109 |
| docfrank | t3:bosconovitch | 114 → 380 | 176 | 30 | t3 +266 |
| dxmmii-patchwork | donors:dxmmii | 150 → 154 | 57 | 52 | donor +4 |
| gyou | t8:hwoarang, t7:hwoarang, t3:hwoarang | 149 → 872 | 358 | 51 | t8 +209, t7 +326, t3 +188 |
| jin_soul | t8:yoshimitsu, t7:yoshimitsu, t3:yoshimitsu | 123 → 1012 | 536 | 39 | t8 +312, t7 +386, t3 +191 |
| kai | t8:eddy, t7:eddy, t3:eddy | 146 → 853 | 376 | 48 | t8 +152, t7 +337, t3 +218 |
| kingtyrant | t8:eddy, t7:eddy, t3:eddy | 286 → 848 | 363 | 73 | t8 +7, t7 +337, t3 +218 |
| kinpo | t8:asuka, t7:asuka | 285 → 525 | 229 | 91 | t8 +8, t7 +232 |
| koreshi | donors:vega/sf-vega | 329 → 572 | 351 | 61 | donor +243 |
| kronos | donors:zangief/sf-zangief | 257 → 388 | 88 | 50 | donor +131 |
| kronos-attire2 | donors:kronos/zangief/sf-zangief | 142 → 380 | 88 | 33 | donor +238 |
| lili | t8:lili, t7:lili | 349 → 508 | 215 | 74 | t8 +148, t7 +11 |
| marduk | t7:marduk | 130 → 340 | 155 | 9 | t7 +210 |
| mariposa | t8:zafina, t7:zafina | 223 → 372 | 189 | 63 | t8 +146, t7 +3 |
| mariposa-monarch | t8:zafina, t7:zafina, donors:mariposa | 351 → 508 | 202 | 77 | t8 +146, t7 +11 |
| michiko | t7:katarina | 332 → 344 | 159 | 102 | t7 +12 |
| negativo | t7:negan | 270 → 282 | 129 | 71 | t7 +12 |
| nightwolf | t7:julia, t3:julia | 135 → 554 | 221 | 30 | t7 +236, t3 +183 |
| pantera | t8:king, t7:king, t3:king | 370 → 873 | 394 | 92 | t8 +7, t7 +297, t3 +199 |
| phantom | t8:yoshimitsu, t7:yoshimitsu, t3:yoshimitsu | 432 → 1019 | 538 | 90 | t8 +8, t7 +386, t3 +193 |
| purplerain | t8:lee, t7:lee | 298 → 569 | 264 | 99 | t8 +6, t7 +265 |
| rave | t7:lei, t3:lei | 648 → 926 | 419 | 81 | t7 +12, t3 +266 |
| retsu | t8:bryan, t7:bryan, t3:bryan | 111 → 685 | 292 | 31 | t8 +168, t7 +266, t3 +140 |
| rin | t8:jin, t7:jin, t3:jin | 149 → 659 | 307 | 50 | t8 +128, t7 +198, t3 +184 |
| sakura | t8:xiaoyu, t7:xiaoyu, t3:xiaoyu | 306 → 764 | 325 | 65 | t8 +7, t7 +259, t3 +192 |
| samura1 | t8:jack-8, t7:jack-7, t3:gunjack | 342 → 860 | 368 | 86 | t8 +7, t7 +298, t3 +213 |
| scimitar | t8:shaheen, t7:shaheen | 229 → 362 | 161 | 75 | t8 +8, t7 +125 |
| sf-akuma | t7:akuma | 32 → 168 | 119 | 19 | t7 +136 |
| sha | t8:xiaoyu, t7:xiaoyu, t3:xiaoyu | 303 → 762 | 325 | 64 | t8 +7, t7 +259, t3 +193 |
| skull | t8:bryan, t7:bryan, t3:bryan | 275 → 688 | 291 | 92 | t8 +6, t7 +266, t3 +141 |
| slice | t8:dragunov, t7:dragunov | 331 → 486 | 208 | 87 | t8 +141, t7 +14 |
| star | t8:xiaoyu, t7:xiaoyu, t3:xiaoyu | 282 → 908 | 402 | 70 | t8 +175, t7 +259, t3 +192 |
| torch | t8:anna, t7:anna, t3:anna | 307 → 892 | 392 | 85 | t8 +7, t7 +354, t3 +224 |
| tou | t8:paul, t7:paul, t3:paul | 143 → 640 | 282 | 48 | t8 +143, t7 +185, t3 +169 |
| waterfall | t7:josie | 146 → 341 | 159 | 48 | t7 +195 |
| yukihyo | t8:armor_king, t7:armorking | 342 → 534 | 263 | 94 | t8 +173, t7 +19 |
| zen | t8:heihachi, t7:heihachi, t3:heihachi | 148 → 639 | 297 | 53 | t8 +145, t7 +183, t3 +163 |
| zui | t8:steve, t7:steve | 156 → 614 | 291 | 59 | t8 +171, t7 +287 |

**Totals (58 fighters): 12673 → 33662 moves.**

## Owner-directed exclusions

- **doc-frank-hood**: inputs that only Gun Jack proxy moves answered and Bosconovitch has no move for, so they stay empty: `d/f+2+3`, `f+1` (the moves remain in the file)
- **doc-frank-machine-shop**: inputs that only Gun Jack proxy moves answered and Bosconovitch has no move for, so they stay empty: `d,d/f,d,d/f+1+2`, `d/b+1`, `d/b+1,1`, `d/b+1,1,1`, `d/b+1,1,1,2`, `d/b+2+3`, `d/b,n,f+2`, `d/f+1+3`, `d/f+2+3`, `d/f+2+4`, `f+1`, `f+2+3`, `u/b+1`, `u/b+3`, `u/f+3`, `u/f+3+4,1`, `u/f+3+4,1,2`, `u/f+3+4,1,2,1`, `u/f+3+4,1,2,1,2`, `u/f+3+4,2`, `u/f+3+4,2,1`, `u/f+3+4,2,1,2`, `u/f+3+4,2,1,2,1` (the moves remain in the file)
- **doc-frank-wowomomo**: inputs that only Gun Jack proxy moves answered and Bosconovitch has no move for, so they stay empty: `d/f+2+3`, `f+1` (the moves remain in the file)
- **docfrank**: inputs that only Gun Jack proxy moves answered and Bosconovitch has no move for, so they stay empty: `d,d/f,d,d/f+1+2`, `d/b,n,f+2`, `f+1` (the moves remain in the file)

## Not merged (no decoded Tekken data for their base) — 38 files

These keep exactly what they had. Their bases need other teardowns wired (SF 3D, DOA4 movesets, Urban Reign, No Mercy / WMXIX, KOF): baek (Baek), blanka (Blanka (SF)), cainelias (Undertaker (WWE)), charger (Blanka (SF) — fighter replaced by CHARGER (owner 2026-10-20)), deathfang (Iori Yagami (KOF)), doa-ayane (Ayane (DOA4 / DOA Ultimate)), doa-bass (Bass Armstrong (DOA5 Last Round / DOA Ultimate)), doa-hayabusa (Ryu Hayabusa (DOA5 Last Round)), doa-jannlee (Jann Lee (DOA4 / DOA Ultimate)), doa-kasumi (Kasumi (DOA5 Last Round)), doa-tina (Tina Armstrong (DOA4 / DOA Ultimate)), dxmmii (Mokujin), hugo (Hugo Andore (Final Fight/SF)), iori (Iori Yagami (KOF)), kutz (Goh Hinogami), raiden (Big Bear / Raiden (Fatal Fury/KOF)), realizzt (Brad Burns), ryuji (Ryuji Yamazaki (KOF XV) / The Rock hybrid), ryuji-rock (Ryuji Yamazaki (KOF) x The Rock), sf-blanka (Blanka (SF)), sf-cammy (Cammy (SF) — Akuma-pattern translation), sf-chunli (Chun-Li (SF) — Akuma-pattern translation), sf-dhalsim (Dhalsim (SF) — Akuma-pattern translation), sf-guile (Guile (SF) — Akuma-pattern translation), sf-ken (Ken (SF)), sf-mbison (M. Bison (SF) — Akuma-pattern translation), sf-ryu (Ryu (SF)), sf-sagat (Sagat (SF) — Akuma-pattern translation), sf-vega (Vega (SF)), sf-zangief (Zangief (SF)), sunra (Pac-Man), thor (Ganryu), vainabel (Bass Armstrong), vega (Vega (SF)), vf-akira (Akira Yuki (Virtua Fighter 5 Final Showdown)), vf-kage (Kage-Maru (Virtua Fighter 5 Final Showdown)), vf-sarah (Sarah Bryant (Virtua Fighter 5 Final Showdown)), zangief (Zangief (SF)).

## Known limits (honest)

- The game engine resolves `moves[exact key]`; the 2026-10-21 engine change makes it read `slots` + support WS./FC./SS./BT./stance/motion inputs. Until that lands, new keys like `1~t8.eddy` are listed but not fired.
- Animation: new T7/T8 moves carry `anim_t3` = the same base character's decoded T3 row for the same notation, else the nearest by limb/class/startup (flagged approximate). Rows still have to be baked for the 10 banks PR #405 added (no rows.pack.json yet).
- Damage scaling: new T8 moves ×100/180 and T7 ×100/170 to WH's 100 HP (raw kept in `damage_raw`). Earlier imports (PR #357 T8 cluster, 74efb3fb T7) kept raw T7/T8 damage. Those payloads are untouched here and flagged in the Muse handoff.
- Character-specific stances (Lei SNK/DRG/PHX...) are keyed; the engine needs stance-entry data to reach them (T8 `notes` carry the transitions).
- Doc Frank's Dr. Gero / Mojo Jojo / Dr. Weird inspired moves and King Tyrant's Booker T moves need WWE/other data that isn't decoded yet. Not invented.
