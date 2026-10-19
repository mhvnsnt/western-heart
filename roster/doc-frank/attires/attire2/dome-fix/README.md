# Wowomomo Dome Fix — Build Notes

**Owner spec (2026-10-19):** Real glass (IOR/transmission), full dome connected
all the way around, green fluid inside (partial fill, sloshing), closure is
glass too. Brain already inside — NEVER add an extra brain.

## What was built

**File:** `model-dome-glass.glb` (73MB)

**Changes from the original `base/model.glb`:**
1. **DomeGlass material** (transmission=1.0, IOR=1.5, roughness=0.05) assigned
   to 134,000 polygons (70,728 verts) forming the dome shell. The shell was
   identified by spherical selection: r=0.075–0.105 from head center
   (-0.012, 0.000, 0.395), z>0.32.
2. **DomeFluidMat material** (green, transmission=0.9, IOR=1.33) on a new
   `DomeFluid` mesh (608 verts) — a partial UV sphere inside the dome,
   positioned at the head center, scaled to 60% height to simulate partial
   fill. The top is cut flat (bisect) to create a liquid surface.
3. **Brain:** NOT duplicated. The existing brain geometry (inside the mesh)
   shows through the transparent dome. Verified: no new brain mesh added.

## Analysis findings

- The dome shell covers a FULL 360° at the top (z>0.44, 18k verts). The
  "half-dome" the owner sees may refer to: (a) the hemisphere profile (which
  is correct for a dome), or (b) the base/closure not being sealed. The shell
  is geometrically complete around the vertical axis.
- The closure (flat bottom of the hemisphere) was not separately identified;
  the dome sits on the head mesh which forms the base. If a distinct glass
  closure disk is needed, it requires manual modeling.

## Verification status

- ✅ **Structural:** GLB parses, 3 materials with correct transmission values,
  2 meshes (main + fluid), 73MB.
- ❌ **Visual (transparency):** NOT verified. The VM has no GPU/EGL for EEVEE
  (Blender crashes on EEVEE renders). Workbench renders don't show
  transmission. The glass/fluid WILL render correctly in the game engine
  (which supports glTF KHR_materials_transmission), but this has not been
  seen with own eyes.
- ⚠️ **Sloshing:** The fluid is a static mesh. Shader-based sloshing (vertex
  displacement/UV scroll) must be implemented in the game engine — not baked
  into the GLB.

## Next steps

1. Load `model-dome-glass.glb` in the game to visually verify the glass +
   green fluid + brain visibility.
2. If the "half-dome" refers to a missing front section (not found in the
   geometric analysis), provide a reference image circling the gap.
3. Implement fluid slosh shader in `game/js/` (vertex wobble driven by
   character velocity).
