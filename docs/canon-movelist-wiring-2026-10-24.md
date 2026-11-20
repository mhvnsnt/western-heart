# Canon moves wired into the Move List Creator — 2026-10-24

Owner directive (verbatim intent, 2026-10-24): "make sure all extra canon animations that are pulled from non Tekken games or made get added to the move list creator and to appropriate additive Tekken style input to each character they go to individually".

## Scope and honesty notes

- **190 canon entries wired** across **66 moveset files**: 179 master-table moves + 9 addendum moves + 2 Chatur stance loops (TEMPLE DANCE, BRIDGE), grouped under **67 owner groups** (GERO rows wire into `docfrank.json` alongside DOCFRANK rows, so Doc Frank carries 7). Counts reconcile exactly with `canon-moves-needing-made-animations-2026-10-24.md` (179 + 9 = 188, + 2 stance loops = 190; ADAPT 147, BUILD 43).
- **Additive only.** No Tekken moves entry was replaced, overwritten, or deleted. Each file gains a top-level `canon_moves` array plus a `canon_wiring` note block. The only other change to a moveset file is an `anim_ref` field added to an existing entry that lacked one (18 backfills: Chatur 5 specials, Pond 5 specials, Megami 4 moves, Menajerii 4 moves) — no input, name, damage, or timing field was touched.
- **No new `moves`-map keys were added, deliberately.** Several canon inputs collide with existing Tekken keys (see Collision resolutions), and a minimal canon entry would have to invent active/recovery/knock/soulGain values the canon file does not give. The editor is this task's wiring surface and reads `canon_moves`; game-loader wiring of `canon_moves` is follow-up for the animation lane once clips exist. This is stated, not hidden.
- **Animation status is NOT a play claim.** `wh:` refs are placeholders for animations not yet authored (canon file header). `made:` refs are wiring labels pending the sibling animation lane's clips. PR #1012 (open, branch `megami-made-2026-10-24`) supplies the only authored MADE specs reused here: Megami's 4 canon moves (inputs verbatim, MADE ids `wh:megami:*`). PR #1012's 17 Jun-core MADE pose specs are NOT new canon moves: 13 of them already exist as Megami moveset rows (inputs match) and 4 are GEN-stance follow-ups (`GEN LP1/RP2/LK3/RK4`, already rows `GEN 1/2/3/4`); no duplicate entries were created for them. Their specs are the animation source to consult when those rows get clips.
- **Buttons use LP1/RP2/LK3/RK4 everywhere.** LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4. `input_original` preserves a filed non-Tekken notation (e.g. `P+K`, `S`) where it differs from the translated Tekken input.
- **NEEDS-INPUT: none.** Every one of the 190 moves carries a documented input from the canon file or PR #1012, so no input had to be invented and none is flagged NEEDS-INPUT. Where the canon file's translation is itself a judgment call (source-game `P+K`/`S` notations rendered as LP1+RK4 / LP1+RP2), the filed notation is preserved in `input_original` and the translation is noted in the per-character tables.
- **Editor status meanings.** `correct (canon)` = the entry is consistent with its own input under the editor's model, with canon-authored properties — it is NOT a clip-verified claim and still requires verification by playing. `approximate` = some property is unknown (see Editor change below). No canon row is `unmapped` or `wrong` in its own slot after this wiring (editor-test proof below). Stance-gated (GEN/RAGE/SCT/HRN), dash-first (`f,f`/`b,b`), and motion-first (`qcf`/`qcb`/`hcb`/`f,n,d,d/f`) inputs validate as input-consistent because the editor derives slot and candidate properties from the same input string; the stance/form gate itself is recorded on the entry (`stance`/`form` fields and the per-character tables), not verified by the editor.

## Editor change (minimal, additive)

File: `packages/creation-suite/src/movelist-editor.js` (+ test `packages/creation-suite/src/movelist-editor.canon-wiring.test.mjs`).
1. `fromMovesetFile()` now reads a fighter's `canon_moves` array (after `moves` + `specials`), skipping any entry whose `anim_ref` already appears (so Pantera-style variant keys `1+4`/`P+K` for one move never produce a duplicate row). Entries with no `anim_ref` are skipped (nothing to play).
2. `fromMovesetFile()` specials loop now prefers `special.anim_ref` (canon specials carry `wh:`/`made:` refs and no t3 row) and `special.name`; Tekken specials without `anim_ref` fall back to the t3-derived ref exactly as before.
3. `deriveCandidateProperties()` accepts `properties.source === "canon"` as known (authored) properties, returning verification `"canon"` — never `"clip"`. Unknown canon properties stay `unknown`/null and yield `approximate` in `validateAssignment()`, never silent `correct`. Tekken entries never carry source `"canon"`, so Tekken validation is untouched by this branch.
4. Slot-kind alignment (`slotKindHint()`): a slot's kind now honors `throw: true` as well as `move_class === "throw"` (candidate typing already honored `throw: true`, so throw-filed-as-`signature`/`special` rows showed `wrong` in their OWN slots — a slot-derivation bug, not bad mappings), and `move_class === "stance"` yields kind `"any"` (a stance/parry slot is neither strike nor grapple; stance/direction/limb checks still apply). This is the only editor change that moves pre-existing rows, and its full effect is counted in Editor validation below — every flipped row moves `wrong` → `correct`/`approximate`, none moves the other way, and no strike/jumping/direction/limb check changed.
5. `renderEntryRow()` labels verification `"canon"` as "(canon wiring, verify by playing)".

## Collision resolutions

Rule applied everywhere: the Tekken entry is NEVER overwritten. The canon move is wired in `canon_moves` only, and the resolution below is recorded on the entry (`collisions` field). In-game input resolution for these rows needs an owner decision; nothing was silently remapped.

