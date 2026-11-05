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


## Phase 3 start — Ryusan (closest)

**Started:** 2026-11-05 (this ranking PR). Not finished.

| Axis | State | Remaining |
|---|---|---|
| Model / rig | Live `model-rerig.glb` = **521 joints** (blend 520 + neutral); fidelity renders in `docs/proof/2026-11-04/smutbase6-fidelity/ryusan-*` | None for bone-count bar. Do not re-strip. |
| Character card | `game/assets/portraits/ryusan.png` present (90,289 B) but ROSTER-100 marks nearly all cards stale vs post-refit models | Re-run `tools/portraits/capture.mjs` for `ryusan` after confirming PreviewPane loads the 521-joint GLB; replace PNG only via that pipeline (320×320). |
| Moveset data | `ryusan.json`: 211 moves, **211/211** `anim_ref` (`t7:luckychloe:…`); slots identity map complete; real T7 frame data (not proxy) | No donor fills. |
| Animations | T7 Lucky Chloe bank landed (#1550): `game/assets/anim/t7/luckychloe/` + t3 generic bank; BASICS probe 9/10 + throw | Logged gaps from `docs/handoffs/SMUTBASE-T7-BANKS-2026-11-03.md`: **4 multi-hit clips** (one-clip-one-hit rule), resolver no-match rows, intro/win SHOW slots (no body-clip candidate). Fix only with real reverse-engineering-repo / T7 motion — never invent mappings. |
| Probe residual | 10/10 damaging on confirmation probe (9 correct + throw) | Optional: sequenced-press probe for strings like `d/f+1,2`. |

**Blocked without new GRE data:** inventing the 4 multi-hit clip splits or SHOW intro/win. **Not blocked:** portrait recapture (tooling exists).

