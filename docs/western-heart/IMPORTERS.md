# Western Heart Lab: importer status

All importers target **WH-Canonical-22** (`lab/skeleton/`) and the shared `MoveTable` interpreter where move data exists. Each needs: an importer, a round-trip test, a rig-check pass/fail, and a proof sheet (idle/walk/strike) in its own PR.

| Game | Source in repo | Status | Notes / blocker |
|---|---|---|---|
| Tekken 3 (PS1) | teardown/tekken3 (KMD, stance OBJ, movesets) | **WORKING** | `t3_to_gltf.py`; King only (only King has a decoded stance). Rig check PASS. 7 move tables in `MoveTable`. Seam-vertex imports (~43% of faces) are undecoded and there are no TIM textures |
| Owner originals (Tripo GLB) | Drive → `lab/source_assets/original` | **WORKING** | `autorig.py`; Pantera Leo-Man rig check PASS (0.37% of tris >2× stretch). Bannon mask = attachment |
| Tekken 6 (PSP) | Release `tekken6-psp-v1` (ISO); teardown/tekken6 has only videos/frames + a decrypted ELF | **BLOCKED** | No model format is decoded in-repo (cipher hunt in progress per teardown docs). ISO download needs about 1 GB of the box's ~2 GB free disk |
| Tekken Tag Tournament 2 | Release `ttt2-7z-v1` (split 7z); teardown/tekken-tag-tournament-2/extracted-small | **BLOCKED** | Full archive is tens of GB (doesn't fit the disk); the small extracts are unidentified blobs with no model parser |
| Urban Reign (PS2) | teardown/urban-reign (.p3d/.pbd/.ppk, 970 MB) | **BLOCKED (next candidate)** | Geometry is in-repo, but the bone translation is still WIP per its teardown; no parser in tools yet |
| WWF No Mercy (N64) | teardown/wwf-no-mercy (3,587 OBJ, 13 GLB) | **PARTIAL** | OBJ/GLB parts are unskinned, with no skeleton; could rigid-bind per part like T3 once the part→bone table is known |
| WWE WrestleMania XIX (GC) | teardown/wmxix (166 OBJ) | **PARTIAL** | OBJ dumps only, no rig data. Wrestlers now belong to the wrestling-game repo (Oct 13 directive) |
| Virtua Fighter 5 (PS3) | Release `vf5-ps3-v1`; teardown docs + 2 × 7z | **BLOCKED** | No model parser |
| Soulcalibur II (PS2) | Release `soulcalibur2-ps2-v1`; docs + 1 py | **BLOCKED** | No model parser |
| Dead or Alive 4 (X360) | Release `doa4-iso-v1` | **BLOCKED** | Docs only |
| Street Fighter EX2 Plus (PS1) | Release `sf-ex2-plus-v1` | **BLOCKED** | Docs only; PS1 like T3, so a TMD-style importer is the likely route |
| Eastern Mind | Release `eastern-mind-v1` | **BLOCKED** | World/art source, not fighters. Needs a stage importer |
| Def Jam: FFNY | wrestling-game repo teardown (371 MB) | **BLOCKED** | Belongs to wrestling-game now; no parser |

Order agreed with the owner: the Tekken 3 slice first (done), then Tekken 6 and TTT2. Both are BLOCKED on format RE and disk, so the first workable next step is Urban Reign or No Mercy rigid-bind once disk is freed.