- **cyborgx — Lullaby Hum (d+LP1+RP2)**: specials-input `d+1+2` = None (None). Resolution: canon wired in `canon_moves` only; Tekken row untouched.
- **docfrank — Crayon Notes (LP1+RK4)**: tekken-moves-key `1+4` = Bad Stomach (t3:bosconovitch:bad_stomach). Resolution: canon wired in `canon_moves` only; Tekken row untouched.
- **docfrank — Peer Review (LP1+RP2)**: tekken-moves-key `1+2` = Parry (t3:bosconovitch:parry). Resolution: canon wired in `canon_moves` only; Tekken row untouched.
- **phantom — Cut Is the Prayer (LP1+RP2)**: specials-input `1+2` = None (None). Resolution: canon wired in `canon_moves` only; Tekken row untouched.
- **phantom — Three Seconds Quiet (d+LP1+RP2)**: specials-input `d+1+2` = None (None). Resolution: canon wired in `canon_moves` only; Tekken row untouched.
- **sakura — You Can't Hit a Song (d+LP1)**: tekken-moves-key `D+1` = Flapping Wings to Phoenix (t7:xiaoyu:xiaoyu_189). Resolution: canon wired in `canon_moves` only; Tekken row untouched.
- **samura1 — Designation Query (LP1+RK4)**: specials-input `1+4` = None (None). Resolution: canon wired in `canon_moves` only; Tekken row untouched.
- **vf-akira — Eight Extremes (LP1+RK4)**: tekken-moves-key `1+4` = Mountain Stance [WH SIGNATURE] (wh:vf-akira:sig:mountain-stance); canon-canon `1+4` = Mountain Stance (wh:vf-akira:sig:mountain-stance). Resolution: canon wired in `canon_moves` only; Tekken row untouched.
- **vf-akira — Mountain Stance (LP1+RK4)**: canon-canon `1+4` = Eight Extremes (wh:vf-akira:sig:eight-extremes). Resolution: canon wired in `canon_moves` only; Tekken row untouched.
- **chatur — TEMPLE DANCE (stance loop) (LK3+RK4)**: tekken-moves-key `3+4` = Twin Drum (t3:ogre:row:178). Resolution: canon wired in `canon_moves` only; Tekken row untouched.
- **chatur — BRIDGE (stance loop) (LP1+RK4)**: tekken-moves-key `1+4` = Four-Arm Crush (t3:ogre:row:185). Resolution: canon wired in `canon_moves` only; Tekken row untouched.
- **System inputs (canon file open question Q5, unresolved — recorded, not decided here):** LP1+RP2+LK3+RK4 is both Nine-Soul Release (system super at full meter) and Chatur FOURFOLD MUDRA / Deathfang TRANSFORMED: SHACKLE HOWL (wolf form). LP1+RK4 is both Reihou (only while the foe is in RAGE — otherwise the moveset LP1+RK4 plays) and many fighters' LP1+RK4 signatures. Resolver precedence needs an owner decision before in-game wiring; the editor lists both rows and does not pick a winner.
- **Translation-level (not key-level) collisions:** several sigs are filed under source-game notations (`P+K`, `S`) that the canon file translates to LP1+RK4 / LP1+RP2. Where the translated input lands on another move's key in the same file (VF-Akira Eight Extremes `P+K` → LP1+RK4 vs Mountain Stance at LP1+RK4), the filed row is untouched and the translated collision is recorded here; do NOT merge `P+K` into LP1+RK4 without an owner decision. Where no literal key exists (e.g. Ryuji-Rock LAYIN' THE SMACKDOWN `P+K`, TONGUE OUT `S`), the filed notation row displays and the translation is preserved in `input_original`.

## Per-character wiring tables

Columns: move | Tekken-style input (LP1/RP2/LK3/RK4) | ADAPT/BUILD | animation ref | editor status basis (existing entry vs canon_moves-only) | move_class filed. `*` on a move name = input collision recorded above (see Collisions).


### AWAPOP → `game/assets/movesets/awapop.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Last Thing You Hear | LP1+RK4 | ADAPT | `wh:awapop:sig:last-thing-you-hear` | existing moves `1+4` | signature |
| Pop! | LP1+RP2 | ADAPT | `wh:awapop:sig:pop` | existing moves `1+2` | signature |

### BAEK → `game/assets/movesets/baek.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Homework | LP1+RK4 | ADAPT | `wh:baek:sig:homework` | existing moves `1+4` | signature |
| Kick Is the Question | LP1+RP2 | ADAPT | `wh:baek:sig:kick-is-the-question` | existing moves `1+2` | signature |

### BAEK-MASTER-WHITE → `game/assets/movesets/baek-master-white.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Eleventh Lecture | LP1+RK4 | ADAPT | `wh:baek-master-white:sig:eleventh-lecture` | existing moves `1+4` | signature |
| Master's White | LP1+RP2 | ADAPT | `wh:baek-master-white:sig:masters-white` | existing moves `1+2` | signature |

### BRUNO → `game/assets/movesets/bruno.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| 3AM Despair | LP1+RP2 | ADAPT | `wh:bruno:sig:3am-despair` | existing moves `1+2` | signature |
| Lean In | LP1+RK4 | ADAPT | `wh:bruno:sig:lean-in` | existing moves `1+4` | signature |

### BURGER → `game/assets/movesets/burger.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Appetite's Grip | LP1+RK4 | ADAPT | `wh:burger:sig:appetites-grip` | existing moves `1+4` | signature |
| Side Dish Slam | LP1+RP2 | ADAPT | `wh:burger:sig:side-dish-slam` | existing moves `1+2` | signature |

### BYOU → `game/assets/movesets/byou.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Sickness Pattern | LP1+RP2 | ADAPT | `wh:byou:sig:sickness-pattern` | existing moves `1+2` | signature |
| Wrong Foot | d+RK4 | ADAPT | `wh:byou:sig:wrong-foot` | existing moves `d+4` | signature |

