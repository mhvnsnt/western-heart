# Urban Reign Character Renders — STATUS (2026-10-19)

The 72 Urban Reign fighters **cannot be rendered yet** — not because the teardown is missing (it is in the repo at `teardown/urban-reign/`, fully inventoried), but because the character-model decode is still open.

## Why no renders
The extracted OBJs in `teardown/urban-reign/models/char001–char072/` are **bone-local vertex soup, not meshes**: positions/normals/UVs only, zero triangle faces, and every chunk sits in an unknown bone's local frame. Bone bind matrices were never found (`tools/ur_bone_hunt.py` is a documented negative result). The repo's own `TEARDOWN.md` lists "Character model decode" under "What's Blocked."

Rendering the raw verts would produce scattered garbage — a fake render. So none were made.

## What unblocks the renders
1. Binary RE: find triangle face indices + bone bind matrices in the char PPKs (`teardown/urban-reign/ppks/chars/`). Lead: `motion/*.gyu` files (parse for skeleton bone count/names).
2. Then: render all 72 locked-standard fronts here at `docs/tpose-refs/urban-reign/<charNNN>/p1_front.png`.

## What IS torn down (verified 2026-10-19)
- 72 fighter PPKs + extracted vertex data (242,569 verts) + ROSTER.json
- 7 stage PPKs, 46 motion-pack PPKs, 100 mission PPKs + 256 mission definitions
- .gyu motion files, 1,000 audio files, VGS batch + inventory, 35 cutscene PPKs, full UI (character-select/menus/screens/title-screens), AFS maps
- 4.14GB ISO safe on GitHub Release `urban-reign-iso-v1`

Full detail: `docs/urban-reign/URBAN-REIGN-RENDER-STATUS-2026-10-19.md`
