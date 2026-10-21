# Soulcalibur II (Xbox) — Wiring Inventory, 2026-10-20

Per the teardown wiring standard (PR #397): every file ends **WIRED** with
path evidence or **FLAGGED** with a named reason. Decode record:
game-reverse-engineering, MODEL-HUNT phases 1–4 (PRs #26, #28, #30, and the
phase-4 PR stacked on #30). Container chain: `root.olk` → OLK sub-archives →
per-character bundles (v982) → VMX models.

## Character model bundles — v982 archive (ISO 0x3C27D000, 982 entries)

Character blocks are 39 files each, keyed by the XBE's FUN_00047440 table
(slot index = hex character tag in `CHARACTER-MAP.md`). P1 bundle = base+1.
Fighter VMX = vmx0 in each bundle; vmx1+ = weapon/extra VMXs (decoded,
GLBs in the game-reverse-engineering phase-4 PR, regenerable via its
tools). Fighter GLBs below are the placed bind-pose models (skinned +
rigid parts placed by proven node world matrices; sheet-class parts only
in the `_full` variants in the decode PR).

| Slot/Tag | Fighter | Entry | Model in this repo | Status |
|---|---|---|---|---|
| 01 | Mitsurugi | 47 | `teardown/soulcalibur-2/models/idx47_fighter_placed.glb` | FLAGGED — model decoded + import-verified (render viewed); not yet in roster: moveset JSON + animations pending (see Cross-cutting) |
| 02 | Seong Mi-na | 86 | `teardown/soulcalibur-2/models/idx86_fighter_placed.glb` | FLAGGED — same; render viewed, fully coherent |
| 03 | Taki | 125 | `teardown/soulcalibur-2/models/idx125_fighter_placed.glb` | FLAGGED — model decoded + import-verified; roster pending |
| 04 | Maxi | 164 | `teardown/soulcalibur-2/models/idx164_fighter_placed.glb` | FLAGGED — same |
| 05 | Voldo | 203 | `teardown/soulcalibur-2/models/idx203_fighter_placed.glb` | FLAGGED — same |
| 06 | Sophitia | 242 | `teardown/soulcalibur-2/models/idx242_fighter_placed.glb` | FLAGGED — same |
| 0b | Ivy | 281 | `teardown/soulcalibur-2/models/idx281_fighter_placed.glb` | FLAGGED — same |
| 0c | Kilik | 320 | `teardown/soulcalibur-2/models/idx320_fighter_placed.glb` | FLAGGED — same |
| 0d | Xianghua | 359 | `teardown/soulcalibur-2/models/idx359_fighter_placed.glb` | FLAGGED — same |
| 0f | Yoshimitsu | 398 | `teardown/soulcalibur-2/models/idx398_fighter_placed.glb` | FLAGGED — same (rigid-heavy model: 81 rigid parts) |
| 11 | Nightmare | 437 | `teardown/soulcalibur-2/models/idx437_fighter_placed.glb` | FLAGGED — same; render viewed; thigh/hip gap in placed GLB remains OPEN (sheet-class parts in `_full` do not form legible coverage — viewed) |
| 12 | Astaroth | 476 | `teardown/soulcalibur-2/models/idx476_fighter_placed.glb` | FLAGGED — same |
| 13 | — not in CHARACTER-MAP — | 749 | — | FLAGGED — bundle's vmx0 is a rigid-only model (82 nodes, 86 parts), not a standard fighter; identity + role unproven, not decoded as a fighter |
| 14 | Cervantes | 515 | `teardown/soulcalibur-2/models/idx515_fighter_placed.glb` | FLAGGED — model decoded + import-verified; render viewed, fully coherent; roster pending |
| 15 | Raphael | 554 | `teardown/soulcalibur-2/models/idx554_fighter_placed.glb` | FLAGGED — model decoded + import-verified; roster pending |
| 16 | Talim | 593 | `teardown/soulcalibur-2/models/idx593_fighter_placed.glb` | FLAGGED — same |
| 17 | Cassandra | 632 | `teardown/soulcalibur-2/models/idx632_fighter_placed.glb` | FLAGGED — same |
| 18 | — not in CHARACTER-MAP — | 788 | — | FLAGGED — vmx0 rigid-only (52 nodes, 102 parts, 10,662 tris); `_full` render viewed: incoherent plane stacks under fighter placement rules; not a standard fighter; identity + assembly path unproven |
| 19 | Necrid | 671 | `teardown/soulcalibur-2/models/idx671_fighter_placed.glb` | FLAGGED — model decoded + import-verified; bundle holds 6 VMXs (5 extra), roster pending |
| 1a | Yun-seong | 710 | `teardown/soulcalibur-2/models/idx710_fighter_placed.glb` | FLAGGED — model decoded + import-verified; render viewed, fully coherent; roster pending |
| 1d | Spawn | 944 | `teardown/soulcalibur-2/models/idx944_fighter_placed.glb` | FLAGGED — Xbox-source only (gate G4); render viewed; minor ankle-area scatter of small rigid parts recorded; roster pending |
| 1e | UNIDENTIFIED (per CHARACTER-MAP) | 827 | `teardown/soulcalibur-2/models/idx827_fighter_placed.glb` | FLAGGED — fighter decoded + import-verified; identity unproven in source data |
| 1f | UNIDENTIFIED (per CHARACTER-MAP) | 866 | `teardown/soulcalibur-2/models/idx866_fighter_placed.glb` | FLAGGED — same |
| 20 | UNIDENTIFIED (per CHARACTER-MAP) | 905 | `teardown/soulcalibur-2/models/idx905_fighter_placed.glb` | FLAGGED — same (rigid-heavy: 65 rigid parts) |

## Remaining v982 content (inventoried, not yet decoded)

| Class | Entries | Status |
|---|---|---|
| Costume trios beyond P1 (base+2, base+3, base+9..base+11 per slot) | ~120 entries incl. 438/439/446/447 | FLAGGED — numbering proven (G1 concordance, phase-4 doc §6); decode is mechanical via the shipped decoder, not yet run |
| Common/motion bundles (~2.6–2.8 MB series at block bases, +39 stride: 75, 114, 153, …) | ~20 entries | FLAGGED — animation source; motion format not yet decoded; blocks animation wiring |
| Motion/sound resources inside character bundles (types 1–0xd per FUN_00033fb0) | in-bundle | FLAGGED — resource table parsed in phase 2; contents not yet converted |
| Small entries (404 files 100–600 KB; 30 under 100 KB) | ~434 entries | FLAGGED — unclassified; no contents claimed (gate: probe before claims) |

## Other archives

| Content | Location | Status |
|---|---|---|
| Stages — v404 archive, 41 VMX models | game-reverse-engineering phase 2 | FLAGGED — vertex positions decoded + verified (m003 floor plan, own-eyes); face topology rescore + GLB assembly pending; stage registry entry pending |
| Textures — v516 archive (VXT containers) + per-VMX VXT sections | ISO / in-bundle | FLAGGED — VXT record decode not done; GLBs carry authored UVs but no texture images yet (gate G3 remainder) |
| Movesets — v33 archive, 24 command-list files | extracted phase 1 (`CHARACTER-MAP.md`) | FLAGGED — command lists extracted and fighters identified by move evidence; not yet converted to `moveset-library/` JSON with Tekken inputs (standard §4) |
| Audio — bgm.afs / movie.afs (CRI AFS) + bundle sound (type 0xc) | ISO | FLAGGED — standard container, not yet extracted |

## Cross-cutting blockers to "playable in the build"

1. **Animations**: motion bundles (above) must be decoded to clips and
   indexed before any SCII fighter can fight in-game. This is the single
   largest remaining piece.
2. **Moveset conversion**: v33 command lists → moveset-library JSON
   (Tekken inputs), per fighter.
3. **Skeleton/weights export**: current GLBs are bind-pose geometry;
   per-vertex bone data exists in the source streams (rec28 sections) but
   the bind matrices for the ~65 non-node bone ids are not yet derived
   (phase-4 doc §7.2), so no skeleton is embedded yet.
4. **Textures**: VXT decode (above).
5. **Canon conversion**: pending owner assignment — see
   `CANON-CONVERSION.md` in this folder. No canon names invented.

## Verification evidence (this wiring)

- Import-verify: every GLB listed above was imported in Blender 4.0.2
  (headless, Cycles) during the phase-4 lane; front renders of 7 fighters
  + the idx47 weapon were viewed by the lane author (verdicts in the
  phase-4 doc §4.3). GLBs that failed import would have failed the batch
  (zero failures over 50 VMXs).
- Independent re-verification (standard §5) has **not** been run on this
  inventory yet — it is a lane claim until the audit pass walks it.
