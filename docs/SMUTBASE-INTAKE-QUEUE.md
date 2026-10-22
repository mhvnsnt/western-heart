# SmutBase Intake Queue — living document

**Standing order (2026-10-22):** every SmutBase model landing in
`~/workspace/browser_downloads/` gets pulled into the repo and wired up.
Intake as they land — don't wait per-model. This file is the queue and the
manifest: what's landed, where it went, what's queued, and what each model
needs next.

**Method:** originals verified by hash; archives extracted with UNRAR 7.12 /
unzip; files ≤95MB committed in-repo via the Git Database API (blobs limit);
files above that staged durably in `~/workspace/fix2/smutbase-source/<id>/`
and registered here with hashes — the repo is the system of record, the
workspace staging is the byte store (same split as the TeraBox convention).

**Tripo auto-intake does NOT apply** to this batch: `tools/tripo-intake/` takes
Tripo Studio GLB pulls only. SmutBase models are Blender-native (several
already rigged: Rigify / IK) and go through the Blender rig lane + manual
character assignment. Nothing here sits in the tripo inbox.

## Landed this round (2026-10-22)

| # | Model | Roster id | Source archive | Size | Status | In-repo / staged path | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Lily (SultryRenders, G8F) | `lily-donor` | `sess-3959612345/…-0-SultryRendersLily_DuolingoMommy.rar` | 1.70 GB | ✅ extracted | staged: `~/workspace/fix2/lily/` (2.6 GB: `Lily Duolingo.blend` + `textures/`) | **DONOR — rig/skeleton donor for the female roster.** Genesis 8 Female, thick/curvy; user-approved body reference for female Tripo models (except Nightwolf). Donor for: female rigging, jiggle setup (breasts/belly/hips/thighs), body-part scaling, anatomy transfer. Joins Scarlett/Madeline as anatomy reference. |
| 2 | Cydney (MilkGuy_3D) | `cydney` | `sess-3959612345/…-1-Cydney_Sweeny.rar` | 296 MB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/cydney/` (`Cydney Sweeny.blend`, 541 MB) | **Size UP breasts and ass when rigging** (user note). Review nude at intake. |
| 3 | Rahkasa v1.1 | `rahkasa` | `sess-3045850964/…-4-RahkasaV1.1.blend` | 11.5 MB | ✅ in-repo | `roster/rahkasa/intake/RahkasaV1.1.blend` | **Oversoul spirit body** — user-picked four-armed female = a spirit body of a Spirit in the Eastern Mind canon (connects to Zen's Oversoul / souls Tou, Kai, Retsu, Gyou). |
| 4 | Mina Ashido (rigify) | `mina-ashido` | `sess-3045850964/…-9-Mina_Ashido_rigify_N3KT032.zip` | 18.2 MB | ✅ in-repo | `roster/mina-ashido/intake/` (13 files: rigify .blend + `Mina textures/`) | Rigify-rigged MHA character. Needs character assignment (new fighter or customization part donor?). |
| 5 | Pink Narwhal | *(stage)* | `sess-3045850964/…-8-ThePinkNarwhal_zVamCQj.blend` | 51.6 MB | ✅ staged | staged: `~/workspace/fix2/smutbase-source/pink-narwhal/`; registered in-repo at `game/assets/stages/pink-narwhal/README.md` | **ARENA ASSET, not a character — CONFIRMED 2026-10-22: this IS the club/DJ arena base (SmutBase b8ada591), a strip-club map.** Base for the club/djbooth/concert arena variants per `~/workspace/intake-stage/stages/CLUB-ARENA-PLAN.md`. 51.6MB exceeds the blobs-API single-request limit (HTTP 422; gzip no relief) — staged, not committed. |
| 6 | Fishnet material (RenCeifer) | *(material)* | `sess-3045850964/…-6-Fishnet_material_by_RenCeifer.blend` | 159 KB | ✅ in-repo | `game/assets/materials/fishnet/` | **MATERIAL, not a model.** Shared material for the customization suite / attire lane. |
| 7 | Parvati (Commission) | `parvati` | `sess-3045850964/…-2-ParvatiCommission.rar` | 326 MB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/parvati/` (`Parvati(Commission).blend`, 596 MB); registered in-repo at `roster/parvati/intake/README.md` | Was on the incoming list — landed. **Batch-2 re-check:** the three later re-downloads (`…-11-`, `…-12-`, `…-17-`) are byte-identical (sha256 `2601d935…`), extracted once. Blender 4.02, GZM widget rig, separate clothing meshes (Body Suit, Bra, Bottom, Belt, Choker, sheer robe/panties). Awaiting character assignment. |
| 8 | Vixen (Commission) | `vixen` | `sess-3045850964/…-3-Vixen_Commission.rar` | 412 MB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/vixen/` (`Vixen (Commission).blend`, 985 MB); registered in-repo at `roster/vixen/intake/README.md` | **🚩 MOVESET REBUILD REQUIRED — full moveset in TEKKEN notation; do NOT reuse her source game's (Injustice 2) input system.** Was on the incoming list — landed. **Batch-2 re-check:** the later re-download (`…-19-`) is byte-identical (sha256 `e6d2754b…`), extracted once. Blender 4.02, GZM widget rig, separate clothing meshes (Body Suit, Bra ×2, Boots, Gloves, Pantie, Stocking, Choker, BDSM harness). |
| 9 | Nyoka | `nyoka` | `sess-3045850964/…-1-Nyoka.rar` (downloaded twice, byte-identical — extracted once) | 341 MB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/nyoka/` (`Nyoka.blend`, 557 MB) | Was on the incoming list — landed. **Batch-2 verification (2026-10-22):** the .blend was byte-inspected (object/datablock names) — it genuinely contains **Nyoka** (XNALara port by gep5/de1tnn4: `Nyoka_Torso`, `Nyoka_Face`, `nyoka___xnalara_by_gep5_de1tnn4` texture paths). It is NOT Mirko. The Mirko model arrived separately via the `miruko_IK` zip (row 10) and is correctly filed under `miruko`. Awaiting character assignment. |
| 10 | Miruko (IK) | `miruko` | `sess-3045850964/…-7-miruko_IK_VWUk6qY.zip` | 7.6 MB | ✅ in-repo | `roster/miruko/intake/` (14 files: IK .blend + `textures/`) | Not on the queue list — downloaded anyway, intaken. MHA Miruko (Rumi Usagiyama), IK-rigged. **Batch-2 re-check:** the later re-download (`…-18-`) is byte-identical (sha256 `67106659…`). Filed as **Mirko**, not Nyoka. Awaiting character assignment. |
| 11 | Tsuyu Asui (IK v1.1) | `tsuyu-asui` | `sess-3045850964/…-10-Tsuyu_Asui_IK_V1.1.zip` | 34.2 MB | ✅ in-repo | `roster/tsuyu-asui/intake/` (11 files: IK .blend + .blend1 + `textures/`); per-model notes in `roster/tsuyu-asui/intake/INTAKE-NOTES.md` | Not on the queue list — downloaded anyway, intaken. MHA Tsuyu, IK-rigged. **Batch-2 anatomy pass (blend byte-inspected):** clothing is SEPARATE modeled geometry — `OBsuit`, `OBboots`, `OBgloves`, `OBBody_belt.dmx`, `OBBody_mask.dmx`, `OBBody_google.dmx`, `OBHair` are separate objects from the body (`OBtsuyu`) → undress = hide/remove those meshes. **User-flagged camel-toe: the mesh `OBBulge` covers that region — KEEP it in the anatomy pass** (do not flatten/remove). Note: an `OBPenis` mesh is also present in the file. Awaiting character assignment. |
| 12 | movie-maddness nm v2 | *(unassigned)* | `sess-3045850964/…-0-movie-maddness_nm_v2_gWOumfK.blend` | 929 MB | ✅ staged | staged: `~/workspace/fix2/smutbase-source/movie-maddness/` | Not on the queue list — downloaded anyway. 929 MB .blend, purpose unknown (name suggests a No Mercy movie/scene pack?). Needs a Blender look to identify. **Not intaken as a character.** |
| 13 | FluidPainter NSFW addon v1.0.1 | *(tool)* | `sess-3045850964/…-13-FluidPainterNSFWAddon_1_0_1_Blender_3.1_4.0_5.0.zip` | 4.4 MB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/tools/fluidpainter-nsfw/` (38 MB: Blender addon + asset libraries); evaluated in `docs/research/smutbase-batch2-tool-evaluations-2026-10-22.md` | **TOOL, not a model.** Fluid-painting Blender addon (Blender 3.1/4.0/5.0) — evaluated for the texture/anatomy pipeline: useful for the customization suite's NSFW fluid-decal detail layer, not a replacement for the skin/anatomy repaint work. |
| 14 | BuildABod Male v1.3 | *(tool)* | `sess-3045850964/…-14-BuildABod_Male_1_3.7z` | 3.0 MB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/tools/buildabod-male/` (`BuildABod_Male_1_3.blend`, 73 MB); evaluated in `docs/research/smutbase-batch2-tool-evaluations-2026-10-22.md` | **TOOL, not a model.** Male body-builder asset (DAZ G3M + morph set) — evaluated for the body-part scaling pipeline. |
| 15 | BuildABod Female v1.3 | *(tool)* | `sess-3045850964/…-15-BuildABod_Female_1_3.7z` | 4.4 MB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/tools/buildabod-female/` (`BuildABod_Female_1_3.blend`, 104 MB); evaluated in `docs/research/smutbase-batch2-tool-evaluations-2026-10-22.md` | **TOOL, not a model.** Female body-builder asset (DAZ G3F + full morph set: Breasts/Butt/Thighs/…) — evaluated for the body-part scaling pipeline; pairs with the Lily donor work for female body types. |
| 16 | naughty_rig v0.2.3 | *(tool)* | `sess-3045850964/…-16-naughty_rig_v0.2.3.zip` | 200 KB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/tools/naughty-rig/` (1.1 MB extracted); evaluated in `docs/research/smutbase-batch2-tool-evaluations-2026-10-22.md` | **TOOL, not a model — NEW in batch 2.** Rigify **feature set** (not a standalone addon; installs via Rigify → Feature Sets) by nekomata, Blender 3.3+. Spring-chain physics rigs (`phys_single_chain`, `phys_double_chain` — jiggle), shrinkwrap metarigs/rigs, spline-IK chains (tentacle/penetrator/tracer), geo-nodes assets. Evaluated for the anatomy/jiggle rigging pipeline: fits the Torch reference piece's full jiggle set (breasts/belly/hips/ass/thighs) on the Blender-authoring side; runtime bake stays in `tools/jiggle/`. |

