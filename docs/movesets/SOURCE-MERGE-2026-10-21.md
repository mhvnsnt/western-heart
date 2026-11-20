# Moveset source merge — 2026-10-21 (T8 + T7 + fixed T3 + donors, additions only)

Owner: "We need move string, combos, different moves and move inputs, everything Tekken and the teardown files have, but Tekken as the base" · "If ur just using stuff from t3 not the other then u will be limiting us" · "why would you decrease fighter moves?"

Tools: `tools/moveset-merge/merge_sources.py` (+ `notation.py`, `bases.json`, `engine_check.mjs`, this `report_md.py`). Runs on top of PR #407's history union (main already = union of all 548 historical versions). Raw numbers: `docs/movesets/SOURCE-MERGE-2026-10-21.json`.

## Guarantees

- every existing move key kept with a byte-identical payload; strings/specials only appended (re-verified against origin/main: 0 files with a lost or changed move)
- every new move carries `merge_source` resolving to a record in a vendored dataset (T8 wavu id, T7 t7chicken id, T3 bank row) or a donor file
- `tools/moveset-merge/engine_check.mjs`: every input that fired a move on origin/main's engine fires one on the new engine (96 fighters, 4,370 inputs, 0 failures), apart from the owner-directed Doc Frank exclusion listed below
- files keep their own JSON formatting (byte-exact round-trip), so the diff is additions (patience diff: lines changed only where a comma or an empty `[]` gained entries)

## Owner corrections applied (2026-10-21)

- **Lei Wulong = RAVE / Kiko Tanaka, not Byou** ("Lei wulong is not byou, he is Rave/Kiko tanaka"). Rave gets Lei T7 + Lei T3 + Byou's moves ("U can add leis and byous moves to rave"). Byou keeps exactly its origin/main file; its base is not recorded anywhere (CANON.md:427 "blocked pending the owner's Lei naming decision"), so nothing is merged into Byou until the owner names it.
- **Doc Frank = Bosconovitch** (all four files): Bosconovitch T3, Gun Jack proxy moves never take a default input.

## Per fighter

`slots` maps every notation to the move it fires by default: WH signature > T8 base > T7 base > T3 base > curated/donor > proxy bank. Every other move stays assignable in the moveset editor (loadout).