### CAINELIAS → `game/assets/movesets/cainelias.json` (5 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Chokeslam | b+LP1+RP2 | ADAPT | `wh:cainelias:sig:chokeslam` | existing moves `b+1+2` | signature |
| Hell's Gate | d+LP1+RP2 | ADAPT | `wh:cainelias:sig:hells-gate` | existing moves `d+1+2` | signature |
| Last Ride | f,f+LP1+RP2 | ADAPT | `wh:cainelias:sig:last-ride` | existing moves `f,f+1+2` | signature |
| Old School | u+LP1+RP2 | ADAPT | `wh:cainelias:sig:old-school` | existing moves `u+1+2` | signature |
| Tombstone Piledriver | d/b+LP1+RP2 | ADAPT | `wh:cainelias:sig:tombstone-piledriver` | existing moves `d/b+1+2` | signature |

### CHATUR → `game/assets/movesets/chatur.json` (7 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| BRIDGE OF ARMS | b+LP1+RK4 | BUILD | `wh:chatur:bridge-of-arms` | existing specials `b+1+4` | special |
| FOURFOLD MUDRA | LP1+RP2+LK3+RK4 | BUILD | `wh:chatur:fourfold-mudra` | existing specials `1+2+3+4` | special |
| GYOU'S MARK | f,f+RP2 | ADAPT | `wh:chatur:gyou-s-mark` | existing specials `f,f+2` | special |
| OVERSOUL SURGE | qcf+RP2 | BUILD | `wh:chatur:oversoul-surge` | existing specials `qcf+2` | special |
| REFUSED TO DIE | d+LP1+RP2 | BUILD | `wh:chatur:refused-to-die` | existing specials `d+1+2` | special |
| TEMPLE DANCE (stance loop) * | LK3+RK4 | BUILD | `wh:chatur:stance:temple-dance` | canon_moves only | stance |
| BRIDGE (stance loop) * | LP1+RK4 | BUILD | `wh:chatur:stance:bridge` | canon_moves only | stance |

### CHORDZ → `game/assets/movesets/chordz.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Encore Breakdown | d/f+RK4 | ADAPT | `wh:chordz:sig:encore-breakdown` | existing moves `d/f+4` | signature |
| Power Chord | LP1+RP2 | ADAPT | `wh:chordz:sig:power-chord` | existing moves `1+2` | signature |

### CYBORGX → `game/assets/movesets/cyborgx.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Lullaby Hum * | d+LP1+RP2 | BUILD | `wh:cyborgx:sig:lullaby-hum` | existing moves `d+1+2` | signature |
| Motion Mandatory | LP1+RP2 | BUILD | `wh:cyborgx:sig:motion-mandatory` | existing moves `1+2` | signature |

### DEATHFANG-WOLF → `game/assets/movesets/deathfang-werewolf.json` (13 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| DEATHFANG — CHAINBREAK RUSH | b,b+RP2 | ADAPT | `wh:deathfang-wolf:sig:chainbreak-rush` | existing moves `b,b+2` | strike |
| DEATHFANG — FERAL MAUL | qcf+LK3 | BUILD | `wh:deathfang-wolf:sig:feral-maul` | existing moves `qcf+3` | strike |
| DEATHFANG — GRAVE BITE | d/f+LP1+RP2 | BUILD | `wh:deathfang-wolf:sig:grave-bite` | existing moves `d/f+1+2` | strike |
| DEATHFANG — MOONFANG LUNGE | f,f+RP2 | ADAPT | `wh:deathfang-wolf:sig:moonfang-lunge` | existing moves `f,f+2` | strike |
| DEATHFANG — RISING MOONCLAW | ws+LP1+RP2 | BUILD | `wh:deathfang-wolf:sig:rising-moonclaw` | existing moves `ws+1+2` | strike |
| TRANSFORMED: SHACKLE HOWL | LP1+RP2+LK3+RK4 (wolf) | ADAPT | `made:deathfang-werewolf:transformed-shackle-howl` | existing moves `wolf_howl` | special |
| WEREWOLF: CHAIN MAUL | qcf+LP1 (wolf) | ADAPT | `made:deathfang-werewolf:werewolf-chain-maul` | existing moves `wolf_maul` | special |
| WEREWOLF: FERAL REND | qcb+LP1 (wolf) | ADAPT | `made:deathfang-werewolf:werewolf-feral-rend` | existing moves `wolf_rend` | special |
| WEREWOLF: MOONFANG LEAP | f,n,d,d/f+RP2 (wolf) | ADAPT | `made:deathfang-werewolf:werewolf-moonfang-leap` | existing moves `wolf_leap` | special |
| WEREWOLF: NO FUTURE SLASH | qcf,hcb+LP1+RP2 (wolf) | ADAPT | `made:deathfang-werewolf:werewolf-no-future-slash` | existing moves `wolf_nofuture` | special |
| WEREWOLF: GRIEF PILEDRIVER | hcb,f+LP1+RP2 (wolf) | ADAPT | `made:deathfang-werewolf:werewolf-grief-piledriver` | existing moves `wolf_grab` | throw |
| WEREWOLF: GRIEF BURST | qcb,hcf+LP1+RP2 (wolf) | ADAPT | `made:deathfang-werewolf:werewolf-grief-burst` | existing moves `wolf_burst` | special |
| WEREWOLF: SHACKLE LUNGE | f,f+LK3+RK4 (wolf) | ADAPT | `made:deathfang-werewolf:werewolf-shackle-lunge` | existing moves `wolf_lunge` | special |

### DEMONIO → `game/assets/movesets/demonio.json` (3 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Apology Burned Away | qcf+LP1 | ADAPT | `wh:demonio:sig:apology-burned-away` | existing moves `qcf+1` | signature |
| RIN's Baseline | LP1+RP2 | ADAPT | `wh:demonio:sig:rins-baseline` | existing moves `1+2` | signature |
| The Unbowed | LP1+RK4 | ADAPT | `wh:demonio:sig:the-unbowed` | existing moves `1+4` | signature |

