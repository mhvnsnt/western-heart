# Western Heart — T-Pose Render Standard

## Default Front View

Most models face the camera correctly with **no model rotation** when the camera is placed on the **−X axis** looking toward **+X**.

**Zafina** is the exception: it requires an additional **−90° rotation on the Z axis** before centering.

## Pipeline

1. Import GLB
2. Scale objects ×100 and apply (models export at 1/100 scale)
3. For Zafina only: rotate vertices −90° on Z
4. Compute bounding box and center model at origin
5. Orthographic camera on **−X** side, looking toward **+X**
6. Neutral gray background
7. Even studio lighting
8. 1024×1024 output

## Camera

- Position: `(-size * 2.5, 0, size * 0.05)`
- Ortho scale: `size * 1.15`
- Rotation: `(90°, 0°, −90°)` so camera looks toward +X

## Per-Model Notes

| Model | Extra Rotation | Notes |
|-------|----------------|-------|
| Most (Skull, Thor, King Tyrant, Kinpo Alt, Baek, Lili, Phantom, Saku Ra, Zui, Awa Pop, SAM-UR-A1, Waterfall, Pantera Alt, Purple Rain, N3GΔTIV0, etc.) | None | Camera on −X is sufficient |
| Zafina | −90° Z | Required to face forward |
| Kinpo, DXMMII, Nightwolf, Rave | May vary | Confirm orientation if blank or side-facing |

## Orientation Reference

| Request | Action |
|---------|--------|
| Front (default) | Camera on −X, no model rotation (Zafina: −90 Z) |
| Back | Camera on +X, or +180 Z on model |
| Left | Camera on −Y |
| Right | Camera on +Y |

## Notes

- Do not assume all models share the same default orientation.
- If a render is blank or tiny, check bounds and try camera on a different axis before rotating the model.
- Vertex-level edits work for unrigged meshes; object-level scale + apply is safer for most.
- All agents and render scripts should use camera-on-−X as the default front view.
