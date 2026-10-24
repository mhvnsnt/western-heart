# DEMONIO — Forms (owner 2026-10-19)

Three forms, one fighter. Transform system supports both directions
(Roshi-style mid-match, classic Tekken/DBZ).

| # | Form | Model | Moveset | Access |
|---|------|-------|---------|--------|
| 1 | **Attire 1: unwinged demon** (base/default) | `attires/attire1/model.glb` | demonio (base) | Start |
| 2 | **Winged devil** (transform UP) | `attires/winged-devil/model.glb` | demonio-devil (devil Jin base: flight, laser) | Mid-battle transform from Attire 1, OR start as this form |
| 3 | **Human** (transform DOWN, rare depower) | `attires/human/model.glb` | demonio (basic) | Rare reverse transform from base demon form, OR start as this form |

## Canon notes (owner verbatim)
- Attire 1: "Demonio attire 1 (unwinged demon, normal Jin moveset)" — the
  demonio moveset family is the renamed Tekken Jin family (owner 2026-10-19).
- Winged: "complex hands, do le hands on each hands, demon bat hands coming
  from his palms/wrists, 3 fingered extra bat hands on each palms, 8 fingers
  on each arm/ 2 palms on each hand, all need rigging, winged, devil Jin
  moveset base, can transform to him mid battle or choose to start as this
  form, classic Tekken/DBZ style"
- Human: "demon face still on chest/torso, possessing him, rare
  transformation down from base default demonio, can also start as him,
  basic jin moveset"

## Rig status
- Attire 1 + human: standard auto_rig pass (dense Tripo statics → `knn`
  backend recommended).
- Winged: see `RIG-SPEC.md` — complex hand + wing rigging. Most complex rig
  on the roster. No shortcuts.

Renders own-eyes verified 2026-10-19 (Workbench front views).
