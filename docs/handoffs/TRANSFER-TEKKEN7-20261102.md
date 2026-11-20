# Transfer: Tekken 7 teardown -> Western Heart moveset code — 2026-11-02

Source of truth for this lane: `docs/handoffs/TOOLS-AUDIT-20261102.md`
(PR #1506, main `497b12f4`). Source docs read via the GitHub API:
`mhvnsnt/teardown-tekken7` — README, TEARDOWN, TRANSFER-MAP, WIRING-PLAN.
The source game is named here only as docs provenance about pulling
its data. No source-game character name, model, texture, animation,
audio, logo or UI asset is in this PR, and no source-game character
name appears in any player-facing UI string in this PR.

## What this PR wires (code the game can actually read)

| Transfer | Wired here | How it is read |
|---|---|---|
| T1 frame-data row schema (TEARDOWN §3) | `game/js/frame-data-schema.js` + `game/data/frame-data-schema-examples.json` | `validateFrameRow` / `normalizeFrameRow` parse command, hit levels, damage, startup (`i16`, `i30~31`, `i10, i23`), on-block/on-hit/on-CH, tags, transitions, recovery. Unparseable values stay `null` + flagged, never coerced. |
| T3 move properties (TEARDOWN §4) | Same module | Tag windows (`hb`, `pc7~16`, `js21~29`, `cs`), guard rules (high whiffs croucher, mid hits croucher, low blocked only by crouch guard), punish check (`canPunish`). Existing `game/js/combat-core.js` keeps owning live contact; this module owns the row shape it reads. |
| T1b rig mapping (TEARDOWN §5, WH bake path) | `game/js/mannequin-role-map.js` | The 19-bone mannequin list WH's own Blender bake path already uses maps to WH semantic roles (16 roles + root). Upper-arm bones have no WH role and are returned as `unmapped`, not dropped silently. |
| 23-bone clip shape (TEARDOWN §5) | Same module | `validateClip23` (23x3 numbers per frame) + `spikeFilterClip23` (0.5 rad step rule from the teardown) + mm->m root conversion. Shape only — see the owed item below. |
| Tests | `test/frame-data-schema.test.mjs` (22 assertions) | Run by the existing `game-checks` game-unit-tests job. |

## Explicitly NOT claimed here (still owed, with reasons)

- **23-bone -> mannequin bone map: OWED, evidence-gated.** The teardown
  records the 23-bone clip list and the 19-bone mannequin list as
  different lists, and the per-bone reference frame for compressed
  (0x64) clips as an open problem gated on paired 0xC8/0x64 data or a
  named community source. This PR does not invent that map; it
  validates the 23-bone shape only.
- **Per-class command-input / hit-contact / throw sweeps (T2/T3/T4):
  OWED, queued behind the combat lane's one-class-at-a-time seam.**
  This PR adds the row schema those sweeps read; it does not change
  `game/js/input.js` or `game/js/combat-core.js`.
- **Per-fighter clipmaps beyond the existing tools (T6/T6b): OWED.**
  `tools/anim/t7_anim64.py` / `t7_clipmap.py` already exist; running
  them per fighter is lane work, not redone here.
- **Common-bank (0x8000) join: already prepared in the teardown's
  wiring plan as a separate claim; not bundled here** to keep this PR
  additive and reviewable.
- **Stages / customization / select / menus / health (T8-T11): already
  wired in WH** per the teardown's wiring plan and SYSTEMS-COVERAGE;
  not redone here.
- **No raw commercial files, no deploy.** This PR adds only
  `.js` / `.json` / `.md` files. No file is deleted or modified.

## A doc-only PR would not count here

This PR is not doc-only: the modules above are imported and asserted
by `test/frame-data-schema.test.mjs`, and the example data file is
parsed and validated by that test. The doc in this file is the
transfer record, not the deliverable.
