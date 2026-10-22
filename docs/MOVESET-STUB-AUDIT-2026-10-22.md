# MOVESET STUB AUDIT — Pass 1 (2026-10-22)

**Master roadmap, pass 1: the audit.** The owner's vision: every fighter fights
with their real moves from the Tekken teardowns — no stubs, nothing unwired.
This pass catalogs every gap. It wires nothing and removes nothing.

**Method (exact, not estimated).** A move counts as WIRED iff the game's own
fight logic can play its real animation — i.e. `fighter.js::_moveRowAction`
returns a clip. Replicated exactly in the audit scanner
(`wiring_audit.py`, run 2026-10-22):

- **Path A:** `t3_row` set, `SOURCE_TO_BANK[t3_source]` (no fallback — an
  unknown source means the game resolves `undefined`) equals the fighter's
  anim bank (or the king→armorking family exception), **and** `row:N` is
  baked in that bank's `game/assets/anim/t3/<bank>/rows.pack.json`.
- **Path B:** `anim_t3 {bank,row}` set, mapped bank equals the fighter's bank,
  and the row is baked in the pack.

Fighter bank resolution replicates `fighter.js::bankIdFor` exactly:
`FIGHTER_BANK` override → `index.json` `anim_bank`/`t3_source` → file
`t3_source` → `SOURCE_TO_BANK`. The loader gate is also replicated:
`movesets.js::_fetchOne` returns `null` (no moveset at all) when
`index.json` has no entry for the id.

Scope: all 59 roster ids in `game/js/roster-full.js`, all 100 files in
`game/assets/movesets/`, all 17 baked T3 anim banks, all 20 T3 teardown
banks, `game/js/movesets.js` / `fighter.js` / `t3anims.js` / `main.js`.

## Headline numbers

| Metric | Count |
|---|---:|
| Roster fighters audited | 59 |
| Base moves (all `moves` keys) | **34,247** |
| Moves WIRED (real T3 row clip plays in-fight) | 16,948 (**49.5%**) |
| Moves UNWIRED (generic/procedural fallback in-fight) | **17,299** (**50.5%**) |
| Strings: wired / total | 492 / 3,656 (**13%**) |
| Specials: wired / total | 133 / 1,579 (**8%**) |
| Fighters with >90% of base moves wired | **1** (byou, 97%) |
| Files declaring `proxy: true` | 5 |
| Moves carrying stub/placeholder/TODO markers | 4 entries + 1 file-level TODO |
| Roster ids whose moveset never loads | 3 |
| Roster fighters with no anim bank at all | 1 (ryuji — 103 moves, 0 wired) |
| Orphan moveset files (not roster, not a form target) | 36 |

## Gap classes

### A. Moveset never loads (the file exists but the fight never sees it)

`_fetchOne` gates on `index.json`. Missing index entry → `null` → the
fighter (or form) silently fights with no moveset.

| Id | Role | File | Status |
|---|---|---|---|
| `charger-attire2` | **selectable roster fighter** | `charger-attire2.json` (142 moves, king bank) | in `MOVESET_IDS`, NOT in `index.json` → never fetched |
| `deathfang-werewolf` | DEATHFANG transform target (`forms` → `moveset: 'deathfang-werewolf'`, pushed by `main.js`) | `deathfang-werewolf.json` (17 moves, proxy) | in `MOVESET_IDS`, NOT in `index.json` → werewolf form has no moveset |
| `doc-frank-frankenstein` | selectable roster fighter | **no file at all** | `roster-full.js` id with zero moveset data |

### B. No anim bank — ryuji

`ryuji` (RYUJI, roster fighter): `ryuji.json` has **no `t3_source`** and no
`anim_bank`; all 103 moves use `kofxv:ryuji:*` anim_refs (editor-only) with
no `t3_row`/`anim_t3`. Bank resolution returns null → the fighter has no
real motion bank. There is **no KOF teardown** in the repo to wire him from.