| Fighter | Built on | Moves on main → now | Inputs (slots) | Fired before | Added (this tool) |
|---|---|---:|---:|---:|---|
| armor-king | t8:armor_king, t7:armorking | 125 → 500 | 247 | 112 | t8 +173, t7 +202 |
| awapop | t8:nina, t7:nina, t3:nina | 340 → 909 | 402 | 215 | t8 +6, t7 +354, t3 +209 |
| baek-master-white | donors:baek | 113 → 134 | 36 | 33 | donor:baek +21 |
| bob | t8:bob, t7:bob | 115 → 557 | 238 | 136 | t8 +161, t7 +281 |
| bruno | t7:miguel | 315 → 328 | 170 | 70 | t7 +13 |
| burger | t8:bob, t7:bob | 264 → 552 | 240 | 125 | t8 +7, t7 +281 |
| burger-demon | t8:bob, t7:bob | 24 → 466 | 237 | 135 | t8 +161, t7 +281 |
| burger-speed-demon | t8:bob, t7:bob | 12 → 454 | 233 | 135 | t8 +161, t7 +281 |
| burger-the-mouth | t8:bob, t7:bob | 12 → 454 | 230 | 135 | t8 +161, t7 +281 |
| chordz | t8:lars, t7:lars | 145 → 452 | 203 | 109 | t8 +121, t7 +186 |
| cyborgx | t8:alisa, t7:alisa | 334 → 624 | 302 | 112 | t8 +6, t7 +284 |
| demonio | t8:jin, t7:jin, t3:jin | 270 → 658 | 299 | 164 | t8 +7, t7 +198, t3 +183 |
| demonio-bloodline-ember | t8:jin, t7:jin, t3:jin, donors:demonio | 147 → 680 | 299 | 170 | t8 +128, t7 +198, t3 +183, donor:demonio +24 |
| demonio-human | donors:demonio | 102 → 677 | 299 | 162 | donor:demonio +575 |
| demonio-winged | t8:devil_jin/jin, t7:deviljin/jin, t3:jin, donors:demonio | 175 → 1057 | 394 | 186 | t8 +148, t7 +416, t3 +199, donor:demonio +119 |
| diablo | t8:heihachi, t7:heihachi, t3:heihachi | 288 → 642 | 297 | 143 | t8 +7, t7 +183, t3 +164 |
| dio | t7:akuma | 265 → 275 | 134 | 59 | t7 +10 |
| doc-frank-hood | t3:bosconovitch, donors:docfrank | 101 → 788 | 176 | 115 | t3 +266, donor:docfrank +421 |
| doc-frank-machine-shop | t3:bosconovitch, donors:docfrank | 147 → 829 | 176 | 137 | t3 +266, donor:docfrank +416 |
| doc-frank-wowomomo | t3:bosconovitch, donors:docfrank | 101 → 788 | 176 | 115 | t3 +266, donor:docfrank +421 |
| docfrank | t3:bosconovitch | 114 → 380 | 176 | 116 | t3 +266 |
| dxmmii-patchwork | donors:dxmmii | 150 → 166 | 57 | 52 | donor:dxmmii +16 |
| gyou | t8:hwoarang, t7:hwoarang, t3:hwoarang | 149 → 872 | 358 | 156 | t8 +209, t7 +326, t3 +188 |
| jin_soul | t8:yoshimitsu, t7:yoshimitsu, t3:yoshimitsu | 123 → 1012 | 536 | 177 | t8 +312, t7 +386, t3 +191 |
| kai | t8:eddy, t7:eddy, t3:eddy | 146 → 853 | 376 | 166 | t8 +152, t7 +337, t3 +218 |
| kingtyrant | t8:eddy, t7:eddy, t3:eddy | 286 → 848 | 363 | 145 | t8 +7, t7 +337, t3 +218 |
| kinpo | t8:asuka, t7:asuka | 285 → 525 | 229 | 109 | t8 +8, t7 +232 |
| koreshi | donors:vega/sf-vega | 329 → 953 | 351 | 89 | donor:vega +480, donor:sf-vega +144 |
| kronos | donors:zangief/sf-zangief | 257 → 772 | 88 | 56 | donor:zangief +371, donor:sf-zangief +144 |
| kronos-attire2 | donors:kronos/zangief/sf-zangief | 142 → 1853 | 88 | 56 | donor:kronos +1196, donor:zangief +371, donor:sf-zangief +144 |
| lili | t8:lili, t7:lili | 349 → 508 | 215 | 93 | t8 +148, t7 +11 |
| marduk | t7:marduk | 130 → 340 | 155 | 67 | t7 +210 |
| mariposa | t8:zafina, t7:zafina | 223 → 372 | 189 | 76 | t8 +146, t7 +3 |
| mariposa-monarch | t8:zafina, t7:zafina, donors:mariposa | 351 → 508 | 202 | 86 | t8 +146, t7 +11 |
| michiko | t7:katarina | 332 → 344 | 159 | 102 | t7 +12 |
| negativo | t7:negan | 270 → 282 | 129 | 71 | t7 +12 |
| nightwolf | t7:julia, t3:julia | 135 → 554 | 221 | 146 | t7 +236, t3 +183 |
| pantera | t8:king, t7:king, t3:king | 370 → 873 | 394 | 160 | t8 +7, t7 +297, t3 +199 |
| phantom | t8:yoshimitsu, t7:yoshimitsu, t3:yoshimitsu | 432 → 1019 | 538 | 150 | t8 +8, t7 +386, t3 +193 |
| purplerain | t8:lee, t7:lee | 298 → 569 | 264 | 121 | t8 +6, t7 +265 |
| rave | t7:lei, t3:lei, donors:byou | 648 → 1080 | 452 | 144 | t7 +12, t3 +266, donor:byou +154 |
| retsu | t8:bryan, t7:bryan, t3:bryan | 111 → 685 | 292 | 184 | t8 +168, t7 +266, t3 +140 |
| rin | t8:jin, t7:jin, t3:jin | 149 → 659 | 307 | 179 | t8 +128, t7 +198, t3 +184 |
| sakura | t8:xiaoyu, t7:xiaoyu, t3:xiaoyu | 306 → 764 | 325 | 120 | t8 +7, t7 +259, t3 +192 |
| samura1 | t8:jack-8, t7:jack-7, t3:gunjack | 342 → 860 | 368 | 158 | t8 +7, t7 +298, t3 +213 |
| scimitar | t8:shaheen, t7:shaheen | 229 → 362 | 161 | 86 | t8 +8, t7 +125 |
| sf-akuma | t7:akuma | 32 → 168 | 119 | 56 | t7 +136 |
| sha | t8:xiaoyu, t7:xiaoyu, t3:xiaoyu | 303 → 762 | 325 | 120 | t8 +7, t7 +259, t3 +193 |
| skull | t8:bryan, t7:bryan, t3:bryan | 275 → 688 | 291 | 163 | t8 +6, t7 +266, t3 +141 |
| slice | t8:dragunov, t7:dragunov | 331 → 486 | 208 | 107 | t8 +141, t7 +14 |
| star | t8:xiaoyu, t7:xiaoyu, t3:xiaoyu | 282 → 908 | 402 | 153 | t8 +175, t7 +259, t3 +192 |
| torch | t8:anna, t7:anna, t3:anna | 307 → 892 | 392 | 193 | t8 +7, t7 +354, t3 +224 |
| tou | t8:paul, t7:paul, t3:paul | 143 → 640 | 282 | 162 | t8 +143, t7 +185, t3 +169 |
| waterfall | t7:josie | 146 → 341 | 159 | 98 | t7 +195 |
| yukihyo | t8:armor_king, t7:armorking | 342 → 534 | 263 | 121 | t8 +173, t7 +19 |
| zen | t8:heihachi, t7:heihachi, t3:heihachi | 148 → 639 | 297 | 157 | t8 +145, t7 +183, t3 +163 |
| zui | t8:steve, t7:steve | 156 → 614 | 291 | 110 | t8 +171, t7 +287 |

