# Soulcalibur II (Xbox) — Phase 15 Probes + Solver Fix (evidence)

Phase 15 jobs 1–4. Phase-14's two named blockers and both named
probe next-steps are closed here. Headline: the Ivy failure was not
a solver residual and not source degeneracy — it was a wrong start
offset in the rigid-part reader, inherited from phase 4, and the
same misread invented the "sheet class" that has silently eaten
real geometry from every shipped fighter GLB. Details and the
pipeline-wide consequence are in job 1 — read it first.

## Job 1 — Ivy solver residual (idx283 + idx291): SOLVED (root cause)

Phase-14 read: "build_skinned produces non-finite normals at GLB
export (OverflowError); source pool normals are finite (0 NaN /
3,898 verts in idx283) — solver-side degenerate-bone residual."

Reproduction (unmodified phase-5 `build_skinned.py`, VMX0 @0x3880):
the skin solve completes cleanly (res_max 1.176e-07, all bone
matrices finite), then export dies in the RIGID-part loop:

```
File "build_skinned.py", line 355, in main
  na2 = add_acc(add_view(b''.join(struct.pack('<3f', *n) for n in pn), ...)
OverflowError: float too large to pack with f format
```

First failing vertex: idx283 g0p21 vert 0 (node 7, bone 131) —
transformed "normal" (4.44e31, 5.33e34, 3.428e38), past FLT_MAX.

Mechanism, proven from the bytes, in three steps:

1. **The rigid reader's +8 start shift is wrong.** build_skinned
   (inheriting phase-4's vmx_decode_v2 heuristic) starts a rigid
   part's vertex stream at rec[5]+8 whenever
   `(span − 8) // 40 == max_index + 1`, where span = rec[9] − rec[5].
   Those parts actually carry an 8-byte **trailer** after the
   stream (span = count×40 + 8); their vertices start at rec[5] in
   the standard format (pos, normal, color, UV, pad) like all
   others.
2. **The shift manufactures the "sheet class".** Shifted by 8, the
   vertex's +0x18 ARGB color word lands in the +0x10 normal-Y slot.
   White colors (0xFFFFFFFF) read as NaN → the part was classified
   "sheet" and excluded (this is the entire origin of the phase-4
   sheet class: at +0 alignment there are no NaN normals anywhere).
   Grey/tinted colors (0xFF7F7F7F, 0xFF333333, 0xFFB2A792, …) read
   as ≈ −2.4e38…−3.4e38 floats — finite, so they pass the isnan
   check, and the node-matrix multiply (×~1.0094 + cross terms)
   pushes them to ≈3.428e38 > FLT_MAX → the pack OverflowError.
3. **Census proof (25 bundles: 22 P1 + idx283/291/789).** At +0
   alignment, **all 725 rigid parts** (470 plain-span + 255
   trailer-span) have unit normals (|n| − 1 < 0.05) and
   0xFF-alpha colors at +0x18 for **every** vertex. There is no
   sheet class in the rigid vertex streams. The skinned dst pool
   was always clean (0 non-finite / 3,898 normals in idx283), and
   no bone, weight, or triangle in the source is degenerate.

Why only idx283/idx291 crashed: they are the only variant bundles
whose trailer-span parts carry grey (finite-huge) colors in the
shifted slot in a part ordering that reaches export — everywhere
else the shifted slot happened to be white/NaN (excluded silently)
or the values stayed packable. A scan of all 102 previously
shipped GLBs confirms none carries a non-finite or |normal| > 2
value — no garbage shipped; the cost elsewhere was **silently
missing parts**, not bad data.

**Pipeline-wide consequence (flagged, not fixed in this phase):**
every previously shipped fighter/variant GLB is missing its
trailer-span rigid parts (255 parts across the 25 censused
bundles — e.g. Mitsurugi's "sheet" strips that phase 4 found
"do not form legible coverage" in `_full` were this misread).
Re-decoding the 102 shipped GLBs with the fixed reader is a
follow-on lane; this phase fixes the tool and the 3 blocked
bundles, per scope.

Fix (tools-side, `tools/build_skinned.py` landed in-repo on this
branch — the tool previously lived only in the phase-5 work dir):
vertex streams always start at rec[5] (shift deleted, mechanism
comment in code); finite assertions added before packing all
skinned and rigid positions/normals. No source byte was edited,
and no part is excluded anymore.

Regeneration gates (both bundles, full pipeline
`build_skinned.py` → `apply_textures.py`):

| Gate | idx283 | idx291 |
|---|---|---|
| skin res_max / rms | 1.176e-07 / 1.85e-08 | 1.176e-07 / 1.85e-08 |
| bones / verts | 167 / 3,898 | 167 / 3,898 |
| meshes (all parts incl. 7 recovered trailer-span parts) | 41 | 41 |
| accessor counts identical after texturing | asserted by tool | asserted by tool |
| embedded images | 22 | 22 |
| skins in GLB | exactly 1 | exactly 1 |
| normals finite (all accessors re-parsed) | 0 non-finite | 0 non-finite |
| front render viewed | yes — `phase15-proof/variant-idx283-ivy-front.png` | yes — `phase15-proof/variant-idx291-ivy-front.png` |

Renders (viewed): coherent Ivy costume — black/gold bodice and
cuffs, red rose-pattern tights, long black gloves, white hair,
choker — fully textured, T-pose.

## Job 2 — idx789 rigid bundle: IDENTIFIED + ASSEMBLED

Structure (bundle 730,240 B, VMX0 @0x3880, header-verified):
rec28 skin counts [0, 25312, 3074, 0] with src=dst=0 (no skin
pool), part counts (101, 1, 0), **102/102 parts type 0 (rigid),
zero type-4 skinned parts**, 52 nodes, 6 rec80 materials, 6 VXT
textures, 6,823 verts. Its base slot (788) was never a skinned
fighter because the model is built entirely of rigid parts on
nodes — in fact a golem: with the job-1 reader fix, the parts
assemble into a coherent rocky humanoid (viewed render:
`phase15-proof/idx789-rigid-front.png`) — cracked stone-textured
segments for head/torso/limbs/boots, glowing cyan seams between
segments, and a dark sphere with purple runic markings seated in
the torso. Assembled with the new rigid path
(`tools/build_rigid.py`: node placement, authored normals,
per-part topology by normal-agreement score) + the proven VXT
route (`apply_textures.py`): 102/102 meshes textured, 6 images
embedded, all alpha [255,255]. Bounds x [−1.63, 1.55], y
[−0.67, 2.60], z [−1.00, 1.00]. **No identity is assigned**
(canon assignment is owner-pending; the visual class — a rocky
segment golem with a rune orb core — is reported, not named).

(Assembly note: the first two assembly attempts rendered as a
shard mass — once via strip topology under the old misread, once
still under the +8 shift. Only the job-1 root fix produced the
coherent figure; both failed renders were caught by viewing, per
the own-eyes rule, and are not shipped.)

## Job 3 — rec80 secondary texture (+0x0c): runtime role

Phase-14 proved the +0x0c word is a real second VXT-record reference
(159/159 pointer-exact). Phase 15 read the XBE consumers:

1. **The VMX reloc
...[truncated 5013 chars]