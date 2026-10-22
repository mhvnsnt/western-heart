# Soulcalibur II (Xbox) — Phase 14 State: Stage Exceptions + Costume Variants + Audio/Video

Lane: TEARDOWN COMPLETION SWEEP, Phase 14. Stacked on PR #492
(`scii-phase13-textures-stages` @ 46ad614e, OPEN, base
`scii-wiring-phase4-20261020`). Branch: `scii-phase14-stages-costumes-av`.
Workdir: `~/workspace/scii-work/p13/` reused (sparse clone `wh/` + 22
fetched P1 bundles + work dir). Banned file NOT touched:
`~/workspace/scii-work/p2/v982_idx47.bin`.

## Out of scope (hard gate)

Motion is OUT OF SCOPE (capture-gated, GRE PR #40). Canon assignment is
OWNER-pending — no identities invented. `CANON-CONVERSION.md` untouched.

## Jobs

1. **m000 + m120 STAGE ASSEMBLY** — read VMX v2/v3 loader paths in the
   XBE (Ghidra project `~/workspace/ghidra-projects/soulcalibur2/`,
   JAVA_HOME=/home/hatch/workspace/tools/ghidra/jdk-21.0.12.1+1),
   pin layouts, assemble with per-part normal-agreement topology,
   textured via proven VXT route; renders viewed.
2. **COSTUME-VARIANT DECODE** — v982 variants censused in phase 13
   (base+2/+3/+9/+10/+11 per slot), run VMX→skinned-GLB + VXT pipeline
   per variant; per-fighter isolation under `models-textured/`.
3. **AUDIO/VIDEO EXTRACTION** — bgm.afs 76 ADX → WAV/FLAC via
   vgmstream (pull-in: vgmstream-cli r2117 already on disk at
   `~/workspace/tools/vgmstream/vgmstream-cli`, industry-standard ADX
   decoder); movie.afs 3 MPEG-PS probed, byte-carried; inventories +
   GitHub release + sha256 manifests + pull-back verify.
4. **PROBES** — (a) rec80 secondary texture layer runtime role;
   (b) in-bundle type-0xc sound payload format census. → PHASE14-PROBES.md
5. **WIRING-INVENTORY.md** updated per class.

## Inherited truth (phases 1–13, verified — not re-derived)

- 22 fighters textured GLBs (559 images, 886/891 meshes); VXT spec in
  `VXT-FORMAT.md`; decoder `tools/vxt_decode.py`.
- Stages 39/41 in `stages/` (940,586 verts, 1,795 images; m003 =
  35,390 verts exactly). Exceptions: m000 = VMX v2 (36 B part records,
  58 shared streams, no v4 stream-end word); m120 = VMX v3
  (stream-end = 0xFFFFFFFF sentinel). See `STAGES.md`.
- Census (`CENSUS-PHASE13.md`): v982 variants per slot; v516 = 371
  non-empty VXT entries (206.1 MB); bgm.afs = 76 ADX (48 kHz stereo);
  movie.afs = 3 MPEG-PS (402/17/20 MB).

## Status log

- 2026-10-22 ~01:04 CDT — lane start. Branch created from 46ad614e;
  this state doc is the first commit; PR opened immediately after.
- Pull-in log: vgmstream-cli r2117 (`~/workspace/tools/vgmstream/`) —
  already on disk, used for JOB 3 ADX decode (no new download).
