# DEMONIO — Winged Devil Form Rig Spec (owner 2026-10-19)

Owner spec (verbatim): "Demonio winged transformation (complex hands, do le
hands on each hands, demon bat hands coming from his palms/wrists, 3 fingered
extra bat hands on each palms, 8 fingers on each arm/ 2 palms on each hand,
all need rigging, winged, devil Jin moveset base, can transform to him mid
battle or choose to start as this form, classic Tekken/DBZ style)"

Source model: `roster/demonio/attires/winged-devil/model.glb`
(Tripo pull 2026-10-19, `demon_creature_3d_model.glb`, static, dense).

## Rig inventory (all must be rigged — no shortcuts)

### Base skeleton
Standard WH humanoid skeleton via `tools/auto_rig/` (same Mixamo-style bone
names the game expects). Recommended backend: `knn` with a donor rig
(e.g. `game/assets/models/pantera.glb`) — the source is a dense Tripo static
that Blender chokes on, which is exactly the `knn` backend's purpose.

```bash
python3 tools/auto_rig/auto_rig.py --in roster/demonio/attires/winged-devil/model.glb \
    --out roster/demonio/attires/winged-devil/model-rigged.glb \
    --backend knn --donor game/assets/models/pantera.glb
python3 tools/auto_rig/validate.py --in roster/demonio/attires/winged-devil/model-rigged.glb
```

### Extra demon bat hands (the complex part)
Per owner: demon bat hands growing from the palms/wrists — 3-fingered extra
bat hands on EACH palm — 8 fingers per arm / 2 palms per hand.

- Build as **extra bone chains rooted off the wrist/palm** (same pattern as
  the multi-arm research: extra arms are bone chains rooted off chest/shoulder
  — see `tools/limb-system/dxmmii/RESEARCH-MULTIARM-2026-10-19.md`).
- Each extra hand: wrist-root → palm → 3 bat fingers × 3 segments.
  (Bat fingers are elongated; membrane is skinned, not boned, except the
  finger chains.)
- Total per side: 1 base hand (5 digits) + 1 extra bat hand (3 digits) = the
  owner's "2 palms on each hand / 8 fingers on each arm".
- Weight painting: heat-diffusion will bleed across the overlapping palms —
  hand-tune the palm/wrist vertex groups after the auto pass.

### Wings
Large bat wings. Rig as finger-bone chains (3–4 elongated digits per wing
fanning from the wrist-knuckle) + 2 shoulder-root bones for fold/spread.
Membrane verts weighted to the digit chains. Must support:
- `spread` (flight/idle)
- `fold` (ground combat)
- `flap` cycle (DEVIL FLIGHT special in `demonio-devil.json`)

### Detach/attach rule (PR #302)
Any detach/reattach of the extra hands MUST use **Child Of keyframing**,
not structural reparenting — reparenting is not keyframable and parts won't
follow during playback (KNOWN_ISSUE_EXTRA_ARMS.md TODO #2). The Child Of
keyframing fix spec from PR #302 applies verbatim here.

## Validation gate
`tools/auto_rig/validate.py` — valid glTF, skinned mesh, Mixamo-style bones,
1.5–2.2 m, stretch < 2.5. The extra-hand and wing chains are additive and must
not break the base gate. Nothing ships that doesn't pass.

## Status
SPEC ONLY — rigging is owned by the auto_rig / multi-arm lane. This doc is
the build order. Dxmmii is it/its. Kiko is he/him.
