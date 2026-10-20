# Create Fighter — WORKLOG

## 2026-10-19 — Dome parameter module mounted into the Creation Suite

Owner order (2026-10-19 ~20:54 CDT): stop iterating on the Doc Frank dome in
the render lane — put ALL dome edit abilities into the Creation Suite with a
visual preview so he edits it himself.

What landed (branch `feat/dome-params-suite-20261019`):

- `game/js/dome-params.js` committed as-is from the v5 dome lane (was
  untracked), plus `roster/doc-frank/attires/attire2/dome-fix/dome-params.json`,
  `model-dome-glass-v5.glb`, and `DOME-PARAMS-README.md`.
- `customization/create-fighter/js/app.js`: imports the dome module; ATTIRE
  tab shows a **DOME PARAMETERS** entry when the fighter is Doc Frank and
  Attire 2 ("Wowomomo") is selected; `renderDomePanel()` builds the module's
  Glass / Liquid / Effects UI (sliders + color pickers), loads params from the
  attire's `dome-params.json` (suite-saved `attire().domeParams` win), and the
  module's **Save to Attire** button additionally persists the params onto the
  attire in the fighter JSON (localStorage autosave / presets / export).
- `customization/create-fighter/js/preview3d.js`: `enterDomePreview()` /
  `applyDomeParams()` / `exitDomePreview()`. The preview swaps to Attire 2's
  real base model with the v5 dome parts overlaid — the dome GLB was built in
  that exact model space (same `tripo_node_49e6f6b9-…`, identical bounds,
  identity transform — verified by parsing both GLBs), so there is no guessed
  mount transform. Param edits remap the baked geometry relative to the saved
  build params: liquid bottom/top (remapped z-range), liquid width (radius
  scale), forward depth (z-shift), liquid color + clarity (material), glass
  bottom (joint stays fixed), glass clarity + IOR, lava glow (emissive);
  lava/bubble counts toggle visibility at 0 (exact counts are build-time —
  labeled honestly in-panel). Liquid Top is clamped at 0.421 in code on top
  of the module's locked slider (owner: DO NOT RAISE).
- `customization/create-fighter/css/create-fighter.css`: `.dome-param-*`
  styles matching the suite theme.

Verification: `node --check` clean on all three JS files; a Node harness ran
the real `applyDomeParams` code against stub meshes seeded with the GLB's
measured geometry bounds — 21/21 checks pass (defaults reproduce the baked
geometry exactly, edits land on the requested values, raised Liquid Top is
clamped back to 0.421). No live-browser check was run by this lane.
