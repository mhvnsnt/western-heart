# mat-kings (WWF No Mercy) — Canon Conversion Log

**This file is the per-game source of truth for the No Mercy canon conversion**
(coordinator reconciles root CANON.md / RENAME-MAP.md from here at merge time).
Owner order 2026-10-20 ~08:06 CDT: wire everything, convert third-party identity to WH
canon, rename + lightly tweak animations/moves at industry standard, never break them.
Staging law: the proprietary layer is ADDITIVE — conversion never degrades wired function.
Full file checklist: `teardown/wwf-no-mercy/WIRING-INVENTORY.md`.

---

## 1. Universe rename — DONE

| Source identity | WH canon | Where applied |
|---|---|---|
| WWF No Mercy | `mat-kings` ("Kings of the mat", RENAME-MAP.md) | New move database universe field; this log; root CANON.md + RENAME-MAP.md No Mercy sections (appended 2026-10-20) |

The teardown folder itself keeps its path (`teardown/wwf-no-mercy/`) per owner law:
the No Mercy teardown folder STAYS in Western Heart. RENAME-MAP Phase 3 renames are
directory-level and remain a coordinator decision; nothing in this lane moves files.

## 2. Move / animation conversion — DONE (data layer)

New file: `moveset-library/movesets/mat-kings-move-database.json` — every animation in
the bank, joined programmatically from `animations/manifest.json` +
`tools/NoMercy-FileTableDB.txt` + `re-docs/docs/moves/move-database.md`:

| Item | Count | Conversion |
|---|---|---|
| Move clips | 4,409 | IDs renamed `NM-###` → `MK-####` (MK-0000 = anim_id 0 … MK-4408). Each entry: DB technique name, category, `anim_ref`, `nframes`. |
| System clips | 1,353 | Listed as `system_anims` with DB label + system role (stances, taunts, grapple positions, entrances…). |
| Unmanifested clips | 25 | Files 0x445B–0x4472 + 0x4C04 exist in the bank but not in `animations/manifest.json`; now catalogued explicitly in the database instead of being invisible. |
| Power data join | 507 entries | Power/KO/Bleed/Feature joined from `move-database.md` tables (251 unique documented move names; the md only documents Front Weak/Strong/Finisher categories — the rest have no power table anywhere in the teardown, so none was invented). |
| Tekken-style inputs | 4,153 entries | Federation rule applied at category level: weak grapples → `1+3`, strong grapples → `2+4`, special/finisher grapples → `f+2+4`, ground grapples → `1+3`/`2+4` vs grounded opponent, turnbuckle grapples → corner variants, weak arm strike → `1`, weak leg strike → `3`, strong strike → `2`, running attacks → `f,f+2`, flying → `u/f+2`/`u/f+3`, taunts → `1+2+3+4`, counters → `b+2`/`b+4`. |
| Slot eligibility | 1,966 entries | Mapped to `moveset-library/movesets/MOVE-SLOTS.json` slot names where the category matches a documented slot group. |

**What was NOT done to the animations:** no clip was re-timed, re-posed, or numerically
edited. The AKI→Tekken retarget exists as a proven pipeline on ONE clip
(`aki_to_tekken3_v2.json`, clip 0x339A on King, corrected bank); v1
(`aki_to_tekken3_v1.json`) was built on the misaligned pre-correction bank and is
superseded — do not consume it. Library-scale retarget is a flagged gap (see §6),
not silently skipped work: the .npy bank is wired as library data now, and playback
requires the retarget/loader step the anim lanes own.

**Move display names:** the database keeps the teardown DB's descriptive technique
names (Scoop Slam, Piledriver 01, Sharpshooter…). These are generic wrestling
technique names, not character IP. Two label families need an owner pass before any
proprietary rename (§6): persona-named moves (e.g. `[Back Special Grapple] Reverse
Tazzplex`, `[Front Special Turnbuckle Grapple] Misty Frankensteiner`) — no names were
invented for them here.

## 3. Data corrections found by the audit — FIXED in this PR

| Was | Evidence | Fix |
|---|---|---|
| `pantera-moveset.json` + `MOVE-DATABASE.json` (×2 copies): NM-001 "Scoop Slam" → `anim_3351.npy` | FileTableDB: `3351 = [Turnbuckle Attack] Front Kick 02`. The Scoop Slam clips are `339F` (P1) / `33A0` (P2). | anim_ref → `anim_339F.npy` (canon MK-0125); correction note embedded in pantera-moveset.json. |
| NM-002 "Arm Drag" anim_ref `null` | FileTableDB: `33A9/33AA = [Front Weak A Grapple] Arm Drag P1/P2`; power F matches md table. | anim_ref → `anim_33A9.npy` (MK-0135). |
| NM-003 "Piledriver 01" anim_ref `null` | FileTableDB: `33E1/33E2 = [Front Weak Grapple B] Piledriver 01 P1/P2`; power D matches. | anim_ref → `anim_33E1.npy` (MK-0191). |
| `ANIMATION-INDEX.json` categories | Move bank split into 6 equal contiguous ranges labeled strikes/grapples/submissions/high_flying/weapons/misc_moves; system categories overlap ranges and double-count (category lists sum to 5,932 vs 5,787 real clips). | Not rewritten here (shared index, other lanes consume it) — superseded for No Mercy by the label-true categories in `mat-kings-move-database.json`. Flagged in §6. |

## 4. Arenas / stages — WIRED, display names PENDING OWNER

