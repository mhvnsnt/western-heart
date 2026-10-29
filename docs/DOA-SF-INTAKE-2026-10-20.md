# DOA / Street Fighter Fighter Intake — 2026-10-20

**Owner order (2026-10-20 ~21:30 CDT):** get the Dead or Alive and Street Fighter
fighters into the game — in T-pose and wired up — so they can be replaced with
characters and renamed. Bass Armstrong first among equals: he is the base for
**Vain Abel Elias's later attires (5/6/7)**. Priority correction (~21:37 CDT):
the Bass conversion is the later-attire pipeline, not Attire-1 work — Vain
Abel's main attire stays his Tripo.

**Method:** consume what the teardowns and the repo already hold; convert what
is convertible with production tooling (DragonFF); render T-poses only where a
model is textured and assembled (no gray clay, per the standing
no-untextured-renders rule); verify everything with file evidence.

---

## 1. Bass Armstrong (DOA5) — CONVERTED ✔

Source held in-repo since PR #218:
`teardown/dead-or-alive-4/models/bass-armstrong/DOA5_Bass_Armstrong_Costume_1.zip`
— a GTA SA-format package: 4 DFF/TXD variants (bandana × glasses). Unusable
until converted; that conversion is now done.

**Conversion:** Blender 4.0.2 + DragonFF (the DFF importer already installed on
this box). Two load-bearing details, both proven by diagnostics:

- The DFF must be imported with **Read Material Split = ON**. With it off, all
  39,303 polygons land on material index 0 and the model exports with a single
  texture. With it on, faces distribute across all 13 materials.
- DragonFF parents the armature *to* the mesh; the glTF exporter then drops the
  skin. Fix: unparent the armature, parent the mesh to it
  (`parent_type = ARMATURE`), export with `export_apply = False`.

**Outputs** (in `teardown/dead-or-alive-4/models/bass-armstrong/converted/`):

| File | Variant | Materials | Images | Skin | Size |
|---|---|---|---|---|---|
| `bass_cos01_bandana_glasses.glb` | Bandana + glasses (his DOA5 COS01 look) | 13 | 12 | 1 (32 bones) | 3,314,984 B |
| `bass_cos01_plain.glb` | No bandana, no glasses (clean face — the reskin base) | 11 | 11 | 1 (32 bones) | 3,334,144 B |

Both GLBs were re-imported fresh and verified (mesh, materials, embedded
textures, skin all present). The remaining two zip variants (bandana-only,
glasses-only) convert by the identical recipe whenever an attire slot wants
them.

**T-poses** (in `docs/tpose-refs/bass-armstrong/`, rendered with the repo's
`tpose_render.py` extended for GTA bone names, Workbench FLAT + TEXTURE,
2048×2048, pure white): `p1_front.png` (bandana+glasses), `p2_front.png`
(plain). Both viewed own-eyes: fully textured, front-facing, arms horizontal.
Margin check on p1: 109/109/172/172 px (spec ≥ 40), corners #FFFFFF.

**Role:** these are the model source for Vain Abel Elias **Attires 5/6/7**
(owner correction 2026-10-20 ~21:37 CDT). Roster wiring of those slots belongs
to the attire/auto-rig lanes; the models and refs are ready for them here.

## 2. Vain Abel — moveset + chokeslam VERIFIED ✔ (no changes)

`game/assets/movesets/vainabel.json` on main, checked field by field:

- 44 moves / 8 strings / 5 specials; `tekken_base` = "Bass Armstrong".
- 42 of 44 moves carry `doa_source: bass-armstrong` with `doa_move` names
  matching `teardown/dead-or-alive-4/movesets/bass-armstrong/BASS-MOVELIST.md`
  (41 distinct DOA move names; Palm Jab, Triple Jab, Bass Lariat, Powerbomb,
  Manhattan Driver, Falcon Arrow, Front Facelock all present).
- **The custom chokeslam is in the wired data:** `moves["1+4"]` =
  "Elias Brothers' Chokeslam [WH SIGNATURE]" — `wh_original: true`,
  `move_class: signature`, throw/grab/unblockable, damage 24,
  `anim_ref: wh:vainabel:sig:elias-brothers-chokeslam`, throw break 1+2.
  (Bass has no chokeslam by name; this is the grafted WH signature, as
  designed. Bass's own slam-class throws — Powerslam, Powerbomb, Manhattan
  Driver — are also present as themselves.)
- Wired: `vainabel` is in `game/js/movesets.js` MOVESET_IDS.
- The companion set `game/assets/movesets/doa-bass.json` (20 moves, the pure
  Bass list) is likewise wired (`doa-bass` in MOVESET_IDS).

**Note for the moveset-merge lane:** this intake lane added NOTHING to any
moveset file. `vainabel.json` and `doa-bass.json` are untouched; the merge's
no-loss union already contains the chokeslam via current main.

## 3. DOA intake table

