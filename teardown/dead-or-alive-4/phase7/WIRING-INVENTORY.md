# DOA4 Wiring Inventory — Phase 7 (2026-10-21)

Status key: **STAGED** = game-format asset exists in `teardown/`
(not in `game/` — no roster registration this phase; canon is an
owner decision, see `CANON-QUESTIONS.md`). **PARTIAL** = exists with
documented gaps. **NONE** = does not exist yet.

Per-package detail lives in the phase-6 inventories
(`phase6/inventory-chrone.csv`, `phase6/inventory-chrtwo.csv`,
`phase6/inventory-chrthree.csv` — 148 rows) and the phase-6
manifest (`models/phase6-manifest.json` — per-GLB sha256 + size +
release asset). This doc is the per-container roll-up.

| Container | Packages | Skinned GLB | Textures | Clips | Notes |
|---|---|---|---|---|---|
| chrone.afs | 30/30 | STAGED — release `doa4-phase6-models-20261021` (split zips), manifest in git | PARTIAL — pkg00 only: 42 TX2D decoded to PNG (`textures/chrone-pkg00/`), 3 evidence-only material assignments in `models/chrone-pkg00-textured.glb`; other packages untextured (binding gap, `phase7/BINDING-HUNT.md`) | NONE | pkg00 additionally in git as skinned + textured GLB with viewed proof renders |
| chrtwo.afs | 68/68 | STAGED — same release + manifest | NONE decoded (TX2D format solved phase 6; per-package decode not run) | NONE | 17 oversized packages rebuilt with wide windows in phase 6 |
| chrthree.afs | 50/50 full + 25 TX2D-only sub-packages | STAGED — same release + manifest (50 full) | NONE decoded; the 25 sub-packages are texture bundles (XPR2 + TX2D only, verified again phase 7) | NONE | G2 closed by accounting in phase 6 (75/75) |
| mot.afs | 11 packages (old triangulated set) | PARTIAL — mot packages were assembled as model packages in phases 3–6, not as motion data | NONE | NONE — no clip-format parse exists; mot head is plaintext floats (phase 7), so clips are gated on format work, not on any cipher | see `PHASE7-FINDINGS-2026-10-21.md` §3 |
| anm.afs | 1 file, region-mapped phase 7 | n/a | n/a | NONE — float payload regions are plaintext; the head/index region (0x000000–0x06B000) is undecoded, so clip boundaries/bone mapping are unknown | region map in phase-7 findings §2 |
| stg.afs | 27 packages parsed phase 3 (stg pkg00 graph in git) | PARTIAL — no phase-6-style batch for stages | NONE | n/a (stages) | stage wiring is out of scope for the fighter roster question |

Other staged assets in `teardown/dead-or-alive-4/`:

- 165 triangulated pool GLBs (`models/triangulated/`, PR #386
  import-repaired) — superseded by the phase-6 skinned batch for
  chr*, kept as the decode-provenance record.
- Assembly graphs for all 148 chr packages (`assembly-graphs/`).
- Movesets: `movesets/bass-armstrong/BASS-MOVELIST.md` + the 6
  core fighter move lists noted in
  `DOA4-CONTINUATION-2026-10-19.md` (16–26 moves each; FULL MOVESET
  LAW wants 100+/fighter — flagged, not satisfied).
- Fighter identity of packages: **UNRESOLVED.** Packages are known
  only as chrone/chrtwo/chrthree indices. There is no TOC with
  filenames to recover (§1.2 of the phase-7 findings — no TOC
  exists), so package→character identification must come from
  content (model appearance/moveset matching), not from metadata.
  This is an input to the owner's canon decision.

Wiring blockers, in dependency order:

1. Package→character identification (content-based pass, not yet run).
2. Material→texture binding beyond pkg00's 3 proven assignments
   (`phase7/BINDING-HUNT.md` — hunt run, not found in XEX strings,
   package records, or sub-package directories).
3. Animation clips (anm head/index format + mot/anm stream format).
4. Owner canon decision (`CANON-QUESTIONS.md`) — gates any move
   from `teardown/` staging into `game/`.
