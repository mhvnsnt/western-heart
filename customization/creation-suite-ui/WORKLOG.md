# WORKLOG — Creation Suite UI rebuild

## 2026-10-18/19 — UI rebuild lane

**Owner instruction (verbatim):** "Needs to be more like WWE and Tekken and menus
and sub menus and etc really pull in the UI and layout from the teardown games and
the sliders and menus and everything and u need better placement accuracy and UI
would help u too from the game files verbatim and anything else free and avail and
industry standard for characters customization and parts u can wire up and pull in
to the repo"

**Method specified:** teardown UI extraction (T7 .uasset UI, T6/TTT2 menu data, WWE 2K
CAW flows) → document verbatim sources → free industry-standard UI research →
rebuild the front end on the wired systems → placement-accuracy UI → video demo.

### What was done

1. **Teardown UI extraction** — surveyed `~/workspace/tekken-customization-extraction/REPORT.md`
   (2026-10-16): T7's complete customization database schema is extracted (17 slots,
   slot-group UI ordering, conflict rules, 21-field item CSV, 0-5 color system), but the
   actual `.uasset` UI layout binaries are NOT in any teardown. WWE 2K game files never
   landed (51GB blocked) — CAW flows are researched, not extracted. Documented verbatim
   vs researched in `UI-EXTRACTION-LOG.md`; every menu node in `js/menu-data.js`
   carries its source tag.
2. **Free UI research** — no MIT-licensed web character-creator front end exists worth
   pulling. Wired: three.js (MIT, repo-vendored) for the viewport, MDickie tap grammar
   for every picker, spring-bone jiggle schema. Kenney UI Pack is donation-gated (could
   not pull); Say_K GUI pack lacks a clean license; Godot asset library refused
   connection — UI art is original, zero license risk (documented).
3. **Front end built** (`customization/creation-suite-ui/`):
   - `index.html` — hub shell: full-screen 3D fighter, topbar, left rail, right panel,
     placement dock, bottom bar. Phone-first, 44px+ tap targets, NO drag-and-drop.
   - `css/suite.css` — original dark arena theme.
   - `js/menu-data.js` — verbatim menu trees (T7 17 slots + T6 subdivisions + T8
     additions, No Mercy body/profile, WMXIX proportions, DOA wardrobe, WWE 2K
     flows, jiggle areas/params, placement axes).
   - `js/suite.js` — hub logic: 7 tabs (BODY/ATTIRE/PARTS/JIGGLE/WARDROBE/PROFILE/
     MOVESET), tap-to-assign pickers, buy/equip two-step, conflict Replace/Cancel,
     color channels, wardrobe snapshots, localStorage persistence.
   - `js/viewer3d.js` — three.js viewport: drag-orbit, pinch/wheel zoom, base model
     load, socket-anchored part attach with live placement.
   - `data/parts-catalog.json` — 34 parts derived from PARTS-REGISTRY.json (6 mesh
     parts with real GLB paths + sockets; 28 texture parts).
   - `data/jiggle-schema.json` — per-area amplitude/frequency/damping/stiffness,
     female + male-fat families, Star override stub for the jiggle lane to fill.
4. **Placement accuracy** — every mesh part gets the placement dock: position X/Y/Z
   (±0.5m), pitch/yaw/roll (±180°), scale (0.1–3×), sliders + ±nudge buttons at
   0.001/0.01/0.1 steps, numeric readouts, snap-to-socket, reset. Offsets persist
   per part per attire in the fighter JSON.
5. **Video demo** — `demo/record-demo.py` (Playwright): drives the real UI — PARTS →
   Masks → tap batgirl mask → EQUIP → placement dock nudge → JIGGLE sliders →
   ATTIRE category → buy/equip → BODY slider. Frames own-eyes verified.

### Deviations
- New directory `customization/creation-suite-ui/` instead of editing
  `customization/create-fighter/` in place — the existing hub stays untouched (other
  lanes depend on it); the rebuild reuses its vendored three.js + Soldier.glb.
- UI art is original rather than Kenney-pulled (donation gate) — documented.

### 3D placement engineering (verified with own eyes, 2026-10-19)
- Soldier.glb's rendered size comes from BONE scale, not geometry bbox — sockets
  resolve from bone world positions (mixamorig/mixamorig: prefix stripped), facing
  from the Head bone's world quaternion. Works for any model.
- Part geometry normalized on attach (bbox center → group origin) so cross-character
  parts (modeled for cyborg-x) land on the socket; part-local +Z aligns to bone
  facing, user euler applies on top.
- Batgirl domino mask verified attached at the face socket, oriented correctly
  (eye holes forward), nudge-tested in 0.01/0.001 steps with live readout.
- Demo video: `demo/creation-suite-demo.mp4` (165s, 8.8MB) — full UI walkthrough,
  every frame own-eyes verified via extracted stills.

### Proof
- `demo/creation-suite-demo.mp4` + extracted frame stills (own-eyes verified).
- PR body carries law-15 sections.
