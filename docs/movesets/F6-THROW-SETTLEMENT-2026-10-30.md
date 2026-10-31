# F6 Throw-Mismatch Settlement — 2026-10-30

WH-100 burn-down, finding F6: moves carrying `throw: true` / `isGrab: true` with a non-throw `move_class`, plus strike-class moves whose inputs literally name throws. Settled against each T3 bank's `game/assets/anim/t3/<bank>/hit_frames.json` throw flag (field index 4 of each row array), with playability filtered by the bank's `rows.pack.json`.

These are DATA corrections settled against hit_frames. No play-verification is claimed for any entry in this document.

## Final accounting (184 entries)

| Category | Count |
|---|---|
| Corrected (anim_t3 re-picked to a hit_frames throw=1 row) | 79 |
| — of which also received move_class strike -> throw | 3 (kingtyrant.json Back/Left/Right throw) |
| Settled-consistent, no change | 46 |
| Held | 42 |
| Owner-gated, untouched | 17 |
| **Total** | **184** |

Arithmetic: the coordinator's edit specs covered 84 entries across 36 files (81 anim_t3 re-picks + 6 move_class fixes, with kingtyrant's 3 throw entries counted in both groups = 84 unique entries). 79 of those entries landed (35 files merged); scimitar.json's 5 entries did not land — see Held §3 — leaving 79 corrected entries. 79 + 46 + 42 + 17 = 184.

## 1. Corrected — 79 entries in 35 merged PRs

Each PR touches exactly one moveset file (per-character isolation). Old row -> new row; the old row is hit_frames throw=0 and the new row is hit_frames throw=1 in the same bank in every case.

### `awapop.json` — PR #1315 (merge 489d3eb88bcb3e62e5b3bff43b40c378fe70e805)
- `P+K`: anim_t3 row 162 -> 370
- `1+4`: anim_t3 row 215 -> 370

### `baek-master-white.json` — PR #1319 (merge 5d3e0f02747494eb76edf11a55acb59542308d85)
- `P+K`: anim_t3 row 75 -> 141
- `1+4`: anim_t3 row 75 -> 141

### `baek.json` — PR #1327 (merge 1fb752aa6ef53c2810be0f270564406e9e67704a)
- `P+K`: anim_t3 row 75 -> 141
- `1+4`: anim_t3 row 75 -> 141

### `bruno.json` — PR #1328 (merge 0664ba1158e545f0dc516b80d2f4babd8d08d2d6)
- `P+K`: anim_t3 row 75 -> 141
- `1+4`: anim_t3 row 75 -> 141

### `burger.json` — PR #1330 (merge 169d0a1de9f8d75861ccb6d815a2c0b5307d018a)
- `P+K`: anim_t3 row 75 -> 141
- `1+4`: anim_t3 row 75 -> 141

### `demonio-bloodline-ember.json` — PR #1331 (merge baf56a1a566b91909f12e45a7e8a58f0c484fd37)
- `P+K`: anim_t3 row 162 -> 370
- `1+4`: anim_t3 row 215 -> 370

### `demonio-human.json` — PR #1332 (merge ba2c1d0dfb2eca43615e59bfc68854d0e55181ee)
- `1+4`: anim_t3 row 215 -> 401

### `demonio.json` — PR #1333 (merge c33b5a78788d919e5ec55b53e56784e097a29295)
- `P+K`: anim_t3 row 162 -> 370
- `1+4`: anim_t3 row 215 -> 370

### `diablo.json` — PR #1335 (merge f73dd869d32a34cbaa5d4ffa732e0744cda78c34)
- `P+K`: anim_t3 row 100 -> 354
- `1+4`: anim_t3 row 100 -> 354

### `dio.json` — PR #1336 (merge ae79a57fcaeb7030ad28d72e54c459484b031d6c)
- `P+K`: anim_t3 row 100 -> 354
- `1+4`: anim_t3 row 100 -> 354

