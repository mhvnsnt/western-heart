# Soulcalibur II (Xbox) — FINAL STATE (Teardown Closeout, Phase 17)

This document is the standalone closeout for the Soulcalibur II
teardown. It states what is at 100%, what is capture-gated, what
is closed-unproven, and what waits on the owner — with the proof
pointers for each. Per-phase detail lives in `PHASE13-STATE.md`
through `PHASE17-STATE.md` in this folder; the decode corpus lives
in the game-reverse-engineering repo (GRE) PRs #26–#40.

**Sweep status (phase 17): SCII teardown-side COMPLETE.** Every
statically decodable class has been decoded, gated, and shipped.
The only remaining items are a parent-lane dynamic capture
(motion), a dynamic draw-time probe (rec80), a closed middleware
codec (mmx), and owner canon assignment. None of them blocks any
other SCII work.

Source: Soulcalibur II, **Xbox** version (XISO; the disc was first
misidentified as PS2 — see `XBOX-EXTRACTION-REPORT.md`). Guest
fighter in this build: Spawn. Link (GC) and Heihachi (PS2) exist
in the data as movesets only.

---

## (a) AT 100% — static, shipped

### Container chain + extraction
XISO → `root.olk` (Namco OLK; entry quads, descriptor
pseudo-entries, 0x800 alignment) → 4 sub-archives: **v33**
(movesets, 34 entries), **v404** (stages, 405), **v516**
(textures, 517), **v982** (character bundles, 983). Full
extraction: 1,097 files, byte totals match archive spans
(`XBOX-EXTRACTION-REPORT.md`; extractor in GRE, WH PR #154
extract + release `soulcalibur2-xbox-extract-v1`). XBE anchor
tables: FUN_00047440 (character file-number table) and
FUN_00033fb0 (bundle resource loader; resource type = section
index — the key that identified the in-bundle sound, below).

### VMX / VXT formats
- **VMX** (models): part records (40 B; stage variants v2 = 36 B
  records / shared streams, v3 = sentinel-terminated stream),
  400 B node records with file 4×4 matrices, rec28 skin sections
  (src/dst streams), rec80 material records. Spec + proofs:
  GRE PR #28, `PHASE14-STAGE-LAYOUTS.md`, `tools/build_skinned.py`,
  `tools/build_rigid.py`, `tools/build_placed.py`,
  `tools/build_stage.py` / `tools/build_stage2.py`.
- **VXT** (textures): DXT1/3/5 stored linear; P8 paletted stored
  Xbox-swizzled (indices + BGRA palette). Spec: `VXT-FORMAT.md`;
  decoder `tools/vxt_decode.py`. Fighter↔texture mapping is
  pointer-proven, not guessed: part → rec80 material → +0x08
  primary VXT record (159/159 pointer-exact across 635 materials).

### Fighters — 22, in three sets, ALL with the fixed reader
The fixed reader is `tools/build_skinned.py` as corrected in
phase 15: rigid vertex streams start at rec[5]; the phase-4 "+8
shift" for trailer-span parts (span = count×40 + 8) was a misread
that silently DROPPED those parts (the phase-3/4 "sheet class"
never existed — the parts are armor/equipment plates). Phase 16
re-decoded the skinned + textured sets; phase 17 re-decoded the
placed set through the placement path (`tools/build_placed.py`).

| Set | Files | Parts | Embedded images |
|---|---|---|---|
| `models/` placed (rigid, no skins) | 22 | **1,081** (891 pre-fix) | 0 (by design — UVs + vertex colors carried) |
| `models-skinned/` | 22 | **1,081** (891 pre-fix) | 0 |
| `models-textured/` base | 22 | **1,081** (891 pre-fix) | **601** (559 pre-fix) |
| `models-textured/variants-*/` | 83 | **3,631** | **2,155** |

Recovery reconciled exactly: the phase-15 census (725 rigid parts
/ 25 bundles) holds 255 trailer-span parts = 190 (22 P1 bundles)
+ 7 (idx283) + 7 (idx291) + 51 (idx789); the 80 costume bundles
carry +597 more of their own. Per-file gates (all phases): every
old part present with identical accessor bytes, identical skin
joint set where applicable, all normals finite, textured images
≥ old. Nightmare's phase-3 "thigh gap" is CLOSED in every set —
the dropped parts were his cuisses and leg/cuirass/helmet plates
(renders viewed: `phase16-proof/`, `phase17-proof/`).

