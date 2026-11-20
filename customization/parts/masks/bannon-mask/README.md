# Bannon Mask — Mask Accessory (owner 2026-10-19)

Owner: "Bannon mask accessory piece / mask attire piece for customization
parts and etc. If u don't have it."

Checked 2026-10-19: `customization/parts/` had no mask pieces
(`accessories/` held only `chains`; PARTS-REGISTRY.json had no mask entry).
This is new — no duplicate.

## Piece
- Model: `model.glb` — Tripo pull 2026-10-19 (`metallic_mask_3d_model.glb`,
  23.3MB, by dm333n).
- Style: metallic mecha faceplate — angular brow/cheek plates, eye slits,
  nose bridge, plus a separate lower jaw/chin piece.

## Socket / attachment metadata (creation suite)
```json
{
  "part_id": "bannon-mask",
  "slot": "face",
  "socket": "head",
  "socket_bone": "head",
  "offset": { "x": 0, "y": 0, "z": 0.02 },
  "pieces": ["faceplate", "jaw"],
  "jaw": { "articulated": true, "socket_bone": "jaw" },
  "fits": ["humanoid"],
  "tags": ["mask", "bannon", "metallic", "mecha", "accessory"]
}
```

Notes:
- The jaw is a separate piece — articulate it to the `jaw` bone when the
  target rig has one; otherwise parent both pieces to `head`.
- Eye slits are open geometry (no lenses) — pairs with eye-library pieces.
- Render own-eyes verified 2026-10-19 (Workbench front view).

Standing law: this piece lives in western-heart's customization library.
The Bannon repo itself is untouched.
