# T8 select reference spec — Lane H handoff to the UI lane (2026-10-24)

**Rule first, so the two Tekkens never get confused:** T8 is VISUAL
REFERENCE ONLY. T7 stays the STRUCTURAL source for the select screen.
This lane changes NOTHING in the select CSS, load order, roster, or
grid — it hands the UI lane a spec, staging data, and (via the GPU job)
renders. The UI lane owns any select edit.

## 1. What T8 looks like (visual reference, decoded)

Source decode: `teardown/tekken8/ui/CHARACTER-SELECT.md` (1,831 bytes)
plus `docs/select-redesign/T8-GRID-DECODE.md`. Reference images:
`teardown/tekken8/ui/refs/t8-select-ref-1.png`,
`t8-select-ref-2.png`, `t8-select-ref-3.png` — each 1080×2400 RGBA
phone screenshots, cited in `game/ui_sources.json` for screen-select.

- Stage: full-bleed dark stage, red wash left (P1), blue wash right
  (P2), cool light from top centre.
- Fighters: large 3D model per side in idle fight stance, P1 left
  facing right, P2 right facing left; faded portrait art behind each.
- Name: huge italic condensed uppercase at the outer edge, glow in
  player colour (P1 `#ff2d55`, P2 `#2f9dff` in `game/select-t8.css`).
- Facts: small coloured label chips — Fighting Style / Nationality /
  Height / Weight — white value under each; T8 prints "Unknown" for
  unset facts.
- Grid: compact centred block of small square face cards, no names,
  ~12 per row at 1280×720 (≈60 px cards); P1 cursor red, P2 cursor
  blue; locked cards carry a P1/P2 tag.
- Random: black card with white "?" inside the grid flow.
- Hints: bottom-left glyph hints ("Confirm / Back / Customized
  Slots"), touch targets ≥44 px on phone.
- Timer: countdown top centre, no screen title.

**Honest note on the refs:** ref 1, inspected 2026-10-24, is a phone
screenshot of a search-results page whose thumbnails show the T8
select (Kazuya vs Jun and others) — it corroborates the decode above
(big flanking models, outer-edge italic names, fact chips, centred
face-card grid, "?" card, bottom hints) but it is NOT a clean direct
T8 capture. The clean decode lives in the two docs above, not in the
screenshots alone. Do not cite a screenshot thumbnail as a measured
layout value.

## 2. What T7 structure must be preserved (structural source)

From `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md` (measured T7 Steam
extraction, PR #863):

- Roster card 96×148, portrait bust, number bottom-right.
- P1 cursor 208×336 red `#e0182a`, double frame, gradient up.
- P2 cursor 208×336 blue `#1a8cff`, double frame, gradient up.
- Side panels 108×292 (P1 red left, P2 blue right).
- Random card 68×68 red "?" glyph.
- Stage info 420×656, stage panel (selected) 1180×696,
  navy→black gradient, red 1 px rim, notched corner.
- Panel gradient `#1b2740` → `#0d1322` (55%) → `#04060a`.
- Main menu column 572×1080, dark glass vertical list.
- T7 last-fighter / attire save system (copy it; do not replace it
  with anything T8).

T7 raw textures are Bandai Namco property and belong in the private
repo `mhvnsnt/game-reverse-engineering`, NOT the public repo — the
public build reproduces only sizes/colours/layout rules in CSS.

## 3. What is already on main (do not duplicate it)

- `game/select-t8.css` — the T8 visual layer (stage washes, side
  panes, outer-edge name plates, fact chips, centred grid, random
  card, hints bar, timer, hidden title).
- `game/index.html` loads `select.css`, then `select-t8.css`, then
  `select-t7.css`. NOTE the load order: the T7 skin loads AFTER the
  T8 layer. This lane does not change that order; the UI lane owns
  the final cascade if the order ever needs revisiting.
- `game/ui_sources.json` cites the three T8 refs for screen-select.
- Phone-portrait stacking (stage over grid, 8 columns) comes from
  the owner's Brutal Fist select, not from T8 — keep that
  attribution straight.

## 4. What this lane adds (no select code touched)

1. `game/data/t8-sfm-staging.json` — inert staging for the two T8
   SFM archives (Yoshimitsu Blender, Asuka Source MDL). It is NOT
   loaded by any game JS. It carries: archive locations + verified
   contents, texture gates, bone maps (Asuka `bip_*` known; Yoshimitsu
   pending the GPU Blender dump), wire-in points, and the owner
   eye-check steps. No roster entry is added by it.
2. `tools/gpu-jobs/t8-sfm-gpu-job.py` — the Kaggle GPU job (see §5).
   After a model's texture gate passes, it renders T8-select-framed
   views (P1-left red wash / P2-right blue wash, idle stance, front
   + 3/4 view, square face-card crop) for UI-lane card art. Before
   the gate passes, its renders are DIAGNOSTIC ONLY and must not be
   used as card art.
3. This spec.

## 5. GPU select renders (workstream 4, gated)

- Render on GPU with Blender EEVEE (GPU proof + timings recorded by
  the job script; CPU baselines for unpack/list are in the staging
  file — GPU timings are pending the Kaggle run, never claimed).
- Framing: match the T8 decode (§1) at phone-portrait 1080×2400 for
  the stage view and square crops for face cards.
- Gate: no render ships as select art until (a) the model's texture
  gate passes, (b) the GLB loads with rig + textures, (c) the owner
  eye-checks it, (d) the Asuka attire decision is made (the archive
  attire is a bikini variant — see staging file; it must not become
  a default attire by silence).

## 6. Explicit non-changes (UI lane: please keep these intact)

- No edit to `game/select-t8.css`, `game/select-t7.css`,
  `game/select.css`, `game/index.html` load order, or `game/js`
  select logic in this lane.
- No T8 geometry, card size, cursor size, or save system replaces
  any T7 value.
- No T8 data lands in any T7 file — in particular, NO T8 King data
  in T7 Pantera files (the `tekkenDocs king.json` trap).
- No broken / untextured / wrong-model fighter appears on select,
  ever. Until a model passes gate + eye-check, its slot stays on
  the existing "model coming" placeholder.
- Buttons in all user-facing text: LP1 / RP2 / LK3 / RK4.
  (No move inputs are defined in this lane — models only.)