All 17 assemblies are wired stages on main (`game/assets/stages/no-mercy/*.obj`,
`game/js/stages.js` ids `nm-*`, builder `buildNoMercy()`), with the GLB + gallery layer
in open PR #345. Their in-game display names still carry the source game's event
trademarks (`NO MERCY: RAW IS WAR`, `WRESTLEMANIA`, …) and `universe: 'WWF No Mercy (AKI)'`.
Renaming display strings lives in `game/js/stages.js`, which this lane does not edit
(engine lanes own it) — the conversion is staged here for the coordinator/engine lane.
**No WH names are invented in this table** (owner creates proprietary names):

| Stage id (already WH-neutral) | Source display name | WH canon name |
|---|---|---|
| `nm-arena-raw` | RAW IS WAR | AWAITING OWNER |
| `nm-arena-smackdown` | SMACKDOWN | AWAITING OWNER |
| `nm-arena-royal-rumble` | ROYAL RUMBLE | AWAITING OWNER |
| `nm-arena-wrestlemania` | WRESTLEMANIA | AWAITING OWNER |
| `nm-arena-king-of-the-ring` | KING OF THE RING | AWAITING OWNER |
| `nm-arena-summerslam` | SUMMERSLAM | AWAITING OWNER |
| `nm-arena-survivor-series` | SURVIVOR SERIES | AWAITING OWNER |
| `nm-arena-backlash` | BACKLASH | AWAITING OWNER |
| `nm-arena-armageddon` | ARMAGEDDON | AWAITING OWNER |
| `nm-arena-no-mercy` | NO MERCY | AWAITING OWNER |
| `nm-arena-cage` | STEEL CAGE | AWAITING OWNER |
| `nm-backstage-bar-lounge` | BACKSTAGE: BAR LOUNGE | AWAITING OWNER |
| `nm-backstage-boiler-room` | BACKSTAGE: BOILER ROOM | AWAITING OWNER |
| `nm-backstage-hallway` | BACKSTAGE: HALLWAY | AWAITING OWNER |
| `nm-backstage-locker-room` | BACKSTAGE: LOCKER ROOM | AWAITING OWNER |
| `nm-backstage-parking-lot` | BACKSTAGE: PARKING LOT | AWAITING OWNER |
| `nm-lobby` | THE LOBBY | AWAITING OWNER |

Suggested pattern for the owner's pass (not applied): keep the `mat-kings` frame —
the events become Western Heart's own mat-kings shows in the WH world.

## 5. Characters — NO CONVERSION APPLIED (owner decision required)

- `docs/wrestler-id-table.json` holds 42 wrestler internal IDs/names. RENAME-MAP.md
  maps **zero** No Mercy characters to WH names, and CANON.md + ROSTER.md define no
  mat-kings fighters. Per the federated design (`CHIMERA-ARCHITECTURE.md`), Western
  Heart consumes No Mercy's *systems and animations*, not its wrestler characters;
  the 10 wrestler models (13 GLBs) are ACCOUNTED-ELSEWHERE (wrestlemania-xix-mod
  `mods/no-mercy-wrestlers/`, Bannon, wrestling-game). **Flag:** if the owner wants
  mat-kings-native fighters, he names them; nothing was invented here.
- VPW2 note: the ROM bank includes Virtual Pro Wrestling 2 content (taunt sets etc.,
  AKI family). It is catalogued under its DB labels in the move database with
  provenance intact, inside the mat-kings library.

## 6. Flagged gaps (named reasons)

1. **Stage display names** — owner canon decision (see §4). Engine-lane edit also required.
2. **Wrestler identities (42)** — owner canon decision (see §5).
3. **Persona-named moves** — owner naming pass (see §2).
4. **Library-scale AKI→Tekken retarget** — format/pipeline gap with evidence: v2 proves
   1 clip; 5,762 clips await the retarget lane (PR #364 owns anim retargeting). Until
   then no No Mercy clip plays in-engine; grappling *feel* cannot be verified in a build.
5. **ANIMATION-INDEX.json range-chunk categories** — inaccurate for No Mercy (see §3);
   shared file, coordinator to decide replacement vs repair.
6. **CAW save-record layout** — blocked on a real emulator save dump
   (`CAW-SAVE-RECORD-STATUS.md`); ROM-side ID tables are wired, the save struct is not decodable from ROM alone.
7. **Grappling system in code** — design exists (`docs/grappling/UFC-GRAPPLING-DESIGN.md`,
   PR #147, docs-only, UFC-based, no No Mercy data cited at line level); `game/js/fighter.js`
   implements Tekken throws (1+3/2+4) only. No Mercy grapple *data* now reaches the
   moveset library with Tekken inputs (this PR); engine consumption is the engine lane's.
8. **`models/unlabeled/` (2,431 meshes)** — DB-unlabeled wrestler attire/costume meshes;
   not wired (federated design, §5). They stay in the teardown per owner law.
9. **Textures beyond CAW/stage** — titantron (314), character portraits (102), icons
   (103) and menu/UI categories are not consumed by any WH system yet.
10. **TEARDOWN.md staleness** — it claims 13 character GLBs inside `re-docs/assets/`
    and a labeled animations manifest; the current tree has neither (GLBs accounted-
    elsewhere, manifest has no labels). Doc correction is noted here, file left as-is
    for the coordinator.

## 7. Per-character isolation

This lane touched **shared library data only** (`moveset-library/`) and per-game records
(`teardown/wwf-no-mercy/`). No character's skeleton, animation set, or moveset file was
edited except `pantera-moveset.json`'s single anim_ref correction — Pantera's own file,
correcting Pantera's own move to the clip the FileTableDB proves is the Scoop Slam.
Fighters consume the mat-kings library through their own moveset JSONs (the Oct 14–15
Pantera pattern), so library additions cannot leak into any character's stance, pose, or
kit. **Deliberate parallels sharing:** none — no two characters were made to share
anything by this lane; the library is opt-in per character by design.
