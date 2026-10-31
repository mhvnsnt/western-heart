# Moveset Provenance — Phase 1 Continuation (2026-10-31)

Lane: moveset-provenance phase 1 continuation, resumed by owner order 2026-10-31
("Resume the stalled lanes now" — lane G, canon movesets; core order 2026-10-25:
"get all the movesets and animations done all the inputs done for every character
so I can play this game").

Method, identical to Phase 1: the frozen branchwalk proof engine
(`BRANCHWALK-SPEC.md` A/B/C/S evidence grading) re-run over every remaining
guess-grade `anim_t3` mapping in the 36 class 1-W files, against each fighter's
own T3 bank branch graph, with hit_frames throw/button gates and the rows.pack
presence gate. Three passes per file: pass 0 = Phase 1's own configuration
(native anchors only); pass 1 = plus corrected-twin anchors (Phase 1's landed
corrections as evidence); pass 2 = plus read-only lineage anchor files. Only
graph-proven corrections land, one fighter per PR, via the Git Data API from the
verified current main tree. Everything unprovable stays byte-identical.

**DATA-CORRECTED is not play-verified.** Nothing in this document promotes any
mapping to VERIFIED; that gate belongs to play-verify video evidence, which is
owner-gated and not this lane's.

## Headline numbers (all re-parsed by this lane from the files themselves)

- Guess-grade remaining at this lane's fetch: **8,574** across the 36 class 1-W
  files. (The Phase-2 doc's table said 8,593; the −19 delta is in the four
  bosconovitch doc-frank files — hood/machine-shop/wowomomo 232→227 each,
  frankenstein 186→182 — from sibling F6/burn-down corrections merged between
  that doc and this lane's fetch. Every other file's count matches the doc
  exactly.)
- Proven with today's evidence: **22**, all landed (below).
- Proven but HELD: **33** (paul bank; sole anchor source is an owner-gated
  file — see Held section).
- Remaining guess-grade after this lane: **8,552**, grouped by blocker below.
- Buffalo Bill's forestlaw-bank pass (a 37th run over the same file) proved 0;
  its 305 guess entries are the same entries counted once under the law bank.

## Landed

| PR | Merge commit | File | Corrections | Proofs |
|---|---|---|---|---|
| #1369 | `c9859b540e42d3efb452a2bbd043be8947f711a7` | pantera.json (king) | 20 | A×4, S×3, C×13 |
| #1372 | `cce19f43dd0c310ff715eedc81dd555be5b364ea` | anim/t3/jin/rows.pack.json (bake, see Rin) | row 217 added | — |
| #1374 | `cea9a96af6fc7a2b6adf684e3955ecac0b0b82eb` | rin.json (jin) | 2 | B×2 |

Pantera detail: 7 corrections change the anim row (input `2` → row 99 in 2
entries, `2,1` → row 220 in 3 entries, `u/f+2` → row 245, `u/f+3` → row 55);
13 are proof-C label-only confirms (row already correct, guess-grade label
upgraded to the true-map label). Pantera was provable in pass 0 already — its
own file's native anchors plus strings paths suffice; the king bank has no
sibling files. Verified from main after merge: 20 surgical provenance_fix
records present, remaining guess-grade 175.

## Rin holdback — resolved

Rin's `b+2,1` → Jin row 217 was graph-proven in Phase 1 (proof B) but row 217
was not baked into `game/assets/anim/t3/jin/rows.pack.json`, so the pack gate
held it. This lane:

1. Baked it as its own PR (#1372): `tools/anim/t3_row_bake.py --merge
   --bank jin --rows 217` in a sparse checkout of verified main, with the
   Tekken3Remake research modules the tool requires. Verified by re-parse:
   pack 226 → 227 rows, added key 217 only (slot 556, move_row 217,
   stream_frames 20, n 10), no existing row changed, header and sha256 fields
   identical, `missing` still empty.
2. Re-ran the proof pass for rin against the merged pack: both corrections
   pass the gate (proven 2, not-baked 0).
3. Landed them in per-character PR #1374: `b+2,1` and `b+2,1~t7.jin.2`,
   row 60 → 217, proof B. Rin remaining guess-grade: 211 of 213.

## Held — proven, not landed (owner-gated anchor evidence)

Pass 2 proved 33 paul-bank corrections (t3-paul 18, tou 15; proofs A and C)
that passes 0–1 cannot reach. Their sole enabling anchor source is
gyou-spirit-body.json's direct paul-port entries — and gyou-spirit-body is
Owner Decision List item 5 (Paul wiring vs Hwoarang canon). The lane brief
gates anything touching the Decision List files, so these 33 are counted and
held, not landed. They land mechanically the moment item 5 is ruled (or if the
owner rules the anchor use acceptable); the proof records are preserved in the
lane's sweep output. The other lineage sources produced zero deltas
(demonio-winged for jin, star for eddy/xiaoyu, docfrank + t3-bosconovitch for
bosconovitch, jin_soul for yoshimitsu).

## Per-file results

| File | Bank | Guess-grade | Proven today | Landed | Held (gated anchor) | Remaining |
|---|---|---:|---:|---:|---:|---:|
| aotsuki.json | kuma | 170 | 0 | 0 | 0 | 170 |
| awapop.json | nina | 204 | 0 | 0 | 0 | 204 |
| buffalo-bill.json | law | 305 | 0 | 0 | 0 | 305 |
| demonio-bloodline-ember.json | jin | 232 | 0 | 0 | 0 | 232 |
| demonio-human.json | jin | 140 | 0 | 0 | 0 | 140 |
| demonio.json | jin | 136 | 0 | 0 | 0 | 136 |
| diablo.json | heihachi | 115 | 0 | 0 | 0 | 115 |
| doc-frank-frankenstein.json | bosconovitch | 182 | 0 | 0 | 0 | 182 |
| doc-frank-hood.json | bosconovitch | 227 | 0 | 0 | 0 | 227 |
| doc-frank-machine-shop.json | bosconovitch | 227 | 0 | 0 | 0 | 227 |
| doc-frank-wowomomo.json | bosconovitch | 227 | 0 | 0 | 0 | 227 |
| gashadokuro.json | kuma | 170 | 0 | 0 | 0 | 170 |
| gyou.json | hwoarang | 409 | 0 | 0 | 0 | 409 |
| kai.json | eddy | 285 | 0 | 0 | 0 | 285 |
| kingtyrant.json | eddy | 200 | 0 | 0 | 0 | 200 |
| nightwolf.json | julia | 149 | 0 | 0 | 0 | 149 |
| pantera.json | king | 195 | 20 | 20 | 0 | 175 |
| phantom.json | yoshimitsu | 268 | 0 | 0 | 0 | 268 |
| retsu.json | bryan | 353 | 0 | 0 | 0 | 353 |
| rin.json | jin | 213 | 2 | 2 | 0 | 211 |
| sakura.json | xiaoyu | 167 | 0 | 0 | 0 | 167 |
| samura1.json | gunjack | 192 | 0 | 0 | 0 | 192 |
| sha.json | xiaoyu | 167 | 0 | 0 | 0 | 167 |
| skull.json | bryan | 225 | 0 | 0 | 0 | 225 |
| t3-anna.json | anna | 312 | 0 | 0 | 0 | 312 |
| t3-eddy.json | eddy | 280 | 0 | 0 | 0 | 280 |
| t3-hwoarang.json | hwoarang | 402 | 0 | 0 | 0 | 402 |
| t3-julia.json | julia | 147 | 0 | 0 | 0 | 147 |
| t3-kuma.json | kuma | 170 | 0 | 0 | 0 | 170 |
| t3-law.json | law | 306 | 0 | 0 | 0 | 306 |
| t3-lei.json | lei | 425 | 0 | 0 | 0 | 425 |
| t3-nina.json | nina | 311 | 0 | 0 | 0 | 311 |
| t3-paul.json | paul | 227 | 0 | 0 | 18 | 227 |
| tobi.json | hwoarang | 402 | 0 | 0 | 0 | 402 |
| torch.json | anna | 207 | 0 | 0 | 0 | 207 |
| tou.json | paul | 227 | 0 | 0 | 15 | 227 |
| **Total (36 files)** | | **8574** | **22** | **22** | **33** | **8552** |

## Remaining 8,552, grouped by named blocker (pass-1 configuration)

| Blocker | Count | Meaning |
|---|---:|---|
| no-anchor | 6,842 | First step has no direct-twin or strings anchor. The overwhelming majority are stance/direction-prefixed inputs (WS/FC/BT/crouch-dash families) whose first step resolves only through T3 branch condition codes — the sibling lane's decode. |
| no-branch | 1,270 | Anchored first step, but a later string step matches no branch command in the current row's graph branches. |
| unparsable-step | 329 | A string step has no parseable button part (direction-only follow-ups). Also condition-code territory. |
| ambiguous-branch | 72 | More than one branch matches and the hit_frames button gate cannot break the tie. |
| throw-gate | 18 | A proof fired but the target row's hit_frames throw flag contradicts the move's class. |
| foreign-bank skipped | 21 | Guess entries pointing at a bank other than the file's correction bank; never touched by design. |
| proven-not-baked | 0 | (Rin's 2 were the last members of this class; resolved by the row-217 bake.) |

Total: 6,842 + 1,270 + 329 + 72 + 18 + 21 = 8,552. ✓

## Phase 2 — F4 class-3 layer rows, accounted (no edits)

The Phase-2 doc established that the three "residue layers" are T8-form
true-map layers, not placeholders; T8 governs them and the T3 branchwalk engine
has nothing to prove or correct in them — they carry `t8:` true-map references
(or, for koreshi's heihachi layer, a settled anim_t3 layer under the Phase-2
treatment), not guess-grade mappings. This lane verified the layers in the
current files and made **zero edits**:

| Layer | File | Rows (this lane's re-parse) | Status |
|---|---|---:|---|
| Yoshimitsu T8 layer | koreshi.json | 312 | OWNER-GATED (Decision List item 10) — untouched |
| Heihachi layer | koreshi.json | 48 | part of the same gated koreshi accounting — untouched |
| Devil Jin T8 layer | demonio.json | 35 | T8-form true-map — untouched |
| Paul T8 layer | gyou.json | 47 | T8-form true-map — untouched |

Total F4: **442** by re-parse (the brief said 439 and the Phase-2-derived count
is 441; the one-row delta is demonio's devil_jin layer — 35 `t8_source:
devil_jin` entries in the current file vs 34 in the earlier count. The
treatment is identical either way). Not F4: demonio's jin T8 layer (138) and
gyou's hwoarang T8 layer (209) are those files' base T8 mappings, and
koreshi's vega layers (372 + 160) are its settled base per Phase 2.

Owner-gated files were not edited anywhere in this lane: star, byou, jin_soul,
demonio-winged, gyou-spirit-body, charger, charger-attire2, street-reign,
cainelias, and koreshi's Yoshimitsu layer. Class 2 approved mixes, class 1-S
source-pending files, and class D files were likewise untouched.

## Bootstrap re-sweep

After all three PRs merged, the lane refreshed its pantera.json and rin.json
copies from main and re-ran the entire sweep (37 runs × 3 passes) with the 22
new corrections in place as corrected-twin anchors. Result: **zero new
proofs.** The only differences from the first sweep are the landed entries
leaving the guess pool (pantera 195 → 175 guess-grade, rin 213 → 211) and the
blocker totals settling at exactly the numbers in the table above
(guess_total 8,552 = 6,842 + 1,270 + 329 + 72 + 18 + 21, pass-1 configuration).
Phase 1 is exhausted with today's evidence; the remainder is the sibling
lane's condition-code decode, not more branchwalk passes.

## What unblocks the rest

The 8,552 remaining are dominated by no-anchor (6,842) and unparsable-step
(329) — both are the T3 branch condition-code decode the sibling lane owns.
When that decode lands, this same sweep re-runs and the newly anchored strings
either prove or stay counted. Nothing here waits on any other lane, and no
number in this document comes from a worker report: every count was re-parsed
by this lane from the files or from `gh` output.