### DEMONIO-BLOODLINE-EMBER → `game/assets/movesets/demonio-bloodline-ember.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Cliff's Echo | LP1+RK4 | ADAPT | `wh:demonio-bloodline-ember:sig:cliffs-echo` | existing moves `1+4` | signature |
| Ember Bloodline | LP1+RP2 | ADAPT | `wh:demonio-bloodline-ember:sig:ember-bloodline` | existing moves `1+2` | signature |

### DIABLO → `game/assets/movesets/diablo.json` (3 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Declaration of Conquest | LP1+RP2 | ADAPT | `wh:diablo:sig:declaration-of-conquest` | existing moves `1+2` | signature |
| Final Boss Tax | LP1+RK4 | ADAPT | `wh:diablo:sig:final-boss-tax` | existing moves `1+4` | signature |
| Membrane Tear | qcf+LP1 | BUILD | `wh:diablo:sig:membrane-tear` | existing moves `qcf+1` | signature |

### DIO → `game/assets/movesets/dio.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Crime Scene | LP1+RP2 | ADAPT | `wh:dio:sig:crime-scene` | existing moves `1+2` | signature |
| Hunger Wears a Mind | LP1+RK4 | ADAPT | `wh:dio:sig:hunger-wears-a-mind` | existing moves `1+4` | signature |

### DOA-BASS → `game/assets/movesets/doa-bass.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Overtime Shift | LP1+RK4 | ADAPT | `wh:doa-bass:sig:overtime-shift` | existing moves `P+K` | signature |
| Platform Drop | LK3+RK4 | ADAPT | `wh:doa-bass:sig:platform-drop` | existing moves `S` | signature |

### DOA-HAYABUSA → `game/assets/movesets/doa-hayabusa.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Dragon's Shadow | LP1+RP2 | ADAPT | `wh:doa-hayabusa:sig:dragons-shadow` | existing moves `S` | signature |
| Falcon's Perch | u+RK4 | ADAPT | `wh:doa-hayabusa:sig:falcons-perch` | existing moves `u+K` | signature |

### DOA-KASUMI → `game/assets/movesets/doa-kasumi.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Mist Vanish | d+LP1 | ADAPT | `wh:doa-kasumi:sig:mist-vanish` | existing moves `D+P` | signature |
| Petal Scatter | LP1+RP2 | ADAPT | `wh:doa-kasumi:sig:petal-scatter` | existing moves `S` | signature |

### DOC-FRANK-MACHINE-SHOP → `game/assets/movesets/doc-frank-machine-shop.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Shop Upgrade | LP1+RP2 | BUILD | `wh:doc-frank-machine-shop:sig:shop-upgrade` | existing moves `1+2` | signature |
| Warranty Void | LP1+RK4 | ADAPT | `wh:doc-frank-machine-shop:sig:warranty-void` | existing moves `1+4` | signature |

### DOCFRANK → `game/assets/movesets/docfrank.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Crayon Notes * | LP1+RK4 | BUILD | `wh:docfrank:sig:crayon-notes` | existing moves `P+K` | signature |
| Peer Review * | LP1+RP2 | BUILD | `wh:docfrank:sig:peer-review` | existing moves `S` | signature |

### DXMMII → `game/assets/movesets/dxmmii.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Everybody's Sample | LP1+RK4 | ADAPT | `wh:dxmmii:sig:everybodys-sample` | existing moves `1+4` | signature |
| Tongue In, Run | LP1+RP2 | BUILD | `wh:dxmmii:sig:tongue-in-run` | existing moves `1+2` | signature |

### DXMMII-PATCHWORK → `game/assets/movesets/dxmmii-patchwork.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Crooked Patch | LP1+RP2 | ADAPT | `wh:dxmmii-patchwork:sig:crooked-patch` | existing moves `1+2` | signature |
| Hidden Toolbox | LP1+RK4 | ADAPT | `wh:dxmmii-patchwork:sig:hidden-toolbox` | existing moves `1+4` | signature |

### GERO → `game/assets/movesets/docfrank.json` (5 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Afterimage | b,b+LK3+RK4 | ADAPT | `wh:gero:afterimage` | existing moves `b,b+3+4` | special |
| Energy Absorption | b,b+LP1+RP2 | BUILD | `wh:gero:energy_absorption` | existing moves `b,b+1+2` | special |
| Eye Laser Beam | d,d/f,f+LP1+RP2 | BUILD | `wh:gero:eye_laser_beam` | existing moves `d,d/f,f+1+2` | special |
| Ki Blast | d/f+LP1+RP2 | BUILD | `wh:gero:ki_blast` | existing moves `d/f+1+2` | special |
| Rocket Punch | d,d/f,f+LP1 | ADAPT | `wh:gero:rocket_punch` | existing moves `d,d/f,f+1` | special |

### GYOU → `game/assets/movesets/gyou.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Cannot Stop | LP1+RP2 | ADAPT | `wh:gyou:sig:cannot-stop` | existing moves `1+2` | signature |
| Everywhere Already | d+LP1 | ADAPT | `wh:gyou:sig:everywhere-already` | existing moves `d+1` | signature |

### JIN_SOUL → `game/assets/movesets/jin_soul.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Blood Ends With Me | LP1+RP2 | ADAPT | `wh:jin_soul:sig:blood-ends-with-me` | existing moves `1+2` | signature |
| Red-Eye Warning | u+LP1 | ADAPT | `wh:jin_soul:sig:red-eye-warning` | existing moves `u+1` | signature |

### KAI → `game/assets/movesets/kai.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Doesn't Stop | LP1+RP2 | ADAPT | `wh:kai:sig:doesnt-stop` | existing moves `1+2` | signature |
| Lowest Point | d/f+RK4 | ADAPT | `wh:kai:sig:lowest-point` | existing moves `d/f+4` | signature |

