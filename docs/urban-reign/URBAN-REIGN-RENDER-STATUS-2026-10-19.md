# Urban Reign Character Render Lane — WORKLOG (2026-10-19)

Owner order (2026-10-19 ~02:47 CDT): "Urban reign should be fully 100% tore down in the repo files with all moves, models, arenas and everything."

## What I did
Worked from mhvnsnt/western-heart main via the GitHub API (the shared local clone hangs on 54k files — never used it).

1. Listed `teardown/urban-reign/` on main: models/, animations/motion-packs/, motion/ (.gyu), missions/, ppks/chars/, ppks/stages/, audio/, cutscenes/, ui/, vgs/, sound/, afs-map/, plus format docs (PPK-FORMAT.md, PPK-GEOMETRY.md, VGS-FORMAT.md, TEARDOWN.md).
2. Listed `models/`: ROSTER.json + **72** char dirs (char001–char072, not 49 — the repo has more than the task brief said).
3. Downloaded char001/char002/char036/char072 OBJ parts + vmanifests and inspected them byte-level.
4. Read PPK-GEOMETRY.md, TEARDOWN.md, and tools/ur_bone_hunt.py (the repo's own RE findings).

## The honest finding: 0 of 72 renderable with current decode state

The extracted OBJs are **bone-local vertex soup, not meshes**:
- `charNNN_pos_infl0.obj` — `v` lines ONLY (e.g. char001: 3576 verts, zero faces). No triangle connectivity anywhere.
- `charNNN_normals.obj` — blended normals stored as `v` lines. `charNNN_uv.obj` — `vt` lines.
- Positions are **bone-local** (per the file headers: "bone-local, 3576 verts"). There is no world transform.
- Bone matrices were **never found**: `tools/ur_bone_hunt.py` (committed to the repo, 2026-10-14) is a documented NEGATIVE result — no bone-name strings in any of the 72 PPKs, only 3–4 identity 4x4s in the whole file, and the two-bone translation-constraint test REFUTED the pure-translation model.
- The repo's own TEARDOWN.md "What's Blocked" section lists **"Character model decode"** as open.

Rendering a point cloud of bone-local verts would produce scattered garbage in 72 wrong coordinate frames — that is a fake render, so I did not do it (OWN-EYES law + no fake renders). The locked-standard front views become possible only when the RE lane finds: (a) triangle face indices, (b) bone bind matrices. The `.gyu` motion files in `motion/` are the documented next lead (parse for skeleton bone count/names).

## Full teardown inventory (verified on main 2026-10-19)

- `models/` — 72 fighters: ROSTER.json + char001–char072 (OBJ parts + _vmanifest.json each). 242,569 pos verts / 192,371 normal verts total. Largest: char061 (4,586 verts). Smallest: char002 (102 verts — likely a prop/weapon, not a fighter).
- `ppks/chars/` — 72 original char PPKs (char001.ppk … char072.ppk).
- `ppks/stages/` — 7 stage PPKs (stage003, 004, 020, 028, 029, 030, 031). Stage geometry decode still open (PPK-FORMAT.md).
- `animations/motion-packs/` — 46 motion PPKs (main.ppk, main_in.ppk, mainx.ppk, pmot001–…).
- `motion/` — 6 files: general_30frame.gyu, general_normal.gyu, general_weapon.gyu, gyu_debug.gyu, gyuindex.bin, gyuindex_ppk.bin. **This is the skeleton lead.**
- `missions/definitions/` — 256 mission .bin files (mission000–255). `missions/ppks/` — 100 mission PPKs.
- `audio/` — 1,000 files (sound_ok_se_*.p3d/.pbd). `vgs/` — VGS-BATCH-20261013.md + VGS-INVENTORY.csv + decoded/ + raw/. `cutscenes/` — 35 demo_data PPKs. `ui/` — character-select/, menus/, screens/, title-screens/ + README. `sound/ok_adx/`. `afs-map/` — dvd000/dvd001 AFS maps.
- ISO: `Urban Reign (USA).iso` 4.14GB safe on GitHub Release `urban-reign-iso-v1` (8×500MB parts).

## Delivered in this PR
- `docs/tpose-refs/urban-reign/README.md` — this status, so anyone looking for the renders finds the blockage + the exact RE unblockers instead of silence.
- This WORKLOG.

## Open follow-ups (not this lane)
1. Binary RE lane: find face indices + bone bind matrices in the char PPKs (start with motion/*.gyu for the skeleton).
2. Texture lane (a4f50eeb, running): extracting real textures from PPK/VGS — coordinate so textures land on the same future meshes.
3. Once (1) lands: render all 72 locked-standard fronts into docs/tpose-refs/urban-reign/<charNNN>/p1_front.png.