### C. Bank mismatch — the move's row lives in a bank the fighter never loads

| Fighter | Bank (resolved) | Moves | Unwired | Mismatch |
|---|---|---:|---:|---|
| zen | julia (via `FIGHTER_BANK` override) | 639 | **639 (100%)** | all rows are `heihachi`; file `t3_source` is `heihachi`. One-line suspect: `FIGHTER_BANK.zen='julia'` vs Heihachi-based data |
| doc-frank-hood | bosconovitch (index `anim_bank`) | 788 | 106 | 106 rows still `gunjack` (file `t3_source: gunjack`) — leftover from the retired gunjack stand-in |
| doc-frank-wowomomo | bosconovitch | 788 | 106 | same 106 gunjack rows |
| doc-frank-machine-shop | bosconovitch | 829 | 147 | 147 gunjack rows |
| gyou | hwoarang | 872 | 149 | 145 rows are `jin` |
| kai | eddy | 853 | 146 | 142 rows are `jin` |
| tou | paul | 640 | 143 | 139 rows are `heihachi` |
| nightwolf | julia | 554 | 135 | ~131 rows are `xiaoyu` |
| awapop | nina | 909 | 340 | 151 rows are `jin` |
| rave | lei | 1080 | 798 | 132 rows are `jin`/`xiaoyu` |
| kingtyrant | eddy | 848 | 286 | 137 rows are `xiaoyu` |

### D. No row wiring at all — 11,888 moves

Moves with neither `t3_row` nor `anim_t3`. They carry frame data and
notation but the game can never play a real clip for them. This is 68.7%
of all unwired moves. Worst offenders: kronos-attire2 (1,708), koreshi
(936), rave (798), phantom (652), kronos (619), zui (502), jin_soul
(498), cyborgx (476), burger (446), purplerain (425).

### E. Row referenced but never baked — rows.pack.json gaps

The packs only contain rows baked at bake time; the SOURCE-MERGE
(2026-10-21, T8+T7+T3+history) added moves referencing rows outside the
packs. Examples: `anim_t3 row 317/175/99/…` not in `yoshimitsu` pack
(jin_soul, phantom); `row 104/100/108/…` not in `bryan`/`jin` packs
(retsu, rin, demonio-bloodline-ember, demonio-winged). Per-bank bake
coverage: king 176, jin 153, xiaoyu 135, bryan 97, gunjack 152,
yoshimitsu 111, paul 163, lei 259, nina 199, hwoarang 183, eddy 208,
julia 172, anna 209, bosconovitch 647, heihachi_on_jin 136, armorking 176.
`heihachi_ownrig` ships **no rows.pack.json at all** (alternative bank).

### F. Declared proxies — 5 files

`proxy: true` with honest notes: `deathfang` (Iori kit on heihachi rows),
`koreshi` (heihachi proxy), `ryuji-rock` (22 moves, king proxy),
`deathfang-werewolf` (heihachi proxy), `cainelias` (orphan, king proxy).

### G. Stub / placeholder / TODO markers in the data

- `samura1.json` → move `qcf+1+2`: *"PLACEHOLDER anim — needs the Child-Of
  rig from tools/limb-system/dxmmii (PR #302 spec)."* (owner-requested
  rocket-fist; anim is a stand-in)
- `demonio-winged.json` → 3 moves: *"Placeholder anim until devil-jin T3
  rows mapped."* (flight stance, forehead/chest laser, devil low sweep)
- `ryuji.json` → file-level `canon_note` contains a TODO (full Yamazaki +
  Rock kit spec listed but not encoded as moves)

### H. Orphan moveset files — 36

