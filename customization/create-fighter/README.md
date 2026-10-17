# Create Fighter — working web UI prototype

**Western Heart character customization suite, v0.1 prototype.** Tekken 7 customization FEEL
(full-screen fighter, floating panels, buy→equip loop) + No Mercy CAW depth + DOA wardrobe + WWE moveset.

Self-contained: `python3 -m http.server` in this dir, open `index.html`. No build step, no CDN —
three.js is vendored (`vendor/`), Soldier.glb base rig in `assets/`, data snapshots in `data/`.

## What's real today
- Full-screen 3D preview: Soldier.glb, Idle animation, slow auto-rotate, drag-orbit, scroll/pinch zoom. Fighter never covered by UI.
- Left rail: BODY / ATTIRE / WARDROBE / PROFILE / MOVESET (per `customization/UNIFIED-UI-SPEC.md`).
- ATTIRE: real 3,372-part index (`data/PARTS-INDEX.json`) browsable by category with search + pagination, deterministic prices/rarity, buy→equip two-step with Fight Money wallet, T7-style conflict Replace/Cancel, per-part color/material channels.
- BODY: 14 No Mercy body types, 8 skin tones, WMXIX proportion sliders — all live on the 3D preview.
- WARDROBE: 10 DOA-style quick slots (save/load snapshots), two-phrase titles.
- PROFILE: name/alias/music/titantron + Soul/Element/Land canon + fighting style + No Mercy parameters.
- MOVESET: full 176-slot tree from `MOVE-SLOTS.json`, assign moves from `MOVE-DATABASE.json`, Combot cross-roster rule; grey dummy opponent appears in-ring on this tab.
- Save/export/load fighter JSON (CHARACTER-CREATION.md §6 format) — download + localStorage + photo-mode thumbnails (📸 captures the live canvas).

## Honest gaps (marked in-UI, never faked)
- **Part geometry pending**: part meshes (.ymg/.obj from teardowns) aren't wired to the renderer yet. Every part card carries a `GEOMETRY PENDING` badge; equipping shows a labeled pulsing socket marker at the part's bone anchor in your chosen colors and records the part in the fighter JSON. Color/material edits apply to the marker now and to the real mesh when it lands.
- **Move animation test**: slot→move assignment saves today, but most moves have `anim_ref: null` — live in-ring animation playback wires in when per-move clip links land (CHARACTER-CREATION.md §9.4).

## Layout law
Fighter is always visible full-body, full-screen, on every screen. Panels are translucent, pinned to screen edges, and never cover the fighter. Touch targets ≥ 56px.
