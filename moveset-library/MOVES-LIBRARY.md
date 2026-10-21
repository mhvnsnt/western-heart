# Western Heart — Moveset Library

**The complete moveset customization system.** Pick any animation from any game, assign it to any moveset slot, customize any character.

Built from the owner's directive: combine the full moveset customization of both wrestling games (WWF No Mercy + WWE WrestleMania XIX) with the full Tekken customization code — a complete moveset library like the wrestling games and Mortal Kombat, plus a full character creation suite like WWE + Tekken combined.

---

## Structure

```
moveset-library/
├── MOVES-LIBRARY.md          # This file
├── animations/
│   └── ANIMATION-INDEX.json  # 5,932 clips indexed by category across all games
├── movesets/
│   ├── MOVE-SLOTS.json       # 176-slot unified system (No Mercy layout + Tekken extension)
│   ├── MOVE-DATABASE.json    # Master move list skeleton
│   └── pantera-moveset.json  # Sample fighter moveset (template)
└── customization/
    └── CHARACTER-CREATION.md # Combined WWE CAW + Tekken customization suite
```

---

## The Two Modes

Western Heart has **two fighting modes**, and the moveset system serves both:

1. **Tekken Mode** — open-plane 3D fighting. Uses the `tekken_striking` slot group: jab strings, crouch dash, while-rising, throws, rage arts, stance transitions. Tekken moves are DATA not code (production-study law).

2. **Wrestling Mode** — ring/arena traversal. Uses the full No Mercy slot layout: grappling (front/back, weak/strong), ground, turnbuckle, ringside, apron, Irish whip, taunts, double-team.

Every fighter has the **same 176 slots**. What makes Pantera different from Demonio is which move fills each slot.

---

## Animation Sources

| Game | Clips | Format | Location |
|---|---|---|---|
| WWF No Mercy | 5,787 | NPY int16 (nframes, 26, 3), AKI 26-joint | `teardown/wwf-no-mercy/animations/clips/` |
| WWE WrestleMania XIX | 170 | JSON per clip, Yukes 70-bone | `teardown/wmxix/animations/` |
| Tekken 3 | 20 character banks + common | divmot (types 0-20, 99; type 15 absent from local disc image) | `teardown/tekken3/animations/` |
| Tekken 6 | — | Locked (PSP encryption) | 46 endings extracted |
| Urban Reign | motion pools | PPK/GYU | `teardown/urban-reign/ppks/` |

**Categories** (in `ANIMATION-INDEX.json`): stances, walks, entrances, taunts, getups, grapple_positions, misc_system, strikes, grapples, submissions, high_flying, weapons, misc_moves.

**Retargeting:** `teardown/wwf-no-mercy/aki_to_tekken3.py` maps AKI 26-joint to Tekken skeleton (v1 proven on King). AKI→Tekken7 retarget is the next step.

---

## Move Slots (176 total)

The slot system uses **No Mercy's exact layout** as the template — every input combination maps to a named slot, organized by position and context:

- **Grappling** (34 slots): front/back × weak/strong × 8 inputs + finishers + reversals
- **Standing** (20 slots): strikes, counters, running attacks, evasion
- **Tekken Striking** (30 slots): jab strings, crouch dash, while-rising, throws, rage, stances, homing, power crush
- **Ground** (16 slots): submissions and strikes vs downed opponents
- **Turnbuckle** (20 slots): corner grapples, tree-of-woe, flying attacks
- **Ringside/Apron** (18 slots): rope attacks, apron grapples, dives
- **Irish Whip** (6 slots): whip follow-ups
- **Taunt** (9 slots): standing, special, corner, celebration, entrance
- **Double-Team** (7 slots): co-op grapples and flying attacks

Full schema: `movesets/MOVE-SLOTS.json`.

---

## How to Build a Fighter's Moveset

1. Start from `movesets/pantera-moveset.json` (the template)
2. For each slot, pick a move from `MOVE-DATABASE.json` (or define a new `WH-###` original)
3. Each move entry: `{move_id, move_name, source, slot_eligibility, anim_ref, power, properties}`
4. `anim_ref` points to the animation clip (No Mercy: `anim_id = file_id - 0x3322`)
5. Save as `movesets/<fighter>-moveset.json`
6. Reference it from the character's creation-suite JSON

