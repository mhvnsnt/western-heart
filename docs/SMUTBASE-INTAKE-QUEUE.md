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
| 5 | Pink Narwhal | *(stage)* | `sess-3045850964/…-8-ThePinkNarwhal_zVamCQj.blend` | 51.6 MB | ✅ in-repo | `game/assets/stages/pink-narwhal/` | **ARENA ASSET, not a character.** Possible link to the club/DJ arena base plan (`~/workspace/intake-stage/stages/CLUB-ARENA-PLAN.md`, SmutBase model b8ada591) — **unverified**: needs a Blender look to confirm whether this file IS that base. Flagged for the arena lane. |
| 6 | Fishnet material (RenCeifer) | *(material)* | `sess-3045850964/…-6-Fishnet_material_by_RenCeifer.blend` | 159 KB | ✅ in-repo | `game/assets/materials/fishnet/` | **MATERIAL, not a model.** Shared material for the customization suite / attire lane. |
| 7 | Parvati (Commission) | `parvati` | `sess-3045850964/…-2-ParvatiCommission.rar` | 326 MB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/parvati/` (`Parvati(Commission).blend`, 596 MB) | Was on the incoming list — landed. Awaiting character assignment. |
| 8 | Vixen (Commission) | `vixen` | `sess-3045850964/…-3-Vixen_Commission.rar` | 412 MB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/vixen/` (`Vixen (Commission).blend`, 985 MB) | **Needs a full moveset built with TEKKEN inputs** (not her source game's input system). Was on the incoming list — landed. |
| 9 | Nyoka | `nyoka` | `sess-3045850964/…-1-Nyoka.rar` (downloaded twice, byte-identical — extracted once) | 341 MB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/nyoka/` (`Nyoka.blend`, 557 MB) | Was on the incoming list — landed. Awaiting character assignment. |
| 10 | Miruko (IK) | `miruko` | `sess-3045850964/…-7-miruko_IK_VWUk6qY.zip` | 7.6 MB | ✅ in-repo | `roster/miruko/intake/` (14 files: IK .blend + `textures/`) | Not on the queue list — downloaded anyway, intaken. MHA Miruko, IK-rigged. Awaiting character assignment. |
| 11 | Tsuyu Asui (IK v1.1) | `tsuyu-asui` | `sess-3045850964/…-10-Tsuyu_Asui_IK_V1.1.zip` | 34.2 MB | ✅ in-repo | `roster/tsuyu-asui/intake/` (11 files: IK .blend + .blend1 + `textures/`) | Not on the queue list — downloaded anyway, intaken. MHA Tsuyu, IK-rigged. Awaiting character assignment. |
| 12 | movie-maddness nm v2 | *(unassigned)* | `sess-3045850964/…-0-movie-maddness_nm_v2_gWOumfK.blend` | 929 MB | ✅ staged | staged: `~/workspace/fix2/smutbase-source/movie-maddness/` | Not on the queue list — downloaded anyway. 929 MB .blend, purpose unknown (name suggests a No Mercy movie/scene pack?). Needs a Blender look to identify. **Not intaken as a character.** |
| 13 | FluidPainter NSFW addon v1.0.1 | *(tool)* | `sess-3045850964/…-13-FluidPainterNSFWAddon_1_0_1_Blender_3.1_4.0_5.0.zip` | 4.4 MB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/tools/fluidpainter-nsfw/` (38 MB: Blender addon + asset libraries) | **TOOL, not a model.** Fluid-painting Blender addon (Blender 3.1/4.0/5.0) — relevant to the anatomy/fluid detail work on the female roster. |
| 14 | BuildABod Male v1.3 | *(tool)* | `sess-3045850964/…-14-BuildABod_Male_1_3.7z` | 3.0 MB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/tools/buildabod-male/` (`BuildABod_Male_1_3.blend`, 73 MB) | **TOOL, not a model.** Male body-builder asset for Blender — base bodies for the male roster / customization suite. |
| 15 | BuildABod Female v1.3 | *(tool)* | `sess-3045850964/…-15-BuildABod_Female_1_3.7z` | 4.4 MB | ✅ extracted | staged: `~/workspace/fix2/smutbase-source/tools/buildabod-female/` (`BuildABod_Female_1_3.blend`, 104 MB) | **TOOL, not a model.** Female body-builder asset — pairs with the Lily donor work for female body types. |

**Deliberate call — third-party addons stay out of the repo tree:** the three
Blender addons above (FluidPainter, BuildABod ×2) are third-party code, so
per the repo's owner law (no third-party code in the public repo) they are
**staged in the workspace, not committed** — extracted, hashed, and
registered here, ready for the Blender lane to install. Same treatment as the
oversize blends.

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
| *(this doc)* | `docs/SMUTBASE-INTAKE-QUEUE.md` — the queue itself |
| *(small character assets)* | `roster/rahkasa/intake/`, `roster/mina-ashido/intake/`, `roster/miruko/intake/`, `roster/tsuyu-asui/intake/` |
| *(arena + material)* | `game/assets/stages/pink-narwhal/`, `game/assets/materials/fishnet/` |

All merged via `git_merge.py` (Git Database API 3-way merge), CI green, no deletions.

## Next steps for the rig/character lanes

1. **Lily donor work** — extract her rig/skeleton as the female donor; jiggle reference (breasts/belly/hips/thighs). Blender required (not installed on this VM as of 2026-10-22).
2. **Cydney** — size up breasts/ass at rig time, per user note.
3. **Rahkasa** — wire as the Oversoul spirit-body character (Eastern Mind canon).
4. **Vixen** — build Tekken-notation moveset; do NOT reuse her source game's input system.
5. **Pink Narwhal** — arena lane: confirm whether this is the club/DJ base (b8ada591) from the CLUB-ARENA-PLAN.
6. **movie-maddness** — identify the .blend's contents before any intake decision.
7. **Character assignment** — Mina Ashido, Miruko, Tsuyu Asui, Parvati, Nyoka need fighter slots or explicit customization-donor designation.
