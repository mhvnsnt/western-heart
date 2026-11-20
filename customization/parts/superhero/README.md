# Superhero Pieces — female Cape Jones build kit

Attachable 3D pieces for the future **female Cape Jones** reskin of Cyborg X
(Alisa Bosconovitch, `game/assets/models/cyborg-x.glb` — the 41MB textured build).
Cape Jones is Space Ghost recolored, so the target look is: Space Ghost style,
**no head ears/fins**, **white eyes**, Batgirl-style fittings — built from OUR
pieces, not from any actual Space Ghost / Cape Ghost model.

All pieces are modeled **in place** at Alisa's real coordinates (measured from
`cyborg-x.glb`: eye centers (±0.026, 1.364, 0.055), face front Z≈0.06, forearms
Y≈1.178 Z≈−0.035). Drop them onto her model as-is; nudge in the build lane.

## Pieces

| File | What | Maps to |
|---|---|---|
| `spidergirl/spidergirl-eyes.glb` | Pair of white angular eye lenses (Spider-Girl/Spider-Man style), slight emissive white | **White eyes** — the signature piece |
| `batgirl/batgirl-domino-mask.glb` | Domino eye mask: torus rings around each eye + nose bridge + temple straps, dark charcoal | Batgirl-style eye mask (no cowl ears) |
| `spaceghost/spaceghost-cowl-no-ears.glb` | Skull-cap cowl, purple, face opening cut, **no ears/fins** | Space Ghost head without the ears |
| `batgirl/batgirl-gauntlets.glb` | Pair of finned forearm gauntlets, dark gray | Batgirl-style gloves/gauntlets |

## License

All four pieces are **original geometry modeled for this project** (Blender 4.0,
script: `_superhero-pull/build_pieces.py`) — no third-party mesh data. Treat as
project-original, free for our game builds. Recolor freely in the reskin lane.

## Research log (honest)

Pulled nothing from outside for these pieces — there was nothing openly
licensed AND downloadable through accessible channels:

- **GitHub code search** (`batgirl`/`spider-girl` + `extension:glb/fbx`): zero hits.
- **Sketchfab**: has Batgirl fan models, but downloads require OAuth — not
  accessible; not pulled.
- **Thingiverse** ("Batgirl Cowl FIXED", "BatGirl Cowl Gauntlet etc." by jreimers,
  "DC Super Hero Girls - Batgirl Mask" by duolc84): page fetches return HTTP 403
  to automation — licenses unverifiable, files not downloadable; not pulled.
- **Cults3D**: Batgirl cowls are paid or carry "personal use only, do not
  redistribute" terms (e.g. Roman Redbird's Batgirl cowl); not pulled.
- **models-resource.com**: game rips (Batman: Arkham Knight Batgirl exists as a
  rip) — search endpoint unreachable; ripped-game-asset licensing is murky for
  redistribution; not pulled.
- **Quaternius** (already in `assets/characters/quaternius/`, QAL v1.0): only
  generic eyebrows/hair — no superhero pieces; nothing to pull from it.

If cleanly-licensed Batgirl/Spider-Girl pieces surface later, they land here and
this log gets updated. The pieces above are originals, so the build is never
blocked on licensing.