### `doc-frank-frankenstein.json` — PR #1337 (merge a1f6574f2294bc2f3e317b1e2aae3e68de90b222)
- `donor.docfrank.P+K`: anim_t3 row 90 -> 120
- `None~donor.docfrank.51`: anim_t3 row 90 -> 120
- `None~donor.docfrank.102`: anim_t3 row 90 -> 120
- `None~donor.docfrank.153`: anim_t3 row 90 -> 120

### `doc-frank-hood.json` — PR #1339 (merge 23ba2de2b71892e9e2dab1620d5b5f63b01184f1)
- `donor.docfrank.P+K`: anim_t3 row 90 -> 120
- `None~donor.docfrank.51`: anim_t3 row 90 -> 120
- `None~donor.docfrank.102`: anim_t3 row 90 -> 120
- `None~donor.docfrank.153`: anim_t3 row 90 -> 120
- `None~donor.docfrank.204`: anim_t3 row 90 -> 120

### `doc-frank-machine-shop.json` — PR #1340 (merge 8532d91146d7a300986fb849f92de7865657b06e)
- `donor.docfrank.P+K`: anim_t3 row 90 -> 120
- `None~donor.docfrank.51`: anim_t3 row 90 -> 120
- `None~donor.docfrank.102`: anim_t3 row 90 -> 120
- `None~donor.docfrank.153`: anim_t3 row 90 -> 120
- `None~donor.docfrank.204`: anim_t3 row 90 -> 120

### `doc-frank-wowomomo.json` — PR #1341 (merge 4b0ac40f3814a15332becf958fb000c0d88a4633)
- `donor.docfrank.P+K`: anim_t3 row 90 -> 120
- `None~donor.docfrank.51`: anim_t3 row 90 -> 120
- `None~donor.docfrank.102`: anim_t3 row 90 -> 120
- `None~donor.docfrank.153`: anim_t3 row 90 -> 120
- `None~donor.docfrank.204`: anim_t3 row 90 -> 120

### `docfrank.json` — PR #1342 (merge 3fe9fdb7136ef5207a2a594553d9a2603f82616d)
- `b,b+1+2`: anim_t3 row 23 -> 612

### `dxmmii-patchwork.json` — PR #1343 (merge c7005eb98756d767da64b17055596ee96aa93bd5)
- `P+K`: anim_t3 row 162 -> 370
- `1+4`: anim_t3 row 215 -> 370

### `dxmmii.json` — PR #1344 (merge 6a4b9a5a13c19c3add9fa54b18790f42cbc0a120)
- `P+K`: anim_t3 row 162 -> 370
- `1+4`: anim_t3 row 215 -> 370

### `kingtyrant.json` — PR #1345 (merge 83e2737758c455d2a8c6cae40e25e063268c8732)
- `P+K`: anim_t3 row 270 -> 580
- `1+4`: anim_t3 row 232 -> 580
- `Back throw`: anim_t3 row 26 -> 148; move_class strike -> throw
- `Left throw`: anim_t3 row 26 -> 148; move_class strike -> throw
- `Right throw`: anim_t3 row 26 -> 148; move_class strike -> throw

### `kutz.json` — PR #1346 (merge 698fa5bf87322fcbb3c23fb50287479c7943d46a)
- `1+4`: anim_t3 row 232 -> 153

### `lili.json` — PR #1347 (merge 721cf64a831da116a1055dd9af16866844ac668c)
- `P+K`: anim_t3 row 270 -> 580
- `1+4`: anim_t3 row 232 -> 580

### `mariposa-monarch.json` — PR #1348 (merge c74066246ac4190ac91aacb32b0ee5662c27ab25)
- `P+K`: anim_t3 row 270 -> 580
- `1+4`: anim_t3 row 232 -> 580

### `michiko.json` — PR #1349 (merge 5bdc392590be605000524f6f41ec506a6f576d6b)
- `P+K`: anim_t3 row 162 -> 370
- `1+4`: anim_t3 row 215 -> 370