| Fighter | Moveset (wired) | Model | Textures | T-pose | Missing / blocker |
|---|---|---|---|---|---|
| Bass Armstrong (DOA5) | ✔ vainabel + doa-bass | ✔ converted GLBs (§1) | ✔ embedded | ✔ p1/p2 | Attire-slot wiring (attire lanes) |
| Kasumi (DOA4) | ✔ doa-kasumi | geometry pool only | ✗ XPR2 carved, unconverted | ✗ | Assembly (below) |
| Ayane (DOA4) | ✔ doa-ayane | geometry pool only | ✗ | ✗ | Assembly |
| Ryu Hayabusa (DOA4) | ✔ doa-hayabusa | geometry pool only | ✗ | ✗ | Assembly |
| Tina Armstrong (DOA4) | ✔ doa-tina | geometry pool only | ✗ | ✗ | Assembly |
| Jann Lee (DOA4) | ✔ doa-jannlee | geometry pool only | ✗ | ✗ | Assembly |
| Rest of DOA4 cast | ✗ no converted movelist yet | geometry pools | ✗ | ✗ | Assembly + movelist conversion |

**DOA4 model state (evidence):** 165 triangulated GLBs sit on main under
`teardown/dead-or-alive-4/models/triangulated/` (chrone 30 / chrtwo 68 /
chrthree 56 / mot 11). Verified by parsing `chrone_00` directly: 1 mesh,
**0 images, 0 textures, 0 materials, 0 skins** — geometry only. The merged
sweep audit (`teardown/dead-or-alive-4/SWEEP-AUDIT-2026-10-20.md`) states the
meshes are **unassembled per-part pools in local space**; they form a character
only via the MdlGeo/ObjGeo skeleton transforms, which are unparsed. Textures
exist as 219 carved XPR2 on the GitHub release `doa4-xpr2-carved-v1`, not
converted. Per-fighter index mapping for chrone/chrtwo/chrthree is not yet
established in any doc. **Blocker, owned by the teardown sweep:** AFS keystream
+ skeleton-transform parsing (assembly); PR #386 (the import-repaired GLB set)
is still open. No DOA4 T-pose can be rendered until assembly lands — anything
rendered now would be untextured parts, which this intake will not ship.

**DOA6:** docs only in WH (`teardown/dead-or-alive-6/TEARDOWN.md`,
`DOA6-MECHANICS.md`). No DOA6 models in the WH tree; the DOA6 pull is a
separate lane's work.

## 4. Street Fighter intake table

| Fighter | Moveset file | Model | T-pose | Status |
|---|---|---|---|---|
| Ryu / Ken / Chun-Li / Guile / Dhalsim / Zangief / Blanka / Sagat / Vega / M. Bison / Cammy / Akuma | ✔ `game/assets/movesets/sf-*.json` (12 files) | guest rips for Zangief/Vega/Iori/Blanka/Armor King wired as fighters | Vega + Iori done (owner has Tripos); Zangief covered by Kronos | Per owner 2026-10-20: no re-renders for these |
| SF EX cast (EX2 Plus) | ✗ | ✗ nothing extracted | ✗ | **Blocked on extraction** |

**SF EX evidence:** `mhvnsnt/game-reverse-engineering` holds only the EX2 Plus
game bundle (`street-fighter-3d-games/extracted/ex2-plus/`) — no extracted
fighter models anywhere. The PAC decode + Ghidra pipeline is the teardown
sweep's SF EX lane; **the blocker for SF EX intake is that extraction**, named
here for the sweep. This lane does not duplicate it.

## 5. Kane Abel (Cain Elias) — already in, verified ✔

Vain Abel's brother, the Undertaker archetype. Status checked on main:

- **Model:** two Tripo attires wired 2026-10-19 —
  `roster/cain-elias/attires/attire1/model.glb` ("Biker") and attire2
  ("Fight Gear"). He is NOT waiting on a wrestling-teardown rip: the No Mercy
  / WMXIX libraries hold no standalone Undertaker GLB (the WMXIX repo's 13
  No Mercy GLBs are 10 other wrestlers). Undertaker *source material* does
  exist in the WH No Mercy teardown as CAW parts + textures
  (`Face_Male_03_Undertaker_1D76`, gloves/boots/portrait) if a teardown-built
  attire is ever wanted.
- **T-poses:** done — `docs/tpose-refs/cain-elias/a1_front.png` +
  `a2_front.png` (own-eyes verified by the wiring lane).
- **Moveset:** `game/assets/movesets/cainelias.json` — 41 moves,
  `tekken_base` "Undertaker (WWE)", `proxy: true`, and it IS in MOVESET_IDS
  (Stream 6). Undertaker-style signatures present: Tombstone Piledriver,
  Last Ride, **Chokeslam**, Hell's Gate, Old School. Per
  `roster/cain-elias/ATTIRE-SLOTS.md`, the moveset lane's standing pick for his
  long-term source is **Glen Kluger (Urban Reign)** — the "Glenn" the owner
  referred to; the brothers are a matched set (Vain Abel = Kane-based,
  Kane Abel = Undertaker-based, Elias Brothers' Chokeslam on Vain's side,
  Chokeslam signature on Cain's side).

## 6. What this intake did NOT do

- No moveset file was created, edited, or rewritten (merge lane's territory).
- No DOA4/SF EX extraction was started (teardown sweep's territory) — the two
  blockers above are named for it instead.
- No gray-clay or unassembled render was produced or shipped.