**Deliberate call — third-party addons stay out of the repo tree:** the four
Blender tools above (FluidPainter, BuildABod ×2, naughty_rig) are third-party
code, so per the repo's owner law (no third-party code in the public repo)
they are **staged in the workspace, not committed** — extracted, hashed, and
registered here, ready for the Blender lane to install. Same treatment as the
oversize blends. Their pipeline evaluations live in
`docs/research/smutbase-batch2-tool-evaluations-2026-10-22.md`.

## Still incoming (not yet downloaded — intake on landing)

| Model | Note |
|---|---|
| SmutBase 22968842 | User flagged pronounced camel-toe — assess at intake whether clothing is removable (separate meshes) or painted-on. |
| SmutBase 91fca296 | — |
| SmutBase 0b8ceb43 | — |
| SmutBase c278fcf4 | — |

(Parvati, Vixen, Nyoka were on this list and have landed — moved to the table above.)

## Original-archive hashes (sha256)

Verification record for the originals in `~/workspace/browser_downloads/`.
Full hashes also in `~/workspace/fix2/smutbase-source/SHA256-ORIGINALS.txt`.

```
10cc107b…a121a8ed970  sess-3959612345/…-0-SultryRendersLily_DuolingoMommy.rar        (Lily)
c3bd91aa…bbee986b8e2d  sess-3959612345/…-1-Cydney_Sweeny.rar                         (Cydney)
cd55777b…5b721e7cceeb  sess-3045850964/…-0-movie-maddness_nm_v2_gWOumfK.blend        (movie-maddness)
6b3c5454…16342ec6cd1  sess-3045850964/…-1-Nyoka.rar  == …-5-Nyoka.rar (dupes)       (Nyoka ×2)
2601d935…0956db99fc47  sess-3045850964/…-2-ParvatiCommission.rar                     (Parvati)
e6d2754b…fdc41c2be5e5a  sess-3045850964/…-3-Vixen_Commission.rar                      (Vixen)
85610cee…05bc75b7ca33  sess-3045850964/…-4-RahkasaV1.1.blend                         (Rahkasa)
4f7a8cf6…dc720e9ffe4c0  sess-3045850964/…-6-Fishnet_material_by_RenCeifer.blend      (fishnet)
67106659…a76452da12426  sess-3045850964/…-7-miruko_IK_VWUk6qY.zip                     (Miruko)
419a2b6f…29c8daba4a4a  sess-3045850964/…-8-ThePinkNarwhal_zVamCQj.blend               (Pink Narwhal)
033b951e…ab1411234c28b  sess-3045850964/…-9-Mina_Ashido_rigify_N3KT032.zip            (Mina Ashido)
eb8495ee…5d02d57a41baa  sess-3045850964/…-10-Tsuyu_Asui_IK_V1.1.zip                  (Tsuyu Asui)
6d9f5a88…9f5051ca0c94de  sess-3045850964/…-13-FluidPainterNSFWAddon_1_0_1_Blender_3.1_4.0_5.0.zip
efe95e78…3d3f96dc898769  sess-3045850964/…-14-BuildABod_Male_1_3.7z                  (BuildABod male)
5db2905d…12993d517043e0  sess-3045850964/…-15-BuildABod_Female_1_3.7z                (BuildABod female)
```

