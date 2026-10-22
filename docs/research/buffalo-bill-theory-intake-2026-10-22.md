# Intake: Buffalo Bill + Theory Tripo pulls (2026-10-22)

ARCHIVE ONLY. No canon entries invented — canon bridges come later from the user.

## Sources
- Buffalo Bill: user's Ashlane character, one of the Ashlane 28. Distinctive: ram horns.
- Theory: user's "wizard gang" / Ashlane character. 3 attires.

## Pulled assets (immutable originals, Tripo public API)
Owners: `marz6kdabest` for all except theory-a3 (`tzflo312`) and theory-a4 (`eqqq57218`).
| Attire | Tripo project | File | Bytes |
|---|---|---|---|
| Buffalo Bill A1 | fantasy character 3d model | `roster/buffalo-bill/attires/attire1/source/buffalo-bill-a1.glb` | 20,391,004 |
| Buffalo Bill A2 | horned humanoid 3d model | `roster/buffalo-bill/attires/attire2/source/buffalo-bill-a2.glb` | 21,441,832 |
| Theory A1 | gothic cat girl 3d model | `roster/theory/attires/attire1/source/theory-a1.glb` | 22,369,448 |
| Theory A2 | superhero costume 3d model | `roster/theory/attires/attire2/source/theory-a2.glb` | 18,773,404 |
| Theory A3 | dark fantasy character 3d model | `roster/theory/attires/attire3/source/theory-a3.glb` | 20,769,628 |
| Theory A4 | black leather outfit 3d model | `roster/theory/attires/attire4/source/theory-a4.glb` | 21,511,628 |

Each `source/` dir also holds a `manifest.json` with the Tripo share URL, project UUID,
pull timestamp, and byte/magic verification. Tripo signed download URLs in the
manifests expire; the GLBs in the repo are the permanent records.

## Proof renders
`docs/proof/buffalo-bill-theory-2026-10-22/` — 6 T-pose renders (1024x1024 PNG):
`buffalo-bill-a1.png`, `buffalo-bill-a2.png`, `theory-a1.png`, `theory-a2.png`, `theory-a3.png`, `theory-a4.png`.
(All 6 visually verified: Buffalo Bill A1 streetwear w/ ram horns, A2 shirtless w/ ram horns,
Theory A1 gothic cat girl, A2 superhero red cape, A3 dark fantasy spiked, A4 black leather outfit.)

## Restore points
Immutable-original tags on the archive commit: `buffalo-bill-a1-original`,
`buffalo-bill-a2-original`, `theory-a1-original`, `theory-a2-original`,
`theory-a3-original`, `theory-a4-original`. Message: "Restore point: these bytes never change."

## Next steps (for the rig pipeline, not this PR)
- Rig each GLB to its character rig; Buffalo Bill's ram horns are part of the source mesh.
- No canon/bio/moveset work was done here per owner instruction.
