# Teardown Sources — excluded binaries

These files were deliberately left out of the repo (GitHub per-file limits,
bulk, or superseded intermediates). Every one is reproducible from the local
working copies at `~/workspace/game-reverse-engineering/`, which are never
deleted. Sizes in bytes, hashes are SHA-256.

## Raw disc / ROM binaries (extracted knowledge IS in the repo; the raw dumps stay local)

| Size | SHA-256 | Local path |
|---|---|---|
| 1459978240 | b84472a45f66c2ea968f18a4fec7b9abf44b0f1c6fd834e8727332f054e8fcb0 | `wwe-wrestlemania-xix/WWE Wrestlemania XIX (USA).iso` |
| 511082496 | dc972330ce1d483d90478a17c49a3984fdeb8d005911b378abb236fbf89b5350 | `tekken3/disc/files/TEKKEN3/TEKKEN3.XAS` |
| 493793312 | c9a41333f0a6ce86c54e20c767e83d55ea12cb4d8c0613b630233381912a9173 | `tekken3/Tekken and roms for files/Tekken 3 (Everything Unlocked).zip` |
| 33554432 | fc561fce443010b114cc8ea41226772b7b2a2d33055be163fad91ac9c3b096cb | `wwf-no-mercy/WWF No Mercy (USA) (Rev-A).z64` |
| 25926892 | 75e4594fa42233b024291b5e2866414b42e035b12e93a443c7a3e1dec6dafa57 | `wwf-no-mercy/WWF-No-Mercy.zip` |
| 170 | 9e93ecf12d78a8c4c278708706bd249fe086983fb28f82eb880f5c7795043962 | `wwf-no-mercy/nm.torrent` (torrent pointer only) |
| 229376 | ae3b436c1a87564839e6cbd9c2f4677c8ff4d5f6d17430346a10ee51e1d08e94 | `tekken7/king/Animate3D.exe` |

## Third-party tool bulk (tool source IS in the repo; its asset pack stays local)

| Size | Local path | Note |
|---|---|---|
| 150241972 | `tekken3/tools/tekken3recompiled/mods/assets/` | tekken3recompiled's own mod asset pack; re-pull from the upstream project if needed |

## Superseded build intermediates (finals already in the repo)

| Size | Local path | Note |
|---|---|---|
| 14731564 | `tekken7/king/pantera/pantera.glb` | superseded by `roster/pantera/pantera_rigged.glb` |
| 15748564 | `tekken7/king/pantera/pantera_light.glb` | superseded by `roster/pantera/pantera_rigged.glb` |
| 68992 | `tekken7/king/pantera/pantera_tiny.glb` | tiny preview, superseded |
| 91992 | `tekken7/king/pantera/pantera_tiny.b64` | base64 of the above |
| 17183427 | `tekken7/king/pantera/views/` | old render views |
| 43782239 | `tekken7/king/arena/` | Pantera arena build sources (`.blend`, stage scripts); outputs at `roster/pantera/showcase/` |

## Not yet pulled

- **Eastern Mind (Osamu Sato)** — download never confirmed; nothing on disk. Teardown lane pending.

## Public-hunt files over GitHub's 100MB/file limit (TeraBox only)

| Size | SHA-256 | Local path | TeraBox path |
|---|---|---|---|
| 269690413 | `tbd-after-terabox-upload` | `tekken7/arenas/mishima-dojo-full-8_10_21.rar` | `/western-heart/tekken7/arenas/` (pending upload — needs creds refresh) |
