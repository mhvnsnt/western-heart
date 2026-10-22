# Urban Reign — WIRING INVENTORY (Phase-4 canonical record)

> Branch note: the phase-2 wiring inventory lives on the PR #442
> branch (`ur-phase2-motion`) version of this file. This phase-4
> version is created on `ur-phase4-assignment` because that file is
> not present in the phase-3 tree; on merge it supersedes the
> phase-2 inventory's model-set statements. Everything below is
> stated as of Phase 4 (PR #506, stacked on #464).

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
| Move names | ⚠️ **27/35 P1 pairs proven** (Phase-4 Job 2, root-stream identity) and assigned in `motion-names/name-bridge-p1-proven.json`; motdat lists for all pmot fighters exist in the AFS | ⚠️ char001 record updated on this branch (see state file) | type-14 root-decode fix → remaining 8 P1 records + all other fighters' lists + Gnrl naming |
| Textures (72 sets) | ✅ composed CT32/PSMT8+PSMT4 decode (PR #464) | ✅ embedded in canonical GLBs | — |
| char064 geometry | ⚠️ 1197/1260 verts (Phase-4 Job-3 (a)) | ⚠️ as-is | one s16 group; decoder reject-log step named |
| Accessory pieces (11 chars) | ⚠️ unproven skinning (Job-3 (b)) | ⚠️ as-is | per-piece PPK proof or the (c) graph correction |
| Node graph | ⚠️ H-index assumption; proven for bodies (max dev 1.8e-07), suspect for accessories (Job-3 (c)) | ✅ as documented assumption | PPK `0xae00` bone-index decode test named |
| Stages (7 PPKs) | ❌ geometry not decoded | ❌ | stage decode (out of phase-4 scope) |
| Missions (356 files) | ❌ not decoded | ❌ | mission decode |
| Audio (ADX 1133 / banks 1034 / VGS 88) | ⚠️ VGS format documented | ❌ | audio conversion |
| Cutscenes (35) / UI (76) | ⚠️ UI documented | ❌ (game uses own UI) | — |

## Identities

`CANON-CONVERSION.md` identities remain **OWNER-pending**
(CHAR001..072). No identity was invented or changed in Phase 4.
The SLUS named-`.gyu` string table (Phase-4 Job-1 report, item 5)
is recorded as evidence only; it is not a canon assignment.