### Stages — 41/41
All 41 v404 stage VMXs assembled as textured GLBs in `stages/`:
1,446,731 GLB verts / 811,243 tris / 1,879 embedded images,
including the two format exceptions — m000 (VMX v2) and m120
(VMX v3) — resolved in phase 14 (`STAGES.md`,
`PHASE14-STAGE-LAYOUTS.md`; arena/plan renders viewed,
`phase14-proof/`). m003 = 35,390 verts, exactly the phase-2
verified total.

### Costume variants — 83/83
Every v982 costume bundle decoded skinned + textured with the
fixed reader (table above), per-fighter under
`models-textured/variants-idx<P1>-<slug>/`, including Ivy
idx283/idx291 (phase 15 solver-reader fix) and idx789 via the
rigid path (`tools/build_rigid.py`). Census: `CENSUS-PHASE13.md`
(83/83 accounted, phase-16 section).

### Audio + video
- **Audio:** `bgm.afs` — 76/76 CRI ADX entries decoded losslessly
  to FLAC (48 kHz stereo, 73.8 min total; vgmstream-cli r2117).
- **Video:** `movie.afs` — 3/3 MPEG-PS entries byte-carried
  (402 / 17 / 20 MB) + probed.
- Both ship in GitHub release **`scii-phase14-av`** (79 assets)
  with the sha256 manifest `PHASE14-AV-MANIFEST.json` in git.
  **Pull-back proof:** `bgm-09.flac` and `movie1.mpg` were
  re-downloaded from the release and hash-verified against the
  manifest (2026-10-22; `PHASE14-AV-INVENTORY.md`).

### Moveset command records
24 v33 command-list files → `moveset-library/movesets/scii-*.json`:
**5,915 command records verbatim** (source keys, SC2 input tokens,
raw record fields in hex), with the one mechanical input
conversion SC2→Tekken (A→1, B→2, K→3, G→G; numpad directions
shared) logged in `CANON-CONVERSION.md` (phase-5 addition). The
set includes the Link (1b) and Heihachi (1c) guest lists present
in the Xbox build. **Residual, stated plainly:** the display-name
pairing table (type-8/10 sections) is not decoded — display
strings ride in file order under `display_strings` — and the
frame/damage fields inside the command records are not decoded;
the game-format moveset schema v2 waits on those two plus motion
data (below).

### Skeleton / skin + composition math corpus (GRE PRs #26–#40)
Per-bone bind matrices are SOLVED from the file's own src/dst
streams (sections 0–2 fixed grouping; section 3 segmented by
dynamic programming): solve residual max ≤ 2e-05 for 21/22
fighters, exported-GLB skinning reproduction verified per
fighter. **The recurrence finding, stated plainly:** a fighter's
pose is a proven recurrence over runtime state — the static
streams determine the bind pose and the skinning math exactly,
but posed frames are produced by the runtime evaluating that
recurrence; no static re-derivation of posed animation exists,
which is why motion is capture-gated (next section), not
"undecoded".

---

## (b) CAPTURE-GATED

