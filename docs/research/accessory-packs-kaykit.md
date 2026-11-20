# Research: KayKit Adventurers weapons (CC0)

## What it is
KayKit (Kay Lousberg) publishes stylized low-poly game asset packs. The
**Adventurers Character Pack** free tier ships 27 weapons/props. KayKit's
packs live in the official `KayKit-Game-Assets` GitHub account (user, not org).

## Where from
- https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0
- itch.io: https://kaylousberg.itch.io/adventurers-character-pack
- Files taken from `addons/kaykit_character_pack_adventures/Assets/gltf/` in the repo.

## License
**CC0 1.0 Universal** — verified in the pack's own `LICENSE.txt`
("License: (Creative Commons Zero, CC0) ... free to use in personal,
educational and commercial projects."). Owner's license rule allows
CC0/MIT/Apache/permissive; KayKit is CC0, same as Kenney.

## Why pulled
Fantasy melee weapons + shields for the Creation Suite `extra` slot —
complements the Kenney sci-fi blasters with swords/axes/shields/staffs.

## Format note
Upstream ships `.gltf` + `.bin` + `.png` (not single-file GLB). Our pipeline
consumes GLB, so each model was packed into a single-file GLB with a small
script: `.bin` concatenated as the BIN chunk (original bufferView offsets
preserved), referenced `.png` textures embedded as bufferView images with
mimeType, URIs removed. All 27 outputs validated: glTF magic, JSON chunk
parses, non-empty meshes, PNG magic bytes on every embedded image.

## Where landed
- `game/assets/accessories/kaykit-adventurers/` (27 GLB + LICENSE-CC0.txt + README.md)

## Follow-ups
- KayKit Dungeon Remastered + Medieval Hexagon packs may hold more
  armor/weapon pieces (not yet pulled).
- KayKit character bodies (Knight/Barbarian/Rogue/Mage with helmets/hoods)
  are a separate tier — hats/helmets still open.
