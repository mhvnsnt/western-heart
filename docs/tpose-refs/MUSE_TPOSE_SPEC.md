# T-Pose Reference Sheet Standard (for Muse)

**Owner:** mhvnsnt. **Assigned to:** Muse (batch). **Samples by:** Producerbot, 2026-10-14.

The owner builds new models in **Tripo 3D** from a single 1:1 T-pose image of a character on white.
That's how Pantera P1 was made (Leomon refs plus King in T-pose), and that model is in the game now.
Every character and attire needs one of these sheets so it can be rescanned and co-authored into the
Western Heart universe (see `docs/pipeline/MODEL_COAUTHOR_PIPELINE.md`).

## "This is exactly the one"
`pantera/p1_front.png` is the reference standard. Match it.

| Sample | Front | Side |
|---|---|---|
| Pantera P1 (in-game `game/assets/models/pantera.glb`) | `pantera/p1_front.png` | `pantera/p1_side.png` |
| Pantera Leomon attire (`lab/game/assets/pantera_leoman.glb`) | `pantera/leomon_front.png` | `pantera/leomon_side.png` |
| Demonio attire 1 (`game/assets/models/demonio.glb`) | `demonio/a1_front.png` | `demonio/a1_side.png` |
| Create-a-Fighter base (`customization/create-fighter/assets/Soldier.glb`) | `create-fighter-base/soldier_front.png` | `create-fighter-base/soldier_side.png` |

Checksums: `SHA256SUMS` (run `sha256sum -c SHA256SUMS` in this folder).

## The standard
| Item | Rule |
|---|---|
| Canvas | **2048×2048 PNG**, 1:1 square, RGB, no alpha |
| Background | **Pure white, #FFFFFF** everywhere (no gradient, floor, or ground shadow) |
| Camera | **Orthographic**, front view, dead level at the body's center. Optional side view: the character's left side, camera on +X |
| Framing | Full body centered both ways. Ortho scale = 1.12 × max(width, height), which leaves about 5% (~109 px) clear margin on the longest axis. **Fingertips, toes, tail, hair, and cape fully inside the frame** |
| Pose | **T-pose**: upper arm and forearm straight out horizontally, palms down, fingers straight, legs straight and slightly apart (natural hip width), head forward, neutral face. If the source rest pose isn't a T-pose, pose it through the skeleton; never edit the mesh |
| Lighting | Even, flat, unlit (Blender Workbench `FLAT` + `TEXTURE` color, shadows off, cavity off, view transform `Standard`). No rim, AO, or specular |
| Textures | All textures must resolve. **Magenta, untextured grey, or white-default parts = FAIL** |
| Naming | `docs/tpose-refs/<character>/<attire>_front.png` (+ `_side.png`). Lowercase, `-` inside names (`king-tyrant/p1_front.png`) |
| Hash | Add every PNG to `SHA256SUMS` |

## How to render (headless, one command)
```
blender -b --factory-startup -P docs/tpose-refs/_tools/tpose_render.py -- <model.glb|.fbx> /tmp/out/<name> side [flip]
```
- The script imports the model, clears animation, deletes stray primitives (Icosphere, Cube), rotates the
  upper-arm and forearm bones horizontal via the skeleton, frames from the posed mesh bounds, and writes
  `<name>_front.png`, `<name>_side.png`, and `<name>_report.json` (the bones it posed and the bounds).
- `flip`: use it when the model faces +Y and you get its back (the Quaternius `Soldier.glb` needed it).
- Supports Mixamo-style (`LeftArm/LeftForeArm`) and Tekken 8 (`L_UpperArm/L_LowerArm`) bone names. For other
  rigs, extend the `re.fullmatch` in the script.
- Blender 4.2 is on the box at `/workspace/oss/blender/blender-4.2.3-linux-x64/blender`.

## Check steps (all must pass before marking DONE)
1. **Open the PNG and look at it.** The model is intact (no floating or exploded parts), it faces the camera, and it isn't back-facing.
2. Arms are horizontal and hands are open, palms down.
3. Margin check: no non-white pixel within 40 px of any edge:
   ```
   python3 -c "from PIL import Image;import numpy as n,sys;a=n.asarray(Image.open(sys.argv[1]).convert('RGB'));y,x=n.where(a.min(2)<245);print(x.min(),2047-x.max(),y.min(),2047-y.max())" file.png
   ```
   All four numbers must be ≥ 40.
4. The background is exactly 255,255,255.
5. No magenta or untextured parts.
6. Add the file to `SHA256SUMS` and set the row in the table below to `DONE`.

