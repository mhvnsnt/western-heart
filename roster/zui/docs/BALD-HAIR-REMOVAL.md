# Bald / Hair Removal Technique

Saved 2026-10-14. How to make any fighter bald (monk look) without breaking the rig.

## Method: hide the hair meshes (non-destructive)

Do NOT delete hair geometry. Hide it — the rig and skinning stay intact, and the hair can be restored.

```python
for o in bpy.context.scene.objects:
    if "Hair" in o.name and o.type == "MESH":
        o.hide_viewport = True
        o.hide_render = True
```

This matches on the mesh name containing "Hair" (e.g. `ModelHair`, `Hair`, `hair_01`). If the base names it differently, adjust the substring.

## Why hide instead of delete

- Deleting hair meshes can orphan vertex groups and break the armature modifier.
- Hiding keeps the .blend/.glb fully reversible — unhide to restore.
- Hidden meshes are skipped by export (GLB export respects `hide_render` when "Visible Objects" is considered; verify on export).

## Gotchas (learned on the Steve Fox base)

1. **Check for multiple hair pieces.** Some bases split hair into 2–3 meshes (scalp, beard, eyebrows). Eyebrows/beard may be separate — decide per character whether they stay.
2. **Bald cap seam.** If the scalp mesh leaves a visible seam at the hairline, the head mesh underneath is usually complete (game heads are modeled bald under the hair). Verify with a close-up render.
3. **`img.pixels` edits don't survive .blend save/reopen** (Blender 4.0.2 confirmed). If tinting the scalp to skin tone, use a file-backed PNG texture, not in-memory pixel edits.
4. **Workbench renders** materials without an image texture as white — scalp/head materials need their textures intact.

## Full pipeline this was proven in

`~/workspace/zui_stage1.py` through `~/workspace/zui_stage5.py` — import Steve Fox base → hide hair → tint robe/pants → scrunch sleeves → tattoo decals → beads + gourd → render → export GLB. All in ONE Blender session (pixel/tint edits don't survive save/reopen).