### KINGTYRANT → `game/assets/movesets/kingtyrant.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Coronation Entrance | LP1+RP2 | ADAPT | `wh:kingtyrant:sig:coronation-entrance` | existing moves `1+2` | signature |
| Dig This | LP1+RK4 | ADAPT | `wh:kingtyrant:sig:dig-this` | existing moves `1+4` | signature |

### KINPO → `game/assets/movesets/kinpo.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Buttercup Finishes | LP1+RP2 | ADAPT | `wh:kinpo:sig:buttercup-finishes` | existing moves `1+2` | signature |
| Plus-One Pressure | f+LP1 | ADAPT | `wh:kinpo:sig:plus-one-pressure` | existing moves `f+1` | signature |

### KRONOS → `game/assets/movesets/kronos.json` (8 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| ATOMIC BUSTER | f,f+RP2+RK4 | ADAPT | `wh:kronos:sig:atomic-buster` | existing moves `f,f+2+4` | throw |
| CYCLONE CHOP RUSH | qcf+RP2 | ADAPT | `wh:kronos:sig:chop-rush` | existing moves `qcf+2` | special |
| CYCLONE KNEE | f+LK3 | ADAPT | `wh:kronos:sig:knee` | existing moves `f+3` | strike |
| CYCLONE UPPERCUT | d/f+RP2 | ADAPT | `wh:kronos:sig:uppercut` | existing moves `d/f+2` | strike |
| FINAL ATOMIC BUSTER | b,n,f,b,n,f+LP1+RP2 | ADAPT | `wh:kronos:sig:final-atomic-buster` | existing moves `b+1+2~donor.sf-zangief.5` | throw |
| FLYING BODY PRESS | u/f+LK3+RK4 | ADAPT | `wh:kronos:sig:body-press` | existing moves `u,FC.1+2~donor.zangief.4` | special |
| IRON STANCE | b+LK3+RK4 | BUILD | `wh:kronos:sig:iron-stance` | existing moves `b+3+4` | special |
| TIMBERWOLF LUNGE | f,f+LK3+RK4 | BUILD | `wh:kronos:sig:timberwolf-lunge` | existing moves `f,f+3+4` | special |

### KUTZ → `game/assets/movesets/kutz.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Doesn't-Care Drop | LP1+RK4 | BUILD | `wh:kutz:sig:doesnt-care-drop` | existing moves `1+4` | signature |
| Moshpit | LP1+RP2 | BUILD | `wh:kutz:sig:moshpit` | existing moves `1+2` | signature |

### LILI → `game/assets/movesets/lili.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Curtsy | LP1+RP2 | ADAPT | `wh:lili:sig:curtsy` | existing moves `1+2` | signature |
| Kiss Like a Slap | LP1+RK4 | ADAPT | `wh:lili:sig:kiss-like-a-slap` | existing moves `1+4` | signature |

### MARIPOSA-MONARCH → `game/assets/movesets/mariposa-monarch.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Fifth Thing Is the Floor | LP1+RK4 | ADAPT | `wh:mariposa-monarch:sig:fifth-thing-is-the-floor` | existing moves `1+4` | signature |
| Seal Check | LP1+RP2 | ADAPT | `wh:mariposa-monarch:sig:seal-check` | existing moves `1+2` | signature |

### MEGAMI → `game/assets/movesets/megami.json` (4 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Kaimon (Opening) | GEN LP1+RP2 | ADAPT | `wh:megami:kaimon` | existing moves `GEN 1+2` | strike |
| Seal of the Shrine | RAGE,d/f+LP1+RP2 | ADAPT | `wh:megami:seal-of-the-shrine` | existing moves `RAGE,d/f+1+2` | strike |
| Sealed Door | d/b+LP1+RP2 | ADAPT | `wh:megami:sealed-door` | existing moves `d/b+1+2` | strike |
| Threshold Keeper | b+LP1+RP2~b | BUILD | `wh:megami:threshold-keeper` | existing moves `b+1+2~b` | stance |

### MENAJERII → `game/assets/movesets/menajerii.json` (4 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Boar's Commit | f+RP2+LK3 | ADAPT | `wh:menajerii:boar-s-commit` | existing moves `f+2+3` | strike |
| Heron Strike | HRN LP1 | BUILD | `wh:menajerii:heron-strike` | existing moves `HRN 1` | strike |
| Heron's Patience | b+LP1+LK3 | BUILD | `wh:menajerii:heron-s-patience` | existing moves `b+1+3` | stance |
| Serpent's Economy | d/b+RP2+LK3 | ADAPT | `wh:menajerii:serpent-s-economy` | existing moves `d/b+2+3` | strike |

### MICHIKO → `game/assets/movesets/michiko.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Better Marketing | LP1+RK4 | ADAPT | `wh:michiko:sig:better-marketing` | existing moves `1+4` | signature |
| Edge of the Coin | LP1+RP2 | BUILD | `wh:michiko:sig:edge-of-the-coin` | existing moves `1+2` | signature |

### NEGATIVO → `game/assets/movesets/negativo.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Bounty or Fun | LP1+RK4 | ADAPT | `wh:negativo:sig:bounty-or-fun` | existing moves `1+4` | signature |
| Running Out of Room | LP1+RP2 | ADAPT | `wh:negativo:sig:running-out-of-room` | existing moves `1+2` | signature |

### NIGHTWOLF → `game/assets/movesets/nightwolf.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Ancestor's Answer | b+LP1+RP2 | BUILD | `wh:nightwolf:sig:ancestors-answer` | existing moves `b+1+2` | signature |
| Sage for the New Face | LP1+RP2 | ADAPT | `wh:nightwolf:sig:sage-for-the-new-face` | existing moves `1+2` | signature |