## Do / Don't
- **DO** match `pantera/p1_front.png` exactly: same scale logic, white, flat, centered.
- **DO** skip a broken rig and write down why (status `BLOCKED-<reason>`). Don't hand-fix the mesh.
- **DON'T** use perspective, drop shadows, a ground plane, a transparent background, JPEG, or crop the hands.
- **DON'T** render A-pose or idle-pose models as-is. Pose them first; if there's no skeleton, mark `BLOCKED-no-rig`.
- **DON'T** re-render the owner's two Pantera source Kings (T7 King P1 blue/purple/yellow; black tights with KING across the front). He already has them.

## Checklist (every character and attire)
Status: `DONE`, `TODO` (model exists, render it), `NEED-MODEL` (no model in repo yet), or `BLOCKED-<why>`.

| Character (CANON) | Attire | Model source | Status |
|---|---|---|---|
| PANTERA | P1 | `game/assets/models/pantera.glb` | DONE (sample) |
| PANTERA | Leomon | `lab/game/assets/pantera_leoman.glb` | DONE (sample) |
| PANTERA | P2 (recolor) | `roster/pantera/attires/p2/` | TODO |
| PANTERA | Cyborg-88 | `roster/pantera/attires/cyborg/` (design doc only) | NEED-MODEL |
| PANTERA | rigged/tail build | `roster/pantera/pantera_rigged.glb` | BLOCKED-glTF importer assertion in Blender 4.2 (re-export) |
| DEMONIO | A1 | `game/assets/models/demonio.glb` | DONE (sample) |
| PHANTOM | P1 | (Yoshimitsu donor) | NEED-MODEL |
| DIABLO | P1 | (Heihachi donor) | NEED-MODEL |
| SKULL | P1 (+ alts pending review) | (Bryan donor) | NEED-MODEL |
| SAM-∪R-Λ1 | P1 | (Gun Jack donor) | NEED-MODEL |
| SAKU RA | P1 | (Xiaoyu donor; uses stand-in King in-game) | NEED-MODEL |
| ZUI | P1 | — | NEED-MODEL |
| KINPO | P1 | — | NEED-MODEL |
| WATERFALL | P1 | — | NEED-MODEL |
| KING TYRANT | P1 | — | NEED-MODEL |
| BURGER | P1 (cursed) / Slim Bob (uncursed) | (Bob Richards base) | NEED-MODEL |
| AWA POP | P1 | — | NEED-MODEL |
| SCIMITAR | P1 | — | NEED-MODEL |
| PURPLE RAIN | P1 | — | NEED-MODEL |
| NIGHTWOLF | P1 | — | NEED-MODEL |
| MICHIKO | P1 | — | NEED-MODEL |
| STAR | P1 | — | NEED-MODEL |
| TORCH | P1 | — | NEED-MODEL |
| DIO | P1 | — | NEED-MODEL |
| CYBORG X | P1 | — | NEED-MODEL |
| BRUNO | P1 | — | NEED-MODEL |
| N3GΔTIV0 | P1 | — | NEED-MODEL |
| SUN RĀ (boss) | P1 | — | NEED-MODEL |
| Create-a-Fighter base | Soldier | `customization/create-fighter/assets/Soldier.glb` | DONE (sample) |

### Donor and teardown models (King and others)
| Model | Source | Status |
|---|---|---|
| T7 King P1 (blue/purple/yellow) | `teardown/tekken7/king/*.fbx` | SKIP: owner's Pantera source |
| King, black tights "KING" | — | SKIP: owner's Pantera source |
| T3 King | `lab/game/assets/t3_king.glb` | BLOCKED-rig: 20 rigid parts come apart, no texture |
| T8 King S2 / 1P parts | Release `king-variants-2026-10-13` (`Tekken.8.-.King.S2.rar`, `...TK8.Base.7z`) | BLOCKED: the RAR is truncated (9 textures fail, magenta), T8 layered shaders leave parts white, and the rest pose has hands on hips that the arm-chain pose doesn't fix. Needs a full texture set plus a T8 material rebuild |
| T8 Armor King Battle Cloth | Release `Tekken_8_-_Armor_King__Battle_Cloth_.rar` | BLOCKED: same (truncated RAR, untextured) |
| T8 King "Tekken 3" costume | Release `Tekken8_King_Tekken3.7z` (XPS `.mesh.ascii`) | BLOCKED-needs XPS/XNALara importer for Blender |
| Beast King (Tekken Revolution) | Release `beast-king-tekkenrevolution.zip` (XPS) | BLOCKED-needs XPS importer |
| WWF No Mercy wrestlers (Rock, Austin, HHH, ...) | `teardown/wwf-no-mercy/re-docs/assets/3d Assets/characters/` | BLOCKED-no-rig (static A-pose meshes) |
| T6 / TTT2 characters | `teardown/tekken6`, `teardown/tekken-tag-tournament-2` | NEED-MODEL (still encrypted, not extracted) |
| Muse-downloaded models | wherever Muse lands them | TODO: add a row per model |
