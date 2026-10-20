# Stream 3 — Arena Pull Report (2026-10-19)

Owner directive: "get it all wired up fully and to a full chimera build game
and all the arenas." This stream pulls stage/arena geometry from completed
teardowns into `game/` and wires them into the stage system
(`game/js/stages.js` — registry + builders, consumed by `game/js/scene.js`
and the CHOOSE YOUR ARENA select screen in `game/js/main.js`).

## Pulled this stream

| Source | Stages | Format in game | Status |
|---|---|---|---|
| Tekken 3 (teardown/tekken3) | 15 retro arenas | OBJ panorama shells + decoded texture atlases (`game/assets/stages/t3/`) | WIRED (prior lane, verified this stream) |
| WWF No Mercy (teardown/wwf-no-mercy/arenas) | 17 arenas | GLB (`game/assets/stages/nomercy/`), vertex colors from `.vc` sidecars | WIRED this stream |
| Eastern Mind (teardown/eastern-mind) | 6 pano backdrops | PNG (`game/assets/stages/eastern-mind/<stage>/pano.png`) on the 6 canon lands | WIRED this stream |
| Sun Rā boss arena | 1 | existing GLB+planet textures (`game/assets/stages/sunra/`) | VERIFIED wired |

**Registry total: 41 stages** — 8 CANON LANDS + 15 TEKKEN RETRO + 17 WWF NO
MERCY + 1 BOSS STAGES (Sun Rā).

### No Mercy conversion (tools/stage-arena-pull/convert_nomercy.py)

- Input: `teardown/wwf-no-mercy/arenas/<name>.obj` + `<name>.vc` (per-vertex
  RGB, from PR "arena assembly" lane).
- Output: one GLB per arena — per-`g`-group meshes (names preserved for the
  reskin lane), flat normals (authentic N64 look), COLOR_0 vertex colors,
  TEXCOORD_0 UVs preserved, uniform 0.007 scale, fighting surface at y=0.
- Dropped (documented ROM limitations, see teardown ARENAS.md caveat 2):
  ring posts, turnbuckles, apron skirts, ring steps, unlabeled `0xNNN_Arena`
  template groups, cage wall pieces, announce table (all placement-less
  templates / junk coordinates), the 69 crowd/balcony runtime-instance
  templates, and `Outside_Floor_Pads_Larger_Pieces` (stored above the mat).
- The `nomercy` builder re-adds procedural ring posts + 3 ropes/side for
  ring arenas, and procedural chain-link cage walls for `nm-cage`.

### Eastern Mind panos

Real background art frames from the teardown bitmaps, on a cylindrical
backdrop behind the procedural sky: plains-of-chi-u (F_FIELD), helix-palace
(G_CASTLE), palace-of-dreaming (W_PALAC1), tree-of-life (L_FIELD),
phantom-marketplace (D_MERCHA), octagonal-shrine (E_MOUNT).

### Reskin pipeline (tools/stage-arena-pull/reskin_stage.py)

`reskin_stage.py <in.glb> <out.glb> --preset night|sunset|bloodmoon|ultraviolet`
or `--tint r,g,b` / `--group-color SUBSTR=r,g,b`. Originals always ship;
variants are additive (`arena_raw.night.glb`). Verified working; no
variants shipped yet per "ship the originals first."

### Thumbnails + gallery

- `tools/stage-arena-pull/render_gallery.py` screenshots every registered
  stage through `game/stage-test.html` (own-eyes verification).
- Gallery (owner deliverable): `~/workspace/your_files/stage-refs/<id>.png`
- Select-screen thumbnails: `game/assets/stages/thumbs/<id>.png`, wired via
  `s.thumb` with swatch fallback in the stage-card HTML.

## Pending — coordinate with the teardown stream

| Source | Stages | Blocker |
|---|---|---|
| Virtua Fighter 5 (release vf5-ps3-v1) | 18 arenas + 20 training/test | `*_obj.bin` geometry decode (chrrox/3ds Max pipeline noted in teardown/virtua-fighter-5/stages/README.md) — not done |
| Soulcalibur II | ? | teardown at ~60%; no stage geometry extracted yet |
| Tekken Tag Tournament 2 | 29 | teardown in progress |
| Dead or Alive 4 | ? | ISO reassembly sequenced after TTT2 |
| Urban Reign | 7 PPKs | inner Namco geometry not yet decoded |

When a teardown delivers decoded stage geometry (GLB/OBJ + textures), the
pull pattern is: drop files under `game/assets/stages/<game>/`, add a
builder (or reuse `nomercy`'s GLB pattern), register entries with
`STAGES.push`, re-run `render_gallery.py`, open a PR.

## PRs

- Stream 3 work: branch `stream3/arena-pull-20261019` → PR (to be opened on
  completion of the gallery pass).