### PANTERA → `game/assets/movesets/pantera.json` (3 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Battle Itself | LP1+RP2 | ADAPT | `wh:pantera:sig:battle-itself` | existing moves `1+2` | signature |
| Honest Hold | LP1+RK4 | ADAPT | `wh:pantera:sig:honest-hold` | existing moves `1+4` | signature |
| Tail-Tip Lunge | f+LP1 | ADAPT | `wh:pantera:sig:tail-tip-lunge` | existing moves `f+1` | signature |

### PHANTOM → `game/assets/movesets/phantom.json` (3 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Cut Is the Prayer * | LP1+RP2 | ADAPT | `wh:phantom:sig:cut-is-the-prayer` | existing moves `1+2` | signature |
| Mask-Slip Spin | u+LP1 | ADAPT | `wh:phantom:sig:mask-slip-spin` | existing moves `u+1` | signature |
| Three Seconds Quiet * | d+LP1+RP2 | ADAPT | `wh:phantom:sig:three-seconds-quiet` | existing moves `d+1+2` | signature |

### POND → `game/assets/movesets/pond.json` (5 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| BOUNDARY CROSSING | f,f+LK3+RK4 | ADAPT | `wh:pond:boundary-crossing` | existing specials `f,f+3+4` | special |
| EGG GUARD | b+LP1+RK4 | ADAPT | `wh:pond:egg-guard` | existing specials `b+1+4` | special |
| MIST VEIL | qcb+LK3+RK4 | ADAPT | `wh:pond:mist-veil` | existing specials `qcb+3+4` | special |
| STILL WATER | d+LP1+RP2 | BUILD | `wh:pond:still-water` | existing specials `d+1+2` | special |
| TONGUE LASH | f+LP1+RP2 | BUILD | `wh:pond:tongue-lash` | existing specials `f+1+2` | special |

### PURPLERAIN → `game/assets/movesets/purplerain.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Encore Bow | u+RK4 | BUILD | `wh:purplerain:sig:encore-bow` | existing moves `u+4` | signature |
| Four-Four Time | LP1+RP2 | ADAPT | `wh:purplerain:sig:four-four-time` | existing moves `1+2` | signature |

### RAVE → `game/assets/movesets/rave.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Entrance Is the Fight | u+LP1 | ADAPT | `wh:rave:sig:entrance-is-the-fight` | existing moves `u+1` | signature |
| Green Mist | LP1+RP2 | ADAPT | `wh:rave:sig:green-mist` | existing moves `1+2` | signature |

### REALIZZT → `game/assets/movesets/realizzt.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Certified Slam | LP1+RK4 | ADAPT | `wh:realizzt:sig:certified-slam` | existing moves `1+4` | signature |
| Wizard of the Mic | LP1+RP2 | ADAPT | `wh:realizzt:sig:wizard-of-the-mic` | existing moves `1+2` | signature |

### RETSU → `game/assets/movesets/retsu.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| No Mission | LP1+RK4 | ADAPT | `wh:retsu:sig:no-mission` | existing moves `1+4` | signature |
| Pure Force | LP1+RP2 | ADAPT | `wh:retsu:sig:pure-force` | existing moves `1+2` | signature |

### RIN → `game/assets/movesets/rin.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Cold Dignity | b+LP1 | ADAPT | `wh:rin:sig:cold-dignity` | existing moves `b+1` | signature |
| Still Point | LP1+RP2 | ADAPT | `wh:rin:sig:still-point` | existing moves `1+2` | signature |

### RYUJI-ROCK → `game/assets/movesets/ryuji-rock.json` (8 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| BRAHMA BULL LARIAT | f,f+RP2 | ADAPT | `wh:ryuji-rock:sig:brahma-bull-lariat` | existing moves `f,f+2` | special |
| KNIFE SLASH | f+LP1+RP2 | ADAPT | `wh:ryuji-rock:sig:knife-slash` | existing moves `f+1+2` | special |
| LAYIN' THE SMACKDOWN | LP1+RK4 | ADAPT | `wh:ryuji-rock:sig:smackdown` | existing moves `P+K` | signature |
| PEOPLE'S ELBOW | u/f+RP2 | ADAPT | `wh:ryuji-rock:sig:peoples-elbow` | existing moves `peoples_elbow` | special |
| SAND KICK | d/b+RP2 | ADAPT | `wh:ryuji-rock:sig:sand-kick` | existing moves `d/b+2` | special |
| SERPENT SLASH | qcf+LP1 | ADAPT | `wh:ryuji-rock:sig:serpent-slash` | existing moves `qcf+1` | special |
| TONGUE OUT | LP1+RP2 | BUILD | `wh:ryuji-rock:sig:tongue-out` | existing moves `S` | signature |
| ROCK'S DDT | d/b,d/b+LP1+RP2 | ADAPT | `made:ryuji-rock:rock-s-ddt` | existing moves `rock_ddt` | throw |

### RYUSAN → `game/assets/movesets/ryusan.json` (6 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Acid Rain Dance | SCT,b+LK3+RK4 | BUILD | `wh:ryusan:acid-rain-dance` | existing moves `SCT,b+3+4` | string |
| Corrosion Claw | d/b+LK3+RK4 | BUILD | `wh:ryusan:corrosion-claw` | existing moves `d/b+3+4` | strike |
| Don't Tell Me To Calm Down | b+RP2+LK3 | BUILD | `wh:ryusan:calm-down` | existing moves `b+2+3` | special |
| Jotei's Receipt | hcb+LP1 | ADAPT | `wh:ryusan:joteis-receipt` | existing moves `hcb+1` | throw |
| Meltdown | d+LP1+RP2 | BUILD | `wh:ryusan:meltdown` | existing moves `d+1+2` | special |
| Vitriol Spit | qcf+LP1 | BUILD | `wh:ryusan:vitriol-spit` | existing moves `qcf+1` | special |