**Totals (57 fighters merged): 12,516 → 36,509 moves.**

## Owner-directed exclusions

- **doc-frank-hood**: inputs only Gun Jack proxy moves answered, with no Bosconovitch move: `d/f+2+3`, `f+1` (moves stay in the file)
- **doc-frank-machine-shop**: inputs only Gun Jack proxy moves answered, with no Bosconovitch move: `d,d/f,d,d/f+1+2`, `d/b+1`, `d/b+1,1`, `d/b+1,1,1`, `d/b+1,1,1,2`, `d/b+2+3`, `d/b,n,f+2`, `d/f+1+3`, `d/f+2+3`, `d/f+2+4`, `f+1`, `f+2+3`, `u/b+1`, `u/b+3`, `u/f+3`, `u/f+3+4,1`, `u/f+3+4,1,2`, `u/f+3+4,1,2,1`, `u/f+3+4,1,2,1,2`, `u/f+3+4,2`, `u/f+3+4,2,1`, `u/f+3+4,2,1,2`, `u/f+3+4,2,1,2,1` (moves stay in the file)
- **doc-frank-wowomomo**: inputs only Gun Jack proxy moves answered, with no Bosconovitch move: `d/f+2+3`, `f+1` (moves stay in the file)
- **docfrank**: inputs only Gun Jack proxy moves answered, with no Bosconovitch move: `d,d/f,d,d/f+1+2`, `d/b,n,f+2`, `f+1` (moves stay in the file)

## Not merged (39 files: no decoded Tekken base yet)

They keep exactly what they had; their bases need the other teardowns wired (SF 3D, DOA4, Urban Reign, No Mercy / WMXIX, KOF, VF5): baek (Baek), blanka (Blanka (SF)), byou (Lei Wulong), cainelias (Undertaker (WWE)), charger (Blanka (SF) — fighter replaced by CHARGER (owner 2026-10-20)), deathfang (Iori Yagami (KOF)), doa-ayane (Ayane (DOA4 / DOA Ultimate)), doa-bass (Bass Armstrong (DOA5 Last Round / DOA Ultimate)), doa-hayabusa (Ryu Hayabusa (DOA5 Last Round)), doa-jannlee (Jann Lee (DOA4 / DOA Ultimate)), doa-kasumi (Kasumi (DOA5 Last Round)), doa-tina (Tina Armstrong (DOA4 / DOA Ultimate)), dxmmii (Mokujin), hugo (Hugo Andore (Final Fight/SF)), iori (Iori Yagami (KOF)), kutz (Goh Hinogami), raiden (Big Bear / Raiden (Fatal Fury/KOF)), realizzt (Brad Burns), ryuji (Ryuji Yamazaki (KOF XV) / The Rock hybrid), ryuji-rock (Ryuji Yamazaki (KOF) x The Rock), sf-blanka (Blanka (SF)), sf-cammy (Cammy (SF) — Akuma-pattern translation), sf-chunli (Chun-Li (SF) — Akuma-pattern translation), sf-dhalsim (Dhalsim (SF) — Akuma-pattern translation), sf-guile (Guile (SF) — Akuma-pattern translation), sf-ken (Ken (SF)), sf-mbison (M. Bison (SF) — Akuma-pattern translation), sf-ryu (Ryu (SF)), sf-sagat (Sagat (SF) — Akuma-pattern translation), sf-vega (Vega (SF)), sf-zangief (Zangief (SF)), sunra (Pac-Man), thor (Ganryu), vainabel (Bass Armstrong), vega (Vega (SF)), vf-akira (Akira Yuki (Virtua Fighter 5 Final Showdown)), vf-kage (Kage-Maru (Virtua Fighter 5 Final Showdown)), vf-sarah (Sarah Bryant (Virtua Fighter 5 Final Showdown)), zangief (Zangief (SF)).

## Known limits

- Animation: new T7/T8 moves carry `anim_t3` = the same base character's decoded T3 row for the same notation, else the nearest by limb/class/startup (flagged approximate). Rows for the 8 remainder banks are baked by `tools/anim/t3_row_bake.py` (2026-10-21 extension).
- Damage: new T8 moves ×100/180, T7 ×100/170 to WH's 100 HP (raw in `damage_raw`). Earlier imports (PR #357 T8 cluster, 74efb3fb T7) kept raw T7/T8 damage. Those payloads are untouched and flagged in the Muse handoff.
- Character stances: entered from source notes (`stance_after`, unconditional 'Transition to X' only); conditional transitions ('with F') are not automatic yet.
- Not invented: Doc Frank's Dr. Gero / Mojo Jojo / Dr. Weird inspired moves, King Tyrant's Booker T moves, CHARGER's SF 3D moves. They need WWE/SF data decoded first.
