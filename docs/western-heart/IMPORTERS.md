# Western Heart Lab: importer status

> **Owner law (Oct 23, 2026, 2:19 PM CT):** Western Heart's data (moves, animations, frame data, menus, character select) comes from Tekken 5, 6, 7, 8 and TTT2. Tekken 3 is only a last-resort fallback, and every T3 use is logged with its reason. **Primary importers: T5, T6, T7, T8, TTT2. T3: fallback-only.**
>
> **Owner law (Oct 23, 2026, 2:21 PM CT):** no hand-made menus; menus/char select/customization (incl. `packages/creation-suite`) are built from teardowns and every UI change cites its source.

All importers target **WH-Canonical-22** (`lab/skeleton/`) and the shared `MoveTable` interpreter where move data exists. Each needs: an importer, a round-trip test, a rig-check pass/fail, and a proof sheet (idle/walk/strike) in its own PR.

| Game | Source in repo | Status | Notes / blocker |
|---|---|---|---|
| Tekken 5 | not yet located in repo | **PRIMARY — TODO** | Importer not started; locate teardown source |
| Tekken 6 (PSP) | Release `tekken6-psp-v1` (ISO); teardown/tekken6 has only videos/frames + a decrypted ELF | **PRIMARY — BLOCKED** | No model format is decoded in-repo (cipher hunt in progress per teardown docs). ISO download needs about 1 GB of the box's ~2 GB free disk |
| Tekken 7 | not yet located in repo | **PRIMARY — TODO** | Importer not started; locate teardown source |
| Tekken 8 | teardown docs (e.g. Voiceclip stub) | **PRIMARY — TODO** | Importer not started |
| Tekken Tag Tournament 2 | Release `ttt2-7z-v1` (split 7z); teardown/tekken-tag-tournament-2/extracted-small | **PRIMARY — BLOCKED** | Full archive is tens of GB (doesn't fit the disk); the small extracts are unidentified blobs with no model parser |
| Owner originals (Tripo GLB) | Drive → `lab/source_assets/original` | **WORKING** | `autorig.py`; Pantera Leo-Man rig check PASS (0.37% of tris >2× stretch). Bannon mask = attachment |
| Tekken 3 (PS1) | teardown/tekken3 (KMD, stance OBJ, movesets) | **WORKING — FALLBACK ONLY** | `t3_to_gltf.py`; King only (only King has a decoded stance). Rig check PASS. 7 move tables in `MoveTable`. Seam-vertex imports (~43% of faces) are undecoded and there are no TIM textures |
| Urban Reign (PS2) | teardown/urban-reign (.p3d/.pbd/.ppk, 970 MB) | **BLOCKED (next candidate)** | Geometry is in-repo, but the bone translation is still WIP per its teardown; no parser in tools yet |
| WWF No Mercy (N64) | teardown/wwf-no-mercy (3,587 OBJ, 13 GLB) | **PARTIAL** | OBJ/GLB parts are unskinned, with no skeleton; could rigid-bind per part like T3 once the part→bone table is known |
| WWE WrestleMania XIX (GC) | teardown/wmxix (166 OBJ) | **PARTIAL** | OBJ dumps only, no rig data. Wrestlers now belong to the wrestling-game repo (Oct 13 directive) |
| Virtua Fighter 5 (PS3) | Release `vf5-ps3-v1`; teardown docs + 2 × 7z | **BLOCKED** | No model parser |
| Soulcalibur II (PS2) | Release `soulcalibur2-ps2-v1`; docs + 1 py | **BLOCKED** | No model parser |
| Dead or Alive 4 (X360) | Release `doa4-iso-v1` | **BLOCKED** | Docs only |
| Street Fighter EX2 Plus (PS1) | Release `sf-ex2-plus-v1` | **BLOCKED** | Docs only; PS1 like T3, so a TMD-style importer is the likely route |
| Eastern Mind | Release `eastern-mind-v1` | **BLOCKED** | World/art source, not fighters. Needs a stage importer |
| Def Jam: FFNY | wrestling-game repo teardown (371 MB) | **BLOCKED** | Belongs to wrestling-game now; no parser |

Historical order: the Tekken 3 slice was done first. **Superseded Oct 23, 2026, 2:19 PM CT:** T5/T6/T7/T8/TTT2 are the primary importers; T3 is fallback-only. Both are BLOCKED on format RE and disk, so the first workable next step is Urban Reign or No Mercy rigid-bind once disk is freed.
