# Soulcalibur II (Xbox) — Phase 13 State: VXT Textures + Stages

Lane: TEARDOWN COMPLETION SWEEP, Phase 13 (VXT textures + stages — the
unblocked remainder). Stacked on PR #406
(`scii-wiring-phase4-20261020` @ 1af493bb, OPEN, base main). Branch:
`scii-phase13-textures-stages`.

## Out of scope (hard gate)

Motion / composition / clips are GATED on a dynamic emulator capture a
parent lane must run (static routes proven exhausted in phases 10–12,
GRE PR #40). This lane does NOT touch motion, composition, or clips.

## Jobs, in order

1. **JOB 1 — VXT DECODE**: crack the VXT texture format from v516 archive
   bytes (GRE PR #28 VMX/VXT findings as starting point; Xbox tiled /
   swizzled surfaces + DXT as the research baseline). Proof: first
   texture decoded to PNG and VIEWED in real colors (a recognizable
   character texture), then fighter↔texture mapping established with
   evidence (bundle adjacency, VMX material records — rec80 =
   materials, GRE PR #30 — or loader evidence); confidence labeled per
   mapping, never guessed.
2. **JOB 2 — TEXTURED FIGHTER GLBs**: apply the proven mapping to the 22
   skinned GLBs (PR #406, `models-skinned/`): textures EMBEDDED (image
   count per GLB in the inventory), geometry/skinning untouched
   (vert/face/joint counts identical to untextured originals;
   original-comparison documented). Front textured renders on a sample
   (≥4 fighters incl. Mitsurugi + Taki), viewed by the lane, unique
   filenames. Unmappable fighters on an explicit unproven list with the
   reason — no placeholder textures.
3. **JOB 3 — STAGES**: assemble v404 stage streams into stage GLBs
   (streams proven GRE PR #28; m003 verified — reproduce that pipeline
   for all stages in the archive), textured if stage VXT entries map
   with evidence, else untextured-and-stated. Stage inventory (count;
   names only where bytes carry them). One stage front render viewed.
4. **JOB 4 — CENSUS OF THE REST**: costume-variant bundles in v982,
   AFS audio/video contents — census + inventory entries only. Update
   `WIRING-INVENTORY.md`: decoded / wired / left-before-playable per
   class (textures, stages, costumes, audio, video).
   `CANON-CONVERSION.md` left untouched (owner-pending).

## Inherited facts (verified upstream — do not re-derive)

- The game is the **Xbox** version (XISO; the "PS2" release name is
  wrong).
- Container chain: `root.olk` → 4 sub-archives (GRE PR #26):
  v404 = STAGES, v516 = VXT TEXTURES, v982 = CHARACTER bundles.
- VMX/VXT format cracked (GRE PR #28); stage streams proven
  (35,390 verts; stage m003 own-eyes verified, GRE PR #28).
- 22 fighters decoded + placed + SKINNED (GRE PRs #31/#32; WH PR #406
  holds 22 placed GLBs + 22 skinned GLBs in
  `teardown/soulcalibur-2/models-skinned/` + `WIRING-INVENTORY.md` +
  `CANON-CONVERSION.md` + 24 moveset JSONs v1/v2 — identities PENDING
  owner canon, do not invent).
- Fighters are currently UNTEXTURED — VXT was never decoded into the
  GLBs. GLBs carry authored UVs but no texture images
  (`WIRING-INVENTORY.md`, gate G3 remainder).
- Fighter↔v982-entry mapping is in `CHARACTER-MAP.md` /
  `WIRING-INVENTORY.md` (e.g. Mitsurugi = entry 47, Taki = entry 125).
- Extraction sources: WH PR #154's extract (1,097 files) + release
  `soulcalibur2-xbox-extract-v1` (in western-heart).
- HAZARD: NEVER use `~/workspace/scii-work/p2/v982_idx47.bin`
  (stale/corrupt). Verify headers after any range fetch.
- Engine (owner-locked 2026-10-21): Godot 4.7.2 — GLB is its native
  format; GLB artifacts + inventories are the deliverables.

## Owner laws for visuals (2026-10-21)

1. **TEXTURES BAKED IN** — a shipped model carries its source textures
   embedded (proof = image count in the GLB + a textured render);
   stripping textures is a defect.
2. **ORIGINAL-COMPARISON** — every model deliverable rendered
   side-by-side against its original and viewed by the lane;
   comparison = BODY INTEGRITY (proportions / bone placement /
   weights), NOT pose.

## Status log

- 2026-10-21 ~21:49 CDT — lane start. PR #406 branch confirmed via API
- 2026-10-21 ~22:2x CDT — JOB 1 first half DONE: VXT format cracked (linear DXT1/3/5, see `VXT-FORMAT.md`); first textures decoded + viewed (idx47 tex07 skin/sash, tex06 tooled leather). Mapping evidence: part+0x0c → rec80 material → +0x08 primary VXT record pointer (byte-exact). Decoder: `tools/vxt_decode.py`.
- JOB 1 DONE + JOB 2 DONE: P8 format (11) cracked (swizzled indices + BGRA palette); all 22 fighters textured (559 embedded images, 886/891 meshes; idx905 has 5 source color-only parts). Alpha rule: MASK only for true cutout populations (Spawn specular-alpha defect found + fixed by own-eyes render, v2 proof). 4 comparison renders viewed (Mitsurugi/Taki/Cassandra/Spawn) — body integrity identical. JOB 3 in progress: m003 stage GLB built (35,390 verts = phase-2 verified total; 51 images; arena + plan renders viewed — marble temple stage, coherent).
- JOB 3 DONE: 39/41 stages assembled textured (940,586 verts / 791,524 tris / 1,795 images); m000 (VMX v2, 36B records, shared streams) + m120 (VMX v3, sentinel stream-end) flagged with named blockers, no guessed geometry. JOB 4 DONE: census (v982 costumes per slot, v516 371 entries, bgm.afs 76 ADX, movie.afs 3 MPEG-PS) in `CENSUS-PHASE13.md`; `WIRING-INVENTORY.md` updated per class; `CANON-CONVERSION.md` untouched.
  (OPEN, head `scii-wiring-phase4-20261020` @ `1af493bb289a`). Fresh
  sparse clone at `~/workspace/scii-work/p13/wh` (teardown/soulcalibur-2
  only, 178 MB working set). Branch `scii-phase13-textures-stages`
  created. This state doc is the first commit; PR opened immediately
  after, before any analysis.
