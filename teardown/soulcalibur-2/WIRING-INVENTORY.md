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
| Stages — v404 archive, 41 VMX models | game-reverse-engineering phase 2 | PHASE 13: 39/41 assembled as textured GLBs in `stages/` (940,586 verts, 791,524 tris, 1,795 embedded images; per-part topology measured strip-vs-list; m003 = 35,390 verts, matches the phase-2 verified total; arena render viewed). FLAGGED: m000 (VMX version 2, 36 B part records, shared streams — v2 loader path not yet read) and m120 (VMX version 3, sentinel stream-end) not assembled; see `STAGES.md` |
| Textures — v516 archive (VXT containers) + per-VMX VXT sections | ISO / in-bundle | PHASE 13: **VXT DECODED** (`VXT-FORMAT.md`) — DXT1/3/5 stored linear, P8 paletted stored Xbox-swizzled; all 22 fighters textured with embedded images (`TEXTURED-MODELS.md`, `models-textured/`, 559 images, 886/891 meshes; the 5 exceptions are source color-only materials). v516 standalone containers censused (`CENSUS-PHASE13.md`), not decoded — no consumer needs them yet |
| Movesets — v33 archive, 24 command-list files | extracted phase 1 (`CHARACTER-MAP.md`) | FLAGGED — command lists extracted and fighters identified by move evidence; not yet converted to `moveset-library/` JSON with Tekken inputs (standard §4) |
| Audio — bgm.afs / movie.afs (CRI AFS) + bundle sound (type 0xc) | ISO | PHASE 13 census (`CENSUS-PHASE13.md`): bgm.afs = 76 ADX entries (48 kHz stereo, probed header) — standard, decodable, not yet extracted; movie.afs = 3 MPEG-PS entries (402 MB / 17 MB / 20 MB, probed) — standard, not yet extracted; bundle type-0xc payload format unprobed |

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
4. **Textures**: VXT decode (above). — RESOLVED phase 13 (see the
   Phase 13 section at the end of this file).
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

## Phase 5 update (2026-10-20, later) — skeletons/weights + movesets landed

Decode record: game-reverse-engineering phase-5 doc (MODEL-HUNT-PHASE5),
stacked PR on the phase-4 PR #31.

### Skinned models (replaces the phase-4 bind-pose-only status)

All 22 fighter GLBs now exist as **skinned** exports in
`teardown/soulcalibur-2/models-skinned/idxNNN_skinned.glb` (JOINTS_0 /
WEIGHTS_0, one joint per solved bone, inverse bind matrices). The skinning
model is proven by direct solve against the file's own src/dst streams
(residual max <= 2e-05 for 21/22 fighters; exported-GLB reproduction
verified per fighter, 0 bad verts except idx827: 1 of 3,549). The
bind-pose `models/` GLBs from phase 4 remain as the unskinned reference.

| Entry | Fighter (source) | Bones | Verts | Solve res max | Status |
|---|---|---|---|---|---|
| 47 | Mitsurugi | 147 | 3,777 | 1.5e-07 | WIRED (data) — skinned GLB + moveset JSON landed; roster blocked §below |
| 86 | Seong Mi-na | 164 | 3,982 | 1.2e-07 | WIRED (data) — same |
| 125 | Taki | 155 | 4,182 | 1.6e-07 | WIRED (data) — same |
| 164 | Maxi | 170 | 3,909 | 1.0e-05 | WIRED (data) — same |
| 203 | Voldo | 106 | 4,322 | 1.4e-07 | WIRED (data) — same |
| 242 | Sophitia | 181 | 4,207 | 3.4e-07 | WIRED (data) — same |
| 281 | Ivy | 147 | 3,720 | 1.0e-07 | WIRED (data) — same |
| 320 | Kilik | 165 | 4,757 | 2.3e-07 | WIRED (data) — same |
| 359 | Xianghua | 161 | 5,056 | 1.7e-07 | WIRED (data) — same |
| 398 | Yoshimitsu | 58 | 2,516 | 1.4e-07 | WIRED (data) — same |
| 437 | Nightmare | 105 | 2,214 | 4.0e-06 | WIRED (data) — same |
| 476 | Astaroth | 96 | 3,941 | 1.9e-07 | WIRED (data) — same |
| 515 | Cervantes | 159 | 4,253 | 2.2e-06 | WIRED (data) — same |
| 554 | Raphael | 168 | 4,301 | 1.7e-07 | WIRED (data) — same |
| 593 | Talim | 168 | 4,634 | 4.6e-06 | WIRED (data) — same |
| 632 | Cassandra | 187 | 4,406 | 1.9e-07 | WIRED (data) — same |
| 671 | Necrid | 101 | 3,608 | 2.7e-06 | WIRED (data) — same |
| 710 | Yun-seong | 157 | 4,524 | 1.7e-07 | WIRED (data) — same |
| 827 | UNIDENTIFIED (1e) | 107 | 3,549 | 1.9e-03 | FLAGGED — section-3 segmentation approximate (decode doc §1.4); GLB landed with flag |
| 866 | UNIDENTIFIED (1f) | 87 | 3,491 | 7.5e-07 | WIRED (data) — same |
| 905 | UNIDENTIFIED (20) | 74 | 2,412 | 9.0e-07 | WIRED (data) — same |
| 944 | Spawn | 102 | 2,538 | 2.0e-05 | WIRED (data) — same |

