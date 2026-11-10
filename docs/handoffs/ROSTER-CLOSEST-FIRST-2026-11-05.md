# Roster closest-first ranking — 2026-11-05

**Generated:** 2026-11-05 12:06 CST (America/Chicago)  
**Main tip audited:** `787efe14` (includes #1578/#1579 + SmutBase fidelity #1570–#1577 + #1585)  
**Owner order (t377u/t378u):** rank closest-to-done first → restore SmutBase 6 full blend rigs → fix model / character-card / moveset / animations from the closest.  
**Supersedes:** older “Pantera first, then closest” work order. Pantera remains not 100% (55 r17-core8 slots need real King T7 data from the reverse-engineering repo; clipmap `Kg_*`; A1/C1/RC4 already fixed in #1579).

Do **not** invent clip mappings or use donor/procedural fallbacks as real moves. Do **not** clobber open PR #1566 (ASSET-PIPELINE.md) or Muse #1096 / `tools/auto_rig`.

## Score method

| Signal | Source | Weight |
|---|---|---|
| BASICS probe correct / bad | `docs/proof/2026-11-03/roster/roster-verdicts-20261103.json` | +% correct×100; −15×bad; pose-only −40; cannot-instance −80 |
| r17-core8 failing slots | `docs/proof/moveset-sweep-20261028/r17-core8-failing.json` | −1 per failing slot (cap 60) |
| Moveset density | `game/assets/movesets/<id>.json` est. move nodes | +10 if >50 |
| Character card PNG | `game/assets/portraits/<id>.png` size on main | −25 if missing/placeholder (6523 B shared dark PNG) |
| Material gate | `game/js/material-status.js` | −20 if listed |
| SmutBase full-rig already on live path | GLB JSON-chunk joint count this pass | +15 if FULL |
| modelPending / select-hidden | `game/js/roster-full.js` | −50 |

Also consulted: `docs/handoffs/ROSTER-100-FIX-2026-11-04.md`, `docs/handoffs/SMUTBASE6-FIDELITY-2026-11-04.md`, `docs/movesets/MOVE-CLIP-COVERAGE-2026-11-02.md`, `game/js/assets.js` MODEL_URLS.

**Card note:** ROSTER-100 records 71/72 portraits as stale vs post-refit models (only `negativo.png` re-captured). Presence ≠ current art. Re-run `tools/portraits/capture.mjs` after each model lane.

## Phase 2 — SmutBase 6 bone proof (aliases = blend search only)

In-game names stay Pond / Ryusan / Tobi / Chatur / Megami / Menajerii. Aliases below are **only** for finding source `.blend` files.

| WH name | Source alias | Blend found? | Blend path / search | Blend bones | Live file (`assets.js`) | Live joints (this pass) | Before (pre-#1570 era) | Verdict |
|---|---|---|---|---:|---|---:|---:|---|
| Pond | Tsuyu | YES (in-repo) | `roster/tsuyu-asui/intake/Tsuyu Asui IK/Tsuyu Asui IK.blend` (14,248,117 B) | 224 | `model-rigged-textured.glb` | **224** | 52 | **FULL already on live path (#1571). Do not redo.** |
| Ryusan | Mina | YES (in-repo) | `roster/mina-ashido/intake/Mina Ashido rigify/Mina Ashido rigify.blend` (7,396,031 B) | 520 | `model-rerig.glb` | **521** (+neutral) | 73 | **FULL already (#1574). Do not redo.** |
| Tobi | Mirko | YES (in-repo) | `roster/miruko/intake/miruko IK/mirkoIK.blend` (6,310,244 B) | 254 | `model-rerig-textured.glb` | **255** (+neutral) | 73 | **FULL already (#1570). Do not redo.** |
| Chatur | Rahkasa | YES (in-repo) | `roster/rahkasa/intake/RahkasaV1.1.blend` (11,459,182 B) | 983 full / 133 deform | `model-rigged-textured.glb` | **264** (deform set + root) | 52 | **Not 48/52.** Game loads full deform skin; `model-blend-master.glb` keeps **984** joints. |
| Megami | Parvati | YES (recovered; not in public intake/) | Recovered archive byte-identical to `ParvatiCommission.rar` (sha256 `2601d935…`); inventory `inventory-parvati-recovered.json`. Intake README only in-repo (596 MB blend kept out of public dump). | 469 | `model-rigged.glb` | **469** | 52 template | **FULL already (#1576). Do not redo.** |
| Menajerii | Vixen | YES (recovered; not in public intake/) | Recovered `Vixen_Commission.rar` (sha256 `e6d2754b…`); inventory `inventory-vixen-recovered.json`. Intake README only. | 450 | `model-rigged-noplane.glb` | **450** | 52 (`model-rigged.glb` still 52 — unused by `assets.js`) | **FULL already on live path (#1577). Do not redo.** |

**BLOCKER / DO NOT MERGE:** open PR [#1569](https://github.com/mhvnsnt/western-heart/pull/1569) rebuilds Pond onto the original **52-joint `WH_Skeleton`**. That would undo #1571 and violate the owner bar (full blend armature, not the reduced conversion). Leave #1569 open/unmerged until rewritten to keep the 224-bone source rig.

Local box search this pass: no copies of the SmutBase character blends under `/workspace` or `/tmp` (only unrelated ambientcg / fishnet / Blender startup blends). Authoritative sources are the in-repo intake paths above + recovered Megami/Menajerii holdings documented in #1575.

## Ranking table (select-visible, closest first)

| Rank | Fighter | Score | Probe correct/n | Bad | r17 fail | Moves est. | Card | Rig note | Status |
|---:|---|---:|---|---:|---:|---:|---|---|---|
| 1 | `ryusan` | 115 | 9/10 | 0 | — | 103 | present (likely stale) | FULL (#1574) live 521 | probed |
| 2 | `aotsuki` | 100 | 9/10 | 0 | — | 108 | present (likely stale) | n/a | probed |
| 3 | `awapop` | 100 | 9/10 | 0 | — | 175 | present (likely stale) | n/a | probed |
| 4 | `kronos` | 90 | 9/10 | 0 | — | 2 | present (likely stale) | n/a | probed |
| 5 | `scimitar` | 90 | 9/10 | 0 | — | 50 | present (likely stale) | n/a | probed |
| 6 | `slice` | 90 | 9/10 | 0 | — | 45 | present (likely stale) | n/a | probed |
| 7 | `thor` | 90 | 9/10 | 0 | — | 3 | present (likely stale) | n/a | probed |
| 8 | `pond` | 90 | 8/10 | 1 | — | 113 | present (likely stale) | FULL (#1571) live 224 | probed |
| 9 | `burger` | 89 | 9/10 | 0 | 11 | 107 | present (likely stale) | n/a | probed |
| 10 | `torch` | 80 | 9/10 | 0 | — | 155 | present (likely stale) | n/a | probed |
| 11 | `yukihyo` | 80 | 9/10 | 0 | — | 55 | present (likely stale) | n/a | probed |
| 12 | `megami` | 80 | 8/10 | 1 | — | 18 | present (likely stale) | FULL (#1576) live 469 | probed |
| 13 | `negativo` | 75 | 9/10 | 1 | — | 4 | present (likely stale) | n/a | probed |
| 14 | `diablo` | 75 | 8/10 | 1 | — | 90 | present (likely stale) | n/a | probed |
| 15 | `docfrank` | 75 | 8/10 | 1 | — | 421 | present (likely stale) | n/a | probed |
| 16 | `koreshi` | 75 | 8/10 | 1 | — | 108 | present (likely stale) | n/a | probed |
| 17 | `purplerain` | 75 | 8/10 | 1 | — | 142 | present (likely stale) | n/a | probed |
| 18 | `samura1` | 75 | 8/10 | 1 | — | 116 | present (likely stale) | n/a | probed |
| 19 | `star` | 75 | 8/10 | 1 | — | 134 | present (likely stale) | n/a | probed |
| 20 | `deathfang` | 66 | 8/10 | 1 | 9 | 128 | present (likely stale) | n/a | probed |
| 21 | `cainelias` | 65 | 8/10 | 1 | — | 3 | present (likely stale) | n/a | probed |
| 22 | `mariposa-monarch` | 65 | 8/10 | 1 | — | 47 | present (likely stale) | n/a | probed |
| 23 | `silvertongue` | 65 | 8/10 | 1 | — | 42 | present (likely stale) | n/a | probed |
| 24 | `menajerii` | 65 | 7/10 | 2 | — | 233 | present (likely stale) | FULL (#1577) live 450 | probed |
| 25 | `tobi` | 65 | 7/10 | 2 | — | 146 | present (likely stale) | FULL (#1570) live 255 | probed |
| 26 | `gashadokuro` | 60 | 8/10 | 2 | — | 108 | present (likely stale) | n/a | probed |
| 27 | `pantera` | 55 | 0/0 | 0 | 55 | 81 | present (likely stale) | n/a | complete-prior-lane |
| 28 | `bruno` | 50 | 8/10 | 2 | 0 | 3 | present (likely stale) | n/a | probed |
| 29 | `vainabel` | 50 | 8/10 | 2 | — | 10 | present (likely stale) | n/a | probed |
| 30 | `buffalo-bill` | 50 | 7/10 | 2 | — | 146 | present (likely stale) | n/a | probed |
| 31 | `charger` | 50 | 7/10 | 2 | — | 210 | present (likely stale) | n/a | probed |
| 32 | `kinpo` | 50 | 7/10 | 2 | — | 101 | present (likely stale) | n/a | probed |
| 33 | `phantom` | 50 | 7/10 | 2 | — | 191 | present (likely stale) | n/a | probed |
| 34 | `ryuji-rock` | 50 | 7/10 | 2 | — | 147 | present (likely stale) | n/a | probed |
| 35 | `sakura` | 50 | 7/10 | 2 | — | 84 | present (likely stale) | n/a | probed |
| 36 | `skull` | 50 | 7/10 | 2 | — | 109 | present (likely stale) | n/a | probed |
| 37 | `dorowani` | 40 | 7/10 | 2 | — | 3 | present (likely stale) | n/a | probed |
| 38 | `dxmmii-patchwork` | 40 | 7/10 | 2 | — | 22 | present (likely stale) | n/a | probed |
| 39 | `dio` | 38 | 8/10 | 2 | 12 | 12 | present (likely stale) | n/a | probed |
| 40 | `demonio` | 37 | 8/10 | 2 | 23 | 156 | present (likely stale) | n/a | probed |
| 41 | `chordz` | 35 | 7/10 | 3 | — | 71 | present (likely stale) | n/a | probed |
| 42 | `zui` | 35 | 7/10 | 3 | — | 87 | present (likely stale) | n/a | probed |
| 43 | `baek-master-white` | 15 | 6/10 | 3 | — | 3 | present (likely stale) | n/a | probed |
| 44 | `rave` | 15 | 6/10 | 3 | — | 31 | present (likely stale) | n/a | probed |
| 45 | `cyborgx` | 4 | 6/10 | 3 | 21 | 116 | present (likely stale) | n/a | probed |
| 46 | `waterfall` | -15 | 5/10 | 5 | — | 73 | present (likely stale) | n/a | probed |
| 47 | `chatur` | -30 | 0/0 | 0 | 5 | 7 | present (likely stale) | FULL deform 264 not 52; master 984 | probed |
| 48 | `zen` | -30 | 0/0 | 0 | — | 72 | present (likely stale) | n/a | probed |
| 49 | `kingtyrant` | -70 | 0/0 | 0 | — | 151 | present (likely stale) | n/a | cannot-instance |
| 50 | `nightwolf` | -70 | 0/0 | 0 | — | 56 | present (likely stale) | n/a | cannot-instance |
| 51 | `michiko` | -80 | 0/0 | 0 | — | 28 | present (likely stale) | n/a | cannot-instance |
| 52 | `ryuji` | -120 | 0/0 | 0 | — | 129 | present (likely stale) | n/a | cannot-instance |
| 53 | `gyou` | -145 | 0/0 | 0 | — | 198 | placeholder | n/a | cannot-instance |
| 54 | `kai` | -145 | 0/0 | 0 | — | 156 | placeholder | n/a | cannot-instance |
| 55 | `retsu` | -145 | 0/0 | 0 | — | 103 | placeholder | n/a | cannot-instance |
| 56 | `rin` | -145 | 0/0 | 0 | — | 75 | placeholder | n/a | cannot-instance |
| 57 | `sha` | -145 | 0/0 | 0 | — | 84 | placeholder | n/a | cannot-instance |
| 58 | `tou` | -145 | 0/0 | 0 | — | 60 | placeholder | n/a | cannot-instance |
| 59 | `byou` | -155 | 0/0 | 0 | — | 29 | placeholder | n/a | cannot-instance |

## Closest to finish — recommended fix order

1. **`ryusan`** — #1. Full 521-joint live rig. BASICS 9/10 + throw. Real Lucky Chloe T7 bank (#1550). Remaining: recapture stale card after fidelity; finish any unmapped Lucky Chloe teardown rows with **real** reverse-engineering-repo data only; no donor fills.
2. **`aotsuki` / `awapop`** — 9/10 BASICS, dense movesets. Next after Ryusan card/moveset polish (model/card audit + any fire-no-damage hit-window fixes).
3. **`pond`** — full 224-joint live rig; 8/10 (+1 fires-no-damage). Do **not** accept #1569 as written.
4. **`megami` / `menajerii` / `tobi`** — full live rigs; residual probe bads + bank completeness (Jun/Roger/Hwoarang). Menajerii still on kuma stand-in bank per verdict note — real Roger Jr. bank owed from reverse-engineering repo, not invented.
5. **`pantera`** — wiring complete-prior-lane but **55** r17-core8 slots open (`Kg_*`). Not closest.
6. **`chatur`** — rig full (264 deform / 984 master) but pose-only / no True Ogre moveset file anywhere — blocked on real source, leave unmapped.
7. Material-gate cannot-instance: `kingtyrant`, `nightwolf`, `michiko` (SHORT bakes).
8. modelPending placeholders: rin/byou/tou/sha/kai/retsu/gyou (+ ryuji by design).

## Next steps for Muse / this lane

- Phase 1 (this doc) + BUILD-LOG entry → PR, merge when green.
- Phase 2: **closed by verification** for all six live paths (see table). No bone invention.
- Phase 3: start **Ryusan** — portrait recapture + remaining real teardown rows; re-rank when finished.
- Never merge #1569 as a 52-bone Pond graft. Never touch arena sky/lighting/colors. Pages republish only after a real merged asset fix, under 1 GB.


## Phase 3 — Ryusan (closest) — update 2026-11-05 12:31 CST

**Card: DONE this pass.** Anims: finishable multi-hit/SHOW left **explicitly unmapped** (real multi-hit bake / body SHOW clips do not exist yet).

| Axis | State | Remaining |
|---|---|---|
| Model / rig | Live `model-rerig.glb` = **521 joints** | None for bone-count bar. **Ops:** B2 remote still serves stale ~2.1 MB / ~73-bone copy — re-upload from main before live Pages shows the fidelity model. |
| Character card | **RECAPTURED** via `tools/portraits/capture.mjs` → `game/assets/portraits/ryusan.png` (select path). Manifest `bones:521`, `framed:true`. Proof: `docs/proof/2026-11-05/ryusan-phase3/`. sha256 `82ed443be85d61e976adeb07a7a3ea1598b6cc215b8cb1161473a4c81f63c290` (was stale `f156bf5e…` 90289 B). | Stance fit fails on 521-bone rig (luckychloe bank Left shoulder ~1.23 rad) — card uses bind/aim frame. Stance retarget is a separate anim lane, not invented here. |
| Moveset data | 211/211 `anim_ref` | No donor fills. |
| Animations | Pack has 27 moves / 25 clips | **UNMAPPED by name (no invent):** pack skips `1+2`, `u+3+4`, `f+3+4`, `b+1+2` (one-clip-one-hit). SHOW `intro`/`win` (`t3_stance.json` / `t3_win_rp.json`) — no body-clip in motbin. Sequenced-press probe = tooling follow-up. |
| Probe residual | 9/10 + throw | Sequenced-press probe still owed. |

**Ryusan not 100% complete** (4 multi-hit + SHOW + stance-fit + B2 refresh). Closest-for-next-finishable after card: still polish Ryusan anims when GRE multi-hit bake exists; else start **Aotsuki** / **Awapop** model+card+moveset pass.

**Do not merge #1569** (52-bone Pond graft).



## Source search record (t380u–t383u) — 2026-11-05 12:53 CST

Searched reverse-engineering repo + WH + Steam-extract trees before any missing claim.

### Chatur / True Ogre — FOUND (already in WH)

| What | Path |
|---|---|
| T3 Ogre anim bank | `game/assets/anim/t3/ogre/` |
| Moveset (281 rows) | `game/assets/movesets/chatur.json` |
| Mirror | `game/assets/movesets/t3-ogre.json` |
| Runtime | `FIGHTER_BANK.chatur = 'ogre'` in `game/js/fighter.js` |
| Decode | commit `ed16dd6c` (2026-10-23) |
| Proof | `docs/proof/claude-2026-10-23/t3-banks/` |
| Template | `t3-ogre-bank` → **attached-existing** |

GRE `tekken3/animations/`: divmot03/04/07/09/12/13/16/99 only (no divmot14 this pass). WH bank is the landed asset.

### Ryusan multi-hit — motion FOUND (`mhvnsnt/game-reverse-engineering`)

- `teardown/tekken7-steam/tkdata/mothead/bin/dncmot.bin` (2,621,500 B)
- `teardown/tkdata/mothead/bin/dncmot.bin`
- `teardown/tekken7-steam/tkdata/mothead/mask/dncrotsm.arc`
- WH pack still skips `1+2`, `u+3+4`, `f+3+4`, `b+1+2` (`t7_move_bake.py` one-clip-one-hit). Per-hit bake next — not invented.

### Pages

- #1588 → `a2aa63e8`; Pages `cd2905e2` ryusan card.

### t383u land note
- Chatur True Ogre: **FOUND** in WH (not missing). Template attached-existing via #1590.
- Ryusan: card on main; GRE `dnc.json`+`dncmot.bin` named; multi-hit/SHOW still bake-gated after search.
- Pages tip `32607e2b` (publish watch).



## 2026-11-10 — Owner override: PANTERA FIRST (t386u)
- Pass 1: Tekken f,f dash / b,b backdash restored from King T7 motbin + t7_king clips (node-proven; touchscreen proof pending). Open Pantera items, in order:
  1. Duplicate plain vs `~t7.king` rows resolving to unmapped clips.
  2. KBD (group-cancel decode).
  3. Run / re-dash at dash frame 12.
  4. f,n,d,df CD (`cd_entry`).
  5. T7-bank sidestep axis.
  6. Full movelist / throws / chains matrix.
  See `docs/proof/2026-11-10/pantera-tekken-dash/INPUT-MATRIX.md`.

- Pass 2 (2026-11-10): 15 King T7 string steps baked and wired; Pantera plain rows on real King T7 41 → 61 / 643. Next: motion (f,F / f,f) rows via resolver motion support, then stance rows, then throws.
- Pass 3 (2026-11-10): King T7 dash/run moves (f,F+X, f,f,n,2, f,f,f+3/3+4) resolved on King link tables, baked and wired; plain rows on real King T7 61 → 68 / 643. Next: decode input-sequence commands (f,n,d,d/f CD, WR variants) and the KBD group-cancel table.
- Pass 4 (2026-11-10): `f,f,F+3` / `f,f,F+3+4` play King T7 (sourced run alias). The KBD backdash crouch cancel is wired from King's group-cancel table. King T7 sequence/group/requirement tables are decoded (`tools/anim/t7_table_dump.py`). Plain rows on real King T7 68 → 70 / 643. Next: bake run locomotion `Bco_run00`, then WR rows, then throws.
- Pass 5 (2026-11-10): real King T7 run locomotion (dash, f held at frame 12 → sRUN chain, own clips and root travel, requirement-0 exits). Next: run attacks from the real run state (WR rows), gated requirement decode, throws.
- Method change (t388u): King's FULL T7 graph is imported (2,787 moves / 42,621 cancels) with a source-order runtime interpreter and a batch clip bake. Next: the fighter adapter that drives Pantera from the graph (no handwritten rows), then requirement-condition decode.
- Graph adapter (2026-11-10): Pantera can run King's full T7 graph through the real input path as an opt-in DEVELOPMENT integration (`?t7graph=1`). 66 evaluable stance commands are replayed; 28,247 reachable rows are blocked on unknown conditions (217 char-ID, 609, 225, 72 backturn, …). Next: the condition decode (char-ID table, backturn state, distance units), then throws, then sidesteps 0x8003/0x8004.
- Requirement decode (2026-11-10): the exe evaluator decodes 217/225/609/72/73/80/81/35/36/126/554. Unknown reachable rows 28,247 → 13,567, and 73 stance commands replay. Next: the 609 item set, the facing word (backturn/posture), and the evaluator caller (≥0x8000 ids).
- Facing decode (2026-11-10): exe facing words decoded (72/73/80/81 = own yaw vs bearing). They stay UNKNOWN in play until the own-yaw setters are traced. Throws are marked UNSUPPORTED (no grab), and the 0x4000 throw-marker hitbox bug is fixed. Next: own yaw `[+0x1b8]` setters (turn/tracking), then posture.
- Strict precedence (2026-11-10): exe AND lists; STRICT is the dev default. Pantera's stance is fully blocked by row #0 (player vars 809/361 from extra move properties). Next: the extra-property import plus the exe handler, then throws.
- Player vars (2026-11-10): extra props imported (graph.props.json); 809/361 decoded and zeroed at match start; row #0 known-false. Strict still blocks at row #132 (815/359/553). Next: the apply-timing of requirement-list props, then the opponent parry state, then throws.
- Player flags (2026-11-10): exe init zeroes the 100 flag words, and 359 is decoded. 329 exe default-false requirement ids are imported. Row #132 is known-false. Strict is still at 0 stance commands, blocked by facing 72/80 (own yaw `[+0x1b8]`) and 356 (`[+0x390]`). Next: the yaw writers and `[+0x390]`; the throw binary reader.
- Exe walker (2026-11-10): loader-derived cancel_option, main/secondary walk, matcher and list-property timing transcribed. Strict neutral→jab→1,2 string, walk and dash work with the opponent ahead. Blocker: source heading after a source move (`0x14074afe0`, move word 0x56). Next: heading tracker, then `[+0x390]`, then extra-prop frame timing.

- 2026-11-10 14:55 CST Pantera T7 graph: heading trace — per-frame yaw term T undecoded is the continuity blocker; PR #1737 open, not merged (`docs/proof/2026-11-10/t7-heading/README.md`).
