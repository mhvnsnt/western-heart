# Doc Frank Wowomomo Dome — Editable Parameters

**Owner 2026-10-19:** "go in the game and edit it and save the edit on the attire... with a live preview just like the tech and creation suite straight from the files"

## How It Works

The dome is built from **editable parameters**, not baked geometry. Change a parameter, rebuild, see the result.

### Files

| File | Purpose |
|------|---------|
| `dome-params.json` | Parameter values (edit this) |
| `render-work/build-dome-v5.py` | Build script (reads params, outputs GLB) |
| `game/js/dome-params.js` | In-game UI module (sliders, live preview, save) |
| `model-dome-glass-v5.glb` | Built output (do not hand-edit) |

### Parameters

**Glass:**
- `glass_z_bot` — Bottom of glass extension (v5: 0.197, 1/3 shorter than v4)
- `glass_transmission` — Glass clarity (0.0=opaque, 1.0=clear)
- `glass_ior` — Index of refraction (1.5=glass)

**Liquid:**
- `fluid_z_top` — Top of liquid (**LOCKED at 0.421**, owner: "DO NOT RAISE")
- `fluid_z_bot` — Bottom of liquid
- `liquid_forward_offset` — Forward depth toward viewer (covers face front)
- `liquid_radius_scale` — Liquid width multiplier
- `fluid_color` — RGBA liquid color
- `fluid_transmission` — Liquid clarity

**Effects:**
- `lava_count` — Number of lava blobs
- `bubble_count` — Number of bubbles
- `lava_emissive` — Lava glow color

### Editing

**Manual (files):**
1. Edit `dome-params.json`
2. Run `python3 render-work/build-dome-v5.py`
3. New GLB at `dome-fix/model-dome-glass-v5.glb`

**In-game (customization UI):**
1. Open character customization → Doc Frank → Attire 2 → Dome
2. Adjust sliders (live 3D preview updates)
3. Click "Save to Attire" (writes `dome-params.json`)
4. Rebuild GLB (or trigger auto-rebuild)

### Version History

- **v5** (2026-10-19): Bottom shortened 1/3, liquid forward depth +0.005, params file added
- **v4d** (2026-10-19): 3x fluid, lava blobs, extended glass to neck
- **v4** (2026-10-19): Glass extension, fluid rebuild
- **v3** (2026-10-19): First working dome with fluid