## Merge record

| PR | Contents |
|---|---|
| #563 | `docs/SMUTBASE-INTAKE-QUEUE.md` — the queue itself (+ WORKLOG.md entry) |
| #564 | `roster/rahkasa/intake/`, `roster/mina-ashido/intake/`, `roster/miruko/intake/`, `roster/tsuyu-asui/intake/` — small character sources |
| #565 (planned) | `game/assets/stages/pink-narwhal/README.md` (registration), `game/assets/materials/fishnet/` — arena registration + shared material; queue-doc corrections |
| batch-2 PR A | `docs/SMUTBASE-INTAKE-QUEUE.md` — batch-2 update: naughty_rig intake (#16), Tsuyu anatomy notes, Vixen moveset-rebuild flag, Parvati/Vixen/Miruko dupe hashes, Nyoka-vs-Mirko byte-verification note, tool rows point at the evaluation doc |
| batch-2 PR B | `roster/parvati/intake/README.md`, `roster/vixen/intake/README.md` (staged-blend registrations; Vixen carries the moveset-rebuild flag), `roster/tsuyu-asui/intake/INTAKE-NOTES.md` (verified separate-geometry + camel-toe notes) |
| batch-2 PR C | `docs/research/smutbase-batch2-tool-evaluations-2026-10-22.md` — pipeline evaluations: FluidPainter (texture/anatomy), BuildABod ×2 (body-part scaling), naughty_rig (anatomy/jiggle rigging) |

All merged via `git_merge.py` (Git Database API 3-way merge), CI green, no deletions.

## Next steps for the rig/character lanes

1. **Lily donor work** — extract her rig/skeleton as the female donor; jiggle reference (breasts/belly/hips/thighs). Blender required (not installed on this VM as of 2026-10-22).
2. **Cydney** — size up breasts/ass at rig time, per user note.
3. **Rahkasa** — wire as the Oversoul spirit-body character (Eastern Mind canon).
4. **Vixen — 🚩 MOVESET REBUILD (flagged 2026-10-22, batch 2).** Build her full
   moveset in **TEKKEN notation**; do NOT reuse her source game's (Injustice 2)
   input system. Flag is registered at `roster/vixen/intake/README.md` and in
   her queue row. No moveset JSON exists for her yet (`game/assets/movesets/`
   has 101 files, none for Vixen).
5. **Pink Narwhal** — arena lane: CONFIRMED as the club/DJ arena base (SmutBase b8ada591, strip-club map). Build the club/djbooth/concert variants per `~/workspace/intake-stage/stages/CLUB-ARENA-PLAN.md`; source bytes staged at `~/workspace/fix2/smutbase-source/pink-narwhal/`.
6. **movie-maddness** — identify the .blend's contents before any intake decision.
7. **Character assignment** — Mina Ashido, Miruko, Tsuyu Asui, Parvati, Nyoka need fighter slots or explicit customization-donor designation.
8. **Tool lane (batch-2 evaluations in `docs/research/smutbase-batch2-tool-evaluations-2026-10-22.md`):**
   - naughty_rig → Blender rig lane: install as a Rigify feature set, use its
     phys spring-chains for the Torch reference piece's jiggle set
     (breasts/belly/hips/ass/thighs); needs Blender ≥3.3 + Rigify on the rig VM.
   - BuildABod Female → body-part scaling lane: parametric reference for the
     Lily body-type work (breast/butt/thigh morph dials).
   - FluidPainter NSFW → customization suite: NSFW fluid-decal detail layer for
     texture/anatomy finishing (not the core anatomy repaint).
