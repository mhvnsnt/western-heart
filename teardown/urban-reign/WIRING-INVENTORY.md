# Urban Reign — WIRING INVENTORY (Phase-4 canonical record)

> Branch note: the phase-2 wiring inventory lives on the PR #442
> branch (`ur-phase2-motion`) version of this file. This phase-4
> version is created on `ur-phase4-assignment` because that file is
> not present in the phase-3 tree; on merge it supersedes the
> phase-2 inventory's model-set statements. Everything below is
> stated as of Phase 4 (PR #506, stacked on #464).
>
> Phase-5 addendum (PR #518, stacked on #506): the Move names,
> char064 geometry, Accessory pieces and Node graph rows below were
> updated in Phase 5 — see `PHASE5-STATE.md`,
> `motion-names/PHASE5-NAME-BRIDGE-SUMMARY.md`,
> `PHASE5-JOB2-TYPE14.md` and `PHASE5-JOB3-EXECUTIONS.md`.

## CANONICAL FIGHTER MODEL SET — CHANGED IN PHASE 3, RECORDED HERE

**`teardown/urban-reign/textured-models/` is THE canonical fighter
model set for Urban Reign** — 72 textured GLBs
(`charNNN_textured.glb`, 733 embedded images total, `MANIFEST.json`
with per-character geometry-identity verification against the
phase-1 GLBs). It **supersedes** the untextured phase-1 GLBs
(`teardown/urban-reign/models/charNNN/charNNN.glb`, PR #429 branch)
as the source of truth for fighter models. The phase-1 GLBs remain
the geometry/skinning provenance record (the textured set's
verts/indices/joints are verified identical to them per character).

## Game-side copies — swap is a named one-step follow-up (NOT done)

`game/assets/models/street-reign/` (on the PR #442 branch) holds
`charNNN.glb` — the untextured phase-1 copies, 31 of them with
embedded native animation. The canonical textured files are named
`charNNN_textured.glb`, so refreshing the game copies is **not** a
byte-swap of the same filenames, and the 31 animated game GLBs
carry embedded clips the textured GLBs do not. Per the phase-4
rule, the swap was **not** performed. The one-step follow-up:
re-run the phase-2 embedder (`ur_embed.py` / `ur_batch_embed.py`)
with the textured GLBs as the base for the 31 pmot fighters, copy
all 72 textured GLBs into `game/assets/models/street-reign/` under
the existing `charNNN.glb` names, and re-run the roster resolution
check (72/72) from PR #434.

## Decoded / wired / left-before-playable (after Phases 1–4)

| Class | Decoded | Wired into game/ | Left before playable |
|---|---|---|---|
| Fighter models (72) | ✅ skinned + textured, canonical set above | ⚠️ untextured copies wired (PR #434); textured swap = follow-up above | textured swap |
| Native animation (31 pmot fighters) | ✅ `.gyu` cracked, banks embedded in game GLBs (PR #442) | ✅ clips `ur_m*` + `Idle` in game GLBs + `ur-charNNN.json` records | — |
| General-pool animation (829 motions) | ✅ converted to packed banks `game/assets/anim/ur-general-{normal,30frame,weapon}/` | ⚠️ shared pool data only, not per-fighter | per-fighter assignment = runtime capture (Phase-4 Job-1 report spec) |
| Proxy fighters (41) | ✅ models decoded | ⚠️ proxy movesets | assignment (above); native count stays **31/72** |
| Move names | ✅ **Phase 5 (PR #518): 484 own-bank pairs proven across the 27 fighters with held motdat pairs** (886 records held; gate maxDev ≤0.10 mm, unique) in `motion-names/name-bridge-<char>-proven.json` + `PHASE5-NAME-BRIDGE-SUMMARY.md`; 306 further records proven in another bank (cross-bank hits recorded per record, not assigned to the fighter's clips). Type-14 root decode CRACKED (Phase-5 Job 2, `PHASE5-JOB2-TYPE14.md`): P1 now 30/35 records sourced (27 own-bank + weapon/tmot/pmot042 cross-bank); 5 P1 records (6, 10, 11, 12, 14) have no identity in any of 46 shipped banks searched — source bank outside the shipped set, NOT a decode gap. 3 borderline pairs (0.102–0.136 mm, noise-profile) left unproven under the gate | ✅ `motdatName` annotations in `game/assets/movesets/ur-charNNN.json` for all 27 fighters on the Phase-5 branch (char001's from Phase 4 + 26 added from the Phase-2 records, bank-verified clip-by-clip before annotating) | the 5 unsourced P1 records + Gnrl naming (needs a bank outside the shipped set / runtime capture) |
| Textures (72 sets) | ✅ composed CT32/PSMT8+PSMT4 decode (PR #464) | ✅ embedded in canonical GLBs | — |
| char064 geometry | ✅ **RECOVERED 1260/1260 in Phase 5** (`PHASE5-JOB3-EXECUTIONS.md` (a)): the missing piece was group-0 packet 3 (63 verts, two batched rigid sub-objects), dropped at assignment because no single palette window anchors both sub-objects; recovered by splitting the run at its uvflag segment break (vert 42) — each half independently took its siblings' candidate. Textured GLB rebuilt: 1260 verts / 1737 indices / 14 joints / 13 images (was 1197/1674/14/13) | ✅ canonical textured GLB + MANIFEST updated on the Phase-5 branch | — |
| Accessory pieces (11 chars) | ⚠️ unproven skinning — Phase-5 Job-3 (b): PPK `0xae00` test EXECUTED (zone enumerated for char001/042/056/064): palettes + node-group lists only, no per-accessory bone data; per-piece residuals stand (table in `PHASE5-JOB3-EXECUTIONS.md`); NO guessed placements shipped | ⚠️ as-is | runtime (PCSX2) pose capture is the only remaining discriminating evidence |
| Node graph | ⚠️ H-index assumption; proven for bodies (max dev 1.8e-07), suspect for accessories. Phase-5 (c): the `0xae00` test does NOT close the suspicion — no parent/child graph exists in the header-graph zone (explicit verdict in `PHASE5-JOB3-EXECUTIONS.md`) | ✅ as documented assumption | PCSX2 capture of the game's evaluated skeleton |
| Stages (7 PPKs) | ❌ geometry not decoded | ❌ | stage decode (out of phase-4 scope) |
| Missions (356 files) | ❌ not decoded | ❌ | mission decode |
| Audio (ADX 1133 / banks 1034 / VGS 88) | ⚠️ VGS format documented | ❌ | audio conversion |
| Cutscenes (35) / UI (76) | ⚠️ UI documented | ❌ (game uses own UI) | — |

## Identities

`CANON-CONVERSION.md` identities remain **OWNER-pending**
(CHAR001..072). No identity was invented or changed in Phase 4.
The SLUS named-`.gyu` string table (Phase-4 Job-1 report, item 5)
is recorded as evidence only; it is not a canon assignment.