---

## Character Creation

See `customization/CHARACTER-CREATION.md` for the full combined suite:
- **Profile:** name, height, weight, music, titantron + soul/element/land
- **Appearance:** WWE CAW (14M+9F body types, 8 skin tones, 118 faces, 220 body parts, 2,431 attire meshes, 2,690 WMXIX edit_data files) + Tekken 4-slot layered items (Head/Upper/Lower/Other on bone sockets)
- **Moves:** assigned via this library
- **Fighting Style:** No Mercy AI tendencies + Tekken archetype
- **Parameters:** No Mercy 5-zone offense/defense + Tekken frame-data scaling

---

## Sources & Provenance

All reverse-engineered from real game data (chimera build method):
- No Mercy: ROM `WWF No Mercy (USA) (Rev-A).z64`, community re-docs, VPWStudio (MIT)
- WMXIX: ISO `WWE WrestleMania XIX (USA)`, YOBJ/YANM decoders written in-house
- Tekken 3: `TEKKEN3.BNS` via n0madic parser
- Tekken 6: PSP ISO, customization documented from public sources (models encrypted)
- Urban Reign: ISO via GitHub Release, PPK format probed in-house

---

## mat-kings move database (added 2026-10-20, No Mercy wiring lane)

`movesets/mat-kings-move-database.json` is the full No Mercy (mat-kings) library:
4,409 move clips + 1,353 system clips + 25 previously unmanifested clips, joined
from `teardown/wwf-no-mercy/animations/manifest.json`, the FileTableDB labels in
`teardown/wwf-no-mercy/tools/NoMercy-FileTableDB.txt`, and the power tables in
`teardown/wwf-no-mercy/re-docs/docs/moves/move-database.md` (507 entries carry
Power/KO/Bleed). Canon IDs are `MK-####`. Every move carries a Tekken-style
`tekken_input` and, where its category matches a slot group, `slot_eligibility`
into MOVE-SLOTS.json. Note: the category buckets in `animations/ANIMATION-INDEX.json`
are contiguous range chunks and overlap (they sum to 5,932 against 5,787 real
clips) — for No Mercy, prefer the label-true categories in the mat-kings database.
Per-game record: `teardown/wwf-no-mercy/CANON-CONVERSION.md`; full checklist:
`teardown/wwf-no-mercy/WIRING-INVENTORY.md`.

---

## Street Reign (Urban Reign) — wired 2026-10-21

- **Fighters:** all 72 Urban Reign character PPKs decoded to skinned GLBs
  (western-heart PR #429; completion gates G1–G5 pass — see
  `docs/urban-reign/URBAN-REIGN-GATES.md`), copied to
  `game/assets/models/street-reign/charNNN.glb` and registered in
  `game/js/assets.js` (`MODEL_URLS` keys `ur-char001`..`ur-char072`) and
  `game/js/roster-full.js` (bonus tier, ids `ur-char001`..`ur-char072`).
- **Game moveset today:** `game/assets/movesets/street-reign.json`
  (schema v2, `proxy: true`) — the WH engine base set whose values are
  copied from `game/js/fighter.js` built-ins. It is a placeholder for
  the UR-native movelists, labeled as such in the file itself.
- **Animation data:** indexed under source `urban_reign` in
  `animations/ANIMATION-INDEX.json` (status block `status_2026_10_21`):
  the .gyu sampler is cracked (SLUS_212.09 FUN_00292670/FUN_00299130,
  dequant tables at ELF 0x663ac0/0x663cc0/0x663ec8), `general_normal.gyu`
  holds 342 motions; conversion of the motion banks into game
  animation banks is the open follow-on, flagged per file in
  `teardown/urban-reign/WIRING-INVENTORY.md`.
- **Canon:** no per-fighter WH vessel mapping exists in canon for the
  UR roster — see `teardown/urban-reign/CANON-CONVERSION.md` (flagged,
  never invented). Universe name: `street-reign` (root `RENAME-MAP.md`).