1. **Animation / motion composition.** The pose recurrence above
   must be observed running. The capture route is an xemu
   (Xbox emulator) dynamic capture run by a parent lane (GRE
   PR #40); the capture spec exists in the GRE PHASE11 /
   PHASE12 state docs. Static routes were proven exhausted in
   phases 10–12. Nothing in this folder blocks that capture.
2. **rec80 secondary-texture draw-time binding.** Proven
   statically (phases 14–15): rec80 +0x0c is a genuine second
   texture reference (pointer-exact), relocated beside the
   primary at runtime (FUN_00025080), and every referenced VXT
   record is created/uploaded at load (FUN_00025300) —
   **created-and-held**. No draw-time stage/sampler binding was
   found in the functions read, so a visible secondary layer is
   NOT proven; GLBs ship the primary layer only. Closing this
   needs dynamic (draw-time) observation, same capture family
   as motion.

## (c) CLOSED-UNPROVEN

**The `mmx` waveform codec (in-bundle character sound).**
Container and registration are fully mapped (phase 15,
`PHASE15-PROBES.md` job 4): bundle resource type = section index
(FUN_00033fb0); type 0xc = section 12 = character sound; payload
= CRI `mmx` sound-bank container (magic + own total size, XHDp
sub-bank at +0x40, registered by FUN_000ed4d0 → FUN_000ed440;
type 0x02 is the smaller name-voice `mmx`). The waveform codec
inside the `mmx` entries is CRI middleware IP: no ADX frames are
present, and vgmstream rejects both the container and sub-bank
slices. Identification is complete; extraction is closed unless
a CRI-middleware decode becomes available. (This is separate
from `bgm.afs`, which is standard ADX and fully extracted.)

## (d) OWNER-PENDING

**Canon assignment for all SCII identities** — `CANON-CONVERSION.md`
(untouched by every teardown lane): no Western Heart canon names
have been assigned for any SCII fighter; all rows are PENDING
owner assignment, including tags **1e / 1f / 20** (unidentified
in source data), **Spawn** (tag 1d, Xbox guest), the **idx789
golem** (rigid-only slot at entry 788 — a rocky segment golem
with a rune-orb torso core, no identity in source data), and
**idx905** (tag 20's P1 bundle). Until assignment, fighters are
stored under source names as teardown reference data and are not
registered in the game roster.

## (e) KNOWN ARTIFACTS

1. **idx632 (Cassandra) truncation-tail weights:** in the base
   skinned/textured GLBs, JOINTS_0/WEIGHTS_0 bytes differ from
   the pre-fix build on exactly 2 of 4,406 verts, only in
   >4-influence truncation-tail slots carrying weights
   2.1e-09…3.9e-09 — skinning effect ≤ 4e-09, numerically
   negligible; POSITION/NORMAL/INDEX bytes are identical for
   every part. Characterized in `PHASE16-STATE.md`; no action.
2. **m120 stage ships as its stored sphere:** the VMX v3 entry's
   single part is a unit sphere (401 verts, 760 tris, uniform
   white vertex colors, 0 images) — that is what the source bytes
   contain, and it is shipped exactly as stored (`STAGES.md`
   phase-14 section; renders viewed).
3. **idx827 (tag 1e) section-3 segmentation is approximate**
   (solve res max 1.9e-03 vs ≤ 2e-05 elsewhere): the GLB is
   landed with that flag in `WIRING-INVENTORY.md`; it is a
   solver-segmentation flag on one unidentified fighter, not a
   geometry error.

## (f) Full PR stack for SCII

Western Heart (this repo, stacked in order):
- **#406** — wiring: placed + skinned GLBs, movesets, inventory,
  canon-conversion doc (`scii-wiring-phase4-20261020`)
- **#492** — phase 13: VXT textures + stages 39/41 + census
- **#519** — phase 14: stages 41/41, costume variants, AV release
- **#562** — phase 15: Ivy/idx789 fix (the fixed reader), probes
- **#571** — phase 16: full re-decode with the fixed reader
  (skinned + textured + variants)
- **#573** — phase 17: placed-set re-decode + this closeout

game-reverse-engineering (decode corpus):
- **GRE PRs #26–#40** — container chain, VMX/VXT formats, stage
  streams, placed + skinned decode, skeleton/skin solve, moveset
  files, and the motion/composition math with the PHASE11 /
  PHASE12 capture specs.

Per-phase records in this folder: `PHASE13-STATE.md`,
`PHASE14-STATE.md`, `PHASE15-STATE.md`, `PHASE16-STATE.md`,
`PHASE17-STATE.md`; inventories: `WIRING-INVENTORY.md`,
`CENSUS-PHASE13.md`, `CHARACTER-MAP.md`, `STAGES.md`,
`TEXTURED-MODELS.md`, `VXT-FORMAT.md`,
`PHASE14-AV-INVENTORY.md` + `PHASE14-AV-MANIFEST.json`,
`PHASE14-PROBES.md`, `PHASE15-PROBES.md`.