Not a roster id and not a form target. Some are staged future fighters
(`hugo`, `marduk`, `raiden`, `bob`, `blanka`, `mariposa`, `dxmmii`,
`sunra`, `baek`, `chordz`, `kutz`, `lili`, `realizzt`, `vainabel`,
`cainelias`), some are federation sets (`doa-bass`, `doa-kasumi`,
`doa-hayabusa`, `doa-ayane`, `doa-tina`, `doa-jannlee`, `vf-akira`,
`vf-sarah`, `vf-kage`, `sf-akuma`, `sf-blanka`, `sf-cammy`, `sf-chunli`,
`sf-dhalsim`, `sf-guile`, `sf-ken`, `sf-mbison`, `sf-ryu`, `sf-sagat`,
`sf-vega`, `sf-zangief`). Also in `MOVESET_IDS` but absent from
`index.json`: only the two class-A ids. In `index.json` but absent from
`MOVESET_IDS`: `doc-frank-hood`, `doc-frank-wowomomo`, `ryuji`, and the
12 `sf-*` files (`MOVESET_IDS` looks legacy — nothing outside
`movesets.js` references it; the live loader keys off roster ids +
`index.json`).

### I. Strings & specials

Only 13% of strings and 8% of specials resolve to baked row clips
(strings carry `t3_rows` arrays, specials carry `t3_row`; same bank/pack
rules apply). Even well-wired fighters drop here — e.g. byou (97% base
moves wired) still has string/special gaps.

## Per-fighter gap table (unwired count desc)

Columns: bank = resolved anim bank · tot = base moves · W = wired ·
U = unwired · top reason.

