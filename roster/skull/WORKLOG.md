# WORKLOG — Skull Tripo Attire 1 wire (2026-10-19)

## Owner instruction (verbatim, 2026-10-19 ~00:59 CDT)

"did u already get skull for the Bryan fury attire 1 reskin and proprietary
replacement? https://studio.tripo3d.ai/3d-model/d77eb53a-5369-4055-9ee6-b4a46eaf7789
and Bryan fury attires go later in the latter as 4, 5, 6, etc"

## What was done

1. **Pulled the Tripo model** via `tools/tripo-pull/` (public-API tool, no
   sign-in): `human_figure_3d_model.glb` (23MB, 1 mesh, 3 textures,
   meshopt-compressed, valid glTF 2.0). sha256:
   `94c8ef788267cc790caa8eac517a279bd0c62f84eb061298b348acfe2904542d`.
   Model: skull face paint/mask, skeleton ribcage body paint on bare muscular
   torso, digital-camo cargo pants, black combat boots, fingerless gloves.
2. **Viewed the front render with my own eyes** (OWN-EYES-BEFORE-DELIVERY LAW):
   `~/workspace/tripo-downloads/skull-tripo-front.png` — true FRONT view
   (no rotation needed), matches the model description exactly.
3. **Wired as Attire 1** at `roster/skull/attires/attire1/model.glb`
   (Kevin/Star/King-Tyrant pattern — the COMPRESSED original GLB in the repo;
   the decoded copy stays a local Blender working file only).
4. **Wrote `roster/skull/attires/ATTIRE-SLOTS.md`**: A1 = Tripo "Skull"
   proprietary replacement (default); A2/A3 reserved for future customs;
   A4+ = Bryan Fury in-game attires (`game/assets/models/skull.glb` base,
   RigModels fan rip) laddering back per the owner's slot order.
5. **Updated `roster/TRIPO-REGISTRY.md`**: SKULL row added (✅ attached),
   skull removed from the "no Tripo on record" Others row.
6. **Locked-standard front render** at `docs/tpose-refs/skull/p1_front.png`
   (own-eyes verified true front).

## Not done (recorded, not blocking)

- **Live-game default NOT swapped** (`game/js/assets.js` untouched) — the
  Tripo GLB is an unrigged static; the playable swap rides with the auto-rig
  pass (same pattern as Kevin/Star/King Tyrant).
- Rigging: needs auto-rig (tools/auto_rig/, PR #273) before it can fight.
- Generative-AI transform into the proprietary Eastern Mind / Western Heart
  version — flagged 🎨 per registry convention; render goes to the owner.