Pose proof (idx47): Blender renders viewed — bind pose coherent;
bone_12 (hip) +55 deg rotation deforms the hip/sash mass coherently
(rigid-pair drift 2.5e-10 in the numeric test). Decode PR §1.3.

### Movesets (new)

24 v33 command-list files converted to `moveset-library/movesets/
scii-<tag>-<name>.json` — 5,915 command records with source keys, SC2
input tokens, mechanical Tekken-input conversion (logged in
CANON-CONVERSION.md), and raw record fields in hex. Includes Link (1b)
and Heihachi (1c) guest lists present in the Xbox build (data only, no
models in the Xbox v982 fighter set for 1b/1c beyond their movesets).
FLAGGED: display-name pairing table (type-8/10 sections) not yet
decoded — display strings ride in file order under `display_strings`.

### Still blocking "playable in the build" (updated)

1. **Animations** — motion format NOT decoded (phase-5 probe: entry 75
   is dense binary with no VMX/strings; bundle load transform +
   motinfo.olk + track format are the named blockers, decode doc §3).
2. **Canon assignment** — owner-pending (CANON-CONVERSION.md); roster
   registration (game/js/roster-full.js, game/js/assets.js) needs it.
3. **Game-format movesets** — game/assets/movesets schema v2 needs
   frame/damage data from the undecoded cmd-record fields + pairing
   table + motion data.
4. **Textures** — RESOLVED phase 13 (VXT decoded; fighters + stages
   textured with embedded images).

## Phase 13 update (2026-10-21) — VXT textures + stages

Lane record: `PHASE13-STATE.md`; format: `VXT-FORMAT.md`; fighters:
`TEXTURED-MODELS.md`; stages: `STAGES.md`; census: `CENSUS-PHASE13.md`.
Motion/composition/clips untouched (capture gate, GRE PR #40).

| Class | Decoded | Wired | Left before playable |
|---|---|---|---|
| Textures (per-VMX VXT) | YES — DXT1/3/5 linear + P8 swizzled/palette; mapping pointer-proven (part → rec80 material → VXT record) | 22/22 fighters textured GLBs in `models-textured/` (559 embedded images, 886/891 meshes; 5 idx905 meshes are source color-only); 39 stage GLBs textured (1,795 images) | Secondary material texture layer (rec80 +0x0c) not assigned — runtime role unproven; v516 standalone containers censused only |
| Stages (v404) | 39/41 assembled (940,586 verts, 791,524 tris; topology measured per part) | GLBs in `stages/` with embedded textures; m003 render-verified against the phase-2 position proof | m000 (VMX v2 layout) + m120 (VMX v3 sentinel) unassembled — loader-path reads named in `STAGES.md`; stage registry/roster hookup is game-side work |
| Costumes (v982 variants) | Census only (`CENSUS-PHASE13.md`): variant model bundles at base+2/+3/+9/+10/+11 per slot, P1 size class | Not wired | Decode is mechanical via the existing VMX pipeline (same format as P1); not run this phase |
| Audio | Census: bgm.afs 76 ADX entries (48 kHz stereo, probed); bundle type-0xc unprobed | Not wired | ADX extraction (standard tooling) + type-0xc payload probe |
| Video | Census: movie.afs 3 MPEG-PS entries (probed) | Not wired | MPEG extraction (standard tooling) |

### Still blocking SCII true 100% after phase 13

1. **Animations/motion** — unchanged: gated on the parent lane's
   dynamic emulator capture (GRE PR #40); this lane did not touch it.
2. **Canon assignment** — owner-pending (`CANON-CONVERSION.md`,
   untouched by this lane).
3. **Game-format movesets** — frame/damage fields + pairing table +
   motion data (unchanged from phase 5).
4. **Stage exceptions** — m000 (v2) and m120 (v3) assembly, per
   `STAGES.md`.
5. **Costume-variant decode** — mechanical, unrun.
6. **Audio/video extraction** — standard formats, unrun (census done).