### SAKURA → `game/assets/movesets/sakura.json` (3 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Bloom Opening | LP1+RP2 | ADAPT | `wh:sakura:sig:bloom-opening` | existing moves `1+2` | signature |
| Called By Name | LP1+RK4 | ADAPT | `wh:sakura:sig:called-by-name` | existing moves `1+4` | signature |
| You Can't Hit a Song * | d+LP1 | ADAPT | `wh:sakura:sig:you-cant-hit-a-song` | existing moves `d+1` | signature |

### SAMURA1 → `game/assets/movesets/samura1.json` (3 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Designation Query * | LP1+RK4 | ADAPT | `wh:samura1:sig:designation-query` | existing moves `1+4` | signature |
| Log Entry 24 | b+LP1+RP2 | ADAPT | `wh:samura1:sig:log-entry-24` | existing moves `b+1+2` | signature |
| Undefined Soul Protocol | LP1+RP2 | BUILD | `wh:samura1:sig:undefined-soul-protocol` | existing moves `1+2` | signature |

### SCIMITAR → `game/assets/movesets/scimitar.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Closing the Deal | LP1+RK4 | ADAPT | `wh:scimitar:sig:closing-the-deal` | existing moves `1+4` | signature |
| Ledger Entry | LP1+RP2 | ADAPT | `wh:scimitar:sig:ledger-entry` | existing moves `1+2` | signature |

### SHA → `game/assets/movesets/sha.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Erodes Mountains | LP1+RP2 | ADAPT | `wh:sha:sig:erodes-mountains` | existing moves `1+2` | signature |
| Grain Shift | LP1+RK4 | ADAPT | `wh:sha:sig:grain-shift` | existing moves `1+4` | signature |

### SKULL → `game/assets/movesets/skull.json` (3 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Paint-Ride Flurry | f+RK4 | ADAPT | `wh:skull:sig:paint-ride-flurry` | existing moves `f+4` | signature |
| Retribution Keeps Books | LP1+RP2 | ADAPT | `wh:skull:sig:retribution-keeps-books` | existing moves `1+2` | signature |
| Stays Down Stomp | d+RK4 | ADAPT | `wh:skull:sig:stays-down-stomp` | existing moves `d+4` | signature |

### SLICE → `game/assets/movesets/slice.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Skull Mask Off | LP1+RK4 | ADAPT | `wh:slice:sig:skull-mask-off` | existing moves `1+4` | signature |
| Surgical Slice | LP1+RP2 | ADAPT | `wh:slice:sig:surgical-slice` | existing moves `1+2` | signature |

### STAR → `game/assets/movesets/star.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Tide-Song | LP1+RP2 | ADAPT | `wh:star:sig:tide-song` | existing moves `1+2` | signature |
| Undertow | d/b+RK4 | ADAPT | `wh:star:sig:undertow` | existing moves `d/b+4` | signature |

### SUNRA → `game/assets/movesets/sunra.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Immortal Qombat | LP1+RP2 | ADAPT | `wh:sunra:sig:immortal-qombat` | existing moves `1+2` | signature |
| The Stare | b+LP1+RP2 | ADAPT | `wh:sunra:sig:the-stare` | existing moves `b+1+2` | signature |

### THOR → `game/assets/movesets/thor.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Niflheim's Mouth | LP1+RK4 | ADAPT | `wh:thor:sig:niflheims-mouth` | existing moves `1+4` | signature |
| Swallowed Thunder | LP1+RP2 | ADAPT | `wh:thor:sig:swallowed-thunder` | existing moves `1+2` | signature |

### TOBI → `game/assets/movesets/tobi.json` (6 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Courier's Dash | f,F+RK4 | ADAPT | `wh:tobi:couriers-dash` | existing moves `f,F+4` | special |
| Escape Soul Flurry | qcf+LK3 | ADAPT | `wh:tobi:escape-flurry` | existing moves `qcf+3` | string |
| Longleap | WR+LK3 | ADAPT | `wh:tobi:longleap` | existing moves `WR+3` | strike |
| Satchel Swing | SS+LK3+RK4 | BUILD | `wh:tobi:satchel-swing` | existing moves `SS+3+4` | strike |
| The Undelivered Letter | d+LP1+RP2 | BUILD | `wh:tobi:undelivered-letter` | existing moves `d+1+2` | special |
| Tip-Off | b+LP1+RP2 | BUILD | `wh:tobi:tip-off` | existing moves `b+1+2` | strike |

### TORCH → `game/assets/movesets/torch.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Extraction Team of One | LP1+RK4 | ADAPT | `wh:torch:sig:extraction-team-of-one` | existing moves `1+4` | signature |
| Nail File | LP1+RP2 | ADAPT | `wh:torch:sig:nail-file` | existing moves `1+2` | signature |

### TOU → `game/assets/movesets/tou.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Exists to Fight | LP1+RP2 | ADAPT | `wh:tou:sig:exists-to-fight` | existing moves `1+2` | signature |
| No Motive | LP1+RK4 | ADAPT | `wh:tou:sig:no-motive` | existing moves `1+4` | signature |

### VAINABEL → `game/assets/movesets/vainabel.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Elias Brothers' Chokeslam | LP1+RK4 | ADAPT | `wh:vainabel:sig:elias-brothers-chokeslam` | existing moves `P+K` | signature |
| Purple Light Sermon | LK3+RK4 | ADAPT | `wh:vainabel:sig:purple-light-sermon` | existing moves `S` | signature |

### VF-AKIRA → `game/assets/movesets/vf-akira.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Eight Extremes * | LP1+RK4 | ADAPT | `wh:vf-akira:sig:eight-extremes` | existing moves `P+K` | signature |
| Mountain Stance * | LP1+RK4 | BUILD | `wh:vf-akira:sig:mountain-stance` | existing moves `S` | signature |