| Fighter | Bank | Tot | W | U | W% | Top unwired reason |
|---|---|---:|---:|---:|---:|---|
| kronos-attire2 | king | 1853 | 145 | 1708 | 7% | no t3_row and no anim_t3 |
| koreshi | heihachi | 953 | 17 | 936 | 1% | no t3_row and no anim_t3 (+proxy) |
| rave | lei | 1080 | 282 | 798 | 26% | no t3_row and no anim_t3 |
| phantom | yoshimitsu | 1019 | 367 | 652 | 36% | no t3_row and no anim_t3 |
| zen | julia | 639 | 0 | 639 | 0% | bank-mismatch: all rows heihachi, bank julia |
| kronos | king | 772 | 153 | 619 | 19% | no t3_row and no anim_t3 |
| zui | jin | 654 | 152 | 502 | 23% | no t3_row and no anim_t3 |
| jin_soul | yoshimitsu | 1012 | 514 | 498 | 50% | anim_t3 rows not baked in yoshimitsu pack |
| cyborgx | gunjack | 624 | 148 | 476 | 23% | no t3_row and no anim_t3 |
| burger | bryan | 552 | 106 | 446 | 19% | no t3_row and no anim_t3 |
| purplerain | jin | 569 | 144 | 425 | 25% | no t3_row and no anim_t3 |
| samura1 | gunjack | 860 | 465 | 395 | 54% | no t3_row and no anim_t3 (+1 PLACEHOLDER) |
| pantera | king | 873 | 483 | 390 | 55% | no t3_row and no anim_t3 |
| kinpo | jin | 525 | 143 | 382 | 27% | no t3_row and no anim_t3 |
| slice | bryan | 486 | 107 | 379 | 22% | no t3_row and no anim_t3 |
| yukihyo | armorking | 534 | 155 | 379 | 29% | no t3_row and no anim_t3 |
| mariposa-monarch | xiaoyu | 508 | 132 | 376 | 25% | no t3_row and no anim_t3 |
| armor-king | king | 500 | 125 | 375 | 25% | no t3_row and no anim_t3 |
| star | xiaoyu | 908 | 564 | 344 | 62% | no t3_row and no anim_t3 |
| awapop | nina | 909 | 569 | 340 | 62% | bank-mismatch: 151 jin rows, bank nina |
| sakura | xiaoyu | 764 | 431 | 333 | 56% | no t3_row and no anim_t3 |
| demonio-winged | jin | 1057 | 725 | 332 | 68% | no t3_row and no anim_t3 (+3 placeholder anims) |
| sha | xiaoyu | 762 | 431 | 331 | 56% | no t3_row and no anim_t3 |
| skull | bryan | 688 | 366 | 322 | 53% | no t3_row and no anim_t3 |
| torch | anna | 892 | 585 | 307 | 65% | no t3_row and no anim_t3 |
| kingtyrant | eddy | 848 | 562 | 286 | 66% | bank-mismatch: 137 xiaoyu rows, bank eddy |
| demonio-human | jin | 677 | 402 | 275 | 59% | no t3_row and no anim_t3 |
| diablo | heihachi | 642 | 367 | 275 | 57% | no t3_row and no anim_t3 |
| demonio | jin | 658 | 401 | 257 | 60% | no t3_row and no anim_t3 |
| bruno | bryan | 328 | 105 | 223 | 32% | no t3_row and no anim_t3 |
| scimitar | jin | 362 | 143 | 219 | 39% | no t3_row and no anim_t3 |
| retsu | bryan | 685 | 469 | 216 | 68% | anim_t3 rows not baked in bryan pack |
| waterfall | jin | 341 | 142 | 199 | 41% | no t3_row and no anim_t3 |
| michiko | jin | 344 | 151 | 193 | 43% | no t3_row and no anim_t3 |
| negativo | bryan | 282 | 105 | 177 | 37% | no t3_row and no anim_t3 |
| demonio-bloodline-ember | jin | 680 | 509 | 171 | 74% | anim_t3 rows not baked in jin pack |
| rin | jin | 659 | 488 | 171 | 74% | anim_t3 rows not baked in jin pack |
| gyou | hwoarang | 872 | 723 | 149 | 82% | bank-mismatch: 145 jin rows, bank hwoarang |
| doc-frank-machine-shop | bosconovitch | 829 | 682 | 147 | 82% | bank-mismatch: 147 gunjack rows |
| kai | eddy | 853 | 707 | 146 | 82% | bank-mismatch: 142 jin rows, bank eddy |
| tou | paul | 640 | 497 | 143 | 77% | bank-mismatch: 139 heihachi rows, bank paul |
| dio | heihachi | 275 | 135 | 140 | 49% | no t3_row and no anim_t3 |
| thor | bryan | 244 | 107 | 137 | 43% | no t3_row and no anim_t3 |
| nightwolf | julia | 554 | 419 | 135 | 75% | bank-mismatch: 131 xiaoyu rows, bank julia |
| docfrank | bosconovitch | 380 | 266 | 114 | 70% | no t3_row and no anim_t3 |
| charger | bryan | 199 | 90 | 109 | 45% | no t3_row and no anim_t3 |
| doc-frank-hood | bosconovitch | 788 | 682 | 106 | 86% | bank-mismatch: 106 gunjack rows |
| doc-frank-wowomomo | bosconovitch | 788 | 682 | 106 | 86% | bank-mismatch: 106 gunjack rows |
| ryuji | — (none) | 103 | 0 | 103 | 0% | no bank; kofxv refs only, no KOF teardown |
| deathfang | heihachi | 122 | 29 | 93 | 23% | no t3_row and no anim_t3 (+proxy) |
| zangief | king | 217 | 125 | 92 | 57% | no t3_row and no anim_t3 |
| iori | heihachi | 196 | 105 | 91 | 53% | no t3_row and no anim_t3 |
| vega | xiaoyu | 207 | 116 | 91 | 56% | no t3_row and no anim_t3 |
| baek-master-white | bryan | 134 | 114 | 20 | 85% | no t3_row and no anim_t3 |
| dxmmii-patchwork | jin | 166 | 146 | 20 | 87% | no t3_row and no anim_t3 |
| ryuji-rock | king | 24 | 17 | 7 | 70% | no t3_row and no anim_t3 (+proxy) |
| byou | jin | 157 | 153 | 4 | 97% | no t3_row and no anim_t3 |
| charger-attire2 | — | — | — | — | — | CLASS A: file never loads |
| doc-frank-frankenstein | — | — | — | — | — | CLASS A: no moveset file |