### `negativo.json` — PR #1350 (merge 81f48713ed2a5180c5f02b286ffce90678f53601)
- `P+K`: anim_t3 row 75 -> 141
- `1+4`: anim_t3 row 75 -> 141

### `pantera.json` — PR #1351 (merge 2ef3ec7d922f0ec72b4102e9eb04827a437fbad0)
- `1+4`: anim_t3 row 232 -> 153

### `realizzt.json` — PR #1352 (merge cb4cb6174780ec29799a99572e9c072603988687)
- `P+K`: anim_t3 row 162 -> 370
- `1+4`: anim_t3 row 215 -> 370

### `retsu.json` — PR #1353 (merge cf3ff15738a6b6e58822b27b4bfec98b18b4e2a0)
- `P+K`: anim_t3 row 75 -> 141
- `1+4`: anim_t3 row 75 -> 141

### `sakura.json` — PR #1354 (merge ab5059b2366942a2186fd601176c60880afdb02c)
- `P+K`: anim_t3 row 270 -> 580
- `1+4`: anim_t3 row 232 -> 580

### `sha.json` — PR #1355 (merge 69b0a19be8d5259829f60fda7b0d92e482af5ed4)
- `P+K`: anim_t3 row 270 -> 580
- `1+4`: anim_t3 row 232 -> 580

### `silvertongue.json` — PR #1356 (merge a9fedf16ed238aa4067ab330ecb914cbcc933555)
- `P+K`: anim_t3 row 270 -> 580
- `1+4`: anim_t3 row 232 -> 580

### `slice.json` — PR #1357 (merge 27637b331225e1c7ceb57dc3900b5b8126f30ae7)
- `P+K`: anim_t3 row 75 -> 141
- `1+4`: anim_t3 row 75 -> 141

### `thor.json` — PR #1358 (merge 25b648f578505d407c9784188b9a4745d86f4829)
- `P+K`: anim_t3 row 75 -> 141
- `1+4`: anim_t3 row 75 -> 141

### `torch.json` — PR #1359 (merge 2bbe79ba6297cfe2295fb58962f633821c226a7e)
- `P+K`: anim_t3 row 162 -> 370
- `1+4`: anim_t3 row 215 -> 370

### `tou.json` — PR #1360 (merge 9aedeaadb1717bc9544168be43e562617afa3d88)
- `P+K`: anim_t3 row 100 -> 354
- `1+4`: anim_t3 row 100 -> 354

### `waterfall.json` — PR #1361 (merge b60d685ce19ca761cae66cde173f6f32d162f595)
- `P+K`: anim_t3 row 247 -> 371
- `1+4`: anim_t3 row 215 -> 371

### `yukihyo.json` — PR #1362 (merge 2a2f7026329f83a73e6d9adb7e1545134c81c0aa)
- `1+4`: anim_t3 row 232 -> 153

## 2. Settled-consistent, no change — 46 entries

### 2a. Bank row already hit_frames throw=1 — 8 entries

- `doc-frank-machine-shop.json` `P+K` — bank gunjack row 355, hit_frames throw=1
- `doc-frank-machine-shop.json` `1+4` — bank gunjack row 355, hit_frames throw=1
- `kutz.json` `P+K` — bank king row 586, hit_frames throw=1
- `pantera.json` `P+K` — bank king row 586, hit_frames throw=1
- `ryuji-rock.json` `P+K` — bank king row 586, hit_frames throw=1
- `samura1.json` `P+K` — bank gunjack row 355, hit_frames throw=1
- `samura1.json` `1+4` — bank gunjack row 355, hit_frames throw=1
- `yukihyo.json` `P+K` — bank king row 586, hit_frames throw=1

### 2b. Move name names its T3 bank+row, and that row is hit_frames throw=1 — 5 entries