### VF-KAGE → `game/assets/movesets/vf-kage.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Hagakure Leaf | LP1+RP2 | ADAPT | `wh:vf-kage:sig:hagakure-leaf` | existing moves `S` | signature |
| Shadow Step | d+RK4 | ADAPT | `wh:vf-kage:sig:shadow-step` | existing moves `D+K` | signature |

### VF-SARAH → `game/assets/movesets/vf-sarah.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Bryant Intercept | b+RK4 | ADAPT | `wh:vf-sarah:sig:bryant-intercept` | existing moves `b+K` | signature |
| Flamingo's Answer | LP1+RP2 | BUILD | `wh:vf-sarah:sig:flamingos-answer` | existing moves `S` | signature |

### WATERFALL → `game/assets/movesets/waterfall.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| I'm Sorry | LP1+RK4 | ADAPT | `wh:waterfall:sig:im-sorry` | existing moves `1+4` | signature |
| Nine Souls' Grief | LP1+RP2 | ADAPT | `wh:waterfall:sig:nine-souls-grief` | existing moves `1+2` | signature |

### YUKIHYO → `game/assets/movesets/yukihyo.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Storm Shadow's Lesson | LP1+RK4 | ADAPT | `wh:yukihyo:sig:storm-shadows-lesson` | existing moves `1+4` | signature |
| Whiteout | LP1+RP2 | ADAPT | `wh:yukihyo:sig:whiteout` | existing moves `1+2` | signature |

### ZEN → `game/assets/movesets/zen.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Does Not Compete | b+LP1+RP2 | ADAPT | `wh:zen:sig:does-not-compete` | existing moves `b+1+2` | signature |
| Refused Seat | LP1+RP2 | ADAPT | `wh:zen:sig:refused-seat` | existing moves `1+2` | signature |

### ZUI → `game/assets/movesets/zui.json` (2 moves)

| Move | Input | Method | Animation ref | Wiring | move_class |
|---|---|---|---|---|---|
| Beautiful Stumble | d+RK4 | ADAPT | `wh:zui:sig:beautiful-stumble` | existing moves `d+4` | signature |
| Bottle's Honest Truth | LP1+RP2 | ADAPT | `wh:zui:sig:bottles-honest-truth` | existing moves `1+2` | signature |

## Editor validation (Node, editor's own functions, simulation/editor-test proof only — NOT play-verified)

- **Canon rows in the editor:** all **190** unique canon moves appear in `listAllMoves()` (by `anim_ref`). Because variant keys (`P+K`/`S` alongside digit forms) display as separate rows for one move, canon refs account for **306 list rows**: **306 `correct`** (verification `canon` for `canon_moves` rows, `input` for pre-existing moves/specials rows — both mean *consistent with its own input, verify by playing*, never clip-verified), **0 `approximate` in real data, 0 `wrong`, 0 `unmapped`, 0 missing**. The `approximate` path for unknown properties is proven by the synthetic test case in `movelist-editor.canon-wiring.test.mjs` (unknown stance → `approximate`, assignable with warning), not by a real row — no real canon row needed it, because every canon input parses to a self-consistent slot under the editor's first-hit model (stance-gated/dash/motion inputs included; see Scope notes).
- **Own-slot assignment:** every canon row's `computeMappingStatus()` allows assignment in its own slot (no canon move is hard-blocked). A genuinely wrong-kind swap is still blocked by `swapMove()` in block mode (synthetic test: grapple into strike slot → blocked).
- **Serialize safety:** `serializeMoveset()` with no edits changes **nothing** in any of the 66 wired files except adding the `movelist_editor` audit block (66/66 clean; `moves`, `specials`, and `canon_moves` byte-identical through serialize).
- **Tekken regression (old editor vs patched editor, unwired files):** **33,704** rows compared. **127 rows changed status, all `wrong` → `correct`, all explained by `slotKindHint()`:** 121 rows whose file data declares `throw: true` with a non-`throw` `move_class`, + 6 `move_class === "stance"` rows. **0 rows changed in any other direction, 0 strike/jumping/direction/limb checks changed.** Tekken validation is not weakened; two slot-derivation inconsistencies were fixed and counted.
- **NOT play-verified.** This is simulation/editor-test proof only, as the task requires. No live-game play test was run or claimed for this wiring.


## Gaps and follow-ups (honest list)

- Game-loader wiring of `canon_moves` is NOT done here: the game reads `moves`/`specials`, and no loader change was in this task's lane. Until the animation lane wires `canon_moves` into the loader (or promotes entries to `moves` keys once clips exist and collisions are resolved by the owner), canon_moves-only rows are visible and assignable in the Move List Creator but are not yet playable game moves. Rows that already existed in `moves`/`specials` keep whatever playability they had; this task changes their editor visibility (anim_ref backfill), not their clips.
- Deathfang TRANSFORM (`wh:deathfang:sig:23`, human-form LP1+RP2+LK3+RK4) is NOT wired: the canon file leaves open whether it is a made animation or a model/state swap (open question 2). The 8 addendum wolf-form moves + 5 wolf mix-ins (13 total) ARE wired.
- Chatur/Pond/Menajerii canon specials carry no startup/active/recovery in their files (canon file open question 3): `startup_frames` is null for them; timing must be authored with the animation, not copied from a Tekken row.
- Several canon moves share inputs with system moves (see Collision resolutions): resolver precedence is an owner decision, not something this task decided silently.
- VF-Akira Eight Extremes is filed as a "close-range grapple" with `throw: true` on its existing `P+K` row; its canon_moves record carries the filed row's `move_class` (`signature`), so the editor treats the `P+K` row as a grapple slot via `slotKindHint()` (throw:true). No class was re-guessed for absent moves: absent moves default to `special` except explicit "command grab" wording (`throw`) and stance loops (`stance`).
- This task does not create animation clips. Every `wh:`/`made:` ref here is a wiring reference to a clip the sibling animation lane still has to author (or PR #1012-style MADE specs to convert into clips). Nothing in this PR should be read as "the animation exists".