## Teardown coverage per game

| Game | Teardown status | Moveset banks for wiring | Gap |
|---|---|---|---|
| Tekken 3 | 100% — 20 chars decoded (`teardown/tekken3/movesets/`) | 16 baked anim banks in `game/assets/anim/t3/` (+`heihachi_ownrig`, no rows.pack) | forestlaw, gon, kuma, law, ogre decoded but never baked (no current consumers) |
| Tekken 7 | ~40% — King variants only | none beyond T3 king rows | every non-King T7-era base rides a T3 bank or proxy |
| Tekken 6 | ~30% — DATA401 still encrypted | none | blocked on decrypt lane |
| TTT2 | ~15% — not extracted | none | blocked on download/STFS lane |
| DOA4/6 | mechanics docs only | community movelists (`doa-bass` 20 moves, `vainabel` 44 via doa4 teardown partial) | no decoded motion banks |
| VF5 | complete models, no movesets | community movelists (12–19 moves each) | no decoded motion banks |
| Street Fighter | `street-fighter-3d-games` research only | Akuma-pattern translations (10–12 moves, `sf6`/`sfv`/`sf4` sources — **not** in `SOURCE_TO_BANK`, always unwired in-game) | no teardown |
| KOF | none | none — `ryuji` 103 moves fully unwired; `deathfang`/`koreshi` proxy on heihachi | needs source decision |
| Urban Reign | ~95% audio/VGS, no move banks | 30 `urban-reign`-sourced moves in kronos files (unwired — source not in `SOURCE_TO_BANK`) | PPK binary RE lane |

Note: 2,757 moves carry `t3_source` values the game cannot resolve
(`sf6` 1,615 · `sfv` 957 · `original` 65 · `sf4` 50 · `urban-reign` 30 ·
`doa-bass` 40) — `SOURCE_TO_BANK[source]` is `undefined` in
`_moveRowAction`, so these can never wire until they get `t3_row` or
`anim_t3` entries.

## Recommended wiring order (follow-up passes, fighter-by-fighter)

- **P0 — loader/index one-liners (demoable immediately):** add
  `charger-attire2` + `deathfang-werewolf` to `index.json`; fix
  `FIGHTER_BANK.zen` (639 moves, 0% → wired); decide
  `doc-frank-frankenstein` (write file or drop id).
- **P1 — bank-mismatch remaps:** doc-frank trio (365 gunjack→bosconovitch
  rows), gyou/kai/tou/nightwolf/awapop/rave/kingtyrant partials
  (jin/heihachi/xiaoyu rows → fighter bank equivalents).
- **P2 — bake missing rows:** extend `rows.pack.json` per bank for the
  T8/T7-merged rows (jin_soul, retsu, rin, demonio-bloodline-ember,
  demonio-winged, phantom…).
- **P3 — row assignment:** the 11,888 no-row moves, fighter by fighter
  from the top of the table (kronos-attire2, koreshi, rave, phantom,
  kronos, zui…).
- **P4 — proxies to real kits:** deathfang, koreshi, ryuji-rock,
  deathfang-werewolf, cainelias.
- **P5 — ryuji:** needs a KOF source decision (no teardown exists).
- **P6 — orphans:** promote to roster or archive (36 files).

## Files

- This document: `docs/MOVESET-STUB-AUDIT-2026-10-22.md`
- Raw per-move data: `/tmp/wiring_report.json` (build machine only —
  regenerate with the scanner; not committed)
- Scanner: `/tmp/wiring_audit.py` / `/tmp/stub_audit.py` (build machine
  only — candidate for `tools/moveset-coverage/` in a follow-up pass)