- `docfrank.json` `d,d/f,d,d/f+1+2_r276` — gunjack row 276, hit_frames throw=1
- `docfrank.json` `d/b,n,f+2_r271` — gunjack row 271, hit_frames throw=1
- `docfrank.json` `n,d,d/b+1+3_r269` — gunjack row 269, hit_frames throw=1
- `vainabel.json` `d,d/f,d,d/f+1+2` — bryan row 211, hit_frames throw=1
- `vainabel.json` `n,d/b,n,f+1+2` — bryan row 211, hit_frames throw=1

### 2c. No bank row at all; anim_ref is the move's own original/DOA identity — 33 entries (taxonomy-only)

For these, class signature/special is the design taxonomy and the throw flag is a property; no incorrect animation exists, so nothing was changed.

- `baek-master-white.json` `donor.baek.P+K` — class signature, anim_ref `wh:baek:sig:homework`
- `demonio-human.json` `donor.demonio.P+K` — class signature, anim_ref `wh:demonio:sig:the-unbowed`
- `doa-bass.json` `1+4` — class signature, anim_ref `wh:doa-bass:sig:overtime-shift`
- `doa-bass.json` `P+K` — class signature, anim_ref `wh:doa-bass:sig:overtime-shift`
- `doc-frank-frankenstein.json` `b,b+1+2` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-frankenstein.json` `b,b+1+2~donor.docfrank` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-frankenstein.json` `b,b+1+2~donor.docfrank.2` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-frankenstein.json` `b,b+1+2~donor.docfrank.3` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-hood.json` `b,b+1+2` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-hood.json` `b,b+1+2~donor.docfrank` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-hood.json` `b,b+1+2~donor.docfrank.2` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-hood.json` `b,b+1+2~donor.docfrank.3` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-hood.json` `b,b+1+2~donor.docfrank.4` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-machine-shop.json` `b,b+1+2` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-machine-shop.json` `b,b+1+2~donor.docfrank` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-machine-shop.json` `b,b+1+2~donor.docfrank.2` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-machine-shop.json` `b,b+1+2~donor.docfrank.3` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-machine-shop.json` `b,b+1+2~donor.docfrank.4` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-wowomomo.json` `b,b+1+2` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-wowomomo.json` `b,b+1+2~donor.docfrank` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-wowomomo.json` `b,b+1+2~donor.docfrank.2` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-wowomomo.json` `b,b+1+2~donor.docfrank.3` — class special, anim_ref `wh:gero:energy_absorption`
- `doc-frank-wowomomo.json` `b,b+1+2~donor.docfrank.4` — class special, anim_ref `wh:gero:energy_absorption`
- `dxmmii-patchwork.json` `donor.dxmmii.P+K` — class signature, anim_ref `wh:dxmmii:sig:everybodys-sample`
- `ryuji.json` `P+K` — class signature, anim_ref `wh:ryuji-rock:sig:smackdown`
- `vainabel.json` `qcf+1+3` — class special, anim_ref `doa:bass:spear-grapple`
- `vainabel.json` `b,f+1+3` — class special, anim_ref `doa:bass:dynamite-lariat`
- `vainabel.json` `hcb+1+3` — class special, anim_ref `doa:bass:powerbomb`
- `vainabel.json` `qcb+1+3` — class special, anim_ref `doa:bass:manhattan-driver`
- `vainabel.json` `qcf+1+2` — class special, anim_ref `doa:bass:headlock`
- `vainabel.json` `1+4` — class signature, anim_ref `wh:vainabel:sig:elias-brothers-chokeslam`
- `vainabel.json` `P+K` — class signature, anim_ref `wh:vainabel:sig:elias-brothers-chokeslam`
- `vf-akira.json` `P+K` — class signature, anim_ref `wh:vf-akira:sig:eight-extremes`

## 3. Held — 42 entries

### 3a. Re-pick ambiguous — 11 entries

`demonio-bloodline-ember.json` — the-unbowed group x10 at jin rows 192/215: the deterministic re-pick rule produced tied candidates jin 370 and jin 385 with no unique minimum, so no pick was made:

- `demonio-bloodline-ember.json` `donor.demonio.P+K` — bank jin row 192, tied candidates jin 370 / jin 385
- `demonio-bloodline-ember.json` `1+4~donor.demonio` — bank jin row 215, tied candidates jin 370 / jin 385
- `demonio-bloodline-ember.json` `None~donor.demonio.3` — bank jin row 192, tied candidates jin 370 / jin 385
- `demonio-bloodline-ember.json` `1+4~donor.demonio.2` — bank jin row 215, tied candidates jin 370 / jin 385
- `demonio-bloodline-ember.json` `None~donor.demonio.6` — bank jin row 192, tied candidates jin 370 / jin 385
- `demonio-bloodline-ember.json` `1+4~donor.demonio.3` — bank jin row 215, tied candidates jin 370 / jin 385
- `demonio-bloodline-ember.json` `None~donor.demonio.9` — bank jin row 192, tied candidates jin 370 / jin 385
- `demonio-bloodline-ember.json` `1+4~donor.demonio.4` — bank jin row 215, tied candidates jin 370 / jin 385
- `demonio-bloodline-ember.json` `None~donor.demonio.12` — bank jin row 192, tied candidates jin 370 / jin 385
- `demonio-bloodline-ember.json` `1+4~donor.demonio.5` — bank jin row 215, tied candidates jin 370 / jin 385

- `docfrank.json` `P+K` (crayon-notes) — bank bosconovitch row 355: tied candidates bosconovitch 13, 14, 15, 16, 17, 117, 205, 206, 502; no unique minimum, no pick made.

### 3b. Bank has NO data held in-repo — 26 entries

Blocker per bank: there is no `game/assets/anim/t3/<bank>/` directory and no hit_frames for these banks in the repo, so no throw flag can be settled and no re-pick is possible until the bank's T3 data is pulled in:

- Bank **baek** (9 entries, all in `baek-master-white.json`, donor.baek copies of Homework at nominal row 75)
- Bank **dxmmii** (9 entries, all in `dxmmii-patchwork.json`, donor.dxmmii copies of Everybodys Sample at nominal rows 162/215)
- Bank **demonio** (8 entries, all in `demonio-human.json`, donor.demonio copies of The Unbowed at nominal row 66)

- `baek-master-white.json` `1+4~donor.baek` — bank baek row 75
- `baek-master-white.json` `None~donor.baek.3` — bank baek row 75
- `baek-master-white.json` `1+4~donor.baek.2` — bank baek row 75
- `baek-master-white.json` `None~donor.baek.5` — bank baek row 75
- `baek-master-white.json` `1+4~donor.baek.3` — bank baek row 75
- `baek-master-white.json` `None~donor.baek.7` — bank baek row 75
- `baek-master-white.json` `1+4~donor.baek.4` — bank baek row 75
- `baek-master-white.json` `None~donor.baek.9` — bank baek row 75
- `baek-master-white.json` `1+4~donor.baek.5` — bank baek row 75
- `demonio-human.json` `None~donor.demonio.3` — bank demonio row 66
- `demonio-human.json` `1+4~donor.demonio` — bank demonio row 66
- `demonio-human.json` `None~donor.demonio.6` — bank demonio row 66
- `demonio-human.json` `1+4~donor.demonio.4` — bank demonio row 66
- `demonio-human.json` `None~donor.demonio.9` — bank demonio row 66
- `demonio-human.json` `1+4~donor.demonio.5` — bank demonio row 66
- `demonio-human.json` `None~donor.demonio.12` — bank demonio row 66
- `demonio-human.json` `1+4~donor.demonio.6` — bank demonio row 66
- `dxmmii-patchwork.json` `1+4~donor.dxmmii` — bank dxmmii row 215
- `dxmmii-patchwork.json` `None~donor.dxmmii.3` — bank dxmmii row 162
- `dxmmii-patchwork.json` `1+4~donor.dxmmii.2` — bank dxmmii row 215
- `dxmmii-patchwork.json` `None~donor.dxmmii.5` — bank dxmmii row 162
- `dxmmii-patchwork.json` `1+4~donor.dxmmii.3` — bank dxmmii row 215
- `dxmmii-patchwork.json` `None~donor.dxmmii.7` — bank dxmmii row 162
- `dxmmii-patchwork.json` `1+4~donor.dxmmii.4` — bank dxmmii row 215
- `dxmmii-patchwork.json` `None~donor.dxmmii.9` — bank dxmmii row 162
- `dxmmii-patchwork.json` `1+4~donor.dxmmii.5` — bank dxmmii row 215

### 3c. Surgical-editor ambiguity — 5 entries (scimitar.json)

`f6_edit.py` rejected the scimitar.json edit spec with the exact error `BLOCK MATCH COUNT 2 (of 2 candidates) for key Back throw`. Each of the three throw keys exists twice in scimitar.json with identical strike class: once in `moves` and once in the `t8_quarantine_20261024` section, and the editor cannot disambiguate the moves-dict block. Per the lane's hard rule (a rejected edit is stopped and reported, never improvised), no scimitar entry was edited and no PR was opened for scimitar.json:

- `scimitar.json` `P+K` — bank jin row 162, hit_frames throw=0 (spec pick was jin 370; not applied)
- `scimitar.json` `1+4` — bank jin row 215, hit_frames throw=0 (spec pick was jin 370; not applied)
- `scimitar.json` `Back throw` — move_class strike -> throw not applied (bank shaheen has no T3 data held; operative identity is the T8 anim_ref `t8:shaheen:shaheen-back throw`)
- `scimitar.json` `Left throw` — move_class strike -> throw not applied (anim_ref `t8:shaheen:shaheen-left throw`)
- `scimitar.json` `Right throw` — move_class strike -> throw not applied (anim_ref `t8:shaheen:shaheen-right throw`)

## 4. Owner-gated, untouched — 17 entries

These files were never touched by this lane:

- `star.json` x3 (Owner Decision List item 1): `Back throw`, `Left throw`, `Right throw` — strike class, bank eddy row 26, anim_refs name the T8 eddy throws.
- `cainelias.json` x4 (Owner Decision List item 8): `f,f+1+2` (king 586, hit_frames throw=1), `b+1+2` (king 586, hit_frames throw=1), `d/b+1+2` (king 131, hit_frames throw=0), `d+1+2` (king 97, hit_frames throw=0).
- `demonio-winged.json` x10 (Owner Decision List item 4): the-unbowed group at jin rows 192/215:
  - `donor.demonio.P+K` — bank jin row 192
  - `1+4~donor.demonio` — bank jin row 215
  - `None~donor.demonio.3` — bank jin row 192
  - `1+4~donor.demonio.2` — bank jin row 215
  - `None~donor.demonio.6` — bank jin row 192
  - `1+4~donor.demonio.3` — bank jin row 215
  - `None~donor.demonio.9` — bank jin row 192
  - `1+4~donor.demonio.4` — bank jin row 215
  - `None~donor.demonio.12` — bank jin row 192
  - `1+4~donor.demonio.5` — bank jin row 215

## 5. Method

- **Re-pick rule:** for a WH-original throw whose current anim_t3 row is hit_frames throw=0, deterministically re-pick in the SAME bank: same attack-class (from the T3 moveset data) and, where possible, same button profile as the prior row; the candidate must be hit_frames throw=1 AND present in the bank's rows.pack.json (playability filter); ties broken by closest stream_frames, with a unique minimum required — no unique minimum means held, not guessed (§3a).
- **Playability filter details:** bank heihachi's playable set is `game/assets/anim/t3/heihachi_on_jin/rows.pack.json`, the only rows.pack carrying heihachi move rows; bank king resolves to the `king_on_pantera_leoman` bank directory (there is no `t3/king/` directory).
- **Group-twin rule:** group twins of one signature (same file + same anim_ref) all take the primary (P+K) entry's pick.
- **Class fixes:** kingtyrant's Back/Left/Right throw had move_class strike, inputs and T8 anim_refs naming throws, and a non-throw eddy row; they received both the class fix and the re-pick (eddy 26 -> 148).
- **Taxonomy statement:** settled entries keep class signature/special because the mismatch was in the assigned anim row, not the class taxonomy — signature/special is the design taxonomy and throw is a property flag on the move.
- **Edits were surgical:** anim_t3.row, anim_t3.match and (kingtyrant only, among merged files) move_class were the only fields changed; anim_ref was never edited. Each file PR was verified by the editor (reparse OK, unedited entries parse-identical) and merged only with all CI checks green, MERGEABLE state, and zero deleted files.

## 6. Post-merge verification (census re-run against post-merge main)

Census definitions: 175 = entries with (throw:true or isGrab:true) and move_class != "throw" across `game/assets/movesets/*.json`; 9 = strike-class entries whose input is literally "Back throw"/"Left throw"/"Right throw". Re-run against main at the final merge of this settlement:

- 175-pool: 175 entries (pool membership is definition-based; corrected entries remain in the pool because their class taxonomy is unchanged — what changed is the throw flag of the row they point at).
- 175-pool hit_frames throw distribution after settlement: throw=1: 86, throw=0: 25, no bank row / bank not held: 64.
- Every remaining throw=0 entry in the 175-pool is owner-gated (cainelias.json x2, demonio-winged.json x10), held-ambiguous (demonio-bloodline-ember.json x10, docfrank.json P+K x1), or scimitar.json x2 (§3c). **Every non-gated, non-held F6 entry with a bank row now points at a hit_frames throw=1 row.**
- 9-pool after settlement: 6 entries remain — star.json x3 (owner-gated) and scimitar.json x3 (§3c). kingtyrant.json's three throws left the pool (move_class is now throw, rows re-picked to eddy 148, hit_frames throw=1).

## 7. CI notes

- kutz.json PR #1346: instruction-gate initially failed because the proof path `game/assets/anim/t3/king/hit_frames.json` does not exist (bank king lives in `king_on_pantera_leoman/`); the PR body proof path was corrected and the gate passed; merged.
- slice.json PR #1357: speed-quality (hermetic tool gate: py_compile + Hypothesis property tests + pixelmatch self-test) failed on the first run, unrelated to moveset data; an empty retrigger commit re-ran CI, all checks passed, merged.
- torch.json PR #1359: budgets check was CANCELLED on the first run; same empty-commit retrigger, all checks passed, merged.


## 8. Addendum (2026-10-31) — section 3c resolved; final accounting

The five scimitar.json entries held in section 3c landed in PR #1364 (merge df91c42e421179f1c505cf062c16eaed3b3194f0) via a moves-scoped pass of the same surgical editor. The F6 census pool is defined on the top-level moves object, so the editor was restricted to entry blocks inside that object and the identical edit specs applied cleanly: P+K anim_t3 jin 162 -> 370, 1+4 anim_t3 jin 215 -> 370, and Back throw / Left throw / Right throw move_class strike -> throw. The run verified every other top-level key of the file — the t8_quarantine_20261024 duplicates included — parse-identical after the edit. The quarantine copies were not edited: they are a quarantine record, not runtime moves, and were never part of the census pool.

Final F6 accounting: **84 corrected + 46 settled-consistent + 37 held (11 repick-ambiguous + 26 bank-not-held) + 17 owner-gated = 184.** This supersedes the section 1 arithmetic line and the section 6 figures. Post-addendum census re-run against main at df91c42e:

- 175-pool hit_frames throw distribution: throw=1: 88, throw=0: 23, no bank row / bank not held: 64. Every remaining throw=0 entry is owner-gated (cainelias.json x2, demonio-winged.json x10) or held-ambiguous (demonio-bloodline-ember.json x10, docfrank.json P+K x1).
- 9-pool remainder: 3 entries, all star.json (owner-gated, Owner Decision List item 1).